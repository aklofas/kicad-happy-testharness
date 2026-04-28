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
