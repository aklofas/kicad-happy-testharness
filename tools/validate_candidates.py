#!/usr/bin/env python3
"""Validate candidate repos by shallow-cloning and checking for KiCad files.

Sits between search_repos.py and add_repos.py in the expansion pipeline.
Shallow-clones each candidate into a temp directory, checks for KiCad files,
counts components, scores quality, then deletes the temp clone.

Writes results/validated.json with only repos that pass quality thresholds.

Usage:
    python3 validate_candidates.py                         # Validate all candidates
    python3 validate_candidates.py --limit 100             # First 100 only
    python3 validate_candidates.py --min-components 5      # Require 5+ components
    python3 validate_candidates.py --jobs 8                # Parallel validation
    python3 validate_candidates.py --dry-run               # Show stats without writing
    python3 validate_candidates.py --input results/candidates.json
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
from checkout import parse_repos_md, _repo_name_from_url

REPOS_MD = HARNESS_DIR / "repos.md"
CANDIDATES_FILE = HARNESS_DIR / "results" / "candidates.json"
VALIDATED_FILE = HARNESS_DIR / "results" / "validated.json"

# File extensions recognized as KiCad schematics
KICAD_SCH_EXTS = {".kicad_sch"}
LEGACY_SCH_EXTS = {".sch"}
KICAD_PCB_EXTS = {".kicad_pcb"}
GERBER_EXTS = {".gbr", ".gtl", ".gbl", ".gts", ".gbs", ".gto", ".gbo",
               ".drl", ".g1", ".g2", ".g3", ".g4", ".gtp", ".gbp"}


def _is_kicad_legacy_sch(path):
    """Check if a .sch file is KiCad format (not Eagle)."""
    try:
        with open(path, "rb") as f:
            header = f.read(64)
        return header.startswith(b"EESchema")
    except (OSError, IOError):
        return False


def _count_components_kicad_sch(path):
    """Count component instances in a .kicad_sch file (KiCad 6+).

    Counts (lib_id occurrences — each is a component placement.
    """
    try:
        text = path.read_text(errors="ignore", encoding="utf-8")
        return len(re.findall(r"\(lib_id ", text))
    except (OSError, IOError):
        return 0


def _count_components_legacy_sch(path):
    """Count component instances in a legacy .sch file (KiCad 5).

    Counts $Comp blocks.
    """
    try:
        text = path.read_text(errors="ignore", encoding="utf-8")
        return text.count("$Comp")
    except (OSError, IOError):
        return 0


def _count_footprints_pcb(path):
    """Count footprint instances in a .kicad_pcb file."""
    try:
        text = path.read_text(errors="ignore", encoding="utf-8")
        return len(re.findall(r"^\s{2}\(footprint ", text, re.MULTILINE))
    except (OSError, IOError):
        return 0


def _shallow_clone(url, dest, timeout=60):
    """Shallow clone a repo. Returns True on success."""
    try:
        subprocess.run(
            ["git", "clone", "--quiet", "--depth", "1", url, str(dest)],
            capture_output=True, text=True, timeout=timeout, check=True,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def _scan_repo(repo_dir):
    """Scan a cloned repo for KiCad files and count components.

    Returns dict with file counts and component totals.
    """
    result = {
        "kicad_sch_files": 0,
        "legacy_sch_files": 0,
        "kicad_pcb_files": 0,
        "has_gerbers": False,
        "total_components": 0,
        "total_footprints": 0,
        "max_components_per_file": 0,
        "schematic_files": [],  # (path, component_count) tuples
    }

    for root, dirs, files in os.walk(repo_dir):
        # Skip .git and common non-hardware dirs
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__",
                                                 ".github", "docs", "doc"}]
        for fname in files:
            fpath = Path(root) / fname
            suffix = fpath.suffix.lower()

            if suffix in KICAD_SCH_EXTS:
                count = _count_components_kicad_sch(fpath)
                result["kicad_sch_files"] += 1
                result["total_components"] += count
                result["max_components_per_file"] = max(result["max_components_per_file"], count)
                result["schematic_files"].append((str(fpath.relative_to(repo_dir)), count))

            elif suffix in LEGACY_SCH_EXTS:
                if _is_kicad_legacy_sch(fpath):
                    count = _count_components_legacy_sch(fpath)
                    result["legacy_sch_files"] += 1
                    result["total_components"] += count
                    result["max_components_per_file"] = max(result["max_components_per_file"], count)
                    result["schematic_files"].append((str(fpath.relative_to(repo_dir)), count))

            elif suffix in KICAD_PCB_EXTS:
                fp_count = _count_footprints_pcb(fpath)
                result["kicad_pcb_files"] += 1
                result["total_footprints"] += fp_count

            elif suffix in GERBER_EXTS:
                result["has_gerbers"] = True

    return result


def _classify_repo(scan_result):
    """Classify repo type based on scan results.

    Returns one of: 'hardware', 'library', 'tool', 'trivial', 'empty'
    """
    total_sch = scan_result["kicad_sch_files"] + scan_result["legacy_sch_files"]
    total_comp = scan_result["total_components"]

    if total_sch == 0 and scan_result["kicad_pcb_files"] == 0:
        return "empty"

    # Library detection: many schematic files but very few components per file
    if total_sch > 20 and scan_result["max_components_per_file"] < 3:
        return "library"

    if total_comp < 3:
        return "trivial"

    return "hardware"


def _score_quality(scan_result, candidate):
    """Score repo quality 0-100 based on scan results and metadata."""
    score = 0

    total_comp = scan_result["total_components"]
    total_sch = scan_result["kicad_sch_files"] + scan_result["legacy_sch_files"]

    # Component count (0-40 points)
    if total_comp >= 100:
        score += 40
    elif total_comp >= 50:
        score += 30
    elif total_comp >= 20:
        score += 20
    elif total_comp >= 10:
        score += 10
    elif total_comp >= 3:
        score += 5

    # Has PCB (0-20 points)
    if scan_result["kicad_pcb_files"] > 0:
        score += 20

    # Has gerbers (0-10 points) — manufacturing-ready
    if scan_result["has_gerbers"]:
        score += 10

    # Multiple schematic sheets (0-10 points)
    if total_sch >= 3:
        score += 10
    elif total_sch >= 2:
        score += 5

    # Stars from GitHub metadata (0-10 points)
    stars = candidate.get("stars", 0)
    if stars >= 50:
        score += 10
    elif stars >= 10:
        score += 7
    elif stars >= 3:
        score += 3

    # Code-confirmed bonus (0-10 points)
    if candidate.get("has_kicad_files") is True:
        score += 10

    return min(score, 100)


def validate_one(candidate, temp_base, min_components):
    """Validate a single candidate. Returns (candidate, scan_result, status) or None.

    Clones into temp dir, scans, classifies, then deletes the clone.
    """
    owner = candidate["owner"]
    repo = candidate["repo"]
    url = candidate["url"]
    repo_name = f"{owner}/{repo}"

    dest = Path(temp_base) / owner / repo
    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Clone
        if not _shallow_clone(url, dest):
            return candidate, None, "clone_failed"

        # Scan
        scan = _scan_repo(dest)

        # Classify
        classification = _classify_repo(scan)

        if classification == "empty":
            return candidate, scan, "no_kicad_files"
        if classification == "library":
            return candidate, scan, "library"
        if classification == "trivial":
            return candidate, scan, "trivial"
        if scan["total_components"] < min_components:
            return candidate, scan, "below_threshold"

        # Score
        quality = _score_quality(scan, candidate)
        scan["quality_score"] = quality
        scan["classification"] = classification

        return candidate, scan, "pass"

    finally:
        # Always clean up
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        # Clean empty owner dir
        if dest.parent.exists() and not any(dest.parent.iterdir()):
            dest.parent.rmdir()


def main():
    parser = argparse.ArgumentParser(
        description="Validate candidate repos by cloning and checking KiCad files")
    parser.add_argument("--input", type=Path, default=CANDIDATES_FILE,
                        help=f"Input candidates file (default: {CANDIDATES_FILE})")
    parser.add_argument("--output", type=Path, default=VALIDATED_FILE,
                        help=f"Output validated file (default: {VALIDATED_FILE})")
    parser.add_argument("--limit", type=int, default=0,
                        help="Validate only first N candidates")
    parser.add_argument("--min-components", type=int, default=5,
                        help="Minimum total component count to pass (default: 5)")
    parser.add_argument("--min-score", type=int, default=0,
                        help="Minimum quality score to include (default: 0)")
    parser.add_argument("--jobs", "-j", type=int, default=4,
                        help="Parallel validation workers (default: 4)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show validation stats without writing output")
    parser.add_argument("--resume", action="store_true",
                        help="Skip candidates already in output file")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: {args.input} not found. Run search_repos.py first.")
        sys.exit(1)

    candidates = json.loads(args.input.read_text(encoding="utf-8"))
    if args.limit:
        candidates = candidates[:args.limit]

    # Resume support: skip already-validated repos
    already_validated = set()
    if args.resume and args.output.exists():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        already_validated = {f"{c['owner']}/{c['repo']}" for c in existing}
        print(f"Resuming: {len(already_validated)} already validated")

    pending = [c for c in candidates
               if f"{c['owner']}/{c['repo']}" not in already_validated]

    print(f"=== Candidate Validation ===")
    print(f"Total candidates: {len(candidates)}")
    print(f"Already validated: {len(already_validated)}")
    print(f"Pending: {len(pending)}")
    print(f"Min components: {args.min_components}")
    print(f"Workers: {args.jobs}")
    print()

    if not pending:
        print("Nothing to validate.")
        return

    # Create temp directory for clones
    temp_base = tempfile.mkdtemp(prefix="kicad_validate_")
    print(f"Temp dir: {temp_base}")

    # Track results
    passed = []
    stats = {"pass": 0, "clone_failed": 0, "no_kicad_files": 0,
             "library": 0, "trivial": 0, "below_threshold": 0}
    t0 = time.time()
    save_interval = 100  # incremental save every N repos

    def _record_result(cand, scan, status):
        """Record a validation result and return the enriched candidate if passed."""
        stats[status] += 1
        if status == "pass":
            cand_out = cand.copy()
            cand_out["validation"] = {
                "total_components": scan["total_components"],
                "total_footprints": scan["total_footprints"],
                "kicad_sch_files": scan["kicad_sch_files"],
                "legacy_sch_files": scan["legacy_sch_files"],
                "kicad_pcb_files": scan["kicad_pcb_files"],
                "has_gerbers": scan["has_gerbers"],
                "quality_score": scan["quality_score"],
            }
            passed.append(cand_out)

    def _incremental_save(done_count):
        """Save validated.json incrementally to avoid losing progress."""
        if args.dry_run:
            return
        if done_count % save_interval == 0:
            all_passed = passed
            if args.resume and args.output.exists():
                try:
                    existing = json.loads(args.output.read_text(encoding="utf-8"))
                    # Merge: existing + new, dedup by owner/repo
                    seen = {f"{c['owner']}/{c['repo']}" for c in existing}
                    merged = existing + [c for c in passed
                                         if f"{c['owner']}/{c['repo']}" not in seen]
                    all_passed = merged
                except (json.JSONDecodeError, KeyError):
                    all_passed = passed
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(all_passed, indent=2) + "\n", encoding="utf-8")

    def _print_progress(done_count, total):
        if done_count % 10 == 0 or done_count == total:
            elapsed = time.time() - t0
            rate = elapsed / done_count
            remaining = (total - done_count) * rate
            print(f"  [{done_count}/{total}] pass={stats['pass']} "
                  f"fail={sum(v for k,v in stats.items() if k != 'pass')} "
                  f"({elapsed:.0f}s elapsed, ~{remaining/60:.0f}min remaining)")

    try:
        if args.jobs <= 1:
            # Sequential
            for i, candidate in enumerate(pending):
                cand, scan, status = validate_one(candidate, temp_base, args.min_components)
                _record_result(cand, scan, status)
                done = i + 1
                _print_progress(done, len(pending))
                _incremental_save(done)
        else:
            # Parallel
            done = 0
            with ThreadPoolExecutor(max_workers=args.jobs) as pool:
                futures = {
                    pool.submit(validate_one, c, temp_base, args.min_components): c
                    for c in pending
                }
                for future in as_completed(futures):
                    cand, scan, status = future.result()
                    _record_result(cand, scan, status)
                    done += 1
                    _print_progress(done, len(pending))
                    _incremental_save(done)

    finally:
        # Clean up temp dir
        if Path(temp_base).exists():
            shutil.rmtree(temp_base, ignore_errors=True)

    # Merge with previously validated if resuming
    if args.resume and args.output.exists():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        passed = existing + passed

    # Apply min-score filter
    if args.min_score > 0:
        before = len(passed)
        passed = [c for c in passed
                  if c.get("validation", {}).get("quality_score", 0) >= args.min_score]
        print(f"\nScore filter (>={args.min_score}): {before} -> {len(passed)}")

    # Sort by quality score descending, then stars
    passed.sort(key=lambda c: (
        -c.get("validation", {}).get("quality_score", 0),
        -c.get("stars", 0),
    ))

    elapsed = time.time() - t0

    # Print summary
    print(f"\n{'='*60}")
    print(f"VALIDATION RESULTS")
    print(f"{'='*60}")
    print(f"Validated:      {sum(stats.values())}")
    print(f"Passed:         {stats['pass']}")
    print(f"Clone failed:   {stats['clone_failed']}")
    print(f"No KiCad files: {stats['no_kicad_files']}")
    print(f"Library/tool:   {stats['library']}")
    print(f"Trivial (<3):   {stats['trivial']}")
    print(f"Below threshold:{stats['below_threshold']}")
    print(f"Pass rate:      {100*stats['pass']/max(1,sum(stats.values())):.1f}%")
    print(f"Time:           {elapsed:.0f}s ({elapsed/max(1,sum(stats.values())):.1f}s/repo)")

    if passed:
        scores = [c["validation"]["quality_score"] for c in passed]
        comps = [c["validation"]["total_components"] for c in passed]
        print(f"\nPassed repos quality:")
        print(f"  Quality scores: min={min(scores)}, median={sorted(scores)[len(scores)//2]}, "
              f"max={max(scores)}")
        print(f"  Components:     min={min(comps)}, median={sorted(comps)[len(comps)//2]}, "
              f"max={max(comps)}")

        # Quality tier breakdown
        high = sum(1 for s in scores if s >= 60)
        medium = sum(1 for s in scores if 30 <= s < 60)
        low = sum(1 for s in scores if s < 30)
        print(f"  High quality (60+):  {high}")
        print(f"  Medium (30-59):      {medium}")
        print(f"  Low (<30):           {low}")

        # Category breakdown
        cats = {}
        for c in passed:
            cat = c.get("suggested_category", "Miscellaneous")
            cats[cat] = cats.get(cat, 0) + 1
        print(f"\nBy category:")
        for cat, count in sorted(cats.items(), key=lambda x: -x[1])[:15]:
            print(f"  {cat:40s} {count}")

    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(passed, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote {len(passed)} validated candidates to {args.output}")
        print(f"\nNext: python3 add_repos.py --input {args.output}")
    else:
        print(f"\n[DRY RUN] Would write {len(passed)} candidates")


if __name__ == "__main__":
    main()
