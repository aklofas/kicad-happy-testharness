"""Unit tests for validate/validate_spice.py — SPICE cross-validation."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "validate"))
from validate_spice import cross_validate_file


def _make_sch(detectors):
    """Build minimal schematic JSON with findings detectors."""
    findings = []
    _DETECTOR_MAP = {
        "voltage_dividers": "detect_voltage_dividers",
        "rc_filters": "detect_rc_filters",
        "lc_filters": "detect_lc_filters",
        "current_sense": "detect_current_sense",
        "feedback_networks": "validate_feedback_stability",
        "opamp_circuits": "detect_opamp_circuits",
        "power_regulators": "detect_power_regulators",
    }
    for key, items in detectors.items():
        det_name = _DETECTOR_MAP.get(key, f"detect_{key}")
        if isinstance(items, list):
            for item in items:
                entry = dict(item)
                entry["detector"] = det_name
                findings.append(entry)
    return {"findings": findings}


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


# === feedback_network cross-validation ===

def test_feedback_network_match():
    sch = _make_sch({"feedback_networks": [{
        "r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}, "ratio": 0.25,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "feedback_network",
        "components": ["R1", "R2"],
        "expected": {"ratio": 0.25, "fb_voltage_V": 0.825},
        "simulated": {"fb_voltage_V": 0.826},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 1
    assert results[0]["status"] == "match"
    assert results[0]["type"] == "feedback_network"

def test_feedback_network_mismatch():
    sch = _make_sch({"feedback_networks": [{
        "r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}, "ratio": 0.25,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "feedback_network",
        "components": ["R1", "R2"],
        "expected": {"fb_voltage_V": 0.825},
        "simulated": {"fb_voltage_V": 1.5},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 1
    assert results[0]["status"] == "mismatch"

def test_feedback_network_zero_expected():
    sch = _make_sch({"feedback_networks": [{
        "r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}, "ratio": 0.0,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "feedback_network",
        "components": ["R1", "R2"],
        "expected": {"fb_voltage_V": 0},
        "simulated": {"fb_voltage_V": 0.1},
    }])
    results = cross_validate_file(sch, spice)
    assert results == []


# === opamp_circuit cross-validation ===

def test_opamp_circuit_match():
    sch = _make_sch({"opamp_circuits": [{
        "reference": "U1", "configuration": "non-inverting",
    }]})
    spice = _make_spice([{
        "subcircuit_type": "opamp_circuit",
        "components": ["U1"],
        "expected": {"gain_dB": 20.0},
        "simulated": {"gain_dB": 20.1, "gain_linear": 10.12, "bandwidth_hz": 100000},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 1
    assert results[0]["status"] == "match"
    assert results[0]["type"] == "opamp_circuit"
    assert results[0]["delta_pct"] < 5.0

def test_opamp_circuit_mismatch():
    sch = _make_sch({"opamp_circuits": [{
        "reference": "U1", "configuration": "inverting",
    }]})
    spice = _make_spice([{
        "subcircuit_type": "opamp_circuit",
        "components": ["U1"],
        "expected": {"gain_dB": 20.0},
        "simulated": {"gain_dB": 6.0, "gain_linear": 2.0, "bandwidth_hz": 50000},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 1
    assert results[0]["status"] == "mismatch"

def test_opamp_circuit_no_expected_gain():
    """No expected gain_dB means no cross-validation."""
    sch = _make_sch({"opamp_circuits": [{
        "reference": "U1", "configuration": "unknown",
    }]})
    spice = _make_spice([{
        "subcircuit_type": "opamp_circuit",
        "components": ["U1"],
        "expected": {},
        "simulated": {"gain_dB": 20.0, "gain_linear": 10.0, "bandwidth_hz": 100000},
    }])
    results = cross_validate_file(sch, spice)
    assert results == []

def test_opamp_circuit_no_reference():
    """Opamp with empty reference should be skipped."""
    sch = _make_sch({"opamp_circuits": [{
        "reference": "", "configuration": "buffer",
    }]})
    spice = _make_spice([{
        "subcircuit_type": "opamp_circuit",
        "components": ["U1"],
        "expected": {"gain_dB": 0.0},
        "simulated": {"gain_dB": 0.0},
    }])
    results = cross_validate_file(sch, spice)
    assert results == []


# === regulator_feedback cross-validation ===

def test_regulator_feedback_match():
    sch = _make_sch({"power_regulators": [{
        "ref": "U1", "topology": "switching",
        "feedback_divider": {
            "r_top": {"ref": "R1", "ohms": 100000},
            "r_bottom": {"ref": "R2", "ohms": 22000},
            "ratio": 0.18,
        },
        "estimated_vout": 3.3,
    }]})
    spice = _make_spice([{
        "subcircuit_type": "regulator_feedback",
        "components": ["R1", "R2"],
        "regulator": "U1",
        "expected": {"vfb_V": 0.6, "vref_V": 0.6, "ratio": 0.18},
        "simulated": {"vfb_V": 0.6001},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 1
    assert results[0]["status"] == "match"
    assert results[0]["type"] == "regulator_feedback"

def test_regulator_feedback_mismatch():
    sch = _make_sch({"power_regulators": [{
        "ref": "U1",
        "feedback_divider": {
            "r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}, "ratio": 0.18,
        },
    }]})
    spice = _make_spice([{
        "subcircuit_type": "regulator_feedback",
        "components": ["R1", "R2"],
        "expected": {"vfb_V": 0.6},
        "simulated": {"vfb_V": 1.2},
    }])
    results = cross_validate_file(sch, spice)
    assert len(results) == 1
    assert results[0]["status"] == "mismatch"

def test_regulator_feedback_no_divider():
    """Regulator without feedback_divider should be skipped."""
    sch = _make_sch({"power_regulators": [{
        "ref": "U1", "topology": "LDO",
    }]})
    spice = _make_spice([{
        "subcircuit_type": "regulator_feedback",
        "components": ["R1", "R2"],
        "expected": {"vfb_V": 0.6},
        "simulated": {"vfb_V": 0.6},
    }])
    results = cross_validate_file(sch, spice)
    assert results == []

def test_regulator_feedback_zero_expected():
    sch = _make_sch({"power_regulators": [{
        "ref": "U1",
        "feedback_divider": {
            "r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}, "ratio": 0.0,
        },
    }]})
    spice = _make_spice([{
        "subcircuit_type": "regulator_feedback",
        "components": ["R1", "R2"],
        "expected": {"vfb_V": 0},
        "simulated": {"vfb_V": 0.1},
    }])
    results = cross_validate_file(sch, spice)
    assert results == []


# === all 7 types combined ===

def test_all_seven_types():
    """All cross-validation types work together."""
    sch = _make_sch({
        "voltage_dividers": [{"r_top": {"ref": "R1"}, "r_bottom": {"ref": "R2"}, "ratio": 0.5}],
        "rc_filters": [{"resistor": {"ref": "R3"}, "capacitor": {"ref": "C1"}, "cutoff_hz": 1000.0}],
        "lc_filters": [{"inductor": {"ref": "L1"}, "capacitor": {"ref": "C2"}, "resonant_hz": 50000.0}],
        "current_sense": [{"shunt": {"ref": "R4"}, "max_current_50mV_A": 0.5}],
        "feedback_networks": [{"r_top": {"ref": "R5"}, "r_bottom": {"ref": "R6"}, "ratio": 0.25}],
        "opamp_circuits": [{"reference": "U1", "configuration": "non-inverting"}],
        "power_regulators": [{"ref": "U2", "feedback_divider": {
            "r_top": {"ref": "R7"}, "r_bottom": {"ref": "R8"}, "ratio": 0.18,
        }}],
    })
    spice = _make_spice([
        {"subcircuit_type": "voltage_divider", "components": ["R1", "R2"],
         "expected": {"vout_V": 1.65}, "simulated": {"vout_V": 1.65}},
        {"subcircuit_type": "rc_filter", "components": ["C1", "R3"],
         "simulated": {"fc_hz": 1005.0}},
        {"subcircuit_type": "lc_filter", "components": ["C2", "L1"],
         "simulated": {"resonant_hz": 50100.0}},
        {"subcircuit_type": "current_sense", "components": ["R4"],
         "simulated": {"i_at_50mV_A": 0.5001}},
        {"subcircuit_type": "feedback_network", "components": ["R5", "R6"],
         "expected": {"fb_voltage_V": 0.825}, "simulated": {"fb_voltage_V": 0.826}},
        {"subcircuit_type": "opamp_circuit", "components": ["U1"],
         "expected": {"gain_dB": 20.0}, "simulated": {"gain_dB": 20.1}},
        {"subcircuit_type": "regulator_feedback", "components": ["R7", "R8"],
         "expected": {"vfb_V": 0.6}, "simulated": {"vfb_V": 0.6001}},
    ])
    results = cross_validate_file(sch, spice)
    types = {r["type"] for r in results}
    assert types == {
        "voltage_divider", "rc_filter", "lc_filter", "current_sense",
        "feedback_network", "opamp_circuit", "regulator_feedback",
    }
    assert all(r["status"] == "match" for r in results)


# === edge cases ===

def test_empty_findings():
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
