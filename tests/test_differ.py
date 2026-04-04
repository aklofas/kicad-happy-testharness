"""Unit tests for regression/_differ.py — semantic diff engine."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from _differ import extract_manifest_entry


# === extract_manifest_entry: schematic ===

def test_schematic_basic():
    data = {
        "statistics": {"total_components": 50, "total_nets": 30, "total_labels": 5, "total_power_symbols": 3},
        "signal_analysis": {"rc_filters": [1, 2], "voltage_dividers": [1]},
        "design_analysis": {},
        "bom": [{"ref": "R1"}, {"ref": "R2"}],
    }
    entry = extract_manifest_entry(data, "schematic")
    assert entry["total_components"] == 50
    assert entry["total_nets"] == 30
    assert entry["signal_counts"]["rc_filters"] == 2
    assert entry["signal_counts"]["voltage_dividers"] == 1
    assert entry["bom_lines"] == 2

def test_schematic_empty():
    entry = extract_manifest_entry({}, "schematic")
    assert entry["total_components"] == 0
    assert entry["signal_counts"] == {}

def test_schematic_signal_dict():
    data = {"signal_analysis": {"bus_topology": {"spi": {}, "i2c": {}}}, "statistics": {}}
    entry = extract_manifest_entry(data, "schematic")
    assert entry["signal_counts"]["bus_topology"] == 2


# === extract_manifest_entry: pcb ===

def test_pcb_basic():
    data = {"statistics": {"total_footprints": 100, "total_tracks": 500, "total_vias": 20, "total_zones": 4}}
    entry = extract_manifest_entry(data, "pcb")
    assert entry["total_footprints"] == 100
    assert entry["total_tracks"] == 500

def test_pcb_empty():
    entry = extract_manifest_entry({}, "pcb")
    assert entry["total_footprints"] == 0


# === extract_manifest_entry: gerber ===

def test_gerber_basic():
    data = {"layers": [{"name": "F.Cu"}, {"name": "B.Cu"}], "drill_files": [{"file": "a.drl"}]}
    entry = extract_manifest_entry(data, "gerber")
    assert entry["layers"] == 2
    assert entry["drill_files"] == 1

def test_gerber_empty():
    entry = extract_manifest_entry({}, "gerber")
    assert entry["layers"] == 0


# === extract_manifest_entry: spice ===

def test_spice_basic():
    data = {
        "summary": {"total": 10, "pass": 8, "warn": 1, "fail": 0, "skip": 1},
        "simulation_results": [
            {"subcircuit_type": "rc_filter"}, {"subcircuit_type": "rc_filter"},
            {"subcircuit_type": "opamp_circuit"},
        ],
    }
    entry = extract_manifest_entry(data, "spice")
    assert entry["total_sims"] == 10
    assert entry["pass"] == 8
    assert entry["by_type"]["rc_filter"] == 2
    assert entry["by_type"]["opamp_circuit"] == 1
    assert entry["pass_rate"] == 80.0

def test_spice_empty():
    entry = extract_manifest_entry({"summary": {}, "simulation_results": []}, "spice")
    assert entry["total_sims"] == 0
    assert entry["pass_rate"] == 0

def test_spice_zero_total():
    entry = extract_manifest_entry({"summary": {"total": 0, "pass": 0}}, "spice")
    assert entry["pass_rate"] == 0


# === extract_manifest_entry: datasheets ===

def test_datasheets_basic():
    data = {
        "total_parts": 10, "downloaded": 8, "extracted": 5, "sufficient": 4, "stale": 1,
        "avg_score": 7.5,
        "parts": {
            "LM358": {"category": "opamp"}, "TPS5430": {"category": "regulator"},
            "AO3400": {"category": "mosfet"},
        },
    }
    entry = extract_manifest_entry(data, "datasheets")
    assert entry["total_parts"] == 10
    assert entry["extracted"] == 5
    assert entry["by_category"]["opamp"] == 1
    assert entry["by_category"]["regulator"] == 1

def test_datasheets_empty():
    entry = extract_manifest_entry({"parts": {}}, "datasheets")
    assert entry["extracted"] == 0
    assert entry["by_category"] == {}


# === unknown type ===

def test_unknown_type():
    entry = extract_manifest_entry({"x": 1}, "unknown_type")
    assert entry == {}


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
