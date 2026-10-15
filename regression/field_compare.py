#!/usr/bin/env python3
"""Field-level comparator for analyzer envelopes: raw / strict / budgeted modes.

Scope (spec §3, report A3/A4): compare two snapshot trees (or two documents)
and report COMPLETE per-path deltas. The findings multiset diff in
``regression/regression_diff.py`` remains the secondary ``findings_summary``;
``regression/_differ.py`` (compact baseline projection) is unrelated and
unchanged.

Modes
  raw       byte identity per unit file (sha256); legitimately fails whenever
            ``/inputs/run_id`` differs and says so.
  strict    recursive JSON field comparison; absent != null; bool != number;
            list order kept; only policy-listed leaves masked, each shape- and
            linkage-checked.
  budgeted  strict deltas classified against a tracked budget record; every
            delta must be claimed by a class or it is a residual.
"""
from __future__ import annotations

import copy
import hashlib
import importlib
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

POLICY_DIR = Path(__file__).resolve().parent / "normalization"

_ALLOWED_LEAF_KEYS = {"pointer", "pointer_glob", "shape", "equals", "sha256_of", "rewrite", "note"}
_ALLOWED_REWRITES = {"strip_root_prefix", "strip_root_prefix_keys"}
NAMED_SHAPES = {
    "number": None,                         # checked by type, not regex
    "iso8601": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$",
    "run_id": r"^\d{8}T\d{6}Z-[0-9a-f]{6}$",
}


class PolicyError(ValueError):
    """Malformed or missing normalization policy."""


@dataclass
class Policy:
    name: str
    leaves: list[dict] = field(default_factory=list)
    root_prefixes: list[str] = field(default_factory=list)
    root_prefixes_from_manifest: bool = False


def _check_pointer(ptr, idx: int, glob: bool) -> None:
    if not isinstance(ptr, str) or not ptr.startswith("/"):
        raise PolicyError(f"leaf {idx}: pointer must start with '/' (RFC 6901): {ptr!r}")
    for tok in ptr[1:].split("/"):
        if glob and tok == "*":
            continue
        if re.search(r"~(?![01])", tok):
            raise PolicyError(f"leaf {idx}: bad '~' escape in pointer {ptr!r}")


def _validate_leaf(leaf: dict, idx: int) -> None:
    unknown = set(leaf) - _ALLOWED_LEAF_KEYS
    if unknown:
        raise PolicyError(f"leaf {idx}: unknown key(s) {sorted(unknown)}")
    forms = [k for k in ("pointer", "pointer_glob") if k in leaf]
    if len(forms) != 1:
        raise PolicyError(f"leaf {idx}: exactly one of pointer/pointer_glob required")
    ptr = leaf[forms[0]]
    _check_pointer(ptr, idx, forms[0] == "pointer_glob")
    for key in ("shape", "rewrite", "equals", "sha256_of", "note"):
        if key in leaf and not isinstance(leaf[key], str):
            raise PolicyError(f"leaf {idx}: {key} must be a string")
    if "rewrite" in leaf and leaf["rewrite"] not in _ALLOWED_REWRITES:
        raise PolicyError(f"leaf {idx}: rewrite must be one of {sorted(_ALLOWED_REWRITES)}")
    if "equals" in leaf:
        _check_pointer(leaf["equals"], idx, False)
    shape = leaf.get("shape")
    if shape is not None and shape not in NAMED_SHAPES:
        try:
            re.compile(shape)
        except re.error as e:
            raise PolicyError(f"bad shape regex at {ptr}: {e}") from e


