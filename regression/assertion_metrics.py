#!/usr/bin/env python3
"""Assertion quality metrics — track margin, fragility, and staleness.

Records per-assertion metrics each time assertions are evaluated, enabling
analysis of which assertions are fragile (near boundary), stale (never fail),
or high-value (have caught regressions).

Usage:
    python3 regression/assertion_metrics.py record     # record current run
    python3 regression/assertion_metrics.py fragile    # near-boundary assertions
    python3 regression/assertion_metrics.py stale      # never-failed assertions
    python3 regression/assertion_metrics.py summary    # overall quality breakdown
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from checks import evaluate_assertion, load_assertions
from run_checks import find_output_file
from utils import OUTPUTS_DIR, DATA_DIR, ANALYZER_TYPES

METRICS_FILE = DATA_DIR / "assertion_metrics.jsonl"


def compute_margin(assertion, result):
    """Compute how close an assertion result is to its boundary.

    Returns float 0.0 (at boundary) to 1.0 (far from boundary).
    Binary operators (exists, contains_match) return 1.0 if passed, 0.0 if not.
    """
    check = assertion.get("check", {})
    op = check.get("op", "")
    actual = result.get("actual")

    if op == "range":
        lo = check.get("min", 0)
        hi = check.get("max", float("inf"))
        if hi == float("inf") or hi == lo:
            return 1.0 if result["passed"] else 0.0
        if not isinstance(actual, (int, float)):
            return 0.0
        if not result["passed"]:
            return 0.0
        dist_to_lo = actual - lo
        dist_to_hi = hi - actual
        span = hi - lo
        return min(dist_to_lo, dist_to_hi) / span if span > 0 else 0.0

    elif op in ("min_count", "greater_than"):
        threshold = check.get("value", 0)
        if not isinstance(actual, (int, float)) or not isinstance(threshold, (int, float)):
            return 1.0 if result["passed"] else 0.0
        if not result["passed"]:
            return 0.0
        if threshold == 0:
            return 1.0
        return min((actual - threshold) / max(threshold, 1), 1.0)

    elif op in ("max_count", "less_than"):
        threshold = check.get("value", 0)
        if not isinstance(actual, (int, float)) or not isinstance(threshold, (int, float)):
            return 1.0 if result["passed"] else 0.0
        if not result["passed"]:
            return 0.0
        if threshold == 0:
            return 1.0
        return min((threshold - actual) / max(threshold, 1), 1.0)

    # Binary operators
    return 1.0 if result["passed"] else 0.0


def record_metrics(repo_filter=None, type_filter=None):
    """Run assertions and record metrics to JSONL file."""
    assertion_sets = load_assertions(
        DATA_DIR, repo_name=repo_filter, analyzer_type=type_filter)

    timestamp = datetime.now().isoformat()
    records = []

    for aset in assertion_sets:
        atype = aset.get("analyzer_type", "schematic")
        file_pattern = aset.get("file_pattern", "")
        repo = aset.get("_repo", "")
        project_path = aset.get("_project_path")
        source = aset.get("generated_by", "unknown")
        assertions = aset.get("assertions", [])

        output_file = find_output_file(file_pattern, repo, project_path, atype)
        if not output_file:
            continue

        try:
            data = json.loads(output_file.read_text())
        except Exception:
            continue

        for assertion in assertions:
            if assertion.get("aspirational"):
                continue
            result = evaluate_assertion(assertion, data)
            margin = compute_margin(assertion, result)
            records.append({
                "timestamp": timestamp,
                "assertion_id": assertion.get("id", "?"),
                "repo": repo,
                "file_pattern": file_pattern,
                "type": atype,
                "passed": result["passed"],
                "margin": round(margin, 4),
                "source": source,
            })

    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METRICS_FILE, "a") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    return len(records)


def load_metrics():
    """Load all metrics records from JSONL file."""
    if not METRICS_FILE.exists():
        return []
    records = []
    for line in METRICS_FILE.read_text().splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def cmd_fragile(threshold=0.15):
    """Report assertions with margin below threshold."""
    records = load_metrics()
    if not records:
        print("No metrics recorded yet. Run: python3 regression/assertion_metrics.py record")
        return

    # Get most recent run's timestamp
    latest_ts = max(r["timestamp"] for r in records)
    latest = [r for r in records if r["timestamp"] == latest_ts]

    fragile = [r for r in latest if r["passed"] and r["margin"] < threshold]
    fragile.sort(key=lambda r: r["margin"])

    print(f"Fragile assertions (margin < {threshold}, from {len(latest)} evaluated):")
    print(f"Found: {len(fragile)}")
    for r in fragile[:20]:
        print(f"  margin={r['margin']:.3f}  {r['assertion_id']}  "
              f"{r['repo']}/{r['file_pattern']}  [{r['source']}]")
    if len(fragile) > 20:
        print(f"  ... and {len(fragile) - 20} more")


def cmd_stale(min_runs=3):
    """Report assertions that have never failed across multiple runs."""
    records = load_metrics()
    if not records:
        print("No metrics recorded yet.")
        return

    # Group by assertion_id
    by_id = defaultdict(list)
    for r in records:
        by_id[r["assertion_id"]].append(r)

    never_failed = []
    for aid, runs in by_id.items():
        if len(runs) >= min_runs and all(r["passed"] for r in runs):
            never_failed.append({
                "assertion_id": aid,
                "runs": len(runs),
                "avg_margin": sum(r["margin"] for r in runs) / len(runs),
                "source": runs[0].get("source", "?"),
                "repo": runs[0].get("repo", "?"),
            })

    never_failed.sort(key=lambda r: -r["avg_margin"])
    print(f"Assertions that never failed (>={min_runs} runs): {len(never_failed)}")
    for r in never_failed[:20]:
        print(f"  {r['assertion_id']}  {r['runs']} runs  "
              f"avg_margin={r['avg_margin']:.3f}  [{r['source']}]  {r['repo']}")
    if len(never_failed) > 20:
        print(f"  ... and {len(never_failed) - 20} more")


def cmd_summary():
    """Overall quality breakdown."""
    records = load_metrics()
    if not records:
        print("No metrics recorded yet.")
        return

    # Latest run
    latest_ts = max(r["timestamp"] for r in records)
    latest = [r for r in records if r["timestamp"] == latest_ts]

    total = len(latest)
    passed = sum(1 for r in latest if r["passed"])
    failed = total - passed
    margins = [r["margin"] for r in latest if r["passed"]]
    avg_margin = sum(margins) / len(margins) if margins else 0

    by_source = defaultdict(lambda: {"total": 0, "passed": 0, "margins": []})
    for r in latest:
        s = by_source[r["source"]]
        s["total"] += 1
        if r["passed"]:
            s["passed"] += 1
            s["margins"].append(r["margin"])

    # Count runs
    timestamps = set(r["timestamp"] for r in records)

    print(f"Assertion Quality Metrics")
    print(f"{'='*50}")
    print(f"Total runs recorded: {len(timestamps)}")
    print(f"Latest run: {latest_ts[:19]}")
    print(f"Assertions evaluated: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Avg margin (passed): {avg_margin:.3f}")
    print(f"  Fragile (<0.15 margin): {sum(1 for m in margins if m < 0.15)}")
    print(f"  Robust (>0.5 margin): {sum(1 for m in margins if m > 0.5)}")
    print()
    print(f"By source:")
    for source, s in sorted(by_source.items()):
        avg = sum(s["margins"]) / len(s["margins"]) if s["margins"] else 0
        print(f"  {source:<35s} {s['passed']}/{s['total']} passed  "
              f"avg_margin={avg:.3f}")


def main():
    parser = argparse.ArgumentParser(
        description="Assertion quality metrics")
    sub = parser.add_subparsers(dest="command")

    rec = sub.add_parser("record", help="Record metrics for current assertion run")
    rec.add_argument("--repo", help="Only record for this repo")
    rec.add_argument("--type", choices=ANALYZER_TYPES, help="Only this type")

    frag = sub.add_parser("fragile", help="Report fragile assertions")
    frag.add_argument("--threshold", type=float, default=0.15,
                      help="Margin threshold (default: 0.15)")

    stale = sub.add_parser("stale", help="Report never-failed assertions")
    stale.add_argument("--min-runs", type=int, default=3,
                       help="Minimum runs to consider (default: 3)")

    sub.add_parser("summary", help="Overall quality breakdown")

    args = parser.parse_args()

    if args.command == "record":
        n = record_metrics(repo_filter=args.repo, type_filter=args.type)
        print(f"Recorded {n} assertion metrics to {METRICS_FILE}")
    elif args.command == "fragile":
        cmd_fragile(args.threshold)
    elif args.command == "stale":
        cmd_stale(args.min_runs)
    elif args.command == "summary":
        cmd_summary()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
