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
    python3 checkout.py --check-updates --github-api
    python3 checkout.py --check-updates --filter "Open*"
"""

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from utils import HARNESS_DIR, REPOS_DIR
REPOS_MD = HARNESS_DIR / "repos.md"
CLONE_DIR = REPOS_DIR


def parse_repos_md(path: Path) -> list[dict]:
    """Parse repos.md into a list of repo entries.

    Format per line:
        - https://github.com/user/repo @ abc123 (shallow)
        - https://github.com/user/repo (shallow)
        - https://github.com/user/repo @ abc123
        - https://github.com/user/repo
        - https://github.com/user/repo @ <full sha> (as user/repo@<sha7>)

    The last form is a second entry of the same upstream (an upgrade pair): its own
    repos/ dir, reference/ tree and outputs, named `<url name>@<sha prefix>`.
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

        name = None
        m = _AS_RE.search(text)
        if m:
            name = m.group(1)
            text = (text[:m.start()] + text[m.end():]).strip()

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
            entry = {"url": url, "hash": commit_hash, "shallow": shallow, "category": category}
            if name is not None:
                _check_second_entry(name, url, commit_hash)
                entry["name"] = name
            repos.append(entry)

    return repos


def _repo_name_from_url(url: str) -> str:
    """Extract owner/repo name from URL."""
    parts = url.rstrip("/").removesuffix(".git").split("/")
    return f"{parts[-2]}/{parts[-1]}"


_AS_RE = re.compile(r"\(as ([^()\s]+)\)")


def _check_second_entry(name, url, commit_hash):
    """A second entry is named `<url name>@<prefix of its own pin>` (>= 7 hex chars)."""
    base, _, sha = name.partition("@")
    if (base != _repo_name_from_url(url) or not re.fullmatch(r"[0-9a-f]{7,40}", sha)
            or not commit_hash or not commit_hash.startswith(sha)):
        raise ValueError(f"repos.md second entry {name!r} must be "
                         f"'{_repo_name_from_url(url)}@<prefix of {commit_hash}>'")


def entry_name(entry) -> str:
    """repos/ dir name of a repos.md entry: its `(as ...)` name, else owner/repo of the URL."""
    return entry.get("name") or _repo_name_from_url(entry["url"])


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

        # a second entry's pin is its identity: never re-pinned
        if line_url != url or _AS_RE.search(clean):
            continue

        new_line = f"- {line_url} @ {full_hash}"
        if shallow:
            new_line += " (shallow)"
        lines[i] = new_line
        REPOS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return


# Corpus clones are attacker-shaped: a repo can bloat its default-branch tip or name its own
# git-lfs endpoint in .lfsconfig. Skip LFS smudging (the analyzers never read LFS objects)
# and bound every network git call.
CLONE_TIMEOUT_S = 600


def corpus_git_env():
    return {**os.environ, "GIT_LFS_SKIP_SMUDGE": "1"}


def clone_repo(url: str, dest: Path) -> bool:
    """Shallow-clone a git repo (--depth 1). Returns True on success."""
    cmd = ["git", "clone", "--quiet", "--depth", "1", url, str(dest)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True,
                       timeout=CLONE_TIMEOUT_S, env=corpus_git_env())
        return True
    except subprocess.CalledProcessError as e:
        print(f" FAILED: {e.stderr.strip()}")
        return False
    except subprocess.TimeoutExpired:
        print(f" FAILED: clone timed out after {CLONE_TIMEOUT_S}s")
        return False


def checkout_hash(repo_dir: Path, commit_hash: str) -> bool:
    """Check out a specific commit in a shallow clone.

    Fetches the specific commit with --depth 1, then checks it out.
    Requires full 40-char hash (GitHub rejects short hashes for fetch).
    Returns False when the fetch or the checkout fails — caller decides how to handle.
    """
    try:
        subprocess.run(
            ["git", "fetch", "--quiet", "--depth", "1", "origin", commit_hash],
            cwd=str(repo_dir), check=True, capture_output=True, text=True,
            timeout=CLONE_TIMEOUT_S, env=corpus_git_env(),
        )
        subprocess.run(
            ["git", "checkout", "--quiet", commit_hash],
            cwd=str(repo_dir), check=True, capture_output=True, text=True,
            timeout=CLONE_TIMEOUT_S, env=corpus_git_env(),
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def get_head_hash(repo_dir: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_dir), capture_output=True, text=True,
    )
    return result.stdout.strip()


