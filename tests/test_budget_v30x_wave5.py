"""Unit tests for the product 3.0.x Wave 5 budget predicates (regression/budgets/v30x_wave5.py)."""
import json
from pathlib import Path

import pytest

from regression.budgets import v30x_wave5 as w5
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


def test_gerber_outline_gr002_removal_and_aligned_flip_is_g54():
    a = _doc("gerber", [_finding("GR-002")], alignment={"aligned": False, "issues": ["Width varies"]})
    b = _doc("gerber", alignment={"aligned": True, "issues": []})
    r = w5.classify_unit("gerber", a, b)
    assert "G54" in r["label"].split("+") and r["stats"]["aligned F->T"] == 1


def test_gerber_aligned_true_to_false_is_a_residual():
    a = _doc("gerber", alignment={"aligned": True})
    b = _doc("gerber", alignment={"aligned": False})
    r = w5.classify_unit("gerber", a, b)
    assert r["label"] is None and "alignment.aligned True -> False" in r["reasons"]


def test_gerber_complete_true_to_false_only_on_the_job_file_branch():
    a = _doc("gerber", completeness={"complete": True, "source": "gbrjob"})
    b = _doc("gerber", [_finding("GR-001")], completeness={"complete": False, "source": "gbrjob"})
    assert "G51" in w5.classify_unit("gerber", a, b)["label"].split("+")
    a["completeness"]["source"] = b["completeness"]["source"] = "layer_names"
    assert w5.classify_unit("gerber", a, b)["label"] is None


def test_gerber_foreign_block_or_rule_is_a_residual():
    a = _doc("gerber", layers={"n": 2})
    b = _doc("gerber", layers={"n": 4})
    assert "block layers" in w5.classify_unit("gerber", a, b)["reasons"]
    a = _doc("gerber", [_finding("GR-005")])
    b = _doc("gerber")
    assert "finding GR-005" in w5.classify_unit("gerber", a, b)["reasons"]


def test_schematic_type_c_moves_usb_compliance_and_uc003_only():
    a = _doc("schematic", usb_compliance={"connectors": [{"ref": "J1", "is_type_c": False}]})
    b = _doc("schematic", [_finding("UC-003")],
             usb_compliance={"connectors": [{"ref": "J1", "is_type_c": True}]})
    r = w5.classify_unit("schematic", a, b)
    assert r["label"] == "T73" and r["stats"]["is_type_c False->True"] == 1
    b["findings"].append(_finding("UC-001"))
    b.update({k: v for k, v in _doc("schematic", b["findings"]).items() if k.endswith("summary")})
    assert w5.classify_unit("schematic", a, b)["label"] is None


def test_pcb_empty_return_path_added_is_t71_but_a_gap_is_not():
    a = _doc("pcb")
    b = _doc("pcb", return_path_continuity=[])
    assert w5.classify_unit("pcb", a, b)["label"] == "T71"
    b["return_path_continuity"] = [{"net": "CLK"}]
    assert w5.classify_unit("pcb", a, b)["label"] is None


def test_pcb_degenerate_loop_record_is_t74():
    loop = {"regulator_ref": "U1", "inductor_ref": "L1", "cap_ref": "C1", "area_mm2": 0.0,
            "vertices_mm": [[5, 5], [15, 5], [25, 5]]}
    a = _doc("pcb", switching_loop_areas=[loop])
    b = _doc("pcb", switching_loop_areas=[dict(loop, area_mm2=None, estimate="degenerate")])
    assert w5.classify_unit("pcb", a, b)["label"] == "T74"
    b["switching_loop_areas"][0]["cap_ref"] = "C2"
    assert w5.classify_unit("pcb", a, b)["label"] is None


def test_emc_sw003_not_estimated_info_is_t74_and_a_lost_sw003_is_not():
    info = _finding("SW-003", summary="Hot loop for U1 not estimated", severity="info")
    a = _doc("emc")
    b = _doc("emc", [info])
    assert w5.classify_unit("emc", a, b)["label"] == "T74"
    a = _doc("emc", [_finding("SW-003", summary="Hot loop area 40 mm2")])
    r = w5.classify_unit("emc", a, b)
    assert r["label"] is None and "SW-003 lost or changed" in r["reasons"]


def test_emc_gp001_rewording_is_one_for_one():
    old = _finding("GP-001", summary="Return path analysis data not available", severity="info")
    new = _finding("GP-001", summary="Return path not checked: no ground or power plane fill", severity="info")
    assert w5.classify_unit("emc", _doc("emc", [old]), _doc("emc", [new]))["label"] == "T71-reword"
    r = w5.classify_unit("emc", _doc("emc", [old]), _doc("emc", [new, new]))
    assert r["label"] is None and "GP-001 added beyond the rewording" in r["reasons"]


def test_emc_gp001_removal_needs_the_empty_upstream_return_path(tmp_path):
    old = _finding("GP-001", summary="Return path analysis data not available", severity="info")
    paths = {}
    for slot, extra in (("baseline", {}), ("candidate", {"return_path_continuity": []})):
        p = tmp_path / slot / "pcb" / "o" / "r" / "b.kicad_pcb" / "snap.json"
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps(_doc("pcb", **extra)))
        paths[slot] = {"inputs": {"upstream_artifacts": {"pcb": {"path": str(p)}}}}
    a = _doc("emc", [old], **paths["baseline"])
    b = _doc("emc", **paths["candidate"])
    assert w5.classify_unit("emc", a, b)["label"] == "T71-removed"
    r = w5.classify_unit("emc", _doc("emc", [old]), _doc("emc"))
    assert r["label"] is None


def test_cross_without_upstream_move_is_a_residual():
    a = _doc("cross_analysis", [_finding("PS-002")])
    b = _doc("cross_analysis")
    assert w5.classify_unit("cross_analysis", a, b)["label"] is None


@pytest.mark.parametrize("name", ["v30x-wave5", "v30x-wave5-full-chain"])
def test_budget_files_load(name):
    path = ROOT / "regression" / "budgets" / f"{name}.json"
    assert load_budget(path) is not None
    doc = json.loads(path.read_text())
    assert doc["unexplained_deltas_allowed"] == 0
    for c in doc["classes"]:
        mod, fn = c["predicate"].split(":")
        assert mod == "v30x_wave5" and callable(getattr(w5, fn))
