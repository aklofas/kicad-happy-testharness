#!/usr/bin/env python3
"""Download datasheets and validate existing extractions across test repos.

This script handles the deterministic parts of the datasheet pipeline:
  1. Download PDFs via sync_datasheets_digikey.py (requires DigiKey API credentials)
  2. Register downloaded PDFs into datasheet_db as a side effect (sub-project A
     integration) — new records for novel SHAs, merged found_in for dupes
  3. Validate/score existing extractions cached in datasheets/extracted/

The actual PDF→JSON extraction step is NOT automated here — it happens
interactively when a user runs the kicad skill in a Claude Code session.

Usage:
    python3 run/run_datasheets.py                          # Full: download + validate
    python3 run/run_datasheets.py --repo owner/OpenMower    # Single repo
    python3 run/run_datasheets.py --cross-section smoke     # Named cross-section
    python3 run/run_datasheets.py --download-only           # Just download PDFs
    python3 run/run_datasheets.py --validate-only           # Just score existing extractions
    python3 run/run_datasheets.py --dry-run                 # Preview without downloading
    python3 run/run_datasheets.py --jobs 16                 # Parallel processing

Prerequisites:
    1. Schematic outputs in results/outputs/schematic/ (run run_schematic.py first)
    2. For downloads: DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET env vars
    3. kicad-happy repo with datasheet extraction infrastructure

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (required if not at ../kicad-happy)
"""

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (
    DEFAULT_JOBS, OUTPUTS_DIR, REPOS_DIR, add_repo_filter_args,
    resolve_kicad_happy_dir, resolve_repos,
)

# Resolve kicad-happy once at module level
_kicad_happy = resolve_kicad_happy_dir()
_kicad_scripts = _kicad_happy / "skills" / "kicad" / "scripts"
sys.path.insert(0, str(_kicad_scripts))


def find_repos_with_schematics():
    """Find repos that have schematic analysis outputs."""
    schematic_dir = OUTPUTS_DIR / "schematic"
    if not schematic_dir.exists():
        return []

    repos = []
    for owner_dir in sorted(schematic_dir.iterdir()):
        if not owner_dir.is_dir():
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir():
                continue
            if any(repo_dir.glob("*.json")):
                repos.append(f"{owner_dir.name}/{repo_dir.name}")
    return repos


def download_datasheets(repo_name, sync_script, dry_run=False, delay=0.3,
                        parallel=4):
    """Download datasheets for a repo using sync_datasheets_digikey.py.

    Processes all .kicad_sch files in the repo (not just the first one),
    sharing a single datasheets/ output directory so parts are deduplicated.

    Returns (downloaded_count, failed_count, total_parts) or None on error.
    """
    repo_dir = REPOS_DIR / repo_name
    if not repo_dir.exists():
        return None

    # Prefer pre-computed analyzer JSON outputs (fast, no re-analysis)
    analyzer_dir = OUTPUTS_DIR / "schematic" / repo_name
    json_files = sorted(analyzer_dir.glob("*.json")) if analyzer_dir.exists() else []

    # Fall back to .kicad_sch files if no pre-computed outputs
    if not json_files:
        schematics = sorted(repo_dir.rglob("*.kicad_sch"),
                            key=lambda p: len(p.parts))
        if not schematics:
            return None
        json_files = schematics

    total_downloaded = 0
    total_failed = 0

    # Use a shared output dir so the index.json deduplicates across schematics
    out_dir = repo_dir / "datasheets"

    for input_file in json_files:
        cmd = [sys.executable, str(sync_script), str(input_file),
               "--output", str(out_dir),
               "--delay", str(delay),
               "--parallel", str(parallel)]
        if dry_run:
            cmd.append("--dry-run")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            for line in result.stdout.split("\n"):
                if "Downloaded" in line and "bytes" in line:
                    total_downloaded += 1
                if "Failed:" in line:
                    try:
                        total_failed += int(
                            line.strip().split("Failed:")[1].strip().split()[0])
                    except (ValueError, IndexError):
                        pass
        except (subprocess.TimeoutExpired, Exception):
            continue

    return total_downloaded, total_failed, 0