def load_policy(name: str, policy_dir: Path | None = None) -> Policy:
    pdir = Path(policy_dir) if policy_dir is not None else POLICY_DIR
    path = pdir / f"{name}.json"
    if not path.exists():
        raise PolicyError(f"normalization policy {name!r} not found at {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise PolicyError(f"policy {name!r}: invalid JSON: {e}") from e
    if not isinstance(data, dict):
        raise PolicyError(f"policy {name!r}: top level must be an object")
    if not isinstance(data.get("name"), str) or data["name"] != name:
        raise PolicyError(f"policy file {path.name} declares name {data.get('name')!r}, expected {name!r}")
    leaves = data.get("leaves")
    if not isinstance(leaves, list):
        raise PolicyError(f"policy {name!r}: 'leaves' must be a list")
    for i, leaf in enumerate(leaves):
        if not isinstance(leaf, dict):
            raise PolicyError(f"leaf {i}: must be an object")
        _validate_leaf(leaf, i)
    rp = data.get("root_prefixes", [])
    if rp == "from_manifest":
        return Policy(name=name, leaves=leaves, root_prefixes=[], root_prefixes_from_manifest=True)
    if not isinstance(rp, list) or not all(isinstance(x, str) for x in rp):
        raise PolicyError(f"policy {name!r}: root_prefixes must be 'from_manifest' or a list of strings")
    return Policy(name=name, leaves=leaves, root_prefixes=list(rp))


# ---- strict comparison (Task 2) ---------------------------------------------

OPS = ("added", "removed", "changed", "type_changed", "key_order", "bytes", "lexical_numeric")


@dataclass(frozen=True)
class Delta:
    """One field difference. Deltas with list/dict payloads are unhashable; do not put them in sets."""
    unit: str
    analyzer: str
    path: str
    op: str
    before: Any
    after: Any

    def to_json(self) -> dict:
        return {"unit": self.unit, "analyzer": self.analyzer, "path": self.path,
                "op": self.op, "before": self.before, "after": self.after}


# RFC 6901 helpers

def escape_token(token: Any) -> str:
    return str(token).replace("~", "~0").replace("/", "~1")


def _unescape_token(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def join_pointer(parent: str, token: Any) -> str:
    return f"{parent}/{escape_token(token)}"


def split_pointer(pointer: str) -> list[str]:
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise ValueError(f"pointer must start with '/': {pointer!r}")
    return [_unescape_token(t) for t in pointer[1:].split("/")]


def resolve_pointer(doc: Any, pointer: str) -> tuple[bool, Any]:
    cur = doc
    for tok in split_pointer(pointer):
        if isinstance(cur, dict):
            if tok not in cur:
                return False, None
            cur = cur[tok]
        elif isinstance(cur, list):
            if (not (tok.isascii() and tok.isdigit()) or (len(tok) > 1 and tok[0] == "0")
                    or int(tok) >= len(cur)):
                return False, None
            cur = cur[int(tok)]
        else:
            return False, None
    return True, cur


def _kind(v: Any) -> str:
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, (int, float)):
        return "number"
    if v is None:
        return "null"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "list"
    if isinstance(v, dict):
        return "dict"
    return type(v).__name__


class _Ctx:
    __slots__ = ("unit", "analyzer", "key_order", "deltas", "masked", "violations")

    def __init__(self, unit, analyzer, key_order):
        self.unit, self.analyzer, self.key_order = unit, analyzer, key_order
        self.deltas: list[Delta] = []
        self.masked: set[str] = set()      # exact pointers masked by policy (Task 3)
        self.violations: list[str] = []

    def emit(self, path, op, before, after):
        self.deltas.append(Delta(self.unit, self.analyzer, path, op, before, after))


def _walk(a: Any, b: Any, path: str, ctx: _Ctx) -> None:
    if path in ctx.masked:
        return
    ka, kb = _kind(a), _kind(b)
    if ka != kb:
        ctx.emit(path, "type_changed", a, b)
        return
    if ka == "dict":
        if ctx.key_order and list(a.keys()) != list(b.keys()):
            ctx.emit(path, "key_order", list(a.keys()), list(b.keys()))
        for k in a:
            p = join_pointer(path, k)
            if k in b:
                _walk(a[k], b[k], p, ctx)
            elif p not in ctx.masked:
                ctx.emit(p, "removed", a[k], None)
        for k in b:
            if k not in a:
                p = join_pointer(path, k)
                if p not in ctx.masked:
                    ctx.emit(p, "added", None, b[k])
        return
    if ka == "list":
        n = min(len(a), len(b))
        for i in range(n):
            _walk(a[i], b[i], join_pointer(path, i), ctx)
        for i in range(n, len(a)):
            p = join_pointer(path, i)
            if p not in ctx.masked:
                ctx.emit(p, "removed", a[i], None)
        for i in range(n, len(b)):
            p = join_pointer(path, i)
            if p not in ctx.masked:
                ctx.emit(p, "added", None, b[i])
        return
    if a != b and not (ka == "number" and a != a and b != b):   # NaN == NaN in strict mode
        ctx.emit(path, "changed", a, b)


def _all_pointers(doc: Any, path: str = "", out: set[str] | None = None) -> set[str]:
    if out is None:
        out = set()
    out.add(path)
    if isinstance(doc, dict):
        for k, v in doc.items():
            _all_pointers(v, join_pointer(path, k), out)
    elif isinstance(doc, list):
        for i, v in enumerate(doc):
            _all_pointers(v, join_pointer(path, i), out)
    return out


def _expand_glob(glob: str, pointers: set[str]) -> list[str]:
    """`*` matches exactly one segment: compare segment-wise, not fnmatch over '/'."""
    want = split_pointer(glob)
    hits = []
    for p in pointers:
        toks = split_pointer(p)
        if len(toks) == len(want) and all(w == "*" or w == t for w, t in zip(want, toks)):
            hits.append(p)
    return sorted(hits)


def _shape_ok(value: Any, shape: str) -> bool:
    if shape == "number":
        return _kind(value) == "number"
    rx = NAMED_SHAPES.get(shape, shape)
    return isinstance(value, (str, int, float)) and not isinstance(value, bool) \
        and re.search(rx, str(value)) is not None


def _set_pointer(doc: Any, pointer: str, value: Any) -> None:
    toks = split_pointer(pointer)
    cur = doc
    for t in toks[:-1]:
        cur = cur[int(t)] if isinstance(cur, list) else cur[t]
    last = toks[-1]
    if isinstance(cur, list):
        cur[int(last)] = value
    else:
        cur[last] = value


def _strip(s: Any, prefix: str) -> Any:
    return s[len(prefix):] if prefix and isinstance(s, str) and s.startswith(prefix) else s


def _apply_policy(a: Any, b: Any, policy: Policy, ctx: _Ctx,
                  root_prefixes: tuple[str, str] | None = None) -> tuple[Any, Any]:
    """Apply exact-leaf masking and rewrites on deep copies; record masks/violations in ctx."""
    a = copy.deepcopy(a)
    b = copy.deepcopy(b)
    rewrites = any(lf.get("rewrite") for lf in policy.leaves)
    if root_prefixes is not None:
        prefixes = (root_prefixes[0], root_prefixes[1])
    elif len(policy.root_prefixes) >= 2:
        prefixes = (policy.root_prefixes[0], policy.root_prefixes[1])
    else:
        prefixes = ("", "")
        if policy.root_prefixes_from_manifest and rewrites:
            ctx.violations.append(f"{ctx.unit}: root prefixes required but not supplied")
    pointers: set[str] = set()
    if any("pointer_glob" in lf for lf in policy.leaves):
        _all_pointers(a, "", pointers)
        _all_pointers(b, "", pointers)
    for leaf in policy.leaves:
        targets = [leaf["pointer"]] if "pointer" in leaf else _expand_glob(leaf["pointer_glob"], pointers)
        for ptr in targets:
            fa, va = resolve_pointer(a, ptr)
            fb, vb = resolve_pointer(b, ptr)
            if not fa and not fb:
                continue
            rewrite = leaf.get("rewrite")
            if rewrite == "strip_root_prefix":
                if fa and isinstance(va, str):
                    _set_pointer(a, ptr, _strip(va, prefixes[0]))
                if fb and isinstance(vb, str):
                    _set_pointer(b, ptr, _strip(vb, prefixes[1]))
                continue   # compared normally after rewrite
            if rewrite == "strip_root_prefix_keys":
                for doc, found, val, pre in ((a, fa, va, prefixes[0]), (b, fb, vb, prefixes[1])):
                    if not found:
                        continue
                    if not isinstance(val, dict):
                        ctx.violations.append(f"{ctx.unit} {ptr}: strip_root_prefix_keys needs a dict")
                        continue
                    new: dict = {}
                    for k, v in val.items():
                        nk = _strip(k, pre)
                        if nk in new:
                            ctx.violations.append(
                                f"{ctx.unit} {ptr}: strip_root_prefix_keys collision on {nk}")
                        else:
                            new[nk] = v
                    _set_pointer(doc, ptr, new)
                continue
            # masking leaves: refuse containers, require presence on both sides
            if (fa and _kind(va) in ("dict", "list")) or (fb and _kind(vb) in ("dict", "list")):
                ctx.violations.append(f"{ctx.unit} {ptr}: pointer lands on a container; whole-block masking refused")
                continue
            if not (fa and fb):
                continue   # real added/removed; let the walk report it
            ctx.masked.add(ptr)
            shape = leaf.get("shape")
            if shape is not None:
                for side, v in (("a", va), ("b", vb)):
                    if not _shape_ok(v, shape):
                        ctx.violations.append(f"{ctx.unit} {ptr}: side {side} value {v!r} fails shape {shape}")
            eq = leaf.get("equals")
            if eq is not None:
                for side, doc, v in (("a", a, va), ("b", b, vb)):
                    found, other = resolve_pointer(doc, eq)
                    if not found or other != v:
                        ctx.violations.append(f"{ctx.unit} {ptr}: side {side} fails equals {eq} ({v!r} vs {other!r})")
            sib = leaf.get("sha256_of")
            if sib is not None:
                parent = ptr.rsplit("/", 1)[0]
                for side, doc, v, pre in (("a", a, va, prefixes[0]), ("b", b, vb, prefixes[1])):
                    found, p = resolve_pointer(doc, join_pointer(parent, sib))
                    # the sibling may already have been prefix-stripped; re-add the prefix for I/O
                    cand = [p, pre + p] if found and isinstance(p, str) else []
                    target = next((c for c in cand if c and Path(c).is_file()), None)
                    if target is None:
                        ctx.violations.append(f"{ctx.unit} {ptr}: sha256_of {sib}: linked file missing on side {side}")
                        continue
                    if hashlib.sha256(Path(target).read_bytes()).hexdigest() != v:
                        ctx.violations.append(f"{ctx.unit} {ptr}: sha256_of {sib} mismatch on side {side}")
    return a, b


def compare_strict(a: Any, b: Any, policy: Policy | None, *, unit: str, analyzer: str,
                   key_order: bool = False,
                   root_prefixes: tuple[str, str] | None = None) -> tuple[list[Delta], list[str]]:
    """Recursive field comparison. Returns (deltas, policy_violations).

    Two NaNs compare equal. ``key_order=True`` emits a ``key_order`` delta for any
    dict whose key sequence differs, including when the key sets differ.
    ``root_prefixes`` = (a_root, b_root) overrides ``policy.root_prefixes``.
    """
    ctx = _Ctx(unit, analyzer, key_order)
    if policy is not None:
        a, b = _apply_policy(a, b, policy, ctx, root_prefixes)
    _walk(a, b, "", ctx)
    return ctx.deltas, ctx.violations


_NUM_TOKEN = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare_raw(a_path: Path, b_path: Path, *, unit: str, analyzer: str) -> list[Delta]:
    """Byte identity. One ``bytes`` delta when the files differ; additionally one
    ``lexical_numeric`` delta when the parsed JSON is equal but number spelling differs."""
    ab, bb = Path(a_path).read_bytes(), Path(b_path).read_bytes()
    if ab == bb:
        return []
    out = [Delta(unit, analyzer, "", "bytes", hashlib.sha256(ab).hexdigest(), hashlib.sha256(bb).hexdigest())]
    try:
        pa, pb = json.loads(ab), json.loads(bb)
    except json.JSONDecodeError:
        return out
    if pa == pb:
        ta, tb = _NUM_TOKEN.findall(ab.decode("utf-8", "replace")), _NUM_TOKEN.findall(bb.decode("utf-8", "replace"))
        if ta != tb:
            diff = [(x, y) for x, y in zip(ta, tb) if x != y][:50]
            out.append(Delta(unit, analyzer, "", "lexical_numeric", [x for x, _ in diff], [y for _, y in diff]))
    return out


def iter_units(root: Path) -> list[tuple[str, str, Path]]:
    """Every ``snap.json`` under root → (unit_id, analyzer, path). unit_id is the
    parent directory relative to root with '/' separators; analyzer is its first segment."""
    root = Path(root)
    out = []
    for p in sorted(root.rglob("snap.json")):
        rel = p.parent.relative_to(root).as_posix()
        out.append((rel, rel.split("/", 1)[0], p))
    return out


def _manifest_identity(root: Path) -> dict | None:
    m = Path(root) / "manifest.json"
    if not m.exists():
        m = Path(root).parent / "manifest.json"   # gate dir holds the manifest beside the slot roots
    if not m.exists():
        return None
    try:
        data = json.loads(m.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return {k: data.get(k) for k in ("profile", "harness", "product", "selection")}


def compare_trees(a_root: Path, b_root: Path, *, mode: str, policy: Policy | None,
                  key_order: bool = False,
                  root_prefixes: tuple[str, str] | None = None) -> dict:
    if mode not in ("raw", "strict", "budgeted"):
        raise ValueError(f"mode must be raw|strict|budgeted, got {mode!r}")
    a_root, b_root = Path(a_root).resolve(), Path(b_root).resolve()
    prefixes = root_prefixes or (str(a_root), str(b_root))
    a_units = {u: (an, p) for u, an, p in iter_units(a_root)}
    b_units = {u: (an, p) for u, an, p in iter_units(b_root)}
    units_out, deltas, violations = [], [], []
    counts = Counter()
    for unit in sorted(set(a_units) | set(b_units)):
        analyzer = (a_units.get(unit) or b_units.get(unit))[0]
        rec = {"unit": unit, "analyzer": analyzer,
               "a": str(a_units[unit][1].relative_to(a_root)) if unit in a_units else None,
               "b": str(b_units[unit][1].relative_to(b_root)) if unit in b_units else None,
               "status": "compared", "delta_count": 0}
        if unit not in a_units or unit not in b_units:
            rec["status"] = "missing_a" if unit not in a_units else "missing_b"
            counts["missing"] += 1
            units_out.append(rec)
            continue
        pa, pb = a_units[unit][1], b_units[unit][1]
        if mode == "raw":
            ds = compare_raw(pa, pb, unit=unit, analyzer=analyzer)
        else:
            docs = []
            for side, p in (("a", pa), ("b", pb)):
                try:
                    docs.append(json.loads(p.read_text(encoding="utf-8")))
                except (json.JSONDecodeError, OSError, UnicodeDecodeError):
                    rec["status"] = f"parse_error_{side}"
                    break
            if rec["status"] != "compared":
                counts["parse_errors"] += 1
                units_out.append(rec)
                continue
            ds, viol = compare_strict(docs[0], docs[1], policy, unit=unit, analyzer=analyzer,
                                      key_order=key_order, root_prefixes=prefixes)
            violations.extend(viol)
        rec["delta_count"] = len(ds)
        counts["compared"] += 1
        counts["identical" if not ds else "with_deltas"] += 1
        deltas.extend(ds)
        units_out.append(rec)
    by_op = Counter(d.op for d in deltas)
    by_an = Counter(d.analyzer for d in deltas)
    summary = {"units": len(units_out), "compared": counts["compared"], "identical": counts["identical"],
               "with_deltas": counts["with_deltas"], "missing": counts["missing"],
               "parse_errors": counts["parse_errors"], "deltas": len(deltas),
               "by_op": dict(sorted(by_op.items())), "by_analyzer": dict(sorted(by_an.items()))}
    if counts["missing"] or counts["parse_errors"] or violations:
        verdict = "error"
    elif deltas:
        verdict = "deltas"
    else:
        verdict = "clean"
    return {"report_version": 1, "mode": mode, "policy": policy.name if policy else None,
            "key_order": key_order, "a_root": str(a_root), "b_root": str(b_root),
            "identity": {"a": _manifest_identity(a_root), "b": _manifest_identity(b_root)},
            "units": units_out, "deltas": [d.to_json() for d in deltas],
            "policy_violations": violations, "summary": summary, "budget": None, "verdict": verdict}


# ---- budgets (Task 5) --------------------------------------------------------

SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}
_CLASS_KEYS = {"id", "analyzer", "path_glob", "op", "where", "direction", "value_relation",
               "unit_bound", "predicate", "evidence"}
_WHERE_KEYS = {"rule_id", "detector"}


class BudgetError(ValueError):
    """Malformed budget record or unusable predicate."""


def _split_predicate(spec: Any, cid: str) -> tuple[str, str]:
    mod, sep, fn = spec.partition(":") if isinstance(spec, str) else ("", "", "")
    if not (sep and mod.isidentifier() and fn.isidentifier()):
        raise BudgetError(f"class {cid}: predicate must be 'module:function' with a bare module "
                          f"name under regression.budgets, got {spec!r}")
    return mod, fn


def _validate_class(i: int, c: Any) -> None:
    if not isinstance(c, dict) or "id" not in c or "path_glob" not in c:
        raise BudgetError(f"class {i}: 'id' and 'path_glob' are required")
    cid = c["id"]
    if not isinstance(cid, str) or not cid:
        raise BudgetError(f"class {i}: id must be a non-empty string")
    unknown = set(c) - _CLASS_KEYS
    if unknown:
        raise BudgetError(f"class {cid}: unknown key(s) {sorted(unknown)}")
    glob = c["path_glob"]
    if not isinstance(glob, str) or (glob and glob != "**" and not glob.startswith("/")):
        raise BudgetError(f"class {cid}: path_glob must be a pointer-style string")
    if "**" in (split_pointer(glob) if glob.startswith("/") else [])[:-1]:
        raise BudgetError(f"class {cid}: path_glob '**' is only allowed as the last segment")
    if "op" in c:
        if not isinstance(c["op"], list):
            raise BudgetError(f"class {cid}: op must be a list")
        bad_ops = set(c["op"]) - set(OPS)
        if bad_ops:
            raise BudgetError(f"class {cid}: unknown op(s) {sorted(bad_ops)}")
    if "where" in c:
        w = c["where"]
        if (not isinstance(w, dict) or not w or set(w) - _WHERE_KEYS
                or not all(isinstance(v, list) for v in w.values())):
            raise BudgetError(f"class {cid}: where must be a non-empty object of rule_id/detector lists")
    if c.get("direction", "any") not in ("any", "up", "down", "none"):
        raise BudgetError(f"class {cid}: direction must be any|up|down|none")
    if c.get("value_relation", "any") not in ("any", "equal"):
        raise BudgetError(f"class {cid}: value_relation must be any|equal")
    if "unit_bound" in c:
        ub = c["unit_bound"]
        mu = ub.get("max_units") if isinstance(ub, dict) else None
        if not isinstance(ub, dict) or set(ub) != {"max_units"} or isinstance(mu, bool) or not isinstance(mu, int) or mu < 0:
            raise BudgetError(f"class {cid}: unit_bound must be {{\"max_units\": non-negative int}}")
    if "predicate" in c:
        _split_predicate(c["predicate"], cid)


def load_budget(path: Path) -> dict:
    try:
        b = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise BudgetError(f"cannot read budget {path}: {e}") from e
    if not isinstance(b, dict):
        raise BudgetError("budget must be a JSON object")
    for k in ("budget_id", "classes", "unexplained_deltas_allowed", "unexplained_missing_units_allowed", "relock"):
        if k not in b:
            raise BudgetError(f"budget missing required key {k!r}")
    for k in ("unexplained_deltas_allowed", "unexplained_missing_units_allowed"):
        if isinstance(b[k], bool) or not isinstance(b[k], int) or b[k] < 0:
            raise BudgetError(f"{k} must be a non-negative integer")
    if not isinstance(b["relock"], bool):
        raise BudgetError("relock must be a boolean")
    if not isinstance(b["classes"], list):
        raise BudgetError("classes must be a list")
    seen = set()
    for i, c in enumerate(b["classes"]):
        _validate_class(i, c)
        if c["id"] in seen:
            raise BudgetError(f"duplicate class id {c['id']!r}")
        seen.add(c["id"])
    return b


def _glob_match(glob: str, path: str) -> bool:
    """Segment-wise match: ``*`` = exactly one segment, trailing ``**`` = any remainder (incl. none)."""
    if glob == "**":
        return True
    want = split_pointer(glob)
    toks = split_pointer(path)
    trailing = bool(want) and want[-1] == "**"
    if trailing:
        want = want[:-1]
        if len(toks) < len(want):
            return False
        toks = toks[:len(want)]
    elif len(toks) != len(want):
        return False
    return all(w == "*" or w == t for w, t in zip(want, toks))


def _finding_at(doc: Any, path: str) -> dict | None:
    toks = split_pointer(path)
    if len(toks) >= 2 and toks[0] in ("findings", "assessments") and toks[1].isdigit():
        found, f = resolve_pointer(doc, f"/{escape_token(toks[0])}/{toks[1]}")
        return f if found and isinstance(f, dict) else None
    return None


def _where_ok(cls: dict, delta: Delta, a_doc: Any, b_doc: Any) -> bool:
    where = cls.get("where")
    if not where:
        return True
    for f in (_finding_at(a_doc, delta.path), _finding_at(b_doc, delta.path)):
        if f is None:
            continue
        if all(f.get(key) in where[key] for key in ("rule_id", "detector") if key in where):
            return True
    return False


def _direction_ok(cls: dict, delta: Delta) -> bool:
    d = cls.get("direction", "any")
    if d == "any":
        return True
    if delta.op != "changed" or not delta.path.endswith("/severity"):
        return False
    sb, sa = SEVERITY_ORDER.get(delta.before), SEVERITY_ORDER.get(delta.after)
    if sb is None or sa is None:
        return False
    return {"up": sa > sb, "down": sa < sb, "none": sa == sb}[d]


def _load_predicate(spec: str, cid: str = "?"):
    mod, fn = _split_predicate(spec, cid)
    try:
        f = getattr(importlib.import_module(f"regression.budgets.{mod}"), fn)
    except (ImportError, AttributeError) as e:
        raise BudgetError(f"class {cid}: predicate {spec!r} cannot be loaded: {e}") from e
    if not callable(f):
        raise BudgetError(f"class {cid}: predicate {spec!r} is not callable")
    return f


def _class_claims(cls: dict, delta: Delta, docs, pred) -> bool:
    if cls.get("analyzer") and cls["analyzer"] != delta.analyzer:
        return False
    if not _glob_match(cls["path_glob"], delta.path):
        return False
    if "op" in cls and delta.op not in cls["op"]:
        return False
    a_doc, b_doc = (docs or {}).get(delta.unit, (None, None))
    if not _where_ok(cls, delta, a_doc, b_doc):
        return False
    if not _direction_ok(cls, delta):
        return False
    if cls.get("value_relation", "any") == "equal" and delta.before != delta.after:
        return False
    if pred is not None and not pred(delta, a_doc, b_doc):
        return False
    return True


def evaluate_budget(deltas: list[Delta], budget: dict, *, docs: dict | None = None,
                    missing_units: int = 0) -> dict:
    """Classify deltas against budget classes. A delta is claimed iff ALL selectors of some class match."""
    classes = budget["classes"]
    preds = [_load_predicate(c["predicate"], str(c.get("id"))) if c.get("predicate") else None for c in classes]
    claimed: list[list[Delta]] = [[] for _ in classes]
    residuals: list[Delta] = []
    for d in deltas:
        hit = False
        for i, c in enumerate(classes):
            if _class_claims(c, d, docs, preds[i]):
                claimed[i].append(d)
                hit = True
        if not hit:
            residuals.append(d)
    violations = []
    for i, c in enumerate(classes):
        bound = (c.get("unit_bound") or {}).get("max_units")
        n_units = len({d.unit for d in claimed[i]})
        if bound is not None and n_units > bound:
            violations.append(f"class {c['id']} claimed {n_units} units > max_units {bound}")
    allowed_missing = int(budget.get("unexplained_missing_units_allowed", 0))
    if missing_units > allowed_missing:
        violations.append(f"{missing_units} missing units > unexplained_missing_units_allowed {allowed_missing}")
    clean = len(residuals) <= int(budget.get("unexplained_deltas_allowed", 0)) and not violations
    return {"budget_id": budget["budget_id"], "clean": clean,
            "claimed": {c["id"]: [d.to_json() for d in claimed[i]] for i, c in enumerate(classes)},
            "claimed_counts": {c["id"]: len(claimed[i]) for i, c in enumerate(classes) if claimed[i]},
            "claimed_units": {c["id"]: len({d.unit for d in claimed[i]}) for i, c in enumerate(classes) if claimed[i]},
            "residuals": [d.to_json() for d in residuals], "violations": violations}


def docs_for_report(report: dict, a_root: Path, b_root: Path) -> dict:
    """Load (a_doc, b_doc) per compared unit so budget `where`/predicates can resolve findings."""
    docs = {}
    for u in report["units"]:
        if u["status"] == "compared":
            docs[u["unit"]] = (json.loads((Path(a_root) / u["a"]).read_text(encoding="utf-8")),
                               json.loads((Path(b_root) / u["b"]).read_text(encoding="utf-8")))
    return docs


def _slots(gate_root: Path) -> tuple[Path, Path]:
    g = Path(gate_root)
    for a, b in (("baseline", "candidate"), ("v131", "v14")):
        if (g / a).is_dir() and (g / b).is_dir():
            return g / a, g / b
    for a, b in (("baseline", "candidate"), ("v131", "v14")):
        if (g / a).is_dir() and not (g / b).is_dir():
            raise FileNotFoundError(f"gate {g}: slot {a!r} present but {b!r} missing")
    raise FileNotFoundError(f"gate {g}: no baseline/candidate (or v131/v14) slot pair")


def run_modes(gate_root: Path, *, budget_path: Path | None = None, key_order: bool = False,
              policy_name: str = "volatile-leaves-v1", write_reports: bool = True) -> dict:
    """Run raw + strict (+ budgeted) over a gate's two slots. Returns the dict the gate
    stores under rollup['modes']; writes field_report_<mode>.json beside the slots."""
    g = Path(gate_root)
    a_root, b_root = _slots(g)
    policy = load_policy(policy_name)
    out: dict = {"policy": policy.name, "key_order": key_order}

    raw = compare_trees(a_root, b_root, mode="raw", policy=None)
    strict = compare_trees(a_root, b_root, mode="strict", policy=policy, key_order=key_order)
    if write_reports:
        (g / "field_report_raw.json").write_text(json.dumps(raw, indent=1), encoding="utf-8")
        (g / "field_report_strict.json").write_text(json.dumps(strict, indent=1), encoding="utf-8")
    out["raw"] = {"verdict": raw["verdict"], "report": "field_report_raw.json", "summary": raw["summary"]}
    out["strict"] = {"verdict": strict["verdict"], "report": "field_report_strict.json",
                     "summary": strict["summary"], "policy_violations": len(strict["policy_violations"])}

    if budget_path is None:
        out["budgeted"] = {"verdict": "n/a"}
        out["strict_field_clean"] = strict["verdict"] == "clean"
        return out

    budget = load_budget(Path(budget_path))
    deltas = [Delta(**d) for d in strict["deltas"]]
    ev = evaluate_budget(deltas, budget, docs=docs_for_report(strict, a_root, b_root),
                         missing_units=strict["summary"]["missing"])
    missing_allowed = int(budget.get("unexplained_missing_units_allowed", 0))
    hard_error = (strict["summary"]["missing"] > missing_allowed or strict["summary"]["parse_errors"] > 0
                  or bool(strict["policy_violations"]))
    verdict = "error" if hard_error else ("clean" if ev["clean"] else "residuals")
    budgeted = dict(strict, mode="budgeted", budget=ev, verdict=verdict)
    if write_reports:
        (g / "field_report_budgeted.json").write_text(json.dumps(budgeted, indent=1), encoding="utf-8")
    out["budgeted"] = {"verdict": verdict, "report": "field_report_budgeted.json", "budget_id": budget["budget_id"],
                       "claimed_counts": ev["claimed_counts"], "residuals": len(ev["residuals"]),
                       "violations": len(ev["violations"])}
    out["strict_field_clean"] = verdict == "clean"
    return out
