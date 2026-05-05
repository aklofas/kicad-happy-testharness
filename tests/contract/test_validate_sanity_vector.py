"""Unit tests for validate_sanity_vector.py (Phase 3a)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = MAIN_REPO_ROOT / "skills/datasheets/scripts/validate_sanity_vector.py"
VECTOR = HARNESS_ROOT / "tests/fixtures/datasheets/sanity-vector-lm2596-adj.example.yaml"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True
    )


def _good_extraction() -> dict:
    return {
        "base": {
            "absolute_max": {
                "VIN_max": [{"max": 45, "unit": "V",
                             "evidence": {"page": 5, "section": "Abs Max", "confidence": "high", "method": "table"}}]
            },
            "recommended_operating": {
                "VIN": [{"min": 4.5, "max": 40, "unit": "V",
                         "evidence": {"page": 5, "section": "ROC", "confidence": "high", "method": "table"}}]
            }
        },
        "regulator": {
            "topology": "buck",
            "reference_voltage": [
                {"min": 1.18, "typ": 1.23, "max": 1.28, "unit": "V",
                 "evidence": {"page": 5, "section": "EC", "confidence": "high", "method": "table"}}
            ]
        }
    }


@pytest.fixture
def extraction_path(tmp_path):
    p = tmp_path / "LM2596-ADJ.json"
    p.write_text(json.dumps(_good_extraction()))
    return p


def test_passing_vector_exits_zero(extraction_path):
    res = _run(str(VECTOR), str(extraction_path))
    assert res.returncode == 0, res.stderr
    report = json.loads(res.stdout)
    assert all(f["pass"] for f in report["fields"])
    assert report["summary"]["passed"] == 4
    assert report["summary"]["failed"] == 0


def test_value_outside_tolerance_fails(tmp_path, extraction_path):
    bad = _good_extraction()
    bad["base"]["absolute_max"]["VIN_max"][0]["max"] = 30  # 33% off
    extraction_path.write_text(json.dumps(bad))
    res = _run(str(VECTOR), str(extraction_path))
    assert res.returncode == 1
    report = json.loads(res.stdout)
    diverged = [f for f in report["fields"] if not f["pass"]]
    assert len(diverged) == 1
    assert diverged[0]["path"] == "base.absolute_max.VIN_max"


def test_missing_path_reports_failure(tmp_path, extraction_path):
    bad = _good_extraction()
    bad["regulator"].pop("topology")
    extraction_path.write_text(json.dumps(bad))
    res = _run(str(VECTOR), str(extraction_path))
    assert res.returncode == 1
    report = json.loads(res.stdout)
    failed = next(f for f in report["fields"] if f["path"] == "regulator.topology")
    assert not failed["pass"]
    assert "missing" in failed["reason"].lower()


def test_enum_mismatch_fails(tmp_path, extraction_path):
    bad = _good_extraction()
    bad["regulator"]["topology"] = "boost"
    extraction_path.write_text(json.dumps(bad))
    res = _run(str(VECTOR), str(extraction_path))
    assert res.returncode == 1
    report = json.loads(res.stdout)
    failed = next(f for f in report["fields"] if f["path"] == "regulator.topology")
    assert not failed["pass"]
    assert failed["actual"] == "boost"
    assert failed["expected"] == "buck"


def test_within_tolerance_passes(tmp_path, extraction_path):
    bad = _good_extraction()
    # 4% high — within 5% tolerance
    bad["base"]["absolute_max"]["VIN_max"][0]["max"] = 45 * 1.04
    extraction_path.write_text(json.dumps(bad))
    res = _run(str(VECTOR), str(extraction_path))
    assert res.returncode == 0, res.stdout
