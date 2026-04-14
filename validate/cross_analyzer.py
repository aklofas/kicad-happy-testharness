#!/usr/bin/env python3
"""Cross-analyzer consistency checks.

Compares shared data across schematic, PCB, EMC, and SPICE outputs to catch
pairing errors, stale outputs, or extraction bugs.

Checks:
  schematic↔PCB:  component vs footprint count, net count
  PCB↔EMC:        via count, layer count (exact)
  schematic↔SPICE: component refs exist in findings

Usage:
    python3 validate/cross_analyzer.py
    python3 validate/cross_analyzer.py --repo owner/repo
    python3 validate/cross_analyzer.py --cross-section smoke --jobs 16
    python3 validate/cross_analyzer.py --summary
    python3 validate/cross_analyzer.py --json
"""

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import OUTPUTS_DIR, DEFAULT_JOBS, add_repo_filter_args, resolve_repos


# ---------------------------------------------------------------------------
# Pairing: find matching outputs across analyzer types for a repo
# ---------------------------------------------------------------------------

def find_paired_outputs(repo_name):
    """Find sets of matching outputs across analyzer types for a repo.

    Returns list of dicts with keys: stem, schematic, pcb, emc, spice
    (each is a Path or None).
    """
    sch_dir = OUTPUTS_DIR / "schematic" / repo_name
    if not sch_dir.exists():
        return []

    pairs = []
    for sch_file in sorted(sch_dir.glob("*.json")):
        if sch_file.name.startswith("_"):
            continue
        stem = sch_file.name
        entry = {"stem": stem, "schematic": sch_file, "pcb": None,
                 "emc": None, "spice": None}

        # Derive PCB path
        pcb_name = None
        if stem.endswith(".kicad_sch.json"):
            pcb_name = stem.replace(".kicad_sch.json", ".kicad_pcb.json")
        elif stem.endswith(".sch.json"):
            pcb_name = stem.replace(".sch.json", ".kicad_pcb.json")
        if pcb_name:
            pcb_path = OUTPUTS_DIR / "pcb" / repo_name / pcb_name
            if pcb_path.exists() and pcb_path.stat().st_size > 0:
                entry["pcb"] = pcb_path

        # EMC uses same filename as schematic
        emc_path = OUTPUTS_DIR / "emc" / repo_name / stem
        if emc_path.exists() and emc_path.stat().st_size > 0:
            entry["emc"] = emc_path

        # SPICE uses same filename as schematic
        spice_path = OUTPUTS_DIR / "spice" / repo_name / stem
        if spice_path.exists() and spice_path.stat().st_size > 0:
            entry["spice"] = spice_path

        pairs.append(entry)

    return pairs


def _load(path):
    """Load JSON from path, return None on error."""
    if path is None:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Cross-validation functions
# ---------------------------------------------------------------------------

def cross_validate_schematic_pcb(sch_data, pcb_data):
    """Compare schematic statistics against PCB statistics.

    Returns list of {check, source, target, status, detail}.
    """
    results = []
    sch_stats = sch_data.get("statistics", {})
    pcb_stats = pcb_data.get("statistics", {})

    # Component count vs footprint count
    # PCB may be 0-20% higher due to fab marks, fiducials, logos
    sch_comps = sch_stats.get("total_components", 0)
    pcb_fps = pcb_stats.get("footprint_count", 0)
    if sch_comps > 0 and pcb_fps > 0:
        ratio = pcb_fps / sch_comps if sch_comps else 0
        if 0.8 <= ratio <= 1.25:
            status = "match"
        elif pcb_fps >= sch_comps:
            status = "info"  # PCB has more (fab marks) — expected
        else:
            status = "mismatch"
        results.append({
            "check": "component_vs_footprint_count",
            "source": f"schematic={sch_comps}",
            "target": f"pcb={pcb_fps}",
            "status": status,
            "detail": f"ratio={ratio:.2f} (PCB/schematic)",
        })

    # Net count
    # Schematic may have 0-5% more nets than PCB (unrouted/internal)
    sch_nets = sch_stats.get("total_nets", 0)
    pcb_nets = pcb_stats.get("net_count", 0)
    if sch_nets > 0 and pcb_nets > 0:
        delta = sch_nets - pcb_nets
        delta_pct = delta / sch_nets * 100 if sch_nets else 0
        if abs(delta_pct) <= 10:
            status = "match"
        else:
            status = "mismatch"
        results.append({
            "check": "net_count",
            "source": f"schematic={sch_nets}",
            "target": f"pcb={pcb_nets}",
            "status": status,
            "detail": f"delta={delta} ({delta_pct:+.1f}%)",
        })

    return results


