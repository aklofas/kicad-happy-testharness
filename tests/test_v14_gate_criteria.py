"""Lock the v1.4 Layer 1 regression gate's pass-criteria semantics.

Audit LOG 5 / Highest-Risk #14 (2026-05-15): the original ``clean`` verdict
in ``regression/run_v14_gate.py`` checked only ``Disappeared``, ``Downgrades``,
and ``FAIL``. It IGNORED ``NewUnknown`` (unrecognized new findings) and WARN
(uncomparable baselines), so a rollup with 530 NewUnknown rows could still
print ``CLEAN -- eligible for tag``. The rc.1 VD-DET cascade was a
near-miss: ``clean`` happened to be ``False`` only because of cascading
FAIL verdicts; without the FAIL coverage the 530 NewUnknown rows alone
would have green-lit a broken tag.

This test locks two clean verdicts (extracted into
``_compute_pass_criteria`` for testability):

  * ``clean`` — rc.1-compatible interpretation, now ALSO requires
    ``NewUnknown == 0``. The minimum safety guard against the rc.1 cascade
    bug class.
  * ``strict_clean`` — release-blocking interpretation, additionally
    requires ``WARN == 0``. A WARN row means the v1.3.1 baseline failed
    for that repo so the v1.4 output isn't comparable — calling that
    "CLEAN" hides incomplete coverage.

Printed-summary contract (``_print_summary``):

  * MUST NOT print "CLEAN" unmodified when WARN > 0; must surface the
    incomplete-comparison fact.
  * MUST distinguish "STRICT-CLEAN" (full clean) from "CLEAN" (clean modulo
    WARN baselines).
  * MUST flag NewUnknown by name in the NOT-CLEAN reason.

Before/after impact on existing rc.1 rollups (from ``results/v14_gate/``):

  ============================================  pre-fix  post-fix
  rollup_ccadic_TI92-revive.json (WARN=5)       clean    clean / NOT strict
  rollup_rc1_693b664_quick200.json (NU=530)     clean    NOT clean (gate flips)
  rollup_rc1_fix_f561e47_full.json (WARN=5)     clean    clean / NOT strict
  rollup_rc1_fix_f561e47_quick200.json          clean    clean / strict-clean
  rollup_ti92probe.json                         clean    clean / strict-clean

The 693b664 quick200 rollup (the VD-DET cascade catch) now flips earlier
on NewUnknown alone — exactly what LOG 5 is supposed to lock. None of the
rc.1-tagged rollups regress from clean to NOT clean (the f561e47 rc.1 tag
rollup keeps ``clean=True``); they just gain a ``strict_clean=False``
signal that surfaces the WARN-baseline gap.
"""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parent.parent
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from regression.run_v14_gate import _compute_pass_criteria, _print_summary  # noqa: E402


def _totals(*, pass_=0, warn=0, fail=0, skip=0, disappeared=0, downgrades=0,
            upgrades=0, new_known=0, new_upgraded=0, new_unknown=0) -> dict:
    """Synthetic totals dict in the shape ``_compute_pass_criteria`` expects.

    Defaults to all-zero so each test sets only the keys that matter."""
    return {
        "PASS": pass_, "WARN": warn, "FAIL": fail, "SKIP": skip,
        "Disappeared": disappeared, "Downgrades": downgrades,
        "Upgrades": upgrades, "NewKnown": new_known,
        "NewUpgraded": new_upgraded, "NewUnknown": new_unknown,
    }


def _report(totals: dict, *, section="quick_200", units=200) -> dict:
    """Minimum report dict shape that ``_print_summary`` expects."""
    return {
        "section": section,
        "total_units": units,
        "rollup": [],
        "totals": totals,
        "pass_criteria": _compute_pass_criteria(totals),
        "fail_repo_count": totals["FAIL"],
        "fail_repos": [],
        "new_known_rule_distribution": {},
        "new_upgraded_rule_distribution": {},
        "new_unknown_rule_distribution": {},
    }


# ---------------------------------------------------------------------------
# clean criterion — Tier-1 (NewUnknown gating)
# ---------------------------------------------------------------------------

def test_clean_true_when_all_zero():
    crit = _compute_pass_criteria(_totals(pass_=200))
    assert crit["clean"] is True
    assert crit["strict_clean"] is True


def test_clean_false_when_disappeared_present():
    crit = _compute_pass_criteria(_totals(pass_=199, disappeared=1))
    assert crit["clean"] is False
    assert crit["strict_clean"] is False


def test_clean_false_when_downgrades_present():
    crit = _compute_pass_criteria(_totals(pass_=199, downgrades=1))
    assert crit["clean"] is False
    assert crit["strict_clean"] is False


def test_clean_false_when_fail_present():
    crit = _compute_pass_criteria(_totals(pass_=199, fail=1))
    assert crit["clean"] is False
    assert crit["strict_clean"] is False


