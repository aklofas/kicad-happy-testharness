"""Unit tests for the v3 round-8 budget predicates (regression/budgets/v3_round8.py)."""
import copy

import pytest

from regression.budgets import v3_round8 as r8
from regression.field_compare import Delta

pytestmark = pytest.mark.unit


def _d(path, op, before=None, after=None, analyzer="schematic", unit="u"):
    return Delta(unit=unit, analyzer=analyzer, path=path, op=op, before=before, after=after)


def _finding(rule_id, **kw):
    f = {"detector": "d", "rule_id": rule_id, "category": "c", "summary": "s", "description": "",
         "components": [], "nets": [], "pins": [], "severity": "warning", "confidence": "deterministic",
         "evidence_source": "topology", "recommendation": "", "report_context": {},
         "finding_id": f"schematic:{rule_id}:x"}
    f.update(kw)
    return f


# ---- B1 ------------------------------------------------------------------------------------

def test_b1_claims_empty_list_only():
    a, b = {"compat": {}}, {"compat": {}, "diagnostics": []}
    assert r8.b1_explained(_d("/diagnostics", "added", after=[]), a, b)
    assert not r8.b1_explained(_d("/diagnostics", "added", after=[{"source": "x"}]), a, b)
    assert not r8.b1_explained(_d("/diagnostics", "changed", before=[], after=[]), a, b)


# ---- B2 ------------------------------------------------------------------------------------

def _emc_pair():
    x = {"detector": "emc_pdn", "rule_id": "PD-001", "category": "pdn", "title": "T", "summary": "T",
         "description": "", "components": [], "nets": [], "pins": [], "severity": "warning",
         "confidence": "deterministic", "evidence_source": "topology", "recommendation": "",
         "report_context": {}, "finding_id": "emc:PD-001:a"}
    y = {"detector": "emc_pdn", "rule_id": "PD-001", "category": "pdn", "summary": "T", "description": "",
         "components": [], "nets": [], "pins": [], "severity": "warning", "confidence": "deterministic",
         "evidence_source": "topology", "recommendation": "", "report_context": {}, "schema_era": "v3.0",
         "finding_id": "emc:PD-001:a"}
    return {"findings": [x]}, {"findings": [y]}


def test_b2_title_removed_when_summary_carried_it():
    a, b = _emc_pair()
    assert r8.b2_explained(_d("/findings/0/title", "removed", before="T", analyzer="emc"), a, b)
    b["findings"][0]["summary"] = "other"
    assert not r8.b2_explained(_d("/findings/0/title", "removed", before="T", analyzer="emc"), a, b)
    a, b = _emc_pair()
    assert not r8.b2_explained(_d("/findings/0/title", "removed", before="T", analyzer="schematic"), a, b)


def test_b2_key_order_follows_make_finding():
    a, b = _emc_pair()
    assert r8.b2_explained(_d("/findings/0", "key_order", analyzer="emc"), a, b)
    y = b["findings"][0]
    reordered = {k: y[k] for k in ["rule_id", "detector"] + [k for k in y if k not in ("rule_id", "detector")]}
    b["findings"][0] = reordered
    assert not r8.b2_explained(_d("/findings/0", "key_order", analyzer="emc"), a, b)


# ---- B3 ------------------------------------------------------------------------------------

def test_b3_requires_v30_and_listed_rule():
    a = {"findings": [_finding("RS-001")]}
    b = {"findings": [_finding("RS-001", schema_era="v3.0")]}
    assert r8.b3_explained(_d("/findings/0/schema_era", "added", after="v3.0"), a, b)
    assert not r8.b3_explained(_d("/findings/0/schema_era", "added", after="v1.4"), a, b)
    b2 = {"findings": [_finding("ZZ-999", schema_era="v3.0")]}
    assert not r8.b3_explained(_d("/findings/0/schema_era", "added", after="v3.0"), a, b2)


def test_b3_top_issue_copy():
    a = {"audience_summary": {"designer": {"top_issues": [_finding("IO-001")]}}}
    b = {"audience_summary": {"designer": {"top_issues": [_finding("IO-001", schema_era="v3.0")]}}}
    assert r8.b3_explained(_d("/audience_summary/designer/top_issues/0/schema_era", "added", after="v3.0"), a, b)


# ---- B4 ------------------------------------------------------------------------------------

