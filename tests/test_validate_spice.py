"""Unit tests for validate/validate_spice.py — SPICE cross-validation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "validate"))
from validate_spice import cross_validate_file


def _make_sch(detectors):
    """Build minimal schematic JSON with signal_analysis detectors."""
    return {"signal_analysis": detectors}


def _make_spice(results):
    """Build minimal SPICE JSON with simulation_results."""
    return {"simulation_results": results}


# === voltage_divider cross-validation ===

def test_voltage_divider_match():
    sch = _make_sch({"voltage_dividers": [{
        "r_top": {"ref": "R1", "value": "10k"},
        "r_bottom": {"ref": "R2", "value": "10k"},
        "ratio": 0.5,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "voltage_divider",
        "components": ["R1", "R2"],
        "expected": {"vout_V": 1.65},
        "simulated": {"vout_V": 1.65},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 1
    assert results[0]["status"] == "match"
    assert results[0]["delta_pct"] < 0.1

def test_voltage_divider_mismatch():
    sch = _make_sch({"voltage_dividers": [{
        "r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}, "ratio": 0.5,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "voltage_divider",
        "components": ["R1", "R2"],
        "expected": {"vout_V": 1.65},
        "simulated": {"vout_V": 2.5},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 1
    assert results[0]["status"] == "mismatch"

def test_voltage_divider_no_spice_match():
    """SPICE results with different components produce no cross-validation."""
    sch = _make_sch({"voltage_dividers": [{
        "r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}, "ratio": 0.5,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "voltage_divider",
        "components": ["R3", "R4"],
        "expected": {"vout_V": 1.0},
        "simulated": {"vout_V": 1.0},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 0


# === rc_filter cross-validation ===

def test_rc_filter_match():
    sch = _make_sch({"rc_filters": [{
        "resistor": {"ref": "R1"}, "capacitor": {"ref": "C1"},
        "cutoff_hz": 1000.0,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "rc_filter",
        "components": ["C1", "R1"],
        "simulated": {"fc_hz": 1002.0},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 1
    assert results[0]["status"] == "match"
    assert results[0]["delta_pct"] < 1.0

def test_rc_filter_zero_cutoff():
    """Zero cutoff_hz should be skipped (no division by zero)."""
    sch = _make_sch({"rc_filters": [{
        "resistor": {"ref": "R1"}, "capacitor": {"ref": "C1"},
        "cutoff_hz": 0,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "rc_filter",
        "components": ["C1", "R1"],
        "simulated": {"fc_hz": 100.0},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 0  # Skipped due to analyzer_fc == 0

def test_rc_filter_none_simulated():
    """None simulated value should be skipped."""
    sch = _make_sch({"rc_filters": [{
        "resistor": {"ref": "R1"}, "capacitor": {"ref": "C1"},
        "cutoff_hz": 1000.0,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "rc_filter",
        "components": ["C1", "R1"],
        "simulated": {"fc_hz": None},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 0


# === lc_filter cross-validation ===

def test_lc_filter_match():
    sch = _make_sch({"lc_filters": [{
        "inductor": {"ref": "L1"}, "capacitor": {"ref": "C1"},
        "resonant_hz": 50000.0,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "lc_filter",
        "components": ["C1", "L1"],
        "simulated": {"resonant_hz": 50100.0},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 1
    assert results[0]["status"] == "match"

def test_lc_filter_zero_resonant():
    """Zero resonant_hz should be skipped."""
    sch = _make_sch({"lc_filters": [{
        "inductor": {"ref": "L1"}, "capacitor": {"ref": "C1"},
        "resonant_hz": 0,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "lc_filter",
        "components": ["C1", "L1"],
        "simulated": {"resonant_hz": 1000.0},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 0


# === current_sense cross-validation ===

def test_current_sense_match():
    sch = _make_sch({"current_sense": [{
        "shunt": {"ref": "R1"}, "max_current_50mV_A": 0.5,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "current_sense",
        "components": ["R1"],
        "simulated": {"i_at_50mV_A": 0.5001},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 1
    assert results[0]["status"] == "match"

def test_current_sense_zero_analyzer():
    """Zero analyzer value should be skipped."""
    sch = _make_sch({"current_sense": [{
        "shunt": {"ref": "R1"}, "max_current_50mV_A": 0,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "current_sense",
        "components": ["R1"],
        "simulated": {"i_at_50mV_A": 0.5},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 0


# === edge cases ===

def test_empty_signal_analysis():
    results = cross_validate_file({}, _make_spice([]))
    assert results == []

def test_empty_spice_results():
    sch = _make_sch({"voltage_dividers": [{
        "r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}, "ratio": 0.5,
    }]})
    results = cross_validate_file(sch, _make_spice([]))
    assert results == []

def test_non_dict_resistor():
    """Non-dict r_top/r_bottom should be skipped gracefully."""
    sch = _make_sch({"voltage_dividers": [{
        "r_top": "R1", "r_bottom": "R2", "ratio": 0.5,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "voltage_divider",
        "components": ["R1", "R2"],
        "expected": {"vout_V": 1.0},
        "simulated": {"vout_V": 1.0},
    }])
    results = cross_validate_file(sch, spice)
    assert results == []

def test_component_order_independence():
    """Components should match regardless of order."""
    sch = _make_sch({"voltage_dividers": [{
        "r_top": {"ref": "R2"}, "r_bottom": {"ref": "R1"}, "ratio": 0.5,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "voltage_divider",
        "components": ["R1", "R2"],
        "expected": {"vout_V": 1.65},
        "simulated": {"vout_V": 1.65},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 1
    assert results[0]["status"] == "match"

def test_expected_vout_zero():
    """Zero expected value should be skipped (no division by zero)."""
    sch = _make_sch({"voltage_dividers": [{
        "r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}, "ratio": 0.0,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "voltage_divider",
        "components": ["R1", "R2"],
        "expected": {"vout_V": 0},
        "simulated": {"vout_V": 0.1},
    }])
    results = cross_validate_file(sch, spice)
    assert results == []

def test_multiple_types_combined():
    """Multiple detector types in one file."""
    sch = _make_sch({
        "voltage_dividers": [{"r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}, "ratio": 0.5}],
        "rc_filters": [{"resistor": {"ref": "R3"}, "capacitor": {"ref": "C1"}, "cutoff_hz": 1000.0}],
    })
    spice = _make_spice([
        {"subcircuit_type": "voltage_divider", "components": ["R1", "R2"],
         "expected": {"vout_V": 1.65}, "simulated": {"vout_V": 1.65}},
        {"subcircuit_type": "rc_filter", "components": ["C1", "R3"],
         "simulated": {"fc_hz": 1005.0}},
    ])
    results = cross_validate_file(sch, spice)
    assert len(results) == 2
    types = {r["type"] for r in results}
    assert types == {"voltage_divider", "rc_filter"}


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
