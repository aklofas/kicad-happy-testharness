"""argparse CLI dispatch for all datasheet_db subcommands."""

import argparse
import sys


def cmd_stats(args) -> int:
    from validate.datasheet_db.manifest import iter_records
    records = list(iter_records())
    total = len(records)
    if total == 0:
        print("Total: 0 records")
        return 0
    verified = sum(1 for r in records if r.get("verified"))
    with_url = sum(1 for r in records if r.get("source_urls"))
    from collections import Counter
    mfrs = Counter()
    for r in records:
        for m in r.get("manufacturers", []) or []:
            mfrs[m] += 1
    print(f"Total: {total} records")
    print(f"Verified: {verified}")
    print(f"With source URL: {with_url}")
    print("Top manufacturers:")
    for mfr, count in mfrs.most_common(20):
        print(f"  {mfr}: {count}")
    return 0


def cmd_insert(args) -> int:
    from datetime import datetime, timezone
    from pathlib import Path
    from validate.datasheet_db.storage import (
        compute_sha256, write_blob_atomic, store_path, BlobSha256Mismatch
    )
    from validate.datasheet_db.manifest import (
        load_record, save_record, merge_record
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2
        # Check first bytes for PDF magic
        with open(path, "rb") as f:
            head = f.read(8)
        if not head.startswith(b"%PDF-"):
            print(f"ERROR: {path} is not a PDF (magic: {head!r})", file=sys.stderr)
            return 1
        sha = compute_sha256(path)
        size = path.stat().st_size
        data = path.read_bytes()
    elif args.url:
        from validate.datasheet_db.fetcher import fetch_bytes, FetchError
        try:
            result = fetch_bytes(args.url)
        except FetchError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
        sha = result.sha256
        size = result.size_bytes
        data = result.body
    else:
        print("ERROR: --mpn-only insert requires a downloader chain; not yet implemented", file=sys.stderr)
        return 3

    # Build a record skeleton from args
    primary_mpn = args.mpn or Path(args.file or "unknown.pdf").stem
    record_skel = {
        "sha256": sha,
        "size_bytes": size,
        "page_count": None,
        "mpns": [{"mpn": primary_mpn, "primary": True}],
        "manufacturers": [args.manufacturer] if args.manufacturer else [],
        "source_urls": [],
        "filename_aliases": [Path(args.file).name] if args.file else [],
        "found_in": [],
        "revision_label": None,
        "first_seen": now,
        "last_seen": now,
        "verified": False,
        "verification_notes": None,
    }
    if args.url:
        from validate.datasheet_db.fetcher import sanitize_url
        record_skel["source_urls"] = [{
            "url": sanitize_url(args.url),
            "first_seen_at": now,
            "last_verified_at": now,
            "status": "live",
        }]

    existing = load_record(sha)
    if existing is not None:
        merged = merge_record(existing, record_skel, now=now)
        save_record(merged)
        print(f"merged {sha}")
        return 0

    # New record — write blob then save
    try:
        write_blob_atomic(store_path(record_skel), data, expected_sha256=sha)
    except BlobSha256Mismatch as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    save_record(record_skel)
    print(f"new {sha}")
    return 0


def cmd_find(args) -> int:
    from validate.datasheet_db.manifest import (
        find_by_mpn, find_by_sha256_prefix, find_by_url
    )
    from validate.datasheet_db.storage import store_path

    if args.sha256:
        matches = find_by_sha256_prefix(args.sha256)
    elif args.url:
        matches = find_by_url(args.url)
    else:
        matches = find_by_mpn(args.query)

    if not matches:
        return 1

    if args.json:
        import json
        print(json.dumps(matches, indent=2))
        return 0

    for rec in matches:
        print(str(store_path(rec)))
    return 0


def cmd_verify(args) -> int:
    from validate.datasheet_db.manifest import iter_records
    from validate.datasheet_db.storage import store_path, compute_sha256
    scanned = matched = mismatched = missing_blob = 0
    for rec in iter_records():
        scanned += 1
        path = store_path(rec)
        if not path.exists():
            missing_blob += 1
            continue
        if args.fast:
            matched += 1
            continue
        actual = compute_sha256(path)
        if actual == rec["sha256"]:
            matched += 1
        else:
            mismatched += 1
            print(f"MISMATCH: {path} (expected {rec['sha256'][:12]}, got {actual[:12]})")
    print(f"Scanned: {scanned}")
    print(f"Matched: {matched}")
    print(f"Mismatched: {mismatched}")
    print(f"Missing blob: {missing_blob}")
    return 1 if mismatched > 0 else 0


def cmd_list(args) -> int:
    from validate.datasheet_db.manifest import iter_records
    from validate.datasheet_db.storage import store_path

    records = list(iter_records())

    # Filters
    if args.manufacturer:
        records = [r for r in records
                   if args.manufacturer in (r.get("manufacturers") or [])]
    if args.unverified:
        records = [r for r in records if not r.get("verified")]
    if args.missing:
        records = [r for r in records if not store_path(r).exists()]

    if args.format == "json":
        import json
        print(json.dumps(records, indent=2))
        return 0

    if args.format == "tsv":
        for rec in records:
            primary = next((m["mpn"] for m in rec.get("mpns", []) if m.get("primary")), "?")
            mfrs = ",".join(rec.get("manufacturers") or [])
            print(f"{rec['sha256'][:12]}\t{primary}\t{mfrs}\t{store_path(rec).name}")
        return 0

    # default: text columns
    for rec in records:
        primary = next((m["mpn"] for m in rec.get("mpns", []) if m.get("primary")), "?")
        mfrs = ",".join(rec.get("manufacturers") or []) or "Unknown"
        print(f"{rec['sha256'][:12]}  {primary:<30}  {mfrs:<20}  {store_path(rec).name}")
    return 0


def _parse_rate_limit(spec: str) -> float:
    """Parse "N/s" or "N/min" → seconds-per-request interval. Default 1.0 (1/s)."""
    if not spec:
        return 1.0
    try:
        n_str, _, unit = spec.partition("/")
        n = float(n_str)
        unit = unit.strip().lower()
        if unit in ("s", "sec", "second", ""):
            return 1.0 / n if n > 0 else 1.0
        elif unit in ("min", "m", "minute"):
            return 60.0 / n if n > 0 else 60.0
    except Exception:
        pass
    return 1.0


def _try_found_in_fallback(rec: dict):
    """If `rec` has a recoverable `found_in` entry pointing at a local file
    whose bytes hash to rec['sha256'], return those bytes (bytes object).
    Otherwise return None."""
    from pathlib import Path
    from validate.datasheet_db.storage import compute_sha256, HARNESS_DIR
    for entry in rec.get("found_in") or []:
        kind = entry.get("type")
        if kind not in ("repo", "preserved"):
            continue
        ref = entry.get("ref", "")
        rel = entry.get("path", "")
        if not rel:
            continue
        if kind == "repo":
            candidate = HARNESS_DIR / "repos" / ref / rel
        else:  # preserved
            candidate = HARNESS_DIR / "datasheets_from_repos" / ref / rel
        if not candidate.exists():
            continue
        try:
            if compute_sha256(candidate) == rec["sha256"]:
                return candidate.read_bytes()
        except OSError:
            continue
    return None


def _mark_url_dead(rec: dict, dead_url: str, now: str) -> None:
    """Update a record's source_urls entry to status='dead' and persist."""
    import copy
    from validate.datasheet_db.manifest import save_record
    updated = copy.deepcopy(rec)
    for u in updated.get("source_urls") or []:
        if u["url"] == dead_url:
            u["status"] = "dead"
            u["last_verified_at"] = now
    updated["last_seen"] = now
    save_record(updated)


def cmd_fetch_missing(args) -> int:
    import os
    import threading
    from concurrent.futures import ThreadPoolExecutor
    from datetime import datetime, timezone
    from validate.datasheet_db.manifest import (
        iter_records, save_record, load_record, merge_record
    )
    from validate.datasheet_db.storage import (
        store_path, write_blob_atomic, compute_sha256
    )
    from validate.datasheet_db.fetcher import (
        fetch_verified, FetchError, handle_drift, DomainRateLimiter
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Default --jobs cap: min(cpu_count, 8)
    jobs = args.jobs if args.jobs is not None else min(os.cpu_count() or 1, 8)

    # Rate limiter shared across all workers
    interval = _parse_rate_limit(args.rate_limit) if args.rate_limit else 1.0
    rate_limiter = DomainRateLimiter(interval_seconds=interval)

    counters = {"downloaded": 0, "skipped": 0, "failed": 0,
                "unrecoverable": 0, "drifted": 0}
    counters_lock = threading.Lock()
    drift_log = []  # list of (old_sha[:12], new_sha[:12], url) for the report
    drift_log_lock = threading.Lock()

    def _bump(bucket: str):
        with counters_lock:
            counters[bucket] = counters.get(bucket, 0) + 1

    def _process_record(rec: dict) -> str:
        """Process one record and return the bucket name."""
        path = store_path(rec)

        # 1. Skip if blob present and verified
        if path.exists():
            try:
                if compute_sha256(path) == rec["sha256"]:
                    return "skipped"
            except OSError:
                pass  # treat as missing

        # 2. Filter URL list (drop dead unless --retry-dead)
        urls = [u for u in (rec.get("source_urls") or [])
                if u.get("status", "live") != "dead" or args.retry_dead]

        # 3. If no URLs left, try found_in fallback
        if not urls:
            local_bytes = _try_found_in_fallback(rec)
            if local_bytes is not None:
                if args.dry_run:
                    print(f"[dry-run] would copy local: {rec['sha256'][:12]}")
                    return "skipped"  # dry-run; not really downloaded
                write_blob_atomic(path, local_bytes, expected_sha256=rec["sha256"])
                return "downloaded"
            return "unrecoverable"

        # 4. Dry-run: print and return without bucketing
        if args.dry_run:
            print(f"[dry-run] would fetch: {rec['sha256'][:12]} from {urls[0]['url']}")
            return "skipped"  # dry-run records don't increment real buckets

        # 5. Try URLs in order
        success_bucket = None
        for url_entry in urls:
            url = url_entry["url"]
            rate_limiter.wait_for_url(url)
            try:
                result = fetch_verified(url, expected_sha256=rec["sha256"])
            except FetchError:
                # Mark URL as dead and persist
                _mark_url_dead(rec, url, now)
                continue
            if result.matched:
                write_blob_atomic(
                    path, result.fetch_result.body, expected_sha256=rec["sha256"]
                )
                success_bucket = "downloaded"
                break
            else:
                # Drift! Create new record + new blob
                new_record = handle_drift(
                    old_record=rec,
                    drifted_url=url,
                    new_body=result.fetch_result.body,
                    new_sha256=result.fetch_result.sha256,
                    now=now,
                )
                # Write the new blob to the store
                new_path = store_path(new_record)
                write_blob_atomic(
                    new_path, result.fetch_result.body,
                    expected_sha256=result.fetch_result.sha256,
                )
                with drift_log_lock:
                    drift_log.append(
                        (rec["sha256"][:12], result.fetch_result.sha256[:12], url)
                    )
                success_bucket = "drifted"
                break

        return success_bucket if success_bucket else "failed"

    records = list(iter_records())

    # Note: dry-run forces sequential to keep print order deterministic
    if args.dry_run or jobs <= 1:
        for rec in records:
            bucket = _process_record(rec)
            if not args.dry_run:
                _bump(bucket)
    else:
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            for bucket in ex.map(_process_record, records):
                _bump(bucket)

    # Summary
    print(f"Downloaded: {counters['downloaded']}")
    print(f"Skipped: {counters['skipped']}")
    print(f"Drifted: {counters['drifted']}")
    print(f"Failed: {counters['failed']}")
    print(f"Unrecoverable: {counters['unrecoverable']}")

    if drift_log:
        print()
        print("Drift detected — manual review recommended:")
        for old_sha, new_sha, url in drift_log:
            print(f"  {old_sha} → {new_sha} ({url})")

    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="datasheet_db")
    sub = parser.add_subparsers(dest="command", required=True)

    p_stats = sub.add_parser("stats", help="Print store summary")

    p_insert = sub.add_parser("insert", help="Insert a datasheet")
    p_insert.add_argument("--url")
    p_insert.add_argument("--file")
    p_insert.add_argument("--mpn")
    p_insert.add_argument("--manufacturer")
    p_insert.add_argument("--source", choices=["digikey", "lcsc", "auto"])

    p_find = sub.add_parser("find", help="Look up a datasheet")
    p_find.add_argument("query", nargs="?", default=None,
                        help="MPN to look up (or omit and use --sha256/--url)")
    p_find.add_argument("--sha256", help="Look up by sha256 prefix")
    p_find.add_argument("--url", help="Look up by source URL")
    p_find.add_argument("--json", action="store_true", help="Print full record as JSON array")
    p_find.add_argument("--open", action="store_true", help="xdg-open the result (not implemented)")

    p_verify = sub.add_parser("verify", help="Re-hash store blobs and check against manifest")
    p_verify.add_argument("--fast", action="store_true",
                          help="Skip re-hashing; only check blob existence")
    p_verify.add_argument("--record", help="Verify a single record by sha256 (not yet wired)")
    p_verify.add_argument("--json", action="store_true", help="Machine-readable output (not yet wired)")

    p_list = sub.add_parser("list", help="List records (with optional filters)")
    p_list.add_argument("--manufacturer", help="Filter by manufacturer name")
    p_list.add_argument("--missing", action="store_true",
                        help="Show only records whose blob is missing from the store")
    p_list.add_argument("--unverified", action="store_true",
                        help="Show only unverified records")
    p_list.add_argument("--format", choices=["text", "tsv", "json"], default="text",
                        help="Output format (default: text)")

    p_fetch = sub.add_parser("fetch-missing", help="Download blobs missing from the store")
    p_fetch.add_argument("--dry-run", action="store_true",
                         help="Report what would happen, fetch nothing")
    p_fetch.add_argument("--mpn", help="Filter to records containing this MPN (not yet wired)")
    p_fetch.add_argument("--manufacturer", help="Filter by manufacturer (not yet wired)")
    p_fetch.add_argument("--jobs", type=int, default=None,
                         help="Parallel workers (not yet wired)")
    p_fetch.add_argument("--rate-limit", help="Rate limit (not yet wired)")
    p_fetch.add_argument("--timeout", type=float, default=60.0, help="Per-request timeout")
    p_fetch.add_argument("--retry-dead", action="store_true",
                         help="Retry URLs previously marked as dead")
    p_fetch.add_argument("--max", type=int, default=None,
                         help="Stop after N successful downloads (for testing)")

    args = parser.parse_args(argv)

    handlers = {
        "stats": cmd_stats,
        "insert": cmd_insert,
        "find": cmd_find,
        "verify": cmd_verify,
        "list": cmd_list,
        "fetch-missing": cmd_fetch_missing,
    }
    return handlers[args.command](args)
