"""Unit tests for tools/datasheet_db.py CLI."""

TIER = "unit"

import sys
import os
import subprocess
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))


def _run_cli(args, store_dir, manifest_dir, **kwargs):
    """Run datasheet_db with tmp dirs set."""
    env = os.environ.copy()
    env["DATASHEET_DB_STORE_DIR"] = str(store_dir)
    env["DATASHEET_DB_MANIFEST_DIR"] = str(manifest_dir)
    return subprocess.run(
        [sys.executable, str(HARNESS_DIR / "tools" / "datasheet_db.py")] + args,
        capture_output=True, text=True, env=env, **kwargs
    )


def test_stats_empty_store():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        store = tmp / "store"
        manifest = tmp / "manifest"
        store.mkdir()
        manifest.mkdir()
        result = _run_cli(["stats"], store, manifest)
        assert result.returncode == 0
        assert "0 records" in result.stdout or "Total" in result.stdout


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
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
