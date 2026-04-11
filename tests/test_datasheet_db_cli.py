"""Unit tests for tools/datasheet_db.py CLI."""

TIER = "unit"

import sys
import os
import subprocess
import tempfile
from pathlib import Path
import hashlib
from unittest.mock import patch, MagicMock

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


def _with_temp_store_and_manifest_dirs(fn):
    """In-process test helper: override BOTH manifest.MANIFEST_DIR and
    storage.STORE_DIR for the duration of fn(tmp_path).

    Used by tests that need to call cli.main() directly (e.g. fetch-missing
    tests that mock urllib.request.urlopen)."""
    from validate.datasheet_db import manifest as m
    from validate.datasheet_db import storage as s
    orig_manifest = m.MANIFEST_DIR
    orig_store = s.STORE_DIR
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        m.MANIFEST_DIR = tmp / "manifest"
        s.STORE_DIR = tmp / "store"
        m.MANIFEST_DIR.mkdir(parents=True)
        s.STORE_DIR.mkdir(parents=True)
        try:
            fn(tmp)
        finally:
            m.MANIFEST_DIR = orig_manifest
            s.STORE_DIR = orig_store


def _mock_urlopen_response(body: bytes, content_type: str = "application/pdf"):
    """Build a MagicMock that mimics urllib.request.urlopen's context-manager response."""
    mock = MagicMock()
    mock.headers.get.return_value = content_type
    mock.__enter__ = lambda self: self
    mock.__exit__ = lambda self, *a: None
    chunks = [body[i:i + 8192] for i in range(0, len(body), 8192)] + [b""]
    mock.read.side_effect = chunks
    return mock


def _seed_record_with_url(sha256: str, url: str, mpn: str = "TESTMPN"):
    """Save a manifest record without writing the blob to the store."""
    from validate.datasheet_db.manifest import save_record
    save_record({
        "sha256": sha256,
        "size_bytes": 1024,
        "page_count": None,
        "mpns": [{"mpn": mpn, "primary": True}],
        "manufacturers": [],
        "source_urls": [{
            "url": url,
            "first_seen_at": "2026-04-10T00:00:00Z",
            "last_verified_at": "2026-04-10T00:00:00Z",
            "status": "live",
        }],
        "filename_aliases": [],
        "found_in": [],
        "revision_label": None,
        "first_seen": "2026-04-10T00:00:00Z",
        "last_seen": "2026-04-10T00:00:00Z",
        "verified": False,
        "verification_notes": None,
    })


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


def test_find_by_mpn_prints_store_path():
    """find MPN prints the absolute path to the blob in the store."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        store = tmp / "store"
        manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        fake = tmp / "source.pdf"
        _make_fake_pdf(fake, b"AD8605 data")
        # Insert first
        _run_cli(["insert", "--file", str(fake), "--mpn", "AD8605"], store, manifest)
        # Then find
        result = _run_cli(["find", "AD8605"], store, manifest)
        assert result.returncode == 0, result.stderr
        assert "AD8605" in result.stdout
        assert ".pdf" in result.stdout


def test_find_by_mpn_json_output():
    """find MPN --json prints a JSON array of full records."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); store = tmp / "store"; manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        fake = tmp / "source.pdf"
        _make_fake_pdf(fake, b"STM32 content")
        _run_cli(["insert", "--file", str(fake), "--mpn", "STM32F405"], store, manifest)
        result = _run_cli(["find", "STM32F405", "--json"], store, manifest)
        assert result.returncode == 0
        import json
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) == 1
        assert any(m["mpn"] == "STM32F405" for m in data[0]["mpns"])


