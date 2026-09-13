"""KH-373 — CP-003 touch-pad GND clearance was footprint-ORIGIN to zone
BBOX (0.0 mm for any enclosing pour, labelled deterministic). Now: pad
outline sample points to nearest filled-polygon edge."""

TIER = "unit"

import math
import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

import analyze_pcb  # noqa: E402


def _fills_with_hole():
    zf = analyze_pcb.ZoneFills()
    outer = [(0, 0), (9.995, 0), (9.995, 7), (7, 7), (7, 13), (13, 13), (13, 7), (10.005, 7),
             (10.005, 0), (20, 0), (20, 20), (0, 20)]
    zf.add(0, "F.Cu", outer)
    return zf


def _zone():
    return {"net_name": "GND", "layers": ["F.Cu"], "filled_bbox": [0, 0, 20, 20]}


def _tp(x=10.0, y=10.0, w=4.0, h=4.0):
    return {"reference": "TP1", "library": "Touch:Pad_4x4", "layer": "F.Cu", "x": x, "y": y,
            "pads": [{"number": "1", "type": "smd", "shape": "rect", "abs_x": x, "abs_y": y,
                      "width": w, "height": h, "layers": ["F.Cu"], "net_name": "TOUCH_1"}]}


def test_polygon_edge_distance_recovers_true_clearance():
    d, basis = analyze_pcb._nearest_zone_copper_distance(_tp(), "F.Cu", [_zone()], [_zone()], _fills_with_hole())
    assert basis == "filled_polygon"
    assert math.isclose(d, 1.0, abs_tol=0.02)


def test_bbox_fallback_when_no_fill_data():
    d, basis = analyze_pcb._nearest_zone_copper_distance(_tp(), "F.Cu", [_zone()], [_zone()], None)
    assert basis == "filled_bbox"


def test_pad_offset_from_origin_uses_pad_not_origin():
    fp = _tp(x=8.0, y=10.0)
    fp["pads"][0]["abs_x"] = 10.0
    d, _ = analyze_pcb._nearest_zone_copper_distance(fp, "F.Cu", [_zone()], [_zone()], _fills_with_hole())
    assert math.isclose(d, 1.0, abs_tol=0.02)


def test_cp003_finding_carries_polygon_basis_and_nets():
    res = analyze_pcb.analyze_copper_presence([_tp()], [_zone()], _fills_with_hole())
    tc = res.get("touch_pad_gnd_clearance") or []
    assert tc and tc[0]["measurement_basis"] == "filled_polygon"
    assert tc[0]["confidence"] == "deterministic"
    assert math.isclose(tc[0]["gnd_clearance_mm"], 1.0, abs_tol=0.02)
    assert tc[0]["nets"] == ["TOUCH_1"]


def test_pad_sampling_uses_absolute_pad_angle():
    """Fix round 2 (final reviewer): KiCad writes a pad's (at x y angle) as
    the ABSOLUTE board orientation -- it already includes the footprint's
    own rotation (verified 139/140 rotated corpus footprints: pad angle ==
    footprint angle). Adding the footprint angle again double-counts the
    rotation.

    Case A: footprint angle 90, pad angle 90 (what KiCad writes for a pad
    that is unrotated relative to a footprint placed at 90 deg) -- a 4x2 mm
    pad must sample a 2-wide/4-tall rectangle in board space.

    Case B: footprint angle 90, pad has NO angle key -- absolute pad angle
    is 0, so the same 4x2 mm pad samples 4-wide/2-tall (unrotated)."""
    fp_a = {"reference": "TP1", "library": "Touch:Pad", "layer": "F.Cu",
            "x": 10.0, "y": 10.0, "angle": 90,
            "pads": [{"number": "1", "type": "smd", "shape": "rect",
                      "abs_x": 10.0, "abs_y": 10.0, "width": 4.0, "height": 2.0,
                      "layers": ["F.Cu"], "net_name": "TOUCH_1", "angle": 90}]}
    pts_a = analyze_pcb._pad_sample_points(fp_a, "F.Cu")
    xs_a = [p[0] for p in pts_a]
    ys_a = [p[1] for p in pts_a]
    assert math.isclose(max(xs_a) - min(xs_a), 2.0, abs_tol=0.01)
    assert math.isclose(max(ys_a) - min(ys_a), 4.0, abs_tol=0.01)
    d, basis = analyze_pcb._nearest_zone_copper_distance(fp_a, "F.Cu", [_zone()], [_zone()], _fills_with_hole())
    assert basis == "filled_polygon"
    assert math.isclose(d, 1.0, abs_tol=0.02)

    fp_b = {"reference": "TP2", "library": "Touch:Pad", "layer": "F.Cu",
            "x": 10.0, "y": 10.0, "angle": 90,
            "pads": [{"number": "1", "type": "smd", "shape": "rect",
                      "abs_x": 10.0, "abs_y": 10.0, "width": 4.0, "height": 2.0,
                      "layers": ["F.Cu"], "net_name": "TOUCH_1"}]}
    pts_b = analyze_pcb._pad_sample_points(fp_b, "F.Cu")
    xs_b = [p[0] for p in pts_b]
    ys_b = [p[1] for p in pts_b]
    assert math.isclose(max(xs_b) - min(xs_b), 4.0, abs_tol=0.01)
    assert math.isclose(max(ys_b) - min(ys_b), 2.0, abs_tol=0.01)


def test_touch_pad_requires_positive_evidence_not_bare_tp_prefix():
    """KH-373: a bare TP-prefixed ref is not touch-pad evidence on its own --
    466/488 of the corpus's CP-003 "touch pad" refs were real TestPoint:*
    library parts. A testpoint library must produce NO CP-003 entry; a real
    touch/capacitive library still produces one, ref prefix notwithstanding."""
    testpoint = _tp()
    testpoint["library"] = "TestPoint:TestPoint_Pad_D1.0mm"
    res = analyze_pcb.analyze_copper_presence([testpoint], [_zone()], _fills_with_hole())
    assert not (res.get("touch_pad_gnd_clearance") or [])

    touch1 = _tp()
    touch1["reference"] = "TOUCH1"
    touch1["library"] = "Touch:Pad_4x4"
    res2 = analyze_pcb.analyze_copper_presence([touch1], [_zone()], _fills_with_hole())
    tc = res2.get("touch_pad_gnd_clearance") or []
    assert tc and tc[0]["measurement_basis"] == "filled_polygon"


if __name__ == "__main__":
    import sys
    import traceback
    ok = fail = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                ok += 1
            except Exception:  # noqa: BLE001
                fail += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)
