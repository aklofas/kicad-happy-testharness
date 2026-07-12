"""B4+B7 regression tests for Layer 2 schema invariants.

Implements two of the four absorption asks from main-repo LOG entry #71:
  (B4) design_context precedence — when triple {inferred, declared,
       effective} shape ships, harness invariant asserts effective ==
       declared whenever declared is non-null. Schema permits both plain
       enum and triple form via oneOf; precedence rule is harness-
       enforced (not in JSON Schema).
  (B7) novel-findings schema — reviewer_observations[] with origin const
       llm_novel. v2.0 (spec §5) removed the v1.4 caps: no maxItems,
       confidence enum gains 'high', severity enum gains 'error'. The
       cap-removal is locked here so a re-introduction is intentional.
       v1.4 default count is 0 (empty array on the example fixture).

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


def test_reviewer_observations_has_no_maxitems():
    """v2.0 (spec §5): the maxItems=5 cap on reviewer_observations is removed.
    (Flipped from test_reviewer_observations_maxItems_is_5.)"""
    schema = _load_json(REVIEW_ANNOTATIONS_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    obs = schema["properties"]["reviewer_observations"]
    assert "maxItems" not in obs, \
        f"maxItems cap must stay removed in v2.0, got {obs.get('maxItems')!r}"


def test_observation_confidence_enum_includes_high():
    """v2.0 (spec §5): observation confidence cap removed — enum is exactly
    {high, medium, low}. (Flipped from test_observation_confidence_enum_is_medium_low.)"""
    schema = _load_json(REVIEW_ANNOTATIONS_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    enum = schema["properties"]["reviewer_observations"]["items"]["properties"]["confidence"]["enum"]
    assert set(enum) == {"high", "medium", "low"}, \
        f"expected {{high, medium, low}}, got {set(enum)}"


def test_observation_origin_const_is_llm_novel():
    """observation origin is const 'llm_novel' (locked, no other producers)."""
    schema = _load_json(REVIEW_ANNOTATIONS_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    origin = schema["properties"]["reviewer_observations"]["items"]["properties"]["origin"]
    assert origin.get("const") == "llm_novel", \
        f"expected const='llm_novel', got {origin!r}"


def test_observation_severity_enum_includes_error():
    """v2.0 (spec §5): observation severity cap removed — enum is exactly
    {error, warning, info}. (Flipped from test_observation_severity_enum_is_warning_info.)"""
    schema = _load_json(REVIEW_ANNOTATIONS_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    enum = schema["properties"]["reviewer_observations"]["items"]["properties"]["severity"]["enum"]
    assert set(enum) == {"error", "warning", "info"}, \
        f"expected {{error, warning, info}}, got {set(enum)}"


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


def test_six_item_observations_array_accepted():
    """v2.0 (spec §5): no maxItems — a 6-item array must validate.
    (Flipped from test_six_item_observations_array_rejected.)"""
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
    Validator(schema).validate(payload)  # must not raise (cap removed)


# ─── (B4) design_context precedence ───────────────────────────────────────────

def _check_design_context_precedence(data):
    """Walk design_context dict and return list of precedence violations.

    For each of design_category and environment: if value is the triple
    form {inferred, declared, effective} and declared is non-null, then
    effective must equal declared. Returns [] if no violations.
    """
    violations = []
    for field in ("design_category", "environment"):
        value = data.get(field)
        if not isinstance(value, dict):
            continue  # plain enum form — invariant doesn't apply
        if "declared" not in value or "effective" not in value:
            continue  # not the triple form
        declared = value["declared"]
        effective = value["effective"]
        if declared is not None and declared != effective:
            violations.append({
                "field": field,
                "declared": declared,
                "effective": effective,
            })
    return violations


def test_design_context_schema_permits_triple_shape():
    """design_category and environment both accept oneOf [enum, triple]."""
    schema = _load_json(DESIGN_CONTEXT_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    for field in ("design_category", "environment"):
        oneOf = schema["properties"][field].get("oneOf")
        assert isinstance(oneOf, list) and len(oneOf) == 2, \
            f"{field}: expected 2-branch oneOf, got {oneOf!r}"
        refs = [b.get("$ref", "") for b in oneOf]
        assert any("enum" in r for r in refs), \
            f"{field}: missing enum branch in oneOf"
        assert any("triple" in r for r in refs), \
            f"{field}: missing triple branch in oneOf"


def test_design_context_example_fixture_validates():
    """Shipped fixture (plain-enum form) validates."""
    schema = _load_json(DESIGN_CONTEXT_SCHEMA_PATH)
    fixture = _load_json(DESIGN_CONTEXT_FIXTURE_PATH)
    if schema is None or fixture is None:
        print("  SKIP")
        return
    Validator = _import_jsonschema()
    if Validator is None:
        print("  SKIP: jsonschema unavailable")
        return
    Validator(schema).validate(fixture)
    # Plain enum form: invariant trivially holds (no triple to check)
    assert _check_design_context_precedence(fixture) == []


def test_synthesized_triple_with_declared_null_passes_invariant():
    """declared=null => no precedence constraint; invariant holds trivially."""
    schema = _load_json(DESIGN_CONTEXT_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    Validator = _import_jsonschema()
    payload = {
        "design_category": {
            "inferred": "power_supply",
            "declared": None,
            "effective": "power_supply",
        },
        "environment": "industrial",
        "compliance_targets": [],
        "user_declared_intent": None,
        "confidence": "medium",
        "evidence": "BOM heuristic: buck regulator + 24V rail",
        "resolution": "inferred_only",
    }
    if Validator is not None:
        Validator(schema).validate(payload)
    assert _check_design_context_precedence(payload) == []


def test_synthesized_triple_with_declared_equal_effective_passes_invariant():
    """declared==effective: invariant holds; schema accepts."""
    schema = _load_json(DESIGN_CONTEXT_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    Validator = _import_jsonschema()
    payload = {
        "design_category": "power_supply",
        "environment": {
            "inferred": "consumer",
            "declared": "industrial",
            "effective": "industrial",
        },
        "compliance_targets": ["IEC 62368"],
        "user_declared_intent": "Industrial 24V buck regulator demo board",
        "confidence": "high",
        "evidence": "User declared 'industrial' in .kicad-happy.json",
        "resolution": "user_override",
    }
    if Validator is not None:
        Validator(schema).validate(payload)
    assert _check_design_context_precedence(payload) == []


def test_synthesized_triple_with_declared_not_equal_effective_fails_invariant():
    """declared!=effective: schema accepts (no conditional in JSON Schema),
    but harness invariant flags it. Confirms harness is the enforcer."""
    schema = _load_json(DESIGN_CONTEXT_SCHEMA_PATH)
    if schema is None:
        print("  SKIP")
        return
    Validator = _import_jsonschema()
    payload = {
        "design_category": "power_supply",
        "environment": {
            "inferred": "consumer",
            "declared": "industrial",
            "effective": "automotive",  # violates precedence
        },
        "compliance_targets": [],
        "user_declared_intent": "industrial",
        "confidence": "high",
        "evidence": "test fixture for precedence violation",
        "resolution": "agree",
    }
    # Schema MUST accept this — the precedence rule isn't encoded in JSON Schema
    if Validator is not None:
        Validator(schema).validate(payload)
    # But harness invariant MUST flag it
    violations = _check_design_context_precedence(payload)
    assert len(violations) == 1, \
        f"expected 1 violation, got {violations!r}"
    assert violations[0]["field"] == "environment"
    assert violations[0]["declared"] == "industrial"
    assert violations[0]["effective"] == "automotive"


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
