#!/usr/bin/env python3
"""KH-344: PM-002 must describe negative clearances as overhangs, not tell
the user to 'move further from board edge'."""

import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
from analyze_pcb import analyze_placement


def test_negative_clearance_reframed_as_overhang():
    outline = {"bounding_box": {"min_x": 0.0, "min_y": 0.0,
                                "max_x": 20.0, "max_y": 20.0,
                                "width": 20.0, "height": 20.0}}
    fp = {"reference": "U1", "value": "SENSOR", "library": "Package_DFN",
          "layer": "F.Cu", "x": 1.0, "y": 10.0,
          "courtyard": {"min_x": -3.0, "min_y": 8.0,
                        "max_x": 3.0, "max_y": 12.0}}
    result = analyze_placement([fp], outline)
    w = result["edge_clearance_warnings"][0]
    assert w["edge_clearance_mm"] == -3.0
    assert "overhangs" in w["summary"]
    assert "Move" not in w["recommendation"]


def test_positive_clearance_unchanged():
    outline = {"bounding_box": {"min_x": 0.0, "min_y": 0.0,
                                "max_x": 20.0, "max_y": 20.0,
                                "width": 20.0, "height": 20.0}}
    fp = {"reference": "R1", "value": "10k", "library": "Resistor_SMD",
          "layer": "F.Cu", "x": 0.7, "y": 10.0,
          "courtyard": {"min_x": 0.3, "min_y": 9.0,
                        "max_x": 1.1, "max_y": 11.0}}
    result = analyze_placement([fp], outline)
    w = result["edge_clearance_warnings"][0]
    assert "from board edge" in w["summary"]
    assert w["recommendation"].startswith("Move")