def test_find_by_sha256_prefix():
    """find --sha256 PREFIX returns matching records."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); store = tmp / "store"; manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        fake = tmp / "source.pdf"
        _make_fake_pdf(fake, b"sha256-prefix-test")
        _run_cli(["insert", "--file", str(fake), "--mpn", "X"], store, manifest)
        # Get the actual sha by listing the manifest record
        records = list(manifest.rglob("*.json"))
        assert len(records) == 1
        import json
        rec = json.load(open(records[0]))
        sha_prefix = rec["sha256"][:6]
        result = _run_cli(["find", "--sha256", sha_prefix], store, manifest)
        assert result.returncode == 0
        assert ".pdf" in result.stdout


def test_find_no_match_exits_non_zero():
    """find on a missing MPN returns exit 1 with no stdout output."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); store = tmp / "store"; manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        result = _run_cli(["find", "DOES_NOT_EXIST"], store, manifest)
        assert result.returncode == 1


def test_verify_clean_store_exits_zero():
    """Verify on a freshly-inserted store returns exit 0."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        store = tmp / "store"
        manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        fake = tmp / "source.pdf"
        _make_fake_pdf(fake, b"verify-test")
        _run_cli(["insert", "--file", str(fake), "--mpn", "VERIFY1"], store, manifest)
        result = _run_cli(["verify"], store, manifest)
        assert result.returncode == 0, result.stderr
        assert "Matched" in result.stdout


def test_verify_mismatched_blob_exits_nonzero():
    """Mutate a blob on disk; verify should detect the mismatch and exit 1."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); store = tmp / "store"; manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        fake = tmp / "source.pdf"
        _make_fake_pdf(fake, b"original-content")
        _run_cli(["insert", "--file", str(fake), "--mpn", "MUT1"], store, manifest)
        # Find the blob and corrupt it
        blobs = list(store.glob("*.pdf"))
        assert len(blobs) == 1
        blobs[0].write_bytes(b"%PDF-1.5\nCORRUPTED")
        result = _run_cli(["verify"], store, manifest)
        assert result.returncode != 0
        assert "MISMATCH" in result.stdout or "Mismatched" in result.stdout


def test_verify_missing_blob_reported_but_exit_zero():
    """Missing blob is reported (a fresh clone is expected to be missing) but exit 0."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); store = tmp / "store"; manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        fake = tmp / "source.pdf"
        _make_fake_pdf(fake, b"missing-test")
        _run_cli(["insert", "--file", str(fake), "--mpn", "MISS1"], store, manifest)
        # Delete the blob
        blobs = list(store.glob("*.pdf"))
        assert len(blobs) == 1
        blobs[0].unlink()
        result = _run_cli(["verify"], store, manifest)
        assert result.returncode == 0, f"missing blob should not fail verify; got {result.returncode}: {result.stderr}"
        assert "Missing" in result.stdout


def test_verify_fast_skips_hashing():
    """--fast skips re-hashing, so a mutated blob is NOT detected (file just exists)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); store = tmp / "store"; manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        fake = tmp / "source.pdf"
        _make_fake_pdf(fake, b"fast-test")
        _run_cli(["insert", "--file", str(fake), "--mpn", "FAST1"], store, manifest)
        # Corrupt the blob
        blobs = list(store.glob("*.pdf"))
        blobs[0].write_bytes(b"%PDF-1.5\nCORRUPTED")
        # Slow verify catches it
        slow = _run_cli(["verify"], store, manifest)
        assert slow.returncode != 0
        # Fast verify does NOT (no re-hash)
        fast = _run_cli(["verify", "--fast"], store, manifest)
        assert fast.returncode == 0


