#!/usr/bin/env python3
"""Extract MPN + Manufacturer pairs from analyzer JSON outputs.

Reads the schematic analyzer JSON results (not raw KiCad files) and
collects all unique MPN entries with their metadata. This ensures we
use the same extraction logic as the analyzer itself.

Usage:
    python3 validate/extract_mpns.py
    python3 validate/extract_mpns.py --repo OpenMower
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import HARNESS_DIR


def is_valid_mpn(mpn: str) -> bool:
    """Filter out placeholder and generic part numbers."""
    mpn = mpn.strip()
    if not mpn:
        return False
    if "\n" in mpn or "\r" in mpn:
        return False
    if mpn.upper() in ("DNP", "DNA", "N/A", "NA", "TBD", "~", "-", "--", "?", ""):
        return False
    if re.match(r'^MF-(RES|CAP|LED|IND|FER|DIO|TVS)', mpn, re.IGNORECASE):
        return False
    if re.match(r'^[RC]\d{4}\s', mpn):
        return False
    if re.match(r'^\d{1,3}$', mpn):
        return False
    return True


def extract_from_json(json_path: Path) -> list:
    """Extract MPN entries from an analyzer JSON output file."""
    try:
        data = json.loads(json_path.read_text())
    except Exception:
        return []

    entries = []
    bom = data.get("bom", [])

    for item in bom:
        mpn = item.get("mpn", "").strip()
        if not mpn or not is_valid_mpn(mpn):
            continue

        entry = {
            "mpn": mpn,
            "manufacturer": item.get("manufacturer", "").strip(),
            "value": item.get("value", ""),
            "datasheet": item.get("datasheet", ""),
            "references": item.get("references", []),
            "quantity": item.get("quantity", 0),
        }

        for dist in ("digikey", "mouser", "lcsc", "element14"):
            val = item.get(dist, "").strip()
            if val:
                entry[dist] = val

        entries.append(entry)

    return entries


def main():
    parser = argparse.ArgumentParser(
        description="Extract MPNs from analyzer JSON outputs")
    parser.add_argument("--repo", help="Only extract from this repo")
    parser.add_argument(
        "--output", "-o",
        default=str(HARNESS_DIR / "results" / "extracted_mpns.json"),
        help="Output JSON file path")
    args = parser.parse_args()

    results_dir = HARNESS_DIR / "results" / "outputs" / "schematic"
    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    seen = set()
    entries = []
    projects = set()

    # Iterate per-repo subdirectories
    if not results_dir.exists():
        print(f"Error: {results_dir} not found. Run analyzers first.")
        return

    # Structure: results/outputs/schematic/{owner}/{repo}/*.json
    owner_dirs = sorted(d for d in results_dir.iterdir() if d.is_dir())
    for owner_dir in owner_dirs:
        repo_dirs = sorted(d for d in owner_dir.iterdir() if d.is_dir())
        if args.repo:
            repo_dirs = [d for d in repo_dirs
                         if d.name == args.repo
                         or f"{owner_dir.name}/{d.name}" == args.repo]
        for repo_dir in repo_dirs:
            project = f"{owner_dir.name}/{repo_dir.name}"
            for json_file in sorted(repo_dir.glob("*.json")):
                file_entries = extract_from_json(json_file)
                for entry in file_entries:
                    key = (entry["mpn"], entry["manufacturer"], project)
                    if key not in seen:
                        seen.add(key)
                        entry["source_project"] = project
                        entries.append(entry)
                        projects.add(project)

    entries.sort(key=lambda e: (e.get("manufacturer", "").lower(), e["mpn"].lower()))

    output_file.write_text(json.dumps(entries, indent=2) + "\n")
    print(f"Extracted {len(entries)} unique MPN entries from {len(projects)} projects")

    from collections import Counter
    by_project = Counter(e["source_project"] for e in entries)
    for proj, count in sorted(by_project.items()):
        print(f"  {proj}: {count} MPNs")

    with_ds = sum(1 for e in entries if e.get("datasheet") and e["datasheet"] != "~")
    print(f"With datasheet URLs: {with_ds}")

    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
