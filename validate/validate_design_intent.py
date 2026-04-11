#!/usr/bin/env python3
"""Validate design_intent field in schematic and PCB analyzer outputs.

Checks that design_intent exists, has required fields with valid types/ranges,
and reports violations.

Usage:
    python3 validate/validate_design_intent.py
    python3 validate/validate_design_intent.py --repo owner/repo
    python3 validate/validate_design_intent.py --summary
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import OUTPUTS_DIR, list_repos, add_repo_filter_args, resolve_repos, iter_output_repos

VALID_PRODUCT_CLASSES = {"prototype", "production"}
VALID_IPC_CLASSES = {1, 2, 3}
VALID_TARGET_MARKETS = {"hobby", "consumer", "industrial", "medical", "automotive", "aerospace"}
NULLABLE_FIELDS = {
    "expected_lifetime_years", "operating_temp_range",
    "preferred_passive_size", "test_coverage_target",
    "approved_manufacturers",
}


def validate_design_intent(data, filepath=""):
    """Validate the design_intent field in an analyzer output dict.

    Returns a list of (filepath, issue_description) tuples.
    """
    issues = []

    if "design_intent" not in data:
        issues.append((filepath, "missing design_intent field"))
        return issues

    di = data["design_intent"]
    if not isinstance(di, dict):
        issues.append((filepath, f"design_intent is {type(di).__name__}, expected dict"))
        return issues

    # product_class
    pc = di.get("product_class")
    if pc is None:
        issues.append((filepath, "design_intent.product_class is missing"))
    elif not isinstance(pc, str):
        issues.append((filepath, f"design_intent.product_class is {type(pc).__name__}, expected str"))
    elif pc not in VALID_PRODUCT_CLASSES:
        issues.append((filepath, f"design_intent.product_class={pc!r}, expected one of {sorted(VALID_PRODUCT_CLASSES)}"))

    # ipc_class
    ipc = di.get("ipc_class")
    if ipc is None:
        issues.append((filepath, "design_intent.ipc_class is missing"))
    elif not isinstance(ipc, int):
        issues.append((filepath, f"design_intent.ipc_class is {type(ipc).__name__}, expected int"))
    elif ipc not in VALID_IPC_CLASSES:
        issues.append((filepath, f"design_intent.ipc_class={ipc}, expected one of {sorted(VALID_IPC_CLASSES)}"))

    # target_market
    tm = di.get("target_market")
    if tm is None:
        issues.append((filepath, "design_intent.target_market is missing"))
    elif not isinstance(tm, str):
        issues.append((filepath, f"design_intent.target_market is {type(tm).__name__}, expected str"))
    elif tm not in VALID_TARGET_MARKETS:
        issues.append((filepath, f"design_intent.target_market={tm!r}, expected one of {sorted(VALID_TARGET_MARKETS)}"))

    # confidence
    conf = di.get("confidence")
    if conf is None:
        issues.append((filepath, "design_intent.confidence is missing"))
    elif not isinstance(conf, (int, float)):
        issues.append((filepath, f"design_intent.confidence is {type(conf).__name__}, expected float"))
    elif not (0.0 <= conf <= 1.0):
        issues.append((filepath, f"design_intent.confidence={conf}, expected 0.0-1.0"))

    # detection_signals
    ds = di.get("detection_signals")
    if ds is None:
        issues.append((filepath, "design_intent.detection_signals is missing"))
    elif not isinstance(ds, list):
        issues.append((filepath, f"design_intent.detection_signals is {type(ds).__name__}, expected list"))
    else:
        for i, item in enumerate(ds):
            if not isinstance(item, str):
                issues.append((filepath, f"design_intent.detection_signals[{i}] is {type(item).__name__}, expected str"))
                break  # one error is enough

    # source
    src = di.get("source")
    if src is None:
        issues.append((filepath, "design_intent.source is missing"))
    elif not isinstance(src, dict):
        issues.append((filepath, f"design_intent.source is {type(src).__name__}, expected dict"))

    # Nullable fields: don't fail if None
    for field in NULLABLE_FIELDS:
        val = di.get(field)
        # None is acceptable — no issue reported
        # Field absence is also acceptable for nullable fields

    return issues


def _scan_outputs(repo_filter=None, analyzer_types=("schematic", "pcb")):
    """Scan outputs and validate design_intent. Returns (issues, stats)."""
    issues = []
    stats = defaultdict(int)

    for atype in analyzer_types:
        base_dir = OUTPUTS_DIR / atype
        for repo_name, repo_dir in iter_output_repos(base_dir, repo_filter):
            for json_file in sorted(repo_dir.glob("*.json")):
                if json_file.name.startswith("_"):
                    continue
                stats["files_checked"] += 1
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    continue
                filepath = f"{atype}/{repo_name}/{json_file.name}"
                file_issues = validate_design_intent(data, filepath)
                if file_issues:
                    stats["files_with_issues"] += 1
                    issues.extend(file_issues)
                else:
                    stats["files_ok"] += 1

    return issues, dict(stats)


def main():
    parser = argparse.ArgumentParser(description="Validate design_intent field in outputs")
    add_repo_filter_args(parser)
    parser.add_argument("--summary", action="store_true",
                        help="Print summary only, suppress per-file details")
    args = parser.parse_args()

    repo_filter = None
    repos = resolve_repos(args)
    if repos and len(repos) == 1:
        repo_filter = repos[0]

    issues, stats = _scan_outputs(repo_filter)

    checked = stats.get("files_checked", 0)
    ok = stats.get("files_ok", 0)
    with_issues = stats.get("files_with_issues", 0)

    if not args.summary:
        for filepath, desc in issues:
            print(f"  {filepath}: {desc}")
        if issues:
            print()

    print(f"design_intent validation: {checked} files checked, "
          f"{ok} ok, {with_issues} with issues, {len(issues)} total issues")

    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
