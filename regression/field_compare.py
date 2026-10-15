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

import json
import re
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
            if not tok.isdigit() or int(tok) >= len(cur):
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
            ctx.emit(join_pointer(path, i), "removed", a[i], None)
        for i in range(n, len(b)):
            ctx.emit(join_pointer(path, i), "added", None, b[i])
        return
    if a != b:
        ctx.emit(path, "changed", a, b)


def _apply_policy(a: Any, b: Any, policy: Policy, ctx: _Ctx) -> tuple[Any, Any]:
    """Masking seam; Task 3 replaces this body. No-op while the policy has no leaves."""
    if policy.leaves:
        raise NotImplementedError("policy masking lands in Task 3")
    return a, b


def compare_strict(a: Any, b: Any, policy: Policy | None, *, unit: str, analyzer: str,
                   key_order: bool = False) -> tuple[list[Delta], list[str]]:
    """Recursive field comparison. Returns (deltas, policy_violations)."""
    ctx = _Ctx(unit, analyzer, key_order)
    if policy is not None:
        a, b = _apply_policy(a, b, policy, ctx)
    _walk(a, b, "", ctx)
    return ctx.deltas, ctx.violations
