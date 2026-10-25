"""Pins how check_assertions (adoption counts) and the run_checks CLI count and report the
same data root: outputs present, missing, unparsable, and an unreadable assertion file."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.unit

REPO = "o/r"


def _check(op_value, **kw):
    return {"path": "findings", "detector_filter": "detect_rc_filters", "op": "min_count",
            "value": op_value, **kw}


def _assertion(aid, value, **extra):
    return {"id": aid, "description": f"desc {aid}", "check": _check(value), **extra}


def _project(root, name, file_pattern, assertions, raw=None):
    proj = root / "reference" / REPO / name
    (proj / "baselines").mkdir(parents=True)
    (proj / "baselines" / "metadata.json").write_text(json.dumps({"project_path": "."}))
    adir = proj / "assertions" / "schematic"
    adir.mkdir(parents=True)
    body = raw if raw is not None else json.dumps(
        {"file_pattern": file_pattern, "analyzer_type": "schematic", "assertions": assertions})
    (adir / f"{file_pattern}.json").write_text(body)


def _output(root, file_pattern, text):
    out = root / "results" / "outputs" / "schematic" / REPO / f"{file_pattern}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)


@pytest.fixture
def data_root(tmp_path):
    out = {"findings": [{"detector": "detect_rc_filters", "ref": "R1"}]}
    pre = {"era": "pre-v1.4", "tagged_by_rule": "RC-001",
           "tagged_at": "2026-01-01T00:00:00Z", "tagged_reason": "r"}
    # A: output present
    _project(tmp_path, "pa", "a.kicad_sch", [
        _assertion("A-PASS", 1), _assertion("A-FAIL", 5),
        _assertion("A-ASP", 5, aspirational=True),
        _assertion("A-PRE", 1, schema_era=pre)])
    _output(tmp_path, "a.kicad_sch", json.dumps(out))
    # B: no output file
    _project(tmp_path, "pb", "b.kicad_sch", [
        _assertion("B-1", 1), _assertion("B-2", 1), _assertion("B-ASP", 1, aspirational=True)])
    # C: unparsable assertion file
    _project(tmp_path, "pc", "c.kicad_sch", [], raw="{not json")
    # D: output exists but is not JSON
    _project(tmp_path, "pd", "d.kicad_sch", [_assertion("D-1", 1)])
    _output(tmp_path, "d.kicad_sch", "garbage")
    return tmp_path


def _env(root):
    return dict(os.environ, KICAD_HAPPY_TESTHARNESS_DATA_DIR=str(root))


def test_check_assertions_counts(data_root):
    code = ("import run_checks, json; from utils import DATA_DIR; "
            "print(json.dumps(run_checks.check_assertions(DATA_DIR)))")
    p = subprocess.run([sys.executable, "-c", code], cwd=HARNESS / "regression",
                       env={**_env(data_root), "PYTHONPATH": str(HARNESS)},
                       capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stderr
    result = json.loads(p.stdout)
    # era is not filtered here: A-PRE counts; aspirational sets are skipped; the unreadable
    # file adds an error but no total
    assert result == {"total": 6, "passed": 2, "failed": 1, "errors": 4}


def test_cli_json_counts_and_error_records(data_root):
    p = subprocess.run([sys.executable, "regression/run_checks.py", "--json", "--jobs", "1"],
                       cwd=HARNESS, env=_env(data_root), capture_output=True, text=True, timeout=60)
    assert p.returncode != 0
    out = json.loads(p.stdout)
    # default era drops A-PRE; the CLI counts load errors separately from errors
    assert (out["total"], out["passed"], out["failed"], out["errors"], out["load_errors"]) == (5, 1, 1, 3, 1)
    assert out["aspirational"] == {"total": 2, "passed": 0, "failed": 2}
    by_id = {r["id"]: r for r in out["results"]}
    assert "A-PRE" not in by_id
    assert by_id["A-PASS"]["passed"] and not by_id["A-FAIL"]["passed"]
    assert by_id["B-1"]["error"] == "output file not found"
    assert by_id["B-ASP"]["error"] == "output file not found" and by_id["B-ASP"]["aspirational"]
    assert by_id["B-1"]["repo"] == REPO and by_id["B-1"]["description"] == "desc B-1"
    parse = by_id["D-1"]
    assert parse["error"].startswith("JSON parse error: ")
    assert set(parse) == {"file", "id", "passed", "error", "aspirational"}   # no repo/project/description
    unreadable = by_id["<assertion file>"]
    assert unreadable["error"].startswith("assertion file unreadable: JSONDecodeError")
    assert unreadable["passed"] is False
