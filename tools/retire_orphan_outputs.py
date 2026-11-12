#!/usr/bin/env python3
"""List, and with --apply quarantine, schematic/pcb/gerber outputs that no current manifest
unit writes (TH-099).

An output whose input left the manifest, or was named under an older output-naming scheme,
is never rewritten by the batch runners and stays live for run_checks and for the chained
runners' pairing. --apply renames each one to <name>.stale, the same quarantine the chained
runners use for their own orphans. Without --apply nothing is renamed.

Usage:
    python3 tools/retire_orphan_outputs.py --all
    python3 tools/retire_orphan_outputs.py --repo owner/repo --type pcb --apply

Exit 0 on success; 2 on a missing manifest or no selector.
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (MANIFESTS_DIR, OUTPUTS_DIR, add_repo_filter_args, filter_manifest_by_repo,
                   repo_name_from_path, resolve_repos, retire_orphaned_outputs, safe_name)

MANIFESTS = {"schematic": "all_schematics.txt", "pcb": "all_pcbs.txt", "gerber": "all_gerbers.txt"}


def expected_outputs(kind, repo_list):
    """repo -> output names the manifest's units write, as the batch runner names them."""
    lines = [l.strip() for l in (MANIFESTS_DIR / MANIFESTS[kind]).read_text(
        encoding="utf-8").splitlines() if l.strip()]
    if repo_list is not None:
        lines = [l for rn in repo_list for l in filter_manifest_by_repo(lines, rn)]
    expected = defaultdict(set)
    for line in lines:
        expected[repo_name_from_path(line)].add(safe_name(line) + ".json")
    return expected


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    add_repo_filter_args(parser)
    parser.add_argument("--type", nargs="+", choices=sorted(MANIFESTS), default=["pcb", "gerber"],
                        help="output types to check (default: pcb gerber)")
    parser.add_argument("--apply", action="store_true",
                        help="rename orphans to .stale (default: list only)")
    args = parser.parse_args(argv)
    repo_list = resolve_repos(args, require_explicit_all=True)

    missing = [MANIFESTS[k] for k in args.type if not (MANIFESTS_DIR / MANIFESTS[k]).exists()]
    if missing:
        print(f"Error: manifest missing: {', '.join(missing)}. Run discover.py first.",
              file=sys.stderr)
        return 2

    verb = "RETIRED" if args.apply else "WOULD RETIRE"
    total = 0
    for kind in args.type:
        out_dir = OUTPUTS_DIR / kind
        if not out_dir.is_dir():
            continue
        found = retire_orphaned_outputs(out_dir, repo_list, expected_outputs(kind, repo_list),
                                        apply=args.apply)
        for f in found:
            print(f"{verb} {kind} {f.relative_to(out_dir)}")
        print(f"{kind}: {len(found)} orphan output(s)")
        total += len(found)
    if not args.apply:
        print(f"dry run: {total} output(s) would be renamed to .stale; pass --apply to rename")
    return 0


if __name__ == "__main__":
    sys.exit(main())
