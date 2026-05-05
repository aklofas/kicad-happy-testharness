"""Contract tests for OV-001 VCC-outside-recommended detector (4c)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))


def _make_ctx(components, nets, pin_net, known_power_rails, tmp_path):
    from kicad_types import AnalysisContext
    ctx = AnalysisContext(
        components=components, nets=nets, lib_symbols={},
        pin_net=pin_net, known_power_rails=known_power_rails, source="test",
    )
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)
    return ctx


def _build_facts(rec_specs, power_domain="VDD", pin_name="VDD"):
    """Build a mock DatasheetFacts with base.recommended_operating[VDD] = rec_specs."""
    fake_pin = MagicMock()
    fake_pin.numbers = ["1"]
    fake_pin.name = pin_name
    fake_pin.power_domain = power_domain
    fake_pin.recommended = None

    fake_pinout = MagicMock()
    fake_pinout.__iter__ = MagicMock(return_value=iter([fake_pin]))

    fake_base = MagicMock()
    fake_base.recommended_operating = {"VDD": rec_specs}
    fake_base.pinout = fake_pinout

    fake_facts = MagicMock()
    fake_facts.base = fake_base
    return fake_facts


def test_ov_001_returns_empty_when_no_components(tmp_path):
    from lookup_detectors import detect_vcc_outside_recommended
    ctx = _make_ctx([], {}, {}, set(), tmp_path)
    assert detect_vcc_outside_recommended(ctx, rail_voltages={}) == []


def test_ov_001_skips_when_no_facts(tmp_path):
    import lookup_detectors

    ic = {"reference": "U1", "value": "X", "mpn": "UNK", "type": "ic",
           "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "1", "name": "VDD"}]}
    nets = {"V3V3": {"pins": [{"component": "U1", "pin_number": "1",
                                 "pin_name": "VDD", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): ("V3V3", None)}, {"V3V3"}, tmp_path)

    with patch.object(lookup_detectors, "get_facts", return_value=None):
        assert lookup_detectors.detect_vcc_outside_recommended(
            ctx, rail_voltages={"V3V3": 3.3}) == []


def test_ov_001_fires_when_rail_below_recommended_min(tmp_path):
    """Rail voltage below recommended_operating.VDD.min → warning."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    sv_rec = SpecValue(unit="V", evidence=ev, min=2.7, typ=3.3, max=3.6)

    ic = {"reference": "U1", "value": "X", "mpn": "M", "type": "ic",
           "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "1", "name": "VDD"}]}
    nets = {"V1V8": {"pins": [{"component": "U1", "pin_number": "1",
                                 "pin_name": "VDD", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): ("V1V8", None)}, {"V1V8"}, tmp_path)

    with patch.object(lookup_detectors, "get_facts", return_value=_build_facts([sv_rec])):
        findings = lookup_detectors.detect_vcc_outside_recommended(
            ctx, rail_voltages={"V1V8": 1.8})

    ov = [f for f in findings if f.get("rule_id") == "OV-001"]
    assert ov, f"Expected OV-001 finding (1.8V < 2.7V min), got: {findings}"
    assert all(f["severity"] == "warning" for f in ov)
    assert all(f["confidence"] == "datasheet-backed" for f in ov)
    assert all(f["evidence_source"] == "datasheet" for f in ov)
    assert ov[0].get("recommended_min") == 2.7
    assert ov[0].get("rail_voltage") == 1.8


def test_ov_001_fires_when_rail_above_recommended_max(tmp_path):
    """Rail voltage above recommended_operating.VDD.max → warning."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    sv_rec = SpecValue(unit="V", evidence=ev, min=2.7, typ=3.3, max=3.6)

    ic = {"reference": "U1", "value": "X", "mpn": "M", "type": "ic",
           "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "1", "name": "VDD"}]}
    nets = {"V5V": {"pins": [{"component": "U1", "pin_number": "1",
                                "pin_name": "VDD", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): ("V5V", None)}, {"V5V"}, tmp_path)

    with patch.object(lookup_detectors, "get_facts", return_value=_build_facts([sv_rec])):
        findings = lookup_detectors.detect_vcc_outside_recommended(
            ctx, rail_voltages={"V5V": 5.0})

    ov = [f for f in findings if f.get("rule_id") == "OV-001"]
    assert ov, f"Expected OV-001 finding (5.0V > 3.6V max), got: {findings}"
    assert ov[0].get("recommended_max") == 3.6


def test_ov_001_no_finding_when_within_range(tmp_path):
    """Rail voltage between min and max → no finding."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    sv_rec = SpecValue(unit="V", evidence=ev, min=2.7, typ=3.3, max=3.6)

    ic = {"reference": "U1", "value": "X", "mpn": "M", "type": "ic",
           "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "1", "name": "VDD"}]}
    nets = {"V3V3": {"pins": [{"component": "U1", "pin_number": "1",
                                 "pin_name": "VDD", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): ("V3V3", None)}, {"V3V3"}, tmp_path)

    with patch.object(lookup_detectors, "get_facts", return_value=_build_facts([sv_rec])):
        findings = lookup_detectors.detect_vcc_outside_recommended(
            ctx, rail_voltages={"V3V3": 3.3})

    ov = [f for f in findings if f.get("rule_id") == "OV-001"]
    assert ov == [], f"Expected no OV-001 (3.3V within [2.7, 3.6]), got: {ov}"
