"""Unit tests for validate/datasheet_db/manifest.py and _validators.py."""

TIER = "unit"

import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from validate.datasheet_db._validators import validate_record


def _valid_record():
    """Return a minimal but valid manifest record for tests."""
    return {
        "sha256": "ab" * 32,
        "size_bytes": 1024,
        "page_count": 10,
        "mpns": [{"mpn": "R1", "primary": True}],
        "manufacturers": ["Acme"],
        "source_urls": [],
        "filename_aliases": [],
        "found_in": [],
        "revision_label": None,
        "first_seen": "2026-04-10T00:00:00Z",
        "last_seen": "2026-04-10T00:00:00Z",
        "verified": False,
        "verification_notes": None,
    }


def test_validate_record_minimal_valid():
    """A minimal well-formed record produces no violations."""
    assert validate_record(_valid_record()) == []


def test_validate_record_missing_sha256():
    rec = _valid_record()
    del rec["sha256"]
    violations = validate_record(rec)
    assert any("sha256" in v for v in violations)


def test_validate_record_sha256_wrong_length():
    rec = _valid_record()
    rec["sha256"] = "ab" * 10
    violations = validate_record(rec)
    assert any("sha256" in v for v in violations)


def test_validate_record_missing_mpns():
    rec = _valid_record()
    del rec["mpns"]
    violations = validate_record(rec)
    assert any("mpn" in v for v in violations)


def test_validate_record_empty_mpns():
    rec = _valid_record()
    rec["mpns"] = []
    violations = validate_record(rec)
    assert any("mpn" in v for v in violations)


def test_validate_record_no_primary_mpn():
    """Exactly one mpns entry must have primary=True."""
    rec = _valid_record()
    rec["mpns"] = [{"mpn": "R1", "primary": False}]
    violations = validate_record(rec)
    assert any("primary" in v for v in violations)


def test_validate_record_multiple_primary_mpns():
    """More than one primary=True is invalid."""
    rec = _valid_record()
    rec["mpns"] = [
        {"mpn": "R1", "primary": True},
        {"mpn": "R2", "primary": True},
    ]
    violations = validate_record(rec)
    assert any("primary" in v for v in violations)


def test_validate_record_first_seen_after_last_seen():
    rec = _valid_record()
    rec["first_seen"] = "2026-04-11T00:00:00Z"
    rec["last_seen"] = "2026-04-10T00:00:00Z"
    violations = validate_record(rec)
    assert any("first_seen" in v or "last_seen" in v for v in violations)


def test_validate_record_source_urls_not_sorted():
    rec = _valid_record()
    rec["source_urls"] = [
        {"url": "https://z.example/", "first_seen_at": "2026-04-10T00:00:00Z",
         "last_verified_at": "2026-04-10T00:00:00Z", "status": "live"},
        {"url": "https://a.example/", "first_seen_at": "2026-04-10T00:00:00Z",
         "last_verified_at": "2026-04-10T00:00:00Z", "status": "live"},
    ]
    violations = validate_record(rec)
    assert any("sorted" in v for v in violations)


def test_validate_record_filename_aliases_not_sorted():
    rec = _valid_record()
    rec["filename_aliases"] = ["z.pdf", "a.pdf"]
    violations = validate_record(rec)
    assert any("sorted" in v or "alias" in v for v in violations)


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
