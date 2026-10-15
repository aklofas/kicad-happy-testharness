"""TH-069: discover_in lists only regular files as schematic/pcb/project units.

A gerber export folder named `<board> 2.kicad_pcb` (BrettHallen/Conversion_Boards) was
listed as a pcb unit; analyze_pcb refused it with exit 2 and the baseline ledger carried
the crash as product debt."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import discover  # noqa: E402

pytestmark = pytest.mark.unit


def test_discover_in_skips_directories_named_like_units(tmp_path):
    (tmp_path / "board.kicad_pcb").write_text("(kicad_pcb)")
    (tmp_path / "board 2.kicad_pcb").mkdir()
    (tmp_path / "board 2.kicad_pcb" / "F_Cu.gbr").write_text("G04*")
    (tmp_path / "board.kicad_sch").write_text("(kicad_sch)")
    (tmp_path / "old.kicad_sch").mkdir()
    (tmp_path / "board.kicad_pro").write_text("{}")
    (tmp_path / "x.kicad_pro").mkdir()
    found = discover.discover_in(tmp_path)
    assert [Path(p).name for p in found["pcbs"]] == ["board.kicad_pcb"]
    assert [Path(p).name for p in found["schematics"]] == ["board.kicad_sch"]
    assert [Path(p).name for p in found["projects"]] == ["board.kicad_pro"]
    assert found["gerbers"] == [str(tmp_path / "board 2.kicad_pcb")]
