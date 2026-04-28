"""Tests for regression/check_gold_currency.py.

Spec: docs/superpowers/specs/2026-04-27-a7-gold-set-versioning-design.md §5.2.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

TIER = "unit"

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHECK_CLI = REPO_ROOT / "regression" / "check_gold_currency.py"
FIXTURES = REPO_ROOT / "tests" / "datasheets" / "fixtures" / "a7"


def _run(args, cwd):
    return subprocess.run(
        [sys.executable, str(CHECK_CLI), *args],
        capture_output=True, text=True, cwd=str(cwd),
    )


def _seed_gold(tmp_path, *, schema_versions=None, extractor_version="1.0",
                pdf_bytes=b"pdf-bytes"):
    """Build a gold-set tree with one MPN. Returns (gold_root, slug_dir, pdf_dir, pdf_sha)."""
    schema_versions = schema_versions or {"base": "1.0",
                                            "categories": {"regulator": "0.3"}}
    pdf_sha = hashlib.sha256(pdf_bytes).hexdigest()

    gold_root = tmp_path / "regression" / "reference_extractions"
    gold_root.mkdir(parents=True)
    (gold_root / "_meta.schema.json").write_text(
        (REPO_ROOT / "regression" / "reference_extractions" / "_meta.schema.json").read_text())

    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    (pdf_dir / "lm2596-adj.pdf").write_bytes(pdf_bytes)

    slug_dir = gold_root / "lm2596-adj"
    slug_dir.mkdir()
    cache = json.loads((FIXTURES / "lm2596-adj.cache.json").read_text())
    cache["schema_version"] = schema_versions
    cache["extraction"]["extractor_schema_version"] = extractor_version
    cache["source"]["sha256"] = "sha256:" + pdf_sha
    cache["source"]["local_path"] = "datasheets/lm2596-adj.pdf"
    (slug_dir / f"gold_v{schema_versions['base']}.json").write_text(
        json.dumps(cache, indent=2))

    meta = {
        "mpn": "LM2596-ADJ",
        "mpn_slug": "lm2596-adj",
        "pdf_sha256": pdf_sha,
        "pdf_filename": "lm2596-adj.pdf",
        "schema_version_at_curation": schema_versions,
        "extractor_schema_version_at_curation": extractor_version,
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
            "pdf_sha256": pdf_sha,
            "schema_version": schema_versions,
            "gate_quality_score": 98,
        }],
    }
    (slug_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    return gold_root, slug_dir, pdf_dir, pdf_sha


def _write_synth_schemas(tmp_path, *, base="1.0", categories=None,
                          extractor="1.0"):
    """Write synthetic schema files at <tmp_path>/skills/datasheets/schemas/.

    Each schema declares a top-level `version` field; extraction.schema.json
    declares `extractor_schema_version`. The currency-check tool reads these
    fields directly.
    """
    categories = categories or {"regulator": "0.3"}
    schemas_dir = tmp_path / "skills" / "datasheets" / "schemas"
    schemas_dir.mkdir(parents=True)
    (schemas_dir / "base.schema.json").write_text(json.dumps({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "version": base,
    }))
    for cat, ver in categories.items():
        (schemas_dir / f"{cat}.schema.json").write_text(json.dumps({
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "version": ver,
        }))
    (schemas_dir / "extraction.schema.json").write_text(json.dumps({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "extractor_schema_version": extractor,
    }))
    return schemas_dir


def test_help_works():
    r = subprocess.run([sys.executable, str(CHECK_CLI), "--help"],
                        capture_output=True, text=True)
    assert r.returncode == 0
    assert "--mpn" in r.stdout
    assert "--all" in r.stdout
    assert "--release" in r.stdout


def test_clean_state_returns_zero(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    gold_root, _, pdf_dir, _ = _seed_gold(tmp_path)
    schemas_dir = _write_synth_schemas(tmp_path)
    r = _run([
        "--all",
        "--pdf-dir", str(pdf_dir),
        "--schemas-dir", str(schemas_dir),
        "--gold-dir", str(gold_root),
    ], cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 ERROR" in r.stdout or "no error" in r.stdout.lower()


def test_pdf_sha_mismatch_returns_one(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    gold_root, _, pdf_dir, _ = _seed_gold(tmp_path)
    (pdf_dir / "lm2596-adj.pdf").write_bytes(b"different-bytes")
    schemas_dir = _write_synth_schemas(tmp_path)
    r = _run([
        "--all",
        "--pdf-dir", str(pdf_dir),
        "--schemas-dir", str(schemas_dir),
        "--gold-dir", str(gold_root),
    ], cwd=tmp_path)
    assert r.returncode == 1
    assert "pdf" in r.stdout.lower()
    assert "error" in r.stdout.lower()


def test_base_minor_bump_returns_zero_with_info(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    gold_root, _, pdf_dir, _ = _seed_gold(tmp_path)
    schemas_dir = _write_synth_schemas(tmp_path, base="1.1")
    r = _run([
        "--all",
        "--pdf-dir", str(pdf_dir),
        "--schemas-dir", str(schemas_dir),
        "--gold-dir", str(gold_root),
    ], cwd=tmp_path)
    assert r.returncode == 0
    assert "info" in r.stdout.lower() or "1.0" in r.stdout


def test_base_major_bump_returns_one(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    gold_root, _, pdf_dir, _ = _seed_gold(tmp_path)
    schemas_dir = _write_synth_schemas(tmp_path, base="2.0")
    r = _run([
        "--all",
        "--pdf-dir", str(pdf_dir),
        "--schemas-dir", str(schemas_dir),
        "--gold-dir", str(gold_root),
    ], cwd=tmp_path)
    assert r.returncode == 1
    assert "error" in r.stdout.lower()


def test_per_category_minor_bump_returns_zero_info(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    gold_root, _, pdf_dir, _ = _seed_gold(tmp_path)
    schemas_dir = _write_synth_schemas(tmp_path, base="1.0",
                                         categories={"regulator": "0.4"})
    r = _run([
        "--all",
        "--pdf-dir", str(pdf_dir),
        "--schemas-dir", str(schemas_dir),
        "--gold-dir", str(gold_root),
    ], cwd=tmp_path)
    assert r.returncode == 0
    assert "info" in r.stdout.lower() or "0.3" in r.stdout


def test_per_category_major_bump_returns_one(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    gold_root, _, pdf_dir, _ = _seed_gold(tmp_path)
    schemas_dir = _write_synth_schemas(tmp_path, base="1.0",
                                         categories={"regulator": "1.0"})
    r = _run([
        "--all",
        "--pdf-dir", str(pdf_dir),
        "--schemas-dir", str(schemas_dir),
        "--gold-dir", str(gold_root),
    ], cwd=tmp_path)
    assert r.returncode == 1


def test_extractor_version_mismatch_info_only(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    gold_root, _, pdf_dir, _ = _seed_gold(tmp_path, extractor_version="1.0")
    schemas_dir = _write_synth_schemas(tmp_path, extractor="1.1")
    r = _run([
        "--all",
        "--pdf-dir", str(pdf_dir),
        "--schemas-dir", str(schemas_dir),
        "--gold-dir", str(gold_root),
    ], cwd=tmp_path)
    assert r.returncode == 0
    out = r.stdout.lower()
    assert "extractor" in out or "info" in out


def test_json_output_shape(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    gold_root, _, pdf_dir, _ = _seed_gold(tmp_path)
    schemas_dir = _write_synth_schemas(tmp_path)
    r = _run([
        "--all", "--json",
        "--pdf-dir", str(pdf_dir),
        "--schemas-dir", str(schemas_dir),
        "--gold-dir", str(gold_root),
    ], cwd=tmp_path)
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert "audited_count" in payload
    assert "summary" in payload
    assert "findings" in payload
    assert payload["audited_count"] == 1


def test_malformed_meta_returns_two(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    gold_root, slug_dir, pdf_dir, _ = _seed_gold(tmp_path)
    (slug_dir / "meta.json").write_text("not json {{")
    schemas_dir = _write_synth_schemas(tmp_path)
    r = _run([
        "--all",
        "--pdf-dir", str(pdf_dir),
        "--schemas-dir", str(schemas_dir),
        "--gold-dir", str(gold_root),
    ], cwd=tmp_path)
    assert r.returncode == 2


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
