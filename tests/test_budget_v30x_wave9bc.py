"""Unit tests for the product 3.0.x Waves 9b + 9c budget predicates (regression/budgets/v30x_wave9bc.py)."""
import copy
from pathlib import Path

import pytest

from regression.budgets import v30x_wave9bc as w9
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


def _pin(comp, num, ptype="passive"):
    return {"component": comp, "pin_number": num, "pin_type": ptype}


def _sch(nets, findings=()):
    return _doc("schematic", findings, nets={k: {"name": k, "pins": v} for k, v in nets.items()},
                components=[{"reference": "U1", "pin_nets": {}}], statistics={"total_nets": len(nets)},
                labels=[])


def _label(analyzer, a, b):
    return w9.classify_unit(analyzer, a, b)["label"]


def test_budget_files_load_and_name_the_module():
    for name in ("v30x-wave9bc", "v30x-wave9bc-full-chain"):
        b = load_budget(ROOT / "regression" / "budgets" / f"{name}.json")
        assert {c["predicate"].split(":")[0] for c in b["classes"]} == {"v30x_wave9bc"}


def test_nc_pin_taking_its_own_net_is_nc():
    a = _sch({"GND": [_pin("U1", "1", "power_in"), _pin("U1", "5", "no_connect")]})
    b = _sch({"GND": [_pin("U1", "1", "power_in")], "__unnamed_0": [_pin("U1", "5", "no_connect")]})
    assert _label("schematic", a, b) == "NC"


def test_legacy_unconnected_pin_alone_on_a_label_net_is_nc():
    a = _sch({"SPI_CLK": [_pin("U4", "45", "unconnected")]})
    b = _sch({"SPI_CLK": [], "__unnamed_0": [_pin("U4", "45", "unconnected")]})
    b["statistics"]["total_nets"] = 2
    assert _label("schematic", a, b) == "NC"


def test_signal_pin_leaving_a_net_is_a_residual():
    a = _sch({"SIG": [_pin("U1", "1", "input"), _pin("R1", "1")]})
    b = _sch({"SIG": [_pin("R1", "1")], "__unnamed_0": [_pin("U1", "1", "input")]})
    assert _label("schematic", a, b) is None


def test_listed_rule_may_move_other_rules_only_in_place():
    nets = {"VCC": [_pin("U1", "1", "power_in")]}
    a = _sch(nets, [_finding("LD-DET", collector_is_power=False)])
    b = _sch(nets, [_finding("LD-DET", collector_is_power=True), _finding("DC-DET")])
    assert _label("schematic", a, b) == "F"
    c = _sch(nets, [])
    assert _label("schematic", a, c) is None


def _pcb(findings=(), **extra):
    return _doc("pcb", findings, **extra)


def test_ko001_drops_the_allowed_net_key_and_findings_only_leave():
    a = _pcb([_finding("KO-001", via_x=1.0, keepout_allowed_net=""), _finding("KO-001", via_x=2.0, keepout_allowed_net="")])
    b = _pcb([_finding("KO-001", via_x=1.0)])
    assert _label("pcb", a, b) == "KO"
    c = _pcb([_finding("KO-001", via_x=1.0, keepout_allowed_net="")])
    assert _label("pcb", a, c) is None


def test_decoupling_caps_only_leave():
    a = _pcb(decoupling_placement=[{"ic": "U1", "nearby_caps": [{"cap": "C1"}, {"cap": "C2"}]}])
    b = _pcb(decoupling_placement=[{"ic": "U1", "nearby_caps": [{"cap": "C2"}]}])
    assert _label("pcb", a, b) == "DEC"
    assert _label("pcb", b, a) is None


def test_ground_domains_pad_named_leave_zero_volt_arrives():
    def gd(*nets):
        return {"domain_count": len(nets), "domains": [{"net": n} for n in nets], "multi_domain_components": []}
    a = _pcb(ground_domains=gd("GND", "unconnected-(U1-GND-Pad3)"))
    b = _pcb(ground_domains=gd("GND", "/BAT-"))
    assert _label("pcb", a, b) == "GND"
    assert _label("pcb", a, _pcb(ground_domains=gd("GND", "AGND"))) is None


def _gerber(files, **extra):
    return _doc("gerber", [], gerbers=files, statistics={"gerber_files": len(files)}, **extra)


def test_gerber_dotfile_leaves_and_extent_restored_from_zero():
    a = _gerber([{"filename": "b.gtl", "layer_type": "F.Cu"}, {"filename": "b.gtl:Zone.Identifier", "layer_type": "F.Cu"}],
                alignment={"aligned": True, "layer_extents": {"F.Cu": {"width": 0, "height": 0}}})
    b = _gerber([{"filename": "b.gtl", "layer_type": "F.Cu"}],
                alignment={"aligned": True, "layer_extents": {"F.Cu": {"width": 30.0, "height": 20.0}}})
    assert _label("gerber", a, b) == "G-EXT+G-SKIP"


def test_gerber_extent_growing_without_a_dropped_file_is_a_residual():
    a = _gerber([{"filename": "b.gtl"}], alignment={"layer_extents": {"F.Cu": {"width": 10.0, "height": 10.0}}})
    b = copy.deepcopy(a)
    b["alignment"]["layer_extents"]["F.Cu"]["width"] = 12.0
    assert _label("gerber", a, b) is None


def test_emc_listed_rule_moves_unlisted_needs_an_upstream_move():
    a = _doc("emc", [_finding("SW-003", severity="error")])
    b = _doc("emc", [_finding("SW-003", severity="info")])
    assert _label("emc", a, b) == "E"
    c = _doc("emc", [_finding("XT-001")])
    assert _label("emc", _doc("emc", []), c) is None
