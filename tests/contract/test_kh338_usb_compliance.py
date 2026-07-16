#!/usr/bin/env python3
"""KH-338: USB compliance — ESD arrays credit vbus_esd_protection; failed
checks are promoted to rich findings (UC-001..UC-004)."""

import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
from analyze_schematic import analyze_usb_compliance
from kicad_types import AnalysisContext


def _mk_ctx(components, nets):
    pin_net = {}
    for net_name, info in nets.items():
        for p in info["pins"]:
            pin_net[(p["component"], p["pin_number"])] = (net_name, p.get("pin_name"))
    return AnalysisContext(components=components, nets=nets,
                           lib_symbols={}, pin_net=pin_net)


_J1 = {"reference": "J1", "value": "USB_B_Micro", "type": "connector",
       "lib_id": "Connector:USB_B_Micro", "footprint": "", "pins": []}
_U2 = {"reference": "U2", "value": "USBLC6-2SC6", "type": "ic",
       "lib_id": "Power_Protection:USBLC6-2SC6", "footprint": "", "pins": []}


def _nets_with_esd_array():
    return {
        "__unnamed_10": {"pins": [
            {"component": "J1", "pin_number": "1", "pin_name": "VBUS", "x": 0.0, "y": 0.0},
            {"component": "U2", "pin_number": "5", "pin_name": "VBUS", "x": 1.0, "y": 0.0},
        ]},
        "USB_DP": {"pins": [
            {"component": "J1", "pin_number": "3", "pin_name": "D+", "x": 0.0, "y": 2.0},
            {"component": "U2", "pin_number": "3", "pin_name": "IO1", "x": 1.0, "y": 2.0},
        ]},
        "USB_DM": {"pins": [
            {"component": "J1", "pin_number": "2", "pin_name": "D-", "x": 0.0, "y": 4.0},
            {"component": "U2", "pin_number": "4", "pin_name": "IO2", "x": 1.0, "y": 4.0},
        ]},
        "GND": {"pins": [
            {"component": "J1", "pin_number": "5", "pin_name": "GND", "x": 0.0, "y": 6.0},
            {"component": "U2", "pin_number": "2", "pin_name": "GND", "x": 1.0, "y": 6.0},
        ]},
    }


def test_esd_array_credits_vbus_esd_protection():
    """USBLC6's own VBUS pin must credit vbus_esd_protection even when the
    VBUS net is unnamed (resolved by connector pin name, not net name)."""
    ctx = _mk_ctx([_J1, _U2], _nets_with_esd_array())
    result = analyze_usb_compliance(ctx, {})
    checks = result["connectors"][0]["checks"]
    assert checks["vbus_esd_protection"] == "pass"


def test_failed_checks_become_findings():
    """No caps + no ESD anywhere → vbus_decoupling and vbus_esd_protection
    fail AND surface as UC-001/UC-002 rich findings."""
    nets = {
        "__unnamed_10": {"pins": [
            {"component": "J1", "pin_number": "1", "pin_name": "VBUS", "x": 0.0, "y": 0.0},
        ]},
        "USB_DP": {"pins": [
            {"component": "J1", "pin_number": "3", "pin_name": "D+", "x": 0.0, "y": 2.0},
        ]},
    }
    ctx = _mk_ctx([_J1], nets)
    result = analyze_usb_compliance(ctx, {})
    checks = result["connectors"][0]["checks"]
    assert checks["vbus_decoupling"] == "fail"
    assert checks["vbus_esd_protection"] == "fail"
    rules = {f["rule_id"] for f in result.get("findings", [])}
    assert "UC-001" in rules and "UC-002" in rules
    uc1 = next(f for f in result["findings"] if f["rule_id"] == "UC-001")
    assert uc1["components"] == ["J1"]
    assert uc1["severity"] == "warning"
    assert uc1["confidence"] == "deterministic"
    assert uc1["detector"] == "analyze_usb_compliance"
