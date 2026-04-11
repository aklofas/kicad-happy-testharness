#!/usr/bin/env python3
"""Clone repos from repos.md at pinned commit hashes, and check for updates.

Reads the list in repos.md, clones each repo into repos/, and checks
out pinned commits where specified. New clones get their HEAD hash
pinned back into repos.md for reproducibility.

Usage:
    python3 checkout.py
    python3 checkout.py --limit 5
    python3 checkout.py --filter "Open*,Glasgow*"
    python3 checkout.py --check-updates
    python3 checkout.py --check-updates --pin
    python3 checkout.py --check-updates --fetch
    python3 checkout.py --check-updates --json
    python3 checkout.py --check-updates --filter "Open*"
"""

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from utils import HARNESS_DIR
REPOS_MD = HARNESS_DIR / "repos.md"
CLONE_DIR = HARNESS_DIR / "repos"


def parse_repos_md(path: Path) -> list[dict]:
    """Parse repos.md into a list of repo entries.

    Format per line:
        - https://github.com/user/repo @ abc123 (shallow)
        - https://github.com/user/repo (shallow)
        - https://github.com/user/repo @ abc123
        - https://github.com/user/repo

    Lines starting with # are category headers. Everything else is ignored.
    """
    repos = []
    category = ""

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()

        # Track category from ## headings
        if stripped.startswith("## "):
            category = stripped[3:].strip()
            continue

        # Parse list items: - URL [@ hash] [(shallow)]
        if not stripped.startswith("- http"):
            continue

        text = stripped[2:].strip()  # remove "- "

        # Extract (shallow) flag
        shallow = "(shallow)" in text
        text = text.replace("(shallow)", "").strip()

        # Extract @ hash
        commit_hash = None
        if " @ " in text:
            parts = text.split(" @ ", 1)
            url = parts[0].strip()
            commit_hash = parts[1].strip() or None
        else:
            url = text.strip()

        if url.startswith("http"):
            repos.append({
                "url": url,
                "hash": commit_hash,
                "shallow": shallow,
                "category": category,
            })

    return repos


def _repo_name_from_url(url: str) -> str:
    """Extract owner/repo name from URL."""
    parts = url.rstrip("/").removesuffix(".git").split("/")
    return f"{parts[-2]}/{parts[-1]}"


def pin_hash_in_repos_md(url: str, full_hash: str):
    """Write the full commit hash into repos.md for a specific repo URL."""
    lines = REPOS_MD.read_text(encoding="utf-8").splitlines()

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("- http"):
            continue

        text = stripped[2:].strip()
        shallow = "(shallow)" in text
        clean = text.replace("(shallow)", "").strip()

        # Extract URL (strip existing hash if present)
        line_url = clean.split(" @ ")[0].strip() if " @ " in clean else clean

        if line_url != url:
            continue

        new_line = f"- {line_url} @ {full_hash}"
        if shallow:
            new_line += " (shallow)"
        lines[i] = new_line
        REPOS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return


def clone_repo(url: str, dest: Path) -> bool:
    """Shallow-clone a git repo (--depth 1). Returns True on success."""
    cmd = ["git", "clone", "--quiet", "--depth", "1", url, str(dest)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f" FAILED: {e.stderr.strip()}")
        return False


def checkout_hash(repo_dir: Path, commit_hash: str) -> bool:
    """Check out a specific commit in a shallow clone.

    Fetches the specific commit with --depth 1, then checks it out.
    Requires full 40-char hash (GitHub rejects short hashes for fetch).
    Returns False only on fetch failure — caller decides how to handle.
    """
    try:
        subprocess.run(
            ["git", "fetch", "--quiet", "--depth", "1", "origin", commit_hash],
            cwd=str(repo_dir), check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "checkout", "--quiet", commit_hash],
            cwd=str(repo_dir), check=True, capture_output=True, text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_head_hash(repo_dir: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_dir), capture_output=True, text=True,
    )
    return result.stdout.strip()


def get_remote_head(url: str) -> str | None:
    """Get the HEAD commit hash from a remote repo without cloning."""
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--quiet", url, "HEAD"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split()[0]
    except (subprocess.TimeoutExpired, Exception):
        pass
    return None


