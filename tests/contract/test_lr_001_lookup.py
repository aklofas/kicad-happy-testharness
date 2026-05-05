"""Contract tests for LR-001 lookup() upgrade (4b)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))


def test_lr_001_helper_smoke_missing_mpn(tmp_path):
    """get_facts returns None for an unknown LED MPN (cache miss)."""
    from lookup_helpers import get_facts
    assert get_facts("UNKNOWN-LED", cache_dir=tmp_path) is None


def test_lr_001_falls_back_to_heuristic_when_no_facts(tmp_path):
    """When get_facts returns None (cache miss), detector emits with confidence='heuristic'."""
    from kicad_types import AnalysisContext
    import validation_detectors

    # Minimal LED: no series resistor, no transistor/IC driver.
    # The LED is on n1="VCC_3V3" (power) and n2="LED_NET" (non-power).
    # detect path: no series resistors found → emits "no current-limiting resistor" at severity=error.
    ref = "D1"
    led = {
        "reference": ref,
        "value": "LED_RED",
        "type": "led",
        "lib_id": "Device:LED",
        "footprint": "",
        "properties": {},
    }
    ctx = AnalysisContext(
        components=[led],
        nets={
            "VCC_3V3": {"pins": [{"component": ref, "pin_number": "A", "pin_name": "A", "x": 0, "y": 0}]},
            "LED_NET": {"pins": [{"component": ref, "pin_number": "K", "pin_name": "K", "x": 0, "y": 0}]},
        },
        lib_symbols={},
        pin_net={(ref, "A"): ("VCC_3V3", None), (ref, "K"): ("LED_NET", None)},
        known_power_rails={"VCC_3V3"},
        source="test",
    )
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)

    with patch.object(validation_detectors, "get_facts", return_value=None):
        findings = validation_detectors.validate_led_resistors(ctx)

    assert findings, "Expected at least one LR-001 finding"
    lr_findings = [f for f in findings if f.get("rule_id") == "LR-001"]
    assert lr_findings, "Expected LR-001 rule_id on findings"
    assert all(f["confidence"] == "heuristic" for f in lr_findings), (
        f"Expected confidence='heuristic', got: {[f['confidence'] for f in lr_findings]}"
    )
    assert all(f["evidence_source"] == "topology" for f in lr_findings), (
        f"Expected evidence_source='topology', got: {[f['evidence_source'] for f in lr_findings]}"
    )


def test_lr_001_datasheet_branch_fires_when_facts_has_vf(tmp_path):
    """When get_facts() returns facts with .diode.vf populated, validate_led_resistors()
    emits findings with confidence='datasheet-backed' and evidence_source='datasheet'."""
    from datasheet_types import SpecValue, Evidence
    from kicad_types import AnalysisContext
    import validation_detectors

    # Build a SpecValue for Vf = 2.0V (typ). Schema fields store list[SpecValue].
    ev = Evidence(page=3, confidence="medium", method="table")
    sv_vf = SpecValue(unit="V", evidence=ev, typ=2.0, min=1.8, max=2.2)

    # Build minimal facts mock: facts.diode.vf = [sv_vf] (list, as the schema stores it)
    fake_diode = MagicMock()
    fake_diode.vf = [sv_vf]
    fake_diode.if_max = None  # if_max not populated — Vf alone triggers datasheet path
    fake_facts = MagicMock()
    fake_facts.diode = fake_diode

    # Net topology: R1 (50R) between VCC_5V and LED_A, LED between LED_A and GND.
    # Detector finds R1 as series resistor with rail=VCC_5V (5V).
    # With Vf=2.0V from datasheet: current = (5 - 2.0) / 50 * 1000 = 60mA > 40mA threshold.
    led_ref = "D1"
    res_ref = "R1"
    led = {
        "reference": led_ref,
        "value": "FAKE-LED",
        "mpn": "FAKE-LED-MPN",
        "type": "led",
        "lib_id": "Device:LED",
        "footprint": "",
        "properties": {},
    }
    resistor = {
        "reference": res_ref,
        "value": "50",
        "type": "resistor",
        "lib_id": "Device:R",
        "footprint": "",
        "properties": {},
    }
    ctx = AnalysisContext(
        components=[led, resistor],
        nets={
            "VCC_5V": {"pins": [{"component": res_ref, "pin_number": "1", "pin_name": "1", "x": 0, "y": 0}]},
            "LED_A": {"pins": [
                {"component": res_ref, "pin_number": "2", "pin_name": "2", "x": 0, "y": 0},
                {"component": led_ref, "pin_number": "A", "pin_name": "A", "x": 0, "y": 0},
            ]},
            "GND": {"pins": [{"component": led_ref, "pin_number": "K", "pin_name": "K", "x": 0, "y": 0}]},
        },
        lib_symbols={},
        pin_net={
            (res_ref, "1"): ("VCC_5V", None),
            (res_ref, "2"): ("LED_A", None),
            (led_ref, "A"): ("LED_A", None),
            (led_ref, "K"): ("GND", None),
        },
        known_power_rails={"VCC_5V", "GND"},
        source="test",
    )
    # Wire parsed_values so the resistor has 50 ohms.
    ctx.parsed_values = {res_ref: 50.0}
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)

    with patch.object(validation_detectors, "get_facts", return_value=fake_facts):
        findings = validation_detectors.validate_led_resistors(ctx)

    lr_findings = [f for f in findings if f.get("rule_id") == "LR-001"]
    assert lr_findings, (
        "Expected at least one LR-001 finding (current too high) with datasheet-backed confidence"
    )
    assert all(f["confidence"] == "datasheet-backed" for f in lr_findings), (
        f"Expected confidence='datasheet-backed', got: {[f['confidence'] for f in lr_findings]}"
    )
    assert all(f["evidence_source"] == "datasheet" for f in lr_findings), (
        f"Expected evidence_source='datasheet', got: {[f['evidence_source'] for f in lr_findings]}"
    )
