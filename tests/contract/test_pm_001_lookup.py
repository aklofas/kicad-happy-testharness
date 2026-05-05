"""Contract tests for PM-001 wrong-signal-type detector (4c)."""

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


def _build_alt_func(name, peripheral):
    af = MagicMock()
    af.name = name
    af.peripheral = peripheral
    return af


def _build_pin(name, number, alt_functions):
    fake_pin = MagicMock()
    fake_pin.numbers = [number]
    fake_pin.name = name
    fake_pin.alt_functions = alt_functions
    return fake_pin


def _build_facts(pins):
    fake_pinout = MagicMock()
    fake_pinout.__iter__ = MagicMock(return_value=iter(pins))
    fake_base = MagicMock()
    fake_base.pinout = fake_pinout
    fake_facts = MagicMock()
    fake_facts.base = fake_base
    return fake_facts


def test_pm_001_returns_empty_when_no_components(tmp_path):
    from lookup_detectors import detect_wrong_signal_type
    ctx = _make_ctx([], {}, {}, set(), tmp_path)
    assert detect_wrong_signal_type(ctx) == []


def test_pm_001_skips_when_alt_functions_empty(tmp_path):
    """Pin with empty alt_functions → can't validate; skip silently."""
    import lookup_detectors

    ic = {"reference": "U1", "value": "X", "mpn": "M", "type": "ic",
           "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "1", "name": "P1"}]}
    nets = {"USART1_TX": {"pins": [{"component": "U1", "pin_number": "1",
                                      "pin_name": "P1", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): ("USART1_TX", None)}, set(), tmp_path)

    pin = _build_pin("P1", "1", alt_functions=[])  # no alt funcs published
    with patch.object(lookup_detectors, "get_facts", return_value=_build_facts([pin])):
        findings = lookup_detectors.detect_wrong_signal_type(ctx)
    assert findings == []


def test_pm_001_fires_when_uart_net_on_non_uart_pin(tmp_path):
    """Net named 'USART1_TX' on pin whose alt_functions don't include
    any USART/UART peripheral → warning."""
    import lookup_detectors

    ic = {"reference": "U1", "value": "STM32", "mpn": "STM32",
           "type": "ic", "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "10", "name": "PA0"}]}
    nets = {"USART1_TX": {"pins": [{"component": "U1", "pin_number": "10",
                                      "pin_name": "PA0", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "10"): ("USART1_TX", None)},
                    set(), tmp_path)

    # Pin only supports SPI / TIM, not USART
    pin = _build_pin("PA0", "10", alt_functions=[
        _build_alt_func("SPI1_MOSI", "SPI1"),
        _build_alt_func("TIM2_CH1", "TIM2"),
    ])
    with patch.object(lookup_detectors, "get_facts", return_value=_build_facts([pin])):
        findings = lookup_detectors.detect_wrong_signal_type(ctx)

    pm = [f for f in findings if f.get("rule_id") == "PM-001"]
    assert pm, f"Expected PM-001 finding, got: {findings}"
    assert all(f["severity"] == "warning" for f in pm)
    assert all(f["confidence"] == "datasheet-backed" for f in pm)


def test_pm_001_no_finding_when_pin_supports_inferred_function(tmp_path):
    """Net 'USART1_TX' on pin with USART1 alt_function → no finding."""
    import lookup_detectors

    ic = {"reference": "U1", "value": "STM32", "mpn": "STM32",
           "type": "ic", "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "10", "name": "PA9"}]}
    nets = {"USART1_TX": {"pins": [{"component": "U1", "pin_number": "10",
                                      "pin_name": "PA9", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "10"): ("USART1_TX", None)},
                    set(), tmp_path)

    pin = _build_pin("PA9", "10", alt_functions=[
        _build_alt_func("USART1_TX", "USART1"),
    ])
    with patch.object(lookup_detectors, "get_facts", return_value=_build_facts([pin])):
        findings = lookup_detectors.detect_wrong_signal_type(ctx)

    pm = [f for f in findings if f.get("rule_id") == "PM-001"]
    assert pm == [], f"Expected no PM-001 (pin supports USART), got: {pm}"


def test_pm_001_skips_unrecognized_net_names(tmp_path):
    """Net 'NET_42' carries no peripheral hint → no finding."""
    import lookup_detectors

    ic = {"reference": "U1", "value": "X", "mpn": "M", "type": "ic",
           "lib_id": "Device:U", "footprint": "", "properties": {},
           "pins": [{"number": "1", "name": "P1"}]}
    nets = {"NET_42": {"pins": [{"component": "U1", "pin_number": "1",
                                   "pin_name": "P1", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): ("NET_42", None)}, set(), tmp_path)

    pin = _build_pin("P1", "1", alt_functions=[
        _build_alt_func("SPI1_MOSI", "SPI1"),
    ])
    with patch.object(lookup_detectors, "get_facts", return_value=_build_facts([pin])):
        findings = lookup_detectors.detect_wrong_signal_type(ctx)
    assert findings == []
