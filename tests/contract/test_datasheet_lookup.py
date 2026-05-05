"""Contract tests for datasheet_lookup — the consumer API entry point.

Track 2.3 of the v1.4 datasheet extraction work. Tests the lookup()
facade, MPN sanitization, cache-path resolution, and PDF staleness
detection. All tests are self-contained via pytest.tmp_path — no
committed test cache files.
"""
from __future__ import annotations

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import hashlib
import json
import sys
from pathlib import Path

import pytest

SCHEMA_DIR = MAIN_REPO_ROOT / "skills" / "datasheets" / "schemas"
FIXTURE_DIR = SCHEMA_DIR / "fixtures"

# Make both the datasheet_types package and the scripts module importable.
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets" / "scripts"))


def _load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# sanitize_mpn
# ---------------------------------------------------------------------------

def test_sanitize_mpn_clean_passthrough() -> None:
    """Already-clean MPNs pass through unchanged."""
    from datasheet_lookup import sanitize_mpn

    assert sanitize_mpn("LM2596-ADJ") == "LM2596-ADJ"
    assert sanitize_mpn("STM32F103C8T6") == "STM32F103C8T6"
    assert sanitize_mpn("RC0603FR-071KL") == "RC0603FR-071KL"


def test_sanitize_mpn_replaces_unsafe_chars() -> None:
    """Slashes, dots, spaces, percent signs → underscore."""
    from datasheet_lookup import sanitize_mpn

    assert sanitize_mpn("STM32/F103") == "STM32_F103"
    assert sanitize_mpn("LM2596.ADJ") == "LM2596_ADJ"
    assert sanitize_mpn("ACME 1234") == "ACME_1234"
    assert sanitize_mpn("PART%V2") == "PART_V2"


def test_sanitize_mpn_strips_whitespace() -> None:
    """Leading/trailing whitespace is stripped before sanitization."""
    from datasheet_lookup import sanitize_mpn

    assert sanitize_mpn("  LM2596-ADJ  ") == "LM2596-ADJ"
    assert sanitize_mpn("\tLM2596-ADJ\n") == "LM2596-ADJ"


def test_sanitize_mpn_preserves_underscore_and_hyphen() -> None:
    """_ and - are safe filename characters and preserved."""
    from datasheet_lookup import sanitize_mpn

    assert sanitize_mpn("LM_2596-ADJ") == "LM_2596-ADJ"


# ---------------------------------------------------------------------------
# cache_path_for
# ---------------------------------------------------------------------------

def test_cache_path_for_composes_sanitized_filename() -> None:
    """cache_path_for returns <cache_dir>/<sanitized_mpn>.json."""
    from datasheet_lookup import cache_path_for

    cache_dir = Path("/tmp/test-cache")
    assert cache_path_for("LM2596-ADJ", cache_dir) == cache_dir / "LM2596-ADJ.json"
    assert cache_path_for("STM32/F103", cache_dir) == cache_dir / "STM32_F103.json"


# ---------------------------------------------------------------------------
# lookup() — core read path (no staleness yet)
# ---------------------------------------------------------------------------

def test_lookup_returns_none_when_cache_dir_missing(tmp_path: Path) -> None:
    """lookup returns None when the cache directory doesn't exist."""
    from datasheet_lookup import lookup

    missing_cache_dir = tmp_path / "does-not-exist"
    assert lookup("LM2596-ADJ", cache_dir=missing_cache_dir) is None


def test_lookup_returns_none_when_cache_file_missing(tmp_path: Path) -> None:
    """lookup returns None when the cache file for the MPN doesn't exist."""
    from datasheet_lookup import lookup

    cache_dir = tmp_path / "extracted"
    cache_dir.mkdir()
    assert lookup("NOT-CACHED", cache_dir=cache_dir) is None


def test_lookup_returns_none_when_cache_json_malformed(tmp_path: Path) -> None:
    """lookup returns None when the cache file contains malformed JSON."""
    from datasheet_lookup import lookup

    cache_dir = tmp_path / "extracted"
    cache_dir.mkdir()
    (cache_dir / "BROKEN.json").write_text("{not valid json")
    assert lookup("BROKEN", cache_dir=cache_dir) is None


def test_lookup_returns_none_when_cache_file_binary_corrupt(tmp_path: Path) -> None:
    """lookup returns None (not an exception) when the cache file is
    non-UTF-8 binary garbage — guards against read_text raising
    UnicodeDecodeError that would otherwise propagate to the caller.
    """
    from datasheet_lookup import lookup

    cache_dir = tmp_path / "extracted"
    cache_dir.mkdir()
    # Write invalid UTF-8 bytes (0xff 0xfe is not a valid UTF-8 sequence).
    (cache_dir / "CORRUPT.json").write_bytes(b"\xff\xfe\x00\x01not-json")
    assert lookup("CORRUPT", cache_dir=cache_dir) is None


