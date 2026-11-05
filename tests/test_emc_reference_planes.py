"""EMC stackup rules find an inner reference plane by its ground or power zone fill.

Fixtures tests/fixtures/emc_planes/: four-layer 40 x 30 mm boards (prepreg 0.2 / core 1.065 /
prepreg 0.2) with a GND zone filled over In1.Cu and a CLK track on F.Cu.
signal_typed_planes.kicad_pcb also fills +3V3 over In2.Cu; both inner layers keep KiCad's
default type `signal`. mixed_small_fill.kicad_pcb types In2.Cu `mixed` but fills +3V3 over only
16.6 % of the board. The rule: an inner layer whose ground and power fill covers at least a
quarter of the board area is a plane; an inner layer with a smaller such fill is not, whatever
its type; only a layer without such fill falls back to the type (`power` / `mixed`).
SU-001 (adjacent signal layers), SU-002 (signal layer over 0.3 mm from a plane) and CK-001
(clock on an outer layer while an inner signal layer is free) all read that plane set.
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
EMC = _KH / "skills/emc/scripts/analyze_emc.py"
FIXTURES = _HARNESS / "tests/fixtures/emc_planes"


def _stackup_findings(tmp_path, board):
    pcb = tmp_path / "pcb.json"
    pcb.write_text(subprocess.run([sys.executable, str(PCB), str(FIXTURES / board)],
                                  capture_output=True, text=True, check=True).stdout,
                   encoding="utf-8")
    out = subprocess.run([sys.executable, str(EMC), "--pcb", str(pcb)],
                         capture_output=True, text=True, check=True).stdout
    return sorted((f["rule_id"], f["summary"]) for f in json.loads(out)["findings"]
                  if f.get("rule_id") in ("SU-001", "SU-002", "CK-001"))


def test_signal_typed_inner_fills_are_planes(tmp_path):
    assert _stackup_findings(tmp_path, "signal_typed_planes.kicad_pcb") == []


def test_small_fill_on_a_mixed_layer_is_not_a_plane(tmp_path):
    assert _stackup_findings(tmp_path, "mixed_small_fill.kicad_pcb") == [
        ("CK-001", "Clock CLK on outer layer"),
        ("SU-001", "Adjacent signal layers: In2.Cu, B.Cu"),
        ("SU-002", "Signal layer B.Cu far from reference plane"),
        ("SU-002", "Signal layer In2.Cu far from reference plane"),
    ]
