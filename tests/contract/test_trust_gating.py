"""Contract tests for trust-gating helpers (best, trusted, has_data).

Track 2.4 of the v1.4 datasheet extraction work. Tests the per-field
tri-state API that lets detectors filter list[SpecValue] data by
evidence.confidence (spec §12 per-detector MIN_CONFIDENCE contract).
"""
from __future__ import annotations

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))


def _make_spec(value: float, confidence: str, method: str = "table") -> "SpecValue":
    """Construct a SpecValue with controlled evidence for testing."""
    from datasheet_types.spec_value import SpecValue, Evidence
    return SpecValue(
        unit="V",
        evidence=Evidence(page=1, confidence=confidence, method=method),
        typ=value,
    )


# ---------------------------------------------------------------------------
# has_data
# ---------------------------------------------------------------------------

def test_has_data_none_returns_false() -> None:
    """has_data(None) is False — field was not extracted."""
    from datasheet_types.trust_gating import has_data

    assert has_data(None) is False


def test_has_data_empty_list_returns_false() -> None:
    """has_data([]) is False — extraction produced no values."""
    from datasheet_types.trust_gating import has_data

    assert has_data([]) is False


def test_has_data_non_empty_returns_true() -> None:
    """has_data([spec]) is True regardless of confidence levels."""
    from datasheet_types.trust_gating import has_data

    specs = [_make_spec(1.0, "low")]
    assert has_data(specs) is True


# ---------------------------------------------------------------------------
# best
# ---------------------------------------------------------------------------

def test_best_none_returns_none() -> None:
    """best(None) returns None without inspecting min_confidence."""
    from datasheet_types.trust_gating import best

    assert best(None, min_confidence="low") is None


def test_best_empty_list_returns_none() -> None:
    """best([]) returns None."""
    from datasheet_types.trust_gating import best

    assert best([], min_confidence="low") is None


def test_best_all_below_gate_returns_none() -> None:
    """best with all entries below min_confidence returns None.

    Distinguishes 'present-but-below-gate' from 'missing' — pair with
    has_data() to get the tri-state signal.
    """
    from datasheet_types.trust_gating import best

    specs = [_make_spec(1.0, "low"), _make_spec(2.0, "low")]
    assert best(specs, min_confidence="medium") is None


def test_best_returns_first_matching_entry() -> None:
    """best returns the first SpecValue meeting the gate — preserves
    extractor's intended ordering."""
    from datasheet_types.trust_gating import best

    specs = [
        _make_spec(1.0, "low"),     # below gate
        _make_spec(2.0, "medium"),  # first passing
        _make_spec(3.0, "high"),    # also passes but comes later
    ]
    result = best(specs, min_confidence="medium")
    assert result is not None
    assert result.typ == 2.0  # First match wins — no re-ranking by confidence


def test_best_high_gate_accepts_only_high() -> None:
    """min_confidence='high' filters out medium and low entries."""
    from datasheet_types.trust_gating import best

    specs = [
        _make_spec(1.0, "medium"),
        _make_spec(2.0, "high"),
        _make_spec(3.0, "low"),
    ]
    result = best(specs, min_confidence="high")
    assert result is not None
    assert result.typ == 2.0


def test_best_low_gate_accepts_all() -> None:
    """min_confidence='low' accepts any entry, returns first."""
    from datasheet_types.trust_gating import best

    specs = [_make_spec(1.0, "low"), _make_spec(2.0, "high")]
    result = best(specs, min_confidence="low")
    assert result is not None
    assert result.typ == 1.0  # First-match, not highest-confidence


# ---------------------------------------------------------------------------
# trusted
# ---------------------------------------------------------------------------

def test_trusted_none_returns_empty_list() -> None:
    """trusted(None) returns [] — consumers can iterate without None check."""
    from datasheet_types.trust_gating import trusted

    assert trusted(None, min_confidence="low") == []


def test_trusted_empty_list_returns_empty_list() -> None:
    """trusted([]) returns []."""
    from datasheet_types.trust_gating import trusted

    assert trusted([], min_confidence="low") == []


def test_trusted_filters_below_gate_preserves_order() -> None:
    """trusted returns only entries meeting min_confidence, in input order."""
    from datasheet_types.trust_gating import trusted

    specs = [
        _make_spec(1.0, "low"),     # filtered
        _make_spec(2.0, "high"),    # kept
        _make_spec(3.0, "medium"),  # kept
        _make_spec(4.0, "low"),     # filtered
    ]
    result = trusted(specs, min_confidence="medium")
    assert [s.typ for s in result] == [2.0, 3.0]  # Input order, not sorted


