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


def test_relocate_moves_function_scope_constants_with_the_function():
    old, new = "skills/kicad/scripts/analyze_schematic.py", "skills/kicad/scripts/schematic/sheets.py"
    reg = {"version": 2, "last_scan": None, "constants": [
        {"id": "CONST-010", "file": old, "scope": "_parse_sheet", "function": "_parse_sheet",
         "name": "pin_types", "status": "verified", "source": "KiCad docs"},
        {"id": "CONST-011", "file": old, "scope": "_parse_sheet", "function": "_parse_sheet",
         "name": "_parse_sheet:412", "status": "verified", "source": "s"},
        {"id": "CONST-012", "file": old, "scope": "_parse_sheet.inner", "function": "inner",
         "name": "LIMITS", "status": "unverified"},
        {"id": "CONST-013", "file": old, "scope": "_parse_sheet_extra", "function": "_parse_sheet_extra",
         "name": "keep", "status": "verified"},
        {"id": "CONST-014", "file": old, "scope": "other", "function": "other",
         "name": "keep2", "status": "verified"}]}
    moved = ac.relocate_registry(reg, [{"symbol": "analyze_schematic._parse_sheet",
                                        "old_owner": old, "new_owner": new,
                                        "new_name": "parse_sheet", "facade_until": None}])
    assert moved == 3
    c = {e["id"]: e for e in reg["constants"]}
    assert (c["CONST-010"]["file"], c["CONST-010"]["scope"], c["CONST-010"]["function"],
            c["CONST-010"]["name"]) == (new, "parse_sheet", "parse_sheet", "pin_types")
    assert c["CONST-010"]["status"] == "verified" and c["CONST-010"]["source"] == "KiCad docs"
    assert c["CONST-010"]["relocated_from"] == old
    assert c["CONST-011"]["name"] == "parse_sheet:412" and c["CONST-011"]["scope"] == "parse_sheet"
    assert c["CONST-012"]["scope"] == "parse_sheet.inner" and c["CONST-012"]["function"] == "inner"
    assert c["CONST-013"]["file"] == old and c["CONST-014"]["file"] == old
    assert "relocated_from" not in c["CONST-013"]


def test_relocate_function_same_name_keeps_scope():
    reg = {"version": 2, "last_scan": None, "constants": [
        {"id": "CONST-020", "file": "a.py", "scope": "f", "function": "f", "name": "f:9",
         "status": "verified"},
        {"id": "CONST-021", "file": "a.py", "scope": "f:9", "name": "x", "status": "verified"}]}
    assert ac.relocate_registry(reg, [{"symbol": "a.f", "old_owner": "a.py", "new_owner": "b.py",
                                       "new_name": "f", "facade_until": None}]) == 2
    assert [(e["file"], e["scope"], e["name"]) for e in reg["constants"]] == [
        ("b.py", "f", "f:9"), ("b.py", "f:9", "x")]


def _scanned(name, file, content_hash, entries=None, scope="module"):
    return ac.ConstantInfo(name=name, file=file, line=1, scope=scope, const_type="lookup_table",
                           entry_count=len(entries or {}), content_hash=content_hash,
                           entries=entries)


def test_update_registry_carries_evidence_across_a_file_move_by_hash():
    """A verified constant whose file moved (same scope, name, hash; old key gone) keeps its id
    and evidence instead of being removed and re-added unverified (TH-076)."""
    reg = {"version": 2, "last_scan": None, "constants": [
        {"id": "CONST-106", "file": "skills/kicad/scripts/kicad_utils.py", "scope": "module",
         "name": "_REGULATOR_VREF", "line": 143, "end_line": 249, "type": "lookup_table",
         "entry_count": 2, "content_hash": "sha256:abc", "status": "verified",
         "source": "TI datasheets", "notes": "n", "verified_entries": 1,
         "entries": {"LM317": {"value": 1.25, "status": "verified", "source": "SLVS044"},
                     "AP2112": {"value": 0.8, "status": "unverified", "source": None}}}]}
    scanned = [_scanned("_REGULATOR_VREF", "skills/kicad/scripts/kicad_core/parts.py", "sha256:abc",
                        {"LM317": {"value": 1.25}, "AP2112": {"value": 0.8}})]
    added, updated, removed = ac.update_registry(reg, scanned)
    assert (added, updated, removed) == (0, 1, 0)
    c = reg["constants"][0]
    assert c["id"] == "CONST-106"
    assert c["file"] == "skills/kicad/scripts/kicad_core/parts.py"
    assert c["relocated_from"] == "skills/kicad/scripts/kicad_utils.py"
    assert c["status"] == "verified" and c["source"] == "TI datasheets" and c["notes"] == "n"
    assert c["verified_entries"] == 1
    assert c["entries"]["LM317"] == {"value": 1.25, "status": "verified", "source": "SLVS044"}
    assert c["entries"]["AP2112"]["status"] == "unverified"


