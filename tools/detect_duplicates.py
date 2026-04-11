#!/usr/bin/env python3
"""Detect potential duplicate/forked repos in the corpus.

Compares repos by complexity fingerprint (component count, unique parts,
nets, PCB layers, board area) to find soft forks that weren't caught by
GitHub's fork detection.

Usage:
    python3 detect_duplicates.py                    # Find duplicates, print report
    python3 detect_duplicates.py --json              # Output as JSON
    python3 detect_duplicates.py --min-group 3       # Only show groups with 3+ repos
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
CATALOG_FILE = HARNESS_DIR / "reference" / "repo_catalog.json"
OUTPUT_FILE = HARNESS_DIR / "results" / "duplicates.json"


def _fingerprint(entry):
    """Create a complexity fingerprint for a repo entry.

    Returns a hashable tuple or None if data is insufficient.
    """
    c = entry.get("complexity", {})
    total = c.get("total_components", 0)
    unique = c.get("unique_parts", 0)
    nets = c.get("total_nets", 0)
    layers = c.get("pcb_layers_max", 0)
    sheets = c.get("sheets", 0)

    # Skip trivial repos (< 5 components — too generic to match)
    if total < 5:
        return None

    return (total, unique, nets, layers, sheets)


def _project_name_key(entry):
    """Extract normalized project name for name-similarity grouping."""
    repo = entry.get("repo", "")
    # Use just the repo name part (after owner/)
    name = repo.split("/", 1)[-1] if "/" in repo else repo
    # Normalize: lowercase, strip common prefixes/suffixes
    name = name.lower().replace("-", "").replace("_", "").replace(" ", "")
    for suffix in ("hardware", "hw", "pcb", "kicad", "board", "v2", "v3",
                    "rev2", "rev3", "reva", "revb"):
        name = name.replace(suffix, "")
    return name


def find_fingerprint_duplicates(catalog):
    """Find repos with identical complexity fingerprints."""
    groups = defaultdict(list)
    for entry in catalog:
        fp = _fingerprint(entry)
        if fp is not None:
            groups[fp].append(entry["repo"])

    # Only keep groups with 2+ repos
    return {str(k): v for k, v in groups.items() if len(v) >= 2}


def find_name_duplicates(catalog):
    """Find repos with very similar names (likely forks/copies)."""
    groups = defaultdict(list)
    for entry in catalog:
        key = _project_name_key(entry)
        if key and len(key) >= 3:  # Skip very short names
            groups[key].append(entry["repo"])

    return {k: v for k, v in groups.items() if len(v) >= 2}


def cross_reference(fp_groups, name_groups):
    """Find repos that appear in BOTH fingerprint and name groups (strongest signal)."""
    # Build repo → group mappings
    fp_repo_groups = {}
    for gid, repos in fp_groups.items():
        for r in repos:
            fp_repo_groups.setdefault(r, set()).add(gid)

    name_repo_groups = {}
    for gid, repos in name_groups.items():
        for r in repos:
            name_repo_groups.setdefault(r, set()).add(gid)

    # Find repos in both
    both = set(fp_repo_groups.keys()) & set(name_repo_groups.keys())

    # Group them
    confirmed = []
    seen = set()
    for repo in sorted(both):
        if repo in seen:
            continue
        # Find all repos that share a fingerprint AND name group with this one
        cluster = {repo}
        for fp_gid in fp_repo_groups[repo]:
            for peer in fp_groups[fp_gid]:
                if peer in both:
                    cluster.add(peer)
        for name_gid in name_repo_groups[repo]:
            for peer in name_groups[name_gid]:
                if peer in both:
                    cluster.add(peer)
        if len(cluster) >= 2:
            confirmed.append(sorted(cluster))
            seen.update(cluster)

    return confirmed


def main():
    parser = argparse.ArgumentParser(
        description="Detect potential duplicate/forked repos")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--min-group", type=int, default=2,
                        help="Minimum group size to report (default: 2)")
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE,
                        help=f"Output file (default: {OUTPUT_FILE})")
    args = parser.parse_args()

    if not CATALOG_FILE.exists():
        print(f"Error: {CATALOG_FILE} not found")
        sys.exit(1)

    catalog = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(catalog)} repos from catalog")

    # Find duplicates by fingerprint
    fp_groups = find_fingerprint_duplicates(catalog)
    fp_repos = sum(len(v) for v in fp_groups.values())
    print(f"\nFingerprint matches: {len(fp_groups)} groups ({fp_repos} repos)")

    # Find duplicates by name
    name_groups = find_name_duplicates(catalog)
    name_repos = sum(len(v) for v in name_groups.values())
    print(f"Name matches: {len(name_groups)} groups ({name_repos} repos)")

    # Cross-reference (strongest signal)
    confirmed = cross_reference(fp_groups, name_groups)
    confirmed_repos = sum(len(g) for g in confirmed)
    print(f"Confirmed (both match): {len(confirmed)} groups ({confirmed_repos} repos)")

    # Filter by min-group
    fp_filtered = {k: v for k, v in fp_groups.items()
                   if len(v) >= args.min_group}
    name_filtered = {k: v for k, v in name_groups.items()
                     if len(v) >= args.min_group}

    result = {
        "total_repos": len(catalog),
        "fingerprint_groups": len(fp_filtered),
        "fingerprint_repos": sum(len(v) for v in fp_filtered.values()),
        "name_groups": len(name_filtered),
        "name_repos": sum(len(v) for v in name_filtered.values()),
        "confirmed_groups": len(confirmed),
        "confirmed_repos": confirmed_repos,
        "confirmed": confirmed,
        "fingerprint_matches": {k: v for k, v in sorted(fp_filtered.items(),
                                key=lambda x: -len(x[1]))[:50]},
        "name_matches": {k: v for k, v in sorted(name_filtered.items(),
                         key=lambda x: -len(x[1]))[:50]},
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return

    # Save to file
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"\nSaved to {args.output}")

    # Print confirmed duplicates
    if confirmed:
        print(f"\n=== Confirmed Duplicates (fingerprint + name match) ===")
        for group in confirmed:
            print(f"  {' | '.join(group)}")

    # Print largest fingerprint groups
    if fp_filtered:
        print(f"\n=== Largest Fingerprint Groups ===")
        for fp, repos in sorted(fp_filtered.items(),
                                 key=lambda x: -len(x[1]))[:20]:
            print(f"  [{len(repos)} repos] fingerprint={fp}")
            for r in repos[:5]:
                print(f"    {r}")
            if len(repos) > 5:
                print(f"    ... +{len(repos) - 5} more")


if __name__ == "__main__":
    main()