def test_trusted_all_pass_returns_complete_list() -> None:
    """trusted with min_confidence='low' returns every entry unchanged."""
    from datasheet_types.trust_gating import trusted

    specs = [_make_spec(1.0, "low"), _make_spec(2.0, "medium"), _make_spec(3.0, "high")]
    result = trusted(specs, min_confidence="low")
    assert [s.typ for s in result] == [1.0, 2.0, 3.0]


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def test_best_invalid_min_confidence_raises_valueerror() -> None:
    """best() raises ValueError with a clear message when min_confidence is bogus."""
    from datasheet_types.trust_gating import best

    with pytest.raises(ValueError, match="min_confidence must be"):
        best([_make_spec(1.0, "high")], min_confidence="extreme")


def test_trusted_invalid_min_confidence_raises_valueerror() -> None:
    """trusted() raises ValueError likewise."""
    from datasheet_types.trust_gating import trusted

    with pytest.raises(ValueError, match="min_confidence must be"):
        trusted([_make_spec(1.0, "high")], min_confidence="extreme")


def test_best_validates_min_confidence_even_when_specs_is_none() -> None:
    """best() validates min_confidence BEFORE checking specs — a consumer
    passing None specs with an invalid min_confidence gets ValueError
    (not None). Stricter validation over permissive shortcut: detector
    code that constructs min_confidence dynamically should fail fast."""
    from datasheet_types.trust_gating import best

    with pytest.raises(ValueError, match="min_confidence must be"):
        best(None, min_confidence="extreme")


def test_trusted_validates_min_confidence_even_when_specs_is_none() -> None:
    """trusted() validates min_confidence BEFORE checking specs — parallel
    invariant to best()."""
    from datasheet_types.trust_gating import trusted

    with pytest.raises(ValueError, match="min_confidence must be"):
        trusted(None, min_confidence="extreme")


def test_best_safely_handles_unknown_confidence_value_in_data() -> None:
    """best() treats unknown evidence.confidence values as below any gate.

    Defensive: schema is the authoritative validator, but runtime code
    should not crash on a cache file with an unrecognized confidence
    string (e.g. a new extractor scout writing 'very_high' before the
    schema adds it). Behaves as if the value were below the lowest gate.
    """
    from datasheet_types.spec_value import SpecValue, Evidence
    from datasheet_types.trust_gating import best

    spec_unknown = SpecValue(
        unit="V",
        evidence=Evidence(page=1, confidence="very_high", method="table"),
        typ=1.0,
    )
    spec_high = SpecValue(
        unit="V",
        evidence=Evidence(page=2, confidence="high", method="table"),
        typ=2.0,
    )
    # Unknown confidence filtered out even at min_confidence='low'.
    result = best([spec_unknown], min_confidence="low")
    assert result is None
    # Valid 'high' entry passes alongside ignored unknown.
    result = best([spec_unknown, spec_high], min_confidence="high")
    assert result is not None
    assert result.typ == 2.0


def test_trusted_safely_handles_unknown_confidence_value_in_data() -> None:
    """trusted() treats unknown evidence.confidence as below any gate."""
    from datasheet_types.spec_value import SpecValue, Evidence
    from datasheet_types.trust_gating import trusted

    spec_unknown = SpecValue(
        unit="V",
        evidence=Evidence(page=1, confidence="very_high", method="table"),
        typ=1.0,
    )
    spec_medium = SpecValue(
        unit="V",
        evidence=Evidence(page=2, confidence="medium", method="table"),
        typ=2.0,
    )
    # Unknown filtered; medium kept.
    result = trusted([spec_unknown, spec_medium], min_confidence="medium")
    assert [s.typ for s in result] == [2.0]


# ---------------------------------------------------------------------------
# Public API re-exports
# ---------------------------------------------------------------------------

def test_trust_gating_reexported_from_datasheet_types() -> None:
    """datasheet_types re-exports best, trusted, has_data at package level.

    Spec §11/§12 consumer pattern:
        from datasheet_types import best, trusted, has_data
    """
    import datasheet_types
    from datasheet_types.trust_gating import (
        best as best_direct,
        trusted as trusted_direct,
        has_data as has_data_direct,
    )

    assert hasattr(datasheet_types, "best")
    assert hasattr(datasheet_types, "trusted")
    assert hasattr(datasheet_types, "has_data")
    # Identity equality — same callable, not a copy.
    assert datasheet_types.best is best_direct
    assert datasheet_types.trusted is trusted_direct
    assert datasheet_types.has_data is has_data_direct
    # __all__ includes them so `from datasheet_types import *` pulls them in.
    assert "best" in datasheet_types.__all__
    assert "trusted" in datasheet_types.__all__
    assert "has_data" in datasheet_types.__all__
