#!/usr/bin/env python3
"""Discover KiCad repositories on GitHub, GitLab, Codeberg, and Bitbucket.

GitHub search uses three strategies via ``gh`` CLI:
  1. Code search (extension:kicad_sch) — highest signal, proves files exist
  2. Topic search (topic:kicad) — good signal, easy pagination
  3. Keyword search (kicad pcb) — broad sweep, higher false-positive rate

GitLab, Codeberg, and Bitbucket use their public REST APIs via urllib.

Deduplicates against repos.md and outputs candidates to results/candidates.json.

Usage:
    python3 search_repos.py --strategy code
    python3 search_repos.py --strategy topic
    python3 search_repos.py --strategy keyword
    python3 search_repos.py --all
    python3 search_repos.py --all --limit 500
    python3 search_repos.py --source gitlab
    python3 search_repos.py --source codeberg
    python3 search_repos.py --source bitbucket
    python3 search_repos.py --source all            # All platforms
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
from checkout import parse_repos_md, _repo_name_from_url
from utils import MISC_CATEGORY

REPOS_MD = HARNESS_DIR / "repos.md"
CANDIDATES_FILE = HARNESS_DIR / "results" / "candidates.json"

# GitHub search API: 30 req/min — 2.1s between requests is safe
RATE_LIMIT_DELAY = 2.1

# Size shards for code search (bypass 1,000-result limit per query).
# GitHub code search supports size: but NOT pushed:/created: qualifiers.
# Shards are tuned so most return <1,000 results; large-file shards may
# be truncated but still yield plenty of unique repos.
CODE_SEARCH_SHARDS = [
    (0, 1000),
    (1001, 5000),
    (5001, 10000),
    (10001, 20000),
    (20001, 50000),
    (50001, 100000),
    (100001, 200000),
    (200001, 500000),
]

# GitHub topic -> repos.md category
TOPIC_CATEGORY_MAP = {
    "keyboard": "Keyboards",
    "mechanical-keyboard": "Keyboards",
    "qmk": "Keyboards",
    "zmk": "Keyboards",
    "esp32": "ESP32",
    "esp8266": "ESP32",
    "stm32": "STM32",
    "rp2040": "RP2040 / Raspberry Pi",
    "raspberry-pi": "RP2040 / Raspberry Pi",
    "raspberry-pi-pico": "RP2040 / Raspberry Pi",
    "pico": "RP2040 / Raspberry Pi",
    "arduino": "Arduino recreations",
    "arduino-shield": "Arduino recreations",
    "synthesizer": "Synthesizers / audio",
    "eurorack": "Synthesizers / audio",
    "audio": "Synthesizers / audio",
    "led": "LED / display",
    "display": "LED / display",
    "risc-v": "RISC-V / FPGA",
    "riscv": "RISC-V / FPGA",
    "fpga": "RISC-V / FPGA",
    "cubesat": "CubeSat / aerospace",
    "satellite": "CubeSat / aerospace",
    "aerospace": "CubeSat / aerospace",
    "robotics": "Motor controllers / robotics",
    "robot": "Motor controllers / robotics",
    "motor-controller": "Motor controllers / robotics",
    "motor": "Motor controllers / robotics",
    "battery": "Power / battery",
    "power-supply": "Power / battery",
    "bms": "Power / battery",
    "sdr": "Networking / radio / SDR",
    "radio": "Networking / radio / SDR",
    "ham-radio": "Networking / radio / SDR",
    "lora": "Networking / radio / SDR",
    "lorawan": "Networking / radio / SDR",
    "retro": "Retro computing",
    "retro-computing": "Retro computing",
    "z80": "Retro computing",
    "6502": "Retro computing",
    "sensor": "Sensor boards / IoT",
    "iot": "Sensor boards / IoT",
    "usb": "USB / interface adapters",
    "test-equipment": "Test equipment / debug tools",
    "oscilloscope": "Test equipment / debug tools",
    "sparkfun": "SparkFun boards",
    "wearable": "Smartwatches / wearables",
    "smartwatch": "Smartwatches / wearables",
    "adc": "ADC / DAC / measurement",
    "dac": "ADC / DAC / measurement",
    "single-board-computer": "SBCs / carrier boards",
    "sbc": "SBCs / carrier boards",
}

# Description/name keywords -> category (fallback when topics miss)
KEYWORD_CATEGORY_MAP = {
    "esp32": "ESP32",
    "esp8266": "ESP32",
    "stm32": "STM32",
    "rp2040": "RP2040 / Raspberry Pi",
    "raspberry pi": "RP2040 / Raspberry Pi",
    "keyboard": "Keyboards",
    "synthesizer": "Synthesizers / audio",
    "eurorack": "Synthesizers / audio",
    "fpga": "RISC-V / FPGA",
    "risc-v": "RISC-V / FPGA",
    "cubesat": "CubeSat / aerospace",
    "arduino": "Arduino recreations",
    "sparkfun": "SparkFun boards",
}

# Red-flag description keywords — repos that are likely not real hardware
RED_FLAGS = {"tutorial", "template", "learning", "course", "lesson", "example project",
             "getting started", "hello world", "kicad library", "footprint library",
             "symbol library"}


def load_existing_repos() -> set:
    """Load owner/repo names already in repos.md (lowercase for dedup)."""
    repos = parse_repos_md(REPOS_MD)
    return {_repo_name_from_url(r["url"]).lower() for r in repos}


def _gh_api(endpoint, params=None):
    """Call GitHub API via ``gh api``. Returns parsed JSON.

    Sleeps RATE_LIMIT_DELAY after each call. On rate-limit 403, waits 60s
    and retries once.
    """
    cmd = ["gh", "api", endpoint]
    if params:
        for k, v in params.items():
            cmd.extend(["-f", f"{k}={v}"])

    for attempt in range(2):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT: {endpoint}", file=sys.stderr)
            return None

        if result.returncode != 0:
            stderr = result.stderr.strip().lower()
            if "rate limit" in stderr or "secondary rate limit" in stderr:
                if attempt == 0:
                    print("  Rate limited — waiting 60s...", file=sys.stderr)
                    time.sleep(60)
                    continue
            # Try to parse error JSON for message
            try:
                err = json.loads(result.stderr or result.stdout)
                msg = err.get("message", result.stderr.strip())
            except (json.JSONDecodeError, ValueError):
                msg = result.stderr.strip()
            print(f"  API error: {msg}", file=sys.stderr)
            return None

        time.sleep(RATE_LIMIT_DELAY)
        try:
            return json.loads(result.stdout)
        except (json.JSONDecodeError, ValueError):
            print(f"  JSON parse error for {endpoint}", file=sys.stderr)
            return None

    return None


def _search_paginated(query, endpoint="search/repositories", max_pages=10,
                      item_key="items"):
    """Paginate through GitHub search results. Returns all items."""
    all_items = []
    # Replace spaces with + for URL query encoding
    q = query.replace(" ", "+")
    for page in range(1, max_pages + 1):
        sep = "&" if "?" in endpoint else "?"
        url = f"{endpoint}{sep}q={q}&per_page=100&page={page}"
        data = _gh_api(url)
        if data is None:
            break
        items = data.get(item_key, data.get("items", []))
        if not items:
            break
        all_items.extend(items)
        total = data.get("total_count", 0)
        if len(all_items) >= total:
            break
    return all_items


def suggest_category(topics, description, name):
    """Assign a repos.md category from GitHub metadata.

    Priority: topic mapping > description keywords > default.
    """
    # Check topics first
    for topic in (topics or []):
        cat = TOPIC_CATEGORY_MAP.get(topic.lower())
        if cat:
            return cat

    # Check description and name keywords
    text = f"{description or ''} {name or ''}".lower()
    for keyword, cat in KEYWORD_CATEGORY_MAP.items():
        if keyword in text:
            return cat

    return MISC_CATEGORY


def _is_red_flag(description, name):
    """Check if description/name suggests a non-hardware repo."""
    text = f"{description or ''} {name or ''}".lower()
    return any(flag in text for flag in RED_FLAGS)


def _make_candidate(full_name, repo_data, source, has_kicad_files=True):
    """Build a candidate dict from GitHub API repo data."""
    owner, repo = full_name.split("/", 1)
    topics = repo_data.get("topics", [])
    description = repo_data.get("description") or ""
    return {
        "owner": owner,
        "repo": repo,
        "url": f"https://github.com/{full_name}",
        "description": description,
        "stars": repo_data.get("stargazers_count", 0),
        "topics": topics,
        "updated_at": repo_data.get("pushed_at", ""),
        "size_kb": repo_data.get("size", 0),
        "source": source,
        "has_kicad_files": has_kicad_files,
        "suggested_category": suggest_category(topics, description, repo),
    }


def search_code(existing):
    """Strategy A: Code search for extension:kicad_sch and extension:kicad_pcb.

    Date-sharded to bypass the 1,000-result limit per query.
    Returns candidate dicts for repos NOT in existing set.
    """
    print("=== Code search (extension:kicad_sch + kicad_pcb) ===")

    # Collect unique repo full_names from code search
    seen_repos = {}  # full_name_lower -> repo_data from code search
    total_results = 0

    for ext in ["kicad_sch", "kicad_pcb"]:
        for lo, hi in CODE_SEARCH_SHARDS:
            query = f"extension:{ext}+size:{lo}..{hi}"
            print(f"  {ext} size:{lo}..{hi}", end="", flush=True)

            items = _search_paginated(
                query, endpoint="search/code", max_pages=10, item_key="items",
            )
            shard_repos = set()
            for item in items:
                repo_obj = item.get("repository", {})
                fn = repo_obj.get("full_name", "")
                if fn:
                    fn_lower = fn.lower()
                    shard_repos.add(fn_lower)
                    if fn_lower not in seen_repos:
                        seen_repos[fn_lower] = {"full_name": fn, "repo_data": repo_obj}

            print(f" -> {len(items)} results, {len(shard_repos)} repos")
            total_results += len(items)

            if len(items) >= 1000:
                print(f"    WARNING: shard hit 1,000 cap — some repos may be missed")

    print(f"  Total code search results: {total_results}")
    print(f"  Unique repos found: {len(seen_repos)}")

    # Filter and build candidates
    candidates = []
    skipped_existing = 0
    skipped_filter = 0

    for fn_lower, info in seen_repos.items():
        if fn_lower in existing:
            skipped_existing += 1
            continue

        repo_data = info["repo_data"]
        full_name = info["full_name"]

        # Code search repo objects have limited fields — filter what we can
        if repo_data.get("fork", False):
            skipped_filter += 1
            continue

        if _is_red_flag(repo_data.get("description", ""), full_name):
            skipped_filter += 1
            continue

        candidates.append(_make_candidate(full_name, repo_data, "code",
                                          has_kicad_files=True))

    print(f"  Skipped (already in corpus): {skipped_existing}")
    print(f"  Skipped (filtered): {skipped_filter}")
    print(f"  New candidates: {len(candidates)}")
    return candidates


def search_topics(existing):
    """Strategy B: Topic search for topic:kicad fork:false.

    Date-sharded to bypass the 1,000-result limit. Returns candidate dicts
    for repos NOT in existing set.
    """
    print("\n=== Topic search (topic:kicad fork:false) ===")

    # Date shards for the main topic:kicad query (3,500+ repos)
    topic_shards = [
        "topic:kicad fork:false created:<2021-01-01",
        "topic:kicad fork:false created:2021-01-01..2022-01-01",
        "topic:kicad fork:false created:2022-01-01..2023-01-01",
        "topic:kicad fork:false created:2023-01-01..2024-01-01",
        "topic:kicad fork:false created:2024-01-01..2025-01-01",
        "topic:kicad fork:false created:>=2025-01-01",
        # Additional focused topics
        "topic:kicad-pcb fork:false",
    ]

    seen = set()
    candidates = []
    skipped_existing = 0
    skipped_filter = 0

    for query in topic_shards:
        print(f"  Query: {query}", end="", flush=True)
        items = _search_paginated(query, max_pages=10)
        print(f" -> {len(items)} results")

        for item in items:
            fn = item.get("full_name", "")
            fn_lower = fn.lower()
            if fn_lower in seen:
                continue
            seen.add(fn_lower)

            if fn_lower in existing:
                skipped_existing += 1
                continue

            if item.get("fork", False) or item.get("archived", False):
                skipped_filter += 1
                continue

            size_kb = item.get("size", 0)
            if size_kb < 10 or size_kb > 500_000:
                skipped_filter += 1
                continue

            if _is_red_flag(item.get("description", ""), fn):
                skipped_filter += 1
                continue

            candidates.append(_make_candidate(fn, item, "topic",
                                              has_kicad_files="unverified"))

    print(f"  Skipped (already in corpus): {skipped_existing}")
    print(f"  Skipped (filtered): {skipped_filter}")
    print(f"  New candidates: {len(candidates)}")
    return candidates


def search_keywords(existing):
    """Strategy C: Keyword search for 'kicad pcb fork:false'.

    Broader sweep with stricter filtering. Returns candidate dicts.
    """
    print("\n=== Keyword search (kicad pcb fork:false) ===")

    queries = [
        "kicad pcb fork:false",
        "kicad schematic fork:false",
        "kicad hardware fork:false",
    ]

    seen = set()
    candidates = []
    skipped_existing = 0
    skipped_filter = 0

    for query in queries:
        print(f"  Query: {query}", end="", flush=True)
        items = _search_paginated(query, max_pages=10)
        print(f" -> {len(items)} results")

        for item in items:
            fn = item.get("full_name", "")
            fn_lower = fn.lower()
            if fn_lower in seen:
                continue
            seen.add(fn_lower)

            if fn_lower in existing:
                skipped_existing += 1
                continue

            if item.get("fork", False) or item.get("archived", False):
                skipped_filter += 1
                continue

            size_kb = item.get("size", 0)
            if size_kb < 10 or size_kb > 500_000:
                skipped_filter += 1
                continue

            if _is_red_flag(item.get("description", ""), fn):
                skipped_filter += 1
                continue

            candidates.append(_make_candidate(fn, item, "keyword",
                                              has_kicad_files="unverified"))

    print(f"  Skipped (already in corpus): {skipped_existing}")
    print(f"  Skipped (filtered): {skipped_filter}")
    print(f"  New candidates: {len(candidates)}")
    return candidates


def deduplicate(candidates):
    """Merge candidates from multiple strategies, keeping best metadata.

    Deduplicates by owner/repo (case-insensitive). Merges source tags
    (e.g., 'code+topic' if found by both). Prefers code search data
    (has_kicad_files=True) over topic/keyword.
    """
    by_name = {}
    for c in candidates:
        key = f"{c['owner']}/{c['repo']}".lower()
        if key in by_name:
            existing = by_name[key]
            # Merge source tags
            sources = set(existing["source"].split("+"))
            sources.add(c["source"])
            existing["source"] = "+".join(sorted(sources))
            # Prefer code search confirmation
            if c["has_kicad_files"] is True:
                existing["has_kicad_files"] = True
            # Keep higher star count (in case of data freshness difference)
            if c["stars"] > existing["stars"]:
                existing["stars"] = c["stars"]
                existing["description"] = c["description"]
                existing["topics"] = c["topics"]
                existing["updated_at"] = c["updated_at"]
                existing["suggested_category"] = c["suggested_category"]
        else:
            by_name[key] = c.copy()

    return list(by_name.values())


###############################################################################
# Multi-platform search (GitLab, Codeberg, Bitbucket)
###############################################################################

def _http_get_json(url, headers=None, timeout=30):
    """GET a URL and return parsed JSON. Returns None on error."""
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError,
            TimeoutError, OSError) as e:
        print(f"  HTTP error: {e}", file=sys.stderr)
        return None


def search_gitlab(existing):
    """Search GitLab.com public API for KiCad repos.

    GitLab API: /api/v4/projects?search=kicad&visibility=public
    No auth required. Rate limit: 300 req/min unauthenticated.
    Paginated up to 100 per page, but GitLab caps at 10,000 results.
    """
    print("\n=== GitLab search ===")

    queries = ["kicad", "kicad pcb", "kicad schematic"]
    seen = set()
    candidates = []
    skipped_existing = 0
    skipped_filter = 0

    for search_term in queries:
        print(f"  Query: {search_term}", end="", flush=True)
        page_count = 0
        for page in range(1, 21):  # up to 2,000 results per query
            encoded = urllib.parse.quote(search_term)
            url = (f"https://gitlab.com/api/v4/projects"
                   f"?search={encoded}&visibility=public"
                   f"&per_page=100&page={page}"
                   f"&order_by=star_count&sort=desc")
            data = _http_get_json(url)
            if data is None or not data:
                break
            page_count += len(data)

            for item in data:
                path = item.get("path_with_namespace", "")
                path_lower = path.lower()
                if path_lower in seen:
                    continue
                seen.add(path_lower)

                if path_lower in existing:
                    skipped_existing += 1
                    continue

                if item.get("forked_from_project"):
                    skipped_filter += 1
                    continue

                if item.get("archived", False):
                    skipped_filter += 1
                    continue

                desc = item.get("description") or ""
                if _is_red_flag(desc, path):
                    skipped_filter += 1
                    continue

                owner, repo = path.split("/", 1) if "/" in path else (path, path)
                topics = item.get("topics", []) or item.get("tag_list", [])
                candidates.append({
                    "owner": owner,
                    "repo": repo,
                    "url": item.get("web_url", f"https://gitlab.com/{path}"),
                    "description": desc,
                    "stars": item.get("star_count", 0),
                    "topics": topics,
                    "updated_at": item.get("last_activity_at", ""),
                    "size_kb": 0,
                    "source": "gitlab",
                    "has_kicad_files": "unverified",
                    "suggested_category": suggest_category(topics, desc, repo),
                })

            time.sleep(0.3)  # gentle rate limiting

        print(f" -> {page_count} results")

    print(f"  Skipped (already in corpus): {skipped_existing}")
    print(f"  Skipped (filtered): {skipped_filter}")
    print(f"  New candidates: {len(candidates)}")
    return candidates


def search_codeberg(existing):
    """Search Codeberg (Gitea-based) API for KiCad repos.

    Codeberg API: /api/v1/repos/search?q=kicad&limit=50
    No auth required.
    """
    print("\n=== Codeberg search ===")

    queries = ["kicad", "kicad pcb"]
    seen = set()
    candidates = []
    skipped_existing = 0
    skipped_filter = 0

    for search_term in queries:
        print(f"  Query: {search_term}", end="", flush=True)
        page_count = 0
        for page in range(1, 21):  # up to 1,000 results
            encoded = urllib.parse.quote(search_term)
            url = (f"https://codeberg.org/api/v1/repos/search"
                   f"?q={encoded}&limit=50&page={page}"
                   f"&sort=stars&order=desc")
            data = _http_get_json(url)
            if data is None:
                break
            items = data.get("data", data) if isinstance(data, dict) else data
            if not items:
                break
            page_count += len(items)

            for item in items:
                fn = item.get("full_name", "")
                fn_lower = fn.lower()
                if fn_lower in seen:
                    continue
                seen.add(fn_lower)

                if fn_lower in existing:
                    skipped_existing += 1
                    continue

                if item.get("fork", False) or item.get("archived", False):
                    skipped_filter += 1
                    continue

                desc = item.get("description") or ""
                if _is_red_flag(desc, fn):
                    skipped_filter += 1
                    continue

                owner = item.get("owner", {}).get("login", fn.split("/")[0] if "/" in fn else fn)
                repo = item.get("name", fn.split("/")[-1] if "/" in fn else fn)
                topics = item.get("topics", []) or []
                html_url = item.get("html_url", f"https://codeberg.org/{fn}")
                candidates.append({
                    "owner": owner,
                    "repo": repo,
                    "url": html_url,
                    "description": desc,
                    "stars": item.get("stars_count", 0),
                    "topics": topics,
                    "updated_at": item.get("updated_at", ""),
                    "size_kb": item.get("size", 0),
                    "source": "codeberg",
                    "has_kicad_files": "unverified",
                    "suggested_category": suggest_category(topics, desc, repo),
                })

            time.sleep(0.5)

        print(f" -> {page_count} results")

    print(f"  Skipped (already in corpus): {skipped_existing}")
    print(f"  Skipped (filtered): {skipped_filter}")
    print(f"  New candidates: {len(candidates)}")
    return candidates


def search_bitbucket(existing):
    """Search Bitbucket Cloud API for KiCad repos.

    NOTE: Bitbucket's repository search API requires authentication for
    filtered queries. Without app credentials, this returns no results.
    Bitbucket has very few KiCad hardware repos — low priority.
    """
    print("\n=== Bitbucket search ===")
    print("  NOTE: Bitbucket search requires app credentials (not configured)")
    print("  Skipping — very few KiCad repos on Bitbucket")
    return []


def print_summary(candidates):
    """Print category distribution and stats."""
    print(f"\n{'='*60}")
    print(f"CANDIDATES SUMMARY")
    print(f"{'='*60}")
    print(f"Total candidates: {len(candidates)}")

    # Source breakdown
    source_counts = {}
    for c in candidates:
        for s in c["source"].split("+"):
            source_counts[s] = source_counts.get(s, 0) + 1
    print(f"\nBy source:")
    for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  {src:12s} {count}")

    # Confirmed vs unverified
    confirmed = sum(1 for c in candidates if c["has_kicad_files"] is True)
    unverified = len(candidates) - confirmed
    print(f"\nKiCad files confirmed (code search): {confirmed}")
    print(f"KiCad files unverified (topic/keyword): {unverified}")

    # Category breakdown
    cat_counts = {}
    for c in candidates:
        cat = c["suggested_category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    print(f"\nBy category:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat:40s} {count}")

    # Stars distribution
    stars = sorted([c["stars"] for c in candidates], reverse=True)
    if stars:
        print(f"\nStars: max={stars[0]}, median={stars[len(stars)//2]}, "
              f"mean={sum(stars)/len(stars):.0f}")
        top10 = [c for c in candidates if c["stars"] >= 10]
        print(f"Repos with 10+ stars: {len(top10)}")


def main():
    parser = argparse.ArgumentParser(
        description="Discover KiCad repos on GitHub, GitLab, Codeberg, Bitbucket")
    strategy = parser.add_mutually_exclusive_group()
    strategy.add_argument("--strategy", choices=["code", "topic", "keyword"],
                          help="Run a single GitHub search strategy")
    strategy.add_argument("--all", action="store_true",
                          help="Run all three GitHub strategies (code, topic, keyword)")
    parser.add_argument("--source", choices=["github", "gitlab", "codeberg",
                                             "bitbucket", "all"],
                        help="Search a specific platform (or all platforms)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit output to top N candidates (by stars)")
    parser.add_argument("--json", action="store_true",
                        help="Print full JSON to stdout")
    args = parser.parse_args()

    # Determine what to run
    run_github = (args.all or args.strategy
                  or args.source in ("github", "all")
                  or not args.source)
    run_gitlab = args.source in ("gitlab", "all")
    run_codeberg = args.source in ("codeberg", "all")
    run_bitbucket = args.source in ("bitbucket", "all")

    if not (args.strategy or args.all or args.source):
        parser.print_help()
        sys.exit(1)

    # Load existing repos for dedup
    existing = load_existing_repos()
    print(f"Loaded {len(existing)} existing repos from repos.md\n")

    # Run selected strategies — each deduplicates against repos.md only.
    # Cross-strategy dedup happens in deduplicate() at the end.
    all_candidates = []

    if run_github:
        if args.all or args.strategy == "code" or args.source in ("github", "all"):
            all_candidates.extend(search_code(existing))
        if args.all or args.strategy == "topic" or args.source in ("github", "all"):
            all_candidates.extend(search_topics(existing))
        if args.all or args.strategy == "keyword" or args.source in ("github", "all"):
            all_candidates.extend(search_keywords(existing))

    if run_gitlab:
        all_candidates.extend(search_gitlab(existing))

    if run_codeberg:
        all_candidates.extend(search_codeberg(existing))

    if run_bitbucket:
        all_candidates.extend(search_bitbucket(existing))

    # Deduplicate across strategies
    candidates = deduplicate(all_candidates)

    # Sort by stars descending
    candidates.sort(key=lambda c: (-c["stars"], c["owner"].lower(), c["repo"].lower()))

    # Apply limit
    if args.limit and args.limit < len(candidates):
        candidates = candidates[:args.limit]

    print_summary(candidates)

    # Write output
    CANDIDATES_FILE.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATES_FILE.write_text(json.dumps(candidates, indent=2) + "\n")
    print(f"\nWrote {len(candidates)} candidates to {CANDIDATES_FILE}")

    if args.json:
        json.dump(candidates, sys.stdout, indent=2)
        print()


if __name__ == "__main__":
    main()
