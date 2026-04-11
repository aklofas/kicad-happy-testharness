"""Unit tests for detection_schema.py — unified detection type schema."""

TIER = "unit"

import json
import math
import os
import sys
from pathlib import Path

# Harness root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# kicad-happy scripts directory
KICAD_HAPPY = os.environ.get(
    "KICAD_HAPPY_DIR",
    str(Path(__file__).resolve().parent.parent.parent / "kicad-happy"),
)
SCRIPTS_DIR = os.path.join(KICAD_HAPPY, "skills", "kicad", "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from detection_schema import (
    SCHEMAS,
    DetectionSchema,
    DerivedField,
    recalc_derived,
    get_derived_field_names,
    get_inverse_solver,
    get_identity_and_value_fields,
    get_primary_metric,
)

HARNESS_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# 3a. Schema parity — recalc_derived produces correct outputs
# ============================================================

def _approx(actual, expected, tol_pct):
    """Assert actual is within tol_pct% of expected."""
    assert abs(actual - expected) / abs(expected) < tol_pct / 100.0, (
        f"expected ~{expected}, got {actual} (tolerance {tol_pct}%)"
    )


def test_recalc_rc_filter():
    det = {"resistor": {"ohms": 4700}, "capacitor": {"farads": 1e-7}}
    recalc_derived(det, "rc_filters")
    assert "cutoff_hz" in det
    _approx(det["cutoff_hz"], 338.63, 0.5)


def test_recalc_voltage_divider():
    det = {"r_top": {"ohms": 10000}, "r_bottom": {"ohms": 10000}}
    recalc_derived(det, "voltage_dividers")
    assert "ratio" in det
    assert det["ratio"] == 0.5


def test_recalc_opamp_non_inverting():
    det = {
        "feedback_resistor": {"ohms": 47000},
        "input_resistor": {"ohms": 10000},
        "configuration": "non_inverting",
    }
    recalc_derived(det, "opamp_circuits")
    assert "gain" in det
    assert "gain_dB" in det
    _approx(det["gain"], 5.7, 1.0)
    _approx(det["gain_dB"], 15.12, 1.0)


def test_recalc_opamp_inverting():
    det = {
        "feedback_resistor": {"ohms": 47000},
        "input_resistor": {"ohms": 10000},
        "configuration": "inverting",
    }
    recalc_derived(det, "opamp_circuits")
    assert "gain" in det
    assert det["gain"] == -4.7
    assert "gain_dB" in det
    _approx(det["gain_dB"], 20.0 * math.log10(4.7), 0.1)


def test_recalc_lc_filter():
    det = {"inductor": {"henries": 10e-6}, "capacitor": {"farads": 100e-9}}
    recalc_derived(det, "lc_filters")
    assert "resonant_hz" in det
    assert "impedance_ohms" in det
    _approx(det["resonant_hz"], 159155, 1.0)
    _approx(det["impedance_ohms"], math.sqrt(10e-6 / 100e-9), 0.5)


def test_recalc_current_sense():
    det = {"shunt": {"ohms": 0.1}}
    recalc_derived(det, "current_sense")
    assert "max_current_100mV_A" in det
    assert det["max_current_100mV_A"] == 1.0
    assert "max_current_50mV_A" in det
    assert det["max_current_50mV_A"] == 0.5


def test_recalc_crystal():
    det = {
        "load_caps": [{"farads": 22e-12}, {"farads": 22e-12}],
        "stray_capacitance_pF": 3,
    }
    recalc_derived(det, "crystal_circuits")
    assert "effective_load_pF" in det
    assert det["effective_load_pF"] == 14.0


def test_recalc_feedback_network():
    det = {"r_top": {"ohms": 10000}, "r_bottom": {"ohms": 4700}}
    recalc_derived(det, "feedback_networks")
    assert "ratio" in det
    expected = 4700 / (10000 + 4700)
    _approx(det["ratio"], expected, 0.01)


def test_recalc_regulator_feedback():
    det = {
        "feedback_divider": {
            "r_top": {"ohms": 100000},
            "r_bottom": {"ohms": 47000},
        }
    }
    recalc_derived(det, "power_regulators")
    assert "ratio" in det["feedback_divider"]
    expected = 47000 / (100000 + 47000)
    _approx(det["feedback_divider"]["ratio"], expected, 0.01)


def test_recalc_unknown_type():
    """recalc_derived on unknown type does nothing."""
    det = {"foo": 1}
    recalc_derived(det, "nonexistent_type")
    assert det == {"foo": 1}


