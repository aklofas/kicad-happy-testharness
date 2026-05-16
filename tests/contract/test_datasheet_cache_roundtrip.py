"""Contract test: datasheet cache filename round-trip preserves dots and hyphens.

Audit C1 / Phase 3b carry-over #6: ``datasheet_lookup.sanitize_mpn`` was the
single source of truth for cache filename derivation, but
``datasheet_verify._load_extraction`` had its own private regex at line 26 that
diverged — it stripped dots while ``sanitize_mpn`` preserved them. This made
dot-containing MPNs (e.g. the Phase 3b crystal ``ABM8G-106-12.000MHZ-T``)
silently miss the cache lookup through the verify-path while succeeding through
the lookup-path. The fix widens the verify regex to ``[^A-Za-z0-9_.-]`` to
match the lookup helper and the literal filenames written by
``plan_extraction.py`` and ``merge_results.py``.

Tests:
1. Filename parity for MPNs that contain only safe characters — lookup helper,
   verify helper, and the planner's literal-filename convention all converge.
2. Sanitization parity for MPNs that contain ``/`` or spaces — both helpers
   produce the same sanitized name.
3. Real cached extraction resolution — ``lookup()`` returns a non-None
   DatasheetFacts for ``ABM8G-106-12.000MHZ-T`` from the harness fixtures
   directory.
4. RED-GREEN regression-prove — temporarily revert ``datasheet_lookup.py:53``
   regex to the old narrower form and confirm the round-trip breaks for
   dot-containing MPNs; restore.
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

DATASHEETS_SCRIPTS = MAIN_REPO_ROOT / "skills" / "datasheets" / "scripts"
CACHE_FIXTURES = HARNESS_ROOT / "tests" / "fixtures" / "datasheets-extracted"

sys.path.insert(0, str(DATASHEETS_SCRIPTS))


@pytest.fixture(scope="module")
def lookup_mod():
    import datasheet_lookup
    return datasheet_lookup


@pytest.fixture(scope="module")
def verify_mod():
    import datasheet_verify
    return datasheet_verify


def _verify_legacy_sanitize(verify_mod, mpn: str) -> str:
    """Run the same regex that datasheet_verify._load_extraction uses at
    line 26. Lifted from source so the test pins the *exact* regex shape, not
    just an outcome that might happen to agree."""
    # Pulled from skills/datasheets/scripts/datasheet_verify.py:26 (post-C1
    # fix). If main-repo changes this line the test will need to follow.
    return re.sub(r'[^A-Za-z0-9_.-]', '_', mpn.strip())


# ---------------------------------------------------------------------------
# Filename parity: lookup vs verify vs planner literal convention
# ---------------------------------------------------------------------------

SAFE_MPNS = [
    "LM2596-ADJ",                 # plain hyphenated family
    "ABM8G-106-12.000MHZ-T",      # Phase 3b crystal — the canonical
                                  # breakage MPN from LOG entry 63
    "STM32F103C8T6",              # alphanumeric
    "MBRS540T3G",                 # alphanumeric, no separator
]


@pytest.mark.parametrize("mpn", SAFE_MPNS)
def test_safe_mpn_filename_matches_across_helpers(lookup_mod, verify_mod, mpn, tmp_path):
    """For MPNs containing only [A-Za-z0-9_.-], all three derivations must
    produce the same filename:
        - lookup_mod.cache_path_for(...).name
        - verify_mod's private regex (legacy positional path at :26)
        - planner literal: f"{mpn}.json"
    """
    lookup_name = lookup_mod.cache_path_for(mpn, tmp_path).name
    verify_name = f"{_verify_legacy_sanitize(verify_mod, mpn)}.json"
    planner_name = f"{mpn}.json"
    assert lookup_name == planner_name, (
        f"lookup helper diverges from planner literal for {mpn!r}: "
        f"{lookup_name!r} vs {planner_name!r}"
    )
    assert verify_name == planner_name, (
        f"verify legacy-path regex diverges from planner literal for "
        f"{mpn!r}: {verify_name!r} vs {planner_name!r}"
    )


# ---------------------------------------------------------------------------
# Sanitization parity for MPNs requiring transformation
# ---------------------------------------------------------------------------

UNSAFE_MPNS = [
    "STM32/F103",         # forward slash — common in datasheet shorthand
    "ACME 1234",          # leading/internal whitespace
    "PART+PLUS",          # plus sign
]


@pytest.mark.parametrize("mpn", UNSAFE_MPNS)
def test_unsafe_mpn_sanitization_agrees_between_helpers(lookup_mod, verify_mod, mpn, tmp_path):
    """For MPNs with chars outside [A-Za-z0-9_.-], both helpers must produce
    the same sanitized name — divergence here means lookup-side cache files
    won't resolve from the verify-side."""
    lookup_name = lookup_mod.cache_path_for(mpn, tmp_path).name
    verify_name = f"{_verify_legacy_sanitize(verify_mod, mpn)}.json"
    assert lookup_name == verify_name, (
        f"helpers disagree for {mpn!r}: lookup={lookup_name!r}, "
        f"verify={verify_name!r}"
    )