def test_list_returns_all_records():
    """list with no filters returns one line per record."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        store = tmp / "store"
        manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        # Insert 3 distinct records
        for i, mpn in enumerate(["LST1", "LST2", "LST3"]):
            fake = tmp / f"src{i}.pdf"
            _make_fake_pdf(fake, f"list-{mpn}".encode())
            _run_cli(["insert", "--file", str(fake), "--mpn", mpn], store, manifest)
        result = _run_cli(["list"], store, manifest)
        assert result.returncode == 0, result.stderr
        # 3 lines, each containing one of the MPNs
        for mpn in ["LST1", "LST2", "LST3"]:
            assert mpn in result.stdout


def test_list_filter_by_manufacturer():
    """--manufacturer FOO returns only records from that manufacturer."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); store = tmp / "store"; manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        # Two records with different manufacturers
        for i, (mpn, mfr) in enumerate([("FILT1", "Acme"), ("FILT2", "Other Corp")]):
            fake = tmp / f"src{i}.pdf"
            _make_fake_pdf(fake, f"filter-{mpn}".encode())
            _run_cli(
                ["insert", "--file", str(fake), "--mpn", mpn, "--manufacturer", mfr],
                store, manifest,
            )
        result = _run_cli(["list", "--manufacturer", "Acme"], store, manifest)
        assert result.returncode == 0
        assert "FILT1" in result.stdout
        assert "FILT2" not in result.stdout


def test_list_format_json():
    """--format json prints a valid JSON array."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); store = tmp / "store"; manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        fake = tmp / "src.pdf"
        _make_fake_pdf(fake, b"json-output")
        _run_cli(["insert", "--file", str(fake), "--mpn", "JSONLIST"], store, manifest)
        result = _run_cli(["list", "--format", "json"], store, manifest)
        assert result.returncode == 0
        import json
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) == 1
        mpn_names = {m["mpn"] for m in data[0]["mpns"]}
        assert "JSONLIST" in mpn_names


def test_fetch_missing_dry_run_no_side_effects():
    """Dry run reports missing records without downloading anything."""
    def inner(tmp):
        from validate.datasheet_db.cli import main as cli_main
        # Seed a record with a URL but no blob in the store
        body = b"%PDF-1.5\n" + b"X" * 200
        sha = hashlib.sha256(body).hexdigest()
        _seed_record_with_url(sha, "https://x.com/test.pdf", mpn="DRYRUN")
        # Run dry-run
        rc = cli_main(["fetch-missing", "--dry-run"])
        assert rc == 0
        # No blob should have been written
        store = tmp / "store"
        blobs = list(store.glob("*.pdf"))
        assert len(blobs) == 0
    _with_temp_store_and_manifest_dirs(inner)


def test_fetch_missing_downloads_valid_url():
    """Mock a successful HTTP response; verify the blob lands in the store."""
    def inner(tmp):
        from validate.datasheet_db.cli import main as cli_main
        body = b"%PDF-1.5\n" + b"Y" * 500
        sha = hashlib.sha256(body).hexdigest()
        _seed_record_with_url(sha, "https://x.com/file.pdf", mpn="DOWNLOAD1")
        with patch("urllib.request.urlopen", return_value=_mock_urlopen_response(body)):
            rc = cli_main(["fetch-missing"])
        assert rc == 0
        # Blob should now exist
        store = tmp / "store"
        blobs = list(store.glob("*.pdf"))
        assert len(blobs) == 1
        # SHA must match
        from validate.datasheet_db.storage import compute_sha256
        assert compute_sha256(blobs[0]) == sha
    _with_temp_store_and_manifest_dirs(inner)


def test_fetch_missing_skips_present_blobs():
    """A record whose blob is already present and verified is skipped."""
    def inner(tmp):
        from validate.datasheet_db.cli import main as cli_main
        from validate.datasheet_db.manifest import load_record
        from validate.datasheet_db.storage import store_path, write_blob_atomic
        body = b"%PDF-1.5\n" + b"Z" * 300
        sha = hashlib.sha256(body).hexdigest()
        _seed_record_with_url(sha, "https://x.com/already.pdf", mpn="SKIPME")
        # Pre-write the blob to the store
        rec = load_record(sha)
        write_blob_atomic(store_path(rec), body, expected_sha256=sha)
        # Now run fetch-missing — should NOT call urlopen
        with patch("urllib.request.urlopen") as mock_open:
            rc = cli_main(["fetch-missing"])
            assert mock_open.call_count == 0, "should not have called urlopen for an already-present blob"
        assert rc == 0
    _with_temp_store_and_manifest_dirs(inner)


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
