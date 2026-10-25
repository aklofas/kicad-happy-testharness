"""Compact baseline projection of analyzer outputs.

`extract_manifest_entry` reduces one analyzer JSON output to the summary the
baselines under reference/ store (snapshot.py writes it, compare.py diffs it).
The findings-level diff lives in regression_diff.py.
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import resolve_path


def _count_at_path(data, path):
    """Count items at a path — length if list/dict, value if int, 0 if missing."""
    val = resolve_path(data, path)
    if val is None:
        return 0
    if isinstance(val, (list, dict)):
        return len(val)
    if isinstance(val, (int, float)):
        return int(val)
    return 0


def _component_type_distribution(data):
    """Get component type counts from analyzer output."""
    components = data.get("components", [])
    types = Counter()
    for c in components:
        ref = c.get("reference", "")
        if ref.startswith("#"):
            continue
        ctype = c.get("type", "unknown")
        types[ctype] += 1
    return dict(types)


def extract_manifest_entry(data, analyzer_type):
    """Extract a compact manifest entry from full analyzer output.

    This is what gets checked into git as the baseline — just the
    essential facts, not the full output.
    """
    if analyzer_type == "schematic":
        stats = data.get("statistics", {})
        da = data.get("design_analysis", {})

        signal_counts = {}
        for finding in data.get("findings", []):
            det = finding.get("detector", "")
            if det:
                signal_counts[det] = signal_counts.get(det, 0) + 1

        type_dist = _component_type_distribution(data)
        sections = sorted(k for k in data.keys() if k != "file")
        bom = data.get("bom", [])

        return {
            "total_components": stats.get("total_components", 0),
            "total_nets": stats.get("total_nets", 0),
            "total_labels": stats.get("total_labels", 0),
            "total_power_symbols": stats.get("total_power_symbols", 0),
            "signal_counts": signal_counts,
            "erc_warning_count": _count_at_path(data, "design_analysis.erc_warnings"),
            "component_types": type_dist,
            "bom_lines": len(bom) if isinstance(bom, list) else 0,
            "sections": sections,
        }

    elif analyzer_type == "pcb":
        stats = data.get("statistics", data.get("summary", {}))
        return {
            "total_footprints": stats.get("total_footprints", 0),
            "total_tracks": stats.get("total_tracks", 0),
            "total_vias": stats.get("total_vias", 0),
            "total_zones": stats.get("total_zones", 0),
            "sections": sorted(k for k in data.keys() if k != "file"),
        }

    elif analyzer_type == "gerber":
        return {
            "layers": len(data.get("layers", [])),
            "drill_files": len(data.get("drill_files", [])),
            "sections": sorted(k for k in data.keys() if k != "file"),
        }

    elif analyzer_type == "spice":
        summary = data.get("summary", {})
        by_type = {}
        for r in data.get("simulation_results", []):
            t = r.get("subcircuit_type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        total = summary.get("total", 0)
        return {
            "total_sims": total,
            "pass": summary.get("pass", 0),
            "warn": summary.get("warn", 0),
            "fail": summary.get("fail", 0),
            "skip": summary.get("skip", 0),
            "pass_rate": round(summary.get("pass", 0) / total * 100, 1) if total else 0,
            "by_type": by_type,
        }

    elif analyzer_type == "emc":
        summary = data.get("summary", {})
        by_category = {}
        for f in data.get("findings", []):
            cat = f.get("category", "other")
            by_category[cat] = by_category.get(cat, 0) + 1
        entry = {
            "total_findings": summary.get("total_checks", 0),
            "critical": summary.get("critical", 0),
            "high": summary.get("high", 0),
            "medium": summary.get("medium", 0),
            "low": summary.get("low", 0),
            "emc_risk_score": summary.get("emc_risk_score", 0),
            "target_standard": data.get("target_standard", ""),
            "by_category": by_category,
        }
        by_sev = summary.get("by_severity")
        if isinstance(by_sev, dict):
            entry["by_severity"] = by_sev
        return entry

    elif analyzer_type == "datasheets":
        parts = data.get("parts", {})
        by_cat = {}
        for info in parts.values():
            cat = info.get("category", "unknown")
            by_cat[cat] = by_cat.get(cat, 0) + 1
        return {
            "total_parts": data.get("total_parts", 0),
            "downloaded": data.get("downloaded", 0),
            "extracted": data.get("extracted", 0),
            "sufficient": data.get("sufficient", 0),
            "stale": data.get("stale", 0),
            "avg_score": data.get("avg_score", 0),
            "by_category": by_cat,
        }

    elif analyzer_type == "thermal":
        summary = data.get("summary", {})
        entry = {
            "components_analyzed": summary.get("components_analyzed", 0),
            "thermal_score": summary.get("thermal_score", 0),
            "total_findings": summary.get("total_findings", summary.get("total_checks", 0)),
            "critical": summary.get("critical", 0),
            "high": summary.get("high", 0),
            "medium": summary.get("medium", 0),
            "low": summary.get("low", 0),
        }
        by_sev = summary.get("by_severity")
        if isinstance(by_sev, dict):
            entry["by_severity"] = by_sev
        return entry

    return {}
