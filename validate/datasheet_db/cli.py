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

    args = parser.parse_args(argv)

    handlers = {
        "stats": cmd_stats,
        "insert": cmd_insert,
        "find": cmd_find,
        "verify": cmd_verify,
        "list": cmd_list,
    }
    return handlers[args.command](args)
