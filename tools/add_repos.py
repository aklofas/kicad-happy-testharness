#!/usr/bin/env python3
"""Batch-add validated candidate repos to the corpus.

Reads candidates from results/candidates.json (output of search_repos.py),
adds them to repos.md, clones, discovers, runs analyzers, seeds assertions,
and verifies 100% pass rate.

Usage:
    python3 add_repos.py                                    # Process all candidates
    python3 add_repos.py --jobs 8                           # 8 repos in parallel
    python3 add_repos.py --limit 50                         # First 50 candidates
    python3 add_repos.py --batch-size 25                    # Checkpoint every 25
    python3 add_repos.py --input results/candidates.json    # Explicit input
    python3 add_repos.py --resume                           # Resume interrupted run
    python3 add_repos.py --dry-run                          # Show plan without executing
    python3 add_repos.py --skip-spice --skip-emc            # Skip slow analyzers

Parallel mode (--jobs > 1):
    Phase 1: Serial pre-add all candidates to repos.md (needs HEAD hash)
    Phase 2: Parallel pipeline per repo (clone, discover, analyze, seed, check)
    Phase 3: Serial post-process (remove purged repos from repos.md)
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
from checkout import parse_repos_md, _repo_name_from_url, get_remote_head
from utils import REPOS_DIR, DEFAULT_JOBS, MISC_CATEGORY, run_pipeline_step

REPOS_MD = HARNESS_DIR / "repos.md"
CANDIDATES_FILE = HARNESS_DIR / "results" / "candidates.json"
PROGRESS_FILE = HARNESS_DIR / "results" / "add_repos_progress.json"


def load_candidates(path, limit=0):
    """Load candidates from JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if limit:
        data = data[:limit]
    return data


def load_progress():
    """Load progress tracker from disk."""
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
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
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2) + "\n", encoding="utf-8")


def _find_category_insert_point(lines, category):
    """Find the line index to insert a new repo entry under a ## category.

    Returns the index of the last ``- http`` line in that section + 1,
    or the line before the next ``## `` header if the section is empty.
    Falls back to the end of "Miscellaneous KiCad projects" section.
    """
    fallback_category = MISC_CATEGORY
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
    lines = REPOS_MD.read_text(encoding="utf-8").splitlines()
    new_line = f"- {url} @ {commit_hash}"
    insert_at = _find_category_insert_point(lines, category)
    lines.insert(insert_at, new_line)
    REPOS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def remove_from_repos_md(url):
    """Remove a repo entry from repos.md by URL."""
    lines = REPOS_MD.read_text(encoding="utf-8").splitlines()
    filtered = [line for line in lines
                if not (line.strip().startswith("- ") and url in line)]
    REPOS_MD.write_text("\n".join(filtered) + "\n", encoding="utf-8")


def _pre_add_repo(candidate):
    """Serial pre-add: get HEAD hash and append to repos.md.

    Returns (repo_name, url, commit_hash, category) or None on failure.
    """
    owner = candidate["owner"]
    repo = candidate["repo"]
    repo_name = f"{owner}/{repo}"
    url = candidate["url"]
    category = candidate.get("suggested_category", MISC_CATEGORY)

    print(f"  {repo_name} ...", end="", flush=True)
    commit_hash = get_remote_head(url)
    if not commit_hash:
        print(" FAILED (unreachable)")
        return None
    print(f" {commit_hash[:12]}")

    append_to_repos_md(url, commit_hash, category)
    return (repo_name, url, commit_hash, category)


