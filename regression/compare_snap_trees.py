#!/usr/bin/env python3
"""Compare two snap trees in raw / strict / budgeted mode and write field_report v1.

Usage:
  python3 regression/compare_snap_trees.py A_ROOT B_ROOT --mode strict -o report.json
  python3 regression/compare_snap_trees.py A_ROOT B_ROOT --mode budgeted \
      --budget regression/budgets/<id>.json -o report.json

Exit codes: 0 clean, 1 deltas (raw/strict) or residuals/over_budget (budgeted), 2 error
(missing root, missing/unparseable units beyond the budget's allowance, policy
violation, bad arguments). The report is written on every exit except bad
arguments / missing roots. A report of more than field_compare.INLINE_DELTAS_MAX deltas
keeps them in <report stem>.deltas.jsonl beside it (budgeted: also .residuals.jsonl and
.claims.jsonl), named in the report.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from regression.field_compare import (  # noqa: E402
    BudgetError, PolicyError, compare_budgeted, compare_trees, load_budget, load_policy, sidecar_path,
)

# each comparison worker holds one unit's two documents and its deltas; the box is shared
DEFAULT_JOBS = min(os.cpu_count() or 1, 8)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a_root"); ap.add_argument("b_root")
    ap.add_argument("--mode", required=True, choices=("raw", "strict", "budgeted"))
    ap.add_argument("--policy", default="volatile-leaves-v1", help="normalization policy name, or 'none'")
    ap.add_argument("--budget", help="budget record JSON (required for --mode budgeted)")
    ap.add_argument("--key-order", action="store_true", help="also report object key-order differences")
    ap.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                    help=f"worker processes for the per-unit comparison (default: {DEFAULT_JOBS})")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args(argv)

    a_root, b_root = Path(args.a_root), Path(args.b_root)
    if not a_root.is_dir() or not b_root.is_dir():
        print(f"error: both roots must be directories: {a_root} {b_root}", file=sys.stderr)
        return 2
    if args.mode == "budgeted" and not args.budget:
        print("error: --mode budgeted requires --budget", file=sys.stderr)
        return 2
    if args.budget and args.mode != "budgeted":
        print("error: --budget requires --mode budgeted", file=sys.stderr)
        return 2
    policy = None
    if args.mode != "raw" and args.policy != "none":
        try:
            policy = load_policy(args.policy)
        except PolicyError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
    budget = None
    if args.budget:
        try:
            budget = load_budget(Path(args.budget))
        except BudgetError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.mode == "budgeted":
        try:
            _, report = compare_budgeted(a_root, b_root, budget, policy=policy, key_order=args.key_order,
                                         jobs=args.jobs, deltas_path=sidecar_path(out, "deltas"),
                                         residuals_path=sidecar_path(out, "residuals"),
                                         claims_path=sidecar_path(out, "claims"))
        except BudgetError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
    else:
        report = compare_trees(a_root, b_root, mode=args.mode, policy=policy, key_order=args.key_order,
                               jobs=args.jobs, deltas_path=sidecar_path(out, "deltas"))

    out.write_text(json.dumps(report, indent=1, sort_keys=False), encoding="utf-8")
    s = report["summary"]
    print(f"{args.mode}: {report['verdict']} — units {s['units']} compared {s['compared']} "
          f"identical {s['identical']} with_deltas {s['with_deltas']} missing {s['missing']} "
          f"parse_errors {s['parse_errors']} deltas {s['deltas']}"
          + (f" residuals {report['budget']['residual_count']}" if report["budget"] else "")
          + (f" policy_violations {len(report['policy_violations'])}" if report["policy_violations"] else ""))
    if report["budget"]:
        for cid in report["budget"].get("over_budget", []):
            st = report["budget"]["bound_status"][cid]
            print(f"over_budget: {cid} claimed {st['deltas']} deltas > 2x expected_magnitude "
                  f"{st['expected_magnitude']}")
    print(f"report: {out}")
    return {"clean": 0, "deltas": 1, "residuals": 1, "over_budget": 1, "error": 2}[report["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
