#!/usr/bin/env python3
"""Validate analyzer JSON outputs across all schematics in the test corpus.

Checks structural invariants, cross-references, and flags anomalies.

Usage:
    python3 validate/validate_outputs.py
    python3 validate/validate_outputs.py --repo owner/repo
    python3 validate/validate_outputs.py --cross-section smoke --jobs 16
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (OUTPUTS_DIR, REPOS_DIR, MANIFESTS_DIR, list_repos,
                   DEFAULT_JOBS, add_repo_filter_args, resolve_repos,
                   _truncate_with_hash)


class ValidationContext:
    def __init__(self):
        self.anomalies = defaultdict(list)  # category -> [(file, detail)]
        self.stats = defaultdict(int)


def load_result(json_path):
    with open(json_path) as f:
        return json.load(f)


def validate_structural(ctx, name, data, is_modern):
    """Check structural invariants that should always hold."""
    ctx.stats["total"] += 1

    # Modern (.kicad_sch / v1.4 envelopes): provenance lives in `inputs`,
    # the legacy top-level `file` field was removed at Track 1.3.
    # Legacy (.sch KiCad 5): pre-envelope shape, still emits `file`.
    provenance_key = "inputs" if is_modern else "file"
    required = [provenance_key, "components", "nets", "labels", "power_symbols", "no_connects", "bom"]
    for key in required:
        if key not in data:
            ctx.anomalies["missing_key"].append((name, f"missing '{key}'"))

    stat_section = data.get("statistics", data.get("summary", {}))
    total_comps = stat_section.get("total_components", len(data.get("components", [])))
    total_nets = stat_section.get("total_nets", len(data.get("nets", [])))

    ctx.stats["total_components"] += total_comps
    ctx.stats["total_nets"] += total_nets

    if total_comps == 0:
        ctx.stats["zero_comp"] += 1
    if total_nets == 0:
        ctx.stats["zero_net"] += 1

    if is_modern and total_comps > 0:
        ctx.stats["modern_with_comps"] += 1
        if "findings" not in data:
            ctx.anomalies["missing_findings"].append((name, f"{total_comps} comps but no findings"))
        if "design_analysis" not in data:
            ctx.anomalies["missing_design_analysis"].append((name, f"{total_comps} comps but no design_analysis"))

        new_sections = [
            "annotation_issues", "label_shape_warnings", "pwr_flag_warnings",
            "footprint_filter_warnings", "sourcing_audit", "ground_domains",
            "bus_topology", "wire_geometry", "property_issues",
            "hierarchical_labels", "title_block"
        ]
        for section in new_sections:
            if section not in data:
                ctx.anomalies["missing_new_section"].append((name, f"missing '{section}'"))

    if not is_modern:
        ctx.stats["legacy"] += 1
    else:
        ctx.stats["modern"] += 1


def validate_components(ctx, name, data):
    """Check component data integrity."""
    components = data.get("components", [])
    refs = [c.get("reference", "") for c in components]

    real_refs = [r for r in refs if r and r != "?" and not r.startswith("#")]
    ref_counts = defaultdict(int)
    for r in real_refs:
        ref_counts[r] += 1
    dupes = {r: c for r, c in ref_counts.items() if c > 1}
    if dupes and len(dupes) > 5:
        ctx.anomalies["many_duplicate_refs"].append((name, f"{len(dupes)} duplicate refs"))

    unknown = [c for c in components if c.get("type") == "unknown" and not c.get("reference", "").startswith("#")]
    if len(unknown) > len(components) * 0.3 and len(unknown) > 5:
        ctx.anomalies["high_unknown_type"].append((name, f"{len(unknown)}/{len(components)} unknown type"))

    bom = data.get("bom", [])
    bom_total = sum(b.get("quantity", 0) for b in bom)
    non_power_comps = [c for c in components if not c.get("reference", "").startswith("#")]
    if bom and abs(bom_total - len(non_power_comps)) > 5:
        ctx.anomalies["bom_mismatch"].append((name, f"BOM qty={bom_total} vs components={len(non_power_comps)}"))


def validate_nets(ctx, name, data, total_comps):
    """Check net data integrity."""
    nets = data.get("nets", {})
    if isinstance(nets, list):
        total_nets = len(nets)
        net_items = nets
    elif isinstance(nets, dict):
        total_nets = len(nets)
        net_items = nets.values()
    else:
        total_nets = 0
        net_items = []

    if total_comps > 10 and total_nets > 0 and total_comps / total_nets > 10:
        ctx.anomalies["high_comp_net_ratio"].append((name, f"comps={total_comps} nets={total_nets} ratio={total_comps/total_nets:.1f}"))

    if total_comps > 5 and total_nets == 0:
        ctx.anomalies["comps_but_no_nets"].append((name, f"{total_comps} components but 0 nets"))

    for net in net_items:
        if isinstance(net, dict):
            pin_count = net.get("pin_count", len(net.get("pins", [])))
            net_name = net.get("name", "?")
        else:
            continue
        if pin_count > 500:
            ctx.anomalies["huge_net"].append((name, f"net '{net_name}' has {pin_count} pins"))


def validate_findings(ctx, name, data):
    """Check findings plausibility for modern files."""
    findings = data.get("findings", [])
    if not isinstance(findings, list):
        return

    # Group findings by detector for per-detector counts
    grouped = {}
    for f in findings:
        det = f.get("detector", "")
        if det:
            grouped.setdefault(det, []).append(f)

    for det, items in grouped.items():
        if len(items) > 200:
            ctx.anomalies["signal_explosion"].append((name, f"findings[{det}] has {len(items)} entries"))

    # Check decoupling findings count
    decoupling = grouped.get("detect_decoupling_analysis", [])
    if decoupling:
        ics = len(decoupling)
        if ics > 200:
            ctx.anomalies["decoupling_explosion"].append((name, f"decoupling analyzed {ics} ICs"))


def validate_design_analysis(ctx, name, data):
    """Check design analysis plausibility."""
    if "design_analysis" not in data:
        return

    da = data["design_analysis"]
    erc = da.get("erc_warnings", [])
    if isinstance(erc, list) and len(erc) > 100:
        ctx.anomalies["many_erc_warnings"].append((name, f"{len(erc)} ERC warnings"))


def validate_new_sections(ctx, name, data):
    """Validate the new Tier 1/2 analysis sections."""
    aa = data.get("annotation_issues", {})
    if isinstance(aa, dict):
        dupes = aa.get("duplicate_references", [])
        if isinstance(dupes, list) and len(dupes) > 20:
            ctx.anomalies["many_annotation_dupes"].append((name, f"{len(dupes)} duplicate refs"))

    wg = data.get("wire_geometry", {})
    if isinstance(wg, dict):
        diag = wg.get("diagonal_wires", 0)
        if isinstance(diag, list):
            diag = len(diag)
        total_wires = wg.get("total_wires", 1)
        if isinstance(total_wires, list):
            total_wires = len(total_wires)
        if isinstance(diag, (int, float)) and isinstance(total_wires, (int, float)) and total_wires > 0 and diag / max(total_wires, 1) > 0.5:
            ctx.anomalies["many_diagonal_wires"].append((name, f"{diag}/{total_wires} diagonal"))

    pi = data.get("property_issues", {})
    if isinstance(pi, dict):
        value_eq_ref = pi.get("value_equals_reference", [])
        if isinstance(value_eq_ref, list) and len(value_eq_ref) > 20:
            ctx.anomalies["many_value_eq_ref"].append((name, f"{len(value_eq_ref)} value==reference"))

    gd = data.get("ground_domains", {})
    if isinstance(gd, dict):
        domains = gd.get("domains", [])
        if len(domains) > 10:
            ctx.anomalies["many_ground_domains"].append((name, f"{len(domains)} ground domains"))


_DESIGN_INTENT_REQUIRED = {"product_class", "ipc_class", "target_market",
                           "confidence", "detection_signals", "source"}
_PRODUCT_CLASSES = {"prototype", "production"}
_TARGET_MARKETS = {"hobby", "consumer", "industrial", "medical",
                   "automotive", "aerospace"}


def validate_design_intent(ctx, name, data):
    """Check design_intent section structure and value constraints."""
    di = data.get("design_intent")
    if di is None:
        return  # absent is OK for legacy/empty files
    if not isinstance(di, dict):
        ctx.anomalies["design_intent_not_dict"].append((name, f"type={type(di).__name__}"))
        return

    for field in _DESIGN_INTENT_REQUIRED:
        if field not in di:
            ctx.anomalies["design_intent_missing_field"].append((name, f"missing '{field}'"))

    ipc = di.get("ipc_class")
    if ipc is not None and ipc not in (1, 2, 3):
        ctx.anomalies["design_intent_bad_ipc"].append((name, f"ipc_class={ipc!r}"))

    pc = di.get("product_class")
    if pc is not None and pc not in _PRODUCT_CLASSES:
        ctx.anomalies["design_intent_bad_product_class"].append((name, f"product_class={pc!r}"))

    tm = di.get("target_market")
    if tm is not None and tm not in _TARGET_MARKETS:
        ctx.anomalies["design_intent_bad_target_market"].append((name, f"target_market={tm!r}"))

    conf = di.get("confidence")
    if conf is not None:
        if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
            ctx.anomalies["design_intent_bad_confidence"].append((name, f"confidence={conf!r}"))

    ds = di.get("detection_signals")
    if ds is not None and not isinstance(ds, list):
        ctx.anomalies["design_intent_bad_signals"].append((name, f"type={type(ds).__name__}"))

    src = di.get("source")
    if src is not None and not isinstance(src, dict):
        ctx.anomalies["design_intent_bad_source"].append((name, f"type={type(src).__name__}"))


def _validate_schematics(schematics):
    """Validate a list of schematic paths. Worker function for parallel execution.

    Returns (stats_dict, anomalies_dict) where anomalies is {category: [(file, detail)]}.
    """
    ctx = ValidationContext()
    repos_dir = str(REPOS_DIR)

    for sch_path in schematics:
        relpath = sch_path
        if sch_path.startswith(repos_dir):
            relpath = sch_path[len(repos_dir):].lstrip("/").lstrip(os.sep)

        # Determine owner/repo and within-repo safe name
        parts = relpath.replace("\\", "/").split("/", 2)
        if len(parts) < 3:
            continue
        owner = parts[0]
        repo = parts[1]
        within_repo = parts[2]
        safe_name = _truncate_with_hash(within_repo.replace(os.sep, "_").replace("/", "_"))

        # Look for output in per-repo dir (owner/repo structure)
        json_path = OUTPUTS_DIR / "schematic" / owner / repo / f"{safe_name}.json"

        if not json_path.exists():
            ctx.anomalies["missing_result"].append((sch_path, "no JSON output"))
            continue

        try:
            data = load_result(json_path)
        except (json.JSONDecodeError, OSError) as e:
            ctx.anomalies["invalid_json"].append((str(json_path), str(e)))
            continue

        name = os.path.basename(sch_path)
        is_modern = sch_path.endswith(".kicad_sch")

        stat_section = data.get("statistics", data.get("summary", {}))
        total_comps = stat_section.get("total_components", len(data.get("components", [])))

        validate_structural(ctx, name, data, is_modern)
        validate_components(ctx, name, data)
        validate_nets(ctx, name, data, total_comps)
        validate_findings(ctx, name, data)
        validate_design_analysis(ctx, name, data)
        validate_design_intent(ctx, name, data)
        if is_modern and total_comps > 0:
            validate_new_sections(ctx, name, data)

    return dict(ctx.stats), dict(ctx.anomalies)


def _validate_repo_schematics(repo_schematics_pair):
    """Validate schematics for a single repo. Picklable top-level worker."""
    _repo, schematics = repo_schematics_pair
    return _validate_schematics(schematics)


def _merge_results(all_stats, all_anomalies, stats, anomalies):
    """Merge per-repo stats and anomalies into accumulators."""
    for k, v in stats.items():
        all_stats[k] = all_stats.get(k, 0) + v
    for cat, items in anomalies.items():
        all_anomalies.setdefault(cat, []).extend(items)


def main():
    parser = argparse.ArgumentParser(description="Validate analyzer JSON outputs")
    add_repo_filter_args(parser)
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel workers (default: {DEFAULT_JOBS})")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    repos = resolve_repos(args)
    if repos is None:
        repos = list_repos()

    schematics_list = MANIFESTS_DIR / "all_schematics.txt"

    if not schematics_list.exists():
        print(f"Error: {schematics_list} not found. Run discover.py first.")
        sys.exit(1)

    with open(schematics_list) as f:
        all_schematics = [line.strip() for line in f if line.strip()]

    # Group schematics by repo
    repos_dir = str(REPOS_DIR)
    repo_set = set(repos)
    by_repo = defaultdict(list)
    for s in all_schematics:
        relpath = s
        if s.startswith(repos_dir):
            relpath = s[len(repos_dir):].lstrip("/").lstrip(os.sep)
        parts = relpath.replace("\\", "/").split("/")
        if len(parts) >= 2:
            repo_name = f"{parts[0]}/{parts[1]}"
        else:
            repo_name = parts[0]
        if repo_name in repo_set:
            by_repo[repo_name].append(s)

    total_schematics = sum(len(v) for v in by_repo.values())
    print(f"Validating {total_schematics} schematics across {len(by_repo)} repos...")
    print()

    all_stats = {}
    all_anomalies = {}
    jobs = args.jobs
    work_items = list(by_repo.items())

    if jobs > 1 and len(work_items) > 1:
        with ProcessPoolExecutor(max_workers=min(jobs, len(work_items))) as pool:
            futures = {pool.submit(_validate_repo_schematics, item): item[0]
                       for item in work_items}
            for future in as_completed(futures):
                stats, anomalies = future.result()
                _merge_results(all_stats, all_anomalies, stats, anomalies)
    else:
        for item in work_items:
            stats, anomalies = _validate_repo_schematics(item)
            _merge_results(all_stats, all_anomalies, stats, anomalies)

    # Report
    if args.json:
        output = {
            "stats": all_stats,
            "anomaly_count": sum(len(v) for v in all_anomalies.values()),
            "anomaly_categories": len(all_anomalies),
            "anomalies": {cat: [{"file": n, "detail": d} for n, d in items]
                          for cat, items in all_anomalies.items()},
        }
        print(json.dumps(output, indent=2))
        return

    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total schematics: {all_stats.get('total', 0)}")
    print(f"Modern: {all_stats.get('modern', 0)}  Legacy: {all_stats.get('legacy', 0)}")
    print(f"Modern with components: {all_stats.get('modern_with_comps', 0)}")
    print(f"Total components: {all_stats.get('total_components', 0):,}")
    print(f"Total nets: {all_stats.get('total_nets', 0):,}")
    print(f"Zero-component files: {all_stats.get('zero_comp', 0)}")
    print(f"Zero-net files: {all_stats.get('zero_net', 0)}")
    print()

    if not all_anomalies:
        print("NO ANOMALIES FOUND")
        return

    print(f"ANOMALIES ({sum(len(v) for v in all_anomalies.values())} total across {len(all_anomalies)} categories):")
    print()

    for cat in sorted(all_anomalies.keys()):
        items = all_anomalies[cat]
        print(f"--- {cat} ({len(items)}) ---")
        for name, detail in items[:10]:
            print(f"  {name}: {detail}")
        if len(items) > 10:
            print(f"  ... and {len(items) - 10} more")
        print()


if __name__ == "__main__":
    main()
