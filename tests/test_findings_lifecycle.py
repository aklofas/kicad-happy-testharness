"""Drift cleanup keeps resolved review observations with a disposition (ruling R9), its
apply paths run at all (code A7-F14, A7-F15), and an unresolvable check path is never
"possibly fixed" (code A7-F11)."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.unit

REPO, PROJ, SRC = "o/r", "p", "main.kicad_sch.json"


def _tree(root, checks):
    out = root / "results" / "outputs" / "schematic" / REPO / SRC
    out.parent.mkdir(parents=True)
    out.write_text(json.dumps({"findings": [{"detector": "detect_rc_filters", "ref": "R2"}]}))
    proj = root / "reference" / REPO / PROJ
    proj.mkdir(parents=True)
    finding = {"id": "FND-1", "repo": REPO, "analyzer_type": "schematic", "source_file": SRC,
               "correct": [], "missed": [],
               "incorrect": [{"description": d, "analyzer_section": "detect_rc_filters", "check": c}
                             for d, c in checks]}
    (proj / "findings.json").write_text(json.dumps({"findings": [finding]}))
    return proj / "findings.json"


GONE = ("R1 wrongly detected", {"path": "findings", "detector_filter": "detect_rc_filters",
                                "op": "not_contains_match", "field": "ref", "pattern": "^R1$"})
LEGACY = ("legacy path", {"path": "signal_analysis.rc_filters", "op": "not_contains_match",
                          "field": "ref", "pattern": "^R9$"})


def _run(root, *argv):
    env = dict(os.environ, KICAD_HAPPY_TESTHARNESS_DATA_DIR=str(root))
    p = subprocess.run([sys.executable, *argv], cwd=HARNESS, env=env, capture_output=True, text=True,
                       timeout=60)
    assert p.returncode == 0, p.stdout + p.stderr
    return p.stdout


@pytest.mark.parametrize("tool", [["regression/cleanup_drift.py", "--apply"],
                                  ["regression/refresh_findings.py", "--apply"]])
def test_apply_keeps_the_item_with_a_disposition(tmp_path, tool):
    ff = _tree(tmp_path, [GONE, LEGACY])
    _run(tmp_path, *tool)
    items = json.loads(ff.read_text())["findings"][0]["incorrect"]
    assert [i["description"] for i in items] == ["R1 wrongly detected", "legacy path"]
    assert items[0]["disposition"]["state"] == "possibly_fixed"
    assert "disposition" not in items[1]                   # unresolvable path: no claim either way
    assert (ff.parent / "findings.md").exists()


def test_drift_reports_unresolvable_and_skips_dispositioned(tmp_path):
    ff = _tree(tmp_path, [GONE, LEGACY])
    out = json.loads(_run(tmp_path, "regression/drift.py", "--all", "--json"))
    assert out["counts"]["possibly_fixed"] == 1 and out["counts"]["unresolvable"] == 1
    _run(tmp_path, "regression/cleanup_drift.py", "--apply")
    out = json.loads(_run(tmp_path, "regression/drift.py", "--all", "--json"))
    assert out["counts"]["possibly_fixed"] == 0 and out["counts"]["unresolvable"] == 1


def test_refresh_reports_no_checkable_items(tmp_path):
    ff = _tree(tmp_path, [GONE])
    data = json.loads(ff.read_text())
    for item in data["findings"][0]["incorrect"]:
        del item["analyzer_section"]
    ff.write_text(json.dumps(data))
    out = json.loads(_run(tmp_path, "regression/refresh_findings.py", "--json"))
    assert out["no_checkable_items"] == 1 and out["no_output"] == 0
    assert out["stale"] == 0


FIXTURE = HARNESS / "tests" / "fixtures" / "wave10"


def _copy_drift_root(dest):
    shutil.copytree(FIXTURE / "drift" / "reference", dest / "reference")
    shutil.copytree(FIXTURE / "drift" / "outputs", dest / "results" / "outputs")
    return dest / "reference" / "o" / "r" / "p" / "findings.json"


def _dispositions(ff):
    out = {}
    for f in json.loads(ff.read_text())["findings"]:
        out[f["id"]] = {t: [[i["disposition"]["state"], i["disposition"]["by"]] if "disposition" in i else None
                            for i in f[t]]
                        for t in ("correct", "incorrect", "missed")}
    return out


@pytest.mark.parametrize("tool", [["regression/cleanup_drift.py", "--apply"],
                                  ["regression/refresh_findings.py", "--apply"]])
def test_cleanup_and_refresh_apply_match_golden(tmp_path, tool):
    ff = _copy_drift_root(tmp_path)
    _run(tmp_path, *tool)
    golden = json.loads((FIXTURE / "drift_apply_golden.json").read_text())
    assert _dispositions(ff) == golden[tool[0]]
    kept = json.loads(ff.read_text())["findings"][0]["incorrect"][4]["disposition"]
    assert kept == {"state": "possibly_fixed", "by": "manual", "date": "2026-01-01"}
