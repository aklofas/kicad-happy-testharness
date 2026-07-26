#!/usr/bin/env python3
"""Run the kicad-cli netlist oracle against golden multi-sheet bus boards.

For each board: runs analyze_schematic.py on the root sheet, exports a
kicad-cli resolved netlist, compares the two by pin-grouping (see
regression/netlist_oracle.py), and prints a per-board report.

DEV/HARNESS-ONLY tooling for GH #25 (hierarchical bus connectivity). Never a
shipped kicad-happy dependency — see memory reference_kicad_cli_netlist_oracle.

Usage:
    python3 regression/run_netlist_oracle.py --board incrementer
    python3 regression/run_netlist_oracle.py --all
    python3 regression/run_netlist_oracle.py --all --strict
    python3 regression/run_netlist_oracle.py --board incrementer --json
    python3 regression/run_netlist_oracle.py --board incrementer --debug-unresolved

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (default ~/Projects/kicad-happy;
                      overridden by --kicad-happy)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# KiCad emits a synthetic single-pin net `unconnected-(<REF>-<PIN>)` for every
# pad with no schematic connection. Most match the analyzer's own single-pin
# unconnected nets 1:1 and compare cleanly. But the analyzer's no-connect design
# ABSORBS a component's NC pads into ONE net, so a component with many NC pads
# (e.g. m68k's U25/U12) shows up as a merged group — one analyzer net covering
# many `unconnected-(...)` oracle nets — plus the extra oracle single-pin nets
# it collapsed. That is a pre-existing NC-modeling divergence, NOT a bus defect
# (tracked for a future release). `_apply_nc_divergence` reclassifies exactly
# those merged groups (every covered oracle net matches the pattern) as
# `nc_divergence`, removing them from the gating `merged` list and discounting
# the collapsed single-pin nets, then recomputes `pass`. This can never mask a
# genuine bus merge: a bus member net is named after its label (e.g. /Bus/D0)
# and never matches this pattern, so a real over-merge always leaves at least
# one non-NC oracle net in the group and stays a gating merge. The analyzer's
# NC behavior is left untouched.
_NC_NET_RE = re.compile(r"^unconnected-\(")


def _apply_nc_divergence(result: dict) -> None:
    """Reclassify all-NC merged groups as non-gating nc_divergence and
    recompute pass. Mutates result in place; no-op on error results."""
    if "merged" not in result:
        return
    nc_groups, real_merged = [], []
    for m in result["merged"]:
        if m["oracle_nets"] and all(_NC_NET_RE.match(n) for n in m["oracle_nets"]):
            nc_groups.append(m)
        else:
            real_merged.append(m)
    result["merged"] = real_merged
    # Each absorbed oracle net is a single-pin unconnected net; the analyzer
    # collapsed them into one multi-pin net, so discount them from the oracle
    # single-pin total before the balance check.
    absorbed = sum(len(m["oracle_nets"]) for m in nc_groups)
    result["nc_divergence"] = absorbed
    result["nc_divergence_groups"] = len(nc_groups)
    adjusted_oracle_single = result["oracle_single_pin"] - absorbed
    result["pass"] = (
        not result["split"]
        and not real_merged
        and result["analyzer_single_pin"] == adjusted_oracle_single
    )

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from regression.netlist_oracle import analyzer_nets, compare, export_netlist, parse_netlist

HARNESS_DIR = Path(__file__).resolve().parent.parent

# Paths relative to the harness root. m68k-hbc fills the spec's "C64" role
# (no single multi-sheet C64 project exists in the corpus) — same-name
# D[0..31]/A[0..31] vector buses across 24 sheets; root file resolved as the
# .kicad_sch matching the .kicad_pro stem (verified 2026-07-24).
GOLDEN = {
    "incrementer": "repos/freesurfer-rge/slothpu16/pcbs/Incrementer/Incrementer.kicad_sch",
    "alu-carrier": "repos/freesurfer-rge/slothpu16/pcbs/ALU Carrier/ALU Carrier.kicad_sch",
    "m68k-hbc": "repos/ehbc-project/ehbc-proto1-board/projects/m68k-hbc/m68k-hbc.kicad_sch",
    "openmd": "repos/CrabLabsLLC/OpenMD/OpenMD.kicad_sch",
    # Older s-expr era (KiCad 6, file version 20221004) — the KiCad "video"
    # demo: 7 sub-sheets, vector buses DQ[0..31]/DPC[0..31]/ADR[2..6]/MXA[0..10]
    # crossing sheet pins. Validates our parse of the older grammar against
    # KiCad's own interpretation of the same file (Task 11 Step 5b). The golden
    # four are all KiCad 7.
    "older-era": "repos/circuitly/kicad-demos/video/video.kicad_sch",
}


def _default_kicad_happy_dir() -> Path:
    return Path.home() / "Projects" / "kicad-happy"


def _verify_golden_paths() -> None:
    """Fail loudly (before any work) if a GOLDEN root file is missing."""
    missing = []
    for name, rel in GOLDEN.items():
        full = HARNESS_DIR / rel
        if not full.exists():
            missing.append((name, str(full)))
    if missing:
        print("Error: GOLDEN board root file(s) not found:", file=sys.stderr)
        for name, full in missing:
            print(f"  {name}: {full}", file=sys.stderr)
        sys.exit(1)


def run_board(name: str, kicad_happy_dir: Path) -> dict:
    """Run one board through the oracle pipeline. Returns the compare() dict
    plus board metadata (board name, sch path, error if the pipeline itself
    failed before compare() could run)."""
    rel = GOLDEN[name]
    sch_path = HARNESS_DIR / rel
    analyzer_script = kicad_happy_dir / "skills" / "kicad" / "scripts" / "analyze_schematic.py"

    with tempfile.TemporaryDirectory(prefix=f"netlist-oracle-{name}-") as tmpdir:
        tmp = Path(tmpdir)
        analysis_json = tmp / "analysis.json"
        oracle_net = tmp / "oracle.net"

        proc = subprocess.run(
            [sys.executable, str(analyzer_script), str(sch_path), "--output", str(analysis_json)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return {
                "board": name,
                "sch_path": str(sch_path),
                "error": f"analyze_schematic.py failed (exit {proc.returncode}): {proc.stderr.strip()[-2000:]}",
            }

        try:
            export_netlist(str(sch_path), str(oracle_net))
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode("utf-8", "replace") if isinstance(e.stderr, bytes) else str(e.stderr)
            return {
                "board": name,
                "sch_path": str(sch_path),
                "error": f"kicad-cli export failed (exit {e.returncode}): {stderr.strip()[-2000:]}",
            }

        analyzer = analyzer_nets(str(analysis_json))
        oracle = parse_netlist(str(oracle_net))
        result = compare(analyzer, oracle)
        result["board"] = name
        result["sch_path"] = str(sch_path)
        result["analyzer_net_count"] = len(analyzer)
        result["oracle_net_count"] = len(oracle)
        _apply_nc_divergence(result)
        return result


def _worst_diffs(result: dict, limit: int = 10) -> list[dict]:
    """Combine split + merged, sorted by group-size (worst first), capped at limit."""
    diffs = []
    for s in result.get("split", []):
        diffs.append({"kind": "split", "size": len(s["analyzer_nets"]), **s})
    for m in result.get("merged", []):
        diffs.append({"kind": "merged", "size": len(m["oracle_nets"]), **m})
    diffs.sort(key=lambda d: (-d["size"], d["kind"], d.get("oracle_net", d.get("analyzer_net", ""))))
    return diffs[:limit]


def print_report(result: dict, debug_unresolved: bool = False) -> None:
    board = result["board"]
    if "error" in result:
        print(f"=== {board}: ERROR ===")
        print(f"  sch: {result['sch_path']}")
        print(f"  {result['error']}")
        return

    status = "PASS" if result["pass"] else "FAIL"
    print(f"=== {board}: {status} ===")
    print(f"  sch: {result['sch_path']}")
    print(f"  analyzer nets: {result['analyzer_net_count']}  oracle nets: {result['oracle_net_count']}")
    print(f"  matched: {result['matched']}  split: {len(result['split'])}  merged: {len(result['merged'])}")
    print(f"  analyzer_only: {len(result['analyzer_only'])}  oracle_only: {len(result['oracle_only'])}")
    print(f"  single-pin nets — analyzer: {result['analyzer_single_pin']}  oracle: {result['oracle_single_pin']}")
    excluded = []
    if result.get("nc_divergence"):
        excluded.append(f"nc_divergence={result['nc_divergence']}")
    if result.get("stacked_pins"):
        excluded.append(f"stacked_pins={len(result['stacked_pins'])} ({', '.join(result['stacked_pins'])})")
    if excluded:
        print(f"  excluded (non-bus structural divergence): {'  '.join(excluded)}")

    worst = _worst_diffs(result)
    if worst:
        print(f"  worst diffs (top {len(worst)}):")
        for d in worst:
            if d["kind"] == "split":
                print(f"    SPLIT  oracle {d['oracle_net']!r} -> analyzer {d['analyzer_nets']}")
            else:
                print(f"    MERGED analyzer {d['analyzer_net']!r} <- oracle {d['oracle_nets']}")

    if debug_unresolved:
        if result["analyzer_only"]:
            print(f"  analyzer_only nets: {result['analyzer_only']}")
        if result["oracle_only"]:
            print(f"  oracle_only nets: {result['oracle_only']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--board", choices=sorted(GOLDEN), help="run a single GOLDEN board")
    group.add_argument("--all", action="store_true", help="run all GOLDEN boards")
    parser.add_argument("--strict", action="store_true", help="exit 1 if any board fails (or errors)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON instead of the text report")
    parser.add_argument("--kicad-happy", default=None, help="path to kicad-happy repo (default: $KICAD_HAPPY_DIR or ~/Projects/kicad-happy)")
    parser.add_argument("--debug-unresolved", action="store_true", help="print full analyzer_only/oracle_only net-name lists")
    args = parser.parse_args()

    if args.kicad_happy:
        kicad_happy_dir = Path(args.kicad_happy)
    elif os.environ.get("KICAD_HAPPY_DIR"):
        kicad_happy_dir = Path(os.environ["KICAD_HAPPY_DIR"])
    else:
        kicad_happy_dir = _default_kicad_happy_dir()

    if not kicad_happy_dir.exists():
        print(f"Error: kicad-happy dir not found: {kicad_happy_dir}", file=sys.stderr)
        return 1

    _verify_golden_paths()

    boards = sorted(GOLDEN) if args.all else [args.board]
    results = [run_board(name, kicad_happy_dir) for name in boards]

    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        for result in results:
            print_report(result, debug_unresolved=args.debug_unresolved)
            print()

    if args.strict:
        failed = [r["board"] for r in results if r.get("error") or not r.get("pass")]
        if failed:
            print(f"STRICT: {len(failed)} board(s) failed: {sorted(failed)}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
