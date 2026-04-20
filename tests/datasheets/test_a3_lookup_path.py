"""A3.1 — raw lookup() + trusted()/best() path.

Covers §3.1 (canned-correct positive flow), §3.2 (staleness detection),
§3.3 (pure-read invariant) of the A3/A4 joint test plan.

Scope: Tracks 2.3 + 2.4 surfaces exercised through `lookup()` →
`DatasheetFacts` → `best()` / `trusted()` / `has_data()`. No compat
wrapper here (A3.2). No synthetic liars (A3.3). No v1.3 divergence (A4).

Note: tri-state signal (has_data + trusted combination) is split across
A3.1 and A3.3. A3.1 covers case 1 (missing — has_data=False) directly
and case 3 (some trusted — implicit in best()/trusted() positive tests).
Case 2 (below-gate — has_data=True, trusted=[]) lands in A3.3's liar
denial tests (lie_correct_value_low_conf pattern).

Convention: plain functions + tempfile.TemporaryDirectory context
manager, matching harness run_tests.py subprocess model. No pytest
dependency.
"""

TIER = "unit"

import hashlib
import json
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(HARNESS_DIR))

# Fixture import triggers sys.path setup for datasheet_types / datasheet_lookup
# as a side effect of loading the fixtures package __init__.
import tests.datasheets.fixtures  # noqa: F401 — sys.path side effect
from tests.datasheets.fixtures.pdf import write_cache_with_pdf


# ===========================================================================
# §3.1 — canned-correct positive flow
# ===========================================================================

def test_lookup_returns_facts_for_present_mpn():
    """lookup() returns a populated DatasheetFacts for a cached MPN."""
    from datasheet_lookup import lookup

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
        assert facts is not None, "lookup should return facts for cached MPN"
        assert facts.source.mpn == "LM2596-ADJ"
        # Fixture template populates regulator + base.
        assert facts.regulator is not None
        assert facts.regulator.topology == "buck"


def test_lookup_returns_none_for_missing_mpn():
    """lookup() returns None for an MPN not in the cache."""
    from datasheet_lookup import lookup

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        assert lookup("DOES-NOT-EXIST", cache_dir=cache_dir) is None


def test_lookup_returns_none_for_malformed_cache():
    """lookup() returns None when the cache file exists but is invalid JSON."""
    from datasheet_lookup import lookup

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = Path(tmp) / "extracted"
        cache_dir.mkdir()
        (cache_dir / "BAD-MPN.json").write_text("{ not valid json")
        assert lookup("BAD-MPN", cache_dir=cache_dir) is None


def test_best_returns_highest_trust_entry():
    """best() returns the first SpecValue at or above the gate, preserving
    extractor order (first-match-wins per Track 2.4 design)."""
    from datasheet_lookup import lookup
    from datasheet_types import best

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    # Fixture's recommended_operating["VIN"] has a high-confidence
    # deterministic entry.
    vin_specs = facts.base.recommended_operating["VIN"]
    picked = best(vin_specs, min_confidence="high")
    assert picked is not None, "fixture has a high-confidence VIN entry"
    assert picked.evidence.confidence == "high"


def test_trusted_filters_to_min_confidence():
    """trusted() returns all SpecValue entries at or above the gate."""
    from datasheet_lookup import lookup
    from datasheet_types import trusted

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    vin_specs = facts.base.recommended_operating["VIN"]
    high = trusted(vin_specs, min_confidence="high")
    med = trusted(vin_specs, min_confidence="medium")
    low = trusted(vin_specs, min_confidence="low")

    # Monotonic: each tier is a superset of the tier above.
    assert set(id(x) for x in high).issubset(id(x) for x in med)
    assert set(id(x) for x in med).issubset(id(x) for x in low)


def test_has_data_true_for_non_empty_specs():
    """has_data() returns True for any non-empty list, regardless of confidence."""
    from datasheet_lookup import lookup
    from datasheet_types import has_data

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    assert has_data(facts.base.recommended_operating["VIN"]) is True


def test_has_data_false_for_empty_or_none():
    """has_data() returns False for both None and empty list."""
    from datasheet_types import has_data

    assert has_data(None) is False
    assert has_data([]) is False


def test_tristate_field_missing_has_data_false():
    """Tri-state case 1: field was not extracted (None) → has_data=False."""
    from datasheet_lookup import lookup
    from datasheet_types import has_data, trusted

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    # Pick a field absent from the LM2596-ADJ fixture's absolute_max.
    missing = facts.base.absolute_max.get("NONEXISTENT_PARAM")
    assert has_data(missing) is False
    assert trusted(missing, min_confidence="low") == []


# ===========================================================================
# §3.2 — staleness detection
# ===========================================================================

def test_stale_flag_false_when_pdf_sha_matches_cache():
    """facts.stale is False when PDF on disk hashes to the cached source.sha256."""
    from datasheet_lookup import lookup

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
        assert facts is not None
        assert facts.stale is False


def test_stale_flag_true_when_pdf_sha_mismatch():
    """facts.stale is True when PDF on disk hashes differently."""
    from datasheet_lookup import lookup

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), pdf_sha_override="0" * 64)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
        assert facts is not None
        assert facts.stale is True


def test_stale_reason_is_STALE_PDF_HASH_MISMATCH_constant():
    """Stale-reason on hash mismatch uses the public STALE_PDF_HASH_MISMATCH
    constant — detectors that want to branch on reason shouldn't string-
    compare arbitrary values."""
    from datasheet_lookup import lookup, STALE_PDF_HASH_MISMATCH

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), pdf_sha_override="0" * 64)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
        assert facts is not None
        # Private attribute per Track 2.3 design — tested against the
        # public constant so downstream code has a stable contract.
        assert facts._cache_context.stale_reason == STALE_PDF_HASH_MISMATCH