def cross_validate_pcb_emc(pcb_data, emc_data):
    """Compare PCB statistics against EMC board_info (should be exact).

    Returns list of {check, source, target, status, detail}.
    """
    results = []
    pcb_stats = pcb_data.get("statistics", {})
    board_info = emc_data.get("board_info", {})

    # Via count — should be exact
    pcb_vias = pcb_stats.get("via_count")
    emc_vias = board_info.get("via_count")
    if pcb_vias is not None and emc_vias is not None:
        status = "match" if pcb_vias == emc_vias else "mismatch"
        results.append({
            "check": "via_count",
            "source": f"pcb={pcb_vias}",
            "target": f"emc={emc_vias}",
            "status": status,
            "detail": "",
        })

    # Layer count — should be exact
    pcb_layers = pcb_stats.get("copper_layers_used")
    emc_layers = board_info.get("layer_count")
    if pcb_layers is not None and emc_layers is not None:
        status = "match" if pcb_layers == emc_layers else "mismatch"
        results.append({
            "check": "layer_count",
            "source": f"pcb={pcb_layers}",
            "target": f"emc={emc_layers}",
            "status": status,
            "detail": "",
        })

    # Footprint count — should be exact
    pcb_fps = pcb_stats.get("footprint_count")
    emc_fps = board_info.get("footprint_count")
    if pcb_fps is not None and emc_fps is not None:
        status = "match" if pcb_fps == emc_fps else "mismatch"
        results.append({
            "check": "footprint_count_pcb_emc",
            "source": f"pcb={pcb_fps}",
            "target": f"emc={emc_fps}",
            "status": status,
            "detail": "",
        })

    return results


def cross_validate_schematic_spice(sch_data, spice_data):
    """Verify SPICE simulation component refs exist in schematic findings.

    Returns list of {check, source, target, status, detail}.
    """
    results = []

    # Collect all component refs from schematic (components array + findings)
    sa_refs = set()
    for comp in sch_data.get("components", []):
        ref = comp.get("reference", "")
        if ref:
            sa_refs.add(ref)
    for finding in sch_data.get("findings", []):
        if not isinstance(finding, dict):
            continue
        for key, val in finding.items():
            if isinstance(val, dict) and "ref" in val:
                sa_refs.add(val["ref"])

    sim_results = spice_data.get("simulation_results", [])
    orphan_refs = []
    total_refs = 0
    for sr in sim_results:
        for ref in sr.get("components", []):
            total_refs += 1
            if ref not in sa_refs:
                orphan_refs.append(ref)

    if total_refs > 0:
        status = "match" if not orphan_refs else "mismatch"
        results.append({
            "check": "spice_component_refs",
            "source": f"schematic_sa_refs={len(sa_refs)}",
            "target": f"spice_refs={total_refs}",
            "status": status,
            "detail": f"orphans={orphan_refs[:5]}" if orphan_refs else "",
        })

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _cross_validate_repo(repo):
    """Cross-validate all paired outputs for a single repo.

    Returns (results_list, match_count, mismatch_count, info_count).
    Picklable top-level function for ProcessPoolExecutor.
    """
    pairs = find_paired_outputs(repo)
    results = []
    match = mismatch = info = 0

    for pair in pairs:
        sch = _load(pair["schematic"])
        pcb = _load(pair["pcb"])
        emc = _load(pair["emc"])
        spice = _load(pair["spice"])

        checks = []

        if sch and pcb:
            checks.extend(cross_validate_schematic_pcb(sch, pcb))
        if pcb and emc:
            checks.extend(cross_validate_pcb_emc(pcb, emc))
        if sch and spice:
            checks.extend(cross_validate_schematic_spice(sch, spice))

        for c in checks:
            c["repo"] = repo
            c["file"] = pair["stem"]
            if c["status"] == "match":
                match += 1
            elif c["status"] == "mismatch":
                mismatch += 1
            else:
                info += 1

        results.extend(checks)

    return results, match, mismatch, info


