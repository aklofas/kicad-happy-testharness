#!/usr/bin/env python3
"""Generate a health report summarizing test harness state.

Collects metrics across all subsystems and outputs a single-page summary.
Optionally appends to reference/health_log.jsonl for trend tracking.

Usage:
    python3 generate_health_report.py           # Plain text report
    python3 generate_health_report.py --json    # Machine-readable JSON
    python3 generate_health_report.py --log     # Also append to health_log.jsonl
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import DATA_DIR, OUTPUTS_DIR, HARNESS_DIR, safe_load_json

HEALTH_LOG = DATA_DIR / "health_log.jsonl"
REGISTRY_FILE = HARNESS_DIR / "regression" / "bugfix_registry.json"
SCHEMA_INVENTORY = DATA_DIR / "schema_inventory.json"
CONSTANTS_REGISTRY = DATA_DIR / "constants_registry.json"


def _count_assertions():
    """Count assertions by type across all repos."""
    counts = {"SEED": 0, "STRUCT": 0, "FND": 0, "BUGFIX": 0, "OTHER": 0}
    total_files = 0

    if not DATA_DIR.exists():
        return counts, total_files, 0

    aspirational = 0
    for f in DATA_DIR.rglob("assertions/*/*.json"):
        data = safe_load_json(f, {})
        if not data:
            continue
        total_files += 1
        for a in data.get("assertions", []):
            aid = a.get("id", "")
            prefix = aid.split("-")[0] if "-" in aid else "OTHER"
            if prefix in counts:
                counts[prefix] += 1
            else:
                counts["OTHER"] += 1
            if a.get("aspirational"):
                aspirational += 1

    return counts, total_files, aspirational


def _count_findings():
    """Count repos with findings and total finding items."""
    repos_with = 0
    total_items = 0

    for f in DATA_DIR.rglob("findings.json"):
        data = safe_load_json(f, {})
        items = data.get("findings", [])
        if items:
            repos_with += 1
            total_items += len(items)

    return repos_with, total_items


def _count_repos_in_reference():
    """Count repo directories in reference/."""
    if not DATA_DIR.exists():
        return 0
    return sum(1 for d in DATA_DIR.iterdir()
               if d.is_dir() and not d.name.startswith("."))


def _bugfix_coverage():
    """Count bugfix registry entries and total assertions."""
    data = safe_load_json(REGISTRY_FILE, [])
    entries = len(data)
    assertions = sum(len(e.get("assertions", [])) for e in data)
    return entries, assertions


def _schema_status():
    """Get schema inventory metadata."""
    data = safe_load_json(SCHEMA_INVENTORY, {})
    meta = data.get("metadata", {})
    return {
        "schematic_detectors": meta.get("schematic_detectors", 0),
        "pcb_sections": meta.get("pcb_sections", 0),
        "files_scanned": (meta.get("schematic_files_scanned", 0)
                          + meta.get("pcb_files_scanned", 0)),
    }


def _constants_status():
    """Get constants verification summary."""
    data = safe_load_json(CONSTANTS_REGISTRY, {})
    constants = data.get("constants", [])
    if not constants:
        return {"total": 0, "verified": 0, "unverified": 0}

    total = len(constants)
    # Constants use 'source' field for verification provenance
    verified = sum(1 for c in constants
                   if c.get("source") or c.get("verified_date"))
    return {"total": total, "verified": verified, "unverified": total - verified}


def _spice_summary():
    """Get SPICE output summary by counting simulation result files."""
    spice_dir = OUTPUTS_DIR / "spice"
    if not spice_dir.exists():
        return {"repos": 0, "files": 0}

    repos = 0
    files = 0
    for repo_dir in spice_dir.iterdir():
        if repo_dir.is_dir():
            repo_files = list(repo_dir.glob("*.json"))
            if repo_files:
                repos += 1
                files += len(repo_files)

    return {"repos": repos, "files": files}


def collect_metrics():
    """Collect all health metrics."""
    assertion_counts, assertion_files, aspirational = _count_assertions()
    total_assertions = sum(assertion_counts.values())
    repos_with_findings, total_findings = _count_findings()
    bugfix_entries, bugfix_assertions = _bugfix_coverage()
    schema = _schema_status()
    constants = _constants_status()
    spice = _spice_summary()
    repo_count = _count_repos_in_reference()

    return {
        "timestamp": datetime.now().isoformat(),
        "repos_in_reference": repo_count,
        "assertions": {
            "total": total_assertions,
            "files": assertion_files,
            "by_type": assertion_counts,
            "aspirational": aspirational,
        },
        "findings": {
            "repos_with_findings": repos_with_findings,
            "total_items": total_findings,
        },
        "bugfix": {
            "registry_entries": bugfix_entries,
            "assertions": bugfix_assertions,
        },
        "schema": schema,
        "constants": constants,
        "spice": spice,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate health report")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--log", action="store_true",
                        help="Also append to health_log.jsonl")
    args = parser.parse_args()

    metrics = collect_metrics()

    if args.log:
        HEALTH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(HEALTH_LOG, "a") as f:
            f.write(json.dumps(metrics) + "\n")

    if args.json:
        print(json.dumps(metrics, indent=2))
        return

    # Plain text report
    a = metrics["assertions"]
    f = metrics["findings"]
    b = metrics["bugfix"]
    s = metrics["schema"]
    c = metrics["constants"]
    sp = metrics["spice"]

    print("=" * 60)
    print("TEST HARNESS HEALTH REPORT")
    print(f"Generated: {metrics['timestamp'][:19]}")
    print("=" * 60)

    print(f"\nRepos in reference:  {metrics['repos_in_reference']}")

    print(f"\nAssertions:          {a['total']:,} across {a['files']:,} files")
    print(f"  SEED:              {a['by_type']['SEED']:,}")
    print(f"  STRUCT:            {a['by_type']['STRUCT']:,}")
    print(f"  FND:               {a['by_type']['FND']:,}")
    print(f"  BUGFIX:            {a['by_type']['BUGFIX']:,}")
    if a["by_type"]["OTHER"]:
        print(f"  OTHER:             {a['by_type']['OTHER']:,}")
    print(f"  Aspirational:      {a['aspirational']:,}")

    print(f"\nFindings:            {f['total_items']} items across "
          f"{f['repos_with_findings']} repos")

    print(f"\nBugfix registry:     {b['registry_entries']} entries, "
          f"{b['assertions']} assertions")

    print(f"\nSchema inventory:    {s['schematic_detectors']} schematic detectors, "
          f"{s['pcb_sections']} PCB sections "
          f"({s['files_scanned']} files scanned)")

    print(f"\nConstants:           {c['total']} total, "
          f"{c['verified']} verified, {c['unverified']} unverified")

    print(f"\nSPICE outputs:       {sp['repos']} repos, {sp['files']} files")

    if args.log:
        print(f"\nAppended to {HEALTH_LOG}")


if __name__ == "__main__":
    main()
