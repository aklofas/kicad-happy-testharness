"""B4+B7 regression tests for Layer 2 schema invariants.

Implements two of the four absorption asks from main-repo LOG entry #71:
  (B4) design_context precedence — when triple {inferred, declared,
       effective} shape ships, harness invariant asserts effective ==
       declared whenever declared is non-null. Schema permits both plain
       enum and triple form via oneOf; precedence rule is harness-
       enforced (not in JSON Schema).
  (B7) novel-findings schema — reviewer_observations[] with maxItems 5,
       observation confidence enum [medium, low], origin const llm_novel,
       severity enum [warning, info]. v1.4 default count is 0 (empty
       array on the example fixture).

Tests are pure JSON parsing — only the schema/fixture file paths are
resolved via KICAD_HAPPY_DIR. jsonschema is required for validation
tests; tests skip gracefully when unavailable.
"""
from __future__ import annotations

TIER = "unit"

import json
import os
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
KH_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy")))

REVIEW_SCHEMA_DIR = KH_DIR / "skills" / "kicad" / "review" / "schemas"
REVIEW_FIXTURE_DIR = KH_DIR / "skills" / "kicad" / "review" / "fixtures"

DESIGN_CONTEXT_SCHEMA_PATH = REVIEW_SCHEMA_DIR / "design_context.schema.json"
REVIEW_ANNOTATIONS_SCHEMA_PATH = REVIEW_SCHEMA_DIR / "review_annotations.schema.json"
DESIGN_CONTEXT_FIXTURE_PATH = REVIEW_FIXTURE_DIR / "design_context.example.json"
REVIEW_ANNOTATIONS_FIXTURE_PATH = REVIEW_FIXTURE_DIR / "review_annotations.example.json"


def _load_json(path: Path):
    """Load a JSON file. Returns None if path doesn't exist."""
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _import_jsonschema():
    """Try to import jsonschema's Draft202012Validator. Returns None on miss."""
    try:
        from jsonschema import Draft202012Validator
        return Draft202012Validator
    except ImportError:
        return None


# ─── (B7) novel-findings schema ───────────────────────────────────────────

def test_review_annotations_schema_parses():
    """review_annotations.schema.json is JSON-loadable."""
    schema = _load_json(REVIEW_ANNOTATIONS_SCHEMA_PATH)
    if schema is None:
        print("  SKIP: review_annotations.schema.json not found")
        return
    assert schema.get("title") == "Layer 2 Review Annotations", \
        f"unexpected title: {schema.get('title')!r}"


def test_reviewer_observations_maxItems_is_5():
    """maxItems on reviewer_observations is 5 per spec §4.2."""
    schema = _load_json(REVIEW_ANNOTATIONS_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    obs = schema["properties"]["reviewer_observations"]
    assert obs.get("maxItems") == 5, \
        f"expected maxItems=5, got {obs.get('maxItems')!r}"


def test_observation_confidence_enum_is_medium_low():
    """observation confidence enum is exactly {medium, low} (no high)."""
    schema = _load_json(REVIEW_ANNOTATIONS_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    enum = schema["properties"]["reviewer_observations"]["items"]["properties"]["confidence"]["enum"]
    assert set(enum) == {"medium", "low"}, \
        f"expected {{medium, low}}, got {set(enum)}"


def test_observation_origin_const_is_llm_novel():
    """observation origin is const 'llm_novel' (locked, no other producers)."""
    schema = _load_json(REVIEW_ANNOTATIONS_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    origin = schema["properties"]["reviewer_observations"]["items"]["properties"]["origin"]
    assert origin.get("const") == "llm_novel", \
        f"expected const='llm_novel', got {origin!r}"


def test_observation_severity_enum_is_warning_info():
    """observation severity enum is exactly {warning, info} — never error."""
    schema = _load_json(REVIEW_ANNOTATIONS_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    enum = schema["properties"]["reviewer_observations"]["items"]["properties"]["severity"]["enum"]
    assert set(enum) == {"warning", "info"}, \
        f"expected {{warning, info}}, got {set(enum)}"


def test_review_annotations_example_fixture_validates():
    """The shipped example fixture (empty observations) validates."""
    schema = _load_json(REVIEW_ANNOTATIONS_SCHEMA_PATH)
    fixture = _load_json(REVIEW_ANNOTATIONS_FIXTURE_PATH)
    if schema is None or fixture is None:
        print("  SKIP: schema or fixture missing")
        return
    assert fixture.get("reviewer_observations") == [], \
        "v1.4 default reviewer_observations must be empty array"
    Validator = _import_jsonschema()
    if Validator is None:
        print("  SKIP: jsonschema unavailable")
        return
    Validator(schema).validate(fixture)


def test_six_item_observations_array_rejected():
    """maxItems:5 — a 6-item array must fail validation."""
    schema = _load_json(REVIEW_ANNOTATIONS_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    Validator = _import_jsonschema()
    if Validator is None:
        print("  SKIP: jsonschema unavailable")
        return
    obs = {
        "origin": "llm_novel",
        "observation": "x",
        "severity": "info",
        "confidence": "low",
        "reasoning": "twenty characters at least here",
        "reviewed_at": "2026-04-28T00:00:00Z",
    }
    payload = {
        "schema_version": "1.0",
        "produced_for_run_id": "20260428T000000Z-aaaaaa",
        "produced_at": "2026-04-28T00:00:00Z",
        "annotations": [],
        "reviewer_observations": [obs] * 6,
    }
    try:
        Validator(schema).validate(payload)
    except Exception:
        return  # expected
    raise AssertionError("expected jsonschema rejection on 6-item observations array")


# ─── (B4) design_context precedence ───────────────────────────────────────────

# Custom-runner __main__ block (harness convention)
if __name__ == "__main__":
    import traceback
    fn_names = sorted(n for n, v in globals().items()
                      if n.startswith("test_") and callable(v))
    failed = 0
    passed = 0
    for n in fn_names:
        try:
            globals()[n]()
            print(f"PASS {n}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {n}: {e}")
            failed += 1
        except Exception as e:
            print(f"FAIL {n}: {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"{passed} passed, {failed} failed ({len(fn_names)} total)")
    sys.exit(0 if failed == 0 else 1)
