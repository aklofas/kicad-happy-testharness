"""Unit tests for the product 3.0.x Wave 10b budget predicates (regression/budgets/v30x_wave10b.py)."""
from pathlib import Path

import pytest

from regression.budgets import v30x_wave10b as w10b
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


def _doc(analyzer, findings=(), **extra):
    findings = list(findings)
    doc = {"analyzer_type": analyzer, **extra, "findings": findings}
    doc["summary"] = expected_summary(findings, {})
    doc["trust_summary"] = expected_trust_summary(
        findings, {"by_confidence": {"deterministic": 0, "heuristic": 0},
                   "by_evidence_source": {"topology": 0}})
    doc["audience_summary"] = expected_audience_summary(findings)
    return doc


def _label(a, b, analyzer="schematic", unit=""):
    return w10b.classify_unit(analyzer, a, b, unit)["label"]


def _seq(en_source, enable_type, order=0):
    return {"power_sequencing": {"dependencies": [{"regulator": "U1", "en_net": "GND", "en_source": en_source}]},
            "power_sequencing_validation": {"power_tree": [{"rail": "+5V", "source": "U1", "enable_type": enable_type,
                                                            "sequence_order": order}]}}


def test_budget_files_load_and_name_the_module():
    for name in ("v30x-wave10b", "v30x-wave10b-full-chain"):
        b = load_budget(ROOT / "regression" / "budgets" / f"{name}.json")
        assert {c["predicate"].split(":")[0] for c in b["classes"]} == {"v30x_wave10b"}


def test_rail_voltages_may_only_lose_entries():
    a = _doc("schematic", rail_voltages={"+3V3": 3.3, "A3V3": 3.3})
    assert _label(a, _doc("schematic", rail_voltages={"+3V3": 3.3})) == "RV"
    assert _label(a, _doc("schematic", rail_voltages={"+3V3": 3.3, "A3V3": 3.3, "X": 1.0})) is None
    assert _label(a, _doc("schematic", rail_voltages={"+3V3": 5.0})) is None


def test_en_on_ground_moves_always_on_to_tied_to_ground():
    a = _doc("schematic", **_seq("always_on", "tied_to_rail"))
    assert _label(a, _doc("schematic", **_seq("tied_to_ground", "tied_to_ground"))) == "SEQ"
    assert _label(a, _doc("schematic", **_seq("tied_to_ground", "always_on"))) == "SEQ"


def test_en_source_from_another_value_is_a_residual():
    a = _doc("schematic", **_seq("disabled", "floating"))
    assert _label(a, _doc("schematic", **_seq("tied_to_ground", "tied_to_ground"))) is None


def test_always_on_power_tree_keeps_its_sequence_order():
    a = _doc("schematic", **_seq("always_on", "tied_to_rail", order=0))
    assert _label(a, _doc("schematic", **_seq("always_on", "always_on", order=1))) is None


def test_schematic_finding_counts_may_not_move():
    a = _doc("schematic", [_finding("PR-DET")])
    assert _label(a, _doc("schematic", [_finding("PR-DET"), _finding("RS-001")])) is None


def test_derating_fields_added_in_place():
    a = _doc("schematic", [_finding("PR-DET", output_capacitors=[{"ref": "C1"}])])
    b = _doc("schematic", [_finding("PR-DET", output_capacitors=[{"ref": "C1", "derating_factor": 0.8}])])
    assert _label(a, b) == "DER"


def test_pcb_moves_only_pm001():
    a = _doc("pcb", [_finding("PM-001", layer="F.CrtYd"), _finding("DF-001")])
    assert _label(a, _doc("pcb", [_finding("DF-001")]), "pcb") == "PM"
    assert _label(a, _doc("pcb", [_finding("PM-001", layer="F.CrtYd")]), "pcb") is None


def test_emc_stage_family_must_read_layout():
    a = _doc("emc", [_finding("SU-001", stages=["schematic"]), _finding("GP-001", stages=["layout"])])
    b = _doc("emc", [_finding("SU-001", stages=["layout"]), _finding("GP-001", stages=["layout"])])
    assert _label(a, b, "emc") == "STAGE"
    c = _doc("emc", [_finding("SU-001", stages=["schematic"]), _finding("GP-001", stages=["layout"])])
    assert _label(a, c, "emc") is None


def test_emc_rule_outside_the_set_is_a_residual():
    a = _doc("emc", [])
    assert _label(a, _doc("emc", [_finding("RP-001")]), "emc") == "ZG"
    assert _label(a, _doc("emc", [_finding("GP-001")]), "emc") is None


def test_gerber_only_named_directories():
    a = _doc("gerber", [], drills=[{"file": "x.drl"}])
    b = _doc("gerber", [], drills=[])
    assert _label(a, b, "gerber", "gerber/GlasgowEmbedded/glasgow/hardware_boards_glasgow_revA") == "GERBER"
    assert _label(a, b, "gerber", "gerber/someone/else/board") is None


def test_cross_rp002_removed_or_relabelled():
    a = _doc("cross_analysis", [_finding("RP-002", confidence="deterministic"), _finding("PS-002", confidence="deterministic")])
    b = _doc("cross_analysis", [_finding("PS-002")])
    assert _label(a, b, "cross_analysis") == "RELABEL+RP2"
    assert _label(a, _doc("cross_analysis", [_finding("PS-002", confidence="deterministic"),
                                             _finding("PS-002", confidence="deterministic")]), "cross_analysis") is None
