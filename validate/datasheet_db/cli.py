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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="datasheet_db")
    sub = parser.add_subparsers(dest="command", required=True)

    p_stats = sub.add_parser("stats", help="Print store summary")

    args = parser.parse_args(argv)

    handlers = {
        "stats": cmd_stats,
    }
    return handlers[args.command](args)
