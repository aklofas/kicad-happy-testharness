"""Unit tests for the product 3.0.x Wave 8c + 8b budget predicates (regression/budgets/v30x_wave8b.py)."""
import copy
from pathlib import Path

import pytest

from regression.budgets import v30x_wave8b as w8
from regression.budgets.v232_backport import (
    expected_audience_summary,
    expected_summary,
    expected_trust_summary,
)
from regression.field_compare import load_budget

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parent.parent


def _finding(rule_id, **kw):
    f = {"detector": "d", "rule_id": rule_id, "category": "c", "summary": "s", "description": "",
         "components": [], "nets": [], "pins": [], "severity": "warning", "confidence": "heuristic",
         "evidence_source": "topology", "recommendation": "", "report_context": {},
         "finding_id": f"x:{rule_id}:1"}
    f.update(kw)
    return f


def _doc(analyzer, findings=(), **extra):
    findings = list(findings)
    doc = {"analyzer_type": analyzer}
    doc.update(extra)
    doc["findings"] = findings
    doc["summary"] = expected_summary(findings, {})
    doc["trust_summary"] = expected_trust_summary(
        findings, {"by_confidence": {"deterministic": 0, "heuristic": 0},
                   "by_evidence_source": {"topology": 0}})
    doc["audience_summary"] = expected_audience_summary(findings)
    return doc


def _net(name, pins, sheet=0):
    return {"name": name, "pins": [{"component": c, "pin_number": p} for c, p in pins],
            "labels": [{"name": name, "type": "label", "_sheet": sheet}]}


def _sch(nets, components, findings=(), labels=None):
    return _doc("schematic", findings, nets={n["name"]: n for n in nets}, components=components,
                labels=labels if labels is not None else [{"name": "A", "_sheet": 0}, {"name": "B", "_sheet": 1}])


def _comp(ref, value="10k", **kw):
    c = {"reference": ref, "value": value, "pin_nets": {}}
    c.update(kw)
    return c


def test_budget_files_load_and_name_the_module():
    for name in ("v30x-wave8b", "v30x-wave8b-full-chain"):
        b = load_budget(ROOT / "regression" / "budgets" / f"{name}.json")
        assert b["baseline_sha"] == "647bc85" and b["candidate_sha"] == "0efc012"
        assert all(c["predicate"].startswith("v30x_wave8b:") for c in b["classes"])


def test_net_rename_with_same_connectivity_is_kh800():
    a = _sch([_net("/abc/SDA", [("U1", "1"), ("R1", "2")])],
             [_comp("U1", pin_nets={"1": "/abc/SDA"}), _comp("R1")],
             [_finding("LB-001", nets=["/abc/SDA"], description="Net '/abc/SDA' floats")])
    b = _sch([_net("SDA", [("U1", "1"), ("R1", "2")])],
             [_comp("U1", pin_nets={"1": "SDA"}), _comp("R1")],
             [_finding("LB-001", nets=["SDA"], description="Net 'SDA' floats")])
    b["nets"]["SDA"]["labels"] = a["nets"]["/abc/SDA"]["labels"]
    r = w8.classify_unit("schematic", a, b)
    assert r["label"] == "KH800" and r["stats"]["renamed"] == 1
    assert not any(k.startswith("left ") for k in r["stats"])


def test_changed_connectivity_is_a_residual_even_with_a_rename():
    a = _sch([_net("N1", [("U1", "1"), ("R1", "2")])], [_comp("U1"), _comp("R1")])
    b = _sch([_net("N2", [("U1", "1")])], [_comp("U1"), _comp("R1")])
    r = w8.classify_unit("schematic", a, b)
    assert r["label"] is None and any("connectivity" in x for x in r["reasons"])


def test_sheet_reorder_moves_sheet_indices_and_order_only():
    nets = [_net("GND", [("C1", "2"), ("U1", "3")])]
    a = _sch(nets, [_comp("U1"), _comp("C1")], labels=[{"name": "A", "_sheet": 0}, {"name": "B", "_sheet": 1}])
    b = _sch(copy.deepcopy(nets), [_comp("C1"), _comp("U1")],
             [_finding("PR-DET", components=["C1"])],
             labels=[{"name": "B", "_sheet": 0}, {"name": "A", "_sheet": 1}])
    b["nets"]["GND"]["pins"].reverse()
    r = w8.classify_unit("schematic", a, b)
    assert r["label"] == "KH800" and r["stats"]["reordered"] == 1


def test_ferrite_slash_value_losing_parsed_value_and_its_lc_filter_is_kh850():
    nets = [_net("VIN", [("FB1", "1"), ("C1", "1")])]
    a = _sch(nets, [_comp("FB1", "600R/200mA", parsed_value=600.0), _comp("C1", "10u", parsed_value=1e-5)],
             [_finding("LC-DET", components=["FB1", "C1"])])
    b = _sch(copy.deepcopy(nets), [_comp("FB1", "600R/200mA"), _comp("C1", "10u", parsed_value=1e-5)])
    r = w8.classify_unit("schematic", a, b)
    assert r["label"] == "KH850" and r["stats"]["parsed_value dropped"] == 1


