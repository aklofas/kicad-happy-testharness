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
    # Sanity-vector diff visible in stdout; not exit 2 (sanity passes)
    out = r.stdout + r.stderr
    assert "sanity" in out.lower()
    assert r.returncode != 2  # 2 is sanity-fail, not what we want
    # exit 2 placeholder until 2c lands schema-validation/write — that's OK


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