def ls_remote_head(url: str) -> tuple[str | None, str | None]:
    """(HEAD hash, None) or (None, reason) from an anonymous ls-remote.

    GitHub answers a deleted, private or throttled repo the same way (it asks for a
    username), so `denied-or-missing` cannot tell them apart; only --github-api can.
    """
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--quiet", url, "HEAD"],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except OSError:
        return None, "unreachable"
    if result.returncode == 0:
        out = result.stdout.strip()
        return (out.split()[0], None) if out else (None, "empty")
    err = result.stderr.lower()
    if "could not read username" in err or "not found" in err:
        return None, "denied-or-missing"
    return None, "unreachable"


def get_remote_head(url: str) -> str | None:
    """Get the HEAD commit hash from a remote repo without cloning."""
    return ls_remote_head(url)[0]


_GITHUB_RE = re.compile(r"^https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$")
GRAPHQL_BATCH = 50
GRAPHQL_JOBS = 4


def _graphql_batch(batch):
    """One `gh api graphql` call for up to GRAPHQL_BATCH (url, (owner, repo)); None if unusable."""
    query = "query { " + " ".join(
        f"r{n}: repository(owner: {json.dumps(o)}, name: {json.dumps(r)}) "
        "{ defaultBranchRef { target { oid } } }"
        for n, (_, (o, r)) in enumerate(batch)) + " }"
    try:
        p = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"],
                           capture_output=True, text=True, timeout=120)
        reply = json.loads(p.stdout or "{}")
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None
    data = reply.get("data")
    if not data:
        return None
    not_found = {e["path"][0] for e in reply.get("errors") or []
                 if e.get("type") == "NOT_FOUND" and e.get("path")}
    heads = {}
    for n, (url, _) in enumerate(batch):
        node = data.get(f"r{n}")
        if node is not None:
            oid = ((node.get("defaultBranchRef") or {}).get("target") or {}).get("oid")
            heads[url] = (oid, None) if oid else (None, "empty")
        elif f"r{n}" in not_found:
            heads[url] = (None, "gone")
    return heads


def github_heads(urls) -> dict:
    """Default-branch tips of GitHub repos via authenticated `gh api graphql`.

    Returns {url: (hash, None)} or {url: (None, "gone")} for a repo GitHub reports as not
    found. URLs it could not resolve (gh missing or logged out, other errors) are left out
    so the caller falls back to ls-remote.
    """
    pairs = [(u, m.groups()) for u in urls if (m := _GITHUB_RE.match(u))]
    batches = [pairs[i:i + GRAPHQL_BATCH] for i in range(0, len(pairs), GRAPHQL_BATCH)]
    heads, failed = {}, 0
    with ThreadPoolExecutor(max_workers=GRAPHQL_JOBS) as pool:
        for got in pool.map(_graphql_batch, batches):
            if got is None:
                failed += 1
            else:
                heads.update(got)
    if failed:
        print(f"warning: {failed} gh api graphql batches failed; those repos fall back to "
              "ls-remote", file=sys.stderr)
    return heads


