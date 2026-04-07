#!/usr/bin/env python3
"""Assertion coverage report — identifies gaps in test coverage.

Scans reference/ for each repo and project, counting assertion types
(SEED, STRUCT, FND, BUGFIX), findings status, and component counts.
Flags high-complexity repos with no semantic validation.

Usage:
    python3 coverage_report.py                  # Full report
    python3 coverage_report.py --uncovered-only  # Only repos with no findings
    python3 coverage_report.py --top 20          # Top 20 uncovered by complexity
    python3 coverage_report.py --json            # Machine-readable output
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
from utils import DATA_DIR, safe_load_json


def _count_assertions_by_prefix(assertions_dir):
    """Count assertions by ID prefix (SEED, STRUCT, FND, BUGFIX) in a project."""
    counts = defaultdict(int)
    if not assertions_dir.exists():
        return dict(counts)

    for type_dir in assertions_dir.iterdir():
        if not type_dir.is_dir():
            continue
        for f in type_dir.glob("*.json"):
            data = safe_load_json(f, {})
            for a in data.get("assertions", []):
                aid = a.get("id", "")
                prefix = aid.split("-")[0] if "-" in aid else "OTHER"
                counts[prefix] += 1

    return dict(counts)


def _count_findings(findings_file):
    """Count findings in a findings.json file. Returns (total, reviewed)."""
    data = safe_load_json(findings_file, {})
    findings = data.get("findings", [])
    total = len(findings)
    reviewed = sum(1 for f in findings
                   if f.get("status") not in (None, "new", ""))
    return total, reviewed


def _get_component_count(project_dir):
    """Get total component count from schematic baselines.

    Baselines are keyed by filename, each with total_components.
    Sum across all files in the project.
    """
    sch = safe_load_json(project_dir / "baselines" / "schematic.json", {})
    total = 0
    for key, val in sch.items():
        if isinstance(val, dict):
            total += val.get("total_components", 0)
    return total


def collect_coverage(repo_filter=None):
    """Collect coverage data for all repos/projects in reference/.

    Returns list of dicts sorted by component count descending.
    """
    if not DATA_DIR.exists():
        return []

    results = []
    for owner_dir in sorted(DATA_DIR.iterdir()):
        if not owner_dir.is_dir() or owner_dir.name.startswith("."):
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir():
                continue
            repo_key = f"{owner_dir.name}/{repo_dir.name}"
            # Skip non-repo files (schema_inventory.json, etc.)
            if not any(d.is_dir() for d in repo_dir.iterdir()):
                continue
            if repo_filter and repo_key != repo_filter:
                continue

            for proj_dir in sorted(repo_dir.iterdir()):
                if not proj_dir.is_dir():
                    continue

                assertions_dir = proj_dir / "assertions"
                findings_file = proj_dir / "findings.json"

                counts = _count_assertions_by_prefix(assertions_dir)
                total_assertions = sum(counts.values())

                findings_total, findings_reviewed = 0, 0
                has_findings = findings_file.exists()
                if has_findings:
                    findings_total, findings_reviewed = _count_findings(findings_file)

                comp_count = _get_component_count(proj_dir)

                results.append({
                    "repo": repo_key,
                    "project": proj_dir.name,
                    "components": comp_count,
                    "total_assertions": total_assertions,
                    "seed": counts.get("SEED", 0),
                    "struct": counts.get("STRUCT", 0),
                    "fnd": counts.get("FND", 0),
                    "bugfix": counts.get("BUGFIX", 0),
                    "other": sum(v for k, v in counts.items()
                                 if k not in ("SEED", "STRUCT", "FND", "BUGFIX")),
                    "findings_total": findings_total,
                    "findings_reviewed": findings_reviewed,
                    "has_findings": has_findings and findings_total > 0,
                })

    return sorted(results, key=lambda r: r["components"], reverse=True)


def main():
    parser = argparse.ArgumentParser(description="Assertion coverage report")
    parser.add_argument("--repo", help="Report for one repo only")
    parser.add_argument("--uncovered-only", action="store_true",
                        help="Only show projects with no findings")
    parser.add_argument("--top", type=int, default=0,
                        help="Show top N uncovered projects by component count")
    parser.add_argument("--json", action="store_true",
                        help="Machine-readable JSON output")
    args = parser.parse_args()

    data = collect_coverage(repo_filter=args.repo)

    if args.uncovered_only or args.top:
        data = [r for r in data if not r["has_findings"]]

    if args.top:
        data = data[:args.top]

    # Summary stats
    total_projects = len(data) if not (args.uncovered_only or args.top) else None
    total_assertions = sum(r["total_assertions"] for r in data)
    with_findings = sum(1 for r in data if r["has_findings"])
    without_findings = sum(1 for r in data if not r["has_findings"])
    high_complexity_no_findings = sum(
        1 for r in data if r["components"] >= 50 and not r["has_findings"]
    )

    if args.json:
        output = {
            "summary": {
                "total_projects": len(data),
                "total_assertions": total_assertions,
                "with_findings": with_findings,
                "without_findings": without_findings,
                "high_complexity_no_findings": high_complexity_no_findings,
            },
            "projects": data,
        }
        print(json.dumps(output, indent=2))
        return

    # Header
    print("=" * 80)
    print("ASSERTION COVERAGE REPORT")
    print("=" * 80)

    if total_projects is not None:
        print(f"Total projects:  {len(data)}")
    print(f"With findings:   {with_findings}")
    print(f"No findings:     {without_findings}")
    print(f"High-complexity without findings (50+ comps): {high_complexity_no_findings}")
    print(f"Total assertions: {total_assertions:,}")
    print()

    if not data:
        print("No projects found.")
        return

    # Table
    print(f"{'Repo':<35s} {'Project':<30s} {'Comp':>5s} "
          f"{'SEED':>5s} {'STRCT':>5s} {'FND':>4s} {'BFX':>4s} {'Find':>5s}")
    print("-" * 100)

    for r in data:
        repo = r["repo"][:34]
        proj = r["project"][:29]
        fnd_str = f"{r['findings_total']}" if r["has_findings"] else "-"
        print(f"{repo:<35s} {proj:<30s} {r['components']:>5d} "
              f"{r['seed']:>5d} {r['struct']:>5d} {r['fnd']:>4d} {r['bugfix']:>4d} "
              f"{fnd_str:>5s}")

    print()
    if args.uncovered_only or args.top:
        print(f"Showing {len(data)} uncovered projects "
              f"(sorted by component count, descending)")


if __name__ == "__main__":
    main()
