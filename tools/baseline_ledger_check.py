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
    out = {"checks": [], "contract": [], "timeout_units": []}
    if checks is not None:
        known = {e["identity"] for e in ledger.get("checks", [])}
        out["checks"] = sorted(e["identity"] for e in bl.check_identities(checks) if e["identity"] not in known)
    if junit_text is not None:
        known = {e["identity"] for e in ledger.get("contract", [])}
        out["contract"] = sorted(e["identity"] for e in bl.contract_entries(junit_text) if e["identity"] not in known)
    if units_lines is not None:
        known = ledgered_timeouts(ledger)
        found = []
        for line in units_lines:
            line = line.strip()
            if not line:
                continue
            new = new_timeout(json.loads(line), known)
            if new:
                found.append(new)
        out["timeout_units"] = sorted(found)
    return out


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


def skip_is_ledgered(rec: dict, known: set[str], upstream: dict | None = None) -> bool:
    """A gate SKIP is a known baseline debt iff it is a both_failed unit whose baseline-side
    timeout is ledgered (new_timeout finds nothing new), or a dependency_missing unit whose
    upstream schematic record is such a unit. Crashes and snapshot_read_error never are:
    the ledger records timeouts only."""
    reason = rec.get("reason")
    if reason == "both_failed":
        _, base_to, _ = _timeout_sides(rec)
        return base_to and new_timeout(rec, known) is None
    if reason == "dependency_missing":
        return upstream is not None and upstream.get("reason") == "both_failed" \
            and skip_is_ledgered(upstream, known)
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
