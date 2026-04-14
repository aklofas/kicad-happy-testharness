"""Unit tests for datasheet_verify.py — datasheet verification bridge."""

TIER = "unit"

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))
import datasheet_verify


# ============================================================
# 2a. Voltage estimation — _estimate_net_voltage
# ============================================================

def test_estimate_3v3():
    assert datasheet_verify._estimate_net_voltage("+3V3", {}) == 3.3

def test_estimate_5v():
    assert datasheet_verify._estimate_net_voltage("+5V", {}) == 5.0

def test_estimate_12v0():
    assert datasheet_verify._estimate_net_voltage("12V0", {}) == 12.0

def test_estimate_signal_name():
    assert datasheet_verify._estimate_net_voltage("SDA", {}) is None

def test_estimate_with_rail_voltages():
    """Rail voltage lookup takes precedence over name parsing."""
    result = datasheet_verify._estimate_net_voltage("+3V3", {"+3V3": 3.3})
    assert result == 3.3


# ============================================================
# 2b. Cap recommendation parsing — _parse_cap_recommendation
# ============================================================

def test_parse_cap_22uf_x2():
    r = datasheet_verify._parse_cap_recommendation("22uF ceramic x2, X5R or X7R")
    assert r["count"] == 2
    assert r["min_farads"] is not None
    assert abs(r["min_farads"] - 22e-6) < 1e-7

def test_parse_cap_100nf_distance():
    r = datasheet_verify._parse_cap_recommendation("100nF within 10mm")
    assert r["min_farads"] is not None
    assert abs(r["min_farads"] - 100e-9) < 1e-11
    assert r["max_distance_mm"] == 10.0

def test_parse_cap_10uf():
    r = datasheet_verify._parse_cap_recommendation("10uF")
    assert r["count"] == 1
    assert r["min_farads"] is not None
    assert abs(r["min_farads"] - 10e-6) < 1e-7

def test_parse_cap_empty():
    r = datasheet_verify._parse_cap_recommendation("")
    assert r["count"] == 1
    assert r["min_farads"] is None


# ============================================================
# 2c. Pin voltage verification — verify_pin_voltages
# ============================================================

def _make_extraction(pins):
    """Build a minimal extraction dict with given pins."""
    return {"pins": pins, "meta": {"extraction_score": 10.0}}


def _write_extraction(tmpdir, mpn, extraction):
    """Write extraction JSON to a temp directory."""
    import re
    sanitized = re.sub(r'[^A-Za-z0-9_]', '_', mpn)
    path = os.path.join(tmpdir, f"{sanitized}.json")
    with open(path, "w") as f:
        json.dump(extraction, f)


def test_pin_voltage_abs_max_exceeded():
    """Pin at abs_max=3.6V on 5V net -> CRITICAL finding."""
    tmpdir = tempfile.mkdtemp()
    try:
        extraction = _make_extraction([
            {"number": "1", "name": "VCC", "type": "power",
             "voltage_abs_max": 3.6, "voltage_operating_max": 3.6},
        ])
        _write_extraction(tmpdir, "ATmega328P", extraction)

        components = [
            {"reference": "U1", "type": "ic", "mpn": "ATmega328P",
             "pin_nets": {"1": "+5V"}},
        ]
        findings = datasheet_verify.verify_pin_voltages(
            components, {}, tmpdir, {})
        assert len(findings) == 1
        assert findings[0]["severity"] == "CRITICAL"
        assert findings[0]["type"] == "pin_voltage_abs_max_exceeded"
        assert findings[0]["ref"] == "U1"
    finally:
        shutil.rmtree(tmpdir)


def test_pin_voltage_within_limits():
    """Pin at abs_max=6.0V on 3.3V net -> no finding."""
    tmpdir = tempfile.mkdtemp()
    try:
        extraction = _make_extraction([
            {"number": "1", "name": "VCC", "type": "power",
             "voltage_abs_max": 6.0, "voltage_operating_max": 5.5},
        ])
        _write_extraction(tmpdir, "LM1117", extraction)

        components = [
            {"reference": "U1", "type": "ic", "mpn": "LM1117",
             "pin_nets": {"1": "+3V3"}},
        ]
        findings = datasheet_verify.verify_pin_voltages(
            components, {}, tmpdir, {})
        assert len(findings) == 0
    finally:
        shutil.rmtree(tmpdir)


