#!/usr/bin/env python3
"""Field-level comparator for analyzer envelopes: raw / strict / budgeted modes.

Scope: compare two snapshot trees (or two documents)
and report COMPLETE per-path deltas. The findings multiset diff in
``regression/regression_diff.py`` remains the secondary ``findings_summary``;
``regression/_differ.py`` (compact baseline projection) is unrelated and
unchanged.

Modes
  raw       the per-unit file set (names + sha256 of every regular file in the unit
            dir, excluding ``*.stale`` / ``*.tmp-*``); legitimately fails whenever
            ``/inputs/run_id`` differs and says so in the report (``note`` +
            ``summary.run_id_differs``). DEFERRED: a comparison of captured
            stdout/stderr/exit is not built; the gate records only ``exit_code`` and
            ``stderr_tail`` in ``units.jsonl``, which raw mode does not read.
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
import itertools
import json
import os
import re
import shutil
import tempfile
from collections import Counter, OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

POLICY_DIR = Path(__file__).resolve().parent / "normalization"

_ALLOWED_LEAF_KEYS = {"pointer", "pointer_glob", "shape", "equals", "sha256_of", "rewrite", "verify_values", "note"}
_ALLOWED_REWRITES = {"strip_root_prefix", "strip_root_prefix_keys"}
_ALLOWED_VERIFY = {"sha256_of_key"}
_SHA256_RX = re.compile(r"^[0-9a-f]{64}$")
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
    for key in ("shape", "rewrite", "equals", "sha256_of", "verify_values", "note"):
        if key in leaf and not isinstance(leaf[key], str):
            raise PolicyError(f"leaf {idx}: {key} must be a string")
    if "rewrite" in leaf and leaf["rewrite"] not in _ALLOWED_REWRITES:
        raise PolicyError(f"leaf {idx}: rewrite must be one of {sorted(_ALLOWED_REWRITES)}")
    if "verify_values" in leaf:
        if leaf["verify_values"] not in _ALLOWED_VERIFY:
            raise PolicyError(f"leaf {idx}: verify_values must be one of {sorted(_ALLOWED_VERIFY)}")
        if leaf.get("rewrite") != "strip_root_prefix_keys":
            raise PolicyError(f"leaf {idx}: verify_values requires rewrite strip_root_prefix_keys")
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


# ---- strict comparison ------------------------------------------------------

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


def json_equal(a: Any, b: Any) -> bool:
    """Equality with JSON kinds kept apart: true/1 and false/0 differ (Python's bool is an int),
    while 1 and 1.0 stay equal (one JSON number kind)."""
    return _kind(a) == _kind(b) and a == b


class _Ctx:
    __slots__ = ("unit", "analyzer", "key_order", "deltas", "masked", "violations")

    def __init__(self, unit, analyzer, key_order):
        self.unit, self.analyzer, self.key_order = unit, analyzer, key_order
        self.deltas: list[Delta] = []
        self.masked: set[str] = set()      # exact pointers masked by policy
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


def _prefix_set(p: Any) -> tuple[str, ...]:
    """One side's root prefixes: a string or a sequence of strings (as-given + resolved forms)."""
    items = [p] if isinstance(p, str) else list(p or ())
    out = []
    for x in items:
        x = x.rstrip("/") if x != "/" else x
        if x and x not in out:
            out.append(x)
    return tuple(out)


def _strip_ex(s: Any, prefixes: tuple[str, ...]) -> tuple[Any, bool]:
    """Strip the first prefix that matches on a path boundary (``s == pre`` or ``pre + "/"``)."""
    if isinstance(s, str):
        for pre in prefixes:
            if s == pre or s.startswith(pre + "/"):
                return s[len(pre):], True
    return s, False


def _strip(s: Any, prefixes: tuple[str, ...]) -> Any:
    return _strip_ex(s, prefixes)[0]


def _apply_policy(a: Any, b: Any, policy: Policy, ctx: _Ctx,
                  root_prefixes: tuple[str, str] | None = None) -> tuple[Any, Any]:
    """Apply exact-leaf masking and rewrites on deep copies; record masks/violations in ctx."""
    a = copy.deepcopy(a)
    b = copy.deepcopy(b)
    rewrites = any(lf.get("rewrite") for lf in policy.leaves)
    if root_prefixes is not None:
        prefixes = (_prefix_set(root_prefixes[0]), _prefix_set(root_prefixes[1]))
    elif len(policy.root_prefixes) >= 2:
        prefixes = (_prefix_set(policy.root_prefixes[0]), _prefix_set(policy.root_prefixes[1]))
    else:
        prefixes = ((), ())
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
                verify = leaf.get("verify_values")
                verified: list[set] = [set(), set()]
                for si, (side, doc, found, val, pre) in enumerate(
                        (("a", a, fa, va, prefixes[0]), ("b", b, fb, vb, prefixes[1]))):
                    if not found:
                        continue
                    if not isinstance(val, dict):
                        ctx.violations.append(f"{ctx.unit} {ptr}: strip_root_prefix_keys needs a dict")
                        continue
                    new: dict = {}
                    for k, v in val.items():
                        nk, stripped = _strip_ex(k, pre)
                        if nk in new:
                            ctx.violations.append(
                                f"{ctx.unit} {ptr}: strip_root_prefix_keys collision on {nk}")
                            continue
                        new[nk] = v
                        if verify and stripped:
                            # verify-then-mask: only a slot-rooted key whose value is the sha256 of
                            # the file it names; keys outside the slot roots stay compared
                            err = _verify_sha256_of_key(k, nk, v, pre)
                            if err:
                                ctx.violations.append(f"{ctx.unit} {join_pointer(ptr, nk)}: {err} on side {side}")
                            else:
                                verified[si].add(nk)
                    _set_pointer(doc, ptr, new)
                for nk in sorted(verified[0] & verified[1]):
                    ctx.masked.add(join_pointer(ptr, nk))
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
                    cand = [p] + [x + p for x in pre] if found and isinstance(p, str) else []
                    target = next((c for c in cand if c and Path(c).is_file()), None)
                    if target is None:
                        ctx.violations.append(f"{ctx.unit} {ptr}: sha256_of {sib}: linked file missing on side {side}")
                        continue
                    if hashlib.sha256(Path(target).read_bytes()).hexdigest() != v:
                        ctx.violations.append(f"{ctx.unit} {ptr}: sha256_of {sib} mismatch on side {side}")
    return a, b


def _verify_sha256_of_key(key: str, stripped_key: str, value: Any, prefixes: tuple[str, ...]) -> str | None:
    """None when ``value`` is a sha256 hex digest equal to the file ``key`` names (tried as
    recorded, then re-rooted under each of this side's prefixes); else a violation reason."""
    if not isinstance(value, str) or not _SHA256_RX.match(value):
        return f"source hash value {value!r} fails shape ^[0-9a-f]{{64}}$"
    target = next((c for c in [key] + [x + stripped_key for x in prefixes] if Path(c).is_file()), None)
    if target is None:
        return "verify_values sha256_of_key: keyed file missing"
    if _sha256(Path(target)) != value:
        return "verify_values sha256_of_key: mismatch"
    return None


def compare_strict(a: Any, b: Any, policy: Policy | None, *, unit: str, analyzer: str,
                   key_order: bool = False,
                   root_prefixes: tuple | None = None) -> tuple[list[Delta], list[str]]:
    """Recursive field comparison. Returns (deltas, policy_violations).

    Two NaNs compare equal. ``key_order=True`` emits a ``key_order`` delta for any
    dict whose key sequence differs, including when the key sets differ.
    ``root_prefixes`` = (a, b), each a root string or a sequence of root strings,
    overrides ``policy.root_prefixes``; a prefix strips only on a path boundary.
    """
    ctx = _Ctx(unit, analyzer, key_order)
    if policy is not None:
        a, b = _apply_policy(a, b, policy, ctx, root_prefixes)
    _walk(a, b, "", ctx)
    return ctx.deltas, ctx.violations


_NUM_TOKEN = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare_raw(a_path: Path, b_path: Path, *, unit: str, analyzer: str, path: str = "") -> list[Delta]:
    """Byte identity. One ``bytes`` delta when the files differ; additionally one
    ``lexical_numeric`` delta when the parsed JSON is equal but number spelling differs.

    ``lexical_numeric`` is complete and reorder-safe: ``before``/``after`` are the sorted
    multiset differences of the number tokens (a pure key reorder yields nothing)."""
    ab, bb = Path(a_path).read_bytes(), Path(b_path).read_bytes()
    if ab == bb:
        return []
    out = [Delta(unit, analyzer, path, "bytes", hashlib.sha256(ab).hexdigest(), hashlib.sha256(bb).hexdigest())]
    try:
        pa, pb = json.loads(ab), json.loads(bb)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return out
    if pa == pb:
        ca = Counter(_NUM_TOKEN.findall(ab.decode("utf-8", "replace")))
        cb = Counter(_NUM_TOKEN.findall(bb.decode("utf-8", "replace")))
        before, after = sorted((ca - cb).elements()), sorted((cb - ca).elements())
        if before or after:
            out.append(Delta(unit, analyzer, path, "lexical_numeric", before, after))
    return out


RAW_NOTE = ("raw compares bytes of every file in each unit directory (snap.json and sidecars, "
            "excluding *.stale and *.tmp-*). Analyzer envelopes embed /inputs/run_id, so any two "
            "runs differ in raw mode even on identical code; summary.run_id_differs counts those "
            "units. The strict verdict is the field-level claim.")


def _unit_files(unit_dir: Path) -> dict[str, Path]:
    """Regular files directly in a unit dir, minus quarantined (*.stale) and in-flight (*.tmp-*) files."""
    return {f.name: f for f in sorted(Path(unit_dir).iterdir())
            if f.is_file() and not f.name.endswith(".stale") and ".tmp-" not in f.name}


def compare_raw_unit(a_dir: Path, b_dir: Path, *, unit: str, analyzer: str) -> list[Delta]:
    """Raw mode for one unit: the file-name set (``added``/``removed`` at ``/<file>``) plus
    ``bytes`` (and ``lexical_numeric``) per differing file, path naming the file."""
    fa, fb = _unit_files(a_dir), _unit_files(b_dir)
    out: list[Delta] = []
    for name in sorted(set(fa) | set(fb)):
        ptr = join_pointer("", name)
        if name not in fb:
            out.append(Delta(unit, analyzer, ptr, "removed", _sha256(fa[name]), None))
        elif name not in fa:
            out.append(Delta(unit, analyzer, ptr, "added", None, _sha256(fb[name])))
        else:
            out.extend(compare_raw(fa[name], fb[name], unit=unit, analyzer=analyzer, path=ptr))
    return out


def _run_id_of(path: Path) -> tuple[bool, Any]:
    try:
        return resolve_pointer(json.loads(Path(path).read_text(encoding="utf-8")), "/inputs/run_id")
    except (OSError, ValueError):
        return False, None


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
    return {k: data.get(k) for k in ("run_id", "profile", "harness", "product", "selection", "normalization_policy")}


def _root_forms(root: Path) -> tuple[str, ...]:
    """As-given (absolute, symlinks kept) and fully resolved forms of a slot root."""
    given, resolved = os.path.abspath(str(root)), str(Path(root).resolve())
    return (given,) if given == resolved else (given, resolved)


# A report keeps its delta lists inline up to this many deltas; past it (when the caller gave
# sidecar paths) they go to JSONL sidecars named in the report.
INLINE_DELTAS_MAX = 200_000
# Units queued per worker: workers never wait on the parent, and finished results stay small
# (each worker spools its unit's deltas to disk and returns counts and file ranges only).
_IN_FLIGHT_PER_JOB = 4

# Per-process state of a comparison worker: spool dir, open spool files, budget classes.
_WORKER: dict = {}


def _init_worker(spool_dir: str, budget: dict | None) -> None:
    _close_worker()
    _WORKER["spool"] = Path(spool_dir)
    _WORKER["files"] = {}
    if budget is not None:
        _WORKER["classes"] = budget["classes"]
        _WORKER["preds"] = _predicates(budget)


def _close_worker() -> None:
    for fh in _WORKER.get("files", {}).values():
        fh.close()
    _WORKER.clear()


def _spool(kind: str, lines: list[str]) -> tuple[str, int, int] | None:
    """Append lines to this process's spool file of ``kind``; returns (file name, offset, length)."""
    if not lines:
        return None
    fh = _WORKER["files"].get(kind)
    if fh is None:
        fh = _WORKER["files"][kind] = open(_WORKER["spool"] / f"{os.getpid()}.{kind}", "ab")
    off = fh.tell()
    data = "".join(lines).encode("utf-8")
    fh.write(data)
    fh.flush()
    return fh.name.rsplit("/", 1)[-1], off, len(data)


def sidecar_path(report_path: Path, kind: str) -> Path:
    """``<report stem>.<kind>.jsonl`` beside a report (kind: deltas, residuals, claims)."""
    p = Path(report_path)
    return p.with_name(f"{p.stem}.{kind}.jsonl")


def iter_report_deltas(report: dict, report_dir: Path):
    """The delta dicts of a field report, inline or from its ``deltas_file`` sidecar
    (a name relative to the report's directory)."""
    if report.get("deltas") is not None:
        yield from report["deltas"]
    elif report.get("deltas_file"):
        with open(Path(report_dir) / report["deltas_file"], encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    yield json.loads(line)


def _compare_unit(task: tuple) -> tuple:
    """One unit of the comparison (module-level so ProcessPoolExecutor can pickle it):
    (rec, violations, run_id_differs, info). The unit's deltas go to the worker's spool;
    ``info`` holds their count, per-op counts, spool ranges and, with a budget, the
    per-class claim counts and residual count."""
    unit, analyzer, pa, pb, rec, mode, policy, key_order, prefixes = task
    viol: list[str] = []
    run_id_differs = False
    docs = None
    if mode == "raw":
        ds = compare_raw_unit(pa.parent, pb.parent, unit=unit, analyzer=analyzer)
        if any(d.path == "/snap.json" and d.op == "bytes" for d in ds):
            run_id_differs = _run_id_of(pa) != _run_id_of(pb)
    else:
        docs = []
        for side, p in (("a", pa), ("b", pb)):
            try:
                docs.append(json.loads(p.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError, UnicodeDecodeError):
                return dict(rec, status=f"parse_error_{side}"), [], False, None
        ds, viol = compare_strict(docs[0], docs[1], policy, unit=unit, analyzer=analyzer,
                                  key_order=key_order, root_prefixes=prefixes)
    lines = [json.dumps(d.to_json()) + "\n" for d in ds]
    info = {"n": len(ds), "by_op": dict(Counter(d.op for d in ds)), "deltas": _spool("deltas", lines)}
    if "classes" in _WORKER and ds:
        claims = _claim_indices(ds, _WORKER["classes"], _WORKER["preds"], {unit: (docs[0], docs[1])})
        info["claims"] = _spool("claims", [json.dumps(c) + "\n" for c in claims])
        info["residuals"] = _spool("residuals", [ln for ln, c in zip(lines, claims) if not c])
        info["class_counts"] = dict(Counter(i for c in claims for i in c))
        info["n_resid"] = sum(1 for c in claims if not c)
    return rec, viol, run_id_differs, info


def _results(work: list, jobs: int, spool: Path, budget: dict | None):
    """(index, _compare_unit result) for every task, in completion order. With jobs > 1, a
    process pool holding at most jobs * _IN_FLIGHT_PER_JOB unfinished units."""
    if jobs <= 1 or len(work) <= 1:
        _init_worker(str(spool), budget)
        try:
            for i, t in enumerate(work):
                yield i, _compare_unit(t)
        finally:
            _close_worker()
        return
    from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
    with ProcessPoolExecutor(max_workers=jobs, initializer=_init_worker, initargs=(str(spool), budget)) as pool:
        it = iter(enumerate(work))
        pending: dict = {}

        def fill():
            for i, t in itertools.islice(it, jobs * _IN_FLIGHT_PER_JOB - len(pending)):
                pending[pool.submit(_compare_unit, t)] = i
        fill()
        while pending:
            done, _ = wait(pending, return_when=FIRST_COMPLETED)
            for f in done:
                yield pending.pop(f), f.result()
            fill()


class _SpoolReader:
    def __init__(self, spool: Path):
        self.spool, self.files = spool, {}

    def read(self, ref) -> bytes:
        if ref is None:
            return b""
        name, off, n = ref
        fh = self.files.get(name)
        if fh is None:
            fh = self.files[name] = open(self.spool / name, "rb")
        fh.seek(off)
        return fh.read(n)

    def lines(self, ref) -> list:
        return [json.loads(x) for x in self.read(ref).splitlines()]

    def close(self) -> None:
        for fh in self.files.values():
            fh.close()


def _report_header(a_root: Path, b_root: Path, mode: str, policy: Policy | None, key_order: bool) -> dict:
    return {"report_version": 1, "mode": mode, "policy": policy.name if policy else None,
            "key_order": key_order, "a_root": str(a_root), "b_root": str(b_root),
            "identity": {"a": _manifest_identity(a_root), "b": _manifest_identity(b_root)}}


def _compare(a_root: Path, b_root: Path, *, mode: str, policy: Policy | None, key_order: bool,
             root_prefixes: tuple | None, jobs: int, deltas_path: Path | None,
             tally: "_BudgetTally | None" = None, residuals_path: Path | None = None,
             claims_path: Path | None = None) -> dict:
    """The comparison pass. Workers spool each unit's deltas (and, with ``tally``, its budget
    claims) to a scratch dir and return counts; the parent reassembles everything in sorted
    unit order, so the report is byte-identical for any ``jobs``. Inline when there is no
    ``deltas_path`` or at most INLINE_DELTAS_MAX deltas, else copied to the sidecars."""
    if mode not in ("raw", "strict", "budgeted"):
        raise ValueError(f"mode must be raw|strict|budgeted, got {mode!r}")
    prefixes = root_prefixes or (_root_forms(a_root), _root_forms(b_root))
    a_root, b_root = Path(a_root).resolve(), Path(b_root).resolve()
    a_units = {u: (an, p) for u, an, p in iter_units(a_root)}
    b_units = {u: (an, p) for u, an, p in iter_units(b_root)}
    tasks = []
    for unit in sorted(set(a_units) | set(b_units)):
        analyzer = (a_units.get(unit) or b_units.get(unit))[0]
        rec = {"unit": unit, "analyzer": analyzer,
               "a": a_units[unit][1].relative_to(a_root).as_posix() if unit in a_units else None,
               "b": b_units[unit][1].relative_to(b_root).as_posix() if unit in b_units else None,
               "status": "compared", "delta_count": 0}
        if unit not in a_units or unit not in b_units:
            rec["status"] = "missing_a" if unit not in a_units else "missing_b"
            tasks.append(rec)
            continue
        tasks.append((unit, analyzer, a_units[unit][1], b_units[unit][1], rec, mode, policy, key_order, prefixes))
    work = [t for t in tasks if isinstance(t, tuple)]
    for p in (deltas_path, residuals_path, claims_path):
        if p is not None:
            Path(p).unlink(missing_ok=True)    # a stale sidecar must not outlive an inline report
    spool = Path(tempfile.mkdtemp(prefix=".field_compare-", dir=Path(deltas_path).parent if deltas_path else None))
    reader = _SpoolReader(spool)
    try:
        results: list = [None] * len(work)
        for i, res in _results(work, jobs, spool, tally.budget if tally is not None else None):
            results[i] = res
        units_out, violations, kept = [], [], []
        counts, by_op, by_an = Counter(), Counter(), Counter()
        done = iter(results)
        for t in tasks:
            if isinstance(t, dict):
                counts["missing"] += 1
                units_out.append(t)
                continue
            rec, viol, rid, info = next(done)
            units_out.append(rec)
            if rec["status"] != "compared":
                counts["parse_errors"] += 1
                continue
            violations.extend(viol)
            rec["delta_count"] = info["n"]
            counts["compared"] += 1
            counts["identical" if not info["n"] else "with_deltas"] += 1
            counts["run_id_differs"] += int(rid)
            counts["deltas"] += info["n"]
            by_op.update(info["by_op"])
            if info["n"]:
                by_an[rec["analyzer"]] += info["n"]
                kept.append((rec, info))
        inline = deltas_path is None or counts["deltas"] <= INLINE_DELTAS_MAX
        deltas = None
        if inline:
            deltas = []
            for rec, info in kept:
                ds = reader.lines(info["deltas"])
                deltas.extend(ds)
                if tally is not None:
                    for d, idx in zip(ds, reader.lines(info["claims"])):
                        tally.add(d, idx)
        else:
            with open(deltas_path, "wb") as out:
                for _, info in kept:
                    out.write(reader.read(info["deltas"]))
            if tally is not None:
                tally.spill(kept, reader, residuals_path, claims_path)
    finally:
        reader.close()
        shutil.rmtree(spool, ignore_errors=True)
    summary = {"units": len(units_out), "compared": counts["compared"], "identical": counts["identical"],
               "with_deltas": counts["with_deltas"], "missing": counts["missing"],
               "parse_errors": counts["parse_errors"], "deltas": counts["deltas"],
               "by_op": dict(sorted(by_op.items())), "by_analyzer": dict(sorted(by_an.items()))}
    if mode == "raw":
        summary["run_id_differs"] = counts["run_id_differs"]
    # zero compared units is no evidence of equality (ruling R3)
    if counts["missing"] or counts["parse_errors"] or violations or not counts["compared"]:
        verdict = "error"
    elif counts["deltas"]:
        verdict = "deltas"
    else:
        verdict = "clean"
    report = {**_report_header(a_root, b_root, mode, policy, key_order),
              "units": units_out, "deltas": deltas,
              "deltas_file": None if inline else Path(deltas_path).name,
              "policy_violations": violations, "summary": summary, "budget": None, "verdict": verdict}
    if mode == "raw":
        report["note"] = RAW_NOTE
    return report


def compare_trees(a_root: Path, b_root: Path, *, mode: str, policy: Policy | None,
                  key_order: bool = False,
                  root_prefixes: tuple | None = None, jobs: int = 1,
                  deltas_path: Path | None = None) -> dict:
    """Compare two snap trees. ``root_prefixes`` = (a, b), each a string or a sequence of
    strings; by default each side's as-given and resolved root forms. ``jobs`` > 1 runs the
    per-unit comparisons in a process pool; results are reassembled in sorted unit order,
    so the report is byte-identical for any ``jobs``. With ``deltas_path``, a report of more
    than INLINE_DELTAS_MAX deltas holds ``deltas: null`` and names that JSONL file in
    ``deltas_file`` (read it back with iter_report_deltas)."""
    return _compare(a_root, b_root, mode=mode, policy=policy, key_order=key_order,
                    root_prefixes=root_prefixes, jobs=jobs, deltas_path=deltas_path)


# ---- budgets ----------------------------------------------------------------

SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}
_CLASS_KEYS = {"id", "analyzer", "path_glob", "op", "where", "direction", "value_relation",
               "unit_bound", "predicate", "evidence", "expected_magnitude"}
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
    if "expected_magnitude" in c:
        em = c["expected_magnitude"]
        if isinstance(em, bool) or not isinstance(em, int) or em < 0:
            raise BudgetError(f"class {cid}: expected_magnitude must be a non-negative int")


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


def _predicates(budget: dict) -> list:
    return [_load_predicate(c["predicate"], str(c.get("id"))) if c.get("predicate") else None
            for c in budget["classes"]]


def _claim_indices(deltas: list[Delta], classes: list, preds: list, docs) -> list[list[int]]:
    """Per delta, the indices of every class whose selectors ALL match it."""
    return [[i for i, c in enumerate(classes) if _class_claims(c, d, docs, preds[i])] for d in deltas]


class _BudgetTally:
    """Claims accumulated delta by delta (``add``) or unit by unit (``spill``); unit bounds and
    magnitudes are judged on the totals, so feeding it one unit at a time gives the same
    result as one call over every delta."""

    def __init__(self, budget: dict):
        self.budget = budget
        n = len(budget["classes"])
        self.counts = [0] * n
        self.units: list[set] = [set() for _ in range(n)]
        self.claimed: list[list] | None = [[] for _ in range(n)]
        self.residuals: list | None = []
        self.residual_count = 0
        self.claims_file = self.residuals_file = None

    def add(self, delta: dict, idx: list[int]) -> None:
        for i in idx:
            self.counts[i] += 1
            self.units[i].add(delta["unit"])
            self.claimed[i].append(delta)
        if not idx:
            self.residuals.append(delta)
            self.residual_count += 1

    def spill(self, kept: list, reader, residuals_path: Path, claims_path: Path) -> None:
        """Per-class lists dropped (``claimed: null``); residual deltas copied to
        ``residuals_path`` and per-unit claim rows written to ``claims_path``, in unit order."""
        ids = [c["id"] for c in self.budget["classes"]]
        self.claimed = self.residuals = None
        with open(residuals_path, "wb") as res, open(claims_path, "w", encoding="utf-8") as rows:
            for rec, info in kept:
                for i, n in info["class_counts"].items():
                    self.counts[i] += n
                    self.units[i].add(rec["unit"])
                self.residual_count += info["n_resid"]
                res.write(reader.read(info["residuals"]))
                rows.write(json.dumps({"unit": rec["unit"], "analyzer": rec["analyzer"], "deltas": info["n"],
                                       "claimed": {ids[i]: n for i, n in sorted(info["class_counts"].items())},
                                       "residuals": info["n_resid"]}) + "\n")
        self.residuals_file, self.claims_file = Path(residuals_path).name, Path(claims_path).name

    def result(self, missing_units: int = 0) -> dict:
        budget, classes = self.budget, self.budget["classes"]
        violations, bound_status, over_budget = [], {}, []
        for i, c in enumerate(classes):
            bound = (c.get("unit_bound") or {}).get("max_units")
            n_units = len(self.units[i])
            ok = bound is None or n_units <= bound
            mag = c.get("expected_magnitude")
            n_deltas = self.counts[i]
            over = mag is not None and n_deltas > 2 * mag
            bound_status[c["id"]] = {"max_units": bound, "units": n_units, "ok": ok,
                                     "expected_magnitude": mag, "deltas": n_deltas, "over_budget": over}
            if not ok:
                violations.append(f"class {c['id']} claimed {n_units} units > max_units {bound}")
            if over:
                over_budget.append(c["id"])
                violations.append(f"class {c['id']} claimed {n_deltas} deltas > 2x expected_magnitude {mag} (over_budget)")
        allowed_missing = int(budget.get("unexplained_missing_units_allowed", 0))
        if missing_units > allowed_missing:
            violations.append(f"{missing_units} missing units > unexplained_missing_units_allowed {allowed_missing}")
        clean = self.residual_count <= int(budget.get("unexplained_deltas_allowed", 0)) and not violations
        return {"budget_id": budget["budget_id"], "clean": clean,
                "claimed": None if self.claimed is None else
                {c["id"]: self.claimed[i] for i, c in enumerate(classes)},
                "claimed_counts": {c["id"]: self.counts[i] for i, c in enumerate(classes) if self.counts[i]},
                "claimed_units": {c["id"]: len(self.units[i]) for i, c in enumerate(classes) if self.counts[i]},
                "bound_status": bound_status, "over_budget": sorted(over_budget),
                "residuals": self.residuals, "violations": violations,
                "residual_count": self.residual_count, "claims_file": self.claims_file,
                "residuals_file": self.residuals_file}


def evaluate_budget(deltas: list[Delta], budget: dict, *, docs: dict | None = None,
                    missing_units: int = 0) -> dict:
    """Classify deltas against budget classes. A delta is claimed iff ALL selectors of some class match."""
    tally = _BudgetTally(budget)
    for d, idx in zip(deltas, _claim_indices(deltas, budget["classes"], _predicates(budget), docs)):
        tally.add(d.to_json(), idx)
    return tally.result(missing_units)


class _LazyDocs:
    """``{unit: (a_doc, b_doc)}`` for compared units WITH deltas, loaded on first access and
    kept for the most recent few units only. Deltas arrive grouped per unit in sorted order,
    so a small window serves them without holding every delta unit's pair in memory
    (an output-changing round can touch ten thousand units)."""

    _WINDOW = 4

    def __init__(self, report: dict, a_root: Path, b_root: Path):
        self._paths = {u["unit"]: (Path(a_root) / u["a"], Path(b_root) / u["b"]) for u in report["units"]
                       if u["status"] == "compared" and u.get("delta_count", 0) > 0}
        self._loaded: "OrderedDict[str, tuple]" = OrderedDict()

    def __len__(self) -> int:
        return len(self._paths)

    def __iter__(self):
        return iter(self._paths)

    def __contains__(self, unit) -> bool:
        return unit in self._paths

    def get(self, unit, default=None):
        if unit not in self._paths:
            return default
        hit = self._loaded.get(unit)
        if hit is None:
            pa, pb = self._paths[unit]
            hit = (json.loads(pa.read_text(encoding="utf-8")), json.loads(pb.read_text(encoding="utf-8")))
            self._loaded[unit] = hit
            while len(self._loaded) > self._WINDOW:
                self._loaded.popitem(last=False)
        else:
            self._loaded.move_to_end(unit)
        return hit

    def __getitem__(self, unit):
        hit = self.get(unit)
        if hit is None:
            raise KeyError(unit)
        return hit


def docs_for_report(report: dict, a_root: Path, b_root: Path) -> _LazyDocs:
    """Mapping of (a_doc, b_doc) for compared units WITH deltas only (evaluate_budget consults
    docs[delta.unit] alone), so budget `where`/predicates can resolve findings without
    holding the whole corpus in memory. Pairs load on access, a few units at a time."""
    return _LazyDocs(report, a_root, b_root)


def _sha_agrees(budget_sha: Any, run_sha: Any) -> bool:
    return isinstance(budget_sha, str) and isinstance(run_sha, str) and bool(budget_sha) and bool(run_sha) \
        and (run_sha.startswith(budget_sha) or budget_sha.startswith(run_sha))


def check_budget_identity(budget: dict, strict_report: dict) -> None:
    """Raise BudgetError when the budget names a different normalization policy or product
    SHAs than this run. Policy is checked against the report's policy and, with a gate
    manifest, the manifest's; SHAs only when a manifest identity is present (prefixes allowed)."""
    bp = budget.get("normalization_policy")
    if bp is not None and bp != strict_report.get("policy"):
        raise BudgetError(f"budget {budget['budget_id']}: normalization_policy {bp!r} != "
                          f"comparator policy {strict_report.get('policy')!r}")
    for ident in (strict_report.get("identity") or {}).values():
        if not ident:
            continue
        mp = ident.get("normalization_policy")
        if bp is not None and mp is not None and mp != bp:
            raise BudgetError(f"budget {budget['budget_id']}: normalization_policy {bp!r} != manifest {mp!r}")
        product = ident.get("product") or {}
        for slot in ("baseline", "candidate"):
            want = budget.get(f"{slot}_sha")
            have = (product.get(slot) or {}).get("sha")
            if want is not None and have is not None and not _sha_agrees(want, have):
                raise BudgetError(f"budget {budget['budget_id']}: {slot}_sha {want!r} does not match "
                                  f"manifest {slot} sha {have!r}")


def _budgeted(strict_report: dict, budget: dict, tally: _BudgetTally) -> dict:
    """Budgeted report from a strict report and its tally; verdict precedence
    error > over_budget > residuals > clean."""
    s = strict_report["summary"]
    ev = tally.result(missing_units=s["missing"])
    missing_allowed = int(budget.get("unexplained_missing_units_allowed", 0))
    hard_error = s["missing"] > missing_allowed or s["parse_errors"] > 0 or bool(strict_report["policy_violations"])
    if hard_error:
        verdict = "error"
    elif ev["over_budget"]:
        verdict = "over_budget"
    else:
        verdict = "clean" if ev["clean"] else "residuals"
    return dict(strict_report, mode="budgeted", budget=ev, verdict=verdict)


def budgeted_report(strict_report: dict, budget: dict, a_root: Path, b_root: Path) -> dict:
    """Budgeted field report over a finished strict report with inline deltas: identity check,
    docs for units with deltas, the same per-delta claims as compare_budgeted."""
    check_budget_identity(budget, strict_report)
    if strict_report.get("deltas") is None:
        raise ValueError("strict report keeps its deltas in a sidecar; use compare_budgeted "
                         "(compare_snap_trees.py --mode budgeted) to budget it")
    tally = _BudgetTally(budget)
    classes, preds = budget["classes"], _predicates(budget)
    docs = docs_for_report(strict_report, a_root, b_root)
    for d in strict_report["deltas"]:
        tally.add(d, _claim_indices([Delta(**d)], classes, preds, docs)[0])
    return _budgeted(strict_report, budget, tally)


def compare_budgeted(a_root: Path, b_root: Path, budget: dict, *, policy: Policy | None,
                     key_order: bool = False, root_prefixes: tuple | None = None, jobs: int = 1,
                     deltas_path: Path | None = None, residuals_path: Path | None = None,
                     claims_path: Path | None = None, resolved_units=()) -> tuple[dict, dict]:
    """(strict report, budgeted report) from ONE pass: each worker classifies its unit's
    deltas against the budget while it holds the unit's documents, so no delta list is
    rebuilt. Unit bounds and magnitudes are judged on the totals. ``resolved_units`` are
    exempt from the missing count (see _exempt_resolved). A budget whose policy/SHAs
    contradict the run, or an unloadable predicate, raises BudgetError before any unit is
    compared. Past INLINE_DELTAS_MAX deltas (with sidecar paths) the budget section holds
    ``claimed: null`` and ``residuals: null`` and names ``residuals_file`` / ``claims_file``
    (per-unit rows ``{unit, analyzer, deltas, claimed: {class: n}, residuals}``)."""
    if deltas_path is not None and (residuals_path is None or claims_path is None):
        raise ValueError("deltas_path needs residuals_path and claims_path")
    check_budget_identity(budget, _report_header(Path(a_root).resolve(), Path(b_root).resolve(),
                                                 "strict", policy, key_order))
    _predicates(budget)
    tally = _BudgetTally(budget)
    strict = _compare(a_root, b_root, mode="strict", policy=policy, key_order=key_order,
                      root_prefixes=root_prefixes, jobs=jobs, deltas_path=deltas_path, tally=tally,
                      residuals_path=residuals_path, claims_path=claims_path)
    strict = _exempt_resolved(strict, set(resolved_units))
    return strict, _budgeted(strict, budget, tally)


def _slots(gate_root: Path) -> tuple[Path, Path]:
    g = Path(gate_root)
    for a, b in (("baseline", "candidate"), ("v131", "v14")):
        if (g / a).is_dir() and (g / b).is_dir():
            return g / a, g / b
    for a, b in (("baseline", "candidate"), ("v131", "v14")):
        if (g / a).is_dir() and not (g / b).is_dir():
            raise FileNotFoundError(f"gate {g}: slot {a!r} present but {b!r} missing")
    raise FileNotFoundError(f"gate {g}: no baseline/candidate (or v131/v14) slot pair")


def _exempt_resolved(report: dict, resolved_units) -> dict:
    """Take units the gate judged resolved debts (ledgered failures the candidate fixed, so
    present on one side only) out of the missing count, listed as summary.resolved_missing,
    and recompute the verdict with compare_trees' rule."""
    names = sorted(u["unit"] for u in report["units"]
                   if u["status"] in ("missing_a", "missing_b") and u["unit"] in resolved_units)
    if not names:
        return report
    s = report["summary"]
    s["missing"] -= len(names)
    s["resolved_missing"] = names
    if s["missing"] or s["parse_errors"] or report["policy_violations"] or not s["compared"]:
        report["verdict"] = "error"
    else:
        report["verdict"] = "deltas" if s["deltas"] else "clean"
    return report


def run_modes(gate_root: Path, *, budget_path: Path | None = None, key_order: bool = False,
              policy_name: str = "volatile-leaves-v1", write_reports: bool = True, jobs: int = 1,
              resolved_units=()) -> dict:
    """Run raw + strict (+ budgeted) over a gate's two slots. Returns the dict the gate
    stores under rollup['modes']; writes field_report_<mode>.json beside the slots.
    `resolved_units` (gate_pass.resolved_debts) are exempt from the strict missing count.
    A budget whose policy/SHAs contradict the gate manifest raises BudgetError."""
    g = Path(gate_root)
    a_root, b_root = _slots(g)
    policy = load_policy(policy_name)
    budget = load_budget(Path(budget_path)) if budget_path is not None else None
    out: dict = {"policy": policy.name, "key_order": key_order}

    def side(name, kind):
        return sidecar_path(g / f"field_report_{name}.json", kind) if write_reports else None

    if write_reports:
        for name in ("raw", "strict", "budgeted"):     # budget predicates may read a strict report
            (g / f"field_report_{name}.json").unlink(missing_ok=True)
    if budget is None:
        strict = _exempt_resolved(compare_trees(a_root, b_root, mode="strict", policy=policy, key_order=key_order,
                                                jobs=jobs, deltas_path=side("strict", "deltas")),
                                  set(resolved_units))
        budgeted = None
    else:
        strict, budgeted = compare_budgeted(a_root, b_root, budget, policy=policy, key_order=key_order, jobs=jobs,
                                            deltas_path=side("strict", "deltas"),
                                            residuals_path=side("budgeted", "residuals"),
                                            claims_path=side("budgeted", "claims"), resolved_units=resolved_units)
    raw = compare_trees(a_root, b_root, mode="raw", policy=None, jobs=jobs, deltas_path=side("raw", "deltas"))
    if write_reports:
        (g / "field_report_raw.json").write_text(json.dumps(raw, indent=1), encoding="utf-8")
        (g / "field_report_strict.json").write_text(json.dumps(strict, indent=1), encoding="utf-8")
    out["raw"] = {"verdict": raw["verdict"], "report": "field_report_raw.json", "summary": raw["summary"]}
    out["strict"] = {"verdict": strict["verdict"], "report": "field_report_strict.json",
                     "summary": strict["summary"], "policy_violations": len(strict["policy_violations"])}

    if budgeted is None:
        out["budgeted"] = {"verdict": "n/a"}
        out["strict_field_clean"] = strict["verdict"] == "clean"
        return out

    ev, verdict = budgeted["budget"], budgeted["verdict"]
    if write_reports:
        (g / "field_report_budgeted.json").write_text(json.dumps(budgeted, indent=1), encoding="utf-8")
    out["budgeted"] = {"verdict": verdict, "report": "field_report_budgeted.json", "budget_id": budget["budget_id"],
                       "claimed_counts": ev["claimed_counts"], "residuals": ev["residual_count"],
                       "violations": len(ev["violations"]), "over_budget": ev["over_budget"]}
    out["strict_field_clean"] = verdict == "clean"
    return out
