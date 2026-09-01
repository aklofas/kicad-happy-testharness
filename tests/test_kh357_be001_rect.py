"""KH-357 / GitHub #31 — BE-001 rect outline expansion regression test.

`_point_to_edges_min_distance` treated a `rect` board-outline edge the
same as a `line` edge — i.e. measured distance to the segment joining
its two opposite corners (the rectangle's diagonal) instead of to its
four sides. A trace point sitting near a real board edge but far from
the diagonal was scored as if it were almost ON the diagonal, producing
wrong BE-001 (trace-near-board-edge) distances.

Fixture: a synthetic pcb-analysis dict with a single `rect` board_outline
edge, mirroring the producer's real edge shape (`analyze_pcb.py`'s
`gr_rect` handling emits `{"type": "rect", "start": [x1, y1], "end":
[x2, y2]}`).
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))
sys.path.insert(0, os.path.join(_KH, "skills", "emc", "scripts"))

from emc_rules import _point_to_edges_min_distance


def test_rect_edge_measures_to_nearest_side_not_diagonal():
    """A 100x100 rect outline at the origin: the point (38.425, 38.755)
    sits near the x=0 side (dist ~38.4) but the old code measured to the
    (0,0)->(100,100) diagonal instead (dist ~0.23)."""
    pcb = {
        "board_outline": {
            "edges": [
                {"type": "rect", "start": [0.0, 0.0], "end": [100.0, 100.0]},
            ],
        },
    }
    edges = pcb["board_outline"]["edges"]
    dist = _point_to_edges_min_distance(38.425, 38.755, edges)
    assert abs(dist - 38.425) < 0.01, (
        f"expected distance to nearest side (~38.4), got {dist} "
        f"(0.23 would mean it's still measuring to the diagonal)"
    )


def test_rect_edge_line_behavior_unchanged():
    """Non-rect `line` edges must keep measuring to the exact segment
    (regression guard against the rect fix leaking into the line path)."""
    pcb = {
        "board_outline": {
            "edges": [
                {"type": "line", "start": [0.0, 0.0], "end": [100.0, 100.0]},
            ],
        },
    }
    edges = pcb["board_outline"]["edges"]
    dist = _point_to_edges_min_distance(38.425, 38.755, edges)
    assert abs(dist - 0.2333452377915645) < 0.001


if __name__ == "__main__":
    import sys as _sys
    tests = [(name, fn) for name, fn in globals().items()
             if name.startswith("test_") and callable(fn)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    _sys.exit(1 if failed else 0)
