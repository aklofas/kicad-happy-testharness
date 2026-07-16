#!/usr/bin/env python3
"""KH-341: DC-003 must not demand vias on 2-layer boards or when the cap
pad ties directly into a same-layer pour of its own net."""

import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "emc" / "scripts"))
from emc_rules import check_decoupling_via_distance


def _pcb(layer_types, zones=None, cap_pads=None):
    return {
        "layers": [{"name": f"L{i}", "type": t}
                   for i, t in enumerate(layer_types)],
        "decoupling_placement": [{"ic": "U1", "nearby_caps": [{"cap": "C1"}]}],
        "vias": {"vias": [{"x": 50.0, "y": 50.0}]},
        "zones": zones or [],
        "footprints": [{"reference": "C1", "layer": "F.Cu",
                        "x": 0.0, "y": 0.0, "pads": cap_pads or []}],
    }


def test_two_layer_board_suppressed():
    assert check_decoupling_via_distance(_pcb(["signal", "signal"])) == []


def test_four_layer_board_still_fires():
    findings = check_decoupling_via_distance(
        _pcb(["signal", "power", "power", "signal"]))
    assert len(findings) == 1
    assert findings[0].get("rule_id") == "DC-003"


def test_same_layer_same_net_pour_suppresses():
    zones = [{"net_name": "GND", "layers": ["F.Cu"],
              "filled_bbox": [-5.0, -5.0, 5.0, 5.0]}]
    pads = [{"net_name": "GND", "abs_x": 0.5, "abs_y": 0.0}]
    pcb = _pcb(["signal", "power", "power", "signal"], zones, pads)
    assert check_decoupling_via_distance(pcb) == []
