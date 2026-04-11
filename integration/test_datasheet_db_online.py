"""Online-tier integration tests for validate/datasheet_db/ + tools/datasheet_db.py.

These tests hit real network endpoints to exercise the fetch path end-to-end.
Kept deliberately small because rate limits and flaky URLs are operationally
painful. For unit-tier coverage (mocked HTTP), see tests/test_datasheet_db_*.py.

Run only via: python3 run_tests.py --tier online
"""

TIER = "online"

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

DATASHEET_DB = HARNESS_DIR / "tools" / "datasheet_db.py"


def _run_cli(args, store_dir, manifest_dir, timeout=120):
    """Invoke datasheet_db CLI with tmp dirs in env. Used by every test."""
    env = os.environ.copy()
    env["DATASHEET_DB_STORE_DIR"] = str(store_dir)
    env["DATASHEET_DB_MANIFEST_DIR"] = str(manifest_dir)
    return subprocess.run(
        [sys.executable, str(DATASHEET_DB)] + args,
        capture_output=True, text=True, env=env, timeout=timeout,
    )


def test_insert_real_ad8605_url():
    """Fetch a known-stable Analog Devices AD8605 URL; verify record + blob land."""
    # If this URL stops resolving, the test will fail — update the URL when that
    # happens. Fetching from analog.com is our canonical stable-reference URL.
    url = "https://www.analog.com/media/en/technical-documentation/data-sheets/AD8605_8606_8608.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        store = tmp / "store"
        manifest = tmp / "manifest"
        store.mkdir()
        manifest.mkdir()
        result = _run_cli(
            ["insert", "--url", url, "--mpn", "AD8605ARTZ-REEL7",
             "--manufacturer", "Analog Devices"],
            store, manifest,
        )
        assert result.returncode == 0, (
            f"insert failed: rc={result.returncode} stderr={result.stderr}"
        )
        # Exactly one manifest record
        records = list(manifest.rglob("*.json"))
        assert len(records) == 1, f"expected 1 record, got {len(records)}"
        # Exactly one blob in the store
        blobs = list(store.glob("*.pdf"))
        assert len(blobs) == 1, f"expected 1 blob, got {len(blobs)}"
        # Blob name contains the sanitized primary MPN
        assert "AD8605" in blobs[0].name
        # Record has the right manufacturer + MPN
        rec = json.load(open(records[0]))
        assert "Analog Devices" in rec["manufacturers"]
        assert any(m["mpn"] == "AD8605ARTZ-REEL7" for m in rec["mpns"])


def test_insert_invalid_url_reports_failure():
    """A URL that can't resolve (bogus TLD) should exit non-zero and leave no record."""
    # .invalid is reserved per RFC 6761 — guaranteed to fail DNS lookup
    url = "https://this-host-does-not-exist.invalid/nonexistent.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        store = tmp / "store"
        manifest = tmp / "manifest"
        store.mkdir()
        manifest.mkdir()
        result = _run_cli(
            ["insert", "--url", url, "--mpn", "FAKE"],
            store, manifest,
            timeout=30,
        )
        assert result.returncode != 0, (
            f"expected non-zero exit on invalid URL, got {result.returncode}"
        )
        # No record should have been created
        records = list(manifest.rglob("*.json"))
        assert records == [], f"expected no records, got {len(records)}"
        # No partial blobs either
        blobs = list(store.glob("*.pdf"))
        assert blobs == []


def test_fetch_missing_classifies_valid_and_dead_urls():
    """Seed a manifest with 2 records (one valid URL, one dead), run fetch-missing,
    verify: downloaded=1 and failed=1."""
    # Valid URL (same stable reference as test 1)
    valid_url = "https://www.analog.com/media/en/technical-documentation/data-sheets/AD8605_8606_8608.pdf"
    # Dead URL (RFC 6761 reserved TLD)
    dead_url = "https://this-host-does-not-exist.invalid/nonexistent.pdf"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        store = tmp / "store"
        manifest = tmp / "manifest"
        store.mkdir()
        manifest.mkdir()

        # Seed two records by round-tripping through `insert --url` for the
        # valid URL, then manually writing a record for the dead URL (since
        # insert would refuse to save a record without a valid blob).
        rc = _run_cli(
            ["insert", "--url", valid_url, "--mpn", "AD8605ARTZ-REEL7",
             "--manufacturer", "Analog Devices"],
            store, manifest,
        ).returncode
        assert rc == 0

        # Find the record we just created so we know its real sha
        records = list(manifest.rglob("*.json"))
        assert len(records) == 1
        valid_sha = json.load(open(records[0]))["sha256"]

        # Delete the blob so fetch-missing has something to do for this record
        for b in store.glob("*.pdf"):
            b.unlink()

        # Manually plant a second record with the dead URL — hand-craft it
        # since insert won't save a record without valid bytes
        fake_sha = "de" * 32
        shard = manifest / fake_sha[:2]
        shard.mkdir(exist_ok=True)
        fake_record = {
            "sha256": fake_sha,
            "size_bytes": 1000,
            "page_count": None,
            "mpns": [{"mpn": "DEADMPN", "primary": True}],
            "manufacturers": [],
            "source_urls": [{
                "url": dead_url,
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
        }
        (shard / f"{fake_sha}.json").write_text(json.dumps(fake_record, indent=2))

        # Run fetch-missing with --jobs 1 (sequential, easier to reason about)
        result = _run_cli(
            ["fetch-missing", "--jobs", "1", "--timeout", "30"],
            store, manifest,
        )
        assert result.returncode == 0, (
            f"fetch-missing exited non-zero: {result.stderr}"
        )

        # Parse the summary output — expect Downloaded: 1, Failed: 1
        stdout = result.stdout
        assert "Downloaded: 1" in stdout, f"expected 1 download, stdout=\n{stdout}"
        assert "Failed: 1" in stdout, f"expected 1 failure, stdout=\n{stdout}"

        # The valid blob should now be in the store
        valid_blobs = list(store.glob("*AD8605*"))
        assert len(valid_blobs) == 1


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
