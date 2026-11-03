"""KH-795 (GitHub #60.3) — a high-speed trace over a split between two plane nets.

Fixtures (tests/fixtures/kh795_split/, built with the product's return-path test helpers):
CLK on F.Cu crosses B.Cu planes +3V3 (x 0-9.5) and +5V (x 10.5-20). `analyze_pcb --full`
records one reference-plane change at the gap and EMC GP-001 reports the crossing; with a
capacitor joining +3V3 and +5V within 5 mm of the crossing (split_clk_bridged) the change is
still recorded but GP-001 stays quiet.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.product_root import PRODUCT_ROOT, ensure_import_paths

pytestmark = pytest.mark.unit

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "kh795_split"
PCB = Path(str(PRODUCT_ROOT)) / "skills" / "kicad" / "scripts" / "analyze_pcb.py"
SPLIT = "Signal crosses a split between reference planes"


def _pcb(name: str, tmp_path: Path) -> dict:
    out = tmp_path / f"{name}.json"
    r = subprocess.run([sys.executable, str(PCB), str(FIXTURES / f"{name}.kicad_pcb"), "--full",
                        "--output", str(out)], capture_output=True, text=True, timeout=120,
                       cwd=str(tmp_path))
    assert r.returncode == 0, r.stderr[-2000:]
    return json.loads(out.read_text(encoding="utf-8"))


def _split_findings(pcb: dict) -> list:
    ensure_import_paths("emc")
    from emc_rules import check_return_path_coverage
    return [f for f in check_return_path_coverage(pcb) if f.get("summary") == SPLIT]


def test_split_crossing_is_recorded_and_reported(tmp_path):
    pcb = _pcb("split_clk", tmp_path)
    [change] = pcb["reference_plane_changes"]
    assert (change["net"], change["layer"], change["reference_layer"]) == ("CLK", "F.Cu", "B.Cu")
    assert {change["net_a"], change["net_b"]} == {"+3V3", "+5V"}
    assert 9.5 <= change["x"] <= 10.5
    assert pcb["return_path_continuity"] == []
    [f] = _split_findings(pcb)
    assert f["rule_id"] == "GP-001" and f["nets"] == ["CLK"]


def test_bridging_capacitor_suppresses_the_finding(tmp_path):
    pcb = _pcb("split_clk_bridged", tmp_path)
    assert len(pcb["reference_plane_changes"]) == 1
    assert _split_findings(pcb) == []
