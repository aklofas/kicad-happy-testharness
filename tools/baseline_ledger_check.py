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
        known = {e["identity"] for e in ledger.get("timeout_units", [])}
        found = []
        for line in units_lines:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            ident = f"{rec['analyzer']}/{rec['unit_id']}"
            base_to = (rec.get("baseline") or {}).get("status") == "timeout"
            cand_to = (rec.get("candidate") or {}).get("status") == "timeout"
            # A candidate-only timeout is always new; a timeout on the baseline side (alone or
            # on both sides, e.g. an A/A tree) is new only when the identity is not ledgered.
            if cand_to and not base_to:
                found.append(f"{ident} (candidate)")
            elif base_to and ident not in known:
                found.append(ident)
        out["timeout_units"] = sorted(found)
    return out


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
