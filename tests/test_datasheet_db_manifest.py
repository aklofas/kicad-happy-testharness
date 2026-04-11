"""Unit tests for validate/datasheet_db/manifest.py and _validators.py."""

TIER = "unit"

import sys
from pathlib import Path
import tempfile
import os
import json
from unittest.mock import patch

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from validate.datasheet_db._validators import validate_record
from validate.datasheet_db.manifest import (
    record_path, MANIFEST_DIR, save_record, load_record, merge_record,
    iter_records, find_by_mpn, find_by_url, find_by_sha256_prefix
)


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


# === record_path ===

def test_record_path_shards_by_first_two_chars():
    """Record path is MANIFEST_DIR/{sha256[:2]}/{sha256}.json."""
    sha = "ab1234cdef0123456789abcdef0123456789abcdef0123456789abcdef012345"
    expected = MANIFEST_DIR / "ab" / f"{sha}.json"
    assert record_path(sha) == expected


def test_record_path_returns_path_object():
    """record_path returns a pathlib.Path."""
    sha = "cd" * 32
    assert isinstance(record_path(sha), Path)


def test_record_path_rejects_short_sha():
    """Too-short sha raises ValueError."""
    try:
        record_path("abc")
        assert False, "should have raised"
    except ValueError:
        pass


# === save_record / load_record ===

def _with_temp_manifest_dir(fn):
    """Helper: run `fn(tmp_path)` with MANIFEST_DIR pointed at a tmp dir."""
    from validate.datasheet_db import manifest as m
    original = m.MANIFEST_DIR
    with tempfile.TemporaryDirectory() as tmp:
        m.MANIFEST_DIR = Path(tmp)
        try:
            fn(Path(tmp))
        finally:
            m.MANIFEST_DIR = original


def test_save_and_load_round_trip():
    def inner(tmp):
        rec = _valid_record()
        save_record(rec)
        loaded = load_record(rec["sha256"])
        assert loaded == rec
    _with_temp_manifest_dir(inner)


def test_save_record_creates_sharded_directory():
    def inner(tmp):
        rec = _valid_record()
        save_record(rec)
        assert (tmp / rec["sha256"][:2]).is_dir()
        assert (tmp / rec["sha256"][:2] / f"{rec['sha256']}.json").exists()
    _with_temp_manifest_dir(inner)


def test_save_record_raises_on_invariant_violation():
    """Saving a record with a broken invariant raises."""
    def inner(tmp):
        bad = _valid_record()
        bad["mpns"] = []  # violates "non-empty mpns"
        try:
            save_record(bad)
            assert False, "should have raised"
        except ValueError as e:
            assert "mpn" in str(e).lower()
    _with_temp_manifest_dir(inner)


def test_load_record_missing_returns_none():
    def inner(tmp):
        assert load_record("aa" * 32) is None
    _with_temp_manifest_dir(inner)


def test_save_record_is_atomic():
    """save_record writes via a .tmp file then renames."""
    def inner(tmp):
        rec = _valid_record()
        save_record(rec)
        # No leftover .tmp files in the shard dir
        shard = tmp / rec["sha256"][:2]
        assert list(shard.glob("*.tmp")) == []
    _with_temp_manifest_dir(inner)


# === merge_record ===

def test_merge_adds_new_mpn_alias():
    existing = _valid_record()
    existing["mpns"] = [{"mpn": "R1", "primary": True}]
    incoming = {"mpns": [{"mpn": "R2", "primary": False}]}
    merged = merge_record(existing, incoming)
    mpn_names = [m["mpn"] for m in merged["mpns"]]
    assert "R1" in mpn_names
    assert "R2" in mpn_names
    # R1 stays primary
    assert [m["primary"] for m in merged["mpns"] if m["mpn"] == "R1"] == [True]


def test_merge_dedupes_duplicate_mpn():
    existing = _valid_record()
    existing["mpns"] = [{"mpn": "R1", "primary": True}]
    incoming = {"mpns": [{"mpn": "R1", "primary": False}]}
    merged = merge_record(existing, incoming)
    assert len(merged["mpns"]) == 1


def test_merge_adds_new_source_url():
    existing = _valid_record()
    existing["source_urls"] = [
        {"url": "https://a.example/", "first_seen_at": "2026-04-10T00:00:00Z",
         "last_verified_at": "2026-04-10T00:00:00Z", "status": "live"}
    ]
    incoming = {"source_urls": [
        {"url": "https://b.example/", "first_seen_at": "2026-04-11T00:00:00Z",
         "last_verified_at": "2026-04-11T00:00:00Z", "status": "live"}
    ]}
    merged = merge_record(existing, incoming)
    urls = [u["url"] for u in merged["source_urls"]]
    assert urls == ["https://a.example/", "https://b.example/"]  # sorted