def test_lookup_returns_none_when_cache_violates_shape(tmp_path: Path) -> None:
    """lookup returns None when the cache file parses as JSON but is
    missing required DatasheetFacts fields."""
    from datasheet_lookup import lookup

    cache_dir = tmp_path / "extracted"
    cache_dir.mkdir()
    # Valid JSON but no 'schema_version', 'source', 'extraction', 'base'.
    (cache_dir / "INCOMPLETE.json").write_text(json.dumps({"hello": "world"}))
    assert lookup("INCOMPLETE", cache_dir=cache_dir) is None


def test_lookup_returns_datasheet_facts_for_valid_cache(tmp_path: Path) -> None:
    """lookup returns a populated DatasheetFacts when the cache is valid."""
    from datasheet_lookup import lookup
    from datasheet_types.extraction import DatasheetFacts

    cache_dir = tmp_path / "extracted"
    cache_dir.mkdir()
    # Copy the LM2596-ADJ fixture into the cache dir as the real cache file.
    fixture = _load_json(FIXTURE_DIR / "lm2596-adj.example.json")
    (cache_dir / "LM2596-ADJ.json").write_text(json.dumps(fixture))

    facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
    assert facts is not None
    assert isinstance(facts, DatasheetFacts)
    assert facts.source.mpn == "LM2596-ADJ"
    assert facts.base.family == "step-down switching regulator"
    assert facts.regulator is not None
    assert facts.regulator.topology == "buck"


def test_lookup_attaches_cache_path_to_returned_facts(tmp_path: Path) -> None:
    """lookup attaches the cache path so ds.cache_path returns it."""
    from datasheet_lookup import lookup

    cache_dir = tmp_path / "extracted"
    cache_dir.mkdir()
    fixture = _load_json(FIXTURE_DIR / "lm2596-adj.example.json")
    cache_file = cache_dir / "LM2596-ADJ.json"
    cache_file.write_text(json.dumps(fixture))

    facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
    assert facts is not None
    assert facts.cache_path == cache_file


def test_lookup_quality_passthrough(tmp_path: Path) -> None:
    """lookup-returned facts expose quality via the Task 1 property."""
    from datasheet_lookup import lookup

    cache_dir = tmp_path / "extracted"
    cache_dir.mkdir()
    fixture = _load_json(FIXTURE_DIR / "lm2596-adj.example.json")
    (cache_dir / "LM2596-ADJ.json").write_text(json.dumps(fixture))

    facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
    # LM2596-ADJ fixture has quality_score = 98 (Phase 3a pipeline-produced).
    assert facts.quality == 98


# ---------------------------------------------------------------------------
# Staleness detection
# ---------------------------------------------------------------------------

def _write_cache_with_pdf(
    tmp_path: Path,
    *,
    mpn: str = "LM2596-ADJ",
    pdf_bytes: bytes = b"%PDF-1.4\n%%EOF\n",
    pdf_sha_override: "Optional[str]" = None,
) -> tuple[Path, Path]:
    """Test helper: build a cache_dir + PDF + cache JSON and return paths.

    The cache JSON's source.sha256 is computed from pdf_bytes UNLESS
    pdf_sha_override is provided (used to simulate a stale cache).
    Returns (cache_dir, pdf_path).
    """
    # datasheets/ is the parent; extracted/ is cache_dir; PDF sits in datasheets/.
    datasheets_dir = tmp_path / "datasheets"
    datasheets_dir.mkdir()
    cache_dir = datasheets_dir / "extracted"
    cache_dir.mkdir()

    pdf_path = datasheets_dir / f"{mpn}.pdf"
    pdf_path.write_bytes(pdf_bytes)

    actual_sha = hashlib.sha256(pdf_bytes).hexdigest()
    cached_sha = pdf_sha_override if pdf_sha_override is not None else actual_sha

    # Use the LM2596-ADJ fixture as a template; override source.sha256
    # and source.local_path to point at our test PDF.
    fixture = _load_json(FIXTURE_DIR / "lm2596-adj.example.json")
    fixture["source"]["mpn"] = mpn
    fixture["source"]["sha256"] = f"sha256:{cached_sha}"
    fixture["source"]["local_path"] = f"{mpn}.pdf"

    (cache_dir / f"{mpn}.json").write_text(json.dumps(fixture))
    return cache_dir, pdf_path


def test_lookup_stale_false_when_pdf_hash_matches(tmp_path: Path) -> None:
    """lookup returns facts.stale=False when PDF hash matches cached sha256."""
    from datasheet_lookup import lookup

    cache_dir, _ = _write_cache_with_pdf(tmp_path)
    facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
    assert facts is not None
    assert facts.stale is False


def test_lookup_stale_true_when_pdf_hash_mismatch(tmp_path: Path) -> None:
    """lookup returns facts.stale=True when PDF on disk differs from cache."""
    from datasheet_lookup import lookup

    # Override with a bogus cached hash so it doesn't match the real PDF.
    bogus_sha = "0" * 64
    cache_dir, _ = _write_cache_with_pdf(tmp_path, pdf_sha_override=bogus_sha)

    facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
    assert facts is not None
    assert facts.stale is True
    # The CacheContext carries the reason too, accessible via the private attr.
    ctx = facts._cache_context
    assert ctx.stale_reason == "pdf_hash_mismatch"


