#!/usr/bin/env python3
"""Batch-add validated candidate repos to the corpus.

Reads candidates from results/candidates.json (output of search_repos.py),
adds them to repos.md, clones, discovers, runs analyzers, seeds assertions,
and verifies 100% pass rate.

Usage:
    python3 add_repos.py                                    # Process all candidates
    python3 add_repos.py --limit 50                         # First 50 candidates
    python3 add_repos.py --batch-size 25                    # Checkpoint every 25
    python3 add_repos.py --input results/candidates.json    # Explicit input
    python3 add_repos.py --resume                           # Resume interrupted run
    python3 add_repos.py --dry-run                          # Show plan without executing
    python3 add_repos.py --skip-spice --skip-emc            # Skip slow analyzers
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from checkout import parse_repos_md, _repo_name_from_url, get_remote_head
from utils import HARNESS_DIR, REPOS_DIR

REPOS_MD = HARNESS_DIR / "repos.md"
CANDIDATES_FILE = HARNESS_DIR / "results" / "candidates.json"
PROGRESS_FILE = HARNESS_DIR / "results" / "add_repos_progress.json"


def _run_step(name, cmd, timeout=600):
    """Run a pipeline step. Returns (success, detail).

    Follows run_corpus.py:_run_step() pattern.
    """
    t0 = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(HARNESS_DIR),
        )
        elapsed = time.time() - t0
        ok = result.returncode == 0
        # Get last non-empty line of output as detail
        lines = result.stdout.strip().splitlines()
        detail = lines[-1] if lines else ""
        if not ok and result.stderr:
            detail = result.stderr.strip().splitlines()[-1]
        return ok, f"[{'OK' if ok else 'FAIL'}] {name} ({elapsed:.1f}s) {detail}"
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        return False, f"[TIMEOUT] {name} ({elapsed:.1f}s)"
    except Exception as e:
        elapsed = time.time() - t0
        return False, f"[ERROR] {name} ({elapsed:.1f}s) {e}"


def load_candidates(path, limit=0):
    """Load candidates from JSON file."""
    data = json.loads(path.read_text())
    if limit:
        data = data[:limit]
    return data


def load_progress():
    """Load progress tracker from disk."""
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {
        "completed": [],
        "failed": [],
        "purged": [],
        "stats": {
            "total_processed": 0,
            "total_succeeded": 0,
            "total_failed": 0,
            "total_purged": 0,
        },
    }


def save_progress(progress):
    """Save progress tracker to results/add_repos_progress.json."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2) + "\n")


def _find_category_insert_point(lines, category):
    """Find the line index to insert a new repo entry under a ## category.

    Returns the index of the last ``- http`` line in that section + 1,
    or the line before the next ``## `` header if the section is empty.
    Falls back to the end of "Miscellaneous KiCad projects" section.
    """
    fallback_category = "Miscellaneous KiCad projects"
    target = category
    found_target = False
    insert_at = None

    for attempt in range(2):
        in_section = False
        last_entry_in_section = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("## "):
                header = stripped[3:].strip()
                if header == target:
                    in_section = True
                    found_target = True
                    last_entry_in_section = i  # after the header
                elif in_section:
                    # Reached next section — insert before this header
                    # Back up past any blank lines between entries and header
                    insert_at = i
                    while insert_at > 0 and not lines[insert_at - 1].strip():
                        insert_at -= 1
                    return insert_at
            elif in_section and stripped.startswith("- http"):
                last_entry_in_section = i

        if in_section and last_entry_in_section is not None:
            # Section is the last one in the file
            return last_entry_in_section + 1

        if not found_target and attempt == 0:
            target = fallback_category
        else:
            break

    # Last resort: append before end of file
    return len(lines)


def append_to_repos_md(url, commit_hash, category):
    """Append a repo entry under the correct ## category in repos.md.

    If the category doesn't exist, falls back to 'Miscellaneous KiCad projects'.
    """
    lines = REPOS_MD.read_text().splitlines()
    new_line = f"- {url} @ {commit_hash}"
    insert_at = _find_category_insert_point(lines, category)
    lines.insert(insert_at, new_line)
    REPOS_MD.write_text("\n".join(lines) + "\n")


def remove_from_repos_md(url):
    """Remove a repo entry from repos.md by URL."""
    lines = REPOS_MD.read_text().splitlines()
    filtered = [line for line in lines
                if not (line.strip().startswith("- ") and url in line)]
    REPOS_MD.write_text("\n".join(filtered) + "\n")


