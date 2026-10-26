"""Unit tests for the product 3.0.x Wave 3 budget predicates (regression/budgets/v30x_wave3.py)."""
import copy
import types

import pytest

from regression.budgets import v30x_wave3 as w3
from regression.budgets.v232_backport import (
    expected_audience_summary,
    expected_summary,
    expected_trust_summary,
)
from regression.field_compare import Delta

pytestmark = pytest.mark.unit


def _d(analyzer, path="/findings/0", op="changed"):
    return Delta(unit="u", analyzer=analyzer, path=path, op=op, before=None, after=None)


def _finding(rule_id, **kw):
    f = {"detector": "d", "rule_id": rule_id, "category": "c", "summary": "s", "description": "",
         "components": [], "nets": [], "pins": [], "severity": "warning", "confidence": "heuristic",
         "evidence_source": "topology", "recommendation": "", "report_context": {},
         "finding_id": f"x:{rule_id}:1"}
    f.update(kw)
    return f


def _doc(findings, **extra):
    """An envelope whose derived blocks follow from its findings."""
    doc = dict(extra)
    doc["findings"] = findings
    doc["summary"] = expected_summary(findings, {})
    doc["trust_summary"] = expected_trust_summary(
        findings, {"by_confidence": {"deterministic": 0, "heuristic": 0},
                   "by_evidence_source": {"topology": 0}})
    doc["audience_summary"] = expected_audience_summary(findings)
    return doc


@pytest.fixture(autouse=True)
def _same_netnames(monkeypatch):
    """Both sides classify names alike unless a test says otherwise (no product clone needed)."""
    same = types.SimpleNamespace(is_power_net_name=lambda n, rails=None: str(n).startswith("+"))
    monkeypatch.setattr(w3, "_NETNAMES", {"a": same, "b": same})


def _legacy(**extra):
    return {"legacy_analysis_quality": {"is_legacy_schematic": True}, **extra}


def test_legacy_unit_moves_anywhere_but_the_header():
    a = _doc([_finding("PU-001")], **_legacy(nets={"N1": {"pins": []}}, kicad_version="5 (legacy)"))
    b = _doc([_finding("LB-001")], **_legacy(nets={"N2": {"pins": []}}, kicad_version="5 (legacy)"))
    assert w3.classify_unit("schematic", a, b)["label"] == "L"
    assert w3.legacy(_d("schematic"), a, b)
    assert not w3.modern_schematic(_d("schematic"), a, b)
    b_hdr = copy.deepcopy(b)
    b_hdr["kicad_version"] = "6"
    assert w3.classify_unit("schematic", a, b_hdr)["label"] is None


def test_lb001_shrinking_is_m3_but_growing_or_other_rules_are_not():
    lb = _finding("LB-001", aliases=["A", "B"])
    a = _doc([lb, dict(lb, finding_id="x:LB-001:2", aliases=["C", "D"])])
    b = _doc([lb])
    assert w3.classify_unit("schematic", a, b)["label"] == "M3"
    assert w3.classify_unit("schematic", b, a)["label"] is None
    c = _doc([lb, _finding("RS-001")])
    assert w3.classify_unit("schematic", a, c)["label"] is None


def test_negative_rail_sign_flip_is_m7_and_findings_must_name_the_rail():
    a = _doc([], rail_voltages={"-5V": 5.0})
    b = _doc([], rail_voltages={"-5V": -5.0})
    assert w3.classify_unit("schematic", a, b)["label"] == "M7"
    named = _doc([_finding("VD-004", rail="/Analog/-5V")], rail_voltages={"-5V": -5.0})
    assert w3.classify_unit("schematic", a, named)["label"] == "M7"
    other = _doc([_finding("VD-004", rail="/Analog/+3V3")], rail_voltages={"-5V": -5.0})
    assert w3.classify_unit("schematic", a, other)["label"] is None


def test_duplicate_pin_slots_open_connectivity_movement():
    p = {"component": "U1", "pin_number": "3"}
    a = _doc([_finding("DO-DET")], nets={"A": {"pins": [p]}, "B": {"pins": [p]}})
    b = _doc([_finding("NT-001")], nets={"A": {"pins": [p]}, "B": {"pins": []}})
    assert w3.classify_unit("schematic", a, b)["label"] == "M2"


def test_point_count_only_is_m8pc_and_other_net_fields_are_not():
    a = _doc([], nets={"A": {"pins": [], "point_count": 6}})
    b = _doc([], nets={"A": {"pins": [], "point_count": 5}})
    assert w3.classify_unit("schematic", a, b)["label"] == "M8pc"
    c = _doc([], nets={"A": {"pins": [], "point_count": 5, "labels": [{"name": "X"}]}})
    assert w3.classify_unit("schematic", a, c)["label"] is None


def test_power_name_reclassified_by_the_products_is_m6(monkeypatch):
    old = types.SimpleNamespace(is_power_net_name=lambda n, rails=None: True)
    new = types.SimpleNamespace(is_power_net_name=lambda n, rails=None: n != "VCC_EN")
    monkeypatch.setattr(w3, "_NETNAMES", {"a": old, "b": new})
    a = _doc([_finding("RS-001", nets=["VCC_EN"])], nets={"VCC_EN": {"pins": []}},
             statistics={"power_rails": [{"name": "VCC_EN", "voltage": None}]})
    b = _doc([], nets={"VCC_EN": {"pins": []}}, statistics={"power_rails": []})
    assert w3.classify_unit("schematic", a, b)["label"] == "M6"


