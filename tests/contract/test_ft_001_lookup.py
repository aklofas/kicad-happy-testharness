"""Contract tests for FT-001 5V-on-non-5V-tolerant-pin detector (4c)."""

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


def _build_pin(name, number, is_5v_tolerant):
    fake_pin = MagicMock()
    fake_pin.numbers = [number]
    fake_pin.name = name
    fake_pin.is_5v_tolerant = is_5v_tolerant
    return fake_pin


def _build_facts(pins):
    fake_pinout = MagicMock()
    fake_pinout.__iter__ = MagicMock(return_value=iter(pins))
    fake_base = MagicMock()
    fake_base.pinout = fake_pinout
    fake_facts = MagicMock()
    fake_facts.base = fake_base
    return fake_facts


def test_ft_001_returns_empty_when_no_components(tmp_path):
    from lookup_detectors import detect_5v_on_non_tolerant_pin
    ctx = _make_ctx([], {}, {}, set(), tmp_path)
    assert detect_5v_on_non_tolerant_pin(ctx, rail_voltages={}) == []


def test_ft_001_skips_when_no_facts(tmp_path):
    import lookup_detectors

    ic = {"reference": "U1", "value": "X", "mpn": "UNK", "type": "ic",
           "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "1", "name": "PA0"}]}
    nets = {"V5V": {"pins": [{"component": "U1", "pin_number": "1",
                                "pin_name": "PA0", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): ("V5V", None)}, {"V5V"}, tmp_path)

    with patch.object(lookup_detectors, "get_facts", return_value=None):
        assert lookup_detectors.detect_5v_on_non_tolerant_pin(
            ctx, rail_voltages={"V5V": 5.0}) == []


def test_ft_001_fires_when_5v_on_non_tolerant_pin(tmp_path):
    """Pin with is_5v_tolerant=False on a 5V net → error."""
    import lookup_detectors

    ic = {"reference": "U1", "value": "STM32F103C8T6", "mpn": "STM32F103C8T6",
           "type": "ic", "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "1", "name": "PA0"}]}
    nets = {"V5V": {"pins": [{"component": "U1", "pin_number": "1",
                                "pin_name": "PA0", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): ("V5V", None)}, {"V5V"}, tmp_path)

    pin = _build_pin("PA0", "1", is_5v_tolerant=False)
    with patch.object(lookup_detectors, "get_facts", return_value=_build_facts([pin])):
        findings = lookup_detectors.detect_5v_on_non_tolerant_pin(
            ctx, rail_voltages={"V5V": 5.0})

    ft = [f for f in findings if f.get("rule_id") == "FT-001"]
    assert ft, f"Expected FT-001 finding, got: {findings}"
    assert all(f["severity"] == "error" for f in ft)
    assert all(f["confidence"] == "datasheet-backed" for f in ft)
    assert all(f.get("schema_era") == "v1.4" for f in ft)


def test_ft_001_no_finding_when_5v_tolerant(tmp_path):
    """Pin marked 5V-tolerant on a 5V net → no finding."""
    import lookup_detectors

    ic = {"reference": "U1", "value": "X", "mpn": "M", "type": "ic",
           "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "1", "name": "PB6"}]}
    nets = {"V5V": {"pins": [{"component": "U1", "pin_number": "1",
                                "pin_name": "PB6", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): ("V5V", None)}, {"V5V"}, tmp_path)

    pin = _build_pin("PB6", "1", is_5v_tolerant=True)
    with patch.object(lookup_detectors, "get_facts", return_value=_build_facts([pin])):
        findings = lookup_detectors.detect_5v_on_non_tolerant_pin(
            ctx, rail_voltages={"V5V": 5.0})

    assert findings == [], f"Expected no FT-001 (5V-tolerant pin), got: {findings}"


def test_ft_001_no_finding_when_pin_tolerance_unspecified(tmp_path):
    """Pin with is_5v_tolerant=None (unknown) → no finding (skip silently).
    Detectors treat None as 'unknown' per Pin schema."""
    import lookup_detectors

    ic = {"reference": "U1", "value": "X", "mpn": "M", "type": "ic",
           "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "1", "name": "PA0"}]}
    nets = {"V5V": {"pins": [{"component": "U1", "pin_number": "1",
                                "pin_name": "PA0", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): ("V5V", None)}, {"V5V"}, tmp_path)

    pin = _build_pin("PA0", "1", is_5v_tolerant=None)
    with patch.object(lookup_detectors, "get_facts", return_value=_build_facts([pin])):
        findings = lookup_detectors.detect_5v_on_non_tolerant_pin(
            ctx, rail_voltages={"V5V": 5.0})

    assert findings == [], f"Expected no FT-001 (tolerance unknown), got: {findings}"


def test_ft_001_no_finding_when_net_below_5v(tmp_path):
    """Non-tolerant pin on a 3.3V net → no finding."""
    import lookup_detectors

    ic = {"reference": "U1", "value": "X", "mpn": "M", "type": "ic",
           "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "1", "name": "PA0"}]}
    nets = {"V3V3": {"pins": [{"component": "U1", "pin_number": "1",
                                 "pin_name": "PA0", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): ("V3V3", None)}, {"V3V3"}, tmp_path)

    pin = _build_pin("PA0", "1", is_5v_tolerant=False)
    with patch.object(lookup_detectors, "get_facts", return_value=_build_facts([pin])):
        findings = lookup_detectors.detect_5v_on_non_tolerant_pin(
            ctx, rail_voltages={"V3V3": 3.3})

    assert findings == []