def process_one_repo(candidate, skip_spice, skip_emc, dry_run):
    """Run the full Checklist 14 pipeline for one repo.

    Returns result dict with status and details.
    """
    owner = candidate["owner"]
    repo = candidate["repo"]
    repo_name = f"{owner}/{repo}"
    url = candidate["url"]
    category = candidate.get("suggested_category", "Miscellaneous KiCad projects")
    py = sys.executable

    result = {"repo": repo_name, "url": url, "status": "ok", "steps": [], "category": category}

    if dry_run:
        print(f"  [DRY-RUN] {repo_name} -> {category}")
        result["status"] = "dry-run"
        return result

    print(f"\n--- {repo_name} ---")

    # Step 1: Get HEAD hash
    print(f"  Getting HEAD hash...", end="", flush=True)
    commit_hash = get_remote_head(url)
    if not commit_hash:
        print(" FAILED (unreachable)")
        result["status"] = "failed"
        result["error"] = "git ls-remote failed"
        return result
    print(f" {commit_hash[:12]}")

    # Step 2: Add to repos.md
    append_to_repos_md(url, commit_hash, category)
    result["steps"].append("repos_md")

    # Step 3: Clone
    ok, detail = _run_step("Clone", [py, "checkout.py", "--filter", repo_name])
    print(f"  {detail}")
    if not ok:
        remove_from_repos_md(url)
        result["status"] = "failed"
        result["error"] = "clone failed"
        return result
    result["steps"].append("clone")

    # Step 4: Discover
    ok, detail = _run_step("Discover", [py, "discover.py", "--repo", repo_name])
    print(f"  {detail}")
    result["steps"].append("discover")

    # Check if any KiCad files were found
    manifest_dir = HARNESS_DIR / "results" / "manifests" / owner / repo
    has_files = False
    for mf in ["schematics.txt", "pcbs.txt"]:
        mf_path = manifest_dir / mf
        if mf_path.exists():
            lines = [l.strip() for l in mf_path.read_text().splitlines() if l.strip()]
            if lines:
                has_files = True
                break

    if not has_files:
        print(f"  PURGE: no KiCad files found")
        remove_from_repos_md(url)
        clone_dir = REPOS_DIR / owner / repo
        if clone_dir.exists():
            shutil.rmtree(clone_dir)
        # Clean up empty owner dir
        owner_dir = REPOS_DIR / owner
        if owner_dir.exists() and not any(owner_dir.iterdir()):
            owner_dir.rmdir()
        result["status"] = "purged"
        result["error"] = "no KiCad files"
        return result

    # Step 5: Run analyzers
    ok, detail = _run_step("Schematic analysis",
                           [py, "run/run_schematic.py", "--repo", repo_name, "--jobs", "4"],
                           timeout=300)
    print(f"  {detail}")
    result["steps"].append("schematic")

    ok, detail = _run_step("PCB analysis",
                           [py, "run/run_pcb.py", "--repo", repo_name, "--jobs", "4"],
                           timeout=300)
    print(f"  {detail}")
    result["steps"].append("pcb")

    ok, detail = _run_step("Gerber analysis",
                           [py, "run/run_gerbers.py", "--repo", repo_name, "--jobs", "4"],
                           timeout=300)
    print(f"  {detail}")
    result["steps"].append("gerber")

    if not skip_spice:
        ok, detail = _run_step("SPICE simulations",
                               [py, "run/run_spice.py", "--repo", repo_name, "--jobs", "16"],
                               timeout=300)
        print(f"  {detail}")
        result["steps"].append("spice")

    if not skip_emc:
        ok, detail = _run_step("EMC analysis",
                               [py, "run/run_emc.py", "--repo", repo_name, "--jobs", "8"],
                               timeout=300)
        print(f"  {detail}")
        result["steps"].append("emc")

    # Step 6: Snapshot baselines
    ok, detail = _run_step("Snapshot", [py, "regression/snapshot.py", "--repo", repo_name])
    print(f"  {detail}")
    result["steps"].append("snapshot")

    # Step 7: Seed assertions
    ok, detail = _run_step("Seed SEED-*", [py, "regression/seed.py", "--repo", repo_name])
    print(f"  {detail}")
    result["steps"].append("seed")

    ok, detail = _run_step("Seed STRUCT-*",
                           [py, "regression/seed_structural.py", "--repo", repo_name])
    print(f"  {detail}")
    result["steps"].append("seed_structural")

    # Step 8: Run checks
    ok, detail = _run_step("Run checks",
                           [py, "regression/run_checks.py", "--repo", repo_name])
    print(f"  {detail}")
    result["steps"].append("run_checks")
    if not ok:
        result["status"] = "checks_failed"
        result["error"] = detail

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Batch-add candidate repos to the corpus")
    parser.add_argument("--input", type=Path, default=CANDIDATES_FILE,
                        help=f"Input candidates file (default: {CANDIDATES_FILE})")
    parser.add_argument("--limit", type=int, default=0,
                        help="Process only first N candidates")
    parser.add_argument("--batch-size", type=int, default=50,
                        help="Save progress every N repos (default: 50)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from previous progress file")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without executing")
    parser.add_argument("--skip-spice", action="store_true",
                        help="Skip SPICE simulations (run later)")
    parser.add_argument("--skip-emc", action="store_true",
                        help="Skip EMC analysis (run later)")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: {args.input} not found. Run search_repos.py first.")
        sys.exit(1)

    candidates = load_candidates(args.input, args.limit)
    progress = load_progress() if args.resume else load_progress()

    # Filter out already-completed repos
    completed_set = set(progress["completed"] + progress["purged"]
                        + [f["repo"] for f in progress["failed"]])
    pending = [c for c in candidates
               if f"{c['owner']}/{c['repo']}" not in completed_set]

    print(f"=== Corpus Expansion ===")
    print(f"Total candidates: {len(candidates)}")
    print(f"Already processed: {len(completed_set)}")
    print(f"Pending: {len(pending)}")
    if args.skip_spice:
        print(f"Skipping: SPICE")
    if args.skip_emc:
        print(f"Skipping: EMC")
    if args.dry_run:
        print(f"Mode: DRY RUN")
    print()

    if not pending:
        print("Nothing to do.")
        return

    t_total = time.time()
    batch_count = 0

    for i, candidate in enumerate(pending):
        result = process_one_repo(candidate, args.skip_spice, args.skip_emc, args.dry_run)

        if not args.dry_run:
            repo_name = result["repo"]
            if result["status"] == "ok":
                progress["completed"].append(repo_name)
                progress["stats"]["total_succeeded"] += 1
            elif result["status"] == "purged":
                progress["purged"].append(repo_name)
                progress["stats"]["total_purged"] += 1
            else:
                progress["failed"].append({
                    "repo": repo_name,
                    "error": result.get("error", "unknown"),
                })
                progress["stats"]["total_failed"] += 1

            progress["stats"]["total_processed"] += 1
            batch_count += 1

            # Save progress at batch boundaries
            if batch_count >= args.batch_size:
                save_progress(progress)
                elapsed = time.time() - t_total
                done = progress["stats"]["total_processed"]
                rate = elapsed / done if done else 0
                remaining = len(pending) - (i + 1)
                eta = rate * remaining
                print(f"\n=== Batch checkpoint ({done} processed, "
                      f"{remaining} remaining, ETA {eta/60:.0f}min) ===\n")
                batch_count = 0

    # Final save
    if not args.dry_run:
        save_progress(progress)

    elapsed = time.time() - t_total
    stats = progress["stats"]

    print(f"\n{'='*60}")
    print(f"EXPANSION COMPLETE")
    print(f"{'='*60}")
    print(f"Processed:  {stats['total_processed']}")
    print(f"Succeeded:  {stats['total_succeeded']}")
    print(f"Purged:     {stats['total_purged']}")
    print(f"Failed:     {stats['total_failed']}")
    print(f"Total time: {elapsed:.0f}s ({elapsed/60:.1f}min)")

    if progress["failed"]:
        print(f"\nFailed repos:")
        for f in progress["failed"][-10:]:
            print(f"  {f['repo']:40s} {f['error']}")

    if stats["total_succeeded"] > 0:
        print(f"\nNext steps:")
        if args.skip_spice:
            print(f"  python3 run/run_spice.py --jobs 16")
        if args.skip_emc:
            print(f"  python3 run/run_emc.py --jobs 8")
        print(f"  python3 generate_catalog.py")
        print(f"  python3 regression/run_checks.py   # verify 100%")


if __name__ == "__main__":
    main()