def _discover_output_repos():
    """List repos that have schematic outputs (owner/repo format)."""
    sch_dir = OUTPUTS_DIR / "schematic"
    if not sch_dir.exists():
        return []
    repos = []
    for owner_dir in sorted(sch_dir.iterdir()):
        if not owner_dir.is_dir() or owner_dir.name.startswith("_"):
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if repo_dir.is_dir():
                repos.append(f"{owner_dir.name}/{repo_dir.name}")
    return repos


def main():
    parser = argparse.ArgumentParser(
        description="Cross-analyzer consistency checks")
    add_repo_filter_args(parser)
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel workers (default: {DEFAULT_JOBS})")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--summary", action="store_true",
                        help="Only print summary counts")
    args = parser.parse_args()

    # Find repos
    repos = resolve_repos(args)
    if repos is None:
        repos = _discover_output_repos()

    if not repos:
        print("No schematic outputs found", file=sys.stderr)
        sys.exit(1)

    all_results = []
    total_checks = 0
    total_match = 0
    total_mismatch = 0
    total_info = 0
    jobs = args.jobs

    if jobs > 1 and len(repos) > 1:
        with ProcessPoolExecutor(max_workers=min(jobs, len(repos))) as pool:
            futures = {pool.submit(_cross_validate_repo, repo): repo
                       for repo in repos}
            for future in as_completed(futures):
                results, match, mismatch, info = future.result()
                all_results.extend(results)
                total_match += match
                total_mismatch += mismatch
                total_info += info
                total_checks += match + mismatch + info
    else:
        for repo in repos:
            results, match, mismatch, info = _cross_validate_repo(repo)
            all_results.extend(results)
            total_match += match
            total_mismatch += mismatch
            total_info += info
            total_checks += match + mismatch + info

    if args.json:
        json.dump({
            "total_checks": total_checks,
            "match": total_match,
            "mismatch": total_mismatch,
            "info": total_info,
            "results": all_results,
        }, sys.stdout, indent=2)
        print()
        return

    # Print results
    if not args.summary:
        for r in all_results:
            if r["status"] == "mismatch":
                print(f"MISMATCH {r['repo']}/{r['file']}: {r['check']} "
                      f"— {r['source']} vs {r['target']} {r['detail']}")

    print(f"\n{'='*60}")
    print(f"Cross-Analyzer Consistency Summary")
    print(f"{'='*60}")
    print(f"Total checks:    {total_checks}")
    print(f"  Match:         {total_match}")
    print(f"  Mismatch:      {total_mismatch}")
    print(f"  Info:          {total_info}")
    if total_checks > 0:
        print(f"  Agreement:     {total_match / total_checks * 100:.1f}%")

    # Group mismatches by check type
    if total_mismatch > 0:
        by_check = {}
        for r in all_results:
            if r["status"] == "mismatch":
                by_check.setdefault(r["check"], []).append(r)
        print(f"\nMismatches by check:")
        for check, items in sorted(by_check.items(), key=lambda x: -len(x[1])):
            print(f"  {check}: {len(items)}")


if __name__ == "__main__":
    main()
