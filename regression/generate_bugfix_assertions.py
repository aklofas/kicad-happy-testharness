#!/usr/bin/env python3
"""Generate bugfix regression assertions from the bugfix registry.

Reads bugfix_registry.json and generates assertion files that prevent
fixed bugs from returning. Each assertion is tied to a specific KH-* issue.

Output: reference/{repo}/{project}/assertions/{type}/{file}_bugfix.json

Usage:
    python3 regression/generate_bugfix_assertions.py              # all (dry-run)
    python3 regression/generate_bugfix_assertions.py --apply      # write files
    python3 regression/generate_bugfix_assertions.py --issue KH-150
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import DATA_DIR, data_dir, list_projects_in_data, _truncate_with_hash

REGISTRY_FILE = Path(__file__).resolve().parent / "bugfix_registry.json"


def load_registry():
    """Load the bugfix registry."""
    if not REGISTRY_FILE.exists():
        print(f"Registry not found: {REGISTRY_FILE}")
        return []
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))


def generate_bugfix_assertions(issue_filter=None, dry_run=True):
    """Generate assertion files from bugfix registry.

    Returns (entries_processed, assertions_generated).
    """
    registry = load_registry()
    if not registry:
        return 0, 0

    if issue_filter:
        registry = [e for e in registry if e["issue"] == issue_filter]

    entries_processed = 0
    assertions_generated = 0

    for entry in registry:
        issue = entry["issue"]
        fix_type = entry.get("type", "unknown")
        summary = entry.get("summary", "")
        entry_assertions = entry.get("assertions", [])

        if not entry_assertions:
            continue

        entries_processed += 1

        for i, ast_def in enumerate(entry_assertions, 1):
            repo = ast_def.get("repo", "")
            project = ast_def.get("project", "")
            source_file = ast_def.get("source_file", "")
            check = ast_def.get("check", {})
            desc = ast_def.get("description", f"{issue}: {summary}")

            if not repo or not project or not source_file or not check:
                continue

            # Determine analyzer type from source file extension or explicit field
            atype = ast_def.get("analyzer_type", "")
            if not atype:
                if source_file.endswith(".kicad_sch") or source_file.endswith(".sch"):
                    atype = "schematic"
                elif source_file.endswith(".kicad_pcb"):
                    atype = "pcb"
                else:
                    atype = "schematic"

            assertion = {
                "id": f"BUGFIX-{issue}-{i:02d}",
                "description": desc,
                "issue": issue,
                "fix_type": fix_type,
                "check": check,
            }

            # Build safe filename
            safe = _truncate_with_hash(source_file.replace("/", "_").replace("\\", "_"))

            if dry_run:
                print(f"  {issue} -> {repo}/{project}: {desc}")
                assertions_generated += 1
                continue

            # Write assertion file
            out_dir = data_dir(repo, project, "assertions") / atype
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"{safe}_bugfix.json"

            assertion_data = {
                "file_pattern": safe,
                "analyzer_type": atype,
                "generated_by": "generate_bugfix_assertions.py",
                "evidence_source": "human_review",
                "assertions": [assertion],
            }

            # Merge with existing if present
            if out_file.exists():
                existing = json.loads(out_file.read_text(encoding="utf-8"))
                if existing.get("generated_by") == "generate_bugfix_assertions.py":
                    existing_ids = {a["id"] for a in existing.get("assertions", [])}
                    if assertion["id"] not in existing_ids:
                        existing["assertions"].append(assertion)
                    assertion_data = existing

            out_file.write_text(json.dumps(assertion_data, indent=2) + "\n", encoding="utf-8")
            assertions_generated += 1

    return entries_processed, assertions_generated


def main():
    parser = argparse.ArgumentParser(
        description="Generate bugfix regression assertions")
    parser.add_argument("--issue", help="Only generate for this issue (e.g., KH-150)")
    parser.add_argument("--apply", action="store_true",
                        help="Write files (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without writing (default)")
    args = parser.parse_args()

    dry_run = not args.apply

    if dry_run:
        print("[DRY RUN] Bugfix assertions to generate:\n")

    entries, assertions = generate_bugfix_assertions(
        args.issue, dry_run=dry_run)

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Registry entries processed: {entries}")
    print(f"  Assertions generated: {assertions}")

    if dry_run and assertions > 0:
        print("\nRun with --apply to write files.")


if __name__ == "__main__":
    main()