def validate_extractions(repo_dir):
    """Validate existing extractions for a repo.

    Returns a report dict with scores, staleness, and coverage info.
    """
    from datasheet_extract_cache import (
        get_cached_extraction, is_extraction_stale, list_extractions,
    )
    from datasheet_score import score_extraction

    datasheets_dir = repo_dir / "datasheets"
    extract_dir = datasheets_dir / "extracted"
    index_path = datasheets_dir / "index.json"

    report = {
        "repo": repo_dir.name,
        "total_parts": 0,
        "downloaded": 0,
        "download_failed": 0,
        "extracted": 0,
        "stale": 0,
        "avg_score": 0.0,
        "sufficient": 0,
        "by_category": {},
        "missing_extractions": [],
        "parts": {},
    }

    # Read index once
    index_parts = {}
    if index_path.exists():
        with open(index_path) as f:
            index_parts = json.load(f).get("parts", {})
        report["total_parts"] = len(index_parts)
        report["downloaded"] = sum(1 for p in index_parts.values() if p.get("status") == "ok")
        report["download_failed"] = sum(1 for p in index_parts.values() if p.get("status") == "failed")

    # Score extractions
    if extract_dir.exists():
        extractions = list_extractions(extract_dir)
        report["extracted"] = len(extractions)

        scores = []
        for item in extractions:
            mpn = item["mpn"]
            ext = get_cached_extraction(extract_dir, mpn)
            if not ext:
                continue

            score = score_extraction(ext, expected_pin_count=item.get("pin_count"))
            scores.append(score["total"])

            stale, reason = is_extraction_stale(
                extract_dir, mpn, datasheets_dir=str(datasheets_dir)
            )
            if stale:
                report["stale"] += 1

            cat = ext.get("category", "unknown")
            report["by_category"][cat] = report["by_category"].get(cat, 0) + 1

            if score["sufficient"]:
                report["sufficient"] += 1

            report["parts"][mpn] = {
                "score": round(score["total"], 1),
                "stale": stale,
                "stale_reason": reason if stale else None,
                "category": cat,
                "sufficient": score["sufficient"],
            }

        if scores:
            report["avg_score"] = round(sum(scores) / len(scores), 1)

    # Parts with downloads but no extraction
    for mpn, entry in index_parts.items():
        if entry.get("status") == "ok" and mpn not in report["parts"]:
            report["missing_extractions"].append(mpn)

    return report


def _register_repo_pdfs_in_datasheet_db(repo_name, repo_dir):
    """Register newly-downloaded PDFs from repo_dir/datasheets/ into datasheet_db
    as a side effect of the download phase.

    Walks the repo's `datasheets/` subdirectory, computes SHA256 for each PDF,
    and either creates a new datasheet_db record (with `found_in` pointing at
    the repo path) or merges into an existing record with dedup. The primary
    MPN is inferred from the filename stem.

    Errors are swallowed because this is opportunistic — the main run_datasheets
    flow (download + validate) owns the tool's core purpose, and datasheet_db
    ingestion is bonus bookkeeping.

    Returns (ingested, merged) counts, or (0, 0) on any setup failure.
    """
    try:
        from datetime import datetime, timezone
        from validate.datasheet_db.storage import (
            compute_sha256, write_blob_atomic, store_path
        )
        from validate.datasheet_db.manifest import (
            load_record, save_record, merge_record
        )
    except ImportError:
        return 0, 0

    datasheets_dir = repo_dir / "datasheets"
    if not datasheets_dir.exists():
        return 0, 0

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ingested = merged_count = 0

    for pdf in datasheets_dir.rglob("*.pdf"):
        try:
            size = pdf.stat().st_size
            if size == 0:
                continue  # skip 0-byte broken downloads
            sha = compute_sha256(pdf)
            data = pdf.read_bytes()
        except OSError:
            continue

        try:
            rel = pdf.relative_to(datasheets_dir)
            found_in_entry = {
                "type": "repo",
                "ref": repo_name,
                "path": f"datasheets/{rel}",
                "first_seen": now,
            }
        except ValueError:
            continue

        try:
            existing = load_record(sha)
        except Exception:
            continue

        if existing is not None:
            try:
                merged_rec = merge_record(
                    existing, {"found_in": [found_in_entry]}, now=now
                )
                save_record(merged_rec)
                merged_count += 1
            except Exception:
                pass  # side effect; ignore errors
            continue

        # New record — derive primary MPN from filename stem
        record_skel = {
            "sha256": sha,
            "size_bytes": size,
            "page_count": None,
            "mpns": [{"mpn": pdf.stem, "primary": True}],
            "manufacturers": [],
            "source_urls": [],
            "filename_aliases": [pdf.name],
            "found_in": [found_in_entry],
            "revision_label": None,
            "first_seen": now,
            "last_seen": now,
            "verified": False,
            "verification_notes": None,
        }
        try:
            write_blob_atomic(store_path(record_skel), data, expected_sha256=sha)
            save_record(record_skel)
            ingested += 1
        except Exception:
            pass  # side effect; ignore errors

    return ingested, merged_count


