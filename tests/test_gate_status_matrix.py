"""Status matrix: every unit-record shape x every gate kind -> gate_pass.pass.

Each case is one PASS unit plus the record under test (or the record alone), run through
aggregate -> compute_gate_pass -> apply_modes with the comparator modes clean, so only the
record decides the verdict."""
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
from regression import run_corpus_gate as gate  # noqa: E402

pytestmark = pytest.mark.unit

UID = "o/r/a.kicad_sch"
LEDGER = {"timeout_units": [{"identity": f"schematic/{UID}", "accepted_by": "x"}],
          "crash_units": [{"identity": f"schematic/{UID}", "exit_code": 1, "accepted_by": "x"}]}
KINDS = ("structural", "aa", "baseline", "output-changing", "relock")
OK = {"status": "ok", "exit_code": 0}


def _side(status, code=None):
    return {"status": status, "exit_code": code}


def _rec(verdict, reason=None, base=OK, cand=OK, uid=UID, analyzer="schematic"):
    r = {"analyzer": analyzer, "repo": "o/r", "unit_id": uid, "identity": uid,
         "verdict": verdict, "baseline": base, "candidate": cand}
    if reason is not None:
        r["reason"] = reason
    return r


PASS_UNIT = _rec("PASS", uid="o/r/ok.kicad_sch")

# (case id, record, expected pass for structural-like kinds, expected pass for budgeted kinds)
CASES = [
    ("pass", None, True, True),
    # TH-078: a ledgered debt the candidate fixes is a resolved debt, not a WARN against strict_clean
    ("warn_baseline_failed_ledgered", _rec("WARN", "baseline failed; not comparable", _side("crash", 1)), True, True),
    ("warn_baseline_failed_unledgered", _rec("WARN", "baseline failed; not comparable", _side("crash", 1),
                                             uid="o/r/z.kicad_sch"), False, True),
    ("candidate_failed", _rec("FAIL", gate.CANDIDATE_FAILED_REASON, OK, _side("crash", 1)), False, False),
    ("worker_exception", _rec("FAIL", "worker_exception", None, None), False, False),
    ("not_applicable", _rec("SKIP", "not_applicable", _side("skipped"), _side("skipped"), analyzer="thermal"),
     True, True),
    ("both_timeout_ledgered", _rec("SKIP", "both_failed", _side("timeout"), _side("timeout")), True, True),
    ("timeout_vs_invalid_output", _rec("SKIP", "both_failed", _side("timeout"), _side("invalid_output", 0)),
     False, False),
    ("timeout_vs_no_output", _rec("SKIP", "both_failed", _side("timeout"), _side("no_output", 0)), False, False),
    ("timeout_vs_exit_unexpected", _rec("SKIP", "both_failed", _side("timeout"), _side("exit_unexpected", 3)),
     False, False),
    ("invalid_output_vs_timeout", _rec("SKIP", "both_failed", _side("invalid_output", 0), _side("timeout")),
     False, False),
    ("both_crash_ledgered", _rec("SKIP", "both_failed", _side("crash", 1), _side("crash", 1)), True, True),
    # ruling Q3: a ledgered both-sided crash whose exit code changed is a round delta (also listed, TH-078)
    ("both_crash_exit_changed", _rec("SKIP", "both_failed", _side("crash", 1), _side("crash", 2)), False, False),
    ("one_sided_crash", _rec("SKIP", "both_failed", _side("crash", 1), _side("timeout")), False, False),
    ("unledgered_timeout", _rec("SKIP", "both_failed", _side("timeout"), _side("timeout"), uid="o/r/z.kicad_sch"),
     False, False),
    ("snapshot_read_error", _rec("SKIP", "snapshot_read_error"), False, False),
]


def _verdict(records, kind):
    agg = gate.aggregate(records)
    totals = {k: 0 for k in ("PASS", "WARN", "FAIL", "SKIP", "Disappeared", "Downgrades", "Upgrades",
                             "NewKnown", "NewUpgraded", "NewUnknown", "Rewrites")}
    for c in agg["by_analyzer"].values():
        for k in ("PASS", "WARN", "FAIL", "SKIP"):
            totals[k] += c.get(k, 0)
    crit = gate._compute_pass_criteria(totals)
    gp = gate.compute_gate_pass(crit, agg["skip_breakdown"], {}, agg["executed_census"],
                                skip_records=records, ledger=LEDGER)
    modes = {"strict_field_clean": True, "budgeted": {"verdict": "clean"}}
    out = gate.apply_modes({"gate_pass": gp, "modes": {}, "identity": {}}, modes, kind=kind)
    return out["gate_pass"]


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("case,rec,want_struct,want_budget", CASES, ids=[c[0] for c in CASES])
def test_status_matrix(case, rec, want_struct, want_budget, kind):
    records = [PASS_UNIT] + ([rec] if rec is not None else [])
    want = want_budget if kind in gate.BUDGETED_KINDS else want_struct
    assert _verdict(records, kind)["pass"] is want, (case, kind)


@pytest.mark.parametrize("kind", KINDS)
def test_ledgered_debt_alone_never_passes(kind):
    """Ruling R3: zero compared units is no evidence, even when every skip is ledgered."""
    gp = _verdict([_rec("SKIP", "both_failed", _side("timeout"), _side("timeout"))], kind)
    assert gp["compared_units"] == 0 and gp["skips_ok"] is True and gp["pass"] is False


def test_worker_exception_counted_in_gate_pass():
    gp = _verdict([PASS_UNIT, _rec("FAIL", "worker_exception", None, None)], "relock")
    assert gp["worker_exceptions"] == 1 and gp["candidate_failures"] == 0
    assert "worker_exceptions == 0" in gp["criterion"]


def test_resolved_debt_covers_its_downstream_and_is_listed():
    """TH-078: the downstream dependency_missing units of a resolved schematic debt are covered by it."""
    up = _rec("WARN", "baseline failed; not comparable", _side("timeout"))
    down = _rec("SKIP", "dependency_missing", _side("skipped"), _side("skipped"), analyzer="emc")
    gp = _verdict([PASS_UNIT, up, down], "structural")
    assert gp["pass"] is True and gp["unledgered_skips"] == []
    assert gp["resolved_debts"] == [f"emc/{UID}", f"schematic/{UID}"]


def test_downstream_of_an_unledgered_baseline_failure_stays_unledgered():
    up = _rec("WARN", "baseline failed; not comparable", _side("timeout"), uid="o/r/z.kicad_sch")
    down = _rec("SKIP", "dependency_missing", _side("skipped"), _side("skipped"), uid="o/r/z.kicad_sch",
                analyzer="emc")
    gp = _verdict([PASS_UNIT, up, down], "structural")
    assert gp["pass"] is False and gp["resolved_debts"] == []
    assert gp["unledgered_skips"] == ["dependency_missing emc o/r/z.kicad_sch"]


def test_shape_changed_debt_is_listed():
    gp = _verdict([PASS_UNIT, _rec("SKIP", "both_failed", _side("crash", 1), _side("crash", 2))], "structural")
    assert gp["shape_changed_debts"] == [f"schematic/{UID} (exit_code 1/2 != ledgered 1)"]