def test_clean_false_when_new_unknown_present():
    """LOG 5 / Highest-Risk #14 lock: a NewUnknown row alone must flip
    clean to False. Pre-fix this would have stayed clean=True — the rc.1
    VD-DET cascade was the near-miss that motivated this gate.

    The 693b664 quick200 rollup had NewUnknown=530 + FAIL=558. Even if
    the FAIL coverage had been incomplete (e.g., 0 FAIL but 530
    NewUnknown), the pre-fix gate would have green-lit the tag. Post-fix
    it flips on NewUnknown alone."""
    crit = _compute_pass_criteria(_totals(pass_=199, new_unknown=1))
    assert crit["clean"] is False, (
        "NewUnknown > 0 must flip clean to False — unrecognized findings "
        "MUST be triaged before tagging (Highest-Risk #14 regression)"
    )
    assert crit["strict_clean"] is False


def test_clean_true_with_new_upgraded_tolerated():
    """NewUpgraded (Phase 4b datasheet-backed branch firings) is tolerated
    by clean — these are expected when the datasheet path activates. Only
    surfaced as informational, not gate-blocking."""
    crit = _compute_pass_criteria(_totals(pass_=199, new_upgraded=1))
    assert crit["clean"] is True


def test_clean_true_with_new_known_tolerated():
    """NewKnown rows (rule_ids in NEW_V14_RULES set) are tolerated."""
    crit = _compute_pass_criteria(_totals(pass_=199, new_known=5))
    assert crit["clean"] is True


# ---------------------------------------------------------------------------
# strict_clean criterion — Tier-2 (WARN gating)
# ---------------------------------------------------------------------------

def test_strict_clean_false_when_warn_present():
    """LOG 5 second-tier lock: WARN > 0 means uncomparable baselines —
    strict_clean must be False. ``clean`` stays True for rc.1
    compatibility (it doesn't gate on WARN)."""
    crit = _compute_pass_criteria(_totals(pass_=195, warn=5))
    assert crit["clean"] is True, "rc.1-compatible clean tolerates WARN"
    assert crit["strict_clean"] is False, (
        "strict_clean MUST flip on WARN > 0 — uncomparable baselines "
        "hide incomplete coverage"
    )


def test_strict_clean_matches_rc1_full_rollup_shape():
    """Real-world before/after: the rc.1 f561e47 full rollup had
    WARN=5, NewUnknown=0, FAIL=0. The historical interpretation was
    ``clean=True``; the new ``strict_clean=False`` surfaces the WARN
    gap without retroactively flipping the rc.1 tag verdict."""
    crit = _compute_pass_criteria(_totals(pass_=149_556, warn=5))
    assert crit["clean"] is True
    assert crit["strict_clean"] is False


# ---------------------------------------------------------------------------
# _print_summary contract — text output reflects the verdict honestly
# ---------------------------------------------------------------------------

def _summary_text(totals: dict) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        _print_summary(_report(totals))
    return buf.getvalue()


def test_print_summary_strict_clean_says_so():
    """STRICT-CLEAN verdict must be explicitly labeled."""
    out = _summary_text(_totals(pass_=200))
    assert "STRICT-CLEAN" in out
    assert "NOT CLEAN" not in out


def test_print_summary_warn_baselines_visible_in_clean_path():
    """When clean=True but WARN > 0, the printed summary MUST NOT say
    'STRICT-CLEAN' and MUST surface the WARN baselines explicitly. The
    pre-fix output said 'CLEAN -- eligible for v1.4.0-rc.1 tag' even
    with WARN > 0, which is misleading."""
    out = _summary_text(_totals(pass_=195, warn=5))
    assert "STRICT-CLEAN" not in out, (
        f"Output claimed STRICT-CLEAN despite WARN=5:\n{out}"
    )
    assert "CLEAN" in out, "should say CLEAN (rc.1-compatible)"
    assert "5 WARN baseline" in out or "5 WARN" in out, (
        f"WARN count not surfaced in summary:\n{out}"
    )
    assert "comparison incomplete" in out or "incomplete" in out


def test_print_summary_new_unknown_flagged_by_name():
    """NOT CLEAN reason must call out NewUnknown specifically when present,
    so the operator knows whether to triage findings or chase FAIL repos."""
    out = _summary_text(_totals(pass_=199, new_unknown=1))
    assert "NOT CLEAN" in out
    assert "NewUnknown" in out
    assert "triage" in out


def test_print_summary_not_clean_fail_reason_when_fail_repos():
    out = _summary_text(_totals(pass_=199, fail=1))
    assert "NOT CLEAN" in out
    assert "FAIL" in out


def test_print_summary_includes_warn_count_in_pass_criteria_line():
    """The pass-criteria line MUST include warn= so the verdict is
    self-contained (pre-fix it was omitted entirely)."""
    out = _summary_text(_totals(pass_=199, warn=1))
    assert "warn=1" in out, (
        f"warn= field missing from Pass criteria line:\n{out}"
    )
