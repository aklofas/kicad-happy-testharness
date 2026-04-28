"""Tests for --re-curate-from sweep mode on promote_gold.py.

Spec: docs/superpowers/specs/2026-04-27-a7-gold-set-versioning-design.md §5.1.1.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

TIER = "unit"

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROMOTE_CLI = REPO_ROOT / "regression" / "promote_gold.py"
FIXTURES = REPO_ROOT / "tests" / "datasheets" / "fixtures" / "a7"


def _run_promote(args, cwd, env_overrides=None):
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run(
        [sys.executable, str(PROMOTE_CLI), *args],
        capture_output=True, text=True, cwd=str(cwd), env=env,
    )


def _setup_dirs(tmp_path):
    """Build a gold-ready test sandbox.

    Returns (cache_dir, sanity_dir, gold_dir, pdf_dir, env_overrides).
    """
    cache_dir = tmp_path / "extracted"
    cache_dir.mkdir()
    sanity_dir = tmp_path / "sanity_vectors"
    sanity_dir.mkdir()
    gold_dir = tmp_path / "regression" / "reference_extractions"
    gold_dir.mkdir(parents=True)
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    (pdf_dir / "LM2596-ADJ.pdf").write_bytes(b"pdf-bytes")
    sha = "sha256:" + hashlib.sha256(b"pdf-bytes").hexdigest()
    cache_src = json.loads((FIXTURES / "lm2596-adj.cache.json").read_text())
    cache_src["source"]["sha256"] = sha
    cache_src["source"]["local_path"] = "datasheets/LM2596-ADJ.pdf"
    (cache_dir / "LM2596-ADJ.json").write_text(json.dumps(cache_src))
    (sanity_dir / "lm2596-adj.json").write_text(
        (FIXTURES / "lm2596-adj.sanity_vector.json").read_text())
    (gold_dir / "_meta.schema.json").write_text(
        (REPO_ROOT / "regression" / "reference_extractions" / "_meta.schema.json").read_text())
    env = {
        "HARNESS_SANITY_DIR_OVERRIDE": str(sanity_dir),
        "HARNESS_GOLD_DIR_OVERRIDE": str(gold_dir),
    }
    return cache_dir, sanity_dir, gold_dir, pdf_dir, env


def _initial_promote(tmp_path, cache_dir, gold_dir, pdf_dir, env):
    """Run the initial promote (1.0) before re-curation."""
    return _run_promote(
        ["--mpn", "LM2596-ADJ",
         "--cache-dir", str(cache_dir),
         "--pdf-dir", str(pdf_dir),
         "--no-gate", "--yes"],
        cwd=tmp_path, env_overrides=env,
    )


def _bump_cache_to(cache_dir, base_version):
    cache_path = cache_dir / "LM2596-ADJ.json"
    cache = json.loads(cache_path.read_text())
    cache["schema_version"]["base"] = base_version
    cache_path.write_text(json.dumps(cache))


def test_recurate_renames_existing_to_archived(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    cache_dir, sanity_dir, gold_dir, pdf_dir, env = _setup_dirs(tmp_path)
    _initial_promote(tmp_path, cache_dir, gold_dir, pdf_dir, env)
    slug_dir = gold_dir / "lm2596-adj"
    assert (slug_dir / "gold_v1.0.json").exists()
    _bump_cache_to(cache_dir, "2.0")
    r = _run_promote(
        ["--mpn", "LM2596-ADJ",
         "--cache-dir", str(cache_dir),
         "--pdf-dir", str(pdf_dir),
         "--no-gate", "--yes",
         "--re-curate-from", "1.0"],
        cwd=tmp_path, env_overrides=env,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert (slug_dir / "gold_v1.0.json.archived").exists()
    assert (slug_dir / "gold_v2.0.json").exists()
    meta = json.loads((slug_dir / "meta.json").read_text())
    assert meta["history"][-1]["event"] == "recurate_major_bump"
    assert meta["history"][-1]["from_schema_version"]["base"] == "1.0"


def test_recurate_without_prior_gold_fails(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    cache_dir, sanity_dir, gold_dir, pdf_dir, env = _setup_dirs(tmp_path)
    r = _run_promote(
        ["--mpn", "LM2596-ADJ",
         "--cache-dir", str(cache_dir),
         "--pdf-dir", str(pdf_dir),
         "--no-gate", "--yes",
         "--re-curate-from", "1.0"],
        cwd=tmp_path, env_overrides=env,
    )
    assert r.returncode == 2
    msg = (r.stdout + r.stderr).lower()
    assert "no prior gold" in msg or "not found" in msg


def test_recurate_with_same_major_fails_precondition(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    cache_dir, sanity_dir, gold_dir, pdf_dir, env = _setup_dirs(tmp_path)
    _initial_promote(tmp_path, cache_dir, gold_dir, pdf_dir, env)
    # cache still at 1.0 — try to re-curate from 1.0 (same major)
    r = _run_promote(
        ["--mpn", "LM2596-ADJ",
         "--cache-dir", str(cache_dir),
         "--pdf-dir", str(pdf_dir),
         "--no-gate", "--yes",
         "--re-curate-from", "1.0"],
        cwd=tmp_path, env_overrides=env,
    )
    assert r.returncode == 2
    msg = (r.stdout + r.stderr).lower()
    assert "precondition" in msg or "same major" in msg or "shares major" in msg


def test_recurate_history_records_from_schema_version(tmp_path=None):
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    cache_dir, sanity_dir, gold_dir, pdf_dir, env = _setup_dirs(tmp_path)
    _initial_promote(tmp_path, cache_dir, gold_dir, pdf_dir, env)
    _bump_cache_to(cache_dir, "2.0")
    _run_promote(
        ["--mpn", "LM2596-ADJ",
         "--cache-dir", str(cache_dir),
         "--pdf-dir", str(pdf_dir),
         "--no-gate", "--yes",
         "--re-curate-from", "1.0"],
        cwd=tmp_path, env_overrides=env,
    )
    meta = json.loads((gold_dir / "lm2596-adj" / "meta.json").read_text())
    last = meta["history"][-1]
    assert "from_schema_version" in last
    assert last["from_schema_version"]["base"] == "1.0"
    # The from_schema_version.categories must validate against meta schema
    # (i.e. dict with version-string values)
    assert isinstance(last["from_schema_version"]["categories"], dict)


def test_recurate_keeps_archived_file_in_place(tmp_path=None):
    """Re-curate writes new gold beside (not in) archive structure."""
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    cache_dir, sanity_dir, gold_dir, pdf_dir, env = _setup_dirs(tmp_path)
    _initial_promote(tmp_path, cache_dir, gold_dir, pdf_dir, env)
    _bump_cache_to(cache_dir, "2.0")
    _run_promote(
        ["--mpn", "LM2596-ADJ",
         "--cache-dir", str(cache_dir),
         "--pdf-dir", str(pdf_dir),
         "--no-gate", "--yes",
         "--re-curate-from", "1.0"],
        cwd=tmp_path, env_overrides=env,
    )
    slug_dir = gold_dir / "lm2596-adj"
    assert (slug_dir / "gold_v1.0.json.archived").exists()
    assert (slug_dir / "gold_v2.0.json").exists()
    archived_content = json.loads(
        (slug_dir / "gold_v1.0.json.archived").read_text())
    assert archived_content["schema_version"]["base"] == "1.0"


def test_recurate_help_text_mentions_mode():
    r = subprocess.run(
        [sys.executable, str(PROMOTE_CLI), "--help"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "re-curate" in r.stdout.lower() or "recurat" in r.stdout.lower()


# Custom-runner __main__ block matching harness convention
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
