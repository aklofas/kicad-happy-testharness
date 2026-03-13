#!/usr/bin/env python3
"""Generate review packets for LLM-assisted analysis review.

A review packet pairs a source KiCad file with its analyzer output
and generates review guidance, making it easy for Claude to independently
verify the analysis quality.

Usage:
    python3 review/packet.py --strategy random --count 5
    python3 review/packet.py --strategy changed --baseline before-refactor --count 5
    python3 review/packet.py --file "repos/hackrf/hardware/hackrf-one/hackrf-one.kicad_sch"
    python3 review/packet.py --list
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"
MANIFESTS_DIR = HARNESS_DIR / "results" / "manifests"
PACKETS_DIR = HARNESS_DIR / "results" / "review" / "packets"
BASELINES_DIR = HARNESS_DIR / "data" / "baselines"
DATASHEETS_DIR = HARNESS_DIR / "results" / "datasheets"


def _safe_name(path_str):
    repos_dir = str(HARNESS_DIR / "repos")
    rel = path_str
    if path_str.startswith(repos_dir):
        rel = path_str[len(repos_dir):].lstrip(os.sep)
    return rel.replace(os.sep, "_").replace("/", "_")


def _find_output(source_path, analyzer_type):
    """Find the analyzer output JSON for a given source file."""
    safe = _safe_name(source_path)
    output_file = OUTPUTS_DIR / analyzer_type / f"{safe}.json"
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

    return focus


def _check_datasheets(data):
    """Check which BOM MPNs have datasheets available locally."""
    bom = data.get("bom", [])
    if not bom:
        return None

    available = []
    missing = []

    for entry in bom:
        mpn = entry.get("mpn", "").strip()
        if not mpn:
            continue

        # Check for datasheet files matching this MPN
        found = False
        if DATASHEETS_DIR.exists():
            for pdf in DATASHEETS_DIR.rglob("*.pdf"):
                if mpn.lower() in pdf.stem.lower():
                    available.append({"mpn": mpn, "file": pdf.name})
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
            else:
                summary = {"sections": sorted(data.keys())}

            packet["output_file"] = str(output_file)
            packet["summary"] = summary
            packet["guidance"] = _generate_guidance(summary, analyzer_type)

            # Check datasheet availability for BOM entries
            ds_info = _check_datasheets(data)
            if ds_info:
                packet["datasheets"] = ds_info
        except Exception as e:
            packet["output_error"] = str(e)
    else:
        packet["output_file"] = None
        packet["guidance"] = ["No analyzer output found -- run the analyzer first"]

    return packet


def select_random(manifest_file, count, analyzer_type):
    """Select random files from a manifest."""
    if not manifest_file.exists():
        return []
    lines = [l.strip() for l in manifest_file.read_text().splitlines() if l.strip()]
    # Filter to files that have outputs
    available = [l for l in lines if _find_output(l, analyzer_type)]
    if len(available) <= count:
        return available
    return random.sample(available, count)


def select_changed(baseline_name, count, analyzer_type):
    """Select files with highest change scores from a baseline comparison."""
    sys.path.insert(0, str(HARNESS_DIR / "baselines"))
    from compare import compare_type

    results = compare_type(baseline_name, analyzer_type)
    if "error" in results:
        print(f"Error: {results['error']}")
        return []

    scored = sorted(results["change_scores"].items(), key=lambda x: x[1], reverse=True)
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
    for fname, score in scored[:count]:
        source = source_map.get(fname, fname)
        selected.append(source)
    return selected


def main():
    parser = argparse.ArgumentParser(description="Generate review packets")
    parser.add_argument("--strategy", choices=["random", "changed"],
                        help="File selection strategy")
    parser.add_argument("--count", "-n", type=int, default=5, help="Number of files")
    parser.add_argument("--baseline", help="Baseline name (for --strategy changed)")
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
        sources = select_random(MANIFESTS_DIR / manifest_name, args.count, args.type)
    elif args.strategy == "changed":
        if not args.baseline:
            print("Error: --baseline required with --strategy changed")
            sys.exit(1)
        sources = select_changed(args.baseline, args.count, args.type)
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

        # Write packet
        safe = _safe_name(source)
        packet_file = PACKETS_DIR / f"{safe}.json"
        packet_file.write_text(json.dumps(packet, indent=2) + "\n")

        # Print summary
        repos_dir = str(HARNESS_DIR / "repos")
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
        if packet.get("guidance"):
            print(f"    Focus areas:")
            for g in packet["guidance"][:3]:
                print(f"      - {g}")
        print()

    print(f"Packets written to {PACKETS_DIR}/")
    print(f"\nTo review: read the source file and output JSON, then compare.")


if __name__ == "__main__":
    main()