def _pipeline_one_repo(repo_name, skip_spice, skip_emc):
    """Run the clone-through-checks pipeline for one repo.

    This is a top-level function (picklable) for use with ProcessPoolExecutor.
    Each repo writes to its own dirs so there are no shared-file conflicts.

    Returns result dict with status and details.
    """
    owner, repo = repo_name.split("/", 1)
    py = sys.executable

    result = {"repo": repo_name, "status": "ok", "steps": [], "log": []}

    def log_step(detail):
        result["log"].append(detail)

    ok, detail = run_pipeline_step("Clone", [py, "checkout.py", "--filter", repo_name])
    log_step(detail)
    if not ok:
        result["status"] = "failed"
        result["error"] = "clone failed"
        result["purge"] = True
        return result
    result["steps"].append("clone")

    ok, detail = run_pipeline_step("Discover", [py, "discover.py", "--repo", repo_name])
    log_step(detail)
    result["steps"].append("discover")

    # Check if any KiCad files were found
    manifest_dir = HARNESS_DIR / "results" / "manifests" / owner / repo
    has_files = False
    for mf in ["schematics.txt", "pcbs.txt"]:
        mf_path = manifest_dir / mf
        if mf_path.exists():
            lines = [l.strip() for l in mf_path.read_text(encoding="utf-8").splitlines() if l.strip()]
            if lines:
                has_files = True
                break

    if not has_files:
        log_step("PURGE: no KiCad files found")
        clone_dir = REPOS_DIR / owner / repo
        if clone_dir.exists():
            shutil.rmtree(clone_dir)
        owner_dir = REPOS_DIR / owner
        if owner_dir.exists() and not any(owner_dir.iterdir()):
            owner_dir.rmdir()
        result["status"] = "purged"
        result["error"] = "no KiCad files"
        result["purge"] = True
        return result

    ok, detail = run_pipeline_step("Schematic analysis",
                           [py, "run/run_schematic.py", "--repo", repo_name, "--jobs", "4"],
                           timeout=300)
    log_step(detail)
    result["steps"].append("schematic")

    ok, detail = run_pipeline_step("PCB analysis",
                           [py, "run/run_pcb.py", "--repo", repo_name, "--jobs", "4"],
                           timeout=300)
    log_step(detail)
    result["steps"].append("pcb")

    ok, detail = run_pipeline_step("Gerber analysis",
                           [py, "run/run_gerbers.py", "--repo", repo_name, "--jobs", "4"],
                           timeout=300)
    log_step(detail)
    result["steps"].append("gerber")

    if not skip_spice:
        ok, detail = run_pipeline_step("SPICE simulations",
                               [py, "run/run_spice.py", "--repo", repo_name, "--jobs", "16"],
                               timeout=300)
        log_step(detail)
        result["steps"].append("spice")

    if not skip_emc:
        ok, detail = run_pipeline_step("EMC analysis",
                               [py, "run/run_emc.py", "--repo", repo_name, "--jobs", "8"],
                               timeout=300)
        log_step(detail)
        result["steps"].append("emc")

    ok, detail = run_pipeline_step("Snapshot", [py, "regression/snapshot.py", "--repo", repo_name])
    log_step(detail)
    result["steps"].append("snapshot")

    ok, detail = run_pipeline_step("Seed SEED-*", [py, "regression/seed.py", "--repo", repo_name])
    log_step(detail)
    result["steps"].append("seed")

    ok, detail = run_pipeline_step("Seed STRUCT-*",
                           [py, "regression/seed_structural.py", "--repo", repo_name])
    log_step(detail)
    result["steps"].append("seed_structural")

    ok, detail = run_pipeline_step("Run checks",
                           [py, "regression/run_checks.py", "--repo", repo_name])
    log_step(detail)
    result["steps"].append("run_checks")
    if not ok:
        result["status"] = "checks_failed"
        result["error"] = detail

    return result


def process_one_repo(candidate, skip_spice, skip_emc, dry_run):
    """Run the full Checklist 14 pipeline for one repo (serial mode).

    Returns result dict with status and details.
    """
    owner = candidate["owner"]
    repo = candidate["repo"]
    repo_name = f"{owner}/{repo}"
    url = candidate["url"]
    category = candidate.get("suggested_category", MISC_CATEGORY)

    result = {"repo": repo_name, "url": url, "status": "ok", "steps": [], "category": category}

    if dry_run:
        print(f"  [DRY-RUN] {repo_name} -> {category}")
        result["status"] = "dry-run"
        return result

    print(f"\n--- {repo_name} ---")

    # Pre-add to repos.md
    added = _pre_add_repo(candidate)
    if not added:
        result["status"] = "failed"
        result["error"] = "git ls-remote failed"
        return result

    result["steps"].append("repos_md")

    # Run pipeline
    pipe_result = _pipeline_one_repo(repo_name, skip_spice, skip_emc)
    for line in pipe_result.get("log", []):
        print(f"  {line}")
    result["steps"] = ["repos_md"] + pipe_result["steps"]
    result["status"] = pipe_result["status"]
    if "error" in pipe_result:
        result["error"] = pipe_result["error"]

    # Post-process: remove from repos.md if purged or clone failed
    if pipe_result.get("purge"):
        remove_from_repos_md(url)

    return result


def _update_progress(progress, result):
    """Update progress dict from a single repo result. Returns status string."""
    repo_name = result["repo"]
    status = result["status"]
    if status == "ok":
        progress["completed"].append(repo_name)
        progress["stats"]["total_succeeded"] += 1
    elif status == "purged":
        progress["purged"].append(repo_name)
        progress["stats"]["total_purged"] += 1
    else:
        progress["failed"].append({
            "repo": repo_name,
            "error": result.get("error", "unknown"),
        })
        progress["stats"]["total_failed"] += 1
    progress["stats"]["total_processed"] += 1
    return status


def _run_serial(pending, progress, args):
    """Original serial processing loop."""
    t_total = time.time()
    batch_count = 0

    for i, candidate in enumerate(pending):
        result = process_one_repo(candidate, args.skip_spice, args.skip_emc, args.dry_run)

        if not args.dry_run:
            _update_progress(progress, result)
            batch_count += 1

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

    return time.time() - t_total