def test_pin_voltage_op_max_within_abs_max():
    """Pin at operating_max=3.6V, abs_max=4.2V on 3.3V net -> no finding."""
    tmpdir = tempfile.mkdtemp()
    try:
        extraction = _make_extraction([
            {"number": "1", "name": "VCC", "type": "power",
             "voltage_abs_max": 4.2, "voltage_operating_max": 3.6},
        ])
        _write_extraction(tmpdir, "STM32F4", extraction)

        components = [
            {"reference": "U1", "type": "ic", "mpn": "STM32F4",
             "pin_nets": {"1": "+3V3"}},
        ]
        findings = datasheet_verify.verify_pin_voltages(
            components, {}, tmpdir, {})
        assert len(findings) == 0
    finally:
        shutil.rmtree(tmpdir)


def test_pin_voltage_gnd_skipped():
    """GND pin should be skipped even if voltage mismatch would trigger."""
    tmpdir = tempfile.mkdtemp()
    try:
        extraction = _make_extraction([
            {"number": "1", "name": "GND", "type": "ground",
             "voltage_abs_max": 0.0},
        ])
        _write_extraction(tmpdir, "TPS62130", extraction)

        components = [
            {"reference": "U1", "type": "ic", "mpn": "TPS62130",
             "pin_nets": {"1": "+5V"}},
        ]
        findings = datasheet_verify.verify_pin_voltages(
            components, {}, tmpdir, {})
        assert len(findings) == 0
    finally:
        shutil.rmtree(tmpdir)


def test_pin_voltage_no_extraction():
    """IC without extraction file -> no findings (graceful skip)."""
    tmpdir = tempfile.mkdtemp()
    try:
        components = [
            {"reference": "U1", "type": "ic", "mpn": "NONEXISTENT_PART",
             "pin_nets": {"1": "+5V"}},
        ]
        findings = datasheet_verify.verify_pin_voltages(
            components, {}, tmpdir, {})
        assert len(findings) == 0
    finally:
        shutil.rmtree(tmpdir)


# ============================================================
# 2d. Required externals — verify_required_externals
# ============================================================

def test_required_cap_missing():
    """Required cap, none present -> HIGH finding."""
    tmpdir = tempfile.mkdtemp()
    try:
        extraction = _make_extraction([
            {"number": "1", "name": "BYPASS", "type": "power",
             "required_external": "100nF bypass capacitor"},
        ])
        _write_extraction(tmpdir, "MAX232", extraction)

        components = [
            {"reference": "U1", "type": "ic", "mpn": "MAX232",
             "pin_nets": {"1": "NET_BYPASS"}},
        ]
        nets = {
            "NET_BYPASS": {"pins": [
                {"component": "U1"},
            ]},
        }
        comp_lookup = {"U1": {"type": "ic"}}
        findings = datasheet_verify.verify_required_externals(
            components, nets, tmpdir, comp_lookup)
        assert len(findings) == 1
        assert findings[0]["severity"] == "HIGH"
        assert findings[0]["type"] == "missing_required_external"
    finally:
        shutil.rmtree(tmpdir)


def test_required_cap_present():
    """Required cap, cap present -> no finding."""
    tmpdir = tempfile.mkdtemp()
    try:
        extraction = _make_extraction([
            {"number": "1", "name": "BYPASS", "type": "power",
             "required_external": "100nF bypass capacitor"},
        ])
        _write_extraction(tmpdir, "MAX232", extraction)

        components = [
            {"reference": "U1", "type": "ic", "mpn": "MAX232",
             "pin_nets": {"1": "NET_BYPASS"}},
        ]
        nets = {
            "NET_BYPASS": {"pins": [
                {"component": "U1"},
                {"component": "C1"},
            ]},
        }
        comp_lookup = {
            "U1": {"type": "ic"},
            "C1": {"type": "capacitor"},
        }
        findings = datasheet_verify.verify_required_externals(
            components, nets, tmpdir, comp_lookup)
        assert len(findings) == 0
    finally:
        shutil.rmtree(tmpdir)


