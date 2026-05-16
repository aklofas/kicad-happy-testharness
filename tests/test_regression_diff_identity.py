"""Lock the identity-key semantics of ``regression/regression_diff.py``.

Audit LOG 6 / Highest-Risk #15 (2026-05-15): the original ``_first()``
canonical-key helper only included the first ref/net/pin of each finding,
so a regression that dropped secondary refs (a finding shrinking from
affecting ``["U1","C4","C5"]`` to just ``["U1"]``) was silently absorbed
as the SAME canonical key — the diff engine saw no change.

This test file locks two contracts on ``_canon_key``:

  1. Losing secondary refs produces a DIFFERENT canonical key, so the
     diff engine reports a disappeared (full-set) finding + a new
     (truncated-set) finding instead of silently coalescing them.
  2. Whitespace-only diffs in the summary string (double-space, trailing
     whitespace) produce the SAME canonical key, so cosmetic churn from
     v1.3 ↔ v1.4 wording variants doesn't cause spurious disappeared/new
     pairs.

The ``finding_id`` field is intentionally NOT used here yet — v1.4
finding_id coverage isn't universal (HI-5 partial). The audit notes
"don't block on it now"; when HI-5 lands full coverage, the canonical
key can switch to keying on finding_id where present.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HARNESS_ROOT = Path(__file__).resolve().parent.parent
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from regression.regression_diff import (  # noqa: E402
    _canon_key,
    _canon_refs,
    _norm_summary,
    diff,
)


# ---------------------------------------------------------------------------
# _canon_refs — full sorted-set behavior
# ---------------------------------------------------------------------------

def test_canon_refs_empty_list_returns_empty_string():
    assert _canon_refs([]) == ''
    assert _canon_refs(None or []) == ''


def test_canon_refs_single_item_returns_that_item():
    assert _canon_refs(['U1']) == 'U1'


def test_canon_refs_sorts_full_set_not_just_first():
    """Pre-fix this would have returned only 'C5' (first item). The fix
    sorts the full set so canonical keys reflect every affected ref."""
    assert _canon_refs(['C5', 'U1', 'C4']) == 'C4,C5,U1'


def test_canon_refs_handles_dict_items_with_ref_key():
    items = [{'ref': 'U2', 'pin': '3'}, {'ref': 'U1', 'pin': '1'}]
    assert _canon_refs(items) == 'U1,U2'


def test_canon_refs_handles_dict_items_with_number_fallback():
    items = [{'number': 'D5'}, {'number': 'D1'}]
    assert _canon_refs(items) == 'D1,D5'


# ---------------------------------------------------------------------------
# _canon_key — the load-bearing contract
# ---------------------------------------------------------------------------

def test_canon_key_distinguishes_losing_secondary_refs():
    """Pre-fix bug class: v1.4 detector change drops C4 + C5 from the
    components list, leaving only U1. The finding's canonical key MUST
    change so the diff engine reports it as a disappeared + new pair
    rather than treating them as the same finding."""
    v13 = {
        "rule_id": "RC-001",
        "components": ["U1", "C4", "C5"],
        "nets": ["VOUT"],
        "pins": [],
        "summary": "RC filter on VOUT (U1/C4/C5)",
    }
    v14_truncated = {
        "rule_id": "RC-001",
        "components": ["U1"],
        "nets": ["VOUT"],
        "pins": [],
        "summary": "RC filter on VOUT (U1/C4/C5)",
    }
    k_old = _canon_key(v13)
    k_new = _canon_key(v14_truncated)
    assert k_old != k_new, (
        f"Pre-fix regression: dropping secondary refs (C4, C5) didn't "
        f"change canonical key. Both produced: {k_old!r}. "
        f"The diff engine would silently coalesce these two findings."
    )


def test_canon_key_robust_to_ref_ordering():
    """Set-iteration-order churn between v1.3 and v1.4 (same refs, different
    order) MUST produce the same canonical key — that's noise, not a real
    finding change."""
    f1 = {
        "rule_id": "PR-001",
        "components": ["U1", "U2", "U3"],
        "nets": [],
        "pins": [],
        "summary": "Pull-ups missing on SCL/SDA",
    }
    f2 = {
        "rule_id": "PR-001",
        "components": ["U3", "U1", "U2"],  # different order
        "nets": [],
        "pins": [],
        "summary": "Pull-ups missing on SCL/SDA",
    }
    assert _canon_key(f1) == _canon_key(f2)


def test_canon_key_robust_to_whitespace_in_summary():
    """LOG 6 second contract: cosmetic whitespace differences in the
    summary (double-space, trailing whitespace) MUST NOT change the
    canonical key. v1.4 formatting fixes that touch only whitespace would
    otherwise produce spurious 'disappeared + new' pairs corpus-wide."""
    f_clean = {
        "rule_id": "VD-001",
        "components": ["R1", "R2"],
        "nets": ["FB"],
        "pins": [],
        "summary": "Voltage divider on FB (R1/R2) -> 3.3V",
    }
    f_double_space = {**f_clean,
                      "summary": "Voltage divider on FB  (R1/R2) -> 3.3V"}
    f_trailing_ws = {**f_clean,
                     "summary": "Voltage divider on FB (R1/R2) -> 3.3V   "}
    f_leading_ws = {**f_clean,
                    "summary": "  Voltage divider on FB (R1/R2) -> 3.3V"}
    f_tab_runs = {**f_clean,
                  "summary": "Voltage divider on FB\t(R1/R2) -> 3.3V"}

    base = _canon_key(f_clean)
    for variant_name, variant in [
        ("double-space",  f_double_space),
        ("trailing-ws",   f_trailing_ws),
        ("leading-ws",    f_leading_ws),
        ("tab-runs",      f_tab_runs),
    ]:
        assert _canon_key(variant) == base, (
            f"Whitespace-only diff ({variant_name}) produced different "
            f"canonical key.\nbase: {base!r}\nvariant: {_canon_key(variant)!r}"
        )


def test_canon_key_distinguishes_different_rule_ids():
    """Sanity: findings with the same components but different rule_ids
    are obviously different and must produce different keys."""
    f1 = {"rule_id": "RC-001", "components": ["U1"], "nets": [], "pins": [], "summary": "x"}
    f2 = {"rule_id": "RC-002", "components": ["U1"], "nets": [], "pins": [], "summary": "x"}
    assert _canon_key(f1) != _canon_key(f2)


def test_canon_key_distinguishes_different_nets():
    """Same rule + components, different affected nets → different key."""
    f1 = {"rule_id": "RC-001", "components": ["U1"], "nets": ["VOUT"], "pins": [], "summary": "x"}
    f2 = {"rule_id": "RC-001", "components": ["U1"], "nets": ["VIN"],  "pins": [], "summary": "x"}
    assert _canon_key(f1) != _canon_key(f2)


# ---------------------------------------------------------------------------
# End-to-end: diff() detects what _canon_key now distinguishes
# ---------------------------------------------------------------------------

def test_diff_reports_disappeared_when_secondary_refs_dropped():
    """Pre-fix this scenario would have produced zero disappeared findings —
    the truncated v1.4 finding would have absorbed the v1.3 multi-ref
    finding silently. Post-fix the diff reports the v1.3 finding as
    disappeared AND the v1.4 finding as new (the canonical keys differ)."""
    before = [{
        "rule_id": "RC-001",
        "severity": "warning",
        "components": ["U1", "C4", "C5"],
        "nets": ["VOUT"],
        "pins": [],
        "summary": "RC filter on VOUT (U1/C4/C5)",
    }]
    after = [{
        "rule_id": "RC-001",
        "severity": "warning",
        "components": ["U1"],  # dropped C4 + C5
        "nets": ["VOUT"],
        "pins": [],
        "summary": "RC filter on VOUT (U1/C4/C5)",
    }]
    d = diff(before, after)

    assert len(d['disappeared']) == 1, (
        f"Expected 1 disappeared finding (the v1.3 multi-ref entry), "
        f"got {len(d['disappeared'])}: {d['disappeared']!r}"
    )
    new_combined = d['new_known'] + d['new_upgraded'] + d['new_unknown']
    assert len(new_combined) == 1, (
        f"Expected 1 new finding (the truncated v1.4 entry), got "
        f"{len(new_combined)}: {new_combined!r}"
    )


def test_diff_quiet_on_pure_whitespace_summary_churn():
    """Whitespace-only diff between two otherwise-identical findings MUST
    NOT register as disappeared+new. Cosmetic re-wording at the producer
    side is not a regression."""
    before = [{
        "rule_id": "VD-001",
        "severity": "info",
        "components": ["R1", "R2"],
        "nets": ["FB"],
        "pins": [],
        "summary": "Voltage divider  on FB (R1/R2)",  # double space
    }]
    after = [{
        "rule_id": "VD-001",
        "severity": "info",
        "components": ["R1", "R2"],
        "nets": ["FB"],
        "pins": [],
        "summary": "Voltage divider on FB (R1/R2)",  # single space
    }]
    d = diff(before, after)
    assert d['disappeared'] == [], (
        f"Whitespace-only diff registered as disappeared: {d['disappeared']!r}"
    )
    assert d['new_known'] == [] and d['new_unknown'] == [], (
        f"Whitespace-only diff registered as new: "
        f"known={d['new_known']!r}, unknown={d['new_unknown']!r}"
    )


# ---------------------------------------------------------------------------
# _norm_summary unit checks
# ---------------------------------------------------------------------------

def test_norm_summary_collapses_whitespace_runs():
    assert _norm_summary("a  b   c") == "a b c"
    assert _norm_summary("\ta\nb \tc") == "a b c"
    assert _norm_summary("   leading and trailing   ") == "leading and trailing"


def test_norm_summary_sorts_comma_runs():
    """The pre-existing comma-run normalization still works (regression
    guard for the LOG 6 change)."""
    assert _norm_summary("nets U3, U1, U2 affected") == "nets U1, U2, U3 affected"


def test_norm_summary_truncates_to_120_chars():
    long = "x" * 200
    assert len(_norm_summary(long)) == 120