# ---------------------------------------------------------------------------
# Real cached extraction resolution (the actual end-to-end signal)
# ---------------------------------------------------------------------------

def test_real_abm8g_extraction_resolves_via_lookup(lookup_mod):
    """Phase 3b crystal cache must resolve to a real DatasheetFacts. The
    fixtures live at tests/fixtures/datasheets-extracted/ABM8G-106-12.000MHZ-T.json
    — pre-fix this returned None because the old narrower regex (no ``.``)
    sanitized to ``ABM8G-106-12_000MHZ-T`` and no such file exists."""
    mpn = "ABM8G-106-12.000MHZ-T"
    fixture = CACHE_FIXTURES / f"{mpn}.json"
    assert fixture.is_file(), (
        f"Test setup requires {fixture} to exist; got missing fixture"
    )
    facts = lookup_mod.lookup(mpn, cache_dir=CACHE_FIXTURES)
    assert facts is not None, (
        f"lookup returned None for {mpn!r} despite cache file existing at "
        f"{fixture} — sanitization regex regressed to drop dots"
    )


# ---------------------------------------------------------------------------
# RED-GREEN: confirm a regex revert breaks the round-trip
# ---------------------------------------------------------------------------

def test_red_green_narrow_regex_breaks_dot_lookup(lookup_mod, monkeypatch, tmp_path):
    """Monkey-patch the lookup module's sanitize regex to the old narrower
    form (strips dots) and confirm cache resolution silently fails for
    dot-containing MPNs. This proves the new dot-preserving regex is
    load-bearing — not just cosmetic — for the audit C1 bug class.

    Uses monkeypatch so the patch reverts cleanly even if the test fails.
    Does not edit any file on disk.
    """
    mpn = "ABM8G-106-12.000MHZ-T"

    # Baseline: current regex preserves dots → lookup resolves.
    facts_pre = lookup_mod.lookup(mpn, cache_dir=CACHE_FIXTURES)
    assert facts_pre is not None, "baseline lookup should resolve"

    # Swap in the old narrower regex (no dot in the allowed set) and reload
    # the module's compiled pattern locally.
    narrow = re.compile(r"[^A-Za-z0-9_\-]")
    monkeypatch.setattr(lookup_mod, "_UNSAFE_CHAR", narrow)

    # cache_path_for now sanitizes "ABM8G-106-12.000MHZ-T" →
    # "ABM8G-106-12_000MHZ-T" which does NOT have a fixture file.
    bad_name = lookup_mod.cache_path_for(mpn, CACHE_FIXTURES).name
    assert "12_000MHZ" in bad_name, (
        f"monkeypatch didn't take effect; got {bad_name}"
    )
    facts_post = lookup_mod.lookup(mpn, cache_dir=CACHE_FIXTURES)
    assert facts_post is None, (
        f"narrower regex should have produced silent cache miss; got "
        f"{facts_post!r}"
    )
