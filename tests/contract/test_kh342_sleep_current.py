#!/usr/bin/env python3
"""KH-342: sleep-current audit — dividers scored as V/(R1+R2), series-R +
shunt-C (RC filter) scored ~0 instead of worst-case V/R."""

import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
from analyze_schematic import analyze_sleep_current
from kicad_types import AnalysisContext


def _mk_ctx(components, nets):
    pin_net = {}
    for net_name, info in nets.items():
        for p in info["pins"]:
            pin_net[(p["component"], p["pin_number"])] = (net_name, p.get("pin_name"))
    return AnalysisContext(components=components, nets=nets,
                           lib_symbols={}, pin_net=pin_net)


def _r(ref, value):
    return {"reference": ref, "value": value, "type": "resistor",
            "lib_id": "Device:R", "footprint": "", "pins": []}


def _pins(*items):
    return {"pins": [{"component": c, "pin_number": n, "pin_name": n,
                      "x": 0.0, "y": 0.0} for c, n in items]}


def test_divider_scored_as_one_path():
    """680k + 150k divider from +3V3: one entry at V/(R1+R2) = 3.98uA."""
    components = [_r("R10", "680k"), _r("R11", "150k")]
    nets = {
        "+3V3": _pins(("R10", "1")),
        "MID": _pins(("R10", "2"), ("R11", "1")),
        "GND": _pins(("R11", "2")),
    }
    result = analyze_sleep_current(_mk_ctx(components, nets))
    paths = result["rails"]["+3V3"]["current_paths"]
    divider = [e for e in paths if e["ref"] == "R10"]
    assert len(divider) == 1
    assert divider[0]["type"] == "divider"
    assert abs(divider[0]["current_uA"] - 3.98) < 0.05
    assert divider[0]["divider_partner"] == "R11"


def test_rc_filter_scored_zero():
    """Series R into a shunt-C node (EN RC filter): steady-state ~ 0."""
    components = [
        _r("R7", "330k"),
        {"reference": "C3", "value": "100n", "type": "capacitor",
         "lib_id": "Device:C", "footprint": "", "pins": []},
        {"reference": "U1", "value": "TPS61023", "type": "ic",
         "lib_id": "Regulator_Switching:TPS61023", "footprint": "", "pins": []},
    ]
    nets = {
        "+3V3": _pins(("R7", "1")),
        "EN_RC": _pins(("R7", "2"), ("C3", "1"), ("U1", "4")),
        "GND": _pins(("C3", "2")),
    }
    result = analyze_sleep_current(_mk_ctx(components, nets))
    paths = result["rails"]["+3V3"]["current_paths"]
    rc = [e for e in paths if e["ref"] == "R7"]
    assert len(rc) == 1
    assert rc[0]["type"] == "rc_filter"
    assert rc[0]["current_uA"] == 0.0


def test_plain_pullup_unchanged():
    """A pull-up to a plain signal net stays worst-case V/R."""
    components = [
        _r("R4", "10k"),
        {"reference": "U1", "value": "MCU", "type": "ic",
         "lib_id": "MCU:MCU", "footprint": "", "pins": []},
    ]
    nets = {
        "+3V3": _pins(("R4", "1")),
        "SDA": _pins(("R4", "2"), ("U1", "7")),
    }
    result = analyze_sleep_current(_mk_ctx(components, nets))
    paths = result["rails"]["+3V3"]["current_paths"]
    pu = [e for e in paths if e["ref"] == "R4"]
    assert len(pu) == 1
    assert pu[0]["type"] == "pull_up"
    assert abs(pu[0]["current_uA"] - 330.0) < 0.5
