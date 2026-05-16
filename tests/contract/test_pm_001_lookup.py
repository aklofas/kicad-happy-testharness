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


# ===========================================================================
# Cache-variant locks — stale + match-via-name + case-insensitivity (LOG 13)
# ===========================================================================

def _uart_ic_and_ctx(net_name, tmp_path):
    """One IC, one pin, one UART-named net — minimal ctx for PM-001."""
    ic = {"reference": "U1", "value": "STM32", "mpn": "STM32", "type": "ic",
          "lib_id": "Device:U", "footprint": "", "properties": {},
          "pins": [{"number": "10", "name": "PA0"}]}
    nets = {net_name: {"pins": [{"component": "U1", "pin_number": "10",
                                   "pin_name": "PA0", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "10"): (net_name, None)},
                    set(), tmp_path)
    return ctx


def test_pm_001_stale_cache_still_fires(tmp_path):
    """Detector does NOT branch on facts.stale — PM-001 fires identically
    whether the cache is fresh or stale. Per-detector half of the A3.3
    staleness ↔ trust-gating orthogonality lock."""
    import lookup_detectors

    pin = _build_pin("PA0", "10", alt_functions=[
        _build_alt_func("SPI1_MOSI", "SPI1"),
    ])
    facts = _build_facts([pin])
    facts.stale = True

    ctx = _uart_ic_and_ctx("USART1_TX", tmp_path)
    with patch.object(lookup_detectors, "get_facts", return_value=facts):
        findings = lookup_detectors.detect_wrong_signal_type(ctx)

    pm = [f for f in findings if f.get("rule_id") == "PM-001"]
    assert pm, "stale cache must NOT suppress PM-001 — orthogonality lock"


def test_pm_001_match_via_alt_function_name_when_peripheral_empty(tmp_path):
    """Code checks BOTH af.peripheral AND af.name for the hint substring
    (per `hint_upper in af_peripheral or hint_upper in af_name`). A pin
    with empty peripheral but matching name still counts as supporting
    the inferred peripheral. Locks the OR-on-both-fields contract — a
    regression to peripheral-only would silently mis-flag pins whose only
    peripheral indicator is in the name string."""
    import lookup_detectors

    ctx = _uart_ic_and_ctx("USART1_TX", tmp_path)
    # peripheral is empty; only name carries the USART hint.
    pin = _build_pin("PA9", "10", alt_functions=[
        _build_alt_func(name="USART1_TX", peripheral=""),
    ])
    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts([pin])):
        findings = lookup_detectors.detect_wrong_signal_type(ctx)

    pm = [f for f in findings if f.get("rule_id") == "PM-001"]
    assert pm == [], (
        f"empty peripheral + matching name must count as support, got {pm}"
    )


def test_pm_001_case_insensitive_lowercase_net_matches_uart_hint(tmp_path):
    """The _PERIPHERAL_HINTS regexes use re.IGNORECASE, so a lowercase net
    name like 'uart1_tx' must still trigger the USART/UART hint. Locks
    the case-insensitivity flag — a regression that dropped re.IGNORECASE
    would silently disable detection on KiCad designs that use lowercase
    net naming conventions."""
    import lookup_detectors

    ctx = _uart_ic_and_ctx("uart1_tx", tmp_path)  # lowercase
    # Pin only supports SPI — should produce a PM-001 finding since net
    # IS recognized as UART by the case-insensitive regex.
    pin = _build_pin("PA0", "10", alt_functions=[
        _build_alt_func("SPI1_MOSI", "SPI1"),
    ])
    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts([pin])):
        findings = lookup_detectors.detect_wrong_signal_type(ctx)

    pm = [f for f in findings if f.get("rule_id") == "PM-001"]
    assert pm, (
        "lowercase 'uart1_tx' must still match USART/UART hint via IGNORECASE — "
        "got no finding, suggesting case-insensitivity broke"
    )
