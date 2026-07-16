#!/usr/bin/env python3
"""KH-354: audit_pwr_flags must credit PWR_FLAG via the net-level
has_pwr_flag flag — PWR_FLAG pins never appear in nets[].pins, so the old
reference scan was dead code and every flagged rail still warned."""

import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
from analyze_schematic import build_net_map, audit_pwr_flags


def _components(with_flag):
    comps = [{
        "reference": "U1", "value": "MCU", "type": "ic",
        "in_bom": True, "_sheet": 0,
        "pins": [{"x": 10.0, "y": 20.0, "number": "1", "name": "VDD",
                  "type": "power_in"}],
    }]
    if with_flag:
        comps.append({
            "reference": "#FLG01", "value": "PWR_FLAG", "type": "power_flag",
            "in_bom": False, "_sheet": 0,
            "pins": [{"x": 10.0, "y": 20.0, "number": "1", "name": "pwr",
                      "type": "power_out"}],
        })
    return comps


_WIRES = [{"x1": 10.0, "y1": 20.0, "x2": 10.0, "y2": 18.0, "_sheet": 0}]
_LABELS = [{"x": 10.0, "y": 18.0, "name": "VBUS", "type": "label", "_sheet": 0}]


def test_flagged_rail_not_warned():
    """A power_in-only rail WITH a PWR_FLAG must not warn (that's the
    exact remedy the warning text tells users to apply)."""
    comps = _components(True)
    nets = build_net_map(comps, _WIRES, _LABELS, [], [])
    assert nets["VBUS"].get("has_pwr_flag") is True  # producer precondition
    warnings = audit_pwr_flags(comps, nets, {"VBUS"})
    assert warnings == [], warnings


def test_unflagged_power_in_rail_still_warned():
    comps = _components(False)
    nets = build_net_map(comps, _WIRES, _LABELS, [], [])
    warnings = audit_pwr_flags(comps, nets, {"VBUS"})
    assert len(warnings) == 1
    assert warnings[0]["net"] == "VBUS"
