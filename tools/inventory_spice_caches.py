#!/usr/bin/env python3
"""Read-only inventory of every spice/ directory under repos/.

The spice skill resolves its model cache to <project>/spice/models/ beside the
corpus schematic (TH-059), and other simulator output can land elsewhere under
spice/. run_spice.py --workdir keeps the harness's own simulation work files out
of repos/ and pins the simulator's model cache to the unit workdir
(--model-cache-dir, TH-077); this tool proves no run wrote under repos/ anyway: it hashes every file under every spice/ dir (recursively, keyed by path
relative to that spice/ dir, e.g. models/manifest.json) and never writes under
--repos-root.

Usage:
    python3 tools/inventory_spice_caches.py --repos-root repos -o results/v3_baseline/6a91aaa/spice_cache_inventory.json
    python3 tools/inventory_spice_caches.py --repos-root repos --check <inventory.json>   # exit 1 on drift
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_inventory(repos_root: Path) -> dict:
    repos_root = Path(repos_root)
    dirs = {}
    files = 0
    for spice in sorted(repos_root.rglob("spice")):
        if not spice.is_dir() or ".git" in spice.relative_to(repos_root).parts:
            continue
        rel = spice.relative_to(repos_root).as_posix()
        entry = {"manifest_sha256": None, "files": {}}
        for f in sorted(p for p in spice.rglob("*") if p.is_file()):
            entry["files"][f.relative_to(spice).as_posix()] = _sha(f)
            files += 1
        entry["manifest_sha256"] = entry["files"].get("models/manifest.json")
        dirs[rel] = entry
    return {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "repos_root": str(repos_root.resolve()), "dirs": dirs,
            "dir_count": len(dirs), "file_count": files}


def diff_inventory(old: dict, new: dict) -> list[str]:
    out = []
    for d in sorted(set(old["dirs"]) | set(new["dirs"])):
        a, b = old["dirs"].get(d), new["dirs"].get(d)
        if a is None:
            out.append(f"new dir: {d}")
            continue
        if b is None:
            out.append(f"missing dir: {d}")
            continue
        for f in sorted(set(a["files"]) | set(b["files"])):
            if a["files"].get(f) != b["files"].get(f):
                kind = "new" if f not in a["files"] else ("missing" if f not in b["files"] else "changed")
                out.append(f"{kind} file: {d}/{f}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repos-root", required=True, type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--check", type=Path, help="compare live tree against this inventory")
    args = ap.parse_args(argv)
    inv = build_inventory(args.repos_root)
    if args.check:
        old = json.loads(args.check.read_text(encoding="utf-8"))
        drift = diff_inventory(old, inv)
        for line in drift:
            print(line)
        print(f"{len(drift)} difference(s) vs {args.check}")
        return 1 if drift else 0
    if not args.output:
        ap.error("-o/--output or --check is required")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inv, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{inv['dir_count']} dirs / {inv['file_count']} files -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
