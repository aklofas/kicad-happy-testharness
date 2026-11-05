"""KO-001 under a keepout that names a net — a KiCad rule area can carry a net, but
KiCad does not exempt that net's vias from a vias-restricted keepout (kicad-cli 10.0.7
DRC reports both vias), so KO-001 flags every through via inside it and no finding
carries a `keepout_allowed_net` key. No corpus board exercises this: 0 of 23,336
keepout zones carry a net, so the case is covered here by a synthetic board.
Fixtures: tests/fixtures/ko001/ — two vias inside a vias-restricted keepout, one on
the keepout's net ANT and one on GND, plus a GND via outside it.
"""
TIER = "unit"

import json
import subprocess
import sys
from pathlib import Path
from tests.product_root import PRODUCT_ROOT  # noqa: E402

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(str(PRODUCT_ROOT))
PCB = _KH / "skills/kicad/scripts/analyze_pcb.py"
FIXTURES = _HARNESS / "tests/fixtures/ko001"


def _ko001(name):
    out = subprocess.run([sys.executable, str(PCB), str(FIXTURES / name)],
                         capture_output=True, text=True, check=True)
    return [f for f in json.loads(out.stdout)["findings"] if f.get("rule_id") == "KO-001"]


def test_via_on_the_keepouts_net_is_not_exempt():
    findings = _ko001("antenna_keepout.kicad_pcb")
    assert sorted((f["via_x"], f["via_y"]) for f in findings) == [(110.0, 110.0), (112.0, 110.0)]
    assert {f["keepout_name"] for f in findings} == {"antenna_keepout"}
    assert not any("keepout_allowed_net" in f for f in findings)


def test_same_board_without_a_net_flags_both_vias():
    findings = _ko001("plain_keepout.kicad_pcb")
    assert sorted((f["via_x"], f["via_y"]) for f in findings) == [(110.0, 110.0), (112.0, 110.0)]
    assert not any("keepout_allowed_net" in f for f in findings)
