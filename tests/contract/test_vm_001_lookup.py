"""Contract tests for VM-001 lookup() upgrade (Phase 4b Task 23)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ctx(source="test"):
    """Minimal AnalysisContext with cache_dir and design_context attributes."""
    from kicad_types import AnalysisContext
    ctx = AnalysisContext(
        components=[],
        nets={},
        lib_symbols={},
        pin_net={},
        source=source,
    )
    setattr(ctx, "cache_dir", None)
    setattr(ctx, "design_context", None)
    return ctx


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

def test_vm_001_helper_smoke_missing_mpn(tmp_path):
    """get_facts returns None for an unknown IC MPN (cache miss)."""
    from lookup_helpers import get_facts
    assert get_facts("UNKNOWN-IC", cache_dir=tmp_path) is None


# ---------------------------------------------------------------------------
# Heuristic preservation — domain crossing emits VM-001
# ---------------------------------------------------------------------------

def test_vm_001_domain_crossing_emits_heuristic(tmp_path):
    """Two ICs at different rail voltages sharing a signal net emits VM-001 at heuristic.

    Uses mocked get_unique_ics and _estimate_rail_voltage_for_ic to control
    fixture without building full net topology. Verifies:
    - confidence='heuristic' preserved
    - evidence_source='topology' preserved
    - schema_era='v1.4' threaded through
    - design_context=None accepted without error
    """
    import validation_detectors

    ctx = _make_ctx()
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)

    # Two ICs: U1 at 3.3V, U2 at 5V
    fake_ics = [
        {'reference': 'U1', 'mpn': 'TLV1234', 'value': 'TLV1234'},
        {'reference': 'U2', 'mpn': 'SN74HC', 'value': 'SN74HC'},
    ]

    def fake_voltage(ctx_arg, ref):
        return {'U1': 3.3, 'U2': 5.0}.get(ref)

    # A shared signal net with pins from both ICs
    ctx.nets = {
        'SIG': {
            'pins': [
                {'component': 'U1', 'pin_number': '1', 'pin_name': 'OUT'},
                {'component': 'U2', 'pin_number': '2', 'pin_name': 'IN'},
            ]
        }
    }
    ctx.comp_lookup = {
        'U1': {'mpn': 'TLV1234', 'value': 'TLV1234', 'type': 'ic'},
        'U2': {'mpn': 'SN74HC', 'value': 'SN74HC', 'type': 'ic'},
    }
    ctx.ref_pins = {
        'U1': {'1': ('SIG', None)},
        'U2': {'2': ('SIG', None)},
    }

    with patch.object(validation_detectors, 'get_unique_ics', return_value=fake_ics), \
         patch.object(validation_detectors, '_estimate_rail_voltage_for_ic', side_effect=fake_voltage), \
         patch.object(validation_detectors, 'get_facts', return_value=None), \
         patch.object(validation_detectors, 'get_regulator_features', return_value=None):
        findings = validation_detectors.validate_voltage_levels(ctx)

    vm = [f for f in findings if f.get('rule_id') == 'VM-001']
    assert vm, "Expected VM-001 finding for 3.3V/5V domain crossing on net SIG"

    f = vm[0]
    assert f['confidence'] == 'heuristic', (
        f"Expected confidence='heuristic', got {f['confidence']}"
    )
    assert f['evidence_source'] == 'topology', (
        f"Expected evidence_source='topology', got {f['evidence_source']}"
    )
    assert f.get('schema_era') == 'v1.4', (
        f"Expected schema_era='v1.4', got {f.get('schema_era')}"
    )


# ---------------------------------------------------------------------------
# Probe wiring — get_facts called per IC during voltage estimation
# ---------------------------------------------------------------------------

def test_vm_001_probe_wiring_get_facts_called(tmp_path):
    """Verify get_facts() is called for each IC whose voltage is estimated.

    The probe is informational — confidence must stay heuristic regardless.
    Uses mock assert_called to verify the wiring is active.
    """
    import validation_detectors

    ctx = _make_ctx()
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)

    fake_ics = [
        {'reference': 'U1', 'mpn': 'LM358', 'value': 'LM358'},
    ]

    def fake_voltage(ctx_arg, ref):
        return 5.0

    ctx.nets = {}
    ctx.comp_lookup = {'U1': {'mpn': 'LM358', 'value': 'LM358', 'type': 'ic'}}

    mock_get_facts = MagicMock(return_value=None)
    with patch.object(validation_detectors, 'get_unique_ics', return_value=fake_ics), \
         patch.object(validation_detectors, '_estimate_rail_voltage_for_ic', side_effect=fake_voltage), \
         patch.object(validation_detectors, 'get_facts', mock_get_facts):
        validation_detectors.validate_voltage_levels(ctx)

    mock_get_facts.assert_called()


# ---------------------------------------------------------------------------
# Probe present but confidence stays heuristic
# ---------------------------------------------------------------------------

def test_vm_001_facts_present_confidence_stays_heuristic(tmp_path):
    """When get_facts() returns a non-None mock, VM-001 confidence stays heuristic.

    This is the 4b wiring boundary: probe is informational only. The detector
    does not branch on facts.base.recommended_operating today — that's v1.5.
    """
    import validation_detectors

    fake_facts = MagicMock()
    fake_base = MagicMock()
    fake_base.recommended_operating = MagicMock()
    fake_facts.base = fake_base

    ctx = _make_ctx()
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)

    fake_ics = [
        {'reference': 'U1', 'mpn': 'STM32F103', 'value': 'STM32F103'},
        {'reference': 'U2', 'mpn': 'SN74HC', 'value': 'SN74HC'},
    ]

    def fake_voltage(ctx_arg, ref):
        return {'U1': 3.3, 'U2': 5.0}.get(ref)

    ctx.nets = {
        'DATA': {
            'pins': [
                {'component': 'U1', 'pin_number': '1', 'pin_name': 'IO'},
                {'component': 'U2', 'pin_number': '2', 'pin_name': 'IN'},
            ]
        }
    }
    ctx.comp_lookup = {
        'U1': {'mpn': 'STM32F103', 'value': 'STM32F103', 'type': 'ic'},
        'U2': {'mpn': 'SN74HC', 'value': 'SN74HC', 'type': 'ic'},
    }
    ctx.ref_pins = {
        'U1': {'1': ('DATA', None)},
        'U2': {'2': ('DATA', None)},
    }

    with patch.object(validation_detectors, 'get_unique_ics', return_value=fake_ics), \
         patch.object(validation_detectors, '_estimate_rail_voltage_for_ic', side_effect=fake_voltage), \
         patch.object(validation_detectors, 'get_facts', return_value=fake_facts), \
         patch.object(validation_detectors, 'get_regulator_features', return_value=None):
        findings = validation_detectors.validate_voltage_levels(ctx)

    vm = [f for f in findings if f.get('rule_id') == 'VM-001']
    assert vm, "Expected VM-001 finding even with facts present"
    assert all(f['confidence'] == 'heuristic' for f in vm), (
        f"Confidence must stay 'heuristic' (probe informational): "
        f"{[f['confidence'] for f in vm]}"
    )
    assert all(f.get('schema_era') == 'v1.4' for f in vm), (
        f"schema_era='v1.4' must be on all VM-001 findings: "
        f"{[f.get('schema_era') for f in vm]}"
    )


# ---------------------------------------------------------------------------
# design_context threading — non-None value accepted
# ---------------------------------------------------------------------------

def test_vm_001_design_context_threading(tmp_path):
    """Non-None design_context threads through make_finding without error."""
    import validation_detectors

    ctx = _make_ctx()
    setattr(ctx, "cache_dir", tmp_path)
    dc = {'board_class': 'consumer', 'risk_profile': 'low'}
    setattr(ctx, "design_context", dc)

    fake_ics = [
        {'reference': 'U1', 'mpn': 'TLV1234', 'value': 'TLV1234'},
        {'reference': 'U2', 'mpn': 'SN74HC', 'value': 'SN74HC'},
    ]

    def fake_voltage(ctx_arg, ref):
        return {'U1': 3.3, 'U2': 5.0}.get(ref)

    ctx.nets = {
        'SIG2': {
            'pins': [
                {'component': 'U1', 'pin_number': '1', 'pin_name': 'OUT'},
                {'component': 'U2', 'pin_number': '2', 'pin_name': 'IN'},
            ]
        }
    }
    ctx.comp_lookup = {
        'U1': {'mpn': 'TLV1234', 'value': 'TLV1234', 'type': 'ic'},
        'U2': {'mpn': 'SN74HC', 'value': 'SN74HC', 'type': 'ic'},
    }
    ctx.ref_pins = {
        'U1': {'1': ('SIG2', None)},
        'U2': {'2': ('SIG2', None)},
    }

    with patch.object(validation_detectors, 'get_unique_ics', return_value=fake_ics), \
         patch.object(validation_detectors, '_estimate_rail_voltage_for_ic', side_effect=fake_voltage), \
         patch.object(validation_detectors, 'get_facts', return_value=None), \
         patch.object(validation_detectors, 'get_regulator_features', return_value=None):
        findings = validation_detectors.validate_voltage_levels(ctx)

    vm = [f for f in findings if f.get('rule_id') == 'VM-001']
    assert vm, "Expected VM-001 finding with non-None design_context accepted by make_finding"
    # design_context is consumed by make_finding for severity tuning (not stored in output).
    # Verify schema_era is present, confirming the threaded emit site was reached.
    assert vm[0].get('schema_era') == 'v1.4', (
        f"Expected schema_era='v1.4', got {vm[0].get('schema_era')!r}"
    )


# ---------------------------------------------------------------------------
# No finding when no ICs have voltage estimates
# ---------------------------------------------------------------------------

def test_vm_001_no_ics_no_findings():
    """No ICs with rail voltage estimates → no VM-001 findings."""
    import validation_detectors

    ctx = _make_ctx()
    ctx.nets = {}

    with patch.object(validation_detectors, 'get_unique_ics', return_value=[]):
        findings = validation_detectors.validate_voltage_levels(ctx)

    vm = [f for f in findings if f.get('rule_id') == 'VM-001']
    assert vm == [], f"Expected no VM-001 findings with no ICs, got {vm}"
