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
        "detector": "detect_voltage_dividers",
        "subject_refs": ["R15", "R16"],
        "expected_relation": "in_detector",
    }
    check = _check_from_structured(item, "correct")
    assert check is not None
    assert check["op"] == "contains_match"
    assert check["path"] == "findings"
    assert check["detector_filter"] == "detect_voltage_dividers"
    assert check["field"] == "r_top.ref"
    assert "R15" in check["pattern"]


def test_not_in_detector_incorrect():
    """incorrect item + not_in_detector → not_contains_match."""
    item = {
        "detector": "detect_voltage_dividers",
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
        "detector": "detect_power_regulators",
        "subject_refs": ["U3"],
        "expected_relation": "in_detector",
    }
    check = _check_from_structured(item, "missed")
    assert check is not None
    assert check["op"] == "contains_match"
    assert check["path"] == "findings"
    assert check["detector_filter"] == "detect_power_regulators"
    assert check["field"] == "ref"
    assert "U3" in check["pattern"]


def _fve_item(refs=("R1", "R2"), detector="detect_voltage_dividers"):
    return {"detector": detector, "subject_refs": list(refs), "expected_relation": "field_value_equals",
            "field": "ratio", "expected_value": 0.5}


def _eval(check, findings):
    from regression.checks import evaluate_assertion
    return evaluate_assertion({"id": "F", "check": dict(check)}, {"findings": findings})["passed"]


def test_field_value_equals_round_trip():
    """field_value_equals -> a field_equals check the evaluator honours: it passes on the
    expected value, fails on a changed value, and fails while the subject is absent."""
    check = _check_from_structured(_fve_item(), "correct")
    assert check["op"] == "field_equals"
    assert check["match_field"] == "r_top.ref" and check["match_value"] == "R1"
    assert check["assert_field"] == "ratio" and check["assert_value"] == 0.5
    det = "detect_voltage_dividers"
    good = [{"detector": det, "r_top": {"ref": "R9"}, "ratio": 0.1},
            {"detector": det, "r_top": {"ref": "R1"}, "ratio": 0.5}]
    assert _eval(check, good)
    changed = [dict(good[0]), {**good[1], "ratio": 0.25}]
    assert not _eval(check, changed)
    assert not _eval(check, [good[0]])          # detector item for R1 absent
    assert _eval(check, good + [{"detector": "detect_other", "ratio": 9}])


def test_field_value_equals_short_detector_name_and_no_refs():
    check = _check_from_structured(_fve_item(refs=(), detector="voltage_dividers"), "correct")
    assert check["detector_filter"] == "detect_voltage_dividers"
    assert check["op"] == "contains_match" and check["field"] == "ratio" and check["pattern"] == r"^0\.5$"
    assert _eval(check, [{"detector": "detect_voltage_dividers", "ratio": 0.5}])
    assert not _eval(check, [{"detector": "detect_voltage_dividers", "ratio": 0.4}])


def test_count_equals():
    """count_equals → equals check on section length."""
    item = {
        "detector": "detect_voltage_dividers",
        "subject_refs": [],
        "expected_relation": "count_equals",
        "expected_value": 3,
    }
    check = _check_from_structured(item, "correct")
    assert check is not None
    assert check["op"] == "equals"
    assert check["path"] == "findings"
    assert check["detector_filter"] == "detect_voltage_dividers"
    assert check["value"] == 3


def test_section_exists_correct():
    """correct + section_exists → exists."""
    item = {
        "detector": "detect_power_regulators",
        "subject_refs": [],
        "expected_relation": "section_exists",
    }
    check = _check_from_structured(item, "correct")
    assert check is not None
    assert check["op"] == "min_count"
    assert check["path"] == "findings"
    assert check["detector_filter"] == "detect_power_regulators"


def test_section_exists_incorrect():
    """incorrect + section_exists → max_count 0."""
    item = {
        "detector": "detect_rf_chains",
        "subject_refs": [],
        "expected_relation": "section_exists",
    }
    check = _check_from_structured(item, "incorrect")
    assert check is not None
    assert check["op"] == "max_count"
    assert check["value"] == 0


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
        "detector": "detect_voltage_dividers",
        "subject_refs": [],
        "expected_relation": "in_detector",
    }
    check = _check_from_structured(item, "correct")
    assert check is not None
    assert check["op"] == "min_count"
    assert check["value"] == 1


from checks import evaluate_assertion


def test_roundtrip_in_detector():
    """Round-trip: structured item → check → evaluate against mock output."""
    item = {
        "detector": "detect_power_regulators",
        "subject_refs": ["U1"],
        "expected_relation": "in_detector",
    }
    check = _check_from_structured(item, "correct")
    assert check is not None

    assertion = {
        "id": "TEST-001",
        "description": "U1 in regulators",
        "check": check,
    }
    output = {
        "findings": [
            {"detector": "detect_power_regulators", "ref": "U1", "value": "LM7805"},
        ]
    }
    result = evaluate_assertion(assertion, output)
    assert result["passed"], f"Round-trip failed: {result}"


def test_roundtrip_not_in_detector():
    """Round-trip: not_in_detector check should fail when ref IS present."""
    item = {
        "detector": "detect_voltage_dividers",
        "subject_refs": ["R15"],
        "expected_relation": "not_in_detector",
    }
    check = _check_from_structured(item, "incorrect")
    assertion = {"id": "TEST-002", "description": "R15 not divider", "check": check}

    output = {
        "findings": [
            {"detector": "detect_voltage_dividers", "r_top": {"ref": "R15", "value": "10k"}, "r_bottom": {"ref": "R16", "value": "10k"}, "ratio": 0.5},
        ]
    }
    result = evaluate_assertion(assertion, output)
    assert not result["passed"], f"not_in_detector should fail when ref present: {result}"


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