def process_repo(repo_name, sync_script, ds_out_dir, download_only=False,
                 validate_only=False, dry_run=False, delay=0.3, parallel=4):
    """Process a single repo: download + validate.

    Returns a dict with per-repo results, or None if repo dir missing.
    """
    repo_dir = REPOS_DIR / repo_name
    if not repo_dir.exists():
        return None

    result = {
        "repo": repo_name,
        "downloaded": 0,
        "download_failed": 0,
        "db_ingested": 0,
        "db_merged": 0,
        "report": None,
    }

    if not validate_only:
        dl = download_datasheets(repo_name, sync_script, dry_run,
                                 delay=delay, parallel=parallel)
        if dl:
            result["downloaded"] = dl[0]
            result["download_failed"] = dl[1]
        # Opportunistically register downloaded PDFs into datasheet_db.
        # Errors are swallowed — the main download flow is authoritative.
        if not dry_run:
            try:
                ingested, merged_count = _register_repo_pdfs_in_datasheet_db(
                    repo_name, repo_dir
                )
                result["db_ingested"] = ingested
                result["db_merged"] = merged_count
            except Exception:
                pass

    if not download_only:
        report = validate_extractions(repo_dir)
        if report:
            result["report"] = report
            repo_out = ds_out_dir / repo_name
            repo_out.mkdir(parents=True, exist_ok=True)
            with open(repo_out / "_report.json", "w") as f:
                json.dump(report, f, indent=2)
                f.write("\n")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Download datasheets and validate extractions"
    )
    add_repo_filter_args(parser)
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel jobs (default: {DEFAULT_JOBS})")
    parser.add_argument("--download-only", action="store_true",
                        help="Only download PDFs, skip validation")
    parser.add_argument("--validate-only", action="store_true",
                        help="Only validate existing extractions")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be downloaded")
    parser.add_argument("--delay", type=float, default=0.3,
                        help="Seconds between DigiKey API calls per repo (default: 0.3)")
    parser.add_argument("--parallel", type=int, default=4,
                        help="Download workers within each repo (default: 4)")
    args = parser.parse_args()

    sync_script = _kicad_happy / "skills" / "digikey" / "scripts" / "sync_datasheets_digikey.py"

    if not args.validate_only and not sync_script.exists():
        print(f"Error: {sync_script} not found", file=sys.stderr)
        sys.exit(1)

    if not args.validate_only and not args.dry_run:
        if not os.environ.get("DIGIKEY_CLIENT_ID"):
            print("Warning: DIGIKEY_CLIENT_ID not set — downloads may fail",
                  file=sys.stderr)

    repo_list = resolve_repos(args)
    repos = repo_list if repo_list else find_repos_with_schematics()

    if not repos:
        print("No repos with schematic outputs found. Run run_schematic.py first.",
              file=sys.stderr)
        sys.exit(1)

    print(f"=== Datasheet Pipeline ===")
    print(f"Repos: {len(repos)}")
    if args.jobs > 1:
        print(f"Jobs: {args.jobs}")
    if not args.validate_only:
        print(f"Mode: {'dry-run' if args.dry_run else 'download'} + validate")
    else:
        print(f"Mode: validate-only")
    print()

    ds_out_dir = OUTPUTS_DIR / "datasheets"

    total_downloaded = 0
    total_failed = 0
    total_extracted = 0
    total_stale = 0
    total_sufficient = 0
    total_parts = 0
    total_db_ingested = 0
    total_db_merged = 0
    repos_processed = 0
    all_categories = Counter()

    def _collect(result):
        """Accumulate a single repo result into totals. Returns log line or None."""
        if result is None:
            return None

        nonlocal total_downloaded, total_failed, total_extracted
        nonlocal total_stale, total_sufficient, total_parts, repos_processed
        nonlocal total_db_ingested, total_db_merged

        repos_processed += 1
        total_downloaded += result["downloaded"]
        total_failed += result["download_failed"]
        total_db_ingested += result.get("db_ingested", 0)
        total_db_merged += result.get("db_merged", 0)

        report = result["report"]
        if report:
            total_parts += report["total_parts"]
            total_extracted += report["extracted"]
            total_stale += report["stale"]
            total_sufficient += report["sufficient"]
            all_categories.update(report["by_category"])

            if report["extracted"] > 0:
                return (f"  {result['repo']}: {report['extracted']} extracted "
                        f"(avg {report['avg_score']:.1f}), "
                        f"{report['stale']} stale, "
                        f"{len(report['missing_extractions'])} unextracted")
        return None

    if args.jobs <= 1:
        for repo_name in repos:
            result = process_repo(repo_name, sync_script, ds_out_dir,
                                  args.download_only, args.validate_only,
                                  args.dry_run, args.delay, args.parallel)
            line = _collect(result)
            if line:
                print(line)
    else:
        # I/O-bound: HTTP downloads + subprocess calls — threads are ideal
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {
                pool.submit(process_repo, repo_name, sync_script, ds_out_dir,
                            args.download_only, args.validate_only,
                            args.dry_run, args.delay, args.parallel): repo_name
                for repo_name in repos
            }
            for future in as_completed(futures):
                result = future.result()
                line = _collect(result)
                if line:
                    print(line)

    aggregate = {
        "repos_processed": repos_processed,
        "total_parts": total_parts,
        "total_downloaded": total_downloaded,
        "total_failed": total_failed,
        "total_db_ingested": total_db_ingested,
        "total_db_merged": total_db_merged,
        "total_extracted": total_extracted,
        "total_stale": total_stale,
        "total_sufficient": total_sufficient,
        "by_category": dict(all_categories),
    }
    ds_out_dir.mkdir(parents=True, exist_ok=True)
    with open(ds_out_dir / "_aggregate.json", "w") as f:
        json.dump(aggregate, f, indent=2)
        f.write("\n")

    print()
    print("=" * 60)
    print("Datasheet Pipeline Summary")
    print("=" * 60)
    print(f"Repos processed:        {repos_processed}")
    if not args.validate_only:
        print(f"PDFs downloaded:        {total_downloaded}")
        print(f"Download failures:      {total_failed}")
        print(f"datasheet_db ingested:  {total_db_ingested} (new records)")
        print(f"datasheet_db merged:    {total_db_merged} (dedup hits)")
    if not args.download_only:
        print(f"Total parts:            {total_parts}")
        print(f"Extracted:              {total_extracted}")
        print(f"Sufficient (>= 6.0):   {total_sufficient}")
        print(f"Stale:                  {total_stale}")
        if all_categories:
            print(f"By category:")
            for cat, count in sorted(all_categories.items(), key=lambda x: -x[1]):
                print(f"  {cat:30s}: {count}")


if __name__ == "__main__":
    main()
