"""Contract tests for AM-001 absolute-max violation detector (4c)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))


def _make_ctx(components, nets, pin_net, known_power_rails, tmp_path):
    from kicad_types import AnalysisContext
    ctx = AnalysisContext(
        components=components,
        nets=nets,
        lib_symbols={},
        pin_net=pin_net,
        known_power_rails=known_power_rails,
        source="test",
    )
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)
    return ctx


def test_am_001_returns_empty_when_no_components(tmp_path):
    """No components → no findings."""
    from lookup_detectors import detect_absolute_max_violations

    ctx = _make_ctx([], {}, {}, set(), tmp_path)
    assert detect_absolute_max_violations(ctx, rail_voltages={}) == []


def test_am_001_skips_when_no_facts(tmp_path):
    """When get_facts returns None (cache miss), no findings emitted."""
    import lookup_detectors

    ic_ref = "U1"
    ic = {
        "reference": ic_ref,
        "value": "UNKNOWN-IC",
        "mpn": "UNKNOWN-MPN",
        "type": "ic",
        "lib_id": "Device:U",
        "footprint": "",
        "properties": {},
        "pins": [{"number": "1", "name": "VDD"}],
    }
    nets = {"VCC_5V": {"pins": [{"component": ic_ref, "pin_number": "1",
                                  "pin_name": "VDD", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {(ic_ref, "1"): ("VCC_5V", None)},
                    {"VCC_5V"}, tmp_path)

    with patch.object(lookup_detectors, "get_facts", return_value=None):
        findings = lookup_detectors.detect_absolute_max_violations(
            ctx, rail_voltages={"VCC_5V": 5.0})

    assert findings == []


def test_am_001_fires_when_rail_exceeds_absolute_max(tmp_path):
    """When facts.base.absolute_max[VDD].max < rail_voltage, emit error."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    # absolute_max VDD = 3.6V; rail at 5V → violation
    ev = Evidence(page=2, confidence="high", method="table")
    sv_amax = SpecValue(unit="V", evidence=ev, max=3.6)

    fake_pin = MagicMock()
    fake_pin.numbers = ["1"]
    fake_pin.name = "VDD"
    fake_pin.power_domain = "VDD"
    fake_pin.absolute_max = None  # per-pin not populated → rail-mapping primary path

    fake_pinout = MagicMock()
    fake_pinout.__iter__ = MagicMock(return_value=iter([fake_pin]))

    fake_base = MagicMock()
    fake_base.absolute_max = {"VDD": [sv_amax]}
    fake_base.pinout = fake_pinout

    fake_facts = MagicMock()
    fake_facts.base = fake_base

    ic_ref = "U1"
    ic = {
        "reference": ic_ref, "value": "FAKE-IC", "mpn": "FAKE-MPN",
        "type": "ic", "lib_id": "Device:U", "footprint": "",
        "properties": {}, "pins": [{"number": "1", "name": "VDD"}],
    }
    nets = {"VCC_5V": {"pins": [{"component": ic_ref, "pin_number": "1",
                                  "pin_name": "VDD", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {(ic_ref, "1"): ("VCC_5V", None)},
                    {"VCC_5V"}, tmp_path)

    with patch.object(lookup_detectors, "get_facts", return_value=fake_facts):
        findings = lookup_detectors.detect_absolute_max_violations(
            ctx, rail_voltages={"VCC_5V": 5.0})

    am_findings = [f for f in findings if f.get("rule_id") == "AM-001"]
    assert am_findings, f"Expected AM-001 finding, got: {findings}"
    assert all(f["severity"] == "error" for f in am_findings)
    assert all(f["confidence"] == "datasheet-backed" for f in am_findings)
    assert all(f["evidence_source"] == "datasheet" for f in am_findings)
    assert all(f.get("schema_era") == "v1.4" for f in am_findings)


def test_am_001_resolves_synonyms_for_rail_keys(tmp_path):
    """Rail key 'VCC' on the IC's absolute_max block matches power_domain 'VDD'
    via the VDD_SYNONYMS table."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    sv_amax = SpecValue(unit="V", evidence=ev, max=3.6)

    fake_pin = MagicMock()
    fake_pin.numbers = ["1"]
    fake_pin.name = "VCC"
    fake_pin.power_domain = "VCC"  # pin says VCC
    fake_pin.absolute_max = None

    fake_pinout = MagicMock()
    fake_pinout.__iter__ = MagicMock(return_value=iter([fake_pin]))

    fake_base = MagicMock()
    # absolute_max keyed by VDD even though pin.power_domain is VCC — synonym resolves.
    fake_base.absolute_max = {"VDD": [sv_amax]}
    fake_base.pinout = fake_pinout

    fake_facts = MagicMock()
    fake_facts.base = fake_base

    ic_ref = "U1"
    ic = {
        "reference": ic_ref, "value": "FAKE-IC", "mpn": "FAKE-MPN",
        "type": "ic", "lib_id": "Device:U", "footprint": "",
        "properties": {}, "pins": [{"number": "1", "name": "VCC"}],
    }
    nets = {"VCC_5V": {"pins": [{"component": ic_ref, "pin_number": "1",
                                  "pin_name": "VCC", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {(ic_ref, "1"): ("VCC_5V", None)},
                    {"VCC_5V"}, tmp_path)

    with patch.object(lookup_detectors, "get_facts", return_value=fake_facts):
        findings = lookup_detectors.detect_absolute_max_violations(
            ctx, rail_voltages={"VCC_5V": 5.0})

    am_findings = [f for f in findings if f.get("rule_id") == "AM-001"]
    assert am_findings, "Expected AM-001 to fire via synonym resolution"


def test_am_001_per_pin_override_tightens_limit(tmp_path):
    """When Pin.absolute_max is populated, it overrides the rail-level limit
    when stricter."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    rail_max = SpecValue(unit="V", evidence=ev, max=5.5)  # rail-level: 5.5V max
    pin_max = SpecValue(unit="V", evidence=ev, max=3.6)   # per-pin: 3.6V max (stricter)

    fake_pin = MagicMock()
    fake_pin.numbers = ["1"]
    fake_pin.name = "PA0"
    fake_pin.power_domain = "VDD"
    fake_pin.absolute_max = [pin_max]  # per-pin populated

    fake_pinout = MagicMock()
    fake_pinout.__iter__ = MagicMock(return_value=iter([fake_pin]))

    fake_base = MagicMock()
    fake_base.absolute_max = {"VDD": [rail_max]}
    fake_base.pinout = fake_pinout

    fake_facts = MagicMock()
    fake_facts.base = fake_base

    ic_ref = "U1"
    ic = {
        "reference": ic_ref, "value": "STM32-LIKE", "mpn": "FAKE-MPN",
        "type": "ic", "lib_id": "Device:U", "footprint": "",
        "properties": {}, "pins": [{"number": "1", "name": "PA0"}],
    }
    # Rail at 5V — between per-pin (3.6) and rail-level (5.5). Should fire on per-pin.
    nets = {"NET_5V": {"pins": [{"component": ic_ref, "pin_number": "1",
                                  "pin_name": "PA0", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {(ic_ref, "1"): ("NET_5V", None)},
                    set(), tmp_path)

    with patch.object(lookup_detectors, "get_facts", return_value=fake_facts):
        findings = lookup_detectors.detect_absolute_max_violations(
            ctx, rail_voltages={"NET_5V": 5.0})

    am_findings = [f for f in findings if f.get("rule_id") == "AM-001"]
    assert am_findings, "Expected AM-001 to fire via per-pin override"
    assert am_findings[0].get("absolute_max_v") == 3.6, (
        f"Expected per-pin 3.6V to win over rail 5.5V, got {am_findings[0].get('absolute_max_v')}"
    )