def test_stale_flag_true_when_pdf_missing():
    """facts.stale is True when the referenced PDF doesn't exist on disk."""
    from datasheet_lookup import lookup

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, pdf_path = write_cache_with_pdf(Path(tmp), write_pdf=False)
        assert not pdf_path.exists(), "test pre-condition: PDF absent"
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
        assert facts is not None
        assert facts.stale is True


def test_stale_reason_is_STALE_PDF_MISSING_constant():
    """Stale-reason on missing PDF uses the public STALE_PDF_MISSING constant."""
    from datasheet_lookup import lookup, STALE_PDF_MISSING

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp), write_pdf=False)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
        assert facts is not None
        assert facts._cache_context.stale_reason == STALE_PDF_MISSING


def test_stale_flag_survives_facts_round_trip_through_helpers():
    """best()/trusted()/has_data() don't mutate or strip facts.stale.

    Track 2.3 invariant: _cache_context is non-dataclass property; Track 2.2
    round-trip ignores it. This test locks that the helper layer also doesn't
    accidentally strip it via intermediate dataclass reconstruction.
    """
    from datasheet_lookup import lookup
    from datasheet_types import best, trusted, has_data

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), pdf_sha_override="0" * 64)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    assert facts.stale is True

    # Run helpers; they should be read-only w.r.t. facts.
    _ = best(facts.base.recommended_operating["VIN"], min_confidence="low")
    _ = trusted(facts.base.recommended_operating["VIN"], min_confidence="low")
    _ = has_data(facts.base.recommended_operating["VIN"])

    # facts.stale unchanged.
    assert facts.stale is True


# ===========================================================================
# §3.3 — pure-read invariant
# ===========================================================================

def test_lookup_makes_no_network_calls():
    """lookup() never triggers network I/O — monkey-patched for proof."""
    from datasheet_lookup import lookup

    calls = []

    def _trip(*args, **kwargs):
        calls.append(("network", args, kwargs))
        raise RuntimeError("lookup() must not make network calls")

    # Patch common network entry points. If lookup() ever grows a network
    # path, at least one of these should trip.
    import urllib.request
    original_urlopen = urllib.request.urlopen
    urllib.request.urlopen = _trip
    try:
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir, _ = write_cache_with_pdf(Path(tmp))
            facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
            assert facts is not None
        assert calls == [], f"lookup() made network calls: {calls}"
    finally:
        urllib.request.urlopen = original_urlopen


def test_lookup_triggers_no_subprocess():
    """lookup() never spawns subprocesses — monkey-patched for proof."""
    from datasheet_lookup import lookup

    calls = []

    def _trip(*args, **kwargs):
        calls.append(("subprocess", args, kwargs))
        raise RuntimeError("lookup() must not spawn subprocesses")

    import subprocess
    original_run = subprocess.run
    original_popen = subprocess.Popen
    subprocess.run = _trip
    subprocess.Popen = _trip
    try:
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir, _ = write_cache_with_pdf(Path(tmp))
            facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
            assert facts is not None
        assert calls == [], f"lookup() spawned subprocesses: {calls}"
    finally:
        subprocess.run = original_run
        subprocess.Popen = original_popen


def test_lookup_writes_no_files_in_cache_dir():
    """lookup() is pure-read — the cache file's mtime + size don't change.

    We can't monkey-patch all file-write paths without false positives
    (the fixture itself writes into tmp_path), so we assert on outcome:
    cache file identity/content is unchanged pre/post-lookup.
    """
    from datasheet_lookup import lookup, sanitize_mpn

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        cache_file = cache_dir / f"{sanitize_mpn('LM2596-ADJ')}.json"
        before_bytes = cache_file.read_bytes()
        before_mtime = cache_file.stat().st_mtime_ns

        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
        assert facts is not None

        after_bytes = cache_file.read_bytes()
        after_mtime = cache_file.stat().st_mtime_ns
        assert before_bytes == after_bytes, "lookup modified the cache file"
        assert before_mtime == after_mtime, "lookup touched the cache file mtime"


def test_lookup_ignores_families_subdirectory():
    """Track 2.6 hygiene invariant, harness-side complement.

    Main-repo's test_lookup_ignores_families_subdirectory_coexisting_with_cache_files
    proves `lookup("_families")` returns None. This asserts the positive
    side: when the cache dir contains BOTH a valid cache file AND a populated
    _families/ subdir, lookup() returns the right record and doesn't walk
    into _families/.
    """
    from datasheet_lookup import lookup

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        # Populate _families/ with something that would look like a cache
        # file if lookup() walked into subdirectories.
        families_dir = cache_dir / "_families"
        families_dir.mkdir()
        (families_dir / "FAMILY.json").write_text('{"garbage": true}')
        (families_dir / "LM2596-ADJ.json").write_text('{"garbage": true}')

        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
        assert facts is not None
        # Ensure we got the real record, not the garbage from _families/.
        assert facts.regulator is not None
        assert facts.regulator.topology == "buck"


# ===========================================================================
# __main__ runner — harness convention (run_tests.py subprocess model)
# ===========================================================================

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
    print(f"\n{passed} passed, {failed} failed ({len(tests)} total)")
    sys.exit(1 if failed else 0)
