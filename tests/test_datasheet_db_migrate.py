"""Unit tests for tools/migrate_datasheets_to_db.py."""

TIER = "unit"

import os
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
sys.path.insert(0, str(HARNESS_DIR / "tools"))

from migrate_datasheets_to_db import (
    phase1_enumerate, phase2_group, phase3_stage, phase4_swap,
    phase5_verify, phase6_absorb_verification_json
)


def test_phase1_enumerate_finds_pdfs_in_tmp_tree():
    """Create 3 fake PDFs in different locations, verify all found."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "datasheets").mkdir()
        (tmp / "datasheets_from_repos" / "owner" / "repo").mkdir(parents=True)
        (tmp / "repos" / "owner" / "repo" / "datasheets").mkdir(parents=True)
        for p in [
            tmp / "datasheets" / "a.pdf",
            tmp / "datasheets_from_repos" / "owner" / "repo" / "b.pdf",
            tmp / "repos" / "owner" / "repo" / "datasheets" / "c.pdf",
        ]:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"%PDF-1.5\n" + p.stem.encode())

        entries = list(phase1_enumerate(
            repos_root=tmp / "repos",
            bulk_root=tmp / "datasheets",
            preserved_root=tmp / "datasheets_from_repos",
        ))
        assert len(entries) == 3
        kinds = {e["origin_kind"] for e in entries}
        assert kinds == {"repo", "bulk", "preserved"}


def _make_entry(sha, filename, origin_kind="bulk", origin_ref="bulk"):
    """Build a synthetic phase-1 entry for phase2_group tests."""
    return {
        "path": f"/fake/{filename}",
        "sha256": sha,
        "size": 1024,
        "filename": filename,
        "origin_kind": origin_kind,
        "origin_ref": origin_ref,
    }


def test_phase2_group_dedupes_duplicate_shas():
    """Three entries with the same sha256 collapse to one record."""
    sha = "ab" * 32
    entries = [
        _make_entry(sha, "AD8605.pdf"),
        _make_entry(sha, "AD8605_dup.pdf"),
        _make_entry(sha, "ad8605-datasheet.pdf"),
    ]
    records = phase2_group(entries)
    assert len(records) == 1
    rec = records[0]
    assert rec["sha256"] == sha
    # All 3 filenames should be in filename_aliases (sorted, deduped)
    assert "AD8605.pdf" in rec["filename_aliases"]
    assert "AD8605_dup.pdf" in rec["filename_aliases"]
    assert "ad8605-datasheet.pdf" in rec["filename_aliases"]


def test_phase2_group_infers_mpn_from_filename():
    """A filename like AD8605ARTZ-REEL7.pdf yields the correct primary MPN."""
    sha = "cd" * 32
    entries = [_make_entry(sha, "AD8605ARTZ-REEL7.pdf")]
    records = phase2_group(entries)
    assert len(records) == 1
    primary = next(m for m in records[0]["mpns"] if m["primary"])
    # The longest MPN-like token should be picked
    assert "AD8605" in primary["mpn"] or "8605" in primary["mpn"]


def test_phase2_group_unknown_manufacturer_falls_back():
    """A filename with no recognized prefix gets manufacturer='Unknown'."""
    sha = "ef" * 32
    entries = [_make_entry(sha, "ZZZ_NOTREAL_PART_42.pdf")]
    records = phase2_group(entries)
    assert len(records) == 1
    assert records[0]["manufacturers"] == ["Unknown"]


def test_phase3_stage_copies_blobs_and_writes_records():
    """phase3_stage copies the source blob into staging_store under canonical
    filename and writes the record JSON to staging_manifest under shard dir."""
    import json
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # Plant a fake source PDF
        source = tmp / "source" / "AD8605.pdf"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"%PDF-1.5\n" + b"stage-test")
        # Build a record that points at the source path
        from migrate_datasheets_to_db import phase2_group
        # Compute the actual SHA via the same path the migration would
        sys.path.insert(0, str(HARNESS_DIR))
        from validate.datasheet_db.storage import compute_sha256, canonical_filename
        sha = compute_sha256(source)
        records = phase2_group([{
            "path": str(source),
            "sha256": sha,
            "size": source.stat().st_size,
            "filename": "AD8605.pdf",
            "origin_kind": "bulk",
            "origin_ref": "bulk",
        }])
        assert len(records) == 1

        staging_store = tmp / "datasheets.new"
        staging_manifest = tmp / "manifest.staging"
        phase3_stage(records, staging_store, staging_manifest)

        # Blob should exist at the canonical filename
        canonical = canonical_filename(records[0])
        assert (staging_store / canonical).exists(), \
            f"missing staged blob {canonical}"
        # Manifest record should exist at sharded path
        record_file = staging_manifest / sha[:2] / f"{sha}.json"
        assert record_file.exists(), f"missing staged record {record_file}"
        loaded = json.load(open(record_file))
        assert loaded["sha256"] == sha


def test_phase4_swap_atomic_renames():
    """phase4_swap renames the four directories: live store → bulk bak,
    staging store → live, preserved → preserved bak, staging manifest → live."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # Set up the four directories with marker files
        live_store = tmp / "datasheets"
        live_manifest = tmp / "manifest"  # NOT pre-existing
        staging_store = tmp / "datasheets.new"
        staging_manifest = tmp / "manifest.staging"
        bulk_bak = tmp / "datasheets.bulk_bak"
        preserved_root = tmp / "datasheets_from_repos"
        preserved_bak = tmp / "datasheets_from_repos.bak"

        live_store.mkdir()
        (live_store / "old.pdf").write_text("old")
        staging_store.mkdir()
        (staging_store / "new.pdf").write_text("new")
        staging_manifest.mkdir()
        (staging_manifest / "ab").mkdir()
        (staging_manifest / "ab" / "fake.json").write_text("{}")
        preserved_root.mkdir()
        (preserved_root / "preserved.pdf").write_text("preserved")

        phase4_swap(
            live_store=live_store,
            live_manifest=live_manifest,
            staging_store=staging_store,
            staging_manifest=staging_manifest,
            bulk_bak=bulk_bak,
            preserved_root=preserved_root,
            preserved_bak=preserved_bak,
        )

        # Live store should now contain the staged content
        assert live_store.exists()
        assert (live_store / "new.pdf").exists()
        assert not (live_store / "old.pdf").exists()
        # Live manifest should now exist with the staged content
        assert live_manifest.exists()
        assert (live_manifest / "ab" / "fake.json").exists()
        # Backups should contain the originals
        assert bulk_bak.exists()
        assert (bulk_bak / "old.pdf").exists()
        assert preserved_bak.exists()
        assert (preserved_bak / "preserved.pdf").exists()
        # Staging dirs should no longer exist
        assert not staging_store.exists()
        assert not staging_manifest.exists()
        assert not preserved_root.exists()


