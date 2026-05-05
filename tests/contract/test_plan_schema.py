"""Contract tests for plan.schema.json (Phase 3a)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

SCHEMA_PATH = MAIN_REPO_ROOT / "skills/datasheets/schemas/plan.schema.json"
FIXTURE_PATH = HARNESS_ROOT / "tests/fixtures/datasheets/plan-lm2596-adj.example.json"


def test_plan_schema_is_valid_draft_2020_12():
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)


def test_plan_fixture_round_trips():
    schema = json.loads(SCHEMA_PATH.read_text())
    fixture = json.loads(FIXTURE_PATH.read_text())
    Draft202012Validator(schema).validate(fixture)


def test_plan_task_status_enum_enforced():
    schema = json.loads(SCHEMA_PATH.read_text())
    fixture = json.loads(json.dumps(json.loads(FIXTURE_PATH.read_text())))
    fixture["tasks"][0]["status"] = "bogus"
    with pytest.raises(Exception):
        Draft202012Validator(schema).validate(fixture)


def test_plan_requires_pdf_sha():
    schema = json.loads(SCHEMA_PATH.read_text())
    fixture = json.loads(json.dumps(json.loads(FIXTURE_PATH.read_text())))
    fixture.pop("pdf_sha256")
    with pytest.raises(Exception):
        Draft202012Validator(schema).validate(fixture)


def test_plan_accepts_empty_tasks_for_skip_verdict():
    """Skip-verdict plans have tasks: [] — schema must accept this."""
    schema = json.loads(SCHEMA_PATH.read_text())
    fixture = json.loads(json.dumps(json.loads(FIXTURE_PATH.read_text())))
    fixture["tasks"] = []
    Draft202012Validator(schema).validate(fixture)
