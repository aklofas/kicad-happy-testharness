#!/usr/bin/env python3
"""One-time migration: assign FND-* IDs and normalize analyzer_type.

Scans all reference/{owner}/{repo}/{project}/findings.json files and:
  1. Assigns FND-* IDs to findings that lack one
  2. Normalizes analyzer_type: analyze_schematic -> schematic, etc.
  3. Defaults missing/invalid analyzer_type to "schematic"

Usage:
    python3 tools/migrate_findings.py --dry-run   # Preview changes
    python3 tools/migrate_findings.py --apply      # Write changes
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import DATA_DIR
from regression.findings import save_findings

VALID_TYPES = {"schematic", "pcb", "gerber"}

TYPE_MAP = {
    "analyze_schematic": "schematic",
    "analyze_pcb": "pcb",
    "analyze_gerbers": "gerber",
}


def iter_findings_files():
    """Iterate all findings.json under reference/{owner}/{repo}/{project}/."""
    if not DATA_DIR.exists():
        return
    for owner_dir in sorted(DATA_DIR.iterdir()):
        if not owner_dir.is_dir() or owner_dir.name.startswith("."):
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir() or repo_dir.name.startswith("."):
                continue
            repo_key = f"{owner_dir.name}/{repo_dir.name}"
            for proj_dir in sorted(repo_dir.iterdir()):
                if not proj_dir.is_dir():
                    continue
                ff = proj_dir / "findings.json"
                if ff.exists():
                    yield repo_key, proj_dir.name, ff


def get_max_fnd_number():
    """Scan all findings + fnd_counter to find the current max FND number."""
    max_num = 0
    for _, _, ff in iter_findings_files():
        try:
            data = json.loads(ff.read_text())
            for f in data.get("findings", []):
                fid = f.get("id", "")
                if fid.startswith("FND-"):
                    try:
                        max_num = max(max_num, int(fid.split("-")[1]))
                    except (IndexError, ValueError):
                        pass
        except Exception:
            pass

    counter_file = DATA_DIR / "fnd_counter"
    if counter_file.exists():
        try:
            max_num = max(max_num, int(counter_file.read_text().strip()))
        except (ValueError, OSError):
            pass

    return max_num


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("--dry-run", "--apply"):
        print("Usage: python3 tools/migrate_findings.py --dry-run|--apply")
        sys.exit(1)

    dry_run = sys.argv[1] == "--dry-run"
    mode = "DRY RUN" if dry_run else "APPLY"

    # Get the starting ID number
    next_num = get_max_fnd_number() + 1
    print(f"[{mode}] Starting FND number: FND-{next_num:08d}")

    files_changed = 0
    ids_assigned = 0
    types_fixed = 0
    types_defaulted = 0

    for repo, project, ff in iter_findings_files():
        try:
            data = json.loads(ff.read_text())
        except Exception as e:
            print(f"  SKIP {ff}: {e}")
            continue

        findings = data.get("findings", [])
        if not findings:
            continue

        changed = False
        for f in findings:
            # Fix missing ID
            if not f.get("id"):
                new_id = f"FND-{next_num:08d}"
                if dry_run:
                    print(f"  {repo}/{project}: assign {new_id}")
                f["id"] = new_id
                next_num += 1
                ids_assigned += 1
                changed = True

            # Fix analyzer_type
            atype = f.get("analyzer_type")
            if atype in TYPE_MAP:
                new_type = TYPE_MAP[atype]
                if dry_run:
                    print(f"  {repo}/{project} [{f.get('id')}]: "
                          f"type {atype} -> {new_type}")
                f["analyzer_type"] = new_type
                types_fixed += 1
                changed = True
            elif atype is None or atype not in VALID_TYPES:
                if dry_run:
                    print(f"  {repo}/{project} [{f.get('id')}]: "
                          f"type {atype!r} -> schematic (default)")
                f["analyzer_type"] = "schematic"
                types_defaulted += 1
                changed = True

        if changed:
            files_changed += 1
            if not dry_run:
                save_findings(repo, project, data)

    # Update the counter file
    if not dry_run and ids_assigned > 0:
        counter_file = DATA_DIR / "fnd_counter"
        counter_file.write_text(str(next_num - 1))

    print(f"\n[{mode}] Summary:")
    print(f"  Files modified:     {files_changed}")
    print(f"  IDs assigned:       {ids_assigned}")
    print(f"  Types normalized:   {types_fixed}")
    print(f"  Types defaulted:    {types_defaulted}")
    if dry_run:
        print(f"\nRun with --apply to write changes.")


if __name__ == "__main__":
    main()
