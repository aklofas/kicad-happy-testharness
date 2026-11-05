"""Gerber copper extents and outline closure on two small hand-written Gerber sets.

Fixtures (each a 10 mm square board, copper drawn inside it at 2..8 mm):
tests/fixtures/gerber_parked_move/: F.Cu first moves (D02) to (100, 100) mm, then draws inside
the board. A D02 move deposits nothing, so it does not grow the layer's extents and GR-002
(copper outside the outline) stays silent; the extents are the drawn copper only.
tests/fixtures/gerber_duplicate_edge/: Edge.Cuts draws three sides as an open polyline, then
draws the bottom edge a second time. A duplicated segment does not close a loop, so GR-005
(board outline not closed) fires.
"""
TIER = "unit"

import json
import subprocess
import sys
from pathlib import Path
from tests.product_root import PRODUCT_ROOT  # noqa: E402

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(str(PRODUCT_ROOT))
GERBERS = _KH / "skills/kicad/scripts/analyze_gerbers.py"
FIXTURES = _HARNESS / "tests/fixtures"


def _analysis(name):
    out = subprocess.run([sys.executable, str(GERBERS), str(FIXTURES / name)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def _rules(analysis, rule_id):
    return [f for f in analysis["findings"] if f.get("rule_id") == rule_id]


def test_parked_move_does_not_grow_copper_extents():
    analysis = _analysis("gerber_parked_move")
    assert analysis["alignment"]["aligned"] is True
    assert analysis["alignment"]["layer_extents"]["F.Cu"] == {"width": 6.0, "height": 6.0}
    assert _rules(analysis, "GR-002") == []


def test_duplicated_edge_leaves_the_outline_open():
    [f] = _rules(_analysis("gerber_duplicate_edge"), "GR-005")
    assert f["severity"] == "error"
    assert f["summary"] == "Board outline is not closed — 4 draw(s) form no closed loop"
