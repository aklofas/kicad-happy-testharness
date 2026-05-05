"""Contract tests for scout.schema.json (Phase 3a)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

SCHEMA_PATH = MAIN_REPO_ROOT / "skills/datasheets/schemas/scout.schema.json"
FIXTURE_PATH = HARNESS_ROOT / "tests/fixtures/datasheets/scout-lm2596-adj.example.json"


def test_scout_schema_is_valid_draft_2020_12():
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)


def test_scout_fixture_round_trips():
    schema = json.loads(SCHEMA_PATH.read_text())
    fixture = json.loads(FIXTURE_PATH.read_text())
    Draft202012Validator(schema).validate(fixture)


def test_scout_quality_verdict_required():
    schema = json.loads(SCHEMA_PATH.read_text())
    fixture = json.loads(FIXTURE_PATH.read_text())
    fixture.pop("quality_verdict")
    with pytest.raises(Exception):
        Draft202012Validator(schema).validate(fixture)


@pytest.mark.parametrize("required_key", ["base", "pinout"])
def test_scout_extraction_pages_must_include_base_and_pinout(required_key):
    schema = json.loads(SCHEMA_PATH.read_text())
    fixture = json.loads(FIXTURE_PATH.read_text())
    bad = json.loads(json.dumps(fixture))
    bad["extraction_pages"].pop(required_key)
    with pytest.raises(Exception):
        Draft202012Validator(schema).validate(bad)
