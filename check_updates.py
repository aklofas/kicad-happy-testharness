#!/usr/bin/env python3
"""Check if tracked repos have upstream updates.

Compares the pinned commit hashes in repos.md against the current HEAD
of each repo's default branch on the remote.

Usage:
    python3 check_updates.py
    python3 check_updates.py --pin        # update repos.md with new hashes
    python3 check_updates.py --fetch      # also git fetch in local clones
    python3 check_updates.py --json
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
CLONE_DIR = HARNESS_DIR / "repos"

# Import repo parser from checkout
sys.path.insert(0, str(HARNESS_DIR))
from checkout import parse_repos_md, pin_hash_in_repos_md, REPOS_MD


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


def main():
    parser = argparse.ArgumentParser(description="Check for upstream updates")
    parser.add_argument("--fetch", action="store_true",
                        help="Also git fetch in local clones")
    parser.add_argument("--pin", action="store_true",
                        help="Update repos.md with new commit hashes")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    if not REPOS_MD.exists():
        print(f"Error: {REPOS_MD} not found")
        sys.exit(1)

    repos = parse_repos_md(REPOS_MD)

    results = []
    updated = 0

    if not args.json:
        print(f"Checking {len(repos)} repos for upstream updates...\n")

    for repo in repos:
        url = repo["url"]
        repo_name = url.rstrip("/").split("/")[-1].removesuffix(".git")
        pinned_hash = repo.get("hash")
        repo_dir = CLONE_DIR / repo_name

        entry = {
            "name": repo_name,
            "url": url,
            "pinned": pinned_hash,
        }

        if not args.json:
            print(f"  {repo_name}...", end="", flush=True)

        # Fetch locally if requested
        if args.fetch and repo_dir.exists():
            fetch_local(repo_dir)

        remote_hash = get_remote_head(url)
        entry["remote"] = remote_hash

        if remote_hash is None:
            entry["status"] = "error"
            if not args.json:
                print(" error (could not reach remote)")
        elif not pinned_hash:
            entry["status"] = "not-pinned"
            if not args.json:
                print(f" not pinned (remote: {remote_hash[:12]})")
            if args.pin:
                pin_hash_in_repos_md(url, remote_hash)
                if not args.json:
                    print(f"    -> pinned {remote_hash[:12]} in repos.md")
        elif remote_hash.startswith(pinned_hash) or pinned_hash.startswith(remote_hash[:len(pinned_hash)]):
            entry["status"] = "up-to-date"
            if not args.json:
                print(" up-to-date")
        else:
            entry["status"] = "update-available"
            updated += 1
            if not args.json:
                print(f" UPDATE AVAILABLE")
                print(f"    pinned: {pinned_hash[:12]}")
                print(f"    remote: {remote_hash[:12]}")
            if args.pin:
                pin_hash_in_repos_md(url, remote_hash)
                if not args.json:
                    print(f"    -> pinned {remote_hash[:12]} in repos.md")

        results.append(entry)

    if args.json:
        print(json.dumps({
            "total": len(results),
            "updates_available": updated,
            "repos": results,
        }, indent=2))
    else:
        print(f"\n{'=' * 50}")
        print(f"Total repos:       {len(results)}")
        print(f"Updates available:  {updated}")
        pinned = sum(1 for r in results if r["status"] == "up-to-date")
        not_pinned = sum(1 for r in results if r["status"] == "not-pinned")
        if pinned:
            print(f"Up to date:        {pinned}")
        if not_pinned:
            print(f"Not pinned:        {not_pinned}")

        if updated:
            print(f"\nTo update, delete the repo dir and re-run checkout.py:")
            for r in results:
                if r["status"] == "update-available":
                    print(f"  rm -rf repos/{r['name']} && python3 checkout.py")


if __name__ == "__main__":
    main()
