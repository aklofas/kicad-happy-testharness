#!/usr/bin/env python3
"""Clone repos from repos.md at pinned commit hashes.

Reads the list in repos.md, clones each repo into repos/, and checks
out pinned commits where specified. New clones get their HEAD hash
pinned back into repos.md for reproducibility.

Usage:
    python3 checkout.py
    python3 checkout.py --limit 5
    python3 checkout.py --filter "Open*,Glasgow*"
"""

import argparse
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
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


def pin_hash_in_repos_md(url: str, full_hash: str):
    """Write a short commit hash into repos.md for a specific repo URL."""
    short_hash = full_hash[:12]
    lines = REPOS_MD.read_text().splitlines()

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

        new_line = f"- {line_url} @ {short_hash}"
        if shallow:
            new_line += " (shallow)"
        lines[i] = new_line
        REPOS_MD.write_text("\n".join(lines) + "\n")
        return


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
    parser.add_argument("--filter", type=str, default="",
                        help="Comma-separated glob patterns to filter by repo name (e.g. 'Open*,Glasgow*')")
    args = parser.parse_args()

    if not REPOS_MD.exists():
        print(f"Error: {REPOS_MD} not found")
        sys.exit(1)

    repos = parse_repos_md(REPOS_MD)
    if args.filter:
        patterns = [p.strip() for p in args.filter.split(",")]
        repos = [r for r in repos
                 if any(fnmatch.fnmatch(r["url"].rstrip("/").split("/")[-1].removesuffix(".git"), p)
                        for p in patterns)]
    if args.limit:
        repos = repos[:args.limit]

    CLONE_DIR.mkdir(exist_ok=True)

    print(f"=== Cloning {len(repos)} repositories ===")

    cloned = skipped = failed = 0

    for repo in repos:
        url = repo["url"]
        repo_name = url.rstrip("/").split("/")[-1].removesuffix(".git")
        dest = CLONE_DIR / repo_name

        if dest.exists():
            # Verify existing clone is at the pinned hash
            if repo["hash"] and not repo["shallow"]:
                head = get_head_hash(dest)
                if not head.startswith(repo["hash"]):
                    print(f"RESTORE: {repo_name} ({head[:12]} -> {repo['hash'][:12]})", end="", flush=True)
                    if checkout_hash(dest, repo["hash"]):
                        print(" OK")
                    else:
                        failed += 1
                        continue
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


if __name__ == "__main__":
    main()