def test_merge_dedupes_source_url_by_url_key():
    existing = _valid_record()
    existing["source_urls"] = [
        {"url": "https://a.example/", "first_seen_at": "2026-04-10T00:00:00Z",
         "last_verified_at": "2026-04-10T00:00:00Z", "status": "live"}
    ]
    incoming = {"source_urls": [
        {"url": "https://a.example/", "first_seen_at": "2026-04-12T00:00:00Z",
         "last_verified_at": "2026-04-12T00:00:00Z", "status": "live"}
    ]}
    merged = merge_record(existing, incoming)
    assert len(merged["source_urls"]) == 1
    # last_verified_at updated to the later timestamp
    assert merged["source_urls"][0]["last_verified_at"] == "2026-04-12T00:00:00Z"


def test_merge_adds_filename_alias_sorted_and_deduped():
    existing = _valid_record()
    existing["filename_aliases"] = ["a.pdf"]
    incoming = {"filename_aliases": ["c.pdf", "b.pdf", "a.pdf"]}
    merged = merge_record(existing, incoming)
    assert merged["filename_aliases"] == ["a.pdf", "b.pdf", "c.pdf"]


def test_merge_adds_found_in_entry():
    existing = _valid_record()
    existing["found_in"] = []
    incoming = {"found_in": [
        {"type": "repo", "ref": "skot/bitaxe", "path": "datasheets/R1.pdf",
         "first_seen": "2026-04-10T00:00:00Z"}
    ]}
    merged = merge_record(existing, incoming)
    assert len(merged["found_in"]) == 1


def test_merge_bumps_last_seen():
    existing = _valid_record()
    existing["last_seen"] = "2026-04-10T00:00:00Z"
    incoming = {"filename_aliases": ["new.pdf"]}
    merged = merge_record(existing, incoming, now="2026-04-11T00:00:00Z")
    assert merged["last_seen"] == "2026-04-11T00:00:00Z"


def test_merge_preserves_first_seen():
    existing = _valid_record()
    existing["first_seen"] = "2026-04-10T00:00:00Z"
    incoming = {"filename_aliases": ["new.pdf"]}
    merged = merge_record(existing, incoming, now="2026-04-11T00:00:00Z")
    assert merged["first_seen"] == "2026-04-10T00:00:00Z"


# === iter_records / find_by_mpn / find_by_url / find_by_sha256_prefix ===

def _seed_three_records(tmp):
    """Helper: write three valid records with distinct MPNs and URLs."""
    records = []
    for i, (sha, mpn, url) in enumerate([
        ("aa" * 32, "R1", "https://a.example/r1.pdf"),
        ("bb" * 32, "R2", "https://a.example/r2.pdf"),
        ("cc" * 32, "R3", "https://b.example/r3.pdf"),
    ]):
        rec = _valid_record()
        rec["sha256"] = sha
        rec["mpns"] = [{"mpn": mpn, "primary": True}]
        rec["source_urls"] = [{
            "url": url,
            "first_seen_at": "2026-04-10T00:00:00Z",
            "last_verified_at": "2026-04-10T00:00:00Z",
            "status": "live",
        }]
        save_record(rec)
        records.append(rec)
    return records


def test_iter_records_yields_all():
    def inner(tmp):
        _seed_three_records(tmp)
        found = list(iter_records())
        assert len(found) == 3
        shas = {r["sha256"] for r in found}
        assert shas == {"aa" * 32, "bb" * 32, "cc" * 32}
    _with_temp_manifest_dir(inner)


def test_iter_records_empty_dir():
    def inner(tmp):
        assert list(iter_records()) == []
    _with_temp_manifest_dir(inner)


def test_find_by_mpn_exact_match():
    def inner(tmp):
        _seed_three_records(tmp)
        matches = find_by_mpn("R2")
        assert len(matches) == 1
        assert matches[0]["sha256"] == "bb" * 32
    _with_temp_manifest_dir(inner)


def test_find_by_mpn_matches_alias():
    def inner(tmp):
        rec = _valid_record()
        rec["sha256"] = "dd" * 32
        rec["mpns"] = [
            {"mpn": "AD8605", "primary": True},
            {"mpn": "AD8606", "primary": False},
        ]
        save_record(rec)
        assert len(find_by_mpn("AD8606")) == 1
    _with_temp_manifest_dir(inner)


def test_find_by_mpn_no_match():
    def inner(tmp):
        _seed_three_records(tmp)
        assert find_by_mpn("DOES_NOT_EXIST") == []
    _with_temp_manifest_dir(inner)


def test_find_by_url_exact_match():
    def inner(tmp):
        _seed_three_records(tmp)
        matches = find_by_url("https://a.example/r1.pdf")
        assert len(matches) == 1
        assert matches[0]["sha256"] == "aa" * 32
    _with_temp_manifest_dir(inner)


def test_find_by_sha256_prefix_match():
    def inner(tmp):
        _seed_three_records(tmp)
        matches = find_by_sha256_prefix("aa")
        assert len(matches) == 1
    _with_temp_manifest_dir(inner)


def test_find_by_sha256_prefix_ambiguous():
    """Common prefix across records returns all matches."""
    def inner(tmp):
        for sha in ["abcdef" + "0" * 58, "abcdef" + "1" * 58]:
            rec = _valid_record()
            rec["sha256"] = sha
            save_record(rec)
        assert len(find_by_sha256_prefix("abcdef")) == 2
    _with_temp_manifest_dir(inner)


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