def fetch_local(repo_dir: Path) -> bool:
    """Run git fetch in a local clone."""
    try:
        subprocess.run(
            ["git", "fetch", "--quiet"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=60,
        )
        return True
    except Exception:
        return False


def _filter_repos(repos, filter_str):
    """Filter repos by comma-separated glob patterns on repo name."""
    if not filter_str:
        return repos
    patterns = [p.strip() for p in filter_str.split(",")]
    return [r for r in repos
            if any(fnmatch.fnmatch(_repo_name_from_url(r["url"]), p)
                   for p in patterns)]


def clone_repos(repos, limit):
    """Clone/restore repos from repos.md."""
    if limit:
        repos = repos[:limit]

    CLONE_DIR.mkdir(exist_ok=True)

    print(f"=== Cloning {len(repos)} repositories ===")

    cloned = skipped = failed = 0

    for repo in repos:
        url = repo["url"]
        repo_name = _repo_name_from_url(url)
        dest = CLONE_DIR / repo_name

        if dest.exists():
            # Verify existing clone is at the pinned hash
            if repo["hash"] and len(repo["hash"]) >= 40:
                head = get_head_hash(dest)
                if not head.startswith(repo["hash"]):
                    print(f"RESTORE: {repo_name} ({head[:12]} -> {repo['hash'][:12]})", end="", flush=True)
                    if checkout_hash(dest, repo["hash"]):
                        print(" OK")
                    else:
                        print(" (pin failed, keeping current)")
            skipped += 1
            continue

        print(f"CLONE: {repo_name}", end="", flush=True)

        if not clone_repo(url, dest):
            failed += 1
            continue

        # Check out pinned commit via shallow fetch (needs full hash)
        if repo["hash"] and len(repo["hash"]) >= 40:
            print(f" -> {repo['hash'][:12]}", end="", flush=True)
            if not checkout_hash(dest, repo["hash"]):
                print(f" (pin failed, staying at HEAD)", end="")
        elif repo["hash"]:
            print(f" (short hash, staying at HEAD)", end="")

        head = get_head_hash(dest)
        print(f" OK ({head[:12]})")
        cloned += 1

        # Pin hash in repos.md if not already pinned
        if not repo["hash"]:
            pin_hash_in_repos_md(url, head)

    print(f"\n=== Results ===")
    print(f"Cloned:  {cloned}")
    print(f"Skipped: {skipped}")
    print(f"Failed:  {failed}")

    if cloned > 0:
        pinned = sum(1 for r in repos if not r["hash"])
        if pinned:
            print(f"Pinned {pinned} new hashes in repos.md")


def _check_one_repo(repo, do_fetch):
    """Check one repo for updates. Returns result dict."""
    url = repo["url"]
    repo_name = _repo_name_from_url(url)
    pinned_hash = repo.get("hash")
    repo_dir = CLONE_DIR / repo_name

    entry = {"name": repo_name, "url": url, "pinned": pinned_hash}

    if do_fetch and repo_dir.exists():
        fetch_local(repo_dir)

    remote_hash = get_remote_head(url)
    entry["remote"] = remote_hash

    if remote_hash is None:
        entry["status"] = "error"
    elif not pinned_hash:
        entry["status"] = "not-pinned"
    elif (remote_hash.startswith(pinned_hash)
          or pinned_hash.startswith(remote_hash[:len(pinned_hash)])):
        entry["status"] = "up-to-date"
    else:
        entry["status"] = "update-available"

    return entry


def check_updates(repos, do_fetch, do_pin, as_json, jobs=8):
    """Check if tracked repos have upstream updates."""
    results = []
    updated = 0
    errors = 0
    total = len(repos)

    if not as_json:
        print(f"Checking {total} repos for upstream updates "
              f"({jobs} parallel workers)...\n")

    # Parallel check
    done = 0
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {pool.submit(_check_one_repo, repo, do_fetch): repo
                   for repo in repos}
        for future in as_completed(futures):
            entry = future.result()
            results.append(entry)
            done += 1

            # Progress every 100 repos
            if not as_json and done % 100 == 0:
                print(f"  [{done}/{total}] checked...", flush=True)

    # Sort results back to original order
    name_order = {_repo_name_from_url(r["url"]): i for i, r in enumerate(repos)}
    results.sort(key=lambda e: name_order.get(e["name"], 0))

    # Pin hashes (must be sequential — writes to same file)
    for entry in results:
        if entry["status"] == "update-available":
            updated += 1
            if do_pin and entry["remote"]:
                pin_hash_in_repos_md(entry["url"], entry["remote"])
        elif entry["status"] == "not-pinned":
            if do_pin and entry["remote"]:
                pin_hash_in_repos_md(entry["url"], entry["remote"])
        elif entry["status"] == "error":
            errors += 1

    if as_json:
        print(json.dumps({
            "total": len(results),
            "updates_available": updated,
            "errors": errors,
            "repos": results,
        }, indent=2))
    else:
        up_to_date = sum(1 for r in results if r["status"] == "up-to-date")
        not_pinned = sum(1 for r in results if r["status"] == "not-pinned")

        print(f"\n{'=' * 50}")
        print(f"Total repos:       {len(results)}")
        print(f"Up to date:        {up_to_date}")
        print(f"Updates available:  {updated}")
        if not_pinned:
            print(f"Not pinned:        {not_pinned}")
        if errors:
            print(f"Errors:            {errors}")

        if updated and not do_pin:
            print(f"\nRepos with updates:")
            for r in results:
                if r["status"] == "update-available":
                    print(f"  {r['name']:40s} {r['pinned'][:12]} -> {r['remote'][:12]}")
            print(f"\nRe-run with --pin to update hashes in repos.md")

        if do_pin and updated:
            print(f"\nPinned {updated} new hashes in repos.md")
            print(f"To apply: delete updated repo dirs and re-run checkout.py")


def main():
    parser = argparse.ArgumentParser(
        description="Clone repos from repos.md and check for updates")
    parser.add_argument("--limit", type=int, default=0,
                        help="Only clone first N repos (clone mode only)")
    parser.add_argument("--filter", type=str, default="",
                        help="Comma-separated glob patterns to filter by repo name")
    parser.add_argument("--check-updates", action="store_true",
                        help="Check for upstream updates instead of cloning")
    parser.add_argument("--pin", action="store_true",
                        help="Update repos.md with new commit hashes (with --check-updates)")
    parser.add_argument("--fetch", action="store_true",
                        help="Also git fetch in local clones (with --check-updates)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON (with --check-updates)")
    parser.add_argument("--jobs", "-j", type=int, default=8,
                        help="Parallel workers for --check-updates (default: 8)")
    args = parser.parse_args()

    if not REPOS_MD.exists():
        print(f"Error: {REPOS_MD} not found")
        sys.exit(1)

    repos = parse_repos_md(REPOS_MD)
    repos = _filter_repos(repos, args.filter)

    if args.check_updates:
        check_updates(repos, args.fetch, args.pin, args.json, args.jobs)
    else:
        clone_repos(repos, args.limit)


if __name__ == "__main__":
    main()