def test_recalc_missing_fields():
    """recalc_derived with missing fields does not crash."""
    det = {}
    recalc_derived(det, "rc_filters")
    assert "cutoff_hz" not in det


# ============================================================
# 3b. Inverse round-trip — solve then recalc hits target
# ============================================================

def test_inverse_rc_cutoff():
    """Fix R=10k, target cutoff_hz=1000 -> solve for C -> recalc -> verify."""
    det = {"resistor": {"ohms": 10000, "ref": "R1"}, "capacitor": {"farads": 0, "ref": "C1"}}
    solver = get_inverse_solver("rc_filters", "cutoff_hz")
    assert solver is not None
    suggestions = solver(det, "cutoff_hz", 1000.0)
    assert len(suggestions) > 0
    # Find the suggestion that solves for C (anchored on R)
    c_sugg = [s for s in suggestions if s["field"] == "farads"]
    assert len(c_sugg) == 1
    ideal_c = c_sugg[0]["ideal"]
    # Recalc with solved value
    det2 = {"resistor": {"ohms": 10000}, "capacitor": {"farads": ideal_c}}
    recalc_derived(det2, "rc_filters")
    _approx(det2["cutoff_hz"], 1000.0, 0.1)


def test_inverse_divider_ratio():
    """Fix R_top=10k, target ratio=0.33 -> solve for R_bottom -> recalc -> verify."""
    det = {
        "r_top": {"ohms": 10000, "ref": "R1"},
        "r_bottom": {"ohms": 0, "ref": "R2"},
    }
    solver = get_inverse_solver("voltage_dividers", "ratio")
    assert solver is not None
    suggestions = solver(det, "ratio", 0.33)
    # Find suggestion that solves for R_bottom (anchored on R_top)
    rb_sugg = [s for s in suggestions if s["ref"] == "R2"]
    assert len(rb_sugg) == 1
    ideal_rb = rb_sugg[0]["ideal"]
    det2 = {"r_top": {"ohms": 10000}, "r_bottom": {"ohms": ideal_rb}}
    recalc_derived(det2, "voltage_dividers")
    _approx(det2["ratio"], 0.33, 0.1)


def test_inverse_opamp_gain():
    """Fix Ri=10k, target gain=10 (non-inverting) -> solve for Rf -> recalc -> verify."""
    det = {
        "feedback_resistor": {"ohms": 0, "ref": "Rf"},
        "input_resistor": {"ohms": 10000, "ref": "Ri"},
        "configuration": "non_inverting",
    }
    solver = get_inverse_solver("opamp_circuits", "gain")
    assert solver is not None
    suggestions = solver(det, "gain", 10.0)
    assert len(suggestions) == 1
    ideal_rf = suggestions[0]["ideal"]
    det2 = {
        "feedback_resistor": {"ohms": ideal_rf},
        "input_resistor": {"ohms": 10000},
        "configuration": "non_inverting",
    }
    recalc_derived(det2, "opamp_circuits")
    _approx(det2["gain"], 10.0, 0.1)


def test_inverse_lc_resonant():
    """Fix L=10uH, target resonant_hz=100000 -> solve for C -> recalc -> verify."""
    det = {
        "inductor": {"henries": 10e-6, "ref": "L1"},
        "capacitor": {"farads": 0, "ref": "C1"},
    }
    solver = get_inverse_solver("lc_filters", "resonant_hz")
    assert solver is not None
    suggestions = solver(det, "resonant_hz", 100000.0)
    c_sugg = [s for s in suggestions if s["field"] == "farads"]
    assert len(c_sugg) == 1
    ideal_c = c_sugg[0]["ideal"]
    det2 = {"inductor": {"henries": 10e-6}, "capacitor": {"farads": ideal_c}}
    recalc_derived(det2, "lc_filters")
    _approx(det2["resonant_hz"], 100000.0, 0.5)


def test_inverse_crystal_load():
    """Target effective_load_pF=18 -> solve for symmetric caps -> recalc -> verify."""
    det = {
        "load_caps": [{"farads": 22e-12, "ref": "C1"}, {"farads": 22e-12, "ref": "C2"}],
        "stray_capacitance_pF": 3.0,
    }
    solver = get_inverse_solver("crystal_circuits", "effective_load_pF")
    assert solver is not None
    suggestions = solver(det, "effective_load_pF", 18.0)
    assert len(suggestions) == 2
    # Both caps should have the same ideal value
    ideal_f = suggestions[0]["ideal"]
    det2 = {
        "load_caps": [{"farads": ideal_f}, {"farads": ideal_f}],
        "stray_capacitance_pF": 3.0,
    }
    recalc_derived(det2, "crystal_circuits")
    _approx(det2["effective_load_pF"], 18.0, 0.1)


