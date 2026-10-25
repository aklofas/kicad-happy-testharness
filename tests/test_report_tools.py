"""Report tools: owner/repo identity in analytics, intersected duplicate clusters, flat SPICE
results in batch review (code A5-F12 A5-F13 A5-F14)."""
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS / "tools"))
sys.path.insert(0, str(HARNESS))

pytestmark = pytest.mark.unit


def test_analytics_groups_findings_by_owner_repo(tmp_path, monkeypatch):
    import generate_analytics as ga
    for proj in ("o/r/p1", "o/r/p2", "o/s/p1"):
        d = tmp_path / proj
        d.mkdir(parents=True)
        (d / "findings.json").write_text(json.dumps({"findings": [{"status": "x"}]}))
    monkeypatch.setattr(ga, "REFERENCE_DIR", tmp_path)
    _, _, _, by_repo = ga.collect_findings_data()
    assert by_repo == {"o/r": 2, "o/s": 1}


def test_duplicate_cluster_needs_both_signals():
    import detect_duplicates as dd
    fp_groups = {"f1": ["a", "b", "c"]}
    name_groups = {"n1": ["a", "b"], "n2": ["c", "d"]}
    clusters = dd.cross_reference(fp_groups, name_groups)
    assert ["a", "b"] in clusters and not any("c" in c and "a" in c for c in clusters)


def test_batch_review_attaches_flat_spice_results():
    """A flat simulation_results list (no per-item "simulations") counts as content."""
    src = (HARNESS / "tools" / "batch_review.py").read_text()
    assert "s.get(\"simulations\", [])" not in src


def test_analytics_collectors_read_the_relocated_data_root(tmp_path):
    """The collectors follow KICAD_HAPPY_TESTHARNESS_DATA_DIR for reference/ and results/."""
    import os
    import subprocess
    proj = tmp_path / "reference" / "o" / "r" / "p"
    (proj / "assertions" / "schematic").mkdir(parents=True)
    (proj / "assertions" / "schematic" / "a.json").write_text(
        json.dumps({"assertions": [{"id": "SEED-1"}, {"id": "STRUCT-1"}]}))
    out = tmp_path / "results" / "outputs" / "spice"
    out.mkdir(parents=True)
    (out / "_aggregate.json").write_text(json.dumps({"marker": 1}))
    code = ("import json, generate_analytics as ga;"
            "a = ga.collect_assertion_data();"
            "print(json.dumps([str(ga.REFERENCE_DIR), str(ga.RESULTS_DIR), str(a)]))")
    env = dict(os.environ, KICAD_HAPPY_TESTHARNESS_DATA_DIR=str(tmp_path),
               PYTHONPATH=str(HARNESS / "tools"))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                       env=env, cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    ref, res, data = json.loads(r.stdout.strip().splitlines()[-1])
    assert ref == str(tmp_path / "reference")
    assert res == str(tmp_path / "results")
    assert "'SEED': 1" in data and "'STRUCT': 1" in data
