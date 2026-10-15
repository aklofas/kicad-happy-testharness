"""audit_equations recursion + EQ identity + relocation vs hash change (A2)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS / "validate"))
import audit_equations as ae  # noqa: E402

FAKE = HARNESS / "tests" / "fixtures" / "h0" / "plan4" / "fake_product"


def test_iter_equations_recurses_with_relative_paths():
    eqs = ae.iter_equations(FAKE)
    by_id = {e["eq_id"]: e for e in eqs}
    assert by_id["EQ-901"]["file"] == "skills/kicad/scripts/validation_detectors.py"
    assert by_id["EQ-901"]["function"] == "divider_ratio"
    assert by_id["EQ-902"]["file"] == "skills/kicad/scripts/pcb/reader.py"
    assert by_id["EQ-902"]["function"] == "pad_area"


def test_update_registry_relocation_keeps_verified():
    scanned = ae.scan_all_tagged(FAKE)
    eq901 = [e for e in scanned if e["id"] == "EQ-901"][0]
    reg = {"version": 1, "last_scan": None, "equations": [{
        "id": "EQ-901", "formula": eq901["formula"], "file": "old/place.py", "line": 1,
        "function": "divider_ratio", "sources": [], "content_hash": eq901["content_hash"],
        "status": "verified", "category": "filter_design", "impact": "high",
        "verification_source": "textbook", "notes": None}]}
    added, updated, removed, relocated = ae.update_registry(reg, scanned)
    e = [x for x in reg["equations"] if x["id"] == "EQ-901"][0]
    assert relocated == 1 and e["status"] == "verified"
    assert e["file"] == "skills/kicad/scripts/validation_detectors.py"
    assert e["relocated_from"] == "old/place.py"


def test_update_registry_hash_change_goes_stale():
    scanned = ae.scan_all_tagged(FAKE)
    reg = {"version": 1, "last_scan": None, "equations": [{
        "id": "EQ-901", "formula": "x", "file": "skills/kicad/scripts/validation_detectors.py",
        "line": 1, "function": "divider_ratio", "sources": [], "content_hash": "sha256:deadbeef",
        "status": "verified", "category": "filter_design", "impact": "high",
        "verification_source": "textbook", "notes": None}]}
    added, updated, removed, relocated = ae.update_registry(reg, scanned)
    e = [x for x in reg["equations"] if x["id"] == "EQ-901"][0]
    assert updated == 1 and relocated == 0 and e["status"] == "stale"
