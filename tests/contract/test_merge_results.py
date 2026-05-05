"""Unit tests for merge_results.py (Phase 3a)."""

from __future__ import annotations

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCRIPT = MAIN_REPO_ROOT / "skills/datasheets/scripts/merge_results.py"
FIX = HARNESS_ROOT / "tests/fixtures/datasheets"
PLAN_FIX = FIX / "plan-lm2596-adj.example.json"
SCOUT_FIX = FIX / "scout-lm2596-adj.example.json"
REG_RESULT_FIX = FIX / "result-regulator-complete.example.json"
SCHEMA_DIR = MAIN_REPO_ROOT / "skills/datasheets/schemas"
EXTRACTION_SCHEMA = SCHEMA_DIR / "extraction.schema.json"


def _build_registry() -> Registry:
    """Build a referencing Registry so $ref between schemas resolves."""
    registry = Registry()
    for schema_path in SCHEMA_DIR.glob("*.schema.json"):
        schema = json.loads(schema_path.read_text())
        uri = schema.get("$id")
        if uri:
            registry = registry.with_resource(uri, Resource.from_contents(schema))
    return registry


def _build_base_result(task_id: str = "base") -> dict:
    """Minimal base result that satisfies base.schema.json."""
    return {
        "task_id": task_id,
        "schema_version": "1.0",
        "status": "complete",
        "extracted_at": "2026-04-25T11:00:00Z",
        "model_tier": "B",
        "model_id": "claude-sonnet-4-6",
        "data": {
            "family": "step-down switching regulator",
            "package": {
                "code": "TO-263-5",
                "pin_count": 5,
                "pitch_mm": None,
                "body_mm": None,
                "thermal_pad": True,
                "evidence": {
                    "page": 1,
                    "section": "Features",
                    "confidence": "high",
                    "method": "prose",
                },
            },
            "thermal": {},
            "absolute_max": {},
            "recommended_operating": {},
            "esd": {},
            "moisture_sensitivity": None,
            "compliance": [],
            "pinout": [],
            "pin_relationships": [],
        },
    }


def _build_pinout_result() -> dict:
    return {
        "task_id": "pinout",
        "schema_version": "1.0",
        "status": "complete",
        "extracted_at": "2026-04-25T11:00:00Z",
        "model_tier": "A",
        "model_id": "claude-opus-4-7",
        "data": [
            {
                "numbers": ["1"],
                "name": "VIN",
                "type": "power_in",
                "subtype": None,
                "description": "Input voltage",
                "power_domain": "VIN",
                "alt_functions": [],
                "is_5v_tolerant": None,
                "absolute_max": None,
                "recommended": None,
                "drive_strength": None,
                "notes": None,
                "evidence": {
                    "page": 3,
                    "section": "Pin Configuration",
                    "confidence": "high",
                    "method": "table",
                },
            }
        ],
    }


@pytest.fixture
def workdir(tmp_path):
    cache = tmp_path / "datasheets" / "extracted"
    cache.mkdir(parents=True)
    plan = json.loads(PLAN_FIX.read_text())
    plan["cache_dir"] = str(cache)
    (cache / "LM2596-ADJ.plan.json").write_text(json.dumps(plan, indent=2))
    (cache / "LM2596-ADJ.scout.json").write_text(SCOUT_FIX.read_text())
    (cache / "LM2596-ADJ.base.result.json").write_text(
        json.dumps(_build_base_result(), indent=2)
    )
    (cache / "LM2596-ADJ.pinout.result.json").write_text(
        json.dumps(_build_pinout_result(), indent=2)
    )
    (cache / "LM2596-ADJ.regulator.result.json").write_text(REG_RESULT_FIX.read_text())
    return tmp_path, cache


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_merge_writes_extraction_json(workdir):
    tmp, cache = workdir
    res = _run("LM2596-ADJ", "--cache-dir", str(cache))
    assert res.returncode == 0, res.stderr
    out = json.loads((cache / "LM2596-ADJ.json").read_text())
    assert out["source"]["mpn"] == "LM2596-ADJ"
    assert out["base"]["package"]["code"] == "TO-263-5"
    assert out["regulator"]["topology"] == "buck"
    assert "regulator" in out["categories"]


def test_merged_extraction_validates_against_schema(workdir):
    tmp, cache = workdir
    _run("LM2596-ADJ", "--cache-dir", str(cache))
    out = json.loads((cache / "LM2596-ADJ.json").read_text())
    schema = json.loads(EXTRACTION_SCHEMA.read_text())
    registry = _build_registry()
    validator = Draft202012Validator(schema, registry=registry)
    errors = sorted(validator.iter_errors(out), key=lambda e: list(e.absolute_path))
    assert errors == [], "\n".join(
        f"{list(e.absolute_path)}: {e.message}" for e in errors
    )


