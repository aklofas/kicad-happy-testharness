#!/usr/bin/env python3
"""Generate review packets for LLM-assisted analysis review.

A review packet pairs a source KiCad file with its analyzer output
and generates review guidance, making it easy for Claude to independently
verify the analysis quality.

Usage:
    python3 regression/packet.py --strategy random --count 5
    python3 regression/packet.py --strategy changed --repo OpenMower --count 5
    python3 regression/packet.py --file "repos/hackrf/hardware/hackrf-one/hackrf-one.kicad_sch"
    python3 regression/packet.py --repo OpenMower --strategy random --count 3
    python3 regression/packet.py --list
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (
    HARNESS_DIR, OUTPUTS_DIR, MANIFESTS_DIR, REPOS_DIR, DATA_DIR,
    repo_name_from_path, safe_name as _safe_name,
    filter_manifest_by_repo, list_projects_in_data,
    load_project_metadata,
)

PACKETS_DIR = HARNESS_DIR / "results" / "review" / "packets"
DATASHEETS_DIR = HARNESS_DIR / "results" / "datasheets"


def _find_output(source_path, analyzer_type):
    """Find the analyzer output JSON for a given source file."""
    repo = repo_name_from_path(source_path)
    sname = _safe_name(source_path)
    if repo:
        output_file = OUTPUTS_DIR / analyzer_type / repo / f"{sname}.json"
        if output_file.exists():
            return output_file
    return None


def _summarize_schematic_output(data):
    """Extract review-relevant summary from schematic analyzer output."""
    stats = data.get("statistics", {})
    sa = data.get("signal_analysis", {})

    signal_summary = {}
    if isinstance(sa, dict):
        for key, val in sa.items():
            if isinstance(val, list):
                signal_summary[key] = len(val)

    return {
        "total_components": stats.get("total_components", 0),
        "total_nets": stats.get("total_nets", 0),
        "signal_detections": signal_summary,
        "erc_warning_count": len(data.get("design_analysis", {}).get("erc_warnings", [])),
        "bom_lines": len(data.get("bom", [])),
        "sections_present": sorted(k for k in data.keys() if k != "file"),
    }


def _summarize_pcb_output(data):
    """Extract review-relevant summary from PCB analyzer output."""
    stats = data.get("statistics", {})
    conn = data.get("connectivity", {})
    dfm = data.get("dfm", {})

    return {
        "footprint_count": stats.get("footprint_count", 0),
        "smd_count": stats.get("smd_count", 0),
        "tht_count": stats.get("tht_count", 0),
        "front_side": stats.get("front_side", 0),
        "back_side": stats.get("back_side", 0),
        "copper_layers": stats.get("copper_layers_used", 0),
        "copper_layer_names": stats.get("copper_layer_names", []),
        "track_segments": stats.get("track_segments", 0),
        "via_count": stats.get("via_count", 0),
        "zone_count": stats.get("zone_count", 0),
        "net_count": stats.get("net_count", 0),
        "total_track_length_mm": stats.get("total_track_length_mm", 0),
        "board_width_mm": stats.get("board_width_mm", 0),
        "board_height_mm": stats.get("board_height_mm", 0),
        "routing_complete": stats.get("routing_complete"),
        "unrouted_count": stats.get("unrouted_net_count", 0),
        "dfm_tier": dfm.get("dfm_tier", ""),
        "dfm_violation_count": dfm.get("violation_count", 0),
        "decoupling_count": len(data.get("decoupling_placement", [])),
        "power_net_count": len(data.get("power_net_routing", [])),
        "thermal_pad_vias": len(data.get("thermal_pad_vias", [])),
        "sections_present": sorted(k for k in data.keys() if k != "file"),
    }


def _generate_guidance(summary, analyzer_type):
    """Generate review focus areas from output summary."""
    focus = []

    if analyzer_type == "schematic":
        sigs = summary.get("signal_detections", {})

        for sig_type, count in sigs.items():
            if count == 0:
                focus.append(f"0 {sig_type} detected -- does the schematic have any?")
            else:
                focus.append(f"{count} {sig_type} detected -- verify these are correct")

        comps = summary.get("total_components", 0)
        if comps == 0:
            focus.append("Zero components -- is this a hierarchical sheet or empty?")
        elif comps > 500:
            focus.append(f"{comps} components -- large design, check for parsing issues")

        erc = summary.get("erc_warning_count", 0)
        if erc > 0:
            focus.append(f"{erc} ERC warnings -- are these real issues or false positives?")

        if not focus:
            focus.append("General review: verify component types and signal paths")

    elif analyzer_type == "pcb":
        fps = summary.get("footprint_count", 0)
        if fps == 0:
            focus.append("Zero footprints -- is this an empty or template PCB?")
        else:
            smd = summary.get("smd_count", 0)
            tht = summary.get("tht_count", 0)
            focus.append(f"{fps} footprints ({smd} SMD, {tht} THT) -- verify counts")

        cu = summary.get("copper_layers", 0)
        if cu > 2:
            focus.append(f"{cu}-layer board -- verify layer stack and inner layer usage")

        if not summary.get("routing_complete"):
            unrouted = summary.get("unrouted_count", 0)
            focus.append(f"Routing incomplete ({unrouted} unrouted) -- expected or error?")

        dfm_violations = summary.get("dfm_violation_count", 0)
        if dfm_violations > 0:
            tier = summary.get("dfm_tier", "")
            focus.append(f"{dfm_violations} DFM violations (tier: {tier}) -- verify severity")

        decoupling = summary.get("decoupling_count", 0)
        if decoupling > 0:
            focus.append(f"{decoupling} decoupling placements -- verify IC/cap associations")
        elif fps > 20:
            focus.append("No decoupling analysis -- are there ICs with bypass caps?")

        power = summary.get("power_net_count", 0)
        if power > 0:
            focus.append(f"{power} power net(s) analyzed -- verify current capacity ratings")

        thermal = summary.get("thermal_pad_vias", 0)
        if thermal > 0:
            focus.append(f"{thermal} thermal pad via(s) -- verify adequacy for QFN/BGA")

        if not focus:
            focus.append("General review: verify footprint placement and connectivity")

    return focus


def _check_datasheets(data):
    """Check which BOM MPNs have datasheets available locally."""
    bom = data.get("bom", [])
    if not bom:
        return None

    available = []
    missing = []

    # Pre-build a lookup map of PDF stems for fast matching
    pdf_map = {}
    if DATASHEETS_DIR.exists():
        for pdf in DATASHEETS_DIR.rglob("*.pdf"):
            pdf_map[pdf.stem.lower()] = pdf.name

    for entry in bom:
        mpn = entry.get("mpn", "").strip()
        if not mpn:
            continue

        found = False
        mpn_lower = mpn.lower()
        for stem, filename in pdf_map.items():
            if mpn_lower in stem:
                available.append({"mpn": mpn, "file": filename})
                found = True
                break
        if not found:
            missing.append(mpn)

    total = len(available) + len(missing)
    if total == 0:
        return None

    return {
        "available": available,
        "missing": missing,
        "coverage": f"{len(available)}/{total} ({len(available)*100//total}%)",
    }


def generate_packet(source_path, analyzer_type="schematic"):
    """Generate a single review packet."""
    output_file = _find_output(source_path, analyzer_type)

    packet = {
        "created": datetime.now(timezone.utc).isoformat(),
        "analyzer_type": analyzer_type,
        "source_file": source_path,
        "source_exists": Path(source_path).exists(),
    }

    if output_file:
        try:
            data = json.loads(output_file.read_text())
            if analyzer_type == "schematic":
                summary = _summarize_schematic_output(data)
            elif analyzer_type == "pcb":
                summary = _summarize_pcb_output(data)
            else:
                summary = {"sections": sorted(data.keys())}

            packet["output_file"] = str(output_file)
            packet["summary"] = summary
            packet["guidance"] = _generate_guidance(summary, analyzer_type)

            ds_info = _check_datasheets(data)
            if ds_info:
                packet["datasheets"] = ds_info
        except Exception as e:
            packet["output_error"] = str(e)
    else:
        packet["output_file"] = None
        packet["guidance"] = ["No analyzer output found -- run the analyzer first"]

    return packet


def select_random(manifest_file, count, analyzer_type, repo=None):
    """Select random files from a manifest."""
    if not manifest_file.exists():
        return []
    lines = [l.strip() for l in manifest_file.read_text().splitlines() if l.strip()]
    if repo:
        lines = filter_manifest_by_repo(lines, repo)
    available = [l for l in lines if _find_output(l, analyzer_type)]
    if len(available) <= count:
        return available
    return random.sample(available, count)


def select_changed(repo_name, count, analyzer_type):
    """Select files with highest change scores from a baseline comparison."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from compare import compare_project

    projects = list_projects_in_data(repo_name)
    if not projects:
        print(f"No projects with baselines for {repo_name}")
        return []

    # Collect scores across all projects
    all_scored = []
    for proj_name in projects:
        project_path = load_project_metadata(repo_name, proj_name).get("project_path", ".")

        results = compare_project(repo_name, proj_name, project_path, analyzer_type)
        if "error" in results:
            continue
        for fname, score in results.get("change_scores", {}).items():
            all_scored.append((fname, score))

    all_scored.sort(key=lambda x: x[1], reverse=True)

    # Map output filenames back to source paths
    manifest_file = MANIFESTS_DIR / f"all_{'schematics' if analyzer_type == 'schematic' else analyzer_type + 's'}.txt"
    source_map = {}
    if manifest_file.exists():
        for line in manifest_file.read_text().splitlines():
            line = line.strip()
            if line:
                safe = _safe_name(line) + ".json"
                source_map[safe] = line

    selected = []
    for fname, score in all_scored[:count]:
        source = source_map.get(fname, fname)
        selected.append(source)
    return selected


