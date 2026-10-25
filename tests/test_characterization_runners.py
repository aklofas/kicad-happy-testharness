"""Characterization of runner behaviour the structural consolidation must keep (arch A1-F5):
run_analyzer's parallel + --validate + --json path, run_pcb's argv normalization, a chained
runner's happy path, and `harness.py run` step planning. All runs use a fake product and a
tmp data dir."""
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

HARNESS = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.unit

PCB_FAKE = """import json, pathlib, sys
out = sys.argv[sys.argv.index('-o') + 1]
with open(pathlib.Path(sys.argv[0]).with_name('argv.log'), 'a') as fh:   # temp files are cleaned
    fh.write(json.dumps(sys.argv[1:]) + chr(10))
json.dump({'analyzer_type': 'pcb', 'footprints': [], 'statistics': {'footprint_count': 0},
           'connectivity': {}, 'summary': {'total_findings': 0}, 'findings': []}, open(out, 'w'))
"""
EMC_FAKE = """import json, sys
out = sys.argv[sys.argv.index('--output') + 1]
json.dump({'analyzer_type': 'emc', 'summary': {'total_findings': 1, 'by_severity': {'warning': 1}},
           'findings': [{'rule_id': 'X-1', 'severity': 'warning'}]}, open(out, 'w'))
"""


def _git(path, *args):
    subprocess.run(["git", "-C", str(path), "-c", "user.email=t@t", "-c", "user.name=t", *args],
                   check=True, capture_output=True)


def _product(tmp_path):
    prod = tmp_path / "product"
    (prod / "skills" / "kicad" / "scripts").mkdir(parents=True)
    (prod / "skills" / "emc" / "scripts").mkdir(parents=True)
    (prod / "skills" / "kicad" / "scripts" / "analyze_pcb.py").write_text(PCB_FAKE)
    (prod / "skills" / "emc" / "scripts" / "analyze_emc.py").write_text(EMC_FAKE)
    _git(prod, "init", "-q")
    _git(prod, "add", "-A")
    _git(prod, "commit", "-q", "-m", "x")
    return prod


def _data(tmp_path, boards=("a.kicad_pcb", "b.kicad_pcb")):
    data = tmp_path / "data"
    repo = data / "repos" / "o" / "r"
    repo.mkdir(parents=True)
    paths = []
    for b in boards:
        (repo / b).write_text("(kicad_pcb)")
        paths.append(str(repo / b))
    (data / "results" / "manifests").mkdir(parents=True)
    (data / "results" / "manifests" / "all_pcbs.txt").write_text("\n".join(paths) + "\n")
    return data


def _env(tmp_path, data, prod):
    return dict(os.environ, KICAD_HAPPY_TESTHARNESS_DATA_DIR=str(data), KICAD_HAPPY_DIR=str(prod))


def test_run_pcb_parallel_validate_json_and_argv(tmp_path):
    prod, data = _product(tmp_path), _data(tmp_path)
    r = subprocess.run([sys.executable, str(HARNESS / "run" / "run_pcb.py"), "--repo", "o/r",
                        "--jobs", "2", "--validate", "--json", "--no-proximity"],
                       cwd=HARNESS, env=_env(tmp_path, data, prod), capture_output=True, text=True,
                       timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    summary = json.loads(r.stdout.strip().splitlines()[-1])
    assert summary["type"] == "pcb" and summary["total"] == summary["passed"] == 2
    argv = json.loads((prod / "skills" / "kicad" / "scripts" / "argv.log").read_text().splitlines()[0])
    assert "--full" in argv and "--proximity" not in argv          # default --full kept, opt-out honoured
    manifest = json.loads((data / "results" / "outputs" / "pcb" / "manifest.json").read_text())
    assert manifest["totals"]["ok"] == 2 and manifest["expected_census"] == {"pcb": 2}


def test_chained_emc_happy_path(tmp_path):
    prod, data = _product(tmp_path), tmp_path / "data"
    sch = data / "results" / "outputs" / "schematic" / "o" / "r"
    sch.mkdir(parents=True)
    (sch / "a.kicad_sch.json").write_text(json.dumps({"analyzer_type": "schematic"}))
    r = subprocess.run([sys.executable, str(HARNESS / "run" / "run_emc.py"), "--repo", "o/r", "--jobs", "1"],
                       cwd=HARNESS, env=_env(tmp_path, data, prod), capture_output=True, text=True,
                       timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    emc = data / "results" / "outputs" / "emc"
    assert json.loads((emc / "o" / "r" / "a.kicad_sch.json").read_text())["analyzer_type"] == "emc"
    agg = json.loads((emc / "_aggregate.json").read_text())
    assert agg["total_files"] == 1 and agg["errors"] == 0 and agg["retired"] == 0


def test_harness_run_plans_every_step_for_the_selection(monkeypatch):
    sys.path.insert(0, str(HARNESS))
    import harness
    calls = []
    monkeypatch.setattr(harness, "_run", lambda cmd, desc, timeout=600: calls.append((desc, cmd)) or True)
    args = SimpleNamespace(smoke=False, cross_section=None, repo="o/r", all_repos=False, resume=False,
                           skip_spice=False, skip_emc=False, continue_on_error=False)
    assert harness.cmd_run(args) is True
    descs = [d for d, _ in calls]
    assert descs == ["Unit tests", "Analyzer: run_schematic", "Analyzer: run_pcb", "Analyzer: run_gerbers",
                     "SPICE simulations", "EMC analysis", "Assertion checks"]
    assert all(cmd[-2:] == ["--repo", "o/r"] for d, cmd in calls[1:])
