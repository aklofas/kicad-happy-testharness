"""Unit tests for the product 3.0.x Wave 2 budget predicates (regression/budgets/v30x_wave2.py)."""
import copy

import pytest

from regression.budgets import v30x_wave2 as w2
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


def test_gerber_new_closure_finding_is_g2():
    a = _doc([], completeness={"complete": True})
    b = _doc([_finding("GR-005")], completeness={"complete": True})
    assert w2.classify_unit("gerber", a, b)["label"] == "G2"
    assert w2.g2(_d("gerber"), a, b)
    assert not w2.g3(_d("gerber"), a, b)


def test_gerber_other_rule_or_block_is_residual():
    a = _doc([], completeness={})
    assert w2.classify_unit("gerber", a, _doc([_finding("GR-003")], completeness={}))["label"] is None
    # a layer_count change counts only when new gerber files were read
    a2 = _doc([], gerbers=[{"f": 1}], layer_count=2)
    b2 = _doc([], gerbers=[{"f": 1}], layer_count=4)
    assert w2.classify_unit("gerber", a2, b2)["label"] is None
    b3 = _doc([], gerbers=[{"f": 1}, {"f": 2}], layer_count=4)
    assert w2.classify_unit("gerber", a2, b3)["label"] == "G2"


def test_derived_blocks_must_follow_findings():
    a = _doc([])
    b = _doc([_finding("EG-001", severity="info")])
    assert w2.classify_unit("cross_analysis", a, b)["label"] == "G3"
    bad = copy.deepcopy(b)
    bad["summary"]["total_findings"] = 7
    assert w2.classify_unit("cross_analysis", a, bad)["label"] is None


def test_thermal_shunt_skip_is_g4_but_other_refs_are_not():
    shunt = {"ref": "R1", "pdiss_w": 1.0}
    a = {"findings": [_finding("TS-003", components=["R1"])], "assessments": [shunt]}
    b = {"findings": [], "assessments": [],
         "skipped_components": [{"ref": "R1", "value": "0.01", "reason": "no_operating_current"}]}
    assert w2.classify_unit("thermal", a, b)["label"] == "G4"
    b_other = copy.deepcopy(b)
    b_other["skipped_components"][0]["reason"] = "no_vout"
    assert w2.classify_unit("thermal", a, b_other)["label"] is None


def test_regulator_inductor_pick_is_h1_and_needs_a_trigger():
    pr_a = _finding("PR-DET", ref="U1", components=["U1"], inductor="L2", output_rail="+3V3")
    pr_b = dict(pr_a, inductor="L1")
    do_a = _finding("DO-DET", components=["U1"], inductor="L2", description="with inductor L2")
    do_b = dict(do_a, inductor="L1", description="with inductor L1")
    assert w2.classify_unit("schematic", _doc([pr_a, do_a]), _doc([pr_b, do_b]))["label"] == "H1"
    # the same DO-DET movement without a PR-DET pick change is unexplained
    assert w2.classify_unit("schematic", _doc([pr_a, do_a]), _doc([pr_a, do_b]))["label"] is None


def test_ml001_victims_rebound_to_their_ids_is_h4():
    x = _finding("ML-001", components=["L3", "U6"], finding_id="emc:ML-001:l3")
    y = _finding("ML-001", components=["L3", "U4"], finding_id="emc:ML-001:l3#1")
    a = {"findings": [x, y]}
    b = {"findings": [dict(y, finding_id=x["finding_id"]), dict(x, finding_id=y["finding_id"])]}
    assert w2.classify_unit("emc", a, b)["label"] == "H4"


def test_cp001_text_reorder_is_h3_but_new_words_are_not():
    x = _finding("CP-001", components=["Q2"], description="foreign zone(s): GNDD, +BATT.")
    a, b = _doc([x]), _doc([dict(x, description="foreign zone(s): +BATT, GNDD.")])
    assert w2.classify_unit("pcb", a, b)["label"] == "H3"
    c = _doc([dict(x, description="foreign zone(s): +BATT, VCC.")])
    assert w2.classify_unit("pcb", a, c)["label"] is None