def test_required_cap_wrong_type():
    """Required cap, but resistor present -> HIGH finding."""
    tmpdir = tempfile.mkdtemp()
    try:
        extraction = _make_extraction([
            {"number": "1", "name": "BYPASS", "type": "power",
             "required_external": "100nF bypass capacitor"},
        ])
        _write_extraction(tmpdir, "MAX232", extraction)

        components = [
            {"reference": "U1", "type": "ic", "mpn": "MAX232",
             "pin_nets": {"1": "NET_BYPASS"}},
        ]
        nets = {
            "NET_BYPASS": {"pins": [
                {"component": "U1"},
                {"component": "R1"},
            ]},
        }
        comp_lookup = {
            "U1": {"type": "ic"},
            "R1": {"type": "resistor"},
        }
        findings = datasheet_verify.verify_required_externals(
            components, nets, tmpdir, comp_lookup)
        assert len(findings) == 1
        assert findings[0]["severity"] == "HIGH"
    finally:
        shutil.rmtree(tmpdir)


# ============================================================
# 2e. Decoupling verification — verify_decoupling
# ============================================================

def _make_decoupling_scenario(num_caps, required_count, required_text,
                               cap_farads=22e-6, key="decoupling_cap"):
    """Build components/nets/extraction for decoupling tests.

    Returns (components, nets, tmpdir, comp_lookup, parsed_values).
    Caller must clean up tmpdir.
    """
    tmpdir = tempfile.mkdtemp()

    extraction = {
        "meta": {"extraction_score": 10.0},
        "pins": [
            {"number": "1", "name": "VIN", "type": "power",
             "direction": "input"},
        ],
        "application_circuit": {
            key: required_text,
        },
    }
    _write_extraction(tmpdir, "TPS62130", extraction)

    # IC component
    components = [
        {"reference": "U1", "type": "ic", "mpn": "TPS62130",
         "pin_nets": {"1": "+5V"}},
    ]

    net_pins = [{"component": "U1"}]
    comp_lookup = {"U1": {"type": "ic"}}
    parsed_values = {}

    for i in range(num_caps):
        cref = f"C{i + 1}"
        net_pins.append({"component": cref})
        comp_lookup[cref] = {"type": "capacitor", "value": "22uF"}
        parsed_values[cref] = cap_farads

    nets = {"+5V": {"pins": net_pins}}

    return components, nets, tmpdir, comp_lookup, parsed_values


def test_decoupling_zero_caps():
    """0 caps when 2 required -> HIGH."""
    components, nets, tmpdir, comp_lookup, parsed_values = \
        _make_decoupling_scenario(0, 2, "22uF ceramic x2")
    try:
        findings = datasheet_verify.verify_decoupling(
            components, nets, tmpdir, comp_lookup, parsed_values)
        assert len(findings) == 1
        assert findings[0]["severity"] == "HIGH"
        assert findings[0]["type"] == "decoupling_insufficient"
    finally:
        shutil.rmtree(tmpdir)


def test_decoupling_one_of_two():
    """1 cap when 2 required -> MEDIUM."""
    components, nets, tmpdir, comp_lookup, parsed_values = \
        _make_decoupling_scenario(1, 2, "22uF ceramic x2")
    try:
        findings = datasheet_verify.verify_decoupling(
            components, nets, tmpdir, comp_lookup, parsed_values)
        assert len(findings) == 1
        assert findings[0]["severity"] == "MEDIUM"
    finally:
        shutil.rmtree(tmpdir)


def test_decoupling_two_meeting_spec():
    """2 caps meeting spec -> no finding."""
    components, nets, tmpdir, comp_lookup, parsed_values = \
        _make_decoupling_scenario(2, 2, "22uF ceramic x2")
    try:
        findings = datasheet_verify.verify_decoupling(
            components, nets, tmpdir, comp_lookup, parsed_values)
        assert len(findings) == 0
    finally:
        shutil.rmtree(tmpdir)


