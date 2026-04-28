"""Tests for regression/run_extraction_checks.py.

Spec: docs/superpowers/specs/2026-04-27-a7-gold-set-versioning-design.md §5.3.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

TIER = "unit"

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RUN_CLI = REPO_ROOT / "regression" / "run_extraction_checks.py"
FIXTURES = REPO_ROOT / "tests" / "datasheets" / "fixtures" / "a7"


def _run(args, cwd):
    return subprocess.run(
        [sys.executable, str(RUN_CLI), *args],
        capture_output=True, text=True, cwd=str(cwd),
    )


def _seed_gold_and_cache(tmp_path, *, identical=True):
    """Seed a gold + cache pair. Returns (cache_dir, gold_root).

    If identical=True: cache and gold are byte-identical → A5 reports score=100.
    If identical=False: pin_count diverges 5 vs 7 → A5 reports ERROR + score 75.
    """
    cache_dir = tmp_path / "extracted"
    cache_dir.mkdir()
    cache_src = json.loads((FIXTURES / "lm2596-adj.cache.json").read_text())
    pdf_sha = "sha256:" + hashlib.sha256(b"pdf-bytes").hexdigest()
    cache_src["source"]["sha256"] = pdf_sha
    cache_src["source"]["local_path"] = "datasheets/lm2596-adj.pdf"
    (cache_dir / "LM2596-ADJ.json").write_text(json.dumps(cache_src))

    gold_root = tmp_path / "regression" / "reference_extractions"
    gold_root.mkdir(parents=True)
    (gold_root / "_meta.schema.json").write_text(
        (REPO_ROOT / "regression" / "reference_extractions" / "_meta.schema.json").read_text())

    slug_dir = gold_root / "lm2596-adj"
    slug_dir.mkdir()
    if identical:
        gold = json.loads(json.dumps(cache_src))
    else:
        gold = json.loads(json.dumps(cache_src))
        # Diverge pin_count → A5 sees ERROR (exact scalar mismatch)
        gold["base"]["package"]["pin_count"] = 7
    (slug_dir / "gold_v1.0.json").write_text(json.dumps(gold))

    meta = {
        "mpn": "LM2596-ADJ", "mpn_slug": "lm2596-adj",
        "pdf_sha256": hashlib.sha256(b"pdf-bytes").hexdigest(),
        "pdf_filename": "lm2596-adj.pdf",
        "schema_version_at_curation": cache_src["schema_version"],
        "extractor_schema_version_at_curation": "1.0",
        "curated_at": "2026-04-27T14:22:11Z",
        "curated_from": {
            "cache_path": "x", "gate_run_id": None, "gate_quality_score": 98,
            "sanity_vector_path": "y", "sanity_vector_pass": True,
            "sanity_vector_field_count": 1,
        },
        "history": [{
            "event": "initial", "at": "2026-04-27T14:22:11Z",
            "pdf_sha256": hashlib.sha256(b"pdf-bytes").hexdigest(),
            "schema_version": cache_src["schema_version"],
            "gate_quality_score": 98,
        }],
    }
    (slug_dir / "meta.json").write_text(json.dumps(meta))
    return cache_dir, gold_root


def test_help_works():
    r = subprocess.run([sys.executable, str(RUN_CLI), "--help"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert "--mpn" in r.stdout
    assert "--cache-dir" in r.stdout


def test_identical_pair_score_100_exit_0():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        cache_dir, gold_root = _seed_gold_and_cache(tmp_path, identical=True)
        r = _run([
            "--all",
            "--cache-dir", str(cache_dir),
            "--gold-dir", str(gold_root),
        ], cwd=tmp_path)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "100" in r.stdout


def test_diverged_pair_exit_1():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        cache_dir, gold_root = _seed_gold_and_cache(tmp_path, identical=False)
        r = _run([
            "--all",
            "--cache-dir", str(cache_dir),
            "--gold-dir", str(gold_root),
        ], cwd=tmp_path)
        # pin_count diverges 5 vs 7 → A5 reports ERROR → exit 1
        assert r.returncode == 1


def test_missing_cache_skipped():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        cache_dir, gold_root = _seed_gold_and_cache(tmp_path)
        (cache_dir / "LM2596-ADJ.json").unlink()
        r = _run([
            "--all",
            "--cache-dir", str(cache_dir),
            "--gold-dir", str(gold_root),
        ], cwd=tmp_path)
        # No cache → skipped → exit 0 (nothing regresses)
        assert r.returncode == 0


def test_missing_gold_skipped():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        cache_dir, gold_root = _seed_gold_and_cache(tmp_path)
        shutil.rmtree(gold_root / "lm2596-adj")
        r = _run([
            "--all",
            "--cache-dir", str(cache_dir),
            "--gold-dir", str(gold_root),
        ], cwd=tmp_path)
        assert r.returncode == 0


def test_score_threshold_override():
    """--score-threshold lets caller raise/lower the bar."""
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        cache_dir, gold_root = _seed_gold_and_cache(tmp_path, identical=True)
        r = _run([
            "--all", "--score-threshold", "100",
            "--cache-dir", str(cache_dir),
            "--gold-dir", str(gold_root),
        ], cwd=tmp_path)
        assert r.returncode == 0  # identical → score 100 → meets threshold 100


def test_json_output():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        cache_dir, gold_root = _seed_gold_and_cache(tmp_path, identical=True)
        r = _run([
            "--all", "--json",
            "--cache-dir", str(cache_dir),
            "--gold-dir", str(gold_root),
        ], cwd=tmp_path)
        assert r.returncode == 0
        payload = json.loads(r.stdout)
        assert "summary" in payload
        assert "per_mpn" in payload


def test_single_mpn_filter():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        cache_dir, gold_root = _seed_gold_and_cache(tmp_path, identical=True)
        r = _run([
            "--mpn", "LM2596-ADJ",
            "--cache-dir", str(cache_dir),
            "--gold-dir", str(gold_root),
        ], cwd=tmp_path)
        assert r.returncode == 0


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