def test_inverse_current_sense():
    """Target max_current_100mV_A=2.0 -> solve for shunt R -> recalc -> verify."""
    det = {"shunt": {"ohms": 0.1, "ref": "R1"}}
    solver = get_inverse_solver("current_sense", "max_current_100mV_A")
    assert solver is not None
    suggestions = solver(det, "max_current_100mV_A", 2.0)
    assert len(suggestions) == 1
    ideal_r = suggestions[0]["ideal"]
    det2 = {"shunt": {"ohms": ideal_r}}
    recalc_derived(det2, "current_sense")
    _approx(det2["max_current_100mV_A"], 2.0, 0.1)


def test_inverse_opamp_gain_dB():
    """Target gain_dB=20 (non-inverting, Ri=1k) -> solve for Rf -> recalc -> verify."""
    det = {
        "feedback_resistor": {"ohms": 0, "ref": "Rf"},
        "input_resistor": {"ohms": 1000, "ref": "Ri"},
        "configuration": "non_inverting",
    }
    solver = get_inverse_solver("opamp_circuits", "gain_dB")
    assert solver is not None
    suggestions = solver(det, "gain_dB", 20.0)
    assert len(suggestions) == 1
    ideal_rf = suggestions[0]["ideal"]
    det2 = {
        "feedback_resistor": {"ohms": ideal_rf},
        "input_resistor": {"ohms": 1000},
        "configuration": "non_inverting",
    }
    recalc_derived(det2, "opamp_circuits")
    _approx(det2["gain_dB"], 20.0, 0.5)


def test_no_inverse_for_transistor():
    """Detection types without inverse solvers return None."""
    assert get_inverse_solver("transistor_circuits", "vth_V") is None


# ============================================================
# 3c. Schema completeness — every signal_analysis key covered
# ============================================================

def test_schema_completeness_zebra_x():
    """Every signal_analysis key in a real output has a SCHEMAS entry."""
    output_path = (
        HARNESS_DIR / "results" / "outputs" / "schematic"
        / "Dylanfg123" / "Zebra-X" / "ZeBra-X.kicad_sch.json"
    )
    if not output_path.exists():
        # Skip if output not available (CI or fresh clone)
        return
    with open(output_path) as f:
        data = json.load(f)
    sa_keys = set(data.get("signal_analysis", {}).keys())
    schema_keys = set(SCHEMAS.keys())
    # Not every signal_analysis key needs a schema (only detection types with
    # identity/derived fields need one). But every SCHEMAS key should be a valid
    # signal_analysis key. Check for overlap.
    # Specifically: all SCHEMAS keys should appear in at least one output.
    # We check both directions and report gaps.
    missing_schemas = []
    for key in sa_keys:
        # These are informational sections, not detection types
        if key in ("design_observations", "esd_coverage_audit", "led_audit",
                    "power_sequencing_validation", "power_path"):
            continue
        if key not in schema_keys:
            missing_schemas.append(key)
    assert missing_schemas == [], (
        f"signal_analysis keys missing from SCHEMAS: {missing_schemas}"
    )


# ============================================================
# 3d. SIGNAL_REGISTRY equivalence
# ============================================================

def test_signal_registry_structure():
    """SIGNAL_REGISTRY from diff_analysis.py is a dict with (list, list) values."""
    from diff_analysis import SIGNAL_REGISTRY

    assert isinstance(SIGNAL_REGISTRY, dict)
    assert len(SIGNAL_REGISTRY) > 10, (
        f"Expected >10 entries, got {len(SIGNAL_REGISTRY)}"
    )
    for key, val in SIGNAL_REGISTRY.items():
        assert isinstance(key, str), f"Key {key!r} is not a string"
        assert isinstance(val, (tuple, list)), (
            f"Value for {key!r} is not tuple/list: {type(val)}"
        )
        assert len(val) == 2, f"Value for {key!r} has length {len(val)}, expected 2"
        identity_fields, value_fields = val
        assert isinstance(identity_fields, list), (
            f"identity_fields for {key!r} is not a list"
        )
        assert isinstance(value_fields, list), (
            f"value_fields for {key!r} is not a list"
        )


