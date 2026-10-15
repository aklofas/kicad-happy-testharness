"""audit_constants recursion + qualified paths + relocation (A2)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS / "validate"))
import audit_constants as ac  # noqa: E402

pytestmark = pytest.mark.unit

FAKE = HARNESS / "tests" / "fixtures" / "h0" / "plan4" / "fake_product"


def test_iter_constant_records_recurses_with_qualified_paths():
    recs = ac.iter_constant_records(FAKE)
    files = {r["file"] for r in recs}
    assert "skills/kicad/scripts/schematic/reader.py" in files
    assert "skills/kicad/scripts/pcb/reader.py" in files
    names = {(r["file"], r["name"]) for r in recs}
    assert ("skills/kicad/scripts/schematic/reader.py", "SHEET_DEPTH_MAX") in names
    assert ("skills/kicad/scripts/pcb/reader.py", "SHEET_DEPTH_MAX") in names
    assert ("skills/kicad/scripts/validation_detectors.py", "PULLUP_MIN_OHMS") in names


def test_v1_basename_registry_upgrades_when_unambiguous():
    reg = {"version": 1, "last_scan": None, "constants": [
        {"id": "CONST-001", "file": "validation_detectors.py", "scope": "module",
         "name": "PULLUP_MIN_OHMS", "status": "verified", "source": "s"}]}
    scanned = ac.iter_constant_records(FAKE)
    ambiguous = ac.qualify_registry_paths(reg, scanned)
    assert ambiguous == []
    assert reg["version"] == 2
    assert reg["constants"][0]["file"] == "skills/kicad/scripts/validation_detectors.py"


def test_v1_basename_registry_ambiguous_is_reported():
    reg = {"version": 1, "last_scan": None, "constants": [
        {"id": "CONST-002", "file": "reader.py", "scope": "module",
         "name": "SHEET_DEPTH_MAX", "status": "verified", "source": "s"}]}
    ambiguous = ac.qualify_registry_paths(reg, ac.iter_constant_records(FAKE))
    assert ambiguous == [("CONST-002", "reader.py",
                          ["skills/kicad/scripts/pcb/reader.py",
                           "skills/kicad/scripts/schematic/reader.py"])]


def test_relocate_registry_moves_entry_and_keeps_evidence():
    reg = {"version": 2, "last_scan": None, "constants": [
        {"id": "CONST-003", "file": "skills/kicad/scripts/kicad_utils.py", "scope": "module",
         "name": "VALUE_RE", "status": "verified", "source": "KiCad docs", "notes": "n"}]}
    moved = ac.relocate_registry(reg, [
        {"symbol": "kicad_utils.VALUE_RE",
         "old_owner": "skills/kicad/scripts/kicad_utils.py",
         "new_owner": "skills/kicad/scripts/kicad_happy_core/values.py",
         "new_name": "VALUE_RE", "facade_until": None}])
    assert moved == 1
    c = reg["constants"][0]
    assert c["file"] == "skills/kicad/scripts/kicad_happy_core/values.py"
    assert c["status"] == "verified" and c["source"] == "KiCad docs"
    assert c["relocated_from"] == "skills/kicad/scripts/kicad_utils.py"


def test_relocate_renames_symbol_when_new_name_differs():
    reg = {"version": 2, "last_scan": None, "constants": [
        {"id": "CONST-004", "file": "a.py", "scope": "module", "name": "OLD", "status": "verified"}]}
    moved = ac.relocate_registry(reg, [{"symbol": "a.OLD", "old_owner": "a.py",
                                        "new_owner": "b.py", "new_name": "NEW", "facade_until": None}])
    assert moved == 1 and reg["constants"][0]["name"] == "NEW"
