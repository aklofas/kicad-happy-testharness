"""Tests for regression/reference_extractions/_meta.schema.json validation.

Spec: docs/superpowers/specs/2026-04-27-a7-gold-set-versioning-design.md §4.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import pytest
except ImportError:
    pytest = None

TIER = "unit"

META_SCHEMA_PATH = REPO_ROOT / "regression" / "reference_extractions" / "_meta.schema.json"


def _load_schema():
    return json.loads(META_SCHEMA_PATH.read_text())


def _validator():
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return None
    return Draft202012Validator(_load_schema())


def _valid_meta() -> dict:
    return {
        "mpn": "LM2596-ADJ",
        "mpn_slug": "lm2596-adj",
        "pdf_sha256": "a" * 64,
        "pdf_filename": "lm2596-adj.pdf",
        "schema_version_at_curation": {
            "base": "1.0",
            "categories": {"regulator": "0.3"},
        },
        "extractor_schema_version_at_curation": "1.0",
        "curated_at": "2026-04-27T14:22:11Z",
        "curated_from": {
            "cache_path": "kicad-happy/datasheets/extracted/LM2596-ADJ.json",
            "gate_run_id": None,
            "gate_quality_score": 98,
            "sanity_vector_path": "reference/datasheets/sanity_vectors/lm2596-adj.json",
            "sanity_vector_pass": True,
            "sanity_vector_field_count": 10,
        },
        "history": [{
            "event": "initial",
            "at": "2026-04-27T14:22:11Z",
            "pdf_sha256": "a" * 64,
            "schema_version": {"base": "1.0", "categories": {"regulator": "0.3"}},
            "gate_quality_score": 98,
        }],
    }


def test_schema_loads_as_draft_2020_12():
    schema = _load_schema()
    assert schema["$schema"].endswith("2020-12/schema")


def test_valid_meta_passes_validation():
    validator = _validator()
    if validator is None:
        return  # jsonschema not available; skip
    errors = list(validator.iter_errors(_valid_meta()))
    assert errors == []


def test_missing_mpn_fails():
    validator = _validator()
    if validator is None:
        return  # jsonschema not available; skip
    meta = _valid_meta()
    del meta["mpn"]
    errors = list(validator.iter_errors(meta))
    assert any("mpn" in str(e.message) for e in errors)


def test_invalid_pdf_sha256_format_fails():
    validator = _validator()
    if validator is None:
        return  # jsonschema not available; skip
    meta = _valid_meta()
    meta["pdf_sha256"] = "not-a-sha"
    errors = list(validator.iter_errors(meta))
    assert errors


def test_extra_top_level_key_fails():
    validator = _validator()
    if validator is None:
        return  # jsonschema not available; skip
    meta = _valid_meta()
    meta["extra_field"] = "should_not_be_here"
    errors = list(validator.iter_errors(meta))
    assert any("additional" in str(e.message).lower() for e in errors)


def test_history_must_be_list():
    validator = _validator()
    if validator is None:
        return  # jsonschema not available; skip
    meta = _valid_meta()
    meta["history"] = "not-a-list"
    errors = list(validator.iter_errors(meta))
    assert errors


def test_history_event_enum_enforced():
    validator = _validator()
    if validator is None:
        return  # jsonschema not available; skip
    meta = _valid_meta()
    meta["history"][0]["event"] = "bogus_event"
    errors = list(validator.iter_errors(meta))
    assert errors


def test_curated_from_gate_run_id_nullable():
    validator = _validator()
    if validator is None:
        return  # jsonschema not available; skip
    meta = _valid_meta()
    meta["curated_from"]["gate_run_id"] = None
    errors = list(validator.iter_errors(meta))
    assert errors == []


def test_mpn_slug_basic():
    from regression._mpn_slug import mpn_slug
    assert mpn_slug("LM2596-ADJ") == "lm2596-adj"


def test_mpn_slug_preserves_dots():
    from regression._mpn_slug import mpn_slug
    assert mpn_slug("ABM8G-106-12.000MHZ-T") == "abm8g-106-12.000mhz-t"


def test_mpn_slug_replaces_invalid():
    from regression._mpn_slug import mpn_slug
    assert mpn_slug("Some/Bad MPN") == "some_bad_mpn"


def test_mpn_slug_strips_whitespace():
    from regression._mpn_slug import mpn_slug
    assert mpn_slug("  LM2596-ADJ  ") == "lm2596-adj"


if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed ({len(tests)} total)")
    sys.exit(1 if failed else 0)
