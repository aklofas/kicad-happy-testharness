#!/usr/bin/env python3
"""Bulk-download datasheets from schematic-embedded URLs.

Extracts datasheet URLs from pre-computed analyzer JSON outputs and
downloads them in parallel. No API keys required — uses the URLs that
KiCad component libraries already provide.

For parts without embedded URLs, use run/run_datasheets.py which
searches the DigiKey API.

Usage:
    python3 tools/bulk_download_datasheets.py                    # Full corpus
    python3 tools/bulk_download_datasheets.py --jobs 64          # 64 parallel
    python3 tools/bulk_download_datasheets.py --repo owner/repo  # Single repo
    python3 tools/bulk_download_datasheets.py --dry-run          # Preview only
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import HARNESS_DIR, OUTPUTS_DIR, REPOS_DIR


def sanitize_filename(mpn, ext=".pdf"):
    """Create a safe filename from an MPN."""
    name = re.sub(r'[^\w\-.]', '_', mpn.strip())[:80]
    return name + ext


def collect_urls(repo_filter=None):
    """Collect unique (url, mpn, repo) tuples from schematic outputs."""
    schematic_dir = OUTPUTS_DIR / "schematic"
    if not schematic_dir.exists():
        return []

    seen_urls = {}  # url -> (mpn, repo)
    entries = []

    for owner_dir in sorted(schematic_dir.iterdir()):
        if not owner_dir.is_dir():
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir():
                continue
            repo_name = f"{owner_dir.name}/{repo_dir.name}"
            if repo_filter and repo_name != repo_filter:
                continue

            for json_file in repo_dir.glob("*.json"):
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                except Exception:
                    continue

                for item in data.get("bom", []):
                    url = item.get("datasheet", "").strip()
                    mpn = item.get("mpn", "").strip()
                    if not url or url == "~" or "://" not in url:
                        continue
                    if not mpn:
                        continue
                    if url not in seen_urls:
                        seen_urls[url] = (mpn, repo_name)
                        entries.append({
                            "url": url,
                            "mpn": mpn,
                            "repo": repo_name,
                        })

    return entries


def download_one(entry, datasheets_dir, timeout=30):
    """Download a single datasheet. Returns (mpn, success, size_or_error)."""
    url = entry["url"]
    mpn = entry["mpn"]
    filename = sanitize_filename(mpn)
    output_path = datasheets_dir / filename

    if output_path.exists() and output_path.stat().st_size > 1000:
        return mpn, "skip", output_path.stat().st_size

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (kicad-happy datasheet downloader)",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()

        # Basic PDF validation
        if not data[:5] == b"%PDF-":
            return mpn, "not_pdf", len(data)

        output_path.write_bytes(data)
        return mpn, "ok", len(data)

    except urllib.error.HTTPError as e:
        return mpn, f"http_{e.code}", str(e)
    except Exception as e:
        return mpn, "error", str(e)[:100]


def main():
    parser = argparse.ArgumentParser(
        description="Bulk-download datasheets from schematic-embedded URLs")
    parser.add_argument("--repo", help="Only process this repo (owner/name)")
    parser.add_argument("--jobs", "-j", type=int, default=64,
                        help="Parallel download workers (default: 64)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be downloaded")
    parser.add_argument("--output", "-o", type=Path,
                        default=HARNESS_DIR / "datasheets",
                        help="Output directory for PDFs")
    args = parser.parse_args()

    print("Collecting URLs from schematic outputs...")
    entries = collect_urls(repo_filter=args.repo)
    print(f"Found {len(entries)} unique datasheet URLs")

    if not entries:
        print("No URLs to download.")
        return

    args.output.mkdir(parents=True, exist_ok=True)

    # Check what's already downloaded
    existing = set(f.stem for f in args.output.glob("*.pdf")
                   if f.stat().st_size > 1000)
    to_download = [e for e in entries
                   if sanitize_filename(e["mpn"], "")[:-0] not in existing]

    if args.dry_run:
        print(f"Would download: {len(to_download)} PDFs")
        print(f"Already have: {len(entries) - len(to_download)}")
        for e in to_download[:20]:
            print(f"  {e['mpn']}: {e['url'][:80]}")
        if len(to_download) > 20:
            print(f"  ... and {len(to_download) - 20} more")
        return

    print(f"Downloading {len(entries)} URLs with {args.jobs} workers...")
    ok = skip = fail = not_pdf = 0
    total_bytes = 0

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {
            pool.submit(download_one, e, args.output): e
            for e in entries
        }
        for i, future in enumerate(as_completed(futures), 1):
            mpn, status, detail = future.result()
            if status == "ok":
                ok += 1
                total_bytes += detail
            elif status == "skip":
                skip += 1
            elif status == "not_pdf":
                not_pdf += 1
            else:
                fail += 1

            if i % 100 == 0 or i == len(entries):
                print(f"  [{i}/{len(entries)}] ok={ok} skip={skip} "
                      f"fail={fail} not_pdf={not_pdf} "
                      f"({total_bytes/1024/1024:.1f} MB)")

    print()
    print("=" * 60)
    print(f"Downloaded: {ok} PDFs ({total_bytes/1024/1024:.1f} MB)")
    print(f"Skipped (already had): {skip}")
    print(f"Not PDF: {not_pdf}")
    print(f"Failed: {fail}")
    print(f"Total unique URLs: {len(entries)}")


if __name__ == "__main__":
    main()
