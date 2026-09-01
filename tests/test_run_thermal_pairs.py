"""TH-051: dual-format twins must not race on one thermal output file.

X.kicad_sch.json and X.sch.json (the same board analyzed in both formats)
both strip to {stem}_thermal.json. Under --jobs N two workers wrote that
file concurrently, tearing it; find_thermal_pairs now keeps only the first
twin (sorted order prefers the modern .kicad_sch format).
"""

TIER = "unit"

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "run"))

import utils
from run_thermal import find_thermal_pairs, thermal_output_stem


def test_thermal_output_stem_twins_collide_by_design():
    assert thermal_output_stem("board.kicad_sch.json") == "board"
    assert thermal_output_stem("board.sch.json") == "board"
    assert thermal_output_stem("weird.json") == "weird.json"


def test_find_thermal_pairs_dedupes_dual_format_twins():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        sch_dir = td / "schematic" / "owner" / "repo"
        pcb_dir = td / "pcb" / "owner" / "repo"
        sch_dir.mkdir(parents=True)
        pcb_dir.mkdir(parents=True)
        for name in ("board.kicad_sch.json", "board.sch.json",
                     "other.kicad_sch.json"):
            (sch_dir / name).write_text(json.dumps({"findings": []}))
        for name in ("board.kicad_pcb.json", "other.kicad_pcb.json"):
            (pcb_dir / name).write_text(json.dumps({"findings": []}))
        saved = utils.OUTPUTS_DIR
        try:
            utils.OUTPUTS_DIR = td
            pairs = find_thermal_pairs()
        finally:
            utils.OUTPUTS_DIR = saved
        sch_names = sorted(p[0].name for p in pairs)
        assert sch_names == ["board.kicad_sch.json", "other.kicad_sch.json"], sch_names


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
