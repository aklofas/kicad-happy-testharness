"""Unit tests for regression/seed.py — assertion generation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from seed import (
    _range_bounds,
    _quality_assertions,
    generate_schematic_assertions,
    generate_spice_assertions,
    generate_datasheets_assertions,
    _QUALITY_CHECKS,
    _LIST_DETECTORS,
)


# === _range_bounds ===

def test_range_bounds_normal():
    lo, hi = _range_bounds(100, 0.10)
    assert lo == 90
    assert 110 <= hi <= 111  # ceil(110.0) may be 111 due to float precision

def test_range_bounds_zero():
    lo, hi = _range_bounds(0, 0.10)
    # Should NOT be (0, 0) — minimum spread of 2
    assert hi > lo
    assert lo == 0
    assert hi >= 1

def test_range_bounds_one():
    lo, hi = _range_bounds(1, 0.10)
    # Small value: minimum spread of 2
    assert hi - lo >= 2

def test_range_bounds_large():
    lo, hi = _range_bounds(1000, 0.10)
    assert lo == 900
    assert hi == 1100

def test_range_bounds_tight_tolerance():
    lo, hi = _range_bounds(50, 0.01)
    # 50 * 0.99 = 49.5, floor = 49; 50 * 1.01 = 50.5, ceil = 51
    assert lo == 49
    assert hi == 51

def test_range_bounds_no_negative():
    lo, hi = _range_bounds(1, 0.50)
    assert lo >= 0


# === generate_spice_assertions ===

def test_spice_assertions_basic():
    data = {
        "summary": {"total": 10, "pass": 8, "warn": 1, "fail": 0, "skip": 1},
        "simulation_results": [
            {"subcircuit_type": "rc_filter"},
            {"subcircuit_type": "rc_filter"},
            {"subcircuit_type": "opamp_circuit"},
        ],
    }
    assertions = generate_spice_assertions(data)
    assert len(assertions) >= 3  # total range + pass min + 2 type counts
    ids = [a["id"] for a in assertions]
    assert len(ids) == len(set(ids)), "IDs should be unique"

def test_spice_assertions_empty():
    data = {"summary": {"total": 0}, "simulation_results": []}
    assertions = generate_spice_assertions(data)
    assert assertions == []

def test_spice_assertions_no_pass():
    data = {
        "summary": {"total": 5, "pass": 0, "warn": 5},
        "simulation_results": [{"subcircuit_type": "rc_filter"}] * 5,
    }
    assertions = generate_spice_assertions(data)
    # Should still have total range + type count, but NO pass min
    descs = [a["description"] for a in assertions]
    assert not any("passing" in d for d in descs)


# === generate_datasheets_assertions ===

def test_datasheets_assertions_basic():
    data = {
        "extracted": 5, "sufficient": 4,
        "by_category": {"opamp": 2, "regulator": 3},
        "parts": {},
    }
    assertions = generate_datasheets_assertions(data)
    assert len(assertions) >= 3  # count range + sufficient min + 2 categories
    ids = [a["id"] for a in assertions]
    assert len(ids) == len(set(ids))

def test_datasheets_assertions_empty():
    data = {"extracted": 0, "sufficient": 0, "by_category": {}, "parts": {}}
    assertions = generate_datasheets_assertions(data)
    assert assertions == []


# === _quality_assertions ===

def test_quality_voltage_dividers():
    detections = [{"ratio": 0.5, "r_top": {"ref": "R1"}}]
    qa, next_num = _quality_assertions("voltage_dividers", detections, 100)
    assert len(qa) == 1
    assert qa[0]["check"]["op"] == "not_contains_match"
    assert qa[0]["check"]["field"] == "ratio"
    assert next_num == 101

def test_quality_rc_filters():
    detections = [{"cutoff_hz": 1000.0}]
    qa, _ = _quality_assertions("rc_filters", detections, 1)
    assert len(qa) == 1
    assert qa[0]["check"]["field"] == "cutoff_hz"

def test_quality_unknown_detector():
    """Detectors not in _QUALITY_CHECKS return nothing."""
    qa, num = _quality_assertions("rf_chains", [], 1)
    assert qa == []
    assert num == 1

def test_quality_checks_coverage():
    """All quality check detectors are recognized signal types."""
    for det in _QUALITY_CHECKS:
        assert det in _LIST_DETECTORS or det in (
            "voltage_dividers", "rc_filters", "lc_filters",
            "current_sense", "power_regulators", "crystal_circuits",
            "opamp_circuits", "transistor_circuits", "feedback_networks",
        ), f"{det} not a recognized detector"


# === generate_schematic_assertions with quality ===

def test_schematic_includes_quality():
    """Quality assertions appear after min_count for qualified detectors."""
    data = {
        "statistics": {"total_components": 20, "total_nets": 10, "component_types": {}},
        "signal_analysis": {
            "voltage_dividers": [{"ratio": 0.5, "r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}}],
        },
        "bom": [{"references": ["R1"], "quantity": 1}],
    }
    assertions = generate_schematic_assertions(data, tolerance=0.10)
    ops = [(a["check"]["op"], a.get("description", "")) for a in assertions]
    # Should have both min_count and not_contains_match for voltage_dividers
    has_min = any(op == "min_count" and "voltage_dividers" in desc for op, desc in ops)
    has_quality = any(op == "not_contains_match" and "ratio" in desc for op, desc in ops)
    assert has_min, "Missing min_count for voltage_dividers"
    assert has_quality, "Missing quality assertion for voltage_dividers"

def test_schematic_no_quality_for_unknown():
    """No quality assertions for detectors without _QUALITY_CHECKS entry."""
    data = {
        "statistics": {"total_components": 20, "total_nets": 10, "component_types": {}},
        "signal_analysis": {
            "rf_chains": [{"total_rf_components": 5}],
        },
        "bom": [],
    }
    assertions = generate_schematic_assertions(data, tolerance=0.10)
    quality = [a for a in assertions if a["check"]["op"] == "not_contains_match"]
    assert len(quality) == 0


# === empty-detector assertions ===

def test_empty_detectors_included():
    """With include_empty and 50+ comps, absent detectors get max_count=0."""
    data = {
        "statistics": {"total_components": 60, "total_nets": 30, "component_types": {}},
        "signal_analysis": {
            "voltage_dividers": [{"ratio": 0.5}],
            # All other detectors are absent
        },
        "bom": [],
    }
    assertions = generate_schematic_assertions(data, tolerance=0.10, include_empty=True)
    empty_assertions = [a for a in assertions
                        if a["check"]["op"] == "max_count" and a["check"]["value"] == 0]
    # Should have max_count=0 for each _LIST_DETECTOR that's absent
    assert len(empty_assertions) > 0
    # voltage_dividers is present, so should NOT have max_count=0
    vd_empty = [a for a in empty_assertions if "voltage_dividers" in a["description"]]
    assert len(vd_empty) == 0

def test_empty_detectors_not_included_by_default():
    """Without include_empty, no max_count=0 assertions."""
    data = {
        "statistics": {"total_components": 60, "total_nets": 30, "component_types": {}},
        "signal_analysis": {},
        "bom": [],
    }
    assertions = generate_schematic_assertions(data, tolerance=0.10, include_empty=False)
    empty_assertions = [a for a in assertions if a["check"]["op"] == "max_count"]
    assert len(empty_assertions) == 0

def test_empty_detectors_skip_small_schematics():
    """Empty-detector assertions only for schematics with 50+ components."""
    data = {
        "statistics": {"total_components": 20, "total_nets": 10, "component_types": {}},
        "signal_analysis": {},
        "bom": [],
    }
    assertions = generate_schematic_assertions(data, tolerance=0.10, include_empty=True)
    empty_assertions = [a for a in assertions if a["check"]["op"] == "max_count"]
    assert len(empty_assertions) == 0


# === tightened component_type tolerance ===

def test_component_type_tolerance_tighter():
    """Component type threshold should be 75% of count, not 50%."""
    data = {
        "statistics": {
            "total_components": 100, "total_nets": 50,
            "component_types": {"resistor": 100},
        },
        "signal_analysis": {},
        "bom": [],
    }
    assertions = generate_schematic_assertions(data, tolerance=0.10)
    ctype_assertion = [a for a in assertions
                       if "resistor" in a.get("description", "")]
    assert len(ctype_assertion) == 1
    # Old: max(1, 100 // 2) = 50; New: max(1, int(100 * 0.75)) = 75
    assert ctype_assertion[0]["check"]["value"] == 75

def test_component_type_tolerance_small():
    """Small counts still have minimum of 1."""
    data = {
        "statistics": {
            "total_components": 20, "total_nets": 10,
            "component_types": {"inductor": 5},
        },
        "signal_analysis": {},
        "bom": [],
    }
    assertions = generate_schematic_assertions(data, tolerance=0.10)
    ctype = [a for a in assertions if "inductor" in a.get("description", "")]
    assert len(ctype) == 1
    # max(1, int(5 * 0.75)) = max(1, 3) = 3
    assert ctype[0]["check"]["value"] == 3


# === round-trip: generated assertions pass against source data ===

def test_schematic_roundtrip():
    """Generated assertions should pass when evaluated against their source data."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
    from checks import evaluate_assertion

    data = {
        "statistics": {
            "total_components": 80, "total_nets": 40,
            "component_types": {"resistor": 30, "capacitor": 20, "ic": 10},
        },
        "signal_analysis": {
            "voltage_dividers": [
                {"ratio": 0.5, "r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}},
                {"ratio": 0.33, "r_top": {"ref": "R3"}, "r_bottom": {"ref": "R4"}},
            ],
            "rc_filters": [
                {"cutoff_hz": 1000.0, "resistor": {"ref": "R5"}, "capacitor": {"ref": "C1"}},
            ],
        },
        "bom": [{"references": ["R1"], "quantity": 1}],
    }
    assertions = generate_schematic_assertions(data, tolerance=0.10, include_empty=True)
    for a in assertions:
        result = evaluate_assertion(a, data)
        assert result["passed"], f"Assertion {a['id']} ({a['description']}) failed: {result}"


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