def test_lookup_stale_true_when_pdf_missing(tmp_path: Path) -> None:
    """lookup returns facts.stale=True when source.local_path doesn't exist."""
    from datasheet_lookup import lookup

    cache_dir, pdf_path = _write_cache_with_pdf(tmp_path)
    # Delete the PDF after cache setup to simulate a missing-file staleness.
    pdf_path.unlink()

    facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
    assert facts is not None
    assert facts.stale is True
    ctx = facts._cache_context
    assert ctx.stale_reason == "pdf_missing"


def test_lookup_stale_true_when_source_local_path_is_none(tmp_path: Path) -> None:
    """lookup returns facts.stale=True when source.local_path is None.

    Without a local_path we can't verify freshness, so the safe default
    is to mark the cache stale (consumer triggers re-extraction).
    """
    from datasheet_lookup import lookup

    cache_dir, _ = _write_cache_with_pdf(tmp_path)
    # Mutate the cached fixture to null out local_path.
    cache_file = cache_dir / "LM2596-ADJ.json"
    data = json.loads(cache_file.read_text())
    data["source"]["local_path"] = None
    cache_file.write_text(json.dumps(data))

    facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
    assert facts is not None
    assert facts.stale is True
    ctx = facts._cache_context
    assert ctx.stale_reason == "pdf_missing"


def test_lookup_ignores_families_subdirectory_coexisting_with_cache_files(tmp_path: Path) -> None:
    """lookup() must NOT be confused by a `_families/` subdirectory.

    Track 2.6: `_families/` is reserved for v1.5 Tier 2 family-extraction
    dedup (spec §14). v1.4 code does not read from it, but a real corpus
    cache_dir may contain it. This test locks the invariant that adding
    `_families/` alongside a normal cache file does not alter lookup()
    behavior — neither to spurious False-negative (lookup thinking the
    MPN doesn't exist) nor spurious False-positive (lookup returning
    the directory as a cache file).
    """
    from datasheet_lookup import lookup

    cache_dir, _ = _write_cache_with_pdf(tmp_path)

    # Create the reserved v1.5 subdirectory inside the same cache_dir.
    # Simulates a mid-v1.5 corpus state where families have been written
    # alongside per-MPN caches.
    families_dir = cache_dir / "_families"
    families_dir.mkdir()

    # Also drop a family file inside to confirm the directory's contents
    # are invisible to lookup() (which only checks for <MPN>.json at the
    # cache_dir top level).
    (families_dir / "yageo-rc0603.family.json").write_text("{}")

    # Normal MPN lookup still succeeds.
    facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
    assert facts is not None
    assert facts.source.mpn == "LM2596-ADJ"

    # Lookup for a name that WOULD be a valid sanitized MPN matching the
    # directory name returns None (directory is not a file).
    missing = lookup("_families", cache_dir=cache_dir)
    assert missing is None


def test_lookup_full_happy_path_fresh_cache_with_matching_pdf(tmp_path: Path) -> None:
    """End-to-end happy path: fresh PDF + cache hash match + typed access.

    Stronger invariant than the Task 3 test_lookup_returns_datasheet_facts_for_valid_cache
    (which didn't create a PDF and so implicitly landed in pdf_missing stale
    state). Exercises: stale=False, quality passthrough, cache_path attach,
    typed access across base.pinout and the regulator category extension.
    """
    from datasheet_lookup import lookup

    cache_dir, pdf_path = _write_cache_with_pdf(tmp_path)
    facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    assert facts is not None
    # Staleness: PDF hash matches cache.
    assert facts.stale is False
    assert facts._cache_context.stale_reason is None
    assert facts._cache_context.pdf_path == pdf_path
    # Quality passthrough.
    assert facts.quality == 98
    # Cache path attached.
    assert facts.cache_path == cache_dir / "LM2596-ADJ.json"
    # Typed access across the full composition (Track 2.2).
    assert facts.source.mpn == "LM2596-ADJ"
    assert facts.base.pinout.find(name="ON/OFF").numbers == ["5"]
    assert facts.regulator.topology == "buck"


# ---------------------------------------------------------------------------
# Public API surface — datasheet_types.lookup re-export
# ---------------------------------------------------------------------------

def test_lookup_is_reexported_from_datasheet_types() -> None:
    """Spec §11 consumer pattern: `from datasheet_types import lookup`
    should resolve to the same callable as datasheet_lookup.lookup."""
    import datasheet_types

    assert hasattr(datasheet_types, "lookup"), (
        "datasheet_types must re-export lookup for the spec §11 consumer pattern"
    )
    from datasheet_lookup import lookup as lookup_direct
    assert datasheet_types.lookup is lookup_direct
    # __all__ should include it too for `from datasheet_types import *`.
    assert "lookup" in datasheet_types.__all__
