"""Required offline check: scan coverage vs the tracked baseline (A2).

Fails when the product under KICAD_HAPPY_DIR lost emit sites / EQ ids /
constants / files relative to reference/scan_coverage_baseline.json, when an
emit site is unresolved and not ledgered, or when an exception grew.
Re-baseline with `python3 tools/source_scan.py check --product $KICAD_HAPPY_DIR --accept-baseline`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.offline_contract   # needs the real product

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(HARNESS / "tools"))
from tests.product_root import PRODUCT_ROOT  # noqa: E402
import source_scan  # noqa: E402

BASELINE = HARNESS / "reference" / "scan_coverage_baseline.json"


def test_scan_coverage_not_lost():
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    current = source_scan.coverage_snapshot(PRODUCT_ROOT, source_scan.load_exceptions())
    d = source_scan.coverage_diff(baseline, current)
    msg = json.dumps({k: v for k, v in d.items() if k != "clean" and v}, indent=1)
    assert d["clean"], f"scan coverage regressed vs baseline @{baseline['product_sha'][:7]}:\n{msg}"
