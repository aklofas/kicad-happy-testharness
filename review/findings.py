#!/usr/bin/env python3
"""Store and manage review findings.

Findings are structured observations from LLM review of analyzer outputs.
They capture what the analyzer got right, wrong, or missed, and can be
promoted to permanent assertions.

Usage:
    python3 review/findings.py list
    python3 review/findings.py list --status confirmed
    python3 review/findings.py show FND-0001
    python3 review/findings.py promote FND-0001
    python3 review/findings.py stats
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
FINDINGS_DIR = HARNESS_DIR / "data" / "findings"
FINDINGS_FILE = FINDINGS_DIR / "findings.json"
ASSERTIONS_DIR = HARNESS_DIR / "data" / "assertions"


def load_findings():
    if FINDINGS_FILE.exists():
        return json.loads(FINDINGS_FILE.read_text())
    return {"findings": []}


def save_findings(data):
    FINDINGS_DIR.mkdir(parents=True, exist_ok=True)
    FINDINGS_FILE.write_text(json.dumps(data, indent=2) + "\n")


def next_id(findings_data):
    existing = [f["id"] for f in findings_data.get("findings", [])]
    nums = []
    for eid in existing:
        try:
            nums.append(int(eid.split("-")[1]))
        except (IndexError, ValueError):
            pass
    next_num = max(nums, default=0) + 1
    return f"FND-{next_num:04d}"


def add_finding(findings_data, finding):
    """Add a new finding. Auto-generates ID and timestamp."""
    fid = next_id(findings_data)
    finding["id"] = fid
    finding["created"] = datetime.now(timezone.utc).isoformat()
    finding.setdefault("status", "new")
    finding.setdefault("correct", [])
    finding.setdefault("incorrect", [])
    finding.setdefault("missed", [])
    finding.setdefault("suggestions", [])
    finding.setdefault("datasheets_used", [])
    finding.setdefault("should_become_assertion", False)
    findings_data["findings"].append(finding)
    return fid


def promote_to_assertion(findings_data, finding_id):
    """Generate an assertion file from a confirmed finding."""
    finding = None
    for f in findings_data["findings"]:
        if f["id"] == finding_id:
            finding = f
            break

    if not finding:
        print(f"Finding {finding_id} not found.")
        return None

    atype = finding.get("analyzer_type", "schematic")
    source = finding.get("source_file", "unknown")

    # Generate assertions from incorrect/missed items
    assertions = []
    ast_num = 1

    for item in finding.get("missed", []):
        section = item.get("analyzer_section", "")
        desc = item.get("description", "")
        if section:
            assertions.append({
                "id": f"{finding_id}-AST-{ast_num:03d}",
                "description": desc,
                "created_from": finding_id,
                "check": {
                    "path": section,
                    "op": "min_count",
                    "value": 1,
                },
                "needs_review": True,
            })
            ast_num += 1

    for item in finding.get("incorrect", []):
        desc = item.get("description", "")
        assertions.append({
            "id": f"{finding_id}-AST-{ast_num:03d}",
            "description": f"REVIEW: {desc}",
            "created_from": finding_id,
            "check": {"path": "", "op": "exists"},
            "needs_review": True,
        })
        ast_num += 1

    if not assertions:
        print(f"No assertions could be generated from {finding_id}.")
        print("Add 'missed' or 'incorrect' entries with 'analyzer_section' fields.")
        return None

    # Build a safe filename from the source file
    safe_name = source.replace("/", "_").replace("\\", "_")
    if safe_name.endswith(".json"):
        safe_name = safe_name[:-5]

    assertion_data = {
        "file_pattern": safe_name,
        "analyzer_type": atype,
        "created_from": finding_id,
        "assertions": assertions,
    }

    # Write to assertions directory
    out_dir = ASSERTIONS_DIR / atype
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{safe_name}.json"

    # Merge with existing if present
    if out_file.exists():
        existing = json.loads(out_file.read_text())
        existing_ids = {a["id"] for a in existing.get("assertions", [])}
        for a in assertions:
            if a["id"] not in existing_ids:
                existing["assertions"].append(a)
        assertion_data = existing

    out_file.write_text(json.dumps(assertion_data, indent=2) + "\n")

    # Update finding status
    finding["status"] = "promoted"
    save_findings(findings_data)

    print(f"Generated {len(assertions)} assertion(s) in {out_file}")
    print("NOTE: Assertions marked needs_review=true need manual review.")
    return assertion_data


def main():
    parser = argparse.ArgumentParser(description="Manage review findings")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List findings")
    show_p = sub.add_parser("show", help="Show a finding")
    show_p.add_argument("id", help="Finding ID (e.g., FND-0001)")
    promote_p = sub.add_parser("promote", help="Promote finding to assertion")
    promote_p.add_argument("id", help="Finding ID")
    sub.add_parser("stats", help="Show statistics")

    # List subcommand options
    for sp in [sub.choices.get("list")]:
        if sp:
            sp.add_argument("--status", help="Filter by status")
            sp.add_argument("--type", help="Filter by analyzer_type")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    data = load_findings()
    findings = data.get("findings", [])

    if args.command == "list":
        filtered = findings
        if hasattr(args, "status") and args.status:
            filtered = [f for f in filtered if f.get("status") == args.status]
        if hasattr(args, "type") and args.type:
            filtered = [f for f in filtered if f.get("analyzer_type") == args.type]

        if not filtered:
            print("No findings found.")
            return

        print(f"{'ID':<12s} {'Status':<12s} {'Type':<12s} File")
        print("-" * 70)
        for f in filtered:
            source = f.get("source_file", "?")
            if len(source) > 40:
                source = "..." + source[-37:]
            print(f"{f['id']:<12s} {f.get('status', '?'):<12s} "
                  f"{f.get('analyzer_type', '?'):<12s} {source}")

    elif args.command == "show":
        finding = next((f for f in findings if f["id"] == args.id), None)
        if not finding:
            print(f"Finding {args.id} not found.")
            sys.exit(1)
        print(json.dumps(finding, indent=2))

    elif args.command == "promote":
        promote_to_assertion(data, args.id)

    elif args.command == "stats":
        by_status = {}
        by_type = {}
        for f in findings:
            s = f.get("status", "unknown")
            t = f.get("analyzer_type", "unknown")
            by_status[s] = by_status.get(s, 0) + 1
            by_type[t] = by_type.get(t, 0) + 1

        print(f"Total findings: {len(findings)}")
        print(f"\nBy status:")
        for s, c in sorted(by_status.items()):
            print(f"  {s}: {c}")
        print(f"\nBy type:")
        for t, c in sorted(by_type.items()):
            print(f"  {t}: {c}")

        actionable = sum(1 for f in findings if f.get("should_become_assertion") and f.get("status") != "promoted")
        if actionable:
            print(f"\nActionable (ready to promote): {actionable}")


if __name__ == "__main__":
    main()
