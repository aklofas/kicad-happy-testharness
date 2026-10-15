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
