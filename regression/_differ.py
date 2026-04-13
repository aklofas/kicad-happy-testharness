"""Core semantic JSON diffing engine for analyzer outputs.

Compares two analyzer JSON outputs and produces structured deltas
that highlight new detections, lost detections, and changed values.
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


def _list_at_path(data, path):
    """Get list at path, or empty list."""
    val = resolve_path(data, path)
    if isinstance(val, list):
        return val
    return []


def _extract_identities(items, key_fields):
    """Extract identity strings from list items for stable matching."""
    identities = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        # Build identity from available key fields
        parts = []
        for kf in key_fields:
            val = item.get(kf)
            if val is not None:
                if isinstance(val, list):
                    parts.append(",".join(sorted(str(v) for v in val)))
                else:
                    parts.append(str(val))
        if parts:
            identity = "|".join(parts)
            identities[identity] = item
    return identities


def _diff_lists(baseline_items, current_items, key_fields):
    """Diff two lists of dicts using identity fields. Returns new/lost/kept counts."""
    base_ids = _extract_identities(baseline_items, key_fields)
    curr_ids = _extract_identities(current_items, key_fields)

    new_keys = set(curr_ids.keys()) - set(base_ids.keys())
    lost_keys = set(base_ids.keys()) - set(curr_ids.keys())
    kept_keys = set(base_ids.keys()) & set(curr_ids.keys())

    return {
        "new": [curr_ids[k] for k in sorted(new_keys)],
        "lost": [base_ids[k] for k in sorted(lost_keys)],
        "kept": len(kept_keys),
        "new_count": len(new_keys),
        "lost_count": len(lost_keys),
    }


def _diff_counts(baseline, current, paths):
    """Compare numeric counts at multiple paths."""
    deltas = {}
    for path in paths:
        bval = _count_at_path(baseline, path)
        cval = _count_at_path(current, path)
        if bval != cval:
            deltas[path] = {"baseline": bval, "current": cval, "delta": cval - bval}
    return deltas


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


def _diff_type_distribution(baseline_dist, current_dist):
    """Diff component type distributions."""
    all_types = set(baseline_dist.keys()) | set(current_dist.keys())
    changes = {}
    for t in sorted(all_types):
        bval = baseline_dist.get(t, 0)
        cval = current_dist.get(t, 0)
        if bval != cval:
            changes[t] = {"baseline": bval, "current": cval, "delta": cval - bval}
    return changes


def _top_level_sections(data):
    """Get set of top-level keys in analyzer output."""
    return set(data.keys())


# Identity fields for matching signal analysis items
SIGNAL_IDENTITY_FIELDS = {
    "voltage_dividers": ["components", "references"],
    "power_regulators": ["component", "reference"],
    "filters": ["components", "references"],
    "oscillators": ["components", "references"],
    "bus_protocols": ["protocol", "references"],
    "amplifiers": ["components", "references"],
    "adc_dac": ["component", "reference"],
    "protection_circuits": ["component", "reference", "type"],
    "pull_resistors": ["reference", "net"],
    "current_sensing": ["reference"],
    "differential_pairs": ["references"],
    "power_sequencing": ["reference"],
}


def diff_schematic(baseline, current):
    """Semantic diff of schematic analyzer outputs."""
    result = {
        "has_changes": False,
        "count_deltas": {},
        "signal_deltas": {},
        "design_deltas": {},
        "type_distribution_deltas": {},
        "section_deltas": {},
        "bom_delta": {},
    }

    # Count deltas
    count_paths = [
        "statistics.total_components",
        "statistics.total_nets",
        "statistics.total_labels",
        "statistics.total_power_symbols",
        "statistics.total_no_connects",
    ]
    result["count_deltas"] = _diff_counts(baseline, current, count_paths)

    # Signal analysis deltas
    base_sa = baseline.get("signal_analysis", {})
    curr_sa = current.get("signal_analysis", {})
    if isinstance(base_sa, dict) and isinstance(curr_sa, dict):
        all_keys = set(base_sa.keys()) | set(curr_sa.keys())
        for key in sorted(all_keys):
            base_items = base_sa.get(key, [])
            curr_items = curr_sa.get(key, [])
            if not isinstance(base_items, list) or not isinstance(curr_items, list):
                # Scalar or dict value — just compare counts
                bcount = len(base_items) if isinstance(base_items, (list, dict)) else (1 if base_items else 0)
                ccount = len(curr_items) if isinstance(curr_items, (list, dict)) else (1 if curr_items else 0)
                if bcount != ccount:
                    result["signal_deltas"][key] = {
                        "baseline_count": bcount,
                        "current_count": ccount,
                        "delta": ccount - bcount,
                    }
                continue

            id_fields = SIGNAL_IDENTITY_FIELDS.get(key, ["reference", "references", "component"])
            diff = _diff_lists(base_items, curr_items, id_fields)
            if diff["new_count"] > 0 or diff["lost_count"] > 0:
                result["signal_deltas"][key] = {
                    "baseline_count": len(base_items),
                    "current_count": len(curr_items),
                    "new_count": diff["new_count"],
                    "lost_count": diff["lost_count"],
                }

    # Design analysis deltas
    design_count_paths = [
        "design_analysis.erc_warnings",
        "annotation_issues.duplicate_references",
        "annotation_issues.unannotated_references",
        "property_issues.value_equals_reference",
        "sourcing_audit.components_with_mpn",
        "sourcing_audit.components_without_mpn",
    ]
    result["design_deltas"] = _diff_counts(baseline, current, design_count_paths)

    # Component type distribution
    base_dist = _component_type_distribution(baseline)
    curr_dist = _component_type_distribution(current)
    result["type_distribution_deltas"] = _diff_type_distribution(base_dist, curr_dist)

    # Section presence
    base_sections = _top_level_sections(baseline)
    curr_sections = _top_level_sections(current)
    new_sections = sorted(curr_sections - base_sections)
    lost_sections = sorted(base_sections - curr_sections)
    if new_sections or lost_sections:
        result["section_deltas"] = {
            "new": new_sections,
            "lost": lost_sections,
        }

    # BOM delta
    base_bom = baseline.get("bom", [])
    curr_bom = current.get("bom", [])
    if isinstance(base_bom, list) and isinstance(curr_bom, list):
        bom_diff = _diff_lists(base_bom, curr_bom, ["value", "footprint", "references"])
        if bom_diff["new_count"] > 0 or bom_diff["lost_count"] > 0:
            result["bom_delta"] = {
                "baseline_lines": len(base_bom),
                "current_lines": len(curr_bom),
                "new_lines": bom_diff["new_count"],
                "lost_lines": bom_diff["lost_count"],
            }

    # Check if anything changed
    result["has_changes"] = bool(
        result["count_deltas"] or result["signal_deltas"] or
        result["design_deltas"] or result["type_distribution_deltas"] or
        result["section_deltas"] or result["bom_delta"]
    )

    # Change score for prioritization
    score = 0
    score += len(result["count_deltas"]) * 2
    for sd in result["signal_deltas"].values():
        score += sd.get("new_count", 0) + sd.get("lost_count", 0)
    for dd in result["design_deltas"].values():
        score += abs(dd.get("delta", 0))
    score += len(result.get("section_deltas", {}).get("new", []))
    score += len(result.get("section_deltas", {}).get("lost", [])) * 3  # lost sections are worse
    result["change_score"] = score

    return result


def diff_pcb(baseline, current):
    """Semantic diff of PCB analyzer outputs."""
    result = {
        "has_changes": False,
        "count_deltas": {},
        "section_deltas": {},
    }

    count_paths = [
        "statistics.total_footprints",
        "statistics.total_tracks",
        "statistics.total_vias",
        "statistics.total_zones",
        "statistics.board_area_mm2",
        "statistics.layer_count",
    ]
    result["count_deltas"] = _diff_counts(baseline, current, count_paths)

    base_sections = _top_level_sections(baseline)
    curr_sections = _top_level_sections(current)
    new_sections = sorted(curr_sections - base_sections)
    lost_sections = sorted(base_sections - curr_sections)
    if new_sections or lost_sections:
        result["section_deltas"] = {"new": new_sections, "lost": lost_sections}

    result["has_changes"] = bool(result["count_deltas"] or result["section_deltas"])
    result["change_score"] = len(result["count_deltas"]) * 2 + len(new_sections) + len(lost_sections) * 3
    return result


def diff_gerber(baseline, current):
    """Semantic diff of Gerber analyzer outputs."""
    result = {
        "has_changes": False,
        "count_deltas": {},
    }

    # Gerber outputs vary, so do a flexible count
    for key in baseline.keys() | current.keys():
        bval = baseline.get(key)
        cval = current.get(key)
        if isinstance(bval, list) and isinstance(cval, list) and len(bval) != len(cval):
            result["count_deltas"][key] = {
                "baseline": len(bval), "current": len(cval), "delta": len(cval) - len(bval),
            }
        elif isinstance(bval, (int, float)) and isinstance(cval, (int, float)) and bval != cval:
            result["count_deltas"][key] = {
                "baseline": bval, "current": cval, "delta": cval - bval,
            }

    result["has_changes"] = bool(result["count_deltas"])
    result["change_score"] = len(result["count_deltas"]) * 2
    return result


def extract_manifest_entry(data, analyzer_type):
    """Extract a compact manifest entry from full analyzer output.

    This is what gets checked into git as the baseline — just the
    essential facts, not the full output.
    """
    if analyzer_type == "schematic":
        stats = data.get("statistics", {})
        sa = data.get("signal_analysis", {})
        da = data.get("design_analysis", {})

        signal_counts = {}
        if isinstance(sa, dict):
            for key, val in sa.items():
                if isinstance(val, list):
                    signal_counts[key] = len(val)
                elif isinstance(val, dict):
                    signal_counts[key] = len(val)

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
        return {
            "total_findings": summary.get("total_checks", 0),
            "critical": summary.get("critical", 0),
            "high": summary.get("high", 0),
            "medium": summary.get("medium", 0),
            "low": summary.get("low", 0),
            "emc_risk_score": summary.get("emc_risk_score", 0),
            "target_standard": data.get("target_standard", ""),
            "by_category": by_category,
        }

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
        return {
            "components_analyzed": summary.get("components_analyzed", 0),
            "thermal_score": summary.get("thermal_score", 0),
            "total_findings": summary.get("total_findings", summary.get("total_checks", 0)),
            "critical": summary.get("critical", 0),
            "high": summary.get("high", 0),
            "medium": summary.get("medium", 0),
            "low": summary.get("low", 0),
            "thermal_assessments": len(data.get("thermal_assessments", [])),
        }

    return {}
