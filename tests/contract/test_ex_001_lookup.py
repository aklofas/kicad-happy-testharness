"""Contract tests for EX-001 missing-required-component detector (4c)."""

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


def _build_facts(cin_min=None, cout_min=None, inductor_range=None):
    fake_reg = MagicMock()
    fake_reg.cin_min = cin_min
    fake_reg.cout_min = cout_min
    fake_reg.inductor_range = inductor_range
    fake_facts = MagicMock()
    fake_facts.regulator = fake_reg
    return fake_facts


def test_ex_001_returns_empty_when_no_regulators(tmp_path):
    from lookup_detectors import detect_missing_required_components
    ctx = _make_ctx([], {}, {}, set(), tmp_path)
    assert detect_missing_required_components(ctx, power_regulators=[]) == []


def test_ex_001_skips_when_no_facts(tmp_path):
    import lookup_detectors

    reg = {"ref": "U1", "value": "X", "mpn": "UNK",
            "input_rail": "VIN", "output_rail": "V3V3"}
    ctx = _make_ctx([], {"VIN": {"pins": []}, "V3V3": {"pins": []}},
                    {}, {"VIN", "V3V3"}, tmp_path)

    with patch.object(lookup_detectors, "get_facts", return_value=None):
        assert lookup_detectors.detect_missing_required_components(
            ctx, power_regulators=[reg]) == []


def test_ex_001_fires_when_input_cap_missing(tmp_path):
    """Regulator with cin_min populated but no capacitor on input rail → error."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    sv_cin = SpecValue(unit="F", evidence=ev, min=10e-6)

    reg = {"reference": "U1", "value": "LM2596", "mpn": "LM2596-ADJ",
            "input_rail": "VIN", "output_rail": "V5V"}
    # Output rail has a cap (C2), input rail does NOT.
    cap = {"reference": "C2", "value": "10uF", "type": "capacitor",
            "lib_id": "Device:C", "footprint": "", "properties": {}}
    nets = {
        "VIN": {"pins": []},
        "V5V": {"pins": [
            {"component": "C2", "pin_number": "1", "pin_name": "1", "x": 0, "y": 0},
        ]},
    }
    ctx = _make_ctx([cap], nets, {("C2", "1"): ("V5V", None)},
                    {"VIN", "V5V"}, tmp_path)

    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts(cin_min=[sv_cin])):
        findings = lookup_detectors.detect_missing_required_components(
            ctx, power_regulators=[reg])

    ex = [f for f in findings if f.get("rule_id") == "EX-001"]
    assert ex, f"Expected EX-001 (no input cap), got: {findings}"
    assert all(f["severity"] == "error" for f in ex)
    assert any("input cap" in f.get("missing_kind", "") for f in ex)


def test_ex_001_no_finding_when_cap_present(tmp_path):
    """Regulator with cin_min and a cap on input rail → no finding."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    sv_cin = SpecValue(unit="F", evidence=ev, min=10e-6)

    reg = {"reference": "U1", "value": "LM2596", "mpn": "LM2596-ADJ",
            "input_rail": "VIN", "output_rail": "V5V"}
    cap_in = {"reference": "C1", "value": "10uF", "type": "capacitor",
               "lib_id": "Device:C", "footprint": "", "properties": {}}
    nets = {
        "VIN": {"pins": [{"component": "C1", "pin_number": "1",
                            "pin_name": "1", "x": 0, "y": 0}]},
        "V5V": {"pins": []},
    }
    ctx = _make_ctx([cap_in], nets, {("C1", "1"): ("VIN", None)},
                    {"VIN", "V5V"}, tmp_path)

    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts(cin_min=[sv_cin])):
        findings = lookup_detectors.detect_missing_required_components(
            ctx, power_regulators=[reg])

    ex_input = [f for f in findings if f.get("rule_id") == "EX-001"
                  and f.get("missing_kind") == "input cap"]
    assert ex_input == [], f"Expected no input-cap EX-001, got: {ex_input}"


def test_ex_001_fires_when_inductor_missing(tmp_path):
    """Switching regulator with inductor_range populated but no inductor → error."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    sv_l = SpecValue(unit="H", evidence=ev, min=22e-6, typ=33e-6, max=68e-6)

    reg = {"reference": "U1", "value": "LM2596", "mpn": "LM2596-ADJ",
            "input_rail": "VIN", "output_rail": "V5V",
            "inductor": None}  # no inductor in topology
    ctx = _make_ctx([], {"VIN": {"pins": []}, "V5V": {"pins": []}},
                    {}, {"VIN", "V5V"}, tmp_path)

    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts(inductor_range=[sv_l])):
        findings = lookup_detectors.detect_missing_required_components(
            ctx, power_regulators=[reg])

    ex_l = [f for f in findings if f.get("rule_id") == "EX-001"
              and f.get("missing_kind") == "inductor"]
    assert ex_l, f"Expected EX-001 (missing inductor), got: {findings}"
