"""Unit tests for tools/spice_coverage.py — SPICE simulation coverage metrics."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from spice_coverage import (
    count_detections, count_simulations, merge_coverage,
    aggregate_rows, find_unmapped_types, DETECTOR_SPICE_MAP,
)


def test_count_detections_basic():
    data = {
        "findings": [
            {"detector": "detect_voltage_dividers", "ref": "R1"},
            {"detector": "detect_voltage_dividers", "ref": "R2"},
            {"detector": "detect_rc_filters", "ref": "R1"},
        ]
    }
    counts = count_detections(data)
    assert counts["voltage_dividers"] == 2
    assert counts["rc_filters"] == 1


def test_count_detections_empty():
    counts = count_detections({})
    assert all(v == 0 for v in counts.values())


def test_count_detections_ignores_non_list():
    """Non-list findings value (malformed) produces zero counts."""
    data = {"findings": "not_a_list"}
    counts = count_detections(data)
    assert counts.get("voltage_dividers", 0) == 0


def test_count_simulations_basic():
    data = {
        "simulation_results": [
            {"subcircuit_type": "voltage_divider", "status": "pass"},
            {"subcircuit_type": "voltage_divider", "status": "warn"},
            {"subcircuit_type": "rc_filter", "status": "fail"},
        ]
    }
    sims = count_simulations(data)
    assert sims["voltage_divider"]["total"] == 2
    assert sims["voltage_divider"]["pass"] == 1
    assert sims["voltage_divider"]["warn"] == 1
    assert sims["rc_filter"]["total"] == 1
    assert sims["rc_filter"]["fail"] == 1


def test_count_simulations_empty():
    sims = count_simulations({})
    assert len(sims) == 0


def test_count_simulations_skip_status():
    data = {
        "simulation_results": [
            {"subcircuit_type": "crystal_circuit", "status": "skip"},
            {"subcircuit_type": "crystal_circuit", "status": "pass"},
        ]
    }
    sims = count_simulations(data)
    assert sims["crystal_circuit"]["skip"] == 1
    assert sims["crystal_circuit"]["pass"] == 1
    assert sims["crystal_circuit"]["total"] == 2


def test_merge_coverage_basic():
    detections = {"voltage_dividers": 10, "rc_filters": 5}
    simulations = {
        "voltage_divider": {"total": 8, "pass": 6, "warn": 1, "fail": 1, "skip": 0},
    }
    rows = merge_coverage(detections, simulations)
    vd = [r for r in rows if r["detector"] == "voltage_dividers"][0]
    assert vd["detected"] == 10
    assert vd["simulated"] == 8
    assert vd["coverage_pct"] == 80.0
    assert vd["pass"] == 6
    rc = [r for r in rows if r["detector"] == "rc_filters"][0]
    assert rc["detected"] == 5
    assert rc["simulated"] == 0
    assert rc["coverage_pct"] == 0


def test_merge_coverage_zero_detected():
    """Simulations with no detections → 0% coverage (not infinity)."""
    detections = {}
    simulations = {
        "voltage_divider": {"total": 3, "pass": 3, "warn": 0, "fail": 0, "skip": 0},
    }
    rows = merge_coverage(detections, simulations)
    vd = [r for r in rows if r["detector"] == "voltage_dividers"][0]
    assert vd["detected"] == 0
    assert vd["simulated"] == 3
    assert vd["coverage_pct"] == 0


def test_aggregate_rows():
    rows = [
        {"detector": "voltage_dividers", "spice_type": "voltage_divider",
         "detected": 5, "simulated": 3, "coverage_pct": 60.0,
         "pass": 2, "warn": 1, "fail": 0, "skip": 0},
        {"detector": "voltage_dividers", "spice_type": "voltage_divider",
         "detected": 10, "simulated": 8, "coverage_pct": 80.0,
         "pass": 7, "warn": 0, "fail": 1, "skip": 0},
    ]
    agg = aggregate_rows(rows)
    vd = [r for r in agg if r["detector"] == "voltage_dividers"][0]
    assert vd["detected"] == 15
    assert vd["simulated"] == 11
    assert vd["coverage_pct"] == 73.3
    assert vd["pass"] == 9
    assert vd["warn"] == 1
    assert vd["fail"] == 1


def test_aggregate_empty():
    agg = aggregate_rows([])
    assert all(r["detected"] == 0 for r in agg)
    assert all(r["simulated"] == 0 for r in agg)


def test_find_unmapped_types():
    sims = {
        "voltage_divider": {"total": 5},
        "exotic_new_type": {"total": 2},
        "another_unknown": {"total": 1},
    }
    unmapped = find_unmapped_types(sims)
    assert "exotic_new_type" in unmapped
    assert "another_unknown" in unmapped
    assert "voltage_divider" not in unmapped


def test_find_unmapped_types_empty():
    assert find_unmapped_types({}) == []


def test_detector_spice_map_no_duplicates():
    """Every entry in DETECTOR_SPICE_MAP should have a distinct SPICE type."""
    spice_types = list(DETECTOR_SPICE_MAP.values())
    assert len(spice_types) == len(set(spice_types))


def test_merge_all_detectors_present():
    """merge_coverage always returns a row for every detector in the map."""
    rows = merge_coverage({}, {})
    detector_keys = {r["detector"] for r in rows}
    assert detector_keys == set(DETECTOR_SPICE_MAP.keys())


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