def test_decoupling_below_80_percent():
    """2 caps below 80% of required value -> finding (don't match)."""
    components, nets, tmpdir, comp_lookup, parsed_values = \
        _make_decoupling_scenario(2, 2, "22uF ceramic x2", cap_farads=10e-6)
    try:
        findings = datasheet_verify.verify_decoupling(
            components, nets, tmpdir, comp_lookup, parsed_values)
        # 10uF < 22uF * 0.8 = 17.6uF, so caps don't match
        assert len(findings) >= 1
        assert findings[0]["type"] == "decoupling_insufficient"
    finally:
        shutil.rmtree(tmpdir)


# ============================================================
# 2f. Orchestrator — run_datasheet_verification
# ============================================================

def test_orchestrator_empty_analysis():
    """Empty analysis -> empty findings."""
    result = datasheet_verify.run_datasheet_verification({})
    assert result["findings"] == []
    assert result["summary"]["total_findings"] == 0


def test_orchestrator_no_extraction_dir():
    """No extraction dir -> empty findings with note."""
    result = datasheet_verify.run_datasheet_verification(
        {"components": [], "nets": {}}, project_dir="/nonexistent/path")
    assert result["findings"] == []
    assert "note" in result["summary"]


def test_orchestrator_full_integration():
    """Full integration with temp dir extraction."""
    tmpdir = tempfile.mkdtemp()
    try:
        # Create datasheets/extracted/ structure
        extract_dir = os.path.join(tmpdir, "datasheets", "extracted")
        os.makedirs(extract_dir)

        # Write an extraction that will trigger a finding
        extraction = _make_extraction([
            {"number": "1", "name": "VCC", "type": "power",
             "voltage_abs_max": 3.6},
        ])
        _write_extraction(extract_dir, "ATmega328P", extraction)

        analysis = {
            "file": os.path.join(tmpdir, "design.kicad_sch"),
            "components": [
                {"reference": "U1", "type": "ic", "mpn": "ATmega328P",
                 "pin_nets": {"1": "+5V"}},
            ],
            "nets": {},
            "rail_voltages": {},
        }

        result = datasheet_verify.run_datasheet_verification(
            analysis, project_dir=tmpdir)
        assert result["summary"]["ics_checked"] == 1
        assert result["summary"]["ics_with_extractions"] == 1
        assert result["summary"]["total_findings"] >= 1
        # Should find the voltage violation
        crit = [f for f in result["findings"] if f["severity"] == "CRITICAL"]
        assert len(crit) >= 1
    finally:
        shutil.rmtree(tmpdir)


# ============================================================
# 2g. Graceful degradation
# ============================================================

def test_graceful_no_extracted_dir():
    """datasheets/extracted/ doesn't exist -> no crash."""
    result = datasheet_verify.run_datasheet_verification(
        {"components": [{"reference": "U1", "type": "ic", "mpn": "PART"}],
         "nets": {}},
        project_dir="/nonexistent")
    assert result["findings"] == []


def test_graceful_malformed_extraction():
    """Malformed extraction JSON -> no crash."""
    tmpdir = tempfile.mkdtemp()
    try:
        import re
        sanitized = re.sub(r'[^A-Za-z0-9_]', '_', "BAD_PART")
        path = os.path.join(tmpdir, f"{sanitized}.json")
        with open(path, "w") as f:
            f.write("{invalid json")

        components = [
            {"reference": "U1", "type": "ic", "mpn": "BAD_PART",
             "pin_nets": {"1": "+5V"}},
        ]
        # Should not raise
        findings = datasheet_verify.verify_pin_voltages(
            components, {}, tmpdir, {})
        assert findings == []
    finally:
        shutil.rmtree(tmpdir)


def test_graceful_empty_pin_nets():
    """Empty pin_nets on IC -> no crash."""
    tmpdir = tempfile.mkdtemp()
    try:
        extraction = _make_extraction([
            {"number": "1", "name": "VCC", "type": "power",
             "voltage_abs_max": 3.6},
        ])
        _write_extraction(tmpdir, "SOME_IC", extraction)

        components = [
            {"reference": "U1", "type": "ic", "mpn": "SOME_IC",
             "pin_nets": {}},
        ]
        findings = datasheet_verify.verify_pin_voltages(
            components, {}, tmpdir, {})
        assert findings == []
    finally:
        shutil.rmtree(tmpdir)


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
        except Exception as e:
            failed += 1
            print(f"  FAIL: {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
