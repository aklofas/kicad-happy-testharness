#!/usr/bin/env python3
"""Generate named cross-sections of the test corpus for targeted testing.

Reads reference/repo_catalog.json and generates reference/cross_sections.json
with named subsets of repos for different testing purposes.

Usage:
    python3 generate_cross_sections.py                # Generate all sections
    python3 generate_cross_sections.py --list          # Show available sections
    python3 generate_cross_sections.py --show smoke    # Print repos in a section
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
from utils import MISC_CATEGORY
CATALOG_FILE = HARNESS_DIR / "reference" / "repo_catalog.json"
SMOKE_PACK_FILE = HARNESS_DIR / "reference" / "smoke_pack.md"
OUTPUT_FILE = HARNESS_DIR / "reference" / "cross_sections.json"


def load_catalog(path):
    """Load repo catalog, return list of repo dicts."""
    return json.loads(path.read_text())


def parse_smoke_pack(path):
    """Parse smoke_pack.md into a list of repo names."""
    repos = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            repos.append(line)
    return repos


def _repo_assertions(entry):
    """Get total assertion count for sorting."""
    return entry.get("assertions", {}).get("total", 0)


def _repo_components(entry):
    """Get total component count."""
    return entry.get("complexity", {}).get("total_components", 0)


def section_smoke(catalog):
    """Curated repos from smoke_pack.md."""
    if not SMOKE_PACK_FILE.exists():
        return []
    repos = parse_smoke_pack(SMOKE_PACK_FILE)
    catalog_repos = {e["repo"] for e in catalog}
    return [r for r in repos if r in catalog_repos]


def section_detector_coverage(catalog, target=120):
    """~120 repos covering all detectors with depth on least-covered ones."""
    all_detectors = set()
    repo_detectors = {}
    for entry in catalog:
        fired = set(entry.get("detectors_fired", {}).keys())
        if fired:
            repo_detectors[entry["repo"]] = fired
            all_detectors.update(fired)

    # Phase 1: greedy set cover for breadth
    covered = set()
    selected = []
    selected_set = set()
    remaining = dict(repo_detectors)
    while covered != all_detectors and remaining:
        best_repo = max(remaining,
                        key=lambda r: len(remaining[r] - covered))
        new_coverage = remaining[best_repo] - covered
        if not new_coverage:
            break
        selected.append(best_repo)
        selected_set.add(best_repo)
        covered.update(new_coverage)
        del remaining[best_repo]

    # Phase 2: add repos exercising least-covered detectors until target
    detector_counts = {d: 0 for d in all_detectors}
    for repo in selected:
        for d in repo_detectors.get(repo, set()):
            detector_counts[d] += 1

    candidates = [(r, ds) for r, ds in repo_detectors.items()
                   if r not in selected_set]
    while len(selected) < target and candidates:
        # Score: sum of 1/count for each detector this repo exercises
        def _score(item):
            return sum(1.0 / max(detector_counts[d], 1) for d in item[1])
        candidates.sort(key=_score, reverse=True)
        best = candidates.pop(0)
        selected.append(best[0])
        selected_set.add(best[0])
        for d in best[1]:
            detector_counts[d] += 1

    return selected


def section_complexity_tiers(catalog, per_tier=20):
    """20 repos per complexity tier, ranked by assertion count."""
    tiers = [
        (0, 20, "trivial"),
        (21, 100, "small"),
        (101, 500, "medium"),
        (501, 2000, "large"),
        (2001, 999999, "massive"),
    ]
    selected = []
    for lo, hi, _label in tiers:
        tier_repos = [e for e in catalog
                      if lo <= _repo_components(e) <= hi]
        tier_repos.sort(key=_repo_assertions, reverse=True)
        selected.extend(e["repo"] for e in tier_repos[:per_tier])
    return selected


def section_kicad_versions(catalog, per_gen=20):
    """20 repos per KiCad generation, ranked by assertion count."""
    generations = {}
    for entry in catalog:
        versions = entry.get("kicad_versions", [])
        for v in versions:
            m = re.match(r"(\d+)", v)
            if m:
                major = int(m.group(1))
                if major >= 5:
                    generations.setdefault(f"kicad{major}", []).append(entry)

    selected = []
    seen = set()
    for gen_name in sorted(generations.keys()):
        entries = generations[gen_name]
        entries.sort(key=_repo_assertions, reverse=True)
        count = 0
        for e in entries:
            if e["repo"] not in seen and count < per_gen:
                selected.append(e["repo"])
                seen.add(e["repo"])
                count += 1
    return selected


def section_category_sample(catalog, per_cat=5):
    """5 best repos per category, ranked by assertion count."""
    categories = {}
    for entry in catalog:
        cat = entry.get("category", MISC_CATEGORY)
        categories.setdefault(cat, []).append(entry)

    selected = []
    for cat in sorted(categories.keys()):
        entries = categories[cat]
        entries.sort(key=_repo_assertions, reverse=True)
        n = min(per_cat, len(entries))
        selected.extend(e["repo"] for e in entries[:n])
    return selected


def section_emc_rich(catalog, top_n=100):
    """Top 100 repos by EMC finding count."""
    with_emc = [e for e in catalog
                if (e.get("emc_summary", {}).get("total_findings", 0) or 0) > 0]
    with_emc.sort(key=lambda e: e["emc_summary"]["total_findings"], reverse=True)
    return [e["repo"] for e in with_emc[:top_n]]


def section_spice_rich(catalog, top_n=100):
    """Top 100 repos by SPICE simulation count."""
    with_spice = [e for e in catalog
                  if (e.get("spice_summary", {}).get("total_simulations", 0) or 0) > 0]
    with_spice.sort(key=lambda e: e["spice_summary"]["total_simulations"],
                    reverse=True)
    return [e["repo"] for e in with_spice[:top_n]]


def section_hierarchical(catalog, target=100):
    """Top 100 repos with multi-sheet hierarchical schematics, ranked by sheet count."""
    multi = [e for e in catalog
             if (e.get("complexity", {}).get("sheets") or 0) > 1]
    multi.sort(key=lambda e: e.get("complexity", {}).get("sheets", 0), reverse=True)
    return [e["repo"] for e in multi[:target]]


def section_quick_200(catalog, other_sections, target=200):
    """~200 repos: union of smaller sections, fill from category_sample."""
    combined = set()
    for name in ("smoke", "detector_coverage", "complexity_tiers", "kicad_versions"):
        if name in other_sections:
            combined.update(other_sections[name]["repos"])

    # Fill remaining from category_sample
    if "category_sample" in other_sections:
        for repo in other_sections["category_sample"]["repos"]:
            combined.add(repo)
            if len(combined) >= target:
                break

    # If still under target, add highest-assertion repos
    if len(combined) < target:
        by_assertions = sorted(catalog, key=_repo_assertions, reverse=True)
        for e in by_assertions:
            combined.add(e["repo"])
            if len(combined) >= target:
                break

    return sorted(combined)


def generate_all(catalog):
    """Generate all cross-sections. Returns sections dict."""
    sections = {}

    # Build individual sections
    builders = [
        ("smoke", "Curated ~20 repos from smoke_pack.md — fast sanity testing",
         lambda: section_smoke(catalog)),
        ("detector_coverage",
         "~120 repos covering all 40 detectors with depth on least-covered",
         lambda: section_detector_coverage(catalog)),
        ("complexity_tiers",
         "20 repos per complexity tier (trivial/small/medium/large/massive)",
         lambda: section_complexity_tiers(catalog)),
        ("kicad_versions", "20 repos per KiCad generation (5/6/7/8/9)",
         lambda: section_kicad_versions(catalog)),
        ("category_sample", "5 best repos per category (24 categories)",
         lambda: section_category_sample(catalog)),
        ("emc_rich", "Top 100 repos by EMC finding diversity",
         lambda: section_emc_rich(catalog)),
        ("spice_rich", "Top 100 repos by SPICE simulation count",
         lambda: section_spice_rich(catalog)),
        ("hierarchical", "Top 100 repos with multi-sheet hierarchical schematics",
         lambda: section_hierarchical(catalog)),
    ]

    for name, desc, builder in builders:
        repos = builder()
        sections[name] = {
            "description": desc,
            "count": len(repos),
            "repos": repos,
        }

    # quick_200 depends on other sections
    q200 = section_quick_200(catalog, sections)
    sections["quick_200"] = {
        "description": "~200 repos balanced across categories/versions/complexity",
        "count": len(q200),
        "repos": q200,
    }

    # full = all repos (null sentinel)
    sections["full"] = {
        "description": "All repos in corpus",
        "count": len(catalog),
        "repos": None,
    }

    return sections


def main():
    parser = argparse.ArgumentParser(
        description="Generate cross-section repo subsets for targeted testing")
    parser.add_argument("--catalog", type=Path, default=CATALOG_FILE,
                        help=f"Input catalog (default: {CATALOG_FILE})")
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE,
                        help=f"Output file (default: {OUTPUT_FILE})")
    parser.add_argument("--list", action="store_true",
                        help="List available sections and exit")
    parser.add_argument("--show", metavar="SECTION",
                        help="Print repos in a section and exit")
    args = parser.parse_args()

    # --list and --show can work from existing file
    if args.list or args.show:
        if not args.output.exists():
            print(f"Error: {args.output} not found. Run without --list/--show first.")
            sys.exit(1)
        data = json.loads(args.output.read_text())
        sections = data.get("sections", {})

        if args.list:
            print(f"{'Section':<25s} {'Count':>6s}  Description")
            print("-" * 80)
            for name in sorted(sections.keys()):
                s = sections[name]
                print(f"{name:<25s} {s['count']:>6d}  {s['description']}")
            return

        if args.show:
            if args.show not in sections:
                available = ", ".join(sorted(sections.keys()))
                print(f"Error: '{args.show}' not found. Available: {available}")
                sys.exit(1)
            s = sections[args.show]
            print(f"# {args.show}: {s['description']} ({s['count']} repos)")
            if s["repos"] is None:
                print("(all repos)")
            else:
                for repo in s["repos"]:
                    print(repo)
            return

    if not args.catalog.exists():
        print(f"Error: {args.catalog} not found. Run: python3 generate_catalog.py")
        sys.exit(1)

    catalog = load_catalog(args.catalog)
    print(f"Loaded {len(catalog)} repos from catalog")

    sections = generate_all(catalog)

    output = {
        "metadata": {
            "generated": datetime.now(timezone.utc).isoformat(),
            "catalog_repos": len(catalog),
            "generator": "generate_cross_sections.py",
        },
        "sections": sections,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")

    print(f"\nGenerated {len(sections)} cross-sections:")
    for name in sorted(sections.keys()):
        s = sections[name]
        print(f"  {name:<25s} {s['count']:>6d} repos  {s['description']}")
    print(f"\nWrote {args.output}")


if __name__ == "__main__":
    main()