def _run_parallel(pending, progress, args):
    """Parallel processing: serial pre-add, parallel pipeline, serial post-process."""
    jobs = args.jobs
    t_total = time.time()

    # --- Phase 1: Serial pre-add all candidates to repos.md ---
    print(f"Phase 1: Pre-adding {len(pending)} repos to repos.md...")
    pre_added = []  # list of (repo_name, url, commit_hash, category)
    pre_failed = []  # candidates that failed ls-remote

    for candidate in pending:
        added = _pre_add_repo(candidate)
        if added:
            pre_added.append(added)
        else:
            repo_name = f"{candidate['owner']}/{candidate['repo']}"
            pre_failed.append({
                "repo": repo_name,
                "url": candidate["url"],
                "status": "failed",
                "error": "git ls-remote failed",
            })

    # Record pre-add failures
    for fail in pre_failed:
        _update_progress(progress, fail)

    print(f"  Pre-added: {len(pre_added)}, unreachable: {len(pre_failed)}")
    if not pre_added:
        return time.time() - t_total

    # --- Phase 2: Parallel pipeline ---
    print(f"\nPhase 2: Running pipeline on {len(pre_added)} repos ({jobs} parallel)...")

    batch_count = 0
    completed_count = 0

    with ProcessPoolExecutor(max_workers=jobs) as pool:
        futures = {}
        for repo_name, url, commit_hash, category in pre_added:
            future = pool.submit(_pipeline_one_repo, repo_name,
                                 args.skip_spice, args.skip_emc)
            futures[future] = (repo_name, url, category)

        for future in as_completed(futures):
            repo_name, url, category = futures[future]
            try:
                result = future.result()
            except Exception as e:
                result = {
                    "repo": repo_name,
                    "status": "failed",
                    "error": str(e),
                    "log": [],
                }

            result["url"] = url
            result["category"] = category
            completed_count += 1

            # Print progress
            status_tag = result["status"].upper()
            elapsed = time.time() - t_total
            print(f"  [{completed_count}/{len(pre_added)}] {status_tag:12s} {repo_name} "
                  f"({elapsed:.0f}s elapsed)")
            for line in result.get("log", []):
                print(f"    {line}")

            # Post-process: remove from repos.md if purged or clone failed
            if result.get("purge"):
                remove_from_repos_md(url)

            _update_progress(progress, result)
            batch_count += 1

            if batch_count >= args.batch_size:
                save_progress(progress)
                done = progress["stats"]["total_processed"]
                remaining = len(pre_added) - completed_count + len(pre_failed)
                rate = elapsed / done if done else 0
                eta = rate * remaining
                print(f"\n=== Batch checkpoint ({done} processed, "
                      f"{remaining} remaining, ETA {eta/60:.0f}min) ===\n")
                batch_count = 0

    return time.time() - t_total


def main():
    parser = argparse.ArgumentParser(
        description="Batch-add candidate repos to the corpus")
    parser.add_argument("--input", type=Path, default=CANDIDATES_FILE,
                        help=f"Input candidates file (default: {CANDIDATES_FILE})")
    parser.add_argument("--limit", type=int, default=0,
                        help="Process only first N candidates")
    parser.add_argument("--batch-size", type=int, default=50,
                        help="Save progress every N repos (default: 50)")
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel repo pipelines (default: {DEFAULT_JOBS})")
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
    progress = load_progress() if args.resume else {"completed": [], "purged": [], "failed": []}

    # Filter out already-completed repos
    completed_set = set(progress["completed"] + progress["purged"]
                        + [f["repo"] for f in progress["failed"]])
    pending = [c for c in candidates
               if f"{c['owner']}/{c['repo']}" not in completed_set]

    print(f"=== Corpus Expansion ===")
    print(f"Total candidates: {len(candidates)}")
    print(f"Already processed: {len(completed_set)}")
    print(f"Pending: {len(pending)}")
    print(f"Jobs: {args.jobs}")
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

    # Route to serial or parallel depending on --jobs
    if args.jobs <= 1 or args.dry_run:
        elapsed = _run_serial(pending, progress, args)
    else:
        elapsed = _run_parallel(pending, progress, args)

    # Final save
    if not args.dry_run:
        save_progress(progress)

    stats = progress["stats"]

    print(f"\n{'='*60}")
    print(f"EXPANSION COMPLETE")
    print(f"{'='*60}")
    print(f"Processed:  {stats['total_processed']}")
    print(f"Succeeded:  {stats['total_succeeded']}")
    print(f"Purged:     {stats['total_purged']}")
    print(f"Failed:     {stats['total_failed']}")
    print(f"Total time: {elapsed:.0f}s ({elapsed/60:.1f}min)")
    if stats["total_processed"] > 0:
        print(f"Rate:       {elapsed / stats['total_processed']:.1f}s/repo")

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