def test_update_registry_ambiguous_hash_move_is_not_carried():
    """Two newcomers with the same (scope, name, hash) cannot claim one orphan's evidence."""
    reg = {"version": 2, "last_scan": None, "constants": [
        {"id": "CONST-001", "file": "a.py", "scope": "module", "name": "counts", "line": 1,
         "end_line": 1, "type": "dict", "entry_count": 0, "content_hash": "sha256:same",
         "status": "verified", "source": "s", "notes": None, "verified_entries": 0}]}
    scanned = [_scanned("counts", "b.py", "sha256:same"), _scanned("counts", "c.py", "sha256:same")]
    added, updated, removed = ac.update_registry(reg, scanned)
    assert (added, updated, removed) == (2, 0, 1)
    assert all(c["status"] == "unverified" for c in reg["constants"])


def test_update_registry_hash_move_does_not_steal_from_a_surviving_key():
    """An entry still present at its own key is updated in place; a same-hash twin elsewhere is new."""
    reg = {"version": 2, "last_scan": None, "constants": [
        {"id": "CONST-001", "file": "a.py", "scope": "module", "name": "counts", "line": 1,
         "end_line": 1, "type": "dict", "entry_count": 0, "content_hash": "sha256:same",
         "status": "verified", "source": "s", "notes": None, "verified_entries": 0}]}
    scanned = [_scanned("counts", "a.py", "sha256:same"), _scanned("counts", "b.py", "sha256:same")]
    added, updated, removed = ac.update_registry(reg, scanned)
    assert (added, updated, removed) == (1, 0, 0)
    by_file = {c["file"]: c for c in reg["constants"]}
    assert by_file["a.py"]["status"] == "verified" and "relocated_from" not in by_file["a.py"]
    assert by_file["b.py"]["status"] == "unverified"


def test_update_registry_carries_evidence_across_a_function_split_in_the_same_file():
    """A local moved into a new helper (same file, name and hash, new scope) keeps its evidence."""
    reg = {"version": 2, "last_scan": None, "constants": [
        {"id": "CONST-134", "file": "skills/kicad/scripts/signal_detectors.py",
         "scope": "detect_power_regulators", "function": "detect_power_regulators",
         "name": "_non_reg_exclude", "line": 10, "end_line": 12, "type": "set", "entry_count": 0,
         "content_hash": "sha256:b55a", "status": "verified", "source": "s", "notes": None,
         "verified_entries": 0}]}
    info = _scanned("_non_reg_exclude", "skills/kicad/scripts/signal_detectors.py", "sha256:b55a",
                    scope="_screen_regulator_candidate")
    info.func = "_screen_regulator_candidate"
    added, updated, removed = ac.update_registry(reg, [info])
    assert (added, updated, removed) == (0, 1, 0)
    c = reg["constants"][0]
    assert c["id"] == "CONST-134" and c["status"] == "verified"
    assert c["scope"] == "_screen_regulator_candidate" and c["function"] == "_screen_regulator_candidate"
    assert "relocated_from" not in c


def test_update_registry_merged_copies_keep_the_verified_copy():
    """Two identical dicts merged into one shared table: the verified copy's id and evidence survive,
    the other copy is removed."""
    reg = {"version": 2, "last_scan": None, "constants": [
        {"id": "CONST-365", "file": "skills/kicad/scripts/signal_detectors.py",
         "scope": "_default_switching_freq", "name": "defaults", "line": 1, "end_line": 1,
         "type": "dict", "entry_count": 2, "content_hash": "sha256:2090", "status": "unverified",
         "source": None, "notes": None, "verified_entries": 0},
        {"id": "CONST-384", "file": "skills/emc/scripts/emc_rules.py",
         "scope": "_default_switching_freq", "name": "defaults", "line": 1, "end_line": 1,
         "type": "dict", "entry_count": 2, "content_hash": "sha256:2090", "status": "verified",
         "source": "datasheets", "notes": None, "verified_entries": 0}]}
    info = _scanned("defaults", "skills/kicad/scripts/kicad_core/parts.py", "sha256:2090",
                    scope="default_switching_freq")
    added, updated, removed = ac.update_registry(reg, [info])
    assert (added, updated, removed) == (0, 1, 1)
    c = reg["constants"][0]
    assert c["id"] == "CONST-384" and c["status"] == "verified" and c["source"] == "datasheets"
    assert c["file"] == "skills/kicad/scripts/kicad_core/parts.py"
    assert c["relocated_from"] == "skills/emc/scripts/emc_rules.py"


def test_update_registry_line_keyed_hash_never_carries():
    """Non-literal constants hash as ast_<line>; a same-line coincidence must not transfer evidence."""
    reg = {"version": 2, "last_scan": None, "constants": [
        {"id": "CONST-139", "file": "a.py", "scope": "f", "name": "reg_info", "line": 1,
         "end_line": 1, "type": "dict", "entry_count": 3, "content_hash": "sha256:ast_1741",
         "status": "verified", "source": "s", "notes": None, "verified_entries": 0}]}
    added, updated, removed = ac.update_registry(reg, [_scanned("reg_info", "b.py", "sha256:ast_1741", scope="g")])
    assert (added, updated, removed) == (1, 0, 1)
    assert reg["constants"][0]["status"] == "unverified"
