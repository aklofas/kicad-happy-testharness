"""Hot loop measured pad to pad (`analyze_pcb --schematic`) on a real board file, then graded
by EMC SW-003.

Fixture tests/fixtures/hotloop/: buck.kicad_pcb places input cap C1 (VIN/GND), regulator U1
(VIN/SW/GND) and inductor L1 (SW/VOUT) so the six hot-loop pads span a 12 x 10 mm rectangle;
buck_schematic.json is the minimal schematic analysis naming U1 as a switching regulator with
L1 and C1. Without --schematic the PCB output has no loop records and EMC falls back to the
part-centre triangle (35 mm^2 here), which it reports as an ungraded info estimate.
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
FIXTURES = _HARNESS / "tests/fixtures/hotloop"
BOARD = FIXTURES / "buck.kicad_pcb"
SCHEMATIC = FIXTURES / "buck_schematic.json"


def _pcb(tmp_path, with_schematic):
    args = [sys.executable, str(PCB), str(BOARD)]
    if with_schematic:
        args += ["--schematic", str(SCHEMATIC)]
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    path = tmp_path / ("pcb_sch.json" if with_schematic else "pcb.json")
    path.write_text(out, encoding="utf-8")
    return json.loads(out), path


def _sw003(pcb_path):
    out = subprocess.run([sys.executable, str(EMC), "--schematic", str(SCHEMATIC), "--pcb", str(pcb_path)],
                         capture_output=True, text=True, check=True).stdout
    return [f for f in json.loads(out)["findings"] if f.get("rule_id") == "SW-003"]


def test_pad_loop_from_board_pads(tmp_path):
    pcb, _ = _pcb(tmp_path, with_schematic=True)
    [loop] = pcb["switching_loop_areas"]
    assert loop["method"] == "pad"
    assert loop["area_mm2"] == 120.0
    assert loop["loop_pads"] == ["C1.1", "U1.1", "U1.2", "L1.1", "U1.3", "C1.2"]
    assert loop["vertices_mm"][0] == [101.0, 111.0]


def test_sw003_grades_the_pad_loop(tmp_path):
    _, path = _pcb(tmp_path, with_schematic=True)
    [f] = _sw003(path)
    assert f["severity"] == "error"
    assert "120mm" in f["description"] and "measured through the pads" in f["description"]


def test_without_schematic_the_centre_estimate_is_not_graded(tmp_path):
    pcb, path = _pcb(tmp_path, with_schematic=False)
    assert not pcb.get("switching_loop_areas")
    [f] = _sw003(path)
    assert f["severity"] == "info"
    assert f["summary"] == "Hot loop for U1 not graded: estimated from part centres"
    assert "about 35mm" in f["description"]
