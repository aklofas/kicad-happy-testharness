"""Unit tests for validate/validate_outputs.py — output structural validation."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "validate"))
from validate_outputs import (
    ValidationContext, validate_structural, validate_components,
    validate_nets, validate_signal_analysis, validate_design_analysis,
    validate_new_sections,
)


def _minimal_modern():
    """Build minimal valid modern schematic output."""
    return {
        "file": "test.kicad_sch",
        "components": [{"reference": "R1", "type": "resistor"}],
        "nets": {"net1": {"name": "VCC", "pins": []}},
        "labels": [],
        "power_symbols": [],
        "no_connects": [],
        "bom": [{"references": ["R1"], "quantity": 1}],
        "statistics": {"total_components": 1, "total_nets": 1},
        "signal_analysis": {},
        "design_analysis": {},
        "annotation_issues": {},
        "label_shape_warnings": {},
        "pwr_flag_warnings": {},
        "footprint_filter_warnings": {},
        "sourcing_audit": {},
        "ground_domains": {},
        "bus_topology": {},
        "wire_geometry": {},
        "property_issues": {},
        "hierarchical_labels": {},
        "title_block": {},
    }


# === validate_structural ===

def test_structural_all_keys_present():
    ctx = ValidationContext()
    validate_structural(ctx, "test.kicad_sch", _minimal_modern(), is_modern=True)
    assert "missing_key" not in ctx.anomalies

def test_structural_missing_required_key():
    ctx = ValidationContext()
    data = _minimal_modern()
    del data["bom"]
    validate_structural(ctx, "test.kicad_sch", data, is_modern=True)
    assert "missing_key" in ctx.anomalies
    assert any("bom" in d for _, d in ctx.anomalies["missing_key"])

def test_structural_missing_signal_analysis():
    ctx = ValidationContext()
    data = _minimal_modern()
    del data["signal_analysis"]
    validate_structural(ctx, "test.kicad_sch", data, is_modern=True)
    assert "missing_signal_analysis" in ctx.anomalies

def test_structural_legacy_no_signal_analysis_ok():
    """Legacy files don't require signal_analysis."""
    ctx = ValidationContext()
    data = _minimal_modern()
    del data["signal_analysis"]
    del data["design_analysis"]
    validate_structural(ctx, "test.sch", data, is_modern=False)
    assert "missing_signal_analysis" not in ctx.anomalies

def test_structural_zero_components():
    ctx = ValidationContext()
    data = _minimal_modern()
    data["components"] = []
    data["statistics"]["total_components"] = 0
    validate_structural(ctx, "test.kicad_sch", data, is_modern=True)
    assert ctx.stats["zero_comp"] == 1

def test_structural_missing_new_section():
    ctx = ValidationContext()
    data = _minimal_modern()
    del data["annotation_issues"]
    validate_structural(ctx, "test.kicad_sch", data, is_modern=True)
    assert "missing_new_section" in ctx.anomalies


# === validate_components ===

def test_components_no_anomalies():
    ctx = ValidationContext()
    data = {"components": [
        {"reference": "R1", "type": "resistor"},
        {"reference": "R2", "type": "resistor"},
    ], "bom": [{"references": ["R1", "R2"], "quantity": 2}]}
    validate_components(ctx, "test", data)
    assert "many_duplicate_refs" not in ctx.anomalies

def test_components_many_duplicates():
    ctx = ValidationContext()
    # 10 duplicate refs (>5 threshold)
    comps = [{"reference": f"R{i}", "type": "resistor"} for i in range(20)]
    for i in range(10):
        comps.append({"reference": f"R{i}", "type": "resistor"})
    data = {"components": comps, "bom": []}
    validate_components(ctx, "test", data)
    assert "many_duplicate_refs" in ctx.anomalies

def test_components_high_unknown_type():
    ctx = ValidationContext()
    comps = [{"reference": f"U{i}", "type": "unknown"} for i in range(10)]
    data = {"components": comps, "bom": []}
    validate_components(ctx, "test", data)
    assert "high_unknown_type" in ctx.anomalies

def test_components_bom_mismatch():
    ctx = ValidationContext()
    data = {
        "components": [{"reference": f"R{i}", "type": "resistor"} for i in range(20)],
        "bom": [{"references": ["R1"], "quantity": 10}],  # Only 10 vs 20 comps
    }
    validate_components(ctx, "test", data)
    assert "bom_mismatch" in ctx.anomalies


# === validate_nets ===

