"""Unit tests for validate/datasheet_db/storage.py."""

TIER = "unit"

import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from validate.datasheet_db.storage import (
    _sanitize_mpn, _truncate_to_byte_limit, canonical_filename
)


# === _sanitize_mpn ===

def test_sanitize_mpn_simple():
    """Plain alphanumeric MPN passes through unchanged."""
    assert _sanitize_mpn("STM32F405RGT6") == "STM32F405RGT6"


def test_sanitize_mpn_replaces_slash():
    """Forward slash is replaced with underscore."""
    assert _sanitize_mpn("AD8605/8606") == "AD8605_8606"


def test_sanitize_mpn_replaces_backslash():
    """Backslash is replaced with underscore."""
    assert _sanitize_mpn("FOO\\BAR") == "FOO_BAR"


def test_sanitize_mpn_replaces_colon():
    """Colon is replaced."""
    assert _sanitize_mpn("part:rev") == "part_rev"


def test_sanitize_mpn_replaces_special_characters():
    """All of /\\:*?"<>| are replaced."""
    assert _sanitize_mpn("a/b\\c:d*e?f\"g<h>i|j") == "a_b_c_d_e_f_g_h_i_j"


def test_sanitize_mpn_replaces_whitespace():
    """Whitespace is replaced."""
    assert _sanitize_mpn("AD 8605 REEL7") == "AD_8605_REEL7"
    assert _sanitize_mpn("AD\t8605") == "AD_8605"


def test_sanitize_mpn_replaces_non_ascii():
    """Non-ASCII characters are replaced with underscore.

    Note: leading/trailing replacement underscores are stripped by rule 5,
    so "Ω-01" → "_-01" (after rule 1) → "-01" (after rule 5 strip).
    Plan had "_-01" as expected; corrected to "-01" to match documented rules.
    """
    assert _sanitize_mpn("résistor") == "r_sistor"
    assert _sanitize_mpn("Ω-01") == "-01"


def test_sanitize_mpn_collapses_runs():
    """Runs of underscore collapse to one."""
    assert _sanitize_mpn("AD//8605") == "AD_8605"
    assert _sanitize_mpn("AD   8605") == "AD_8605"


def test_sanitize_mpn_strips_leading_trailing():
    """Leading and trailing underscores and dots are stripped."""
    assert _sanitize_mpn("/AD8605/") == "AD8605"
    assert _sanitize_mpn(".AD8605.") == "AD8605"
    assert _sanitize_mpn("__AD8605__") == "AD8605"


def test_sanitize_mpn_pathological_returns_empty():
    """MPN consisting only of problematic chars returns empty string."""
    assert _sanitize_mpn("///") == ""
    assert _sanitize_mpn("   ") == ""


# === _truncate_to_byte_limit ===

def test_truncate_short_name_unchanged():
    """A name well under the limit is returned as-is."""
    assert _truncate_to_byte_limit("STM32F405RGT6", 130) == "STM32F405RGT6"


def test_truncate_at_exact_limit():
    """A name exactly at the byte limit is returned as-is."""
    name = "A" * 130
    assert _truncate_to_byte_limit(name, 130) == name


def test_truncate_over_limit_ascii():
    """An ASCII name over the limit is truncated with a trailing underscore."""
    name = "A" * 200
    out = _truncate_to_byte_limit(name, 130)
    assert len(out.encode("utf-8")) <= 130
    assert out.endswith("_")


def test_truncate_counts_bytes_not_chars():
    """Byte-based truncation, not character-based.

    The TH-013 143-byte eCryptfs limit is measured in bytes after UTF-8
    encoding. All characters going into this function are already
    sanitized to ASCII, but we still use byte length consistently with the
    rest of the harness (see utils._truncate_with_hash)."""
    # Every char is 1 byte since sanitize removed non-ASCII
    name = "X" * 140
    out = _truncate_to_byte_limit(name, 130)
    assert len(out.encode("utf-8")) <= 130


def test_truncate_tiny_limit():
    """A byte limit smaller than the current name truncates correctly."""
    assert _truncate_to_byte_limit("ABCDEFG", 3) == "AB_"


# === canonical_filename ===

def _make_record(primary_mpn, sha256):
    """Build a minimal manifest record dict for canonical_filename tests."""
    return {
        "sha256": sha256,
        "mpns": [{"mpn": primary_mpn, "primary": True}],
    }


def test_canonical_filename_simple():
    """Simple primary MPN produces {mpn}-{sha256[:8]}.pdf."""
    rec = _make_record("STM32F405RGT6", "ab1234cdef0123456789abcdef0123456789abcdef0123456789abcdef012345")
    assert canonical_filename(rec) == "STM32F405RGT6-ab1234cd.pdf"


def test_canonical_filename_sanitizes_primary_mpn():
    """MPN with bad characters is sanitized in the filename."""
    rec = _make_record("AD8605/8606", "cd1234cdef0123456789abcdef0123456789abcdef0123456789abcdef012345")
    assert canonical_filename(rec) == "AD8605_8606-cd1234cd.pdf"


def test_canonical_filename_empty_primary_fallback():
    """Pathological MPN that sanitizes to empty uses 'unknown' fallback."""
    rec = _make_record("///", "ef1234cdef0123456789abcdef0123456789abcdef0123456789abcdef012345")
    assert canonical_filename(rec) == "unknown-ef1234cd.pdf"


def test_canonical_filename_truncates_long_primary():
    """Primary MPN over byte budget is truncated to fit the 143-byte filename limit."""
    long_mpn = "X" * 200  # 200 bytes, well over the 130-byte budget for the MPN
    sha = "aa" * 32  # 64 hex chars
    rec = _make_record(long_mpn, sha)
    out = canonical_filename(rec)
    # Total filename must fit in the 143-byte TH-013 limit
    assert len(out.encode("utf-8")) <= 143
    # Must still end in -{hash}.pdf
    assert out.endswith("-aaaaaaaa.pdf")


def test_canonical_filename_total_byte_budget():
    """Filename budget is 143 bytes including the -{hash}.pdf suffix (13 bytes)."""
    # Budget for primary_mpn is 143 - 13 = 130 bytes
    mpn_130 = "M" * 130
    sha = "bb" * 32
    rec = _make_record(mpn_130, sha)
    out = canonical_filename(rec)
    assert len(out.encode("utf-8")) <= 143
    # At exactly 130, no truncation needed
    assert out == mpn_130 + "-bbbbbbbb.pdf"


def test_canonical_filename_raises_on_missing_primary():
    """Record with no primary MPN is a programming error — raise."""
    rec = {
        "sha256": "cc" * 32,
        "mpns": [{"mpn": "X", "primary": False}],
    }
    try:
        canonical_filename(rec)
        assert False, "should have raised"
    except ValueError as e:
        assert "primary" in str(e).lower()


def test_canonical_filename_raises_on_empty_mpns():
    """Record with empty mpns list is a programming error — raise."""
    rec = {"sha256": "dd" * 32, "mpns": []}
    try:
        canonical_filename(rec)
        assert False, "should have raised"
    except ValueError:
        pass


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
