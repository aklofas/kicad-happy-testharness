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


# ===========================================================================
# Cache-variant locks — stale + low-conf + boundary + missing-pinout (LOG 13)
# ===========================================================================

def _build_am_facts_with_amax(sv_amax, stale=False, pinout_override=None):
    """Build a mock DatasheetFacts with one VDD pin and absolute_max[VDD]
    populated. Used by the LOG 13 cache-variant tests."""
    fake_pin = MagicMock()
    fake_pin.numbers = ["1"]
    fake_pin.name = "VDD"
    fake_pin.power_domain = "VDD"
    fake_pin.absolute_max = None

    if pinout_override is None:
        fake_pinout = MagicMock()
        fake_pinout.__iter__ = MagicMock(return_value=iter([fake_pin]))
    else:
        fake_pinout = pinout_override

    fake_base = MagicMock()
    fake_base.absolute_max = {"VDD": [sv_amax]}
    fake_base.pinout = fake_pinout
    fake_facts = MagicMock()
    fake_facts.base = fake_base
    fake_facts.stale = stale
    return fake_facts


def _vdd_ic_and_ctx(net_name, tmp_path):
    """Single VDD-pin IC on the given net — minimal ctx for AM-001."""
    ic = {"reference": "U1", "value": "X", "mpn": "M", "type": "ic",
          "lib_id": "Device:U", "footprint": "", "properties": {},
          "pins": [{"number": "1", "name": "VDD"}]}
    nets = {net_name: {"pins": [{"component": "U1", "pin_number": "1",
                                   "pin_name": "VDD", "x": 0, "y": 0}]}}
    ctx = _make_ctx([ic], nets, {("U1", "1"): (net_name, None)},
                    {net_name}, tmp_path)
    return ctx


def test_am_001_stale_cache_still_fires(tmp_path):
    """Detector does NOT branch on facts.stale — same finding emitted as for
    a fresh cache. Per-detector half of the A3.3 staleness ↔ trust-gating
    orthogonality lock (lookup-layer half is in
    tests/datasheets/test_a3_lookup_path.py). A regression that introduces
    `if facts.stale: continue` in this detector would trip this test."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    sv_amax = SpecValue(unit="V", evidence=ev, max=3.6)
    fake_facts = _build_am_facts_with_amax(sv_amax, stale=True)

    ctx = _vdd_ic_and_ctx("VCC_5V", tmp_path)
    with patch.object(lookup_detectors, "get_facts", return_value=fake_facts):
        findings = lookup_detectors.detect_absolute_max_violations(
            ctx, rail_voltages={"VCC_5V": 5.0})

    am = [f for f in findings if f.get("rule_id") == "AM-001"]
    assert am, "stale cache must NOT suppress AM-001 — orthogonality lock"


def test_am_001_low_confidence_absolute_max_no_finding(tmp_path):
    """Low-confidence absolute_max SpecValue → best(min_confidence='medium')
    returns None → silent skip. Locks the implicit per-rule gate (currently
    only globally tested in tests/datasheets/test_a3_trust_gates_deny.py)."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev_low = Evidence(page=2, confidence="low", method="prose")
    sv_amax = SpecValue(unit="V", evidence=ev_low, max=3.6)
    fake_facts = _build_am_facts_with_amax(sv_amax)

    ctx = _vdd_ic_and_ctx("VCC_5V", tmp_path)
    with patch.object(lookup_detectors, "get_facts", return_value=fake_facts):
        findings = lookup_detectors.detect_absolute_max_violations(
            ctx, rail_voltages={"VCC_5V": 5.0})

    assert findings == [], (
        f"low-conf absolute_max must fail medium gate → silent skip, got {findings}"
    )


def test_am_001_no_finding_at_exactly_absolute_max_boundary(tmp_path):
    """rail_v == absolute_max_v is OK — code uses `<=` (inclusive). Locks
    the boundary against a regression to strict `<` that would silently
    flip the rule's fire shape on every part operating right at the limit."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    sv_amax = SpecValue(unit="V", evidence=ev, max=3.6)
    fake_facts = _build_am_facts_with_amax(sv_amax)

    ctx = _vdd_ic_and_ctx("V3V6", tmp_path)
    with patch.object(lookup_detectors, "get_facts", return_value=fake_facts):
        findings = lookup_detectors.detect_absolute_max_violations(
            ctx, rail_voltages={"V3V6": 3.6})

    assert findings == [], (
        f"rail at exact absolute_max boundary must NOT fire (≤ contract), got {findings}"
    )


def test_am_001_missing_pinout_skips(tmp_path):
    """base.pinout=None on facts → silent skip (no AttributeError from
    iterating over None). Locks the None-guard against a regression that
    would crash the analyzer on partial extractions."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    sv_amax = SpecValue(unit="V", evidence=ev, max=3.6)
    # pinout=None forces the `if pinout is None: continue` guard path.
    fake_base = MagicMock()
    fake_base.absolute_max = {"VDD": [sv_amax]}
    fake_base.pinout = None
    fake_facts = MagicMock()
    fake_facts.base = fake_base

    ctx = _vdd_ic_and_ctx("VCC_5V", tmp_path)
    with patch.object(lookup_detectors, "get_facts", return_value=fake_facts):
        # Must not raise; must return [].
        findings = lookup_detectors.detect_absolute_max_violations(
            ctx, rail_voltages={"VCC_5V": 5.0})
    assert findings == []
