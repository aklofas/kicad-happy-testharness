"""Tests for regression/promote_gold.py.

Spec: docs/superpowers/specs/2026-04-27-a7-gold-set-versioning-design.md §5.1.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

TIER = "unit"

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROMOTE_CLI = REPO_ROOT / "regression" / "promote_gold.py"
FIXTURES = REPO_ROOT / "tests" / "datasheets" / "fixtures" / "a7"


def _setup_cache_dir(tmp_path: Path) -> Path:
    cache_dir = tmp_path / "extracted"
    cache_dir.mkdir()
    cache_src = FIXTURES / "lm2596-adj.cache.json"
    (cache_dir / "LM2596-ADJ.json").write_text(cache_src.read_text())
    return cache_dir


def _setup_sanity_dir(tmp_path: Path) -> Path:
    sanity_dir = tmp_path / "sanity_vectors"
    sanity_dir.mkdir(parents=True)
    src = FIXTURES / "lm2596-adj.sanity_vector.json"
    (sanity_dir / "lm2596-adj.json").write_text(src.read_text())
    return sanity_dir


def _run_promote(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PROMOTE_CLI), *args],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
    )


def test_help_works():
    r = _run_promote(["--help"])
    assert r.returncode == 0
    assert "--mpn" in r.stdout


def test_missing_mpn_fails():
    r = _run_promote([])
    assert r.returncode != 0
    assert "--mpn" in r.stderr or "mpn" in r.stderr.lower()


def test_cache_not_found_returns_exit_3(tmp_path=None):
    if tmp_path is None:
        tmp_path = Path(tempfile.mkdtemp())
    cache_dir = tmp_path / "extracted"
    cache_dir.mkdir()
    r = _run_promote(["--mpn", "DOESNOTEXIST", "--cache-dir", str(cache_dir), "--yes"])
    assert r.returncode == 3
    assert "not found" in (r.stdout + r.stderr).lower()


def test_no_gate_skips_gate_runs_sanity(tmp_path=None):
    """--no-gate skips A6 but still runs sanity-vector diff (passes for synthetic)."""
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    cache_dir = _setup_cache_dir(tmp_path)
    sanity_dir = _setup_sanity_dir(tmp_path)
    gold_dir = _setup_gold_dir(tmp_path)
    env = {
        "HARNESS_SANITY_DIR_OVERRIDE": str(sanity_dir),
        "HARNESS_GOLD_DIR_OVERRIDE": str(gold_dir),
    }
    r = subprocess.run(
        [sys.executable, str(PROMOTE_CLI),
         "--mpn", "LM2596-ADJ",
         "--cache-dir", str(cache_dir),
         "--no-gate", "--yes"],
        capture_output=True, text=True,
        env={**__import__("os").environ, **env},
        cwd=str(REPO_ROOT),
    )
    # Sanity-vector diff visible in stdout; sanity passes → not exit 2
    out = r.stdout + r.stderr
    assert "sanity" in out.lower()
    assert r.returncode != 2  # 2 is sanity-fail, not what we want


def test_sanity_vector_mismatch_exits_2(tmp_path=None):
    """Sanity-vector mismatch blocks promotion."""
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    cache_dir = _setup_cache_dir(tmp_path)
    cache_path = cache_dir / "LM2596-ADJ.json"
    cache = json.loads(cache_path.read_text())
    cache["base"]["package"]["pin_count"] = 8  # tamper to 8 — vector says 5
    cache_path.write_text(json.dumps(cache))
    sanity_dir = _setup_sanity_dir(tmp_path)
    env = {"HARNESS_SANITY_DIR_OVERRIDE": str(sanity_dir)}
    r = subprocess.run(
        [sys.executable, str(PROMOTE_CLI),
         "--mpn", "LM2596-ADJ",
         "--cache-dir", str(cache_dir),
         "--no-gate", "--yes"],
        capture_output=True, text=True,
        env={**__import__("os").environ, **env},
        cwd=str(REPO_ROOT),
    )
    assert r.returncode == 2
    assert "sanity" in (r.stdout + r.stderr).lower()


def _setup_gold_dir(tmp_path: Path) -> Path:
    """Create a gold-set tree with the meta schema in place."""
    gold_dir = tmp_path / "regression" / "reference_extractions"
    gold_dir.mkdir(parents=True)
    src_schema = REPO_ROOT / "regression" / "reference_extractions" / "_meta.schema.json"
    (gold_dir / "_meta.schema.json").write_text(src_schema.read_text())
    return gold_dir


def _write_pdf_with_sha(pdf_dir: Path, name: str, content: bytes) -> str:
    """Write a synthetic PDF and return its SHA256."""
    import hashlib
    pdf_dir.mkdir(parents=True, exist_ok=True)
    (pdf_dir / name).write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def test_first_time_promote_writes_gold_and_meta(tmp_path=None):
    """First promote writes gold_v1.0.json + meta.json with event='initial'."""
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    cache_dir = _setup_cache_dir(tmp_path)
    sanity_dir = _setup_sanity_dir(tmp_path)
    gold_dir = _setup_gold_dir(tmp_path)
    pdf_dir = tmp_path / "pdfs"
    pdf_sha = _write_pdf_with_sha(pdf_dir, "lm2596-adj.pdf", b"synthetic-pdf-bytes")

    # Patch cache's sha256 to match real SHA of synthetic PDF
    cache_path = cache_dir / "LM2596-ADJ.json"
    cache = json.loads(cache_path.read_text())
    cache["source"]["sha256"] = f"sha256:{pdf_sha}"
    cache["source"]["local_path"] = "datasheets/lm2596-adj.pdf"
    cache_path.write_text(json.dumps(cache))

    env = {
        "HARNESS_SANITY_DIR_OVERRIDE": str(sanity_dir),
        "HARNESS_GOLD_DIR_OVERRIDE": str(gold_dir),
    }
    r = subprocess.run(
        [sys.executable, str(PROMOTE_CLI),
         "--mpn", "LM2596-ADJ",
         "--cache-dir", str(cache_dir),
         "--pdf-dir", str(pdf_dir),
         "--no-gate", "--yes"],
        capture_output=True, text=True,
        env={**__import__("os").environ, **env},
        cwd=str(REPO_ROOT),
    )
    assert r.returncode == 0, r.stdout + r.stderr

    slug_dir = gold_dir / "lm2596-adj"
    assert (slug_dir / "gold_v1.0.json").exists()
    assert (slug_dir / "meta.json").exists()
    meta = json.loads((slug_dir / "meta.json").read_text())
    assert meta["mpn"] == "LM2596-ADJ"
    assert meta["pdf_sha256"] == pdf_sha
    assert len(meta["history"]) == 1
    assert meta["history"][0]["event"] == "initial"


def test_repeat_promote_appends_to_history(tmp_path=None):
    """Promoting twice with same PDF SHA emits event='update' on second go."""
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    cache_dir = _setup_cache_dir(tmp_path)
    sanity_dir = _setup_sanity_dir(tmp_path)
    gold_dir = _setup_gold_dir(tmp_path)
    pdf_dir = tmp_path / "pdfs"
    pdf_sha = _write_pdf_with_sha(pdf_dir, "lm2596-adj.pdf", b"synthetic-pdf-bytes")

    cache_path = cache_dir / "LM2596-ADJ.json"
    cache = json.loads(cache_path.read_text())
    cache["source"]["sha256"] = f"sha256:{pdf_sha}"
    cache["source"]["local_path"] = "datasheets/lm2596-adj.pdf"
    cache_path.write_text(json.dumps(cache))

    env = {
        "HARNESS_SANITY_DIR_OVERRIDE": str(sanity_dir),
        "HARNESS_GOLD_DIR_OVERRIDE": str(gold_dir),
    }
    args = [sys.executable, str(PROMOTE_CLI),
            "--mpn", "LM2596-ADJ",
            "--cache-dir", str(cache_dir),
            "--pdf-dir", str(pdf_dir),
            "--no-gate", "--yes"]
    subprocess.run(args, capture_output=True, text=True,
                    env={**__import__("os").environ, **env}, cwd=str(REPO_ROOT))
    r = subprocess.run(args, capture_output=True, text=True,
                        env={**__import__("os").environ, **env}, cwd=str(REPO_ROOT))
    assert r.returncode == 0, r.stdout + r.stderr
    meta = json.loads((gold_dir / "lm2596-adj" / "meta.json").read_text())
    assert len(meta["history"]) == 2
    assert meta["history"][-1]["event"] == "update"


def test_pdf_sha_change_archives_old(tmp_path=None):
    """Changed PDF SHA -> old gold + meta moved to archived_pdf_sha_<old>/."""
    if tmp_path is None:
        import tempfile
        tmp_path = Path(tempfile.mkdtemp())
    cache_dir = _setup_cache_dir(tmp_path)
    sanity_dir = _setup_sanity_dir(tmp_path)
    gold_dir = _setup_gold_dir(tmp_path)
    pdf_dir = tmp_path / "pdfs"
    sha_v1 = _write_pdf_with_sha(pdf_dir, "lm2596-adj.pdf", b"v1-pdf-bytes")

    cache_path = cache_dir / "LM2596-ADJ.json"
    cache = json.loads(cache_path.read_text())
    cache["source"]["sha256"] = f"sha256:{sha_v1}"
    cache["source"]["local_path"] = "datasheets/lm2596-adj.pdf"
    cache_path.write_text(json.dumps(cache))

    env = {
        "HARNESS_SANITY_DIR_OVERRIDE": str(sanity_dir),
        "HARNESS_GOLD_DIR_OVERRIDE": str(gold_dir),
    }
    args = [sys.executable, str(PROMOTE_CLI),
            "--mpn", "LM2596-ADJ",
            "--cache-dir", str(cache_dir),
            "--pdf-dir", str(pdf_dir),
            "--no-gate", "--yes"]
    subprocess.run(args, capture_output=True, text=True,
                    env={**__import__("os").environ, **env}, cwd=str(REPO_ROOT))

    # Simulate PDF revision
    sha_v2 = _write_pdf_with_sha(pdf_dir, "lm2596-adj.pdf", b"v2-pdf-bytes")
    cache["source"]["sha256"] = f"sha256:{sha_v2}"
    cache_path.write_text(json.dumps(cache))

    r = subprocess.run(args, capture_output=True, text=True,
                        env={**__import__("os").environ, **env}, cwd=str(REPO_ROOT))
    assert r.returncode == 0, r.stdout + r.stderr
    archived = gold_dir / "lm2596-adj" / f"archived_pdf_sha_{sha_v1}"
    assert archived.exists()
    assert (archived / "gold_v1.0.json").exists()
    assert (archived / "meta.json").exists()


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
