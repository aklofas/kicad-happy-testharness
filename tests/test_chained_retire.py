"""Chained runners retire a downstream output whose upstream output is missing or quarantined
(code A3-F4): the unit is never submitted, so the old output used to stay live for run_checks."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
import utils  # noqa: E402

pytestmark = pytest.mark.unit


def test_retire_orphaned_outputs_quarantines_only_unpaired(tmp_path):
    d = tmp_path / "thermal" / "o" / "r"
    d.mkdir(parents=True)
    for n in ("a_thermal.json", "b_thermal.json", "_aggregate.json", "capability_mode.json"):
        (d / n).write_text("{}")
    retired = utils.retire_orphaned_outputs(tmp_path / "thermal", None, {"o/r": {"a_thermal.json"}})
    assert [p.name for p in retired] == ["b_thermal.json"]
    assert sorted(p.name for p in d.iterdir()) == ["_aggregate.json", "a_thermal.json",
                                                    "b_thermal.json.stale", "capability_mode.json"]


def _product(tmp_path):
    scripts = tmp_path / "product" / "skills" / "kicad" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "analyze_thermal.py").write_text("import sys; sys.exit(3)\n")
    (tmp_path / "product" / "skills" / "emc" / "scripts").mkdir(parents=True)
    return tmp_path / "product"


def test_run_thermal_retires_output_of_a_quarantined_pcb(tmp_path):
    data = tmp_path / "data"
    out = data / "results" / "outputs"
    (out / "schematic" / "o" / "r").mkdir(parents=True)
    (out / "schematic" / "o" / "r" / "b.kicad_sch.json").write_text(json.dumps({"analyzer_type": "schematic"}))
    (out / "pcb" / "o" / "r").mkdir(parents=True)
    (out / "pcb" / "o" / "r" / "b.kicad_pcb.json.stale").write_text("{}")   # pcb timed out this pass
    old = out / "thermal" / "o" / "r" / "b_thermal.json"
    old.parent.mkdir(parents=True)
    old.write_text(json.dumps({"analyzer_type": "thermal", "summary": {}}))
    env = dict(os.environ, KICAD_HAPPY_TESTHARNESS_DATA_DIR=str(data), KICAD_HAPPY_DIR=str(_product(tmp_path)))
    r = subprocess.run([sys.executable, str(HARNESS / "run" / "run_thermal.py"), "--repo", "o/r"],
                       env=env, capture_output=True, text=True, timeout=60)
    assert not old.exists() and old.with_name("b_thermal.json.stale").exists(), r.stdout + r.stderr
    assert "RETIRED o/r/b_thermal.json" in r.stdout


def test_truncated_schematic_output_still_pairs_with_its_pcb(tmp_path, monkeypatch):
    """code A3-F9 / A3-F1: a hash-truncated output name loses its .kicad_sch suffix, so the
    schematic never paired with its PCB (16 corpus boards lost EMC-with-PCB and thermal)."""
    monkeypatch.setattr(utils, "REPOS_DIR", tmp_path / "repos")
    monkeypatch.setattr(utils, "OUTPUTS_DIR", tmp_path / "outputs")
    monkeypatch.setattr(utils, "MANIFESTS_DIR", tmp_path / "manifests")
    deep = "very_long_directory_name_" * 8
    sch_in = tmp_path / "repos" / "o" / "r" / deep / "board.kicad_sch"
    pcb_in = sch_in.with_suffix(".kicad_pcb")
    sch_name, pcb_name = utils.safe_name(str(sch_in)) + ".json", utils.safe_name(str(pcb_in)) + ".json"
    assert not sch_name.endswith(".kicad_sch.json")            # the cap truncated it
    (tmp_path / "manifests" / "o" / "r").mkdir(parents=True)
    (tmp_path / "manifests" / "o" / "r" / "schematics.txt").write_text(f"{sch_in}\n")
    for kind, name in (("schematic", sch_name), ("pcb", pcb_name)):
        d = tmp_path / "outputs" / kind / "o" / "r"
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text("{}")
    sch_out = tmp_path / "outputs" / "schematic" / "o" / "r" / sch_name
    assert utils.find_pcb_output(sch_out) == tmp_path / "outputs" / "pcb" / "o" / "r" / pcb_name
