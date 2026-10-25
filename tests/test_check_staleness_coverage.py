"""check_staleness coverage counts an output only when an executable current-era assertion set
resolves to that same file (code A2-F11, ruling R10)."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.unit

REPO = "o/r"


def _project(root, name, project_path, assertions):
    proj = root / "reference" / REPO / name
    (proj / "baselines").mkdir(parents=True)
    (proj / "baselines" / "metadata.json").write_text(json.dumps({"project_path": project_path}))
    (proj / "assertions" / "schematic").mkdir(parents=True)
    (proj / "assertions" / "schematic" / "main.kicad_sch.json").write_text(json.dumps(
        {"file_pattern": "main.kicad_sch", "analyzer_type": "schematic", "assertions": assertions}))


def _uncovered(root):
    out = root / "results" / "outputs" / "schematic" / REPO
    env = dict(os.environ, KICAD_HAPPY_TESTHARNESS_DATA_DIR=str(root))
    code = ("import sys, json; sys.path.insert(0, {h!r}); sys.path.insert(0, {r!r});"
            "import check_staleness as cs;"
            "print(json.dumps(sorted(Path(u['output_file']).name for u in "
            "cs.find_uncovered_outputs(cs.DATA_DIR, repo_name={repo!r}, analyzer_type='schematic'))))"
            ).format(h=str(HARNESS), r=str(HARNESS / "regression"), repo=REPO)
    code = "from pathlib import Path;" + code
    p = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stderr
    assert out.is_dir()
    return json.loads(p.stdout)


LOCK = {"id": "S1", "check": {"path": "statistics.total_components", "op": "min_count", "value": 1}}


def test_same_basename_in_another_project_is_not_covered(tmp_path):
    _project(tmp_path, "a", "hw/a", [LOCK])
    out = tmp_path / "results" / "outputs" / "schematic" / REPO
    out.mkdir(parents=True)
    for name in ("hw_a_main.kicad_sch.json", "hw_b_main.kicad_sch.json"):
        (out / name).write_text("{}")
    assert _uncovered(tmp_path) == ["hw_b_main.kicad_sch.json"]


def test_empty_or_aspirational_or_other_era_sets_do_not_cover(tmp_path):
    _project(tmp_path, "a", "hw/a", [])
    _project(tmp_path, "b", "hw/b", [dict(LOCK, aspirational=True)])
    _project(tmp_path, "c", "hw/c", [dict(LOCK, schema_era="pre-v1.4")])
    _project(tmp_path, "d", "hw/d", [LOCK])
    out = tmp_path / "results" / "outputs" / "schematic" / REPO
    out.mkdir(parents=True)
    for p in "abcd":
        (out / f"hw_{p}_main.kicad_sch.json").write_text("{}")
    assert _uncovered(tmp_path) == ["hw_a_main.kicad_sch.json", "hw_b_main.kicad_sch.json",
                                    "hw_c_main.kicad_sch.json"]
