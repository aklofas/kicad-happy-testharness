"""Unit tests for the product 3.0.x Wave 4 Part A budget predicates (regression/budgets/v30x_wave4a.py)."""
import json
from pathlib import Path

import pytest

from regression.budgets import v30x_wave4a as w4a
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


def _doc(findings=(), **extra):
    findings = list(findings)
    doc = {"analyzer_type": "schematic", "nets": {}, "components": []}
    doc.update(extra)
    doc["findings"] = findings
    doc["summary"] = expected_summary(findings, {})
    doc["trust_summary"] = expected_trust_summary(
        findings, {"by_confidence": {"deterministic": 0, "heuristic": 0},
                   "by_evidence_source": {"topology": 0}})
    doc["audience_summary"] = expected_audience_summary(findings)
    return doc


@pytest.fixture(autouse=True)
def _no_product_netnames(monkeypatch):
    """Name re-reads come from the product clones; stub them with two tiny rule sets."""
    class Old:
        @staticmethod
        def is_power_net_name(n, rails=None):
            return n.startswith("+")

        @staticmethod
        def parse_voltage_from_net_name(n):
            return None

    class New(Old):
        @staticmethod
        def is_power_net_name(n, rails=None):
            return n.startswith(("+", "-"))

    monkeypatch.setattr(w4a, "_NETNAMES", {"a": Old, "b": New})


def test_padded_value_trimmed_is_a1_with_finding_echo():
    a = _doc([_finding("PU-001", summary="U2 (DS8561-33S5 ) pin EN", components=["U2"])],
             components=[{"reference": "U2", "value": "DS8561-33S5 "}])
    b = _doc([_finding("PU-001", summary="U2 (DS8561-33S5) pin EN", components=["U2"])],
             components=[{"reference": "U2", "value": "DS8561-33S5"}])
    r = w4a.classify_unit("schematic", a, b)
    assert r["label"] == "A1" and r["stats"]["A1_finding_echo"] == 1


def test_value_change_beyond_trim_is_a_residual():
    a = _doc(components=[{"reference": "R1", "value": "1k"}])
    b = _doc(components=[{"reference": "R1", "value": "2k"}])
    r = w4a.classify_unit("schematic", a, b)
    assert r["label"] is None and any(x.startswith("component R1 value") for x in r["reasons"])


def test_dnp_from_a_trimmed_value_is_a1():
    a = _doc(components=[{"reference": "C73", "value": "DNP ", "dnp": False}])
    b = _doc(components=[{"reference": "C73", "value": "DNP", "dnp": True}])
    r = w4a.classify_unit("schematic", a, b)
    assert r["label"] == "A1" and r["stats"]["A1_dnp_by_value"] == 1


def test_dnp_flip_without_a_trimmed_value_is_a_residual():
    a = _doc(components=[{"reference": "C73", "value": "DNP", "dnp": False}])
    b = _doc(components=[{"reference": "C73", "value": "DNP", "dnp": True}])
    assert w4a.classify_unit("schematic", a, b)["label"] is None


def test_nets_never_move():
    a = _doc(nets={"N1": {"pins": []}})
    b = _doc(nets={"N1": {"pins": [{"component": "R1", "pin_number": "1"}]}})
    r = w4a.classify_unit("schematic", a, b)
    assert r["label"] is None and "block nets" in r["reasons"]


def test_negative_rail_reread_opens_findings_naming_it():
    a = _doc([_finding("SJ-DET", power_nets=[], components=["JP1"])], nets={"-9V": {}})
    b = _doc([_finding("SJ-DET", power_nets=["-9V"], components=["JP1"])], nets={"-9V": {}})
    r = w4a.classify_unit("schematic", a, b)
    assert r["label"] == "PWR" and r["stats"]["net_names_reread"] == 1


def test_unlisted_rule_without_a_trigger_is_a_residual():
    a = _doc([_finding("SJ-DET", power_nets=[], components=["JP1"])], nets={"SIG": {}})
    b = _doc([_finding("SJ-DET", power_nets=["SIG"], components=["JP1"])], nets={"SIG": {}})
    r = w4a.classify_unit("schematic", a, b)
    assert r["label"] is None and any(x.startswith("finding SJ-DET") for x in r["reasons"])


def test_erc_retype_is_b6_and_filter_severity_is_b7():
    a = _doc(design_analysis={"erc_warnings": [{"type": "output_conflict"}]},
             footprint_filter_warnings=[{"component": "R1"}])
    b = _doc(design_analysis={"erc_warnings": [{"type": "pin_to_pin"}]},
             footprint_filter_warnings=[{"component": "R1", "severity": "info"}])
    assert w4a.classify_unit("schematic", a, b)["label"] == "B6+B7"


def test_led_retyped_diode_opens_led_rules():
    a = _doc([_finding("LR-001", components=["D1"])], components=[{"reference": "D1", "type": "led"}])
    b = _doc([], components=[{"reference": "D1", "type": "diode"}])
    assert "K1" in w4a.classify_unit("schematic", a, b)["label"].split("+")


def test_derived_summary_must_follow_findings():
    a = _doc([_finding("OA-DET", gain=1.0)])
    b = _doc([_finding("OA-DET", gain=2.0)])
    b["summary"] = {"total_findings": 7}
    r = w4a.classify_unit("schematic", a, b)
    assert r["label"] is None and "b: derived blocks not from findings" in r["reasons"]


def test_pcb_power_net_block_without_a_reread_name_is_a_residual():
    a = _doc(analyzer_type="pcb", layer_transitions=[])
    b = _doc(analyzer_type="pcb", layer_transitions=[{"net": "VM"}])
    assert w4a.classify_unit("pcb", a, b)["label"] is None


def test_pcb_reread_negative_rail_is_a4d_but_only_in_its_blocks():
    a = _doc(analyzer_type="pcb", power_net_resolution={"power": ["GND"]})
    b = _doc(analyzer_type="pcb", power_net_resolution={"power": ["-12V", "GND"]})
    assert w4a.classify_unit("pcb", a, b)["label"] == "A4d"
    b["zones"] = [{"net": "-12V"}]
    r = w4a.classify_unit("pcb", a, b)
    assert r["label"] is None and "pcb block zones" in r["reasons"]


@pytest.mark.parametrize("name", ["v30x-wave4a", "v30x-wave4a-full-chain"])
def test_budget_files_load(name):
    b = load_budget(ROOT / "regression" / "budgets" / f"{name}.json")
    doc = json.loads((ROOT / "regression" / "budgets" / f"{name}.json").read_text())
    assert doc["unexplained_deltas_allowed"] == 0 and b is not None
    for c in doc["classes"]:
        mod, fn = c["predicate"].split(":")
        assert mod == "v30x_wave4a" and callable(getattr(w4a, fn))