def test_flagged_nets_are_the_context_rail_set():
    doc = {"nets": {"HVIL_N": {"pins": [{"component": "#FLG01", "pin_number": "1"}]},
                    "/HVIL/HVIL_N": {"pins": [{"component": "R1", "pin_number": "1"}]}}}
    assert w3._flagged_nets(doc) == {"HVIL_N"}


def test_derived_blocks_must_follow_findings():
    lb = _finding("LB-001")
    a, b = _doc([lb, dict(lb, finding_id="x:LB-001:2", summary="t")]), _doc([lb])
    assert w3.classify_unit("schematic", a, b)["label"] == "M3"
    bad = copy.deepcopy(b)
    bad["summary"]["total_findings"] = 7
    assert w3.classify_unit("schematic", a, bad)["label"] is None


def test_silkscreen_only_is_p3_and_takes_no_findings():
    a = _doc([], silkscreen={"refs_visible_on_silk": 10})
    b = _doc([], silkscreen={"refs_visible_on_silk": 8})
    assert w3.classify_unit("pcb", a, b)["label"] == "P3"
    assert w3.pcb(_d("pcb"), a, b)
    c = _doc([_finding("PM-001")], silkscreen={"refs_visible_on_silk": 8})
    assert w3.classify_unit("pcb", a, c)["label"] is None


def test_courtyard_change_on_a_repeated_reference_is_p2():
    fp = {"reference": "REF**", "layer": "F.Cu", "courtyard": {"min_x": 1.0}}
    a = _doc([], footprints=[dict(fp), dict(fp)])
    b = _doc([_finding("PM-002")], footprints=[dict(fp), dict(fp, courtyard={"min_x": 0.5}, courtyard_poly=[[0, 0]])])
    assert w3.classify_unit("pcb", a, b)["label"] == "P2"
    c = _doc([], footprints=[dict(fp), dict(fp, value="10k")])
    assert w3.classify_unit("pcb", a, c)["label"] is None


def test_outline_change_allows_edge_clearance_but_not_overlap():
    a = _doc([], board_outline={"edges": [1]})
    b = _doc([_finding("PM-002")], board_outline={"edges": [2]})
    assert w3.classify_unit("pcb", a, b)["label"] == "P1"
    c = _doc([_finding("PM-001")], board_outline={"edges": [2]})
    assert w3.classify_unit("pcb", a, c)["label"] is None


def test_chained_unit_with_identical_upstream_is_residual():
    a = {"findings": [_finding("EE-001")], "inputs": {}}
    b = {"findings": [], "inputs": {}}
    r = w3.classify_unit("emc", a, b)
    assert r["label"] is None and "identical upstream" in r["reasons"][0]


def test_bus_trigger_needs_bus_topology_movement_or_a_global_bus_label():
    p = {"component": "U1", "pin_number": "3"}
    bt = {"bus_wire_count": 4, "bus_entry_count": 2, "unresolved": []}
    a = _doc([], nets={"A": {"pins": [p]}}, bus_topology=bt)
    b = _doc([], nets={"A": {"pins": []}}, bus_topology=bt)
    assert w3.classify_unit("schematic", a, b)["label"] is None
    gl = [{"name": "D[0..7]", "type": "global_label"}]
    assert w3.classify_unit("schematic", dict(a, labels=gl), dict(b, labels=gl))["label"] == "M4"
    b_tap = dict(b, bus_topology=dict(bt, unresolved=[{"reason": "unlabeled_entry_tap"}]))
    assert w3.classify_unit("schematic", a, b_tap)["label"] == "M4"


def test_bv001_movement_alone_is_p4():
    a = _doc([_finding("BV-001", summary="Via at (1, 2) is 0.45mm from board edge")])
    b = _doc([_finding("BV-001", summary="Via at (1, 2) is 0.42mm from board edge")])
    assert w3.classify_unit("pcb", a, b)["label"] == "P4"


def test_signal_net_lists_move_only_for_reclassified_names(monkeypatch):
    old = types.SimpleNamespace(is_power_net_name=lambda n, rails=None: True)
    new = types.SimpleNamespace(is_power_net_name=lambda n, rails=None: not str(n).endswith("_EN"))
    monkeypatch.setattr(w3, "_NETNAMES", {"a": old, "b": new})
    keep = {"net": "/SCK", "via_count": 1}
    a = _doc([], power_net_routing=[{"net": "/3V3_EN"}], return_path_continuity=[keep])
    b = _doc([], power_net_routing=[], return_path_continuity=[keep, {"net": "/3V3_EN", "via_count": 2}])
    assert w3.classify_unit("pcb", a, b)["label"] == "M6"
    c = _doc([], power_net_routing=[], return_path_continuity=[keep, {"net": "/MOSI", "via_count": 2}])
    assert w3.classify_unit("pcb", a, c)["label"] is None
