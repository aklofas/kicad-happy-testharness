#!/usr/bin/env python3
"""Automated finding review refresh — detect stale findings and clean up.

Runs drift detection on all findings, identifies stale items (possibly fixed bugs,
newly detected circuits, aged findings), and optionally cleans them up.

Usage:
    python3 regression/refresh_findings.py                # dry run
    python3 regression/refresh_findings.py --apply        # clean up stale findings
    python3 regression/refresh_findings.py --repo X       # one repo
    python3 regression/refresh_findings.py --max-age 30   # flag findings older than 30 days
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from drift import validate_finding
from findings import _iter_findings_files, render_md, save_findings
from utils import DATA_DIR


def analyze_finding_drift(finding):
    """Analyze drift for one finding.

    Returns dict with drift summary: {status, total_items, drifted_items,
    possibly_fixed, regressions, now_detected, details}.
    """
    results = validate_finding(finding)

    total = len(results)
    possibly_fixed = sum(1 for cat, _, _ in results if cat == "possibly_fixed")
    regressions = sum(1 for cat, _, _ in results if cat == "regression")
    now_detected = sum(1 for cat, _, _ in results if cat == "now_detected")
    no_output = sum(1 for cat, _, _ in results if cat == "no_output")
    ok = sum(1 for cat, _, _ in results if cat == "ok")

    drifted = possibly_fixed + regressions + now_detected

    if no_output:
        status = "no_output"
    elif total == 0:
        status = "no_checkable_items"
    elif drifted > total * 0.5:
        status = "needs_re_review"
    elif drifted > 0:
        status = "partially_drifted"
    else:
        status = "current"

    return {
        "status": status,
        "total_items": total,
        "drifted_items": drifted,
        "possibly_fixed": possibly_fixed,
        "regressions": regressions,
        "now_detected": now_detected,
        "ok": ok,
        "details": results,
    }


def finding_age_days(finding):
    """Return age of finding in days, or None if no created timestamp."""
    created = finding.get("created")
    if not created:
        return None
    try:
        dt = datetime.fromisoformat(created)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - dt).days
    except (ValueError, TypeError):
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Automated finding review refresh")
    parser.add_argument("--repo", help="Only refresh this repo")
    parser.add_argument("--max-age", type=int, default=30,
                        help="Flag findings older than N days (default: 30)")
    parser.add_argument("--apply", action="store_true",
                        help="Clean up stale findings (remove drifted items)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    total_findings = 0
    stale_findings = []
    aging_findings = []
    all_possibly_fixed = 0
    all_regressions = 0
    all_now_detected = 0
    no_output_count = 0

    for repo, proj, ff in _iter_findings_files(args.repo):
        try:
            data = json.loads(ff.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        findings = data.get("findings", [])
        modified = False

        for finding in findings:
            total_findings += 1
            fid = finding.get("id", "?")

            # Check drift
            drift = analyze_finding_drift(finding)
            all_possibly_fixed += drift["possibly_fixed"]
            all_regressions += drift["regressions"]
            all_now_detected += drift["now_detected"]
            if drift["status"] == "no_output":
                no_output_count += 1

            if drift["status"] in ("needs_re_review", "partially_drifted"):
                stale_findings.append({
                    "repo": repo, "project": proj, "finding_id": fid,
                    "status": drift["status"],
                    "drifted": drift["drifted_items"],
                    "total": drift["total_items"],
                    "possibly_fixed": drift["possibly_fixed"],
                    "regressions": drift["regressions"],
                })

            # Check age
            age = finding_age_days(finding)
            if age is not None and age > args.max_age:
                aging_findings.append({
                    "repo": repo, "project": proj, "finding_id": fid,
                    "age_days": age,
                })

            # Apply cleanup if requested
            if args.apply and drift["possibly_fixed"] > 0:
                # Remove possibly-fixed incorrect items
                new_incorrect = []
                for item in finding.get("incorrect", []):
                    check = item.get("check")
                    if check:
                        from checks import evaluate_assertion
                        from drift import _load_output
                        output = _load_output(
                            finding.get("analyzer_type", ""),
                            finding.get("repo", repo),
                            finding.get("source_file", ""))
                        if output:
                            r = evaluate_assertion(
                                {"check": check, "id": "cleanup",
                                 "description": ""}, output)
                            if r["passed"]:
                                # Bug appears fixed — remove item
                                modified = True
                                continue
                    new_incorrect.append(item)
                finding["incorrect"] = new_incorrect

            if args.apply and drift["now_detected"] > 0:
                # Remove now-detected missed items
                new_missed = []
                for item in finding.get("missed", []):
                    check = item.get("check")
                    if check:
                        from drift import _load_output
                        output = _load_output(
                            finding.get("analyzer_type", ""),
                            finding.get("repo", repo),
                            finding.get("source_file", ""))
                        if output:
                            r = evaluate_assertion(
                                {"check": check, "id": "cleanup",
                                 "description": ""}, output)
                            if r["passed"]:
                                modified = True
                                continue
                    new_missed.append(item)
                finding["missed"] = new_missed

        if modified and args.apply:
            ff.write_text(json.dumps(data, indent=2) + "\n")
            render_md(repo, proj, data)

    if args.json:
        json.dump({
            "total_findings": total_findings,
            "stale": len(stale_findings),
            "aging": len(aging_findings),
            "possibly_fixed": all_possibly_fixed,
            "regressions": all_regressions,
            "now_detected": all_now_detected,
            "no_output": no_output_count,
        }, sys.stdout, indent=2)
        print()
        return

    print(f"Finding Review Refresh")
    print(f"{'='*50}")
    print(f"Findings analyzed: {total_findings}")
    print(f"  Stale (>50% drift): {len(stale_findings)}")
    print(f"  Aging (>{args.max_age} days): {len(aging_findings)}")
    print(f"  Possibly fixed bugs: {all_possibly_fixed}")
    print(f"  Regressions detected: {all_regressions}")
    print(f"  Newly detected: {all_now_detected}")
    print(f"  No output found: {no_output_count}")

    if stale_findings:
        print(f"\nStale findings:")
        for s in stale_findings[:10]:
            print(f"  {s['finding_id']} ({s['repo']}/{s['project']}): "
                  f"{s['drifted']}/{s['total']} items drifted "
                  f"(fixed={s['possibly_fixed']}, regressed={s['regressions']})")
        if len(stale_findings) > 10:
            print(f"  ... and {len(stale_findings) - 10} more")

    if args.apply:
        cleaned = all_possibly_fixed + all_now_detected
        print(f"\nCleaned up {cleaned} drifted items across stale findings")


if __name__ == "__main__":
    main()
