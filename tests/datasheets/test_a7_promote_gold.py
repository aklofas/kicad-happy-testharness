"""Tests for regression/promote_gold.py.

Spec: docs/superpowers/specs/2026-04-27-a7-gold-set-versioning-design.md §5.1.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

TIER = "unit"

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROMOTE_CLI = REPO_ROOT / "regression" / "promote_gold.py"


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