def test_nets_normal():
    ctx = ValidationContext()
    data = {"nets": {"n1": {"name": "VCC", "pins": []}, "n2": {"name": "GND", "pins": []}}}
    validate_nets(ctx, "test", data, total_comps=5)
    assert "high_comp_net_ratio" not in ctx.anomalies

def test_nets_high_ratio():
    ctx = ValidationContext()
    data = {"nets": {"n1": {"name": "VCC", "pins": []}}}
    validate_nets(ctx, "test", data, total_comps=50)
    assert "high_comp_net_ratio" in ctx.anomalies

def test_nets_comps_no_nets():
    ctx = ValidationContext()
    data = {"nets": {}}
    validate_nets(ctx, "test", data, total_comps=10)
    assert "comps_but_no_nets" in ctx.anomalies

def test_nets_huge_net():
    ctx = ValidationContext()
    data = {"nets": [{"name": "GND", "pin_count": 600}]}
    validate_nets(ctx, "test", data, total_comps=100)
    assert "huge_net" in ctx.anomalies

def test_nets_list_format():
    """Nets can be a list instead of dict."""
    ctx = ValidationContext()
    data = {"nets": [{"name": "VCC", "pins": []}, {"name": "GND", "pins": []}]}
    validate_nets(ctx, "test", data, total_comps=5)
    assert "high_comp_net_ratio" not in ctx.anomalies


# === validate_signal_analysis ===

def test_signal_normal():
    ctx = ValidationContext()
    data = {"signal_analysis": {"voltage_dividers": [{"ratio": 0.5}] * 10}}
    validate_signal_analysis(ctx, "test", data)
    assert "signal_explosion" not in ctx.anomalies

def test_signal_explosion():
    ctx = ValidationContext()
    data = {"signal_analysis": {"voltage_dividers": [{"ratio": 0.5}] * 250}}
    validate_signal_analysis(ctx, "test", data)
    assert "signal_explosion" in ctx.anomalies

def test_signal_missing():
    ctx = ValidationContext()
    validate_signal_analysis(ctx, "test", {})
    assert "signal_explosion" not in ctx.anomalies

def test_signal_decoupling_explosion():
    ctx = ValidationContext()
    data = {"signal_analysis": {"decoupling_analysis": {"ics_analyzed": 300}}}
    validate_signal_analysis(ctx, "test", data)
    assert "decoupling_explosion" in ctx.anomalies


# === validate_design_analysis ===

def test_design_normal():
    ctx = ValidationContext()
    data = {"design_analysis": {"erc_warnings": [{"msg": "warn"}] * 5}}
    validate_design_analysis(ctx, "test", data)
    assert "many_erc_warnings" not in ctx.anomalies

def test_design_many_erc():
    ctx = ValidationContext()
    data = {"design_analysis": {"erc_warnings": [{"msg": "w"}] * 150}}
    validate_design_analysis(ctx, "test", data)
    assert "many_erc_warnings" in ctx.anomalies

def test_design_missing():
    ctx = ValidationContext()
    validate_design_analysis(ctx, "test", {})
    assert "many_erc_warnings" not in ctx.anomalies


# === validate_new_sections ===

def test_new_sections_normal():
    ctx = ValidationContext()
    data = _minimal_modern()
    validate_new_sections(ctx, "test", data)
    assert not ctx.anomalies

def test_new_sections_many_annotation_dupes():
    ctx = ValidationContext()
    data = {"annotation_issues": {"duplicate_references": [f"R{i}" for i in range(30)]}}
    validate_new_sections(ctx, "test", data)
    assert "many_annotation_dupes" in ctx.anomalies

def test_new_sections_many_diagonal_wires():
    ctx = ValidationContext()
    data = {"wire_geometry": {"diagonal_wires": 60, "total_wires": 100}}
    validate_new_sections(ctx, "test", data)
    assert "many_diagonal_wires" in ctx.anomalies

def test_new_sections_many_value_eq_ref():
    ctx = ValidationContext()
    data = {"property_issues": {"value_equals_reference": [f"R{i}" for i in range(25)]}}
    validate_new_sections(ctx, "test", data)
    assert "many_value_eq_ref" in ctx.anomalies

def test_new_sections_many_ground_domains():
    ctx = ValidationContext()
    data = {"ground_domains": {"domains": [{"name": f"GND{i}"} for i in range(12)]}}
    validate_new_sections(ctx, "test", data)
    assert "many_ground_domains" in ctx.anomalies


# === Runner ===

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
