#!/usr/bin/env python3
"""Property-based invariant checker for analyzer outputs.

Checks mathematical and structural invariants that must always hold:
- Voltage divider ratio: 0 < ratio < 1
- RC filter cutoff: cutoff_hz > 0 (when R > 0 and C > 0)
- LC filter resonance: resonant_hz > 0 (when L > 0 and C > 0)
- Crystal: effective_load_pF > 0
- Confidence taxonomy: must be in {deterministic, heuristic, datasheet-backed}
- Evidence source taxonomy: must be in {datasheet, topology, heuristic_rule, symbol_footprint, bom, geometry, api_lookup}
- trust_summary: shape, totals, and enum validity when present
- Component count: total_components >= sum of component_types counts
- No unexpected duplicate component refs

Usage:
    python3 validate/validate_invariants.py                          # all types, all repos
    python3 validate/validate_invariants.py --type schematic         # schematic only
    python3 validate/validate_invariants.py --type thermal --repo X  # thermal, one repo
    python3 validate/validate_invariants.py --type all --cross-section smoke
    python3 validate/validate_invariants.py --summary
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (list_repos,
                   DEFAULT_JOBS, add_repo_filter_args, resolve_repos,
                   iter_output_files)


def check_invariants(data, filepath=""):
    """Check invariants on an analyzer output dict.

    Returns a list of (filepath, violation_description) tuples.
    Null values are skipped (not flagged).
    """
    violations = []

    def _add(desc):
        violations.append((filepath, desc))

    # Group findings by detector
    grouped = {}
    for f in data.get("findings", []):
        det = f.get("detector", "")
        if det:
            grouped.setdefault(det, []).append(f)

    # --- Voltage divider ratio: 0 < ratio < 1 ---
    for i, vd in enumerate(grouped.get("detect_voltage_dividers", [])):
        ratio = vd.get("ratio")
        if ratio is None:
            continue
        if ratio <= 0:
            _add(f"voltage_dividers[{i}].ratio={ratio} <= 0")
        if ratio >= 1:
            _add(f"voltage_dividers[{i}].ratio={ratio} >= 1")

    # --- RC filter cutoff_hz > 0 ---
    for i, rc in enumerate(grouped.get("detect_rc_filters", [])):
        cutoff = rc.get("cutoff_hz")
        if cutoff is None:
            continue
        if cutoff <= 0:
            _add(f"rc_filters[{i}].cutoff_hz={cutoff} <= 0")

    # --- LC filter resonant_hz > 0 ---
    for i, lc in enumerate(grouped.get("detect_lc_filters", [])):
        resonant = lc.get("resonant_hz")
        if resonant is None:
            continue
        if resonant <= 0:
            _add(f"lc_filters[{i}].resonant_hz={resonant} <= 0")

    # --- Crystal effective_load_pF > 0 ---
    for i, xtal in enumerate(grouped.get("detect_crystal_circuits", [])):
        load = xtal.get("effective_load_pF")
        if load is None:
            continue
        if load <= 0:
            _add(f"crystal_circuits[{i}].effective_load_pF={load} <= 0")

    # --- Confidence taxonomy: must be in declared set when present ---
    VALID_CONFIDENCES = {"deterministic", "heuristic", "datasheet-backed"}
    for i, finding in enumerate(data.get("findings", [])):
        conf = finding.get("confidence")
        if conf is not None and conf not in VALID_CONFIDENCES:
            det = finding.get("detector", "?")
            _add(f"findings[{i}] ({det}).confidence='{conf}' "
                 f"not in {VALID_CONFIDENCES}")

    # --- Evidence source taxonomy: must be in declared set when present ---
    VALID_EVIDENCE_SOURCES = {"datasheet", "topology", "heuristic_rule",
                              "symbol_footprint", "bom", "geometry", "api_lookup"}
    for i, finding in enumerate(data.get("findings", [])):
        ev = finding.get("evidence_source")
        if ev is not None and ev not in VALID_EVIDENCE_SOURCES:
            det = finding.get("detector", "?")
            _add(f"findings[{i}] ({det}).evidence_source='{ev}' "
                 f"not in {VALID_EVIDENCE_SOURCES}")

    # --- Provenance structure: when present, must have valid shape ---
    PROV_REQUIRED = {"evidence", "confidence", "claimed_components",
                     "excluded_by", "suppressed_candidates"}
    for i, finding in enumerate(data.get("findings", [])):
        prov = finding.get("provenance")
        if prov is None:
            continue
        if not isinstance(prov, dict):
            det = finding.get("detector", "?")
            _add(f"findings[{i}] ({det}).provenance is not a dict")
            continue
        det = finding.get("detector", "?")
        for key in PROV_REQUIRED:
            if key not in prov:
                _add(f"findings[{i}] ({det}).provenance missing '{key}'")
        pconf = prov.get("confidence", "")
        if pconf and pconf not in VALID_CONFIDENCES:
            _add(f"findings[{i}] ({det}).provenance.confidence='{pconf}' "
                 f"not in {VALID_CONFIDENCES}")
        pev = prov.get("evidence")
        if pev is not None and (not isinstance(pev, str) or not pev):
            _add(f"findings[{i}] ({det}).provenance.evidence is empty/non-string")
        for lk in ("claimed_components", "excluded_by", "suppressed_candidates"):
            val = prov.get(lk)
            if val is not None and not isinstance(val, list):
                _add(f"findings[{i}] ({det}).provenance.{lk} is not a list")

    # --- Every net referenced in findings exists in extracted nets ---
    nets = data.get("nets", {})
    if isinstance(nets, dict):
        net_names = set(nets.keys())
    elif isinstance(nets, list):
        net_names = {n.get("name", "") for n in nets if isinstance(n, dict)}
    else:
        net_names = set()

    if net_names and grouped:
        for det_name, items in grouped.items():
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                for field, val in item.items():
                    if field.endswith("_net") and isinstance(val, str) and val:
                        if val not in net_names:
                            _add(f"{det_name}[{i}].{field}='{val}' not in nets")

    # --- total_components >= len(components) ---
    components = data.get("components", [])
    stats = data.get("statistics", {})
    total = stats.get("total_components")
    if total is not None and len(components) > total:
        _add(f"len(components)={len(components)} > total_components={total}")

    # --- Component count: total_components >= sum(component_types) ---
    stats = data.get("statistics", {})
    total = stats.get("total_components")
    comp_types = stats.get("component_types")
    if total is not None and isinstance(comp_types, dict):
        type_sum = sum(v for v in comp_types.values() if isinstance(v, (int, float)))
        if type_sum > total:
            _add(f"component_types sum ({type_sum}) > total_components ({total})")

    # --- Duplicate component refs (excluding known annotation issues) ---
    components = data.get("components", [])
    if components:
        # Gather known duplicate refs from annotation_issues
        aa = data.get("annotation_issues", {})
        known_dupes = set()
        if isinstance(aa, dict):
            for ref in aa.get("duplicate_references", []):
                if isinstance(ref, str):
                    known_dupes.add(ref)
                elif isinstance(ref, dict):
                    r = ref.get("reference", "")
                    if r:
                        known_dupes.add(r)

        # Count refs (skip power symbols and unassigned)
        ref_counts = defaultdict(int)
        for comp in components:
            ref = comp.get("reference", "")
            if ref and ref != "?" and not ref.startswith("#"):
                ref_counts[ref] += 1

        for ref, count in sorted(ref_counts.items()):
            if count > 1 and ref not in known_dupes:
                _add(f"duplicate ref '{ref}' appears {count} times "
                     f"(not in annotation_issues)")

    # --- trust_summary: when present, must have valid shape ---
    VALID_TRUST_LEVELS = {"high", "mixed", "low"}
    ts = data.get("trust_summary")
    if ts is not None:
        if not isinstance(ts, dict):
            _add("trust_summary is not a dict")
        else:
            findings_count = len(data.get("findings", []))
            ts_total = ts.get("total_findings")
            if ts_total is not None and ts_total != findings_count:
                _add(f"trust_summary.total_findings={ts_total} "
                     f"!= len(findings)={findings_count}")

            tl = ts.get("trust_level")
            if tl is not None and tl not in VALID_TRUST_LEVELS:
                _add(f"trust_summary.trust_level='{tl}' "
                     f"not in {VALID_TRUST_LEVELS}")

            by_conf = ts.get("by_confidence")
            if isinstance(by_conf, dict):
                if set(by_conf.keys()) != VALID_CONFIDENCES:
                    _add(f"trust_summary.by_confidence keys "
                         f"{set(by_conf.keys())} != {VALID_CONFIDENCES}")
                conf_sum = sum(by_conf.values()) + ts.get("unknown_confidence", 0)
                if ts_total is not None and conf_sum != ts_total:
                    _add(f"trust_summary by_confidence sum ({conf_sum}) "
                         f"!= total_findings ({ts_total})")

            by_ev = ts.get("by_evidence_source")
            if isinstance(by_ev, dict):
                if set(by_ev.keys()) != VALID_EVIDENCE_SOURCES:
                    _add(f"trust_summary.by_evidence_source keys "
                         f"{set(by_ev.keys())} != {VALID_EVIDENCE_SOURCES}")
                ev_sum = sum(by_ev.values()) + ts.get("unknown_evidence_source", 0)
                if ts_total is not None and ev_sum != ts_total:
                    _add(f"trust_summary by_evidence_source sum ({ev_sum}) "
                         f"!= total_findings ({ts_total})")

            prov_pct = ts.get("provenance_coverage_pct")
            if prov_pct is not None and not (0 <= prov_pct <= 100):
                _add(f"trust_summary.provenance_coverage_pct={prov_pct} "
                     f"not in [0, 100]")

            bom_cov = ts.get("bom_coverage")
            if isinstance(bom_cov, dict):
                for pct_key in ("mpn_pct", "datasheet_pct"):
                    pct = bom_cov.get(pct_key)
                    if pct is not None and not (0 <= pct <= 100):
                        _add(f"trust_summary.bom_coverage.{pct_key}={pct} "
                             f"not in [0, 100]")

            # --- trust_level threshold consistency ---
            if ts_total and ts_total > 0 and by_conf is not None:
                heu_pct = 100 * by_conf.get("heuristic", 0) / ts_total
                unk = ts.get("unknown_confidence", 0)
                expected_level = ("low" if (heu_pct > 50 or unk > 0)
                                  else "mixed" if heu_pct > 20
                                  else "high")
                if tl and tl != expected_level:
                    _add(f"trust_summary.trust_level='{tl}' but expected "
                         f"'{expected_level}' (heu={heu_pct:.1f}%, unk={unk})")

            # --- provenance_coverage_pct cross-check ---
            if prov_pct is not None and ts_total is not None:
                findings = data.get("findings", [])
                actual_prov = sum(1 for f in findings
                                 if isinstance(f, dict) and "provenance" in f)
                expected_pct = (round(100 * actual_prov / ts_total, 1)
                                if ts_total else 100.0)
                if abs(prov_pct - expected_pct) > 0.2:
                    _add(f"trust_summary.provenance_coverage_pct={prov_pct} "
                         f"but actual={expected_pct}%")

            # --- BOM coverage cross-check ---
            if bom_cov is not None:
                bom = data.get("bom", data.get("components", []))
                actual_total = sum(
                    1 for c in bom if isinstance(c, dict)
                    and c.get("type") not in
                    ("power_symbol", "power_flag", "flag"))
                reported_total = bom_cov.get("total_components", 0)
                if actual_total != reported_total:
                    _add(f"trust_summary.bom_coverage.total_components="
                         f"{reported_total} but actual={actual_total}")

    return violations


def _check_file(json_path):
    """Load a JSON output and check invariants. Returns list of violations."""
    try:
        with open(json_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    return check_invariants(data, filepath=str(json_path))


def _check_type_batch(work_item):
    """Check all output files for a (type, repo) pair. Picklable worker."""
    output_type, repo_name, file_paths = work_item
    all_violations = []
    for json_path in file_paths:
        all_violations.extend(_check_file(json_path))
    return output_type, repo_name, all_violations


VALID_TYPES = ("schematic", "pcb", "emc", "thermal", "gerber")


def main():
    parser = argparse.ArgumentParser(
        description="Check mathematical/structural invariants in analyzer outputs")
    add_repo_filter_args(parser)
    parser.add_argument("--type", "-t", default="all",
                        choices=list(VALID_TYPES) + ["all"],
                        help="Output type to check (default: all)")
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel workers (default: {DEFAULT_JOBS})")
    parser.add_argument("--summary", action="store_true",
                        help="Show only summary counts, not individual violations")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    repos = resolve_repos(args)
    if repos is None:
        repos = list_repos()

    types_to_check = VALID_TYPES if args.type == "all" else (args.type,)

    # Collect work items: (type, repo, [json_paths])
    by_repo = defaultdict(lambda: defaultdict(list))
    total_files = 0
    for otype in types_to_check:
        for json_path, repo_name in iter_output_files(otype, repos):
            by_repo[otype][repo_name].append(json_path)
            total_files += 1

    work_items = []
    for otype in types_to_check:
        for repo_name, paths in sorted(by_repo[otype].items()):
            work_items.append((otype, repo_name, paths))

    all_violations = []
    violations_by_repo = {}
    jobs = args.jobs

    if jobs > 1 and len(work_items) > 1:
        with ProcessPoolExecutor(max_workers=min(jobs, len(work_items))) as pool:
            futures = {pool.submit(_check_type_batch, item): item
                       for item in work_items}
            for future in as_completed(futures):
                otype, repo, viols = future.result()
                if viols:
                    key = f"{otype}:{repo}"
                    violations_by_repo[key] = viols
                    all_violations.extend(viols)
    else:
        for item in work_items:
            otype, repo, viols = _check_type_batch(item)
            if viols:
                key = f"{otype}:{repo}"
                violations_by_repo[key] = viols
                all_violations.extend(viols)

    # Categorize violations
    categories = defaultdict(int)
    for _fp, desc in all_violations:
        if "voltage_dividers" in desc:
            categories["voltage_divider_ratio"] += 1
        elif "rc_filters" in desc:
            categories["rc_filter_cutoff"] += 1
        elif "lc_filters" in desc:
            categories["lc_filter_resonance"] += 1
        elif "crystal_circuits" in desc:
            categories["crystal_load"] += 1
        elif "component_types sum" in desc:
            categories["component_count"] += 1
        elif "duplicate ref" in desc:
            categories["duplicate_ref"] += 1
        elif "evidence_source" in desc:
            categories["evidence_source"] += 1
        elif "trust_summary" in desc:
            categories["trust_summary"] += 1
        else:
            categories["other"] += 1

    if args.json:
        output = {
            "types_checked": list(types_to_check),
            "files_checked": total_files,
            "repos_checked": len(set(r for _, r, _ in work_items)),
            "total_violations": len(all_violations),
            "repos_with_violations": len(violations_by_repo),
            "categories": dict(categories),
            "violations": [{"file": fp, "description": desc}
                           for fp, desc in all_violations],
        }
        print(json.dumps(output, indent=2))
        return

    type_label = ", ".join(types_to_check)
    print(f"Checked {total_files} files ({type_label}) across "
          f"{len(set(r for _, r, _ in work_items))} repos")
    print(f"Violations: {len(all_violations)} across "
          f"{len(violations_by_repo)} repos")
    print()

    if categories:
        print("By category:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count}")
        print()

    if all_violations and not args.summary:
        for key in sorted(violations_by_repo.keys()):
            viols = violations_by_repo[key]
            print(f"--- {key} ({len(viols)}) ---")
            for fp, desc in viols[:20]:
                short = os.path.basename(fp) if fp else "(unknown)"
                print(f"  {short}: {desc}")
            if len(viols) > 20:
                print(f"  ... and {len(viols) - 20} more")
            print()

    if not all_violations:
        print("NO INVARIANT VIOLATIONS")


if __name__ == "__main__":
    main()
