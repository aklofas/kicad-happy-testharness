"""Unit tests for structured finding item check generation."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from generate_finding_checks import _check_from_structured


def test_in_detector_correct():
    """correct item + in_detector → contains_match."""
    item = {
        "detector": "voltage_dividers",
        "subject_refs": ["R15", "R16"],
        "expected_relation": "in_detector",
    }
    check = _check_from_structured(item, "correct")
    assert check is not None
    assert check["op"] == "contains_match"
    assert check["path"] == "signal_analysis.voltage_dividers"
    assert check["field"] == "r_top.ref"
    assert "R15" in check["pattern"]


def test_not_in_detector_incorrect():
    """incorrect item + not_in_detector → not_contains_match."""
    item = {
        "detector": "voltage_dividers",
        "subject_refs": ["R15"],
        "expected_relation": "not_in_detector",
    }
    check = _check_from_structured(item, "incorrect")
    assert check is not None
    assert check["op"] == "not_contains_match"
    assert "R15" in check["pattern"]


def test_in_detector_missed():
    """missed item + in_detector → contains_match."""
    item = {
        "detector": "power_regulators",
        "subject_refs": ["U3"],
        "expected_relation": "in_detector",
    }
    check = _check_from_structured(item, "missed")
    assert check is not None
    assert check["op"] == "contains_match"
    assert check["path"] == "signal_analysis.power_regulators"
    assert check["field"] == "ref"
    assert "U3" in check["pattern"]


def test_field_value_equals():
    """field_value_equals → field_equals check."""
    item = {
        "detector": "voltage_dividers",
        "subject_refs": ["R1", "R2"],
        "expected_relation": "field_value_equals",
        "field": "ratio",
        "expected_value": 0.5,
    }
    check = _check_from_structured(item, "correct")
    assert check is not None
    assert check["op"] == "field_equals"
    assert check["field"] == "ratio"
    assert check["value"] == 0.5


def test_count_equals():
    """count_equals → equals check on section length."""
    item = {
        "detector": "voltage_dividers",
        "subject_refs": [],
        "expected_relation": "count_equals",
        "expected_value": 3,
    }
    check = _check_from_structured(item, "correct")
    assert check is not None
    assert check["op"] == "equals"
    assert check["path"] == "signal_analysis.voltage_dividers"
    assert check["value"] == 3


def test_section_exists_correct():
    """correct + section_exists → exists."""
    item = {
        "detector": "power_regulators",
        "subject_refs": [],
        "expected_relation": "section_exists",
    }
    check = _check_from_structured(item, "correct")
    assert check is not None
    assert check["op"] == "exists"
    assert check["path"] == "signal_analysis.power_regulators"


def test_section_exists_incorrect():
    """incorrect + section_exists → not_exists."""
    item = {
        "detector": "rf_chains",
        "subject_refs": [],
        "expected_relation": "section_exists",
    }
    check = _check_from_structured(item, "incorrect")
    assert check is not None
    assert check["op"] == "not_exists"


def test_unknown_detector_returns_none():
    """in_detector with unknown detector (no REF_FIELD_MAP entry) → None."""
    item = {
        "detector": "nonexistent_detector",
        "subject_refs": ["U1"],
        "expected_relation": "in_detector",
    }
    check = _check_from_structured(item, "correct")
    assert check is None


def test_in_detector_no_refs_fallback():
    """in_detector with empty subject_refs → min_count fallback."""
    item = {
        "detector": "voltage_dividers",
        "subject_refs": [],
        "expected_relation": "in_detector",
    }
    check = _check_from_structured(item, "correct")
    assert check is not None
    assert check["op"] == "min_count"
    assert check["value"] == 1


# === Runner ===

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
