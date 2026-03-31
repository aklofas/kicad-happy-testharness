"""Unit tests for SPICE simulation integration in the regression system.

Tests:
  - SPICE seed assertion generation (seed.py)
  - SPICE structural assertion generation (seed_structural.py)
  - SPICE manifest extraction (_differ.py)
  - SPICE cross-validation logic (validate_spice.py)
  - Full round-trip: generate assertions → evaluate against same data
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from checks import evaluate_assertion
from _differ import extract_manifest_entry
from seed import generate_spice_assertions, _range_bounds
from seed_structural import generate_spice_structural_assertions

# Add validate/ to path for cross-validation tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "validate"))
from validate_spice import cross_validate_file


# ---------------------------------------------------------------------------
# Realistic synthetic SPICE output — used across multiple tests
# ---------------------------------------------------------------------------
SPICE_OUTPUT = {
    "summary": {"total": 8, "pass": 6, "warn": 1, "fail": 0, "skip": 1},
    "simulation_results": [
        {"subcircuit_type": "rc_filter", "status": "pass",
         "components": ["R1", "C1"],
         "simulated": {"fc_hz": 1591.5}, "expected": {"fc_hz": 1591.5}},
        {"subcircuit_type": "rc_filter", "status": "pass",
         "components": ["R2", "C2"],
         "simulated": {"fc_hz": 3386.3}, "expected": {"fc_hz": 3386.3}},
        {"subcircuit_type": "voltage_divider", "status": "pass",
         "components": ["R3", "R4"],
         "simulated": {"vout_V": 1.65}, "expected": {"vout_V": 1.65}},
        {"subcircuit_type": "opamp_circuit", "status": "warn",
         "components": ["U1"],
         "model_note": "TL072 behavioral (GBW=3MHz)",
         "simulated": {"gain_dB": -5.2}, "expected": {"gain": -1.0}},
        {"subcircuit_type": "opamp_circuit", "status": "pass",
         "components": ["U2"],
         "model_note": "NE5532 ideal",
         "simulated": {"gain_dB": 20.1}, "expected": {"gain": 10.0}},
        {"subcircuit_type": "decoupling", "status": "pass",
         "components": ["C3"],
         "simulated": {"impedance_1MHz_ohm": 0.05}},
        {"subcircuit_type": "decoupling", "status": "pass",
         "components": ["C4"],
         "simulated": {"impedance_1MHz_ohm": 0.03}},
        {"subcircuit_type": "crystal_circuit", "status": "skip",
         "components": ["Y1"],
         "note": "no crystal model available"},
    ],
}


# ---------------------------------------------------------------------------
# Seed assertion generation
# ---------------------------------------------------------------------------

def test_spice_seed_count():
    assertions = generate_spice_assertions(SPICE_OUTPUT)
    # Should have: total range + pass min + per-type counts (4 types)
    assert len(assertions) >= 6

def test_spice_seed_total_range():
    assertions = generate_spice_assertions(SPICE_OUTPUT)
    total_assertion = next(a for a in assertions if "count" in a["description"].lower())
    check = total_assertion["check"]
    assert check["op"] == "range"
    assert check["min"] <= 8 <= check["max"]

def test_spice_seed_pass_minimum():
    assertions = generate_spice_assertions(SPICE_OUTPUT)
    pass_assertion = next(a for a in assertions if "passing" in a["description"])
    check = pass_assertion["check"]
    assert check["op"] == "min_count"
    assert check["value"] <= 6  # 80% of 6 = 4.8, so min_pass >= 4

def test_spice_seed_type_counts():
    assertions = generate_spice_assertions(SPICE_OUTPUT)
    type_assertions = [a for a in assertions if a["check"]["op"] == "count_matches"]
    types_found = {a["check"]["pattern"].strip("^$") for a in type_assertions}
    assert "rc_filter" in types_found
    assert "opamp_circuit" in types_found
    assert "decoupling" in types_found
    assert "crystal_circuit" in types_found

def test_spice_seed_ids_unique():
    assertions = generate_spice_assertions(SPICE_OUTPUT)
    ids = [a["id"] for a in assertions]
    assert len(ids) == len(set(ids))

def test_spice_seed_empty_output():
    empty = {"summary": {"total": 0}, "simulation_results": []}
    assert generate_spice_assertions(empty) == []

def test_spice_seed_all_warn():
    """Output with 0 passing should not generate a pass minimum assertion."""
    data = {
        "summary": {"total": 3, "pass": 0, "warn": 3},
        "simulation_results": [
            {"subcircuit_type": "opamp_circuit", "status": "warn"} for _ in range(3)
        ],
    }
    assertions = generate_spice_assertions(data)
    descs = [a["description"] for a in assertions]
    assert not any("passing" in d for d in descs)


# ---------------------------------------------------------------------------
# Structural assertion generation
# ---------------------------------------------------------------------------

def test_spice_structural_type_counts():
    assertions = generate_spice_structural_assertions(SPICE_OUTPUT, strict=True)
    type_assertions = [a for a in assertions if "Exactly" in a["description"]]
    assert len(type_assertions) == 5  # rc_filter, voltage_divider, opamp_circuit, decoupling, crystal_circuit

def test_spice_structural_component_refs():
    assertions = generate_spice_structural_assertions(SPICE_OUTPUT)
    ref_assertions = [a for a in assertions if "simulated as" in a["description"]]
    refs_found = {a["description"].split(" ")[0] for a in ref_assertions}
    assert "R1" in refs_found
    assert "U1" in refs_found
    assert "C3" in refs_found
    assert "Y1" in refs_found

def test_spice_structural_skips_unannotated():
    """Components ending with ? should be skipped."""
    data = {"simulation_results": [
        {"subcircuit_type": "rc_filter", "components": ["R?", "C?"]},
    ]}
    assertions = generate_spice_structural_assertions(data)
    ref_assertions = [a for a in assertions if "simulated as" in a["description"]]
    assert len(ref_assertions) == 0

def test_spice_structural_deduplicates():
    """Same component appearing in multiple sims should only get one assertion."""
    data = {"simulation_results": [
        {"subcircuit_type": "rc_filter", "components": ["R1", "C1"]},
        {"subcircuit_type": "rc_filter", "components": ["R1", "C2"]},
    ]}
    assertions = generate_spice_structural_assertions(data)
    r1_assertions = [a for a in assertions if a["description"].startswith("R1 ")]
    assert len(r1_assertions) == 1

def test_spice_structural_ids_unique():
    assertions = generate_spice_structural_assertions(SPICE_OUTPUT)
    ids = [a["id"] for a in assertions]
    assert len(ids) == len(set(ids))

def test_spice_structural_empty():
    assert generate_spice_structural_assertions({"simulation_results": []}) == []

def test_spice_structural_strict_vs_tolerant():
    strict = generate_spice_structural_assertions(SPICE_OUTPUT, strict=True)
    tolerant = generate_spice_structural_assertions(SPICE_OUTPUT, strict=False)
    # Both should have same count of type assertions
    strict_types = [a for a in strict if "Exactly" in a["description"] or "~" in a["description"]]
    tolerant_types = [a for a in tolerant if "Exactly" in a["description"] or "~" in a["description"]]
    assert len(strict_types) == len(tolerant_types)


# ---------------------------------------------------------------------------
# Round-trip: seed assertions → evaluate against same data
# ---------------------------------------------------------------------------

def test_spice_seed_roundtrip():
    """All seed assertions should pass against the data they were generated from."""
    assertions = generate_spice_assertions(SPICE_OUTPUT)
    for a in assertions:
        result = evaluate_assertion(a, SPICE_OUTPUT)
        assert result["passed"], f"Assertion {a['id']} failed: {a['description']} — actual={result.get('actual')}, expected={result.get('expected')}"

def test_spice_structural_roundtrip():
    """All structural assertions should pass against their source data."""
    assertions = generate_spice_structural_assertions(SPICE_OUTPUT, strict=True)
    for a in assertions:
        result = evaluate_assertion(a, SPICE_OUTPUT)
        assert result["passed"], f"Assertion {a['id']} failed: {a['description']} — actual={result.get('actual')}, expected={result.get('expected')}"

def test_spice_seed_detects_regression():
    """Assertions from one output should FAIL against a degraded output."""
    assertions = generate_spice_assertions(SPICE_OUTPUT)
    # Create degraded output: fewer sims, fewer passes
    degraded = {
        "summary": {"total": 3, "pass": 2, "warn": 1, "fail": 0, "skip": 0},
        "simulation_results": [
            {"subcircuit_type": "rc_filter", "status": "pass"},
            {"subcircuit_type": "rc_filter", "status": "pass"},
            {"subcircuit_type": "opamp_circuit", "status": "warn"},
        ],
    }
    failures = [a for a in assertions if not evaluate_assertion(a, degraded)["passed"]]
    assert len(failures) > 0, "Should detect regression from 8→3 sims"

def test_spice_structural_detects_missing_component():
    """Structural assertions should fail when a component disappears."""
    assertions = generate_spice_structural_assertions(SPICE_OUTPUT)
    # Remove U1 from the output
    modified = dict(SPICE_OUTPUT)
    modified["simulation_results"] = [
        r for r in SPICE_OUTPUT["simulation_results"]
        if "U1" not in r.get("components", [])
    ]
    u1_assertions = [a for a in assertions if "U1" in a["description"]]
    assert len(u1_assertions) > 0
    for a in u1_assertions:
        result = evaluate_assertion(a, modified)
        assert not result["passed"], f"U1 assertion should fail when U1 removed"


# ---------------------------------------------------------------------------
# Manifest extraction
# ---------------------------------------------------------------------------

def test_spice_manifest_extraction():
    entry = extract_manifest_entry(SPICE_OUTPUT, "spice")
    assert entry["total_sims"] == 8
    assert entry["pass"] == 6
    assert entry["warn"] == 1
    assert entry["fail"] == 0
    assert entry["skip"] == 1
    assert entry["pass_rate"] == 75.0  # 6/8 * 100
    assert entry["by_type"]["rc_filter"] == 2
    assert entry["by_type"]["opamp_circuit"] == 2

def test_spice_manifest_zero_sims():
    entry = extract_manifest_entry({"summary": {"total": 0}}, "spice")
    assert entry["total_sims"] == 0
    assert entry["pass_rate"] == 0


# ---------------------------------------------------------------------------
# Cross-validation (validate_spice.py)
# ---------------------------------------------------------------------------

def test_cross_validate_voltage_divider():
    """Matching voltage divider values should produce 'match' status."""
    schematic = {
        "signal_analysis": {
            "voltage_dividers": [{
                "r_top": {"ref": "R3", "value": 10000},
                "r_bottom": {"ref": "R4", "value": 10000},
                "ratio": 0.5,
            }],
        },
    }
    spice = {
        "simulation_results": [{
            "subcircuit_type": "voltage_divider",
            "components": ["R3", "R4"],
            "simulated": {"vout_V": 1.65},
            "expected": {"vout_V": 1.65},
        }],
    }
    results = cross_validate_file(schematic, spice)
    assert len(results) == 1
    assert results[0]["status"] == "match"
    assert results[0]["delta_pct"] < 0.1

def test_cross_validate_rc_filter():
    """Matching RC filter frequency should produce 'match'."""
    schematic = {
        "signal_analysis": {
            "rc_filters": [{
                "resistor": {"ref": "R1", "value": 1000},
                "capacitor": {"ref": "C1", "value": 1e-7},
                "cutoff_hz": 1591.5,
            }],
        },
    }
    spice = {
        "simulation_results": [{
            "subcircuit_type": "rc_filter",
            "components": ["C1", "R1"],
            "simulated": {"fc_hz": 1591.5},
        }],
    }
    results = cross_validate_file(schematic, spice)
    assert len(results) == 1
    assert results[0]["status"] == "match"

def test_cross_validate_mismatch():
    """10% frequency mismatch should be detected."""
    schematic = {
        "signal_analysis": {
            "rc_filters": [{
                "resistor": {"ref": "R1"}, "capacitor": {"ref": "C1"},
                "cutoff_hz": 1000.0,
            }],
        },
    }
    spice = {
        "simulation_results": [{
            "subcircuit_type": "rc_filter",
            "components": ["C1", "R1"],
            "simulated": {"fc_hz": 1100.0},  # 10% off
        }],
    }
    results = cross_validate_file(schematic, spice)
    assert len(results) == 1
    assert results[0]["status"] == "mismatch"
    assert results[0]["delta_pct"] > 5

def test_cross_validate_no_matching_spice():
    """Components in analyzer but not in SPICE should produce no results."""
    schematic = {
        "signal_analysis": {
            "voltage_dividers": [{
                "r_top": {"ref": "R99"}, "r_bottom": {"ref": "R100"},
                "ratio": 0.5,
            }],
        },
    }
    spice = {"simulation_results": []}
    results = cross_validate_file(schematic, spice)
    assert results == []

def test_cross_validate_empty():
    results = cross_validate_file({}, {})
    assert results == []

def test_cross_validate_current_sense():
    schematic = {
        "signal_analysis": {
            "current_sense": [{
                "shunt": {"ref": "R5", "value": 0.1},
                "max_current_50mV_A": 0.5,
            }],
        },
    }
    spice = {
        "simulation_results": [{
            "subcircuit_type": "current_sense",
            "components": ["R5"],
            "simulated": {"i_at_50mV_A": 0.5},
        }],
    }
    results = cross_validate_file(schematic, spice)
    assert len(results) == 1
    assert results[0]["status"] == "match"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_spice_single_sim():
    """Single simulation should still generate valid assertions."""
    data = {
        "summary": {"total": 1, "pass": 1},
        "simulation_results": [
            {"subcircuit_type": "decoupling", "status": "pass", "components": ["C1"]},
        ],
    }
    seed = generate_spice_assertions(data)
    struct = generate_spice_structural_assertions(data)
    assert len(seed) >= 2  # total range + pass min
    assert len(struct) >= 2  # type count + component ref
    # Round-trip
    for a in seed + struct:
        assert evaluate_assertion(a, data)["passed"]

def test_spice_many_types():
    """All 17 subcircuit types should generate unique assertions."""
    types = [
        "rc_filter", "decoupling", "transistor_circuit", "voltage_divider",
        "lc_filter", "inrush", "protection_device", "opamp_circuit",
        "crystal_circuit", "current_sense", "regulator_feedback",
        "feedback_network", "rf_matching", "rf_chain", "bridge_circuit",
        "snubber_circuit", "bms_balance",
    ]
    data = {
        "summary": {"total": len(types), "pass": len(types)},
        "simulation_results": [
            {"subcircuit_type": t, "status": "pass", "components": [f"X{i}"]}
            for i, t in enumerate(types)
        ],
    }
    assertions = generate_spice_assertions(data)
    type_assertions = [a for a in assertions if a["check"]["op"] == "count_matches"]
    assert len(type_assertions) == 17
    # All should pass
    for a in assertions:
        assert evaluate_assertion(a, data)["passed"]


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
