"""Contract test: skills/kicad/review/scripts/_mini_jsonschema.py behavior
matches the real `jsonschema` package on the Layer 2 review-annotations schema.

Audit C2: the kicad-happy plugin previously had a soft jsonschema import in
merge_annotations.py (try/except → skip-with-warning) and a hard one in
validate_review.py. The mini validator replaces both so the plugin stays
dep-free at runtime. This test runs the mini-validator AND the real validator
against the same inputs and asserts behavioral parity — not message-string
identity (too brittle), just that both detect each violation.
"""

from __future__ import annotations

import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tests.contract._paths import MAIN_REPO_ROOT

REVIEW_SCRIPTS = MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"
REVIEW_SCHEMA = MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "schemas" / "review_annotations.schema.json"

sys.path.insert(0, str(REVIEW_SCRIPTS))


@pytest.fixture(scope="module")
def mini():
    import _mini_jsonschema
    return _mini_jsonschema


@pytest.fixture(scope="module")
def review_schema():
    return json.loads(REVIEW_SCHEMA.read_text())


@pytest.fixture
def valid_review():
    """A minimal-but-valid review_annotations doc."""
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": "1.0",
        "produced_for_run_id": "20260516T120000Z-abc123",
        "produced_at": now,
        "annotations": [
            {
                "finding_id": "schematic:detect_addressable_leds:LED1",
                "status": "confirmed",
                "reason": "LED1 needs a series resistor; current finding stands.",
                "confidence": "high",
                "reviewed_at": now,
            }
        ],
        "reviewer_observations": [],
    }


# ---------------------------------------------------------------------------
# Real schema must parse cleanly via mini-validator (sanity)
# ---------------------------------------------------------------------------

def test_real_layer2_schema_validates_valid_review_via_mini(mini, review_schema, valid_review):
    errors = list(mini.iter_errors(valid_review, review_schema))
    assert errors == [], f"Expected no errors; got {[e.message for e in errors]}"


def test_real_layer2_schema_validates_valid_review_via_real_jsonschema(review_schema, valid_review):
    """Cross-check: the same valid fixture must also pass the real validator,
    proving the test fixture isn't accidentally exercising a parity gap."""
    Draft202012Validator(review_schema).validate(valid_review)


def test_mini_validate_round_trip_does_not_raise(mini, review_schema, valid_review):
    """mini.validate() is the strict counterpart of iter_errors — must not
    raise on a valid doc."""
    mini.validate(valid_review, review_schema)


# ---------------------------------------------------------------------------
# Behavioral parity: each mutation must yield >=1 error from BOTH validators
# ---------------------------------------------------------------------------

def _drop_required(doc):
    doc = copy.deepcopy(doc)
    del doc["annotations"]
    return doc


def _bad_enum_status(doc):
    doc = copy.deepcopy(doc)
    doc["annotations"][0]["status"] = "maybe"
    return doc


def _bad_const_schema_version(doc):
    doc = copy.deepcopy(doc)
    doc["schema_version"] = "2.0"
    return doc


def _additional_property(doc):
    doc = copy.deepcopy(doc)
    doc["extra_field"] = "should not be allowed"
    return doc


def _min_length_too_short(doc):
    doc = copy.deepcopy(doc)
    doc["annotations"][0]["reason"] = "too short"  # minLength 20
    return doc


def _bad_date_time(doc):
    doc = copy.deepcopy(doc)
    doc["produced_at"] = "tuesday"
    return doc


@pytest.mark.parametrize(
    "mutator,label",
    [
        (_drop_required, "drop_required_annotations"),
        (_bad_enum_status, "annotation_status_bad_enum"),
        (_bad_const_schema_version, "schema_version_not_const_1_0"),
        (_additional_property, "additionalProperty_at_root"),
        (_min_length_too_short, "annotation_reason_too_short"),
    ],
)
def test_mini_and_real_jsonschema_agree_on_invalid(
    mini, review_schema, valid_review, mutator, label
):
    """For each crafted invalid mutation, BOTH validators must report >= 1
    error. Don't insist on identical messages — too brittle — just that the
    presence/absence of detection matches. ``format`` checks are intentionally
    excluded; see ``test_mini_is_strict_on_date_time_format`` below."""
    bad = mutator(valid_review)
    mini_errors = list(mini.iter_errors(bad, review_schema))
    real_errors = list(Draft202012Validator(review_schema).iter_errors(bad))
    assert mini_errors, f"[{label}] mini validator failed to detect violation"
    assert real_errors, f"[{label}] real validator failed to detect violation"


def test_mini_is_strict_on_date_time_format_while_real_is_permissive(
    mini, review_schema, valid_review
):
    """Deliberate divergence: real Draft202012Validator treats ``format`` as
    informational by default (must opt in via a FormatChecker). The mini
    validator hard-checks ``date-time`` because the Layer 2 schema uses it for
    ``produced_at`` / ``reviewed_at`` and silently accepting "tuesday" would
    defeat the audit trail. Lock this asymmetry so a future "fix" doesn't
    re-introduce permissiveness."""
    bad = _bad_date_time(valid_review)
    mini_errors = list(mini.iter_errors(bad, review_schema))
    real_errors = list(Draft202012Validator(review_schema).iter_errors(bad))
    assert mini_errors, "mini must catch bad date-time"
    assert any("date-time" in e.message for e in mini_errors)
    # Real validator (no FormatChecker wired) reports nothing for bad format.
    # If real ever enables format-by-default this assertion will flip — at
    # which point the mini stops being stricter and this test can be folded
    # back into the parity matrix above.
    assert real_errors == [], (
        f"Expected real jsonschema to be permissive on format by default; "
        f"got {[e.message for e in real_errors]}"
    )


# ---------------------------------------------------------------------------
# Loud failure on unsupported keyword
# ---------------------------------------------------------------------------

def test_mini_loud_fail_on_oneof(mini):
    """oneOf is intentionally not supported. The mini validator must yield an
    'unsupported schema keyword' error rather than silently passing — that's
    the entire point of failing loud at the boundary."""
    schema = {"oneOf": [{"type": "string"}, {"type": "integer"}]}
    errors = list(mini.iter_errors("hello", schema))
    assert errors, "mini validator silently accepted unsupported keyword"
    assert any("unsupported schema keyword" in e.message for e in errors), (
        f"Expected 'unsupported schema keyword' diagnostic; got "
        f"{[e.message for e in errors]}"
    )


def test_mini_loud_fail_on_ref(mini):
    """$ref is also unsupported — datasheets schemas use it, hence they stay
    on real jsonschema. Confirm the mini validator yells if anyone tries."""
    schema = {"$ref": "#/$defs/Foo", "$defs": {"Foo": {"type": "string"}}}
    errors = list(mini.iter_errors("hello", schema))
    assert errors and any("unsupported schema keyword" in e.message for e in errors)


# ---------------------------------------------------------------------------
# Spot-check: validate() raises with ValidationError surface compatible
# with jsonschema.exceptions.ValidationError
# ---------------------------------------------------------------------------

def test_validation_error_exposes_message_and_path(mini, review_schema, valid_review):
    """Callers that previously consumed jsonschema's ValidationError relied on
    .message and .path. The mini ValidationError must expose both."""
    bad = _bad_enum_status(valid_review)
    errors = list(mini.iter_errors(bad, review_schema))
    enum_err = next(e for e in errors if "not one of" in e.message)
    assert isinstance(enum_err.message, str)
    assert isinstance(enum_err.path, list)
    # Path should locate the failure at annotations[0].status
    assert enum_err.path == ["annotations", 0, "status"]