def test_b4_severity_mapping():
    a = {"datasheet_verification": {"findings": [{"severity": "HIGH"}], "summary": {"by_severity": {"HIGH": 1}}}}
    b = {"datasheet_verification": {"findings": [{"severity": "error"}], "summary": {"by_severity": {"error": 1}}}}
    assert r8.b4_explained(_d("/datasheet_verification/findings/0/severity", "changed", before="HIGH", after="error"), a, b)
    assert not r8.b4_explained(_d("/datasheet_verification/findings/0/severity", "changed", before="HIGH", after="warning"), a, b)
    assert r8.b4_explained(_d("/datasheet_verification/summary/by_severity/error", "added", after=1), a, b)


# ---- B5 ------------------------------------------------------------------------------------

def _sch_doc():
    rs = _finding("RS-001", nets=["BST"], pins=["U1.3"], severity="warning",
                  description="Net BST carries power_in pins but has no power_out pin.",
                  finding_id="schematic:RS-001:bst")
    other = _finding("IO-001", severity="info", finding_id="schematic:IO-001:x")
    doc = {"findings": [rs, other],
           "nets": {"BST": {"pins": [{"component": "U1", "pin_number": "3", "pin_name": "BST", "pin_type": "power_in"},
                                     {"component": "C1", "pin_number": "1", "pin_name": "1", "pin_type": "passive"}]}}}
    return doc


def _with_derived(doc):
    f = doc["findings"]
    doc["summary"] = r8.derived_mismatches.__globals__["expected_summary"](f, {})
    doc["trust_summary"] = r8.derived_mismatches.__globals__["expected_trust_summary"](
        f, {"by_confidence": {"deterministic": 0, "heuristic": 0}, "by_evidence_source": {"topology": 0}})
    doc["audience_summary"] = r8.derived_mismatches.__globals__["expected_audience_summary"](f)
    return doc


def test_b5_rs001_bootstrap_removal_is_class_a():
    a = _with_derived(_sch_doc())
    b = copy.deepcopy(a)
    b["findings"] = [dict(a["findings"][1], schema_era="v3.0")]   # RS-001 gone, IO-001 gains the era
    _with_derived(b)
    an = r8.analyze_unit(a, b)
    assert an["explained"] and an["A"] == 1 and an["B"] == 0 and an["moved"]
    assert r8.b5_findings_explained(_d("/findings/0/rule_id", "changed"), a, b)
    assert r8.b5_derived_explained(_d("/summary/total_findings", "changed"), a, b)


def test_b5_removal_of_non_bootstrap_rail_is_unexplained():
    a = _with_derived(_sch_doc())
    a["nets"]["BST"]["pins"][0]["pin_name"] = "VCC"
    b = copy.deepcopy(a)
    b["findings"] = [a["findings"][1]]
    _with_derived(b)
    an = r8.analyze_unit(a, b)
    assert not an["explained"] and "outside A" in an["reasons"][0]
    assert not r8.b5_findings_explained(_d("/findings/0/rule_id", "changed"), a, b)


def test_b5_pp001_on_second_net_is_class_b():
    a = _with_derived({"findings": [_finding("PP-001", pins=["U2.54 (VDDA)"], nets=["N1"], severity="error",
                                             finding_id="schematic:PP-001:u2-54")],
                       "nets": {"N1": {"pins": [{"component": "U2", "pin_number": "54", "pin_type": "power_in"}]},
                                "N2": {"pins": [{"component": "U2", "pin_number": "54", "pin_type": "power_in"}]}}})
    b = copy.deepcopy(a)
    b["findings"].append(_finding("PP-001", pins=["U2.54 (VDDA)"], nets=["N2"], severity="error",
                                  finding_id="schematic:PP-001:u2-54#1"))
    _with_derived(b)
    an = r8.analyze_unit(a, b)
    assert an["explained"] and an["B"] == 1


def test_b5_pure_b3_unit_is_not_a_b5_unit():
    a = _with_derived({"findings": [_finding("IO-001", severity="info")], "nets": {}})
    b = copy.deepcopy(a)
    b["findings"][0]["schema_era"] = "v3.0"
    _with_derived(b)
    an = r8.analyze_unit(a, b)
    assert an["explained"] and not an["moved"]
    assert not r8.b5_findings_explained(_d("/findings/0/schema_era", "added", after="v3.0"), a, b)


def test_b5_unrelated_change_poisons_the_unit():
    a = _with_derived(_sch_doc())
    b = copy.deepcopy(a)
    b["findings"] = [dict(a["findings"][1], schema_era="v3.0", severity="error")]
    _with_derived(b)
    an = r8.analyze_unit(a, b)
    assert not an["explained"]
