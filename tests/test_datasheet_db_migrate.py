"""Unit tests for tools/migrate_datasheets_to_db.py."""

TIER = "unit"

import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
sys.path.insert(0, str(HARNESS_DIR / "tools"))

from migrate_datasheets_to_db import phase1_enumerate


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
