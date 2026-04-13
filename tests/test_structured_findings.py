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


sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from migrate_findings_structured import (
    derive_detector, derive_subject_refs, derive_expected_relation,
    derive_confidence, enrich_item,
)


def test_derive_detector_basic():
    assert derive_detector("signal_analysis.voltage_dividers") == "voltage_dividers"
    assert derive_detector("signal_analysis.power_regulators") == "power_regulators"


def test_derive_detector_missing():
    assert derive_detector("") is None
    assert derive_detector("components") is None
    assert derive_detector("statistics.total_nets") is None


def test_derive_subject_refs():
    assert derive_subject_refs("R15/R16 are a voltage divider") == ["R15", "R16"]
    assert derive_subject_refs("U1 correctly detected") == ["U1"]
    assert derive_subject_refs("No specific refs mentioned") == []


def test_derive_relation_default_correct():
    item = {"description": "U1 detected correctly", "analyzer_section": "signal_analysis.power_regulators"}
    assert derive_expected_relation(item, "correct") == "in_detector"


def test_derive_relation_default_incorrect():
    item = {"description": "R1 is not a divider", "analyzer_section": "signal_analysis.voltage_dividers"}
    assert derive_expected_relation(item, "incorrect") == "not_in_detector"


def test_derive_relation_default_missed():
    item = {"description": "U3 should be detected", "analyzer_section": "signal_analysis.power_regulators"}
    assert derive_expected_relation(item, "missed") == "in_detector"


def test_derive_relation_count_override():
    item = {"description": "should detect 3 voltage dividers", "analyzer_section": "signal_analysis.voltage_dividers"}
    rel = derive_expected_relation(item, "correct")
    assert rel == "count_equals"


def test_derive_relation_value_override():
    item = {"description": "ratio should be 0.5 for R1/R2", "analyzer_section": "signal_analysis.voltage_dividers"}
    rel = derive_expected_relation(item, "correct")
    assert rel == "field_value_equals"


def test_derive_confidence_full():
    assert derive_confidence(detector="voltage_dividers", refs=["R1"], relation="in_detector") == 0.9


def test_derive_confidence_no_refs():
    assert derive_confidence(detector="voltage_dividers", refs=[], relation="in_detector") == 0.7


def test_derive_confidence_value_extraction():
    assert derive_confidence(detector="voltage_dividers", refs=["R1"], relation="field_value_equals") == 0.6


def test_enrich_item_full():
    item = {
        "description": "R15/R16 are a false-positive divider",
        "analyzer_section": "signal_analysis.voltage_dividers",
    }
    enriched = enrich_item(item, "incorrect")
    assert enriched["detector"] == "voltage_dividers"
    assert enriched["subject_refs"] == ["R15", "R16"]
    assert enriched["expected_relation"] == "not_in_detector"
    assert enriched["confidence"] == 0.9


def test_enrich_item_no_section():
    """Items without analyzer_section are returned unchanged."""
    item = {"description": "General observation"}
    enriched = enrich_item(item, "correct")
    assert "detector" not in enriched
    assert "expected_relation" not in enriched


from checks import evaluate_assertion


def test_roundtrip_in_detector():
    """Round-trip: structured item → check → evaluate against mock output."""
    item = {
        "detector": "power_regulators",
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
        "signal_analysis": {
            "power_regulators": [
                {"ref": "U1", "value": "LM7805"},
            ]
        }
    }
    result = evaluate_assertion(assertion, output)
    assert result["passed"], f"Round-trip failed: {result}"


def test_roundtrip_not_in_detector():
    """Round-trip: not_in_detector check should fail when ref IS present."""
    item = {
        "detector": "voltage_dividers",
        "subject_refs": ["R15"],
        "expected_relation": "not_in_detector",
    }
    check = _check_from_structured(item, "incorrect")
    assertion = {"id": "TEST-002", "description": "R15 not divider", "check": check}

    output = {
        "signal_analysis": {
            "voltage_dividers": [
                {"r_top": {"ref": "R15", "value": "10k"}, "r_bottom": {"ref": "R16", "value": "10k"}, "ratio": 0.5},
            ]
        }
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
