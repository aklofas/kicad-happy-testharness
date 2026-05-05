"""Unit tests for validate_extraction_result.py (Phase 3a polish; harness gate Check 1)."""

from __future__ import annotations

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = MAIN_REPO_ROOT / "skills/datasheets/scripts/validate_extraction_result.py"
FIX = HARNESS_ROOT / "tests/fixtures/datasheets"
REG_OK = FIX / "result-regulator-complete.example.json"
REG_FAILED = FIX / "result-regulator-failed.example.json"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def _write_wrapper(path: Path, *, status: str = "complete", data=None, error=None) -> None:
    wrapper = {
        "task_id": "regulator",
        "schema_version": "0.3",
        "status": status,
        "extracted_at": "2026-04-25T11:00:00Z",
        "model_tier": "B",
        "model_id": "claude-sonnet-4-6",
        "data": data,
    }
    if error is not None:
        wrapper["error"] = error
    path.write_text(json.dumps(wrapper, indent=2))


def test_valid_complete_result_exits_zero():
    res = _run("--result-file", str(REG_OK), "--task-type", "regulator")
    assert res.returncode == 0, res.stderr
    assert "valid" in res.stdout.lower()


def test_failed_status_exits_one():
    res = _run("--result-file", str(REG_FAILED), "--task-type", "regulator")
    assert res.returncode == 1
    assert "status" in res.stderr.lower()


def test_schema_invalid_data_exits_one(tmp_path):
    bad = tmp_path / "bad.result.json"
    # `topology` is a required enum; "definitely-not-a-topology" should fail.
    _write_wrapper(bad, data={"topology": "definitely-not-a-topology"})
    res = _run("--result-file", str(bad), "--task-type", "regulator")
    assert res.returncode == 1
    assert "schema validation" in res.stderr.lower()


def test_missing_result_file_exits_two(tmp_path):
    res = _run(
        "--result-file",
        str(tmp_path / "does-not-exist.json"),
        "--task-type",
        "regulator",
    )
    assert res.returncode == 2
    assert "not found" in res.stderr.lower()


def test_unknown_task_type_exits_two(tmp_path):
    # Even with a valid result file, an unknown task-type has no schema → exit 2.
    res = _run(
        "--result-file",
        str(REG_OK),
        "--task-type",
        "totally-not-a-task",
    )
    assert res.returncode == 2
    assert "schema not found" in res.stderr.lower()


def test_unparseable_wrapper_exits_two(tmp_path):
    bad = tmp_path / "garbage.json"
    bad.write_text("{ not json")
    res = _run("--result-file", str(bad), "--task-type", "regulator")
    assert res.returncode == 2
    assert "not valid json" in res.stderr.lower()


def test_emit_json_shape(tmp_path):
    res = _run(
        "--result-file",
        str(REG_OK),
        "--task-type",
        "regulator",
        "--json",
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["valid"] is True
    assert payload["exit_code"] == 0
    assert payload["task_type"] == "regulator"
    assert payload["result_file"].endswith("result-regulator-complete.example.json")


def test_emit_json_on_failure(tmp_path):
    bad = tmp_path / "bad.result.json"
    _write_wrapper(bad, data={"topology": "not-an-enum"})
    res = _run(
        "--result-file",
        str(bad),
        "--task-type",
        "regulator",
        "--json",
    )
    assert res.returncode == 1
    payload = json.loads(res.stdout)
    assert payload["valid"] is False
    assert payload["exit_code"] == 1
    assert "schema validation" in payload["message"].lower()


@pytest.mark.parametrize("task_type", ["scout", "base", "pinout", "regulator"])
def test_all_phase_3a_task_types_resolve_to_a_schema(task_type):
    """Sanity: every Phase 3a task-type name maps to a schema file. Phase 3b
    will add mcu/opamp/transistor/diode/crystal — those will pick up here
    automatically when the schema files land, no code change required."""
    schema_path = MAIN_REPO_ROOT / "skills/datasheets/schemas" / f"{task_type}.schema.json"
    assert schema_path.exists(), f"missing schema for task-type {task_type!r}"
