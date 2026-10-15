"""`baseline_ledger check` implementation: observed debt identities not in the ledger."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baseline_ledger as bl  # noqa: E402


def new_identities(ledger: dict, *, units_lines: Iterable[str] | None = None,
                   checks: dict | None = None, junit_text: str | None = None) -> dict:
    out = {"checks": [], "contract": [], "timeout_units": [], "crash_units": []}
    if checks is not None:
        known = {e["identity"] for e in ledger.get("checks", [])}
        out["checks"] = sorted(e["identity"] for e in bl.check_identities(checks) if e["identity"] not in known)
    if junit_text is not None:
        known = {e["identity"] for e in ledger.get("contract", [])}
        out["contract"] = sorted(e["identity"] for e in bl.contract_entries(junit_text) if e["identity"] not in known)
    if units_lines is not None:
        known, known_crash = ledgered_timeouts(ledger), ledgered_crashes(ledger)
        found, found_crash = [], []
        for line in units_lines:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            new = new_timeout(rec, known)
            if new:
                found.append(new)
            new = new_crash(rec, known_crash)
            if new:
                found_crash.append(new)
        out["timeout_units"] = sorted(found)
        out["crash_units"] = sorted(found_crash)
    return out


def ledgered_crashes(ledger: dict) -> set[str]:
    """Ledgered both-sided crash identities (a ledger without the group reads as empty)."""
    return {e["identity"] for e in ledger.get("crash_units", [])}


def _crash_sides(rec: dict) -> tuple[bool, bool]:
    return ((rec.get("baseline") or {}).get("status") == "crash",
            (rec.get("candidate") or {}).get("status") == "crash")


def new_crash(rec: dict, known: set[str]) -> str | None:
    """The new-debt identity a unit record's crash carries, or None. A one-sided crash is
    always new (a round delta); a both-sided crash is new only when not ledgered."""
    ident = f"{rec['analyzer']}/{rec['unit_id']}"
    base_cr, cand_cr = _crash_sides(rec)
    if base_cr and cand_cr:
        return None if ident in known else ident
    if base_cr or cand_cr:
        return f"{ident} ({'baseline' if base_cr else 'candidate'})"
    return None


def ledgered_timeouts(ledger: dict) -> set[str]:
    return {e["identity"] for e in ledger.get("timeout_units", [])}


def _timeout_sides(rec: dict) -> tuple[str, bool, bool]:
    return (f"{rec['analyzer']}/{rec['unit_id']}",
            (rec.get("baseline") or {}).get("status") == "timeout",
            (rec.get("candidate") or {}).get("status") == "timeout")


def new_timeout(rec: dict, known: set[str]) -> str | None:
    """The new-debt identity a unit record's timeout carries, or None."""
    ident, base_to, cand_to = _timeout_sides(rec)
    # A candidate-only timeout is always new; a timeout on the baseline side (alone or
    # on both sides, e.g. an A/A tree) is new only when the identity is not ledgered.
    if cand_to and not base_to:
        return f"{ident} (candidate)"
    if base_to and ident not in known:
        return ident
    return None


def skip_is_ledgered(rec: dict, known: set[str], upstream: dict | None = None,
                     crashes: set[str] = frozenset()) -> bool:
    """A gate SKIP is a known baseline debt iff it is a both_failed unit whose crash on BOTH
    sides is in `crashes` (crash_units) or whose baseline-side timeout is ledgered
    (new_timeout finds nothing new) with no crash on either side, or a dependency_missing
    unit whose upstream schematic record is such a unit. A crash on one side only and
    snapshot_read_error are never covered."""
    reason = rec.get("reason")
    if reason == "both_failed":
        base_cr, cand_cr = _crash_sides(rec)
        if base_cr or cand_cr:
            return base_cr and cand_cr and new_crash(rec, crashes) is None
        _, base_to, _ = _timeout_sides(rec)
        return base_to and new_timeout(rec, known) is None
    if reason == "dependency_missing":
        return upstream is not None and upstream.get("reason") == "both_failed" \
            and skip_is_ledgered(upstream, known, crashes=crashes)
    return False


def run_check(args) -> int:
    ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    new = new_identities(
        ledger,
        units_lines=Path(args.units).read_text(encoding="utf-8").splitlines() if args.units else None,
        checks=json.loads(Path(args.checks).read_text(encoding="utf-8")) if args.checks else None,
        junit_text=Path(args.junit).read_text(encoding="utf-8") if args.junit else None,
    )
    total = sum(len(v) for v in new.values())
    for section, ids in new.items():
        for i in ids:
            print(f"NEW {section}: {i}")
    print(f"ledger check: {total} identities not covered by {args.ledger}")
    return 1 if total else 0
