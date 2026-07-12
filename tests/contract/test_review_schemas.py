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


# test_severity_tuning_schema_is_valid_draft_2020_12 — DELETED (spec §5):
# severity_tuning.schema.json removed in v2.0 Layer 2 cage decommission.


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


def test_review_annotations_has_no_maxitems_on_reviewer_observations():
    """v2.0 (spec §5): reviewer_observations no longer has maxItems — the cap is
    removed. Verify the schema allows more than 5 observations."""
    schema = _load_schema("review_annotations")
    obs = {
        "origin": "llm_novel",
        "observation": "test obs",
        "severity": "warning",
        "confidence": "medium",
        "reasoning": "x" * 25,
        "reviewed_at": "2026-04-27T00:00:00Z",
    }
    doc = {
        "schema_version": "1.0",
        "produced_for_run_id": "20260427T000000Z-aaaaaa",
        "produced_at": "2026-04-27T00:00:00Z",
        "annotations": [],
        "reviewer_observations": [obs] * 6,  # was rejected pre-v2.0; now allowed
    }
    Draft202012Validator(schema).validate(doc)  # must not raise


def test_review_annotations_observation_allows_high_confidence():
    """v2.0 (spec §5): reviewer_observations[].confidence cap ('medium') removed.
    'high' confidence is now valid."""
    schema = _load_schema("review_annotations")
    doc = {
        "schema_version": "1.0",
        "produced_for_run_id": "20260427T000000Z-aaaaaa",
        "produced_at": "2026-04-27T00:00:00Z",
        "annotations": [],
        "reviewer_observations": [{
            "origin": "llm_novel",
            "observation": "x",
            "severity": "warning",
            "confidence": "high",  # was rejected pre-v2.0; now allowed
            "reasoning": "x" * 25,
            "reviewed_at": "2026-04-27T00:00:00Z",
        }],
    }
    Draft202012Validator(schema).validate(doc)  # must not raise