def test_parsed_value_change_on_a_plain_value_is_a_residual():
    nets = [_net("VIN", [("R1", "1")])]
    a = _sch(nets, [_comp("R1", "10k", parsed_value=1e4)])
    b = _sch(copy.deepcopy(nets), [_comp("R1", "10k", parsed_value=1e3)])
    assert w8.classify_unit("schematic", a, b)["label"] is None


def test_finding_movement_without_rename_reorder_or_lc_det_is_a_residual():
    nets = [_net("VIN", [("R1", "1")])]
    a = _sch(nets, [_comp("R1")])
    b = _sch(copy.deepcopy(nets), [_comp("R1")], [_finding("VM-001")])
    assert w8.classify_unit("schematic", a, b)["label"] is None


def test_pcb_standard_classes():
    note = {"source": "pcb.presentation.assemble_result", "exception": "ValueError",
            "message": "pads are not checked for a copper path between them"}
    a = _doc("pcb", [_finding("OR-001")], setup={"stackup": []}, diagnostics=[note])
    b = _doc("pcb", setup={"stackup": [], "board_thickness_mm": 1.6}, diagnostics=[])
    assert w8.classify_unit("pcb", a, b)["label"] == "KH825+KH851+KH863"


def test_pcb_other_diagnostic_or_finding_is_a_residual():
    a = _doc("pcb", diagnostics=[{"message": "something else"}])
    b = _doc("pcb", diagnostics=[])
    assert w8.classify_unit("pcb", a, b)["label"] is None
    a = _doc("pcb")
    b = _doc("pcb", [_finding("OR-001")])
    assert w8.classify_unit("pcb", a, b)["label"] is None


def _seg(layer, z):
    return {"layer": layer, "width": 0.2, "impedance_ohm": z}


def test_pcb_full_outer_impedance_rise_and_reference_plane_changes():
    a = _doc("pcb", net_lengths=[{"net": "CLK", "trace_segments": [_seg("F.Cu", 100.0), _seg("In1.Cu", 50.0)]}],
             return_path_continuity=[])
    b = _doc("pcb", net_lengths=[{"net": "CLK", "trace_segments": [_seg("F.Cu", 121.9), _seg("In1.Cu", 50.0)]}],
             return_path_continuity=[], reference_plane_changes=[])
    r = w8.classify_unit("pcb", a, b)
    assert r["label"] == "KH795+KH820" and r["stats"]["impedance outer up"] == 1


def test_pcb_inner_impedance_change_or_fall_is_a_residual():
    a = _doc("pcb", net_lengths=[{"net": "CLK", "trace_segments": [_seg("In1.Cu", 50.0)]}])
    b = _doc("pcb", net_lengths=[{"net": "CLK", "trace_segments": [_seg("In1.Cu", 55.0)]}])
    assert w8.classify_unit("pcb", a, b)["label"] is None
    a = _doc("pcb", net_lengths=[{"net": "CLK", "trace_segments": [_seg("F.Cu", 100.0)]}])
    b = _doc("pcb", net_lengths=[{"net": "CLK", "trace_segments": [_seg("F.Cu", 90.0)]}])
    assert w8.classify_unit("pcb", a, b)["label"] is None


def test_emc_split_finding_needs_upstream_reference_plane_changes(monkeypatch):
    split = _finding("GP-001", summary=w8.SPLIT_TITLE, severity="error")
    a = _doc("emc")
    b = _doc("emc", [split])
    up = (_doc("pcb"), _doc("pcb", reference_plane_changes=[{"net": "CLK", "net_a": "+3V3", "net_b": "+5V"}]))
    monkeypatch.setattr(w8, "_upstream_doc_pair", lambda x, y, kind: up if kind == "pcb" else None)
    assert w8.classify_unit("emc", a, b)["label"] == "KH795"
    up = (_doc("pcb"), _doc("pcb", reference_plane_changes=[]))
    assert w8.classify_unit("emc", a, b)["label"] is None


def test_downstream_needs_an_explained_upstream_schematic(monkeypatch):
    a = _doc("cross_analysis", [_finding("EG-001", description="nets X")])
    b = _doc("cross_analysis", [_finding("EG-001", description="nets Y")])
    monkeypatch.setattr(w8, "_upstream_doc_pair", lambda x, y, kind: None)
    assert w8.classify_unit("cross_analysis", a, b)["label"] is None
    sa = _sch([_net("X", [("U1", "1")])], [_comp("U1")])
    sb = _sch([_net("Y", [("U1", "1")])], [_comp("U1")])
    sb["nets"]["Y"]["labels"] = sa["nets"]["X"]["labels"]
    monkeypatch.setattr(w8, "_upstream_doc_pair", lambda x, y, kind: (sa, sb) if kind == "schematic" else None)
    assert w8.classify_unit("cross_analysis", a, b)["label"] == "D"