def test_phase5_verify_runs_against_clean_store():
    """phase5_verify shells out to datasheet_db verify; returns 0 on clean store."""
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        store = tmp / "store"
        manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()
        # Empty store + empty manifest = clean (no records to verify)
        # Call the CLI directly via subprocess with the env vars
        # phase5_verify needs to know which store/manifest to verify
        env = os.environ.copy()
        env["DATASHEET_DB_STORE_DIR"] = str(store)
        env["DATASHEET_DB_MANIFEST_DIR"] = str(manifest)
        rc = phase5_verify(harness_root=HARNESS_DIR, env=env)
        assert rc == 0


def test_phase6_marks_existing_record_verified():
    """phase6_absorb_verification_json sets verified=true on records that already exist."""
    import json
    import os
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        store = tmp / "store"
        manifest = tmp / "manifest"
        store.mkdir(); manifest.mkdir()

        # Override the manifest module's MANIFEST_DIR to point at our temp dir
        from validate.datasheet_db import manifest as m
        from validate.datasheet_db.manifest import save_record, load_record
        original = m.MANIFEST_DIR
        m.MANIFEST_DIR = manifest
        try:
            # Seed an unverified record
            sha = "ab" * 32
            save_record({
                "sha256": sha,
                "size_bytes": 1024,
                "page_count": None,
                "mpns": [{"mpn": "AD8605", "primary": True}],
                "manufacturers": ["Analog Devices"],
                "source_urls": [],
                "filename_aliases": [],
                "found_in": [],
                "revision_label": None,
                "first_seen": "2026-04-10T00:00:00Z",
                "last_seen": "2026-04-10T00:00:00Z",
                "verified": False,
                "verification_notes": None,
            })
            # Write a verification_json with that sha
            ver_json = tmp / "datasheets_verification.json"
            ver_json.write_text(json.dumps([
                {"sha256": sha, "mpn": "AD8605", "manufacturer": "Analog Devices"}
            ]))

            phase6_absorb_verification_json(ver_json)

            # The record should now be verified=true
            rec = load_record(sha)
            assert rec is not None
            assert rec["verified"] is True
            # The verification_json file should be deleted
            assert not ver_json.exists()
        finally:
            m.MANIFEST_DIR = original


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
