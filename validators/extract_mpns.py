#!/usr/bin/env python3
"""Extract MPN + Manufacturer pairs from analyzer JSON outputs.

Reads the schematic analyzer JSON results (not raw KiCad files) and
collects all unique MPN entries with their metadata. This ensures we
use the same extraction logic as the analyzer itself.
"""

import argparse
import json
import os
import re
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent


def is_valid_mpn(mpn: str) -> bool:
    """Filter out placeholder and generic part numbers."""
    mpn = mpn.strip()
    if not mpn:
        return False
    if "\n" in mpn or "\r" in mpn:
        return False
    if mpn.upper() in ("DNP", "DNA", "N/A", "NA", "TBD", "~", "-", "--", "?", ""):
        return False
    # Generic MFR- prefixed parts
    if re.match(r'^MF-(RES|CAP|LED|IND|FER|DIO|TVS)', mpn, re.IGNORECASE):
        return False
    # Bare RC designators like "R0402 "
    if re.match(r'^[RC]\d{4}\s', mpn):
        return False
    # Bare numbers
    if re.match(r'^\d{1,3}$', mpn):
        return False
    return True


def project_name_from_filename(filename: str) -> str:
    """Derive project name from safe filename (first segment before _)."""
    # Safe names are like "OpenMower_Hardware_...json"
    # The first part before the first path-separator-turned-underscore is the project
    # But underscores are ambiguous. Use the repos dir to resolve if possible.
    return filename.split("_")[0]


def extract_from_json(json_path: Path) -> list[dict]:
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

        # Include distributor part numbers if present
        for dist in ("digikey", "mouser", "lcsc", "element14"):
            val = item.get(dist, "").strip()
            if val:
                entry[dist] = val

        entries.append(entry)

    return entries


def main():
    parser = argparse.ArgumentParser(
        description="Extract MPNs from analyzer JSON outputs")
    parser.add_argument(
        "--results-dir",
        default=str(HARNESS_DIR / "results" / "outputs" / "schematic"),
        help="Directory containing schematic JSON output files")
    parser.add_argument(
        "--output", "-o",
        default=str(HARNESS_DIR / "results" / "extracted_mpns.json"),
        help="Output JSON file path")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    seen = set()
    entries = []
    projects = set()

    for json_file in sorted(results_dir.glob("*.json")):
        project = project_name_from_filename(json_file.stem)
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

    # Summary by project
    from collections import Counter
    by_project = Counter(e["source_project"] for e in entries)
    for proj, count in sorted(by_project.items()):
        print(f"  {proj}: {count} MPNs")

    # Count how many have datasheet URLs
    with_ds = sum(1 for e in entries if e.get("datasheet") and e["datasheet"] != "~")
    print(f"With datasheet URLs: {with_ds}")

    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
