"""Multi-unit symbol fixture — a placed symbol with unit > 1. No other fixture has one, so
product tests that pin per-unit model records had nothing to read (TH-102).
Fixture: tests/fixtures/multi-unit/dual_opamp.kicad_sch — U1 (LM358) placed as unit 1
(voltage follower), unit 2 (non-inverting gain stage with R1/R2) and unit 3 (supply pins).
"""
TIER = "unit"

import json
import subprocess
import sys
from pathlib import Path
from tests.product_root import PRODUCT_ROOT  # noqa: E402

_HARNESS = Path(__file__).resolve().parent.parent
SCH = Path(str(PRODUCT_ROOT)) / "skills/kicad/scripts/analyze_schematic.py"
FIXTURE = _HARNESS / "tests/fixtures/multi-unit/dual_opamp.kicad_sch"


def _analyze(tmp_path):
    out = tmp_path / "dual_opamp.json"
    subprocess.run([sys.executable, str(SCH), str(FIXTURE), "-o", str(out)],
                   capture_output=True, text=True, check=True, cwd=tmp_path)
    return json.loads(out.read_text(encoding="utf-8"))


def test_each_placed_unit_is_a_component_record_of_one_part(tmp_path):
    d = _analyze(tmp_path)
    assert sorted((c["reference"], c["unit"]) for c in d["components"]) == [
        ("R1", 1), ("R2", 1), ("U1", 1), ("U1", 2), ("U1", 3)]
    assert d["statistics"]["total_components"] == 3


def test_pins_of_every_unit_join_their_nets(tmp_path):
    nets = _analyze(tmp_path)["nets"]
    pins = {name: sorted((p["component"], p["pin_number"]) for p in net["pins"])
            for name, net in nets.items()}
    assert pins == {
        "SIG_IN": [("U1", "3")],
        "BUF_OUT": [("U1", "1"), ("U1", "2"), ("U1", "5")],
        "FB": [("R1", "2"), ("R2", "1"), ("U1", "6")],
        "AMP_OUT": [("R1", "1"), ("U1", "7")],
        "+5V": [("U1", "8")],
        "GND": [("R2", "2"), ("U1", "4")],
    }
