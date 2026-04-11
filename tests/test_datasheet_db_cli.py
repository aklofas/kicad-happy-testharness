"""Unit tests for tools/datasheet_db.py CLI."""

TIER = "unit"

import sys
import os
import subprocess
import tempfile
from pathlib import Path
import hashlib

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


def _make_fake_pdf(path, content_suffix=b"dummy"):
    """Write a minimal valid-looking PDF to path."""
    with open(path, "wb") as f:
        f.write(b"%PDF-1.5\n" + content_suffix)


def test_insert_file_creates_record_and_blob():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        store = tmp / "store"
        manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        fake = tmp / "source.pdf"
        _make_fake_pdf(fake, b"AD8605 data")
        result = _run_cli(
            ["insert", "--file", str(fake), "--mpn", "AD8605", "--manufacturer", "Analog Devices"],
            store, manifest,
        )
        assert result.returncode == 0, result.stderr
        # One record in manifest
        records = list((manifest).rglob("*.json"))
        assert len(records) == 1
        # Blob in store with canonical filename
        blobs = list(store.glob("*.pdf"))
        assert len(blobs) == 1
        assert "AD8605" in blobs[0].name


def test_insert_file_twice_merges():
    """Second insert of same blob is a merge, not duplicate."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); store = tmp / "store"; manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        fake = tmp / "source.pdf"
        _make_fake_pdf(fake, b"same")
        _run_cli(["insert", "--file", str(fake), "--mpn", "A1"], store, manifest)
        _run_cli(["insert", "--file", str(fake), "--mpn", "A2"], store, manifest)
        records = list(manifest.rglob("*.json"))
        assert len(records) == 1
        import json
        rec = json.load(open(records[0]))
        mpn_names = {m["mpn"] for m in rec["mpns"]}
        assert mpn_names == {"A1", "A2"}


def test_insert_file_rejects_non_pdf():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); store = tmp / "store"; manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        fake = tmp / "source.txt"
        fake.write_text("not a pdf")
        result = _run_cli(["insert", "--file", str(fake), "--mpn", "X"], store, manifest)
        assert result.returncode != 0
        assert list(manifest.rglob("*.json")) == []


def test_insert_file_missing_path():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); store = tmp / "store"; manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        result = _run_cli(["insert", "--file", "/nonexistent.pdf", "--mpn", "X"], store, manifest)
        assert result.returncode != 0


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
