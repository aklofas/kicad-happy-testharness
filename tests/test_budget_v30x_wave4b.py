"""Unit tests for the product 3.0.x Wave 4 Part B budget predicates (regression/budgets/v30x_wave4b.py)."""
import json
from pathlib import Path

import pytest

from regression.budgets import v30x_wave4b as w4b
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


def test_keepout_removal_is_p1():
    a = _doc("pcb", [_finding("KO-001")])
    b = _doc("pcb")
    assert "P1" in w4b.classify_unit("pcb", a, b)["label"].split("+")


def test_footprint_attribute_moves_are_p7_but_other_fields_are_residual():
    a = _doc("pcb", footprints=[{"reference": "R1", "type": "smd", "x": 1}], statistics={"smd_count": 1})
    b = _doc("pcb", footprints=[{"reference": "R1", "type": "unspecified", "x": 1}], statistics={"smd_count": 0})
    assert "P7" in w4b.classify_unit("pcb", a, b)["label"].split("+")
    b["footprints"][0]["x"] = 2
    r = w4b.classify_unit("pcb", a, b)
    assert r["label"] is None and "footprint R1 x" in r["reasons"]


def test_routing_note_diagnostic_is_allowed_but_a_foreign_one_is_not():
    note = {"exception": "ValueError", "message": "pads are not checked for a copper path between them"}
    a = _doc("pcb", diagnostics=[])
    b = _doc("pcb", diagnostics=[note])
    assert w4b.classify_unit("pcb", a, b)["label"]
    b["diagnostics"] = [{"exception": "KeyError", "message": "boom"}]
    r = w4b.classify_unit("pcb", a, b)
    assert r["label"] is None and "diagnostics beyond the Part B records" in r["reasons"]


def test_pcb_block_outside_the_classes_is_a_residual():
    a = _doc("pcb", zones=[{"net": "GND"}])
    b = _doc("pcb", zones=[{"net": "VCC"}])
    r = w4b.classify_unit("pcb", a, b)
    assert r["label"] is None and "block zones" in r["reasons"]


def test_schematic_moves_only_in_pdn_and_net_classification():
    a = _doc("schematic", design_analysis={"net_classification": {"N": "control"}}, pdn_impedance={"r": 1})
    b = _doc("schematic", design_analysis={"net_classification": {"N": "signal"}}, pdn_impedance={"r": 2})
    r = w4b.classify_unit("schematic", a, b)
    assert r["label"] == "P14b+P16" and r["stats"]["P16:control->signal"] == 1
    b["rail_voltages"] = {"+3V3": 3.3}
    assert w4b.classify_unit("schematic", a, b)["label"] is None


def test_emc_part_b_rules_move_on_their_own_others_need_upstream():
    a = _doc("emc", [_finding("EF-002")])
    b = _doc("emc")
    assert w4b.classify_unit("emc", a, b)["label"] == "E"
    a = _doc("emc", [_finding("SW-001")])
    r = w4b.classify_unit("emc", a, b)
    assert r["label"] is None and "identical upstream" in r["reasons"][0]


def test_cross_without_upstream_move_is_a_residual():
    a = _doc("cross_analysis", [_finding("PS-002")])
    b = _doc("cross_analysis")
    assert w4b.classify_unit("cross_analysis", a, b)["label"] is None


@pytest.mark.parametrize("name", ["v30x-wave4b", "v30x-wave4b-full-chain"])
def test_budget_files_load(name):
    path = ROOT / "regression" / "budgets" / f"{name}.json"
    assert load_budget(path) is not None
    doc = json.loads(path.read_text())
    assert doc["unexplained_deltas_allowed"] == 0
    for c in doc["classes"]:
        mod, fn = c["predicate"].split(":")
        assert mod == "v30x_wave4b" and callable(getattr(w4b, fn))
