"""Unit tests for the product 3.0.x Wave 3b Part A budget predicates (regression/budgets/v30x_wave3b.py)."""
import copy

import pytest

from regression.budgets import v30x_wave3b as w3b
from regression.budgets.v232_backport import (
    expected_audience_summary,
    expected_summary,
    expected_trust_summary,
)
from regression.field_compare import Delta

pytestmark = pytest.mark.unit


def _d(analyzer, path="/components/0", op="changed"):
    return Delta(unit="u", analyzer=analyzer, path=path, op=op, before=None, after=None)


def _finding(rule_id, **kw):
    f = {"detector": "d", "rule_id": rule_id, "category": "c", "summary": "s", "description": "",
         "components": [], "nets": [], "pins": [], "severity": "warning", "confidence": "heuristic",
         "evidence_source": "topology", "recommendation": "", "report_context": {},
         "finding_id": f"x:{rule_id}:1"}
    f.update(kw)
    return f


def _doc(findings, **extra):
    doc = dict(extra)
    doc["findings"] = findings
    doc["summary"] = expected_summary(findings, {})
    doc["trust_summary"] = expected_trust_summary(
        findings, {"by_confidence": {"deterministic": 0, "heuristic": 0},
                   "by_evidence_source": {"topology": 0}})
    doc["audience_summary"] = expected_audience_summary(findings)
    return doc


def _comp(ref, **kw):
    c = {"reference": ref, "uuid": f"u-{ref}", "_sheet": 0, "value": "10k", "footprint": "R_0603",
         "datasheet": "~", "dnp": False, "in_bom": True, "on_board": True, "unit": 1, "lib_id": "Device:R"}
    c.update(kw)
    return c


def _net(*pins, **kw):
    n = {"pins": [{"component": c, "pin_number": p, "pin_name": "~", "pin_type": "passive"} for c, p in pins]}
    n.update(kw)
    return n


def _sch(components, nets, findings=(), **extra):
    return _doc(list(findings), analyzer_type="schematic", components=components, nets=nets,
                inputs={"source_files": ["/x/board.kicad_sch"]}, **extra)


def test_tilde_datasheet_only_is_h2():
    a = _sch([_comp("R1")], {"N1": _net(("R1", "1"))})
    b = copy.deepcopy(a)
    b["components"][0]["datasheet"] = ""
    r = w3b.classify_unit("schematic", a, b)
    assert r["label"] == "H2"


def test_narrow_trigger_may_not_move_the_netlist():
    a = _sch([_comp("R1")], {"N1": _net(("R1", "1"))})
    b = copy.deepcopy(a)
    b["components"][0]["datasheet"] = ""
    b["nets"]["N1"]["point_count"] = 3
    r = w3b.classify_unit("schematic", a, b)
    assert r["label"] is None
    assert "block nets" in r["reasons"]


def test_escaped_rename_is_s1_and_keeps_rule_counts():
    f = _finding("NT-001", nets=["A/B"])
    a = _sch([_comp("R1")], {"A/B": _net(("R1", "1"))}, [f])
    b = _sch([_comp("R1")], {"A{slash}B": _net(("R1", "1"), display_name="A/B")},
             [dict(f, nets=["A{slash}B"], finding_id="x:NT-001:2")])
    r = w3b.classify_unit("schematic", a, b)
    assert r["label"] == "S1"


def test_same_membership_plain_rename_is_n1c():
    a = _sch([_comp("R1"), _comp("R2")], {"/s/X": _net(("R1", "1"), ("R2", "1"))})
    b = _sch([_comp("R1"), _comp("R2")], {"Y": _net(("R1", "1"), ("R2", "1"))})
    assert w3b.classify_unit("schematic", a, b)["label"] == "N1c"


def test_same_sheet_local_and_global_join_is_n1a():
    labels = [{"name": "nRST", "type": "label", "_sheet": 0}, {"name": "nRST", "type": "global_label", "_sheet": 0}]
    a = _sch([_comp("R1"), _comp("R2")], {"nRST": _net(("R1", "1")), "/s/nRST": _net(("R2", "1"))}, labels=labels)
    b = _sch([_comp("R1"), _comp("R2")], {"nRST": _net(("R1", "1"), ("R2", "1"))}, labels=labels)
    assert w3b.classify_unit("schematic", a, b)["label"] == "N1a"


def test_movement_without_a_trigger_is_a_residual():
    f = _finding("DO-DET")
    a = _sch([_comp("R1")], {"N1": _net(("R1", "1"))}, [f])
    b = _sch([_comp("R1")], {"N1": _net(("R1", "1"))}, [f, dict(f, finding_id="x:DO-DET:2")])
    r = w3b.classify_unit("schematic", a, b)
    assert r["label"] is None
    assert "schematic movement without a trigger" in r["reasons"]


def test_empty_field_reported_as_tilde_in_the_bom_is_flagged():
    comps = [_comp("U1", datasheet="", footprint="")]
    a = _sch(comps, {}, bom=[{"references": ["U1"], "footprint": "", "datasheet": "", "value": "LM324N"}])
    b = _sch(comps, {}, bom=[{"references": ["U1"], "footprint": "~", "datasheet": "~", "value": "LM324N"}])
    r = w3b.classify_unit("schematic", a, b)
    assert r["label"] is None
    assert any("'~'" in x for x in r["reasons"])


def test_value_notation_lets_passive_detectors_move():
    f = _finding("RC-DET", components=["R1", "C1"])
    comps = [_comp("R1", value="4,7k"), _comp("C1", value="100n")]
    a = _sch(comps, {"N1": _net(("R1", "1"), ("C1", "1"))})
    b = _sch(comps, {"N1": _net(("R1", "1"), ("C1", "1"))}, [f])
    assert w3b.classify_unit("schematic", a, b)["label"] == "V2"


def test_pcb_names_kept_as_written_is_s2():
    a = _doc([], analyzer_type="pcb", nets={"1": "/A/B"}, footprints=[])
    b = _doc([], analyzer_type="pcb", nets={"1": "/A{slash}B"}, footprints=[])
    assert w3b.classify_unit("pcb", a, b)["label"] == "S2"


def test_pcb_rename_that_moves_rule_counts_is_a_residual():
    a = _doc([], analyzer_type="pcb", nets={"1": "/A/B"}, footprints=[])
    b = _doc([_finding("CC-DET")], analyzer_type="pcb", nets={"1": "/A{slash}B"}, footprints=[])
    assert w3b.classify_unit("pcb", a, b)["label"] is None


def test_predicate_claims_only_its_analyzer():
    a = _sch([_comp("R1")], {})
    b = copy.deepcopy(a)
    b["components"][0]["datasheet"] = ""
    assert w3b.schematic(_d("schematic"), a, b)
    assert not w3b.pcb(_d("schematic"), a, b)
