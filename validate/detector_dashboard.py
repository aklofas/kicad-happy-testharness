#!/usr/bin/env python3
"""Detector coverage dashboard — field-level statistics across the corpus.

For each signal detector, reports file hits, field presence %, enum value
distributions, and flags unknown values or low-presence fields.

Usage:
    python3 validate/detector_dashboard.py
    python3 validate/detector_dashboard.py --detector motor_drivers
    python3 validate/detector_dashboard.py --json
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from utils import OUTPUTS_DIR, safe_load_json
from seed import _DETECTOR_FIELD_SPECS


def collect_detector_stats(detector_filter=None):
    """Scan all schematic outputs and collect per-detector field statistics.

    Returns {detector: {files, items, fields: {field: count}, enums: {field: {val: count}}}}.
    """
    sch_dir = OUTPUTS_DIR / "schematic"
    if not sch_dir.exists():
        return {}

    stats = defaultdict(lambda: {
        "files": 0, "items": 0,
        "fields": defaultdict(int),
        "enums": defaultdict(lambda: defaultdict(int)),
        "numerics": defaultdict(list),
    })

    for owner_dir in sorted(sch_dir.iterdir()):
        if not owner_dir.is_dir():
            continue
        for repo_dir in owner_dir.iterdir():
            if not repo_dir.is_dir():
                continue
            for f in repo_dir.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                except Exception:
                    continue
                sa = data.get("signal_analysis", {})
                for det, items in sa.items():
                    if detector_filter and det != detector_filter:
                        continue
                    if not isinstance(items, list) or not items:
                        continue
                    s = stats[det]
                    s["files"] += 1
                    s["items"] += len(items)
                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        for field, val in item.items():
                            s["fields"][field] += 1
                            if isinstance(val, str):
                                s["enums"][field][val] += 1
                            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                                s["numerics"][field].append(val)

    return dict(stats)


def format_report(stats, detector_filter=None):
    """Format detector stats as text report."""
    lines = []
    total_files = 0
    for det in sorted(stats):
        s = stats[det]
        total_files = max(total_files, s["files"])

    for det in sorted(stats, key=lambda d: -stats[d]["files"]):
        s = stats[det]
        spec = _DETECTOR_FIELD_SPECS.get(det, {})
        lines.append(f"\n{'='*60}")
        lines.append(f"{det} — {s['files']} files, {s['items']} items")
        lines.append(f"{'='*60}")

        # Field presence
        lines.append(f"\n  Fields (presence in {s['items']} items):")
        for field in sorted(s["fields"], key=lambda f: -s["fields"][f]):
            count = s["fields"][field]
            pct = count * 100 / s["items"] if s["items"] else 0
            marker = ""
            if field in spec.get("required_fields", []) and pct < 100:
                marker = " *** LOW (required)"
            lines.append(f"    {field:35s} {count:6d} ({pct:5.1f}%){marker}")

        # Enum distributions
        enum_fields = spec.get("enum_fields", {})
        for field in sorted(s["enums"]):
            vals = s["enums"][field]
            if len(vals) > 20:
                continue  # Skip high-cardinality fields (refs, nets, etc.)
            lines.append(f"\n  {field} values:")
            allowed = set(enum_fields.get(field, []))
            for val, count in sorted(vals.items(), key=lambda x: -x[1]):
                flag = ""
                if allowed and val not in allowed:
                    flag = " *** UNKNOWN"
                lines.append(f"    {val:40s} {count:6d}{flag}")

        # Numeric ranges
        for field in sorted(s["numerics"]):
            vals = s["numerics"][field]
            if len(vals) < 3:
                continue
            vals_sorted = sorted(vals)
            median = vals_sorted[len(vals_sorted) // 2]
            lines.append(f"\n  {field} range: min={vals_sorted[0]}, "
                         f"median={median}, max={vals_sorted[-1]} "
                         f"(n={len(vals)})")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Detector coverage dashboard — field-level corpus statistics")
    parser.add_argument("--detector", help="Show only this detector")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    stats = collect_detector_stats(detector_filter=args.detector)

    if not stats:
        print("No detector data found. Run schematic analysis first.")
        sys.exit(1)

    if args.json:
        # Convert defaultdicts to regular dicts for JSON serialization
        out = {}
        for det, s in stats.items():
            out[det] = {
                "files": s["files"],
                "items": s["items"],
                "fields": dict(s["fields"]),
                "enums": {k: dict(v) for k, v in s["enums"].items()},
                "numeric_ranges": {
                    k: {"min": min(v), "max": max(v), "count": len(v)}
                    for k, v in s["numerics"].items() if v
                },
            }
        print(json.dumps(out, indent=2))
        return

    print(f"Detector Dashboard — {len(stats)} detectors")
    print(format_report(stats, args.detector))

    # Summary warnings
    warnings = []
    for det, s in stats.items():
        spec = _DETECTOR_FIELD_SPECS.get(det, {})
        for field in spec.get("required_fields", []):
            count = s["fields"].get(field, 0)
            pct = count * 100 / s["items"] if s["items"] else 0
            if pct < 95:
                warnings.append(f"  {det}.{field}: {pct:.0f}% presence (required)")
        for field, allowed in spec.get("enum_fields", {}).items():
            for val in s["enums"].get(field, {}):
                if val not in allowed:
                    warnings.append(f"  {det}.{field}: unknown value '{val}'")

    if warnings:
        print(f"\n{'!'*60}")
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(w)


if __name__ == "__main__":
    main()
