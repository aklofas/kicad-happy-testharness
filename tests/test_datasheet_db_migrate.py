"""Unit tests for tools/migrate_datasheets_to_db.py."""

TIER = "unit"

import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
sys.path.insert(0, str(HARNESS_DIR / "tools"))

from migrate_datasheets_to_db import phase1_enumerate, phase2_group


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
