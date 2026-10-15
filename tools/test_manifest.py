#!/usr/bin/env python3
"""Collection manifest: which test node ids exist and which tiers they carry.

    python3 tools/test_manifest.py --out m.json [--paths P ...] [-m EXPR | --all-tiers]
    python3 tools/test_manifest.py --compare-legacy legacy.json --manifest m.json

The legacy file is ``run_tests.py --json`` output (per-file passed counts); the
comparison is the migration proof for B9: equal rounded pass rates are not.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent


def write_manifest(out: Path, paths: list[str], marker_expr: str | None,
                   all_tiers: bool) -> int:
    out.unlink(missing_ok=True)  # a stale manifest must never pass the existence check
    cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q",
           "--manifest-out", str(out)]
    if all_tiers:
        cmd.append("--all-tiers")
    elif marker_expr:
        cmd += ["-m", marker_expr]
    cmd += paths
    proc = subprocess.run(cmd, cwd=HARNESS_DIR, capture_output=True, text=True)
    if proc.returncode not in (0, 5) or not out.exists():
        sys.stderr.write(proc.stdout + proc.stderr)
        return 1
    return 0


def compare_legacy(legacy: dict, manifest: dict) -> list[dict]:
    collected = Counter(nodeid.split("::", 1)[0] for nodeid in manifest)
    legacy_by_file = {row["file"]: row for row in legacy.get("files", [])}
    rows = []
    for f in sorted(set(collected) | set(legacy_by_file)):
        lrow = legacy_by_file.get(f)
        lp = lrow["passed"] if lrow else 0
        c = collected.get(f, 0)
        if lrow is None:
            note = "not in legacy run"
        elif c == 0:
            note = "MISSING under pytest — investigate"
        elif lrow.get("parsed") is False or lrow.get("status") in ("no_runner", "unparsed"):
            note = "legacy count was a phantom pass"
        else:
            note = ""
        rows.append({"file": f, "legacy_passed": lp, "collected": c, "delta": c - lp, "note": note})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, help="write manifest JSON here")
    ap.add_argument("--paths", nargs="*", default=[], help="paths to collect (default: testpaths)")
    ap.add_argument("-m", dest="marker_expr", default=None)
    ap.add_argument("--all-tiers", action="store_true")
    ap.add_argument("--compare-legacy", type=Path, help="run_tests.py --json output")
    ap.add_argument("--manifest", type=Path, help="manifest to compare against")
    args = ap.parse_args()
    if args.out:
        return write_manifest(args.out, args.paths, args.marker_expr, args.all_tiers)
    if args.compare_legacy and args.manifest:
        rows = compare_legacy(json.loads(args.compare_legacy.read_text(encoding="utf-8")),
                              json.loads(args.manifest.read_text(encoding="utf-8")))
        print(f"{'file':70} {'legacy':>7} {'pytest':>7} {'delta':>6}  note")
        for r in rows:
            print(f"{r['file']:70} {r['legacy_passed']:7d} {r['collected']:7d} {r['delta']:6d}  {r['note']}")
        missing = [r for r in rows if r["note"].startswith("MISSING")]
        print(f"\nfiles: {len(rows)}; legacy passed {sum(r['legacy_passed'] for r in rows)}; "
              f"pytest collected {sum(r['collected'] for r in rows)}; missing {len(missing)}")
        return 1 if missing else 0
    ap.error("need --out, or --compare-legacy with --manifest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