def main():
    parser = argparse.ArgumentParser(description="Generate review packets")
    parser.add_argument("--strategy", choices=["random", "changed"],
                        help="File selection strategy")
    parser.add_argument("--count", "-n", type=int, default=5, help="Number of files")
    parser.add_argument("--repo", help="Filter to a specific repo")
    parser.add_argument("--file", help="Specific source file to review")
    parser.add_argument("--type", choices=["schematic", "pcb", "gerber"],
                        default="schematic", help="Analyzer type")
    parser.add_argument("--list", action="store_true", help="List existing packets")
    args = parser.parse_args()

    if args.list:
        PACKETS_DIR.mkdir(parents=True, exist_ok=True)
        packets = sorted(PACKETS_DIR.glob("*.json"))
        if not packets:
            print("No review packets found.")
            return
        for p in packets:
            try:
                data = json.loads(p.read_text())
                src = data.get("source_file", "?")
                if len(src) > 50:
                    src = "..." + src[-47:]
                print(f"  {p.name}: {src}")
            except Exception:
                print(f"  {p.name}: (error reading)")
        return

    # Select files
    if args.file:
        sources = [args.file]
    elif args.strategy == "random":
        manifest_name = "all_schematics.txt" if args.type == "schematic" else f"all_{args.type}s.txt"
        sources = select_random(MANIFESTS_DIR / manifest_name, args.count, args.type, repo=args.repo)
    elif args.strategy == "changed":
        if not args.repo:
            print("Error: --repo required with --strategy changed")
            sys.exit(1)
        sources = select_changed(args.repo, args.count, args.type)
    else:
        print("Error: specify --file or --strategy")
        sys.exit(1)

    if not sources:
        print("No files selected for review.")
        sys.exit(1)

    PACKETS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(sources)} review packet(s)...\n")
    for source in sources:
        packet = generate_packet(source, args.type)

        safe = _safe_name(source)
        packet_file = PACKETS_DIR / f"{safe}.json"
        packet_file.write_text(json.dumps(packet, indent=2) + "\n")

        repos_dir = str(REPOS_DIR)
        display = source
        if source.startswith(repos_dir):
            display = source[len(repos_dir):].lstrip(os.sep)

        print(f"  {display}")
        if packet.get("summary"):
            s = packet["summary"]
            if "total_components" in s:
                sigs = s.get("signal_detections", {})
                sig_str = ", ".join(f"{k}={v}" for k, v in sorted(sigs.items()) if v > 0)
                print(f"    Components: {s['total_components']}, Nets: {s['total_nets']}")
                if sig_str:
                    print(f"    Signals: {sig_str}")
            elif "footprint_count" in s:
                print(f"    Footprints: {s['footprint_count']} ({s.get('smd_count',0)} SMD, {s.get('tht_count',0)} THT)")
                print(f"    Layers: {s.get('copper_layers',0)}, Tracks: {s.get('track_segments',0)}, Vias: {s.get('via_count',0)}")
                if s.get("dfm_tier"):
                    print(f"    DFM: {s['dfm_tier']} ({s.get('dfm_violation_count',0)} violations)")
        if packet.get("guidance"):
            print(f"    Focus areas:")
            for g in packet["guidance"][:3]:
                print(f"      - {g}")
        print()

    print(f"Packets written to {PACKETS_DIR}/")
    print(f"\nTo review: read the source file and output JSON, then compare.")


if __name__ == "__main__":
    main()
