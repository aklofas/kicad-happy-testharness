#!/usr/bin/env python3
"""Compare two snap trees in raw / strict / budgeted mode and write field_report v1.

Usage:
  python3 regression/compare_snap_trees.py A_ROOT B_ROOT --mode strict -o report.json
  python3 regression/compare_snap_trees.py A_ROOT B_ROOT --mode budgeted \
      --budget regression/budgets/<id>.json -o report.json

Exit codes: 0 clean, 1 deltas (raw/strict) or residuals (budgeted), 2 error
(missing root, missing/unparseable units beyond the budget's allowance, policy
violation, bad arguments). The report is written on every exit except bad
arguments / missing roots.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from regression.field_compare import (  # noqa: E402
    BudgetError, PolicyError, budgeted_report, compare_trees, load_budget, load_policy,
)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a_root"); ap.add_argument("b_root")
    ap.add_argument("--mode", required=True, choices=("raw", "strict", "budgeted"))
    ap.add_argument("--policy", default="volatile-leaves-v1", help="normalization policy name, or 'none'")
    ap.add_argument("--budget", help="budget record JSON (required for --mode budgeted)")
    ap.add_argument("--key-order", action="store_true", help="also report object key-order differences")
    ap.add_argument("--jobs", "-j", type=int, default=os.cpu_count() or 1,
                    help="worker processes for the per-unit comparison (default: cpu_count)")
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

    report = compare_trees(a_root, b_root, mode="strict" if args.mode == "budgeted" else args.mode,
                           policy=policy, key_order=args.key_order, jobs=args.jobs)
    if args.mode == "budgeted":
        try:
            report = budgeted_report(report, budget, a_root, b_root)
        except BudgetError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, sort_keys=False), encoding="utf-8")
    s = report["summary"]
    print(f"{args.mode}: {report['verdict']} — units {s['units']} compared {s['compared']} "
          f"identical {s['identical']} with_deltas {s['with_deltas']} missing {s['missing']} "
          f"parse_errors {s['parse_errors']} deltas {s['deltas']}"
          + (f" residuals {len(report['budget']['residuals'])}" if report["budget"] else "")
          + (f" policy_violations {len(report['policy_violations'])}" if report["policy_violations"] else ""))
    print(f"report: {out}")
    return {"clean": 0, "deltas": 1, "residuals": 1, "error": 2}[report["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
