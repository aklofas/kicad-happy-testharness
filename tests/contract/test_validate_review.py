"""Contract tests for skills/kicad/review/scripts/validate_review.py CLI."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import subprocess
import sys
from pathlib import Path



def _run(args):
    return subprocess.run(
        [sys.executable, "skills/kicad/review/scripts/validate_review.py", *args],
        capture_output=True, text=True, cwd=MAIN_REPO_ROOT,
    )


def test_validate_review_passes_on_valid_fixture(tmp_path):
    fixture = (MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "fixtures"
               / "review_annotations.example.json")
    result = _run(["--review", str(fixture)])
    assert result.returncode == 0


def test_validate_review_fails_on_short_reason(tmp_path):
    bad = {
        "schema_version": "1.0",
        "produced_for_run_id": "x",
        "produced_at": "2026-04-27T00:00:00Z",
        "annotations": [{
            "finding_id": "sch:R-1:u1",
            "status": "confirmed",
            "reason": "too short",
            "confidence": "high",
            "reviewed_at": "2026-04-27T00:00:00Z",
        }],
        "reviewer_observations": [],
    }
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(json.dumps(bad))
    result = _run(["--review", str(bad_path)])
    assert result.returncode == 1


def test_validate_review_returns_2_on_io_error():
    result = _run(["--review", "/does/not/exist.json"])
    assert result.returncode == 2


def test_validate_review_emits_json_with_flag(tmp_path):
    fixture = (MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "fixtures"
               / "review_annotations.example.json")
    result = _run(["--review", str(fixture), "--json"])
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert parsed["valid"] is True
