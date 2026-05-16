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


# ===========================================================================
# Cache-variant locks — stale + threshold-boundary + missing-pinout (LOG 13)
# ===========================================================================

def _non_tolerant_pin_ctx(net_name, tmp_path):
    """One IC, one non-tolerant pin on the given net — minimal ctx for FT-001."""
    ic = {"reference": "U1", "value": "X", "mpn": "M", "type": "ic",
          "lib_id": "Device:U", "footprint": "", "properties": {},
          "pins": [{"number": "1", "name": "PA0"}]}
    nets = {net_name: {"pins": [{"component": "U1", "pin_number": "1",
                                   "pin_name": "PA0", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): (net_name, None)},
                    {net_name}, tmp_path)
    return ctx


def test_ft_001_stale_cache_still_fires(tmp_path):
    """Detector does NOT branch on facts.stale — FT-001 fires identically
    whether the cache is fresh or stale. Per-detector half of the A3.3
    staleness ↔ trust-gating orthogonality lock."""
    import lookup_detectors

    pin = _build_pin("PA0", "1", is_5v_tolerant=False)
    facts = _build_facts([pin])
    facts.stale = True

    ctx = _non_tolerant_pin_ctx("V5V", tmp_path)
    with patch.object(lookup_detectors, "get_facts", return_value=facts):
        findings = lookup_detectors.detect_5v_on_non_tolerant_pin(
            ctx, rail_voltages={"V5V": 5.0})

    ft = [f for f in findings if f.get("rule_id") == "FT-001"]
    assert ft, "stale cache must NOT suppress FT-001 — orthogonality lock"


def test_ft_001_threshold_boundary_exactly_at_4_5_fires(tmp_path):
    """Threshold is 4.5V. Code uses strict `<` for the skip path
    (`if sig_v < _FT_001_THRESHOLD_V: continue`), so sig_v=4.5 fires while
    sig_v=4.4 skips. Locks the inclusive-at-threshold contract — flipping
    to `<=` would silently disable detection at exactly 4.5V."""
    import lookup_detectors

    # Case A: 4.4V — below threshold, must NOT fire.
    pin = _build_pin("PA0", "1", is_5v_tolerant=False)
    ctx_below = _non_tolerant_pin_ctx("V4V4", tmp_path)
    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts([pin])):
        findings_below = lookup_detectors.detect_5v_on_non_tolerant_pin(
            ctx_below, rail_voltages={"V4V4": 4.4})
    assert findings_below == [], (
        f"4.4V below 4.5V threshold must NOT fire, got {findings_below}"
    )

    # Case B: 4.5V exactly — at threshold, must fire.
    pin2 = _build_pin("PA0", "1", is_5v_tolerant=False)
    ctx_at = _non_tolerant_pin_ctx("V4V5", tmp_path)
    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts([pin2])):
        findings_at = lookup_detectors.detect_5v_on_non_tolerant_pin(
            ctx_at, rail_voltages={"V4V5": 4.5})
    ft = [f for f in findings_at if f.get("rule_id") == "FT-001"]
    assert ft, "4.5V at exact threshold must fire (< contract, inclusive at threshold)"


def test_ft_001_missing_pinout_skips(tmp_path):
    """base.pinout=None on facts → silent skip (no AttributeError from
    iterating over None). Locks the None-guard against a regression that
    would crash on partial extractions."""
    import lookup_detectors

    fake_base = MagicMock()
    fake_base.pinout = None  # partial extraction
    fake_facts = MagicMock()
    fake_facts.base = fake_base

    ctx = _non_tolerant_pin_ctx("V5V", tmp_path)
    with patch.object(lookup_detectors, "get_facts", return_value=fake_facts):
        # Must not raise; must return [].
        findings = lookup_detectors.detect_5v_on_non_tolerant_pin(
            ctx, rail_voltages={"V5V": 5.0})
    assert findings == []
