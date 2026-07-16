#!/usr/bin/env python3
"""KH-350: courtyard overlap must use chained CrtYd polygons, not a single
AABB — QFP corner notches otherwise produce phantom overlaps (GitHub #29)."""

import json
import subprocess
import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
from analyze_pcb import analyze_placement, _chain_segments

ANALYZE_PCB = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_pcb.py"

# Plus/cross-shaped courtyard (12 segments), like a QFP with corner notches
_PLUS = [(-3, -1), (-1, -1), (-1, -3), (1, -3), (1, -1), (3, -1),
         (3, 1), (1, 1), (1, 3), (-1, 3), (-1, 1), (-3, 1)]


def _plus_poly(cx=0.0, cy=0.0):
    return [[cx + px, cy + py] for px, py in _PLUS]


def _rect_poly(x1, y1, x2, y2):
    return [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]


def test_chain_segments_closes_square():
    segs = [((0, 0), (2, 0)), ((2, 2), (0, 2)), ((2, 0), (2, 2)), ((0, 2), (0, 0))]
    polys = _chain_segments(segs)
    assert polys is not None and len(polys) == 1
    assert len(polys[0]) == 4


def test_chain_segments_open_chain_returns_none():
    segs = [((0, 0), (2, 0)), ((2, 0), (2, 2))]
    assert _chain_segments(segs) is None


def test_notch_neighbor_not_flagged():
    """R2 entirely inside the plus-shape's corner notch: AABBs overlap but
    true polygon overlap is 0 — no finding (the GitHub #29 artifact)."""
    fp_a = {"reference": "U1", "layer": "F.Cu", "x": 0.0, "y": 0.0,
            "courtyard": {"min_x": -3.0, "min_y": -3.0, "max_x": 3.0, "max_y": 3.0},
            "courtyard_poly": [_plus_poly()]}
    fp_b = {"reference": "R2", "layer": "F.Cu", "x": 2.0, "y": 2.0,
            "courtyard": {"min_x": 1.2, "min_y": 1.2, "max_x": 2.8, "max_y": 2.8},
            "courtyard_poly": [_rect_poly(1.2, 1.2, 2.8, 2.8)]}
    result = analyze_placement([fp_a, fp_b], {})
    assert not result.get("courtyard_overlaps")


def test_true_overlap_still_flagged_with_refined_area():
    fp_a = {"reference": "U1", "layer": "F.Cu", "x": 0.0, "y": 0.0,
            "courtyard": {"min_x": -3.0, "min_y": -3.0, "max_x": 3.0, "max_y": 3.0},
            "courtyard_poly": [_plus_poly()]}
    fp_c = {"reference": "C1", "layer": "F.Cu", "x": 0.0, "y": 0.0,
            "courtyard": {"min_x": -0.5, "min_y": -0.5, "max_x": 0.5, "max_y": 0.5},
            "courtyard_poly": [_rect_poly(-0.5, -0.5, 0.5, 0.5)]}
    result = analyze_placement([fp_a, fp_c], {})
    overlaps = result.get("courtyard_overlaps", [])
    assert len(overlaps) == 1
    assert 0.9 <= overlaps[0]["overlap_mm2"] <= 1.1


def test_no_polys_falls_back_to_aabb():
    fp_a = {"reference": "U1", "layer": "F.Cu", "x": 0.0, "y": 0.0,
            "courtyard": {"min_x": -3.0, "min_y": -3.0, "max_x": 3.0, "max_y": 3.0}}
    fp_b = {"reference": "R2", "layer": "F.Cu", "x": 2.0, "y": 2.0,
            "courtyard": {"min_x": 1.2, "min_y": 1.2, "max_x": 2.8, "max_y": 2.8}}
    result = analyze_placement([fp_a, fp_b], {})
    assert len(result.get("courtyard_overlaps", [])) == 1


def test_extraction_emits_courtyard_poly(tmp_path):
    """End-to-end: fp_line CrtYd segments chain into courtyard_poly."""
    segs = "\n".join(
        f'    (fp_line (start {x1} {y1}) (end {x2} {y2}) (layer "F.CrtYd") (width 0.05))'
        for (x1, y1), (x2, y2) in zip(_PLUS, _PLUS[1:] + _PLUS[:1]))
    board = f'''(kicad_pcb (version 20221018) (generator pcbnew)
  (general (thickness 1.6))
  (layers (0 "F.Cu" signal) (31 "B.Cu" signal)
    (44 "Edge.Cuts" user) (46 "B.CrtYd" user) (47 "F.CrtYd" user))
  (net 0 "")
  (footprint "Test:CROSS" (layer "F.Cu")
    (at 10 10)
    (property "Reference" "U1" (at 0 0) (layer "F.SilkS"))
{segs}
  )
)
'''
    board_file = tmp_path / "kh350.kicad_pcb"
    board_file.write_text(board)
    out_file = tmp_path / "out.json"
    r = subprocess.run([sys.executable, str(ANALYZE_PCB), str(board_file),
                        "--output", str(out_file)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    data = json.loads(out_file.read_text())
    fp = data["footprints"][0]
    assert fp["courtyard"] == {"min_x": 7.0, "min_y": 7.0,
                               "max_x": 13.0, "max_y": 13.0}
    polys = fp.get("courtyard_poly")
    assert polys and len(polys) == 1 and len(polys[0]) == 12
