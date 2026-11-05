"""Unit tests for the product 3.0.x Wave 9f budget predicates (regression/budgets/v30x_wave9f.py)."""
from pathlib import Path

import pytest

from regression.budgets import v30x_wave9f as w9f
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
         "components": [], "nets": [], "pins": [], "severity": "info", "confidence": "heuristic",
         "evidence_source": "topology", "recommendation": "", "report_context": {},
         "finding_id": f"x:{rule_id}:1"}
    f.update(kw)
    return f


def _sch(findings=(), components=(), **extra):
    findings = list(findings)
    doc = {"analyzer_type": "schematic", "components": list(components), **extra, "findings": findings}
    doc["summary"] = expected_summary(findings, {})
    doc["trust_summary"] = expected_trust_summary(
        findings, {"by_confidence": {"deterministic": 0, "heuristic": 0},
                   "by_evidence_source": {"topology": 0}})
    doc["audience_summary"] = expected_audience_summary(findings)
    return doc


def _label(a, b, analyzer="schematic"):
    return w9f.classify_unit(analyzer, a, b)["label"]


def test_budget_files_load_and_name_the_module():
    for name in ("v30x-wave9f", "v30x-wave9f-full-chain"):
        b = load_budget(ROOT / "regression" / "budgets" / f"{name}.json")
        assert {c["predicate"].split(":")[0] for c in b["classes"]} == {"v30x_wave9f"}


def test_ib_det_removed_when_every_rail_was_a_substring_match():
    a = _sch([_finding("IB-DET", isolated_power_rails=["V_BAT", "MIC_BIAS"])])
    assert _label(a, _sch()) == "IB"


def test_ib_det_narrowed_to_whole_token_rails():
    a = _sch([_finding("IB-DET", isolated_power_rails=["3.3V_B", "VCC_BATT"])])
    b = _sch([_finding("IB-DET", isolated_power_rails=["3.3V_B"])])
    assert _label(a, b) == "IB"


def test_ib_det_dropping_a_whole_token_rail_is_a_residual():
    a = _sch([_finding("IB-DET", isolated_power_rails=["3.3V_B", "ISO_5V"])])
    b = _sch([_finding("IB-DET", isolated_power_rails=["3.3V_B"])])
    assert _label(a, b) is None
    assert _label(a, _sch()) is None


def test_regulator_moves_need_a_low_suffix_part():
    low = [{"reference": "U1", "value": "LC78_03-05"}]
    a = _sch([_finding("PR-DET", estimated_vout=0.3)], low, rail_voltages={"VOUT": 0.3})
    b = _sch([_finding("PR-DET")], low, rail_voltages={})
    assert _label(a, b) == "REG"
    plain = [{"reference": "U1", "value": "AP1117-33"}]
    assert _label(dict(a, components=plain), dict(b, components=plain)) is None


def test_pcb_may_not_move():
    a = {"analyzer_type": "pcb", "findings": []}
    assert _label(a, dict(a, statistics={"x": 1}), "pcb") is None
