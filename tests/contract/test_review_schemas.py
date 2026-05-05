"""Contract tests for skills/kicad/review/schemas/*.schema.json."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMA_DIR = MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "schemas"
FIXTURE_DIR = MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "fixtures"


def _load_schema(name):
    return json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text())


def test_design_context_schema_is_valid_draft_2020_12():
    schema = _load_schema("design_context")
    Draft202012Validator.check_schema(schema)


def test_review_annotations_schema_is_valid_draft_2020_12():
    schema = _load_schema("review_annotations")
    Draft202012Validator.check_schema(schema)


def test_severity_tuning_schema_is_valid_draft_2020_12():
    schema = _load_schema("severity_tuning")
    Draft202012Validator.check_schema(schema)


def test_design_context_fixture_round_trips():
    schema = _load_schema("design_context")
    fixture = json.loads((FIXTURE_DIR / "design_context.example.json").read_text())
    Draft202012Validator(schema).validate(fixture)


def test_review_annotations_fixture_round_trips():
    schema = _load_schema("review_annotations")
    fixture = json.loads((FIXTURE_DIR / "review_annotations.example.json").read_text())
    Draft202012Validator(schema).validate(fixture)


def test_review_annotations_rejects_short_reason():
    """HI-8: reason MUST be ≥20 chars."""
    schema = _load_schema("review_annotations")
    bad = {
        "schema_version": "1.0",
        "produced_for_run_id": "20260427T000000Z-aaaaaa",
        "produced_at": "2026-04-27T00:00:00Z",
        "annotations": [{
            "finding_id": "sch:R-1:u1",
            "status": "confirmed",
            "reason": "too short",  # <20 chars
            "confidence": "high",
            "reviewed_at": "2026-04-27T00:00:00Z",
        }],
        "reviewer_observations": [],
    }
    with pytest.raises(Exception):  # jsonschema.ValidationError
        Draft202012Validator(schema).validate(bad)


def test_review_annotations_caps_reviewer_observations_at_5():
    schema = _load_schema("review_annotations")
    obs = {
        "origin": "llm_novel",
        "observation": "test obs",
        "severity": "warning",
        "confidence": "medium",
        "reasoning": "x" * 25,
        "reviewed_at": "2026-04-27T00:00:00Z",
    }
    bad = {
        "schema_version": "1.0",
        "produced_for_run_id": "20260427T000000Z-aaaaaa",
        "produced_at": "2026-04-27T00:00:00Z",
        "annotations": [],
        "reviewer_observations": [obs] * 6,  # 6 > maxItems 5
    }
    with pytest.raises(Exception):
        Draft202012Validator(schema).validate(bad)


def test_review_annotations_caps_observation_confidence():
    """Per spec §15: reviewer_observations[].confidence capped at 'medium'."""
    schema = _load_schema("review_annotations")
    bad = {
        "schema_version": "1.0",
        "produced_for_run_id": "20260427T000000Z-aaaaaa",
        "produced_at": "2026-04-27T00:00:00Z",
        "annotations": [],
        "reviewer_observations": [{
            "origin": "llm_novel",
            "observation": "x",
            "severity": "warning",
            "confidence": "high",  # rejected
            "reasoning": "x" * 25,
            "reviewed_at": "2026-04-27T00:00:00Z",
        }],
    }
    with pytest.raises(Exception):
        Draft202012Validator(schema).validate(bad)
