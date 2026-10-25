"""Generator -> evaluator round trip for required-field SEED locks: the lock seeded from good
detections passes on them and fails when the field goes missing, null or empty (code A2-F4)."""
import copy
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(HARNESS / "regression"))
from regression import seed  # noqa: E402
from regression.checks import evaluate_assertion  # noqa: E402

pytestmark = pytest.mark.unit

DET = "detect_battery_chargers"
GOOD = [{"detector": DET, "charger_reference": "U3", "charger_type": "single_cell_linear"},
        {"detector": DET, "charger_reference": "U7", "charger_type": "single_cell_switching"}]


def _lock():
    assertions, _ = seed._field_spec_assertions(DET, GOOD, 1)
    locks = [a for a in assertions if a["check"]["op"] == "not_contains_match"]
    assert [a["check"]["field"] for a in locks] == ["charger_reference"]
    return locks[0]


def _passes(findings):
    return evaluate_assertion(copy.deepcopy(_lock()), {"findings": findings})["passed"]


def test_lock_passes_on_the_detections_it_was_seeded_from():
    assert _passes(GOOD)


@pytest.mark.parametrize("bad", ["", None, []], ids=["empty", "null", "empty_list"])
def test_lock_fails_when_the_field_regresses(bad):
    findings = copy.deepcopy(GOOD)
    findings[1]["charger_reference"] = bad
    assert not _passes(findings)


def test_lock_fails_when_the_field_disappears():
    findings = copy.deepcopy(GOOD)
    del findings[0]["charger_reference"]
    assert not _passes(findings)


def test_non_empty_patterns_unaffected_by_null():
    """A NEG-style `not_contains_match pattern=^R5$` still passes over a null field."""
    a = {"id": "N", "check": {"path": "findings", "op": "not_contains_match", "field": "ref",
                              "pattern": "^R5$"}}
    assert evaluate_assertion(a, {"findings": [{"ref": None}, {"ref": []}, {"ref": "R6"}]})["passed"]


def test_include_empty_locks_use_full_detector_names(monkeypatch):
    """--include-empty: an absent detector gets a max_count 0 lock on its real name, never
    detect_<full name> (code A2-F3)."""
    monkeypatch.setattr(seed, "_known_detectors_cache",
                        ["detect_power_regulators", "audit_esd_protection", "led_drivers"])
    data = {"statistics": {"total_components": 60}, "findings": [], "bom": []}
    got = [a["check"]["detector_filter"] for a in
           seed.generate_schematic_assertions(data, include_empty=True)
           if a["check"].get("op") == "max_count"]
    assert got == ["detect_power_regulators", "audit_esd_protection", "detect_led_drivers"]
    lock = next(a for a in seed.generate_schematic_assertions(data, include_empty=True)
                if a["check"].get("detector_filter") == "detect_power_regulators")
    present = {"findings": [{"detector": "detect_power_regulators"}]}
    assert not evaluate_assertion(copy.deepcopy(lock), present)["passed"]


def test_composite_ref_struct_lock_matches_its_source_only():
    """A composite ref field ("R163 442k") seeds a STRUCT lock that passes on its own output and
    does not accept a near-miss ref (code A2-F14)."""
    from regression import seed_structural
    det = "detect_power_regulators"
    src = {"findings": [{"detector": det, "ref": "R163 442k"}, {"detector": det, "ref": "U2"}],
           "statistics": {"total_components": 20}}
    locks = [a for a in seed_structural.generate_structural_assertions(src)
             if a["check"].get("op") == "contains_match"]
    by_ref = {a["description"].split()[0]: a for a in locks}
    assert set(by_ref) == {"R163", "U2"}
    for a in locks:
        assert evaluate_assertion(copy.deepcopy(a), src)["passed"], a
    near = {"findings": [{"detector": det, "ref": "R1630 442k"}]}
    assert not evaluate_assertion(copy.deepcopy(by_ref["R163"]), near)["passed"]
    assert not evaluate_assertion(copy.deepcopy(by_ref["U2"]), {"findings": [{"detector": det, "ref": "U20"}]})["passed"]


@pytest.mark.parametrize("op,value,actual,want", [
    ("max_count", 1.0, 1.83, False),   # int(1.83) == 1 passed this lock
    ("min_count", 0.8, 0.81, True),    # int(0.81) == 0 failed this one
    ("max_count", 2, 2, True),
])
def test_fractional_operands_are_not_truncated(op, value, actual, want):
    """code A2-F10: count operators compare fractional scalars by value."""
    a = {"id": "X", "check": {"path": "x", "op": op, "value": value}}
    assert evaluate_assertion(a, {"x": actual})["passed"] is want
