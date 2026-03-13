#!/usr/bin/env python3
"""Clone repos from repos.md at pinned commit hashes.

Reads the list in repos.md, clones each repo into repos/,
checks out pinned commits where specified, and records HEAD
hashes in repos_state.json for reproducibility.

Usage:
    python3 checkout.py
    python3 checkout.py --limit 5
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
REPOS_MD = HARNESS_DIR / "repos.md"
CLONE_DIR = HARNESS_DIR / "repos"
STATE_FILE = HARNESS_DIR / "repos_state.json"


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

    for line in path.read_text().splitlines():
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


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def clone_repo(url: str, dest: Path, shallow: bool) -> bool:
    """Clone a git repo. Returns True on success."""
    cmd = ["git", "clone", "--quiet"]
    if shallow:
        cmd += ["--depth", "1"]
    cmd += [url, str(dest)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f" FAILED: {e.stderr.strip()}")
        return False


def checkout_hash(repo_dir: Path, commit_hash: str) -> bool:
    """Check out a specific commit. Returns True on success."""
    try:
        subprocess.run(
            ["git", "checkout", "--quiet", commit_hash],
            cwd=str(repo_dir), check=True, capture_output=True, text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f" CHECKOUT FAILED: {e.stderr.strip()}")
        return False


def get_head_hash(repo_dir: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_dir), capture_output=True, text=True,
    )
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description="Clone repos from repos.md")
    parser.add_argument("--limit", type=int, default=0, help="Only clone first N repos")
    args = parser.parse_args()

    if not REPOS_MD.exists():
        print(f"Error: {REPOS_MD} not found")
        sys.exit(1)

    repos = parse_repos_md(REPOS_MD)
    if args.limit:
        repos = repos[:args.limit]

    CLONE_DIR.mkdir(exist_ok=True)
    state = load_state()

    print(f"=== Cloning {len(repos)} repositories ===")

    cloned = skipped = failed = 0

    for repo in repos:
        url = repo["url"]
        repo_name = url.rstrip("/").split("/")[-1].removesuffix(".git")
        dest = CLONE_DIR / repo_name

        if dest.exists():
            print(f"SKIP: {repo_name} (already cloned)")
            skipped += 1
            continue

        shallow_label = " (shallow)" if repo["shallow"] else ""
        print(f"CLONE: {repo_name}{shallow_label}", end="", flush=True)

        if not clone_repo(url, dest, repo["shallow"]):
            failed += 1
            continue

        # Check out pinned commit (skip for shallow clones — already at HEAD)
        if repo["hash"] and not repo["shallow"]:
            print(f" -> {repo['hash'][:12]}", end="", flush=True)
            if not checkout_hash(dest, repo["hash"]):
                failed += 1
                continue

        head = get_head_hash(dest)
        state[repo_name] = head
        save_state(state)

        print(f" OK ({head[:12]})")
        cloned += 1

    print(f"\n=== Results ===")
    print(f"Cloned:  {cloned}")
    print(f"Skipped: {skipped}")
    print(f"Failed:  {failed}")


if __name__ == "__main__":
    main()
