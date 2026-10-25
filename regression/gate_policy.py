"""Corpus gate acceptance policy: findings criteria, skip judgement against the
baseline-debts ledger, gate_pass and the per-kind final verdict.

Runs no analyzers and knows no gate-dir layout; the only side effect is putting tools/ on
sys.path to import the baseline-ledger checker on demand. The gate driver re-exports
these names.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"

BAD_SKIP_REASONS = ("both_failed", "dependency_missing", "snapshot_read_error")
OK_STATUSES = ("ok", "ok_findings_exit")


def _ok(res) -> bool:
    return res.status in OK_STATUSES


CANDIDATE_FAILED_REASON = "candidate failed/produced no output"


def _both_ok(rec):
    b, c = rec.get("baseline"), rec.get("candidate")
    return (isinstance(b, dict) and isinstance(c, dict)
            and b["status"] in OK_STATUSES and c["status"] in OK_STATUSES)


def _compute_pass_criteria(totals: dict) -> dict:
    """Unchanged shape from run_v14_gate (tests/test_v14_gate_criteria.py imports it)."""
    return {
        "disappeared_count": totals["Disappeared"],
        "severity_downgrades": totals["Downgrades"],
        "fail_verdicts": totals["FAIL"],
        "new_unknown_count": totals["NewUnknown"],
        "new_upgraded_count": totals["NewUpgraded"],
        "warn_count": totals["WARN"],
        "rewrites_count": totals.get("Rewrites", 0),
        "clean": (totals["Disappeared"] == 0 and totals["Downgrades"] == 0
                  and totals["FAIL"] == 0 and totals["NewUnknown"] == 0),
        "strict_clean": (totals["Disappeared"] == 0 and totals["Downgrades"] == 0
                         and totals["FAIL"] == 0 and totals["NewUnknown"] == 0
                         and totals["WARN"] == 0),
    }


WORKER_EXCEPTION_REASON = "worker_exception"


def _ledger_check():
    tools = str(_TOOLS_DIR)
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import baseline_ledger_check  # noqa: E402  (sibling tool owns the identity rules)
    return baseline_ledger_check


def ledger_identity(path):
    if path is None:
        return {"ledger": None, "ledger_sha256": None}
    return {"ledger": str(path), "ledger_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}


def split_bad_skips(records, ledger):
    """(ledgered count, sorted "reason analyzer identity" list of bad SKIPs the ledger does not
    cover, sorted ledger identities that cover a skip but carry accepted_by null)."""
    bad = [r for r in records if r.get("verdict") == "SKIP" and r.get("reason") in BAD_SKIP_REASONS]
    if ledger is None:
        return 0, sorted(f"{r['reason']} {r['analyzer']} {r['identity']}" for r in bad), []
    blc = _ledger_check()
    known, crashes = blc.ledgered_timeouts(ledger), blc.ledgered_crashes(ledger)
    accepted = {e["identity"]: e.get("accepted_by") for g in ("timeout_units", "crash_units")
                for e in ledger.get(g, [])}
    upstream = {r["unit_id"]: r for r in records if r.get("analyzer") == "schematic"}
    ledgered, unledgered, unaccepted = 0, [], set()
    for r in bad:
        cover = blc.skip_covering(r, known, upstream=upstream.get(r["unit_id"]), crashes=crashes)
        if cover is None:
            unledgered.append(f"{r['reason']} {r['analyzer']} {r['identity']}")
            continue
        ledgered += 1
        if accepted.get(cover) is None:
            unaccepted.add(cover)
    return ledgered, sorted(unledgered), sorted(unaccepted)


def compute_gate_pass(criteria, skip_breakdown, expected_census, executed_census,
                      skip_records=None, ledger=None):
    if skip_records is None:  # counts only: no identities to match against a ledger
        ledgered, unaccepted = 0, []
        unledgered = [f"{r} (count {skip_breakdown[r]})" for r in BAD_SKIP_REASONS if skip_breakdown.get(r, 0)]
    else:
        ledgered, unledgered, unaccepted = split_bad_skips(skip_records, ledger)
    cand_fail = sum(1 for r in skip_records or () if r.get("verdict") == "FAIL"
                    and r.get("reason") == CANDIDATE_FAILED_REASON)
    worker_exc = sum(1 for r in skip_records or () if r.get("verdict") == "FAIL"
                     and r.get("reason") == WORKER_EXCEPTION_REASON)
    # zero compared units is no evidence: a run of ledgered debt alone never passes
    compared = (None if skip_records is None else
                sum(1 for r in skip_records if r.get("verdict") != "SKIP" and _both_ok(r)))
    skips_ok = not unledgered
    census_ok = all(executed_census.get(a, 0) == n for a, n in expected_census.items())
    strict = bool(criteria["strict_clean"])
    evidence_ok = compared is None or compared > 0
    return {"pass": (strict and skips_ok and census_ok and cand_fail == 0 and worker_exc == 0
                     and evidence_ok),
            "strict_clean": strict,
            "census_ok": census_ok, "skips_ok": skips_ok, "candidate_failures": cand_fail,
            "worker_exceptions": worker_exc, "compared_units": compared,
            "ledgered_skips": ledgered, "unledgered_skips": unledgered,
            "ledgered_unaccepted": {"count": len(unaccepted), "identities": unaccepted},
            "skip_breakdown": dict(skip_breakdown),
            "expected_census": dict(expected_census), "executed_census": dict(executed_census)}


KIND_CHOICES = ("structural", "output-changing", "relock", "aa", "baseline", "gate")
BUDGETED_KINDS = ("output-changing", "relock")
CRITERIA = {
    "structural": ("structural: findings strict_clean AND strict_field_clean AND census_ok AND skips_ok "
                   "AND candidate_failures == 0 AND worker_exceptions == 0 AND compared_units > 0"),
    **{k: (f"{k}: census_ok AND skips_ok AND budgeted verdict clean AND candidate_failures == 0 "
           "AND worker_exceptions == 0 AND compared_units > 0")
       for k in BUDGETED_KINDS},
}


def final_pass(gp, modes, kind):
    """The gate verdict for `kind`, given compute_gate_pass's dict (whose "pass" is the
    findings-level verdict) and the comparator modes."""
    if kind in BUDGETED_KINDS:
        # a candidate-only analyzer failure is never budgetable
        return (bool(gp.get("census_ok")) and bool(gp.get("skips_ok"))
                and gp.get("candidate_failures", 0) == 0
                and gp.get("worker_exceptions", 0) == 0
                and gp.get("compared_units") != 0
                and (modes.get("budgeted") or {}).get("verdict") == "clean")
    return bool(gp.get("pass")) and bool(modes.get("strict_field_clean"))


def apply_modes(report, modes, kind="structural", budget_sha256=None):
    """Merge run_modes() output into the rollup and set gate_pass per kind.

    structural/aa/baseline: findings strict_clean AND strict_field_clean AND census_ok
    AND skips_ok. output-changing/relock: census_ok AND skips_ok AND budgeted verdict
    clean (findings strict_clean kept as information)."""
    report["modes"] = {**report.get("modes", {}), **modes}
    budgeted = report["modes"].get("budgeted")
    if isinstance(budgeted, dict):
        report["modes"]["budgeted"] = {**budgeted, "budget_sha256": budget_sha256}
    report.setdefault("identity", {})["budget_sha256"] = budget_sha256
    gp = report.setdefault("gate_pass", {})
    gp["strict_field_clean"] = bool(modes.get("strict_field_clean"))
    gp["pass"] = final_pass(gp, modes, kind)
    gp["kind"] = kind
    gp["criterion"] = CRITERIA.get(kind, CRITERIA["structural"])
    return report