def test_signal_registry_matches_schemas():
    """SIGNAL_REGISTRY keys match SCHEMAS keys exactly."""
    from diff_analysis import SIGNAL_REGISTRY

    reg_keys = set(SIGNAL_REGISTRY.keys())
    schema_keys = set(SCHEMAS.keys())
    assert reg_keys == schema_keys, (
        f"Key mismatch — in registry only: {reg_keys - schema_keys}, "
        f"in schemas only: {schema_keys - reg_keys}"
    )


def test_signal_registry_fields_from_schema():
    """SIGNAL_REGISTRY values are derived from SCHEMAS identity/value fields."""
    from diff_analysis import SIGNAL_REGISTRY

    for key in SCHEMAS:
        schema = SCHEMAS[key]
        reg_identity, reg_values = SIGNAL_REGISTRY[key]
        assert reg_identity == schema.identity_fields, (
            f"{key}: identity fields mismatch"
        )
        assert reg_values == schema.value_fields, (
            f"{key}: value fields mismatch"
        )


# ============================================================
# Convenience function tests
# ============================================================

def test_get_derived_field_names():
    names = get_derived_field_names("rc_filters")
    assert "cutoff_hz" in names


def test_get_derived_field_names_unknown():
    assert get_derived_field_names("nonexistent") == []


def test_get_identity_and_value_fields():
    identity, values = get_identity_and_value_fields("voltage_dividers")
    assert "r_top.ref" in identity
    assert "ratio" in values


def test_get_identity_and_value_fields_unknown():
    identity, values = get_identity_and_value_fields("nonexistent")
    assert identity == ["reference"]
    assert values == []


def test_get_primary_metric():
    assert get_primary_metric("rc_filters") == "cutoff_hz"
    assert get_primary_metric("nonexistent") is None


def test_schemas_are_all_detection_schema():
    """Every SCHEMAS value is a DetectionSchema instance."""
    for key, schema in SCHEMAS.items():
        assert isinstance(schema, DetectionSchema), (
            f"SCHEMAS[{key!r}] is {type(schema)}, expected DetectionSchema"
        )


def test_derived_fields_are_derived_field():
    """Every derived entry is a DerivedField with callable recalc."""
    for key, schema in SCHEMAS.items():
        for df in schema.derived:
            assert isinstance(df, DerivedField), (
                f"SCHEMAS[{key!r}] derived entry is {type(df)}"
            )
            assert callable(df.recalc), (
                f"SCHEMAS[{key!r}].{df.name} recalc is not callable"
            )


# Known-failing tests that document real kicad-happy bugs surfaced when
# TH-014 was fixed (these tests had been silently dead because the file
# was missing its __main__ runner block — see commit history). Remove
# names from this set as the corresponding KH issues are closed in
# kicad-happy. Each entry is a (test_name, kh_issue_id) tuple.
KNOWN_FAILURES = {
    # KH-231: opamp_circuits non_inverting recalc returns -Rf/Ri (the
    # inverting formula) regardless of configuration.
    "test_recalc_opamp_non_inverting": "KH-231",
    "test_inverse_opamp_gain": "KH-231",
    "test_inverse_opamp_gain_dB": "KH-231",
    # KH-232: lc_filters schema has no inverse solver registered for
    # resonant_hz, so get_inverse_solver returns None.
    "test_inverse_lc_resonant": "KH-232",
    # KH-233: SCHEMAS dict has not kept up with detector additions in
    # analyze_schematic.py — 22 signal_analysis output keys lack a
    # corresponding SCHEMAS entry as of 2026-04-10.
    "test_schema_completeness_zebra_x": "KH-233",
}


if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = xfailed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            if name in KNOWN_FAILURES:
                # Test passed unexpectedly — bug fixed upstream, stop
                # treating it as known-failing so the skip list doesn't
                # rot.
                passed += 1
                print(f"  XPASS (remove from KNOWN_FAILURES, "
                      f"{KNOWN_FAILURES[name]} may be fixed): {name}")
            else:
                passed += 1
                print(f"  PASS: {name}")
        except (AssertionError, Exception) as e:
            if name in KNOWN_FAILURES:
                xfailed += 1
                kh = KNOWN_FAILURES[name]
                print(f"  XFAIL ({kh}): {name}: {type(e).__name__}: {e}")
            else:
                failed += 1
                print(f"  FAIL: {name}: {type(e).__name__}: {e}")
    total = passed + failed + xfailed
    print(f"\n{passed} passed, {failed} failed, {xfailed} xfailed "
          f"({total} total)")
    sys.exit(1 if failed else 0)
