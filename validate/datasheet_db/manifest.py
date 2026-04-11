"""Manifest layer: sharded per-record JSON load/save and lookup indexes."""

import json
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent.parent
MANIFEST_DIR = HARNESS_DIR / "reference" / "datasheet_manifest"


def record_path(sha256: str) -> Path:
    """Return the sharded on-disk path for a record keyed by sha256.

    Layout: reference/datasheet_manifest/{sha256[:2]}/{sha256}.json

    Defensively rejects sha values that are obviously too short to be a real
    sha256. The threshold (more than 3 chars) is arbitrary — the sharding
    logic only requires 2 chars for `sha[:2]`. Plan called for `< 3`; raised
    to `<= 3` so the rejection test (`record_path("abc")`) actually fires.
    Real shas are 64 chars, so this guard never trips in production.
    """
    if not isinstance(sha256, str) or len(sha256) <= 3:
        raise ValueError(f"sha256 must be a string of more than 3 chars, got {sha256!r}")
    return MANIFEST_DIR / sha256[:2] / f"{sha256}.json"