def fetch_local(repo_dir: Path) -> bool:
    """Run git fetch in a local clone."""
    try:
        r = subprocess.run(
            ["git", "fetch", "--quiet"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=60,
        )
        return r.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def _filter_repos(repos, filter_str):
    """Filter repos by comma-separated glob patterns on repo name."""
    if not filter_str:
        return repos
    patterns = [p.strip() for p in filter_str.split(",")]
    return [r for r in repos
            if any(fnmatch.fnmatch(entry_name(r), p)
                   for p in patterns)]


def clone_repos(repos, limit):
    """Clone/restore repos from repos.md. Returns the number of failures: a clone that
    failed, or a clone / existing checkout that could not be put at its pinned commit."""
    if limit:
        repos = repos[:limit]

    CLONE_DIR.mkdir(exist_ok=True)

    print(f"=== Cloning {len(repos)} repositories ===")

    cloned = skipped = failed = 0

    for repo in repos:
        url = repo["url"]
        repo_name = entry_name(repo)
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
                        print(" FAILED (pin failed, keeping current)")
                        failed += 1
                        continue
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
                print(f" FAILED (pin failed, staying at HEAD {get_head_hash(dest)[:12]})")
                failed += 1
                continue
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
    return failed


def _status(pinned_hash, remote_hash):
    if not pinned_hash:
        return "not-pinned"
    if (remote_hash.startswith(pinned_hash)
            or pinned_hash.startswith(remote_hash[:len(pinned_hash)])):
        return "up-to-date"
    return "update-available"


def _check_one_repo(repo, do_fetch, known=None):
    """Check one repo for updates. Returns result dict.

    `known` is a (hash, reason) already resolved for this URL (--github-api).
    """
    url = repo["url"]
    repo_name = entry_name(repo)
    pinned_hash = repo.get("hash")
    repo_dir = CLONE_DIR / repo_name

    entry = {"name": repo_name, "url": url, "pinned": pinned_hash}
    if repo.get("name"):
        entry.update(remote=None, status="second-entry")   # pinned by design; no ls-remote
        return entry

    if do_fetch and repo_dir.exists():
        fetch_local(repo_dir)

    remote_hash, reason = known or ls_remote_head(url)
    entry["remote"] = remote_hash
    if remote_hash:
        entry["status"] = _status(pinned_hash, remote_hash)
    elif reason == "gone":
        entry["status"] = "gone"
    else:
        entry.update(status="error", reason=reason)
    return entry


# One slow second pass over failed lookups: GitHub throttles anonymous ls-remote under load,
# and a throttled repo reads exactly like a deleted one.
RETRY_DELAY_S = 2
RETRY_JOBS = 2


def _retry(repo):
    time.sleep(RETRY_DELAY_S)
    return _check_one_repo(repo, do_fetch=False)   # the first pass already fetched


def check_updates(repos, do_fetch, do_pin, as_json, jobs=8, github_api=False):
    """Check if tracked repos have upstream updates."""
    results = []
    updated = 0
    errors = 0
    total = len(repos)

    if not as_json:
        print(f"Checking {total} repos for upstream updates "
              f"({jobs} parallel workers)...\n")

    known = (github_heads([r["url"] for r in repos if not r.get("name")])
             if github_api else {})

    # Parallel check
    done = 0
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {pool.submit(_check_one_repo, repo, do_fetch, known.get(repo["url"])): repo
                   for repo in repos}
        for future in as_completed(futures):
            entry = future.result()
            results.append(entry)
            done += 1

            # Progress every 100 repos
            if not as_json and done % 100 == 0:
                print(f"  [{done}/{total}] checked...", flush=True)

    failed = {e["name"] for e in results if e["status"] == "error"}
    if failed:
        if not as_json:
            print(f"  retrying {len(failed)} failed lookups ({RETRY_JOBS} workers)...", flush=True)
        retry = [r for r in repos if entry_name(r) in failed]
        with ThreadPoolExecutor(max_workers=RETRY_JOBS) as pool:
            again = {e["name"]: e for e in pool.map(_retry, retry)}
        results = [again.get(e["name"], e) for e in results]

    # Sort results back to original order
    name_order = {entry_name(r): i for i, r in enumerate(repos)}
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

    gone = sum(1 for r in results if r["status"] == "gone")
    reasons = {}
    for r in results:
        if r["status"] == "error":
            reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1

    if as_json:
        print(json.dumps({
            "total": len(results),
            "updates_available": updated,
            "gone": gone,
            "errors": errors,
            "error_reasons": reasons,
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
        if gone:
            print(f"Gone (GitHub):     {gone}")
        if errors:
            print(f"Errors:            {errors} "
                  f"({', '.join(f'{k} {v}' for k, v in sorted(reasons.items()))})")
            if reasons.get("denied-or-missing") and not github_api:
                print("  denied-or-missing may be GitHub throttling anonymous ls-remote; "
                      "re-run with --github-api")

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
    parser.add_argument("--github-api", action="store_true",
                        help="Resolve GitHub repos through authenticated `gh api graphql` "
                             "(with --check-updates); tells deleted repos from throttling")
    parser.add_argument("--best-effort", action="store_true",
                        help="Exit 0 despite clone or pin failures (clone mode)")
    args = parser.parse_args()

    if not REPOS_MD.exists():
        print(f"Error: {REPOS_MD} not found")
        sys.exit(1)

    repos = parse_repos_md(REPOS_MD)
    repos = _filter_repos(repos, args.filter)

    if args.check_updates:
        check_updates(repos, args.fetch, args.pin, args.json, args.jobs, args.github_api)
    else:
        failed = clone_repos(repos, args.limit)
        if failed and not args.best_effort:
            print(f"{failed} clone/pin failures: exit 1 (--best-effort to accept them)",
                  file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
