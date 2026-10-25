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