def test_merge_records_outcomes_in_plan(workdir):
    tmp, cache = workdir
    _run("LM2596-ADJ", "--cache-dir", str(cache))
    plan = json.loads((cache / "LM2596-ADJ.plan.json").read_text())
    by = {o["task_id"]: o for o in plan["execution"]["outcomes"]}
    assert by["base"]["final_status"] == "complete"
    assert by["regulator"]["final_status"] == "complete"
    assert plan["execution"]["completed_at"] is not None


def test_merge_writes_quality_score_field(workdir):
    tmp, cache = workdir
    _run("LM2596-ADJ", "--cache-dir", str(cache))
    out = json.loads((cache / "LM2596-ADJ.json").read_text())
    assert "quality_score" in out["extraction"]
    score = out["extraction"]["quality_score"]
    assert score is not None
    assert 0 <= score <= 100
    # LM2596-ADJ happy-path fixture should comfortably pass the 60-floor
    assert score >= 60, f"score {score} below 60-floor; rubric or fixture out of sync"


FAILED_FIX = FIX / "result-regulator-failed.example.json"


def _bad_schema_result() -> dict:
    """status:complete but data violates regulator schema (missing topology)."""
    return {
        "task_id": "regulator",
        "schema_version": "0.3",
        "status": "complete",
        "extracted_at": "2026-04-25T11:00:00Z",
        "model_tier": "B",
        "model_id": "claude-sonnet-4-6",
        "data": {"vin_range": None},  # missing required `topology`
    }


def test_failed_status_triggers_retry_signal(workdir):
    tmp, cache = workdir
    (cache / "LM2596-ADJ.regulator.result.json").write_text(FAILED_FIX.read_text())
    res = _run("LM2596-ADJ", "--cache-dir", str(cache))
    assert res.returncode == 1
    plan = json.loads((cache / "LM2596-ADJ.plan.json").read_text())
    o = next(o for o in plan["execution"]["outcomes"] if o["task_id"] == "regulator")
    assert o["final_status"] == "failed"
    assert o["attempts"] == 1
    assert "unable to locate" in (o["last_error"] or "")


def test_schema_invalid_data_triggers_retry_signal(workdir):
    tmp, cache = workdir
    (cache / "LM2596-ADJ.regulator.result.json").write_text(json.dumps(_bad_schema_result()))
    res = _run("LM2596-ADJ", "--cache-dir", str(cache))
    assert res.returncode == 1
    plan = json.loads((cache / "LM2596-ADJ.plan.json").read_text())
    o = next(o for o in plan["execution"]["outcomes"] if o["task_id"] == "regulator")
    assert o["final_status"] == "failed"
    assert "schema validation" in (o["last_error"] or "")


def test_retry_failed_with_still_failing_writes_partial_sentinel(workdir):
    tmp, cache = workdir
    (cache / "LM2596-ADJ.regulator.result.json").write_text(FAILED_FIX.read_text())
    _run("LM2596-ADJ", "--cache-dir", str(cache))                          # first attempt
    res = _run("LM2596-ADJ", "--cache-dir", str(cache), "--retry-failed")  # still failing
    assert res.returncode == 0
    out = json.loads((cache / "LM2596-ADJ.json").read_text())
    assert out["regulator"] == {
        "_extraction_failed": True,
        "reason": "Subagent reported: 'unable to locate Electrical Characteristics table on requested pages'",
    }
    plan = json.loads((cache / "LM2596-ADJ.plan.json").read_text())
    o = next(o for o in plan["execution"]["outcomes"] if o["task_id"] == "regulator")
    assert o["final_status"] == "partial"
    assert o["attempts"] == 2


def test_retry_failed_with_now_passing_completes_cleanly(workdir):
    tmp, cache = workdir
    (cache / "LM2596-ADJ.regulator.result.json").write_text(FAILED_FIX.read_text())
    _run("LM2596-ADJ", "--cache-dir", str(cache))                          # first attempt: fail
    (cache / "LM2596-ADJ.regulator.result.json").write_text(REG_RESULT_FIX.read_text())  # repaired
    res = _run("LM2596-ADJ", "--cache-dir", str(cache), "--retry-failed")
    assert res.returncode == 0
    out = json.loads((cache / "LM2596-ADJ.json").read_text())
    assert out["regulator"]["topology"] == "buck"
    plan = json.loads((cache / "LM2596-ADJ.plan.json").read_text())
    o = next(o for o in plan["execution"]["outcomes"] if o["task_id"] == "regulator")
    assert o["final_status"] == "complete"
