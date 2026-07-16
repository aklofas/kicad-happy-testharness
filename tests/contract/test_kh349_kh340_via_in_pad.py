#!/usr/bin/env python3
"""KH-349 + KH-340: VP-001 must skip copper-less pads (GitHub #28) and use
shape/rotation-aware hit-testing instead of the axis-aligned bbox."""

import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
from analyze_pcb import analyze_via_in_pad


def _pad(shape="rect", w=2.0, h=2.0, angle=0, x=0.0, y=0.0,
         layers=("F.Cu", "F.Mask"), number="1"):
    p = {"number": number, "type": "smd", "shape": shape,
         "abs_x": x, "abs_y": y, "width": w, "height": h,
         "layers": list(layers), "net_name": "N1"}
    if angle:
        p["angle"] = angle
    return p


def _run(pads, via_xy):
    fps = [{"reference": "U2", "pads": pads}]
    vias = {"vias": [{"x": via_xy[0], "y": via_xy[1]}]}
    return analyze_via_in_pad(fps, vias, set())


def test_copperless_pad_skipped():
    """RFM69-style disabled pad: (layers "Dwgs.User") — no copper, no finding."""
    assert _run([_pad(layers=("Dwgs.User",), number="")], (0.0, 0.0)) == []


def test_copper_pad_still_flagged():
    findings = _run([_pad()], (0.0, 0.0))
    assert len(findings) == 1
    assert findings[0]["rule_id"] == "VP-001"


def test_missing_layers_key_keeps_current_behavior():
    p = _pad()
    del p["layers"]
    assert len(_run([p], (0.0, 0.0))) == 1


def test_circle_pad_corner_via_not_flagged():
    """KH-340 repro: via at 8.16mm radial from a 15mm circular pad center
    sits in the bbox corner but outside the copper circle."""
    assert _run([_pad(shape="circle", w=15.0, h=15.0)], (5.77, 5.77)) == []


def test_circle_pad_inside_flagged():
    assert len(_run([_pad(shape="circle", w=15.0, h=15.0)], (5.0, 0.0))) == 1


def test_rotated_rect_pad():
    """4x1 pad rotated 90 deg: real extent is x±0.5, y±2.0."""
    pads = [_pad(shape="rect", w=4.0, h=1.0, angle=90)]
    assert len(_run(pads, (0.0, 1.5))) == 1   # inside rotated pad
    assert _run(pads, (1.5, 0.0)) == []        # outside rotated pad


def test_oval_pad_corner_not_flagged():
    """3x1 stadium: (1.4, 0.45) is inside the bbox but past the end cap."""
    pads = [_pad(shape="oval", w=3.0, h=1.0)]
    assert _run(pads, (1.4, 0.45)) == []
    assert len(_run(pads, (1.4, 0.0))) == 1
