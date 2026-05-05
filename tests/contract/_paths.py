"""Cross-repo path bridge for the harness contract suite.

HARNESS_ROOT       — this repo's root (this file → parents[2]).
MAIN_REPO_ROOT     — kicad-happy main repo root (KICAD_HAPPY_DIR env, required).

Fixtures live under HARNESS_ROOT (tests/fixtures/...).
Analyzer scripts and main-repo schemas live under MAIN_REPO_ROOT (skills/...).
"""
from __future__ import annotations

import os
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[2]

_kh = os.environ.get("KICAD_HAPPY_DIR")
if not _kh:
    raise RuntimeError(
        "KICAD_HAPPY_DIR env var not set; required to run the contract suite. "
        "Example: KICAD_HAPPY_DIR=/path/to/kicad-happy pytest tests/contract/"
    )
MAIN_REPO_ROOT = Path(_kh).resolve()
