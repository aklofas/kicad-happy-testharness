#!/usr/bin/env python3
"""Mutation testing framework for assertion effectiveness.

Injects deliberate errors into analyzer outputs and verifies that at least one
assertion catches each mutation. Measures assertion catch rate — if a mutation
goes undetected, the assertions covering that area are too weak.

Usage:
    python3 validate/mutation_test.py --repo ESP32-EVB --type schematic
    python3 validate/mutation_test.py --repo ESP32-EVB --type schematic --mutations 100
    python3 validate/mutation_test.py --repo ESP32-EVB --type schematic --seed 42
"""

import argparse
import copy
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from checks import evaluate_assertion, load_assertions
from run_checks import find_output_file
from utils import OUTPUTS_DIR, DATA_DIR, ANALYZER_TYPES, resolve_path


# ---------------------------------------------------------------------------
# Mutation operators
# ---------------------------------------------------------------------------

def _find_list_paths(data, prefix=""):
    """Find all paths to non-empty lists in a nested dict."""
    paths = []
    if isinstance(data, dict):
        for k, v in data.items():
            p = f"{prefix}.{k}" if prefix else k
            if isinstance(v, list) and len(v) > 0:
                paths.append(p)
            elif isinstance(v, dict):
                paths.extend(_find_list_paths(v, p))
    return paths


def _find_numeric_paths(data, prefix=""):
    """Find all paths to numeric values in a nested dict."""
    paths = []
    if isinstance(data, dict):
        for k, v in data.items():
            p = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                paths.append((p, v))
            elif isinstance(v, dict):
                paths.extend(_find_numeric_paths(v, p))
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        paths.extend(_find_numeric_paths(item, f"{p}[{i}]"))
    return paths


def _set_path(data, path, value):
    """Set a value at a dotted path (supports [N] array indexing)."""
    import re
    parts = re.split(r'\.(?![^\[]*\])', path)
    current = data
    for part in parts[:-1]:
        m = re.match(r'(.+)\[(\d+)\]$', part)
        if m:
            current = current[m.group(1)][int(m.group(2))]
        else:
            current = current[part]
    last = parts[-1]
    m = re.match(r'(.+)\[(\d+)\]$', last)
    if m:
        current[m.group(1)][int(m.group(2))] = value
    else:
        current[last] = value


def _delete_path(data, path):
    """Delete a key at a dotted path."""
    parts = path.split(".")
    current = data
    for part in parts[:-1]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False
    if isinstance(current, dict) and parts[-1] in current:
        del current[parts[-1]]
        return True
    return False


def mutate_delete_list_item(data, rng):
    """Remove a random item from a non-empty list."""
    paths = _find_list_paths(data, "")
    # Prefer signal_analysis paths
    sa_paths = [p for p in paths if "signal_analysis" in p]
    target_paths = sa_paths if sa_paths else paths
    if not target_paths:
        return None, None

    path = rng.choice(target_paths)
    lst = resolve_path(data, path)
    if not lst or not isinstance(lst, list) or len(lst) == 0:
        return None, None

    mutated = copy.deepcopy(data)
    m_lst = resolve_path(mutated, path)
    idx = rng.randrange(len(m_lst))
    removed = m_lst.pop(idx)
    desc = f"delete_list_item: removed item [{idx}] from {path}"
    return mutated, desc


def mutate_change_numeric(data, rng, factor_range=(0.3, 0.7)):
    """Change a numeric value by a significant factor."""
    paths = _find_numeric_paths(data)
    # Filter to interesting paths (not version numbers, line counts)
    interesting = [(p, v) for p, v in paths
                   if v != 0 and not any(x in p for x in
                   ("kicad_version", "file_version", "line", "column"))]
    if not interesting:
        return None, None

    path, old_val = rng.choice(interesting)
    factor = rng.uniform(*factor_range)
    if rng.random() < 0.5:
        factor = 1.0 + factor  # increase
    else:
        factor = 1.0 - factor  # decrease
    new_val = old_val * factor

    mutated = copy.deepcopy(data)
    try:
        _set_path(mutated, path, new_val)
    except (KeyError, IndexError, TypeError):
        return None, None
    desc = f"change_numeric: {path} {old_val} -> {new_val:.4g} (×{factor:.2f})"
    return mutated, desc


def mutate_remove_key(data, rng):
    """Remove an entire key from the top-level or signal_analysis."""
    candidates = []
    sa = data.get("signal_analysis", {})
    for k, v in sa.items():
        if isinstance(v, list) and len(v) > 0:
            candidates.append(f"signal_analysis.{k}")
    # Also consider top-level keys
    for k in ("statistics", "components", "signal_analysis"):
        if k in data:
            candidates.append(k)
    if not candidates:
        return None, None

    path = rng.choice(candidates)
    mutated = copy.deepcopy(data)
    _delete_path(mutated, path)
    desc = f"remove_key: deleted {path}"
    return mutated, desc


def mutate_change_ref(data, rng):
    """Change a component reference string to a nonexistent one."""
    sa = data.get("signal_analysis", {})
    ref_locations = []
    for det_name, dets in sa.items():
        if not isinstance(dets, list):
            continue
        for i, det in enumerate(dets):
            if not isinstance(det, dict):
                continue
            for key, val in det.items():
                if isinstance(val, dict) and "ref" in val and val["ref"]:
                    ref_locations.append(
                        (f"signal_analysis.{det_name}[{i}].{key}.ref", val["ref"]))
    if not ref_locations:
        return None, None

    path, old_ref = rng.choice(ref_locations)
    new_ref = "XMUT999"
    mutated = copy.deepcopy(data)
    try:
        _set_path(mutated, path, new_ref)
    except (KeyError, IndexError, TypeError):
        return None, None
    desc = f"change_ref: {path} {old_ref} -> {new_ref}"
    return mutated, desc


MUTATION_OPS = [
    mutate_delete_list_item,
    mutate_change_numeric,
    mutate_remove_key,
    mutate_change_ref,
]


def generate_mutations(data, count, seed=42):
    """Generate N mutations of the data."""
    rng = random.Random(seed)
    mutations = []
    attempts = 0
    while len(mutations) < count and attempts < count * 5:
        attempts += 1
        op = rng.choice(MUTATION_OPS)
        mutated, desc = op(data, rng)
        if mutated is not None:
            mutations.append((mutated, desc))
    return mutations


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_mutation_test(original_data, assertions, mutations):
    """Run assertions against each mutation, check if caught.

    Returns dict with {total, caught, missed, catch_rate, by_type, missed_details}.
    """
    total = len(mutations)
    caught = 0
    missed_details = []
    by_type = {}

    for mutated_data, desc in mutations:
        mutation_type = desc.split(":")[0]
        by_type.setdefault(mutation_type, {"total": 0, "caught": 0})
        by_type[mutation_type]["total"] += 1

        # Check if any assertion fails on the mutated data
        any_failed = False
        for assertion in assertions:
            result = evaluate_assertion(assertion, mutated_data)
            if not result["passed"]:
                any_failed = True
                break

        if any_failed:
            caught += 1
            by_type[mutation_type]["caught"] += 1
        else:
            missed_details.append(desc)

    catch_rate = caught / total * 100 if total else 0
    return {
        "total": total,
        "caught": caught,
        "missed": total - caught,
        "catch_rate": round(catch_rate, 1),
        "by_type": {k: {**v, "rate": round(v["caught"] / v["total"] * 100, 1)
                         if v["total"] else 0}
                    for k, v in by_type.items()},
        "missed_details": missed_details,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Mutation testing for assertion effectiveness")
    parser.add_argument("--repo", required=True, help="Repo to test")
    parser.add_argument("--type", required=True, choices=ANALYZER_TYPES,
                        help="Analyzer type")
    parser.add_argument("--mutations", "-n", type=int, default=50,
                        help="Number of mutations to generate (default: 50)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    # Load assertions for the repo/type
    assertion_sets = load_assertions(
        DATA_DIR, repo_name=args.repo, analyzer_type=args.type)
    if not assertion_sets:
        print(f"No assertions found for {args.repo}/{args.type}", file=sys.stderr)
        sys.exit(1)

    # Find matching output files and run mutations
    total_results = {
        "total": 0, "caught": 0, "missed": 0,
        "by_type": {}, "missed_details": [],
    }

    for aset in assertion_sets:
        file_pattern = aset.get("file_pattern", "")
        project_path = aset.get("_project_path")
        assertions = aset.get("assertions", [])
        if not assertions:
            continue

        output_file = find_output_file(
            file_pattern, args.repo, project_path, args.type)
        if not output_file:
            continue

        try:
            data = json.loads(output_file.read_text())
        except Exception:
            continue

        # Collect ALL assertions for this output (from all assertion sets)
        all_assertions = []
        for other_aset in assertion_sets:
            if other_aset.get("file_pattern") == file_pattern:
                all_assertions.extend(other_aset.get("assertions", []))

        mutations = generate_mutations(data, args.mutations, seed=args.seed)
        if not mutations:
            continue

        result = run_mutation_test(data, all_assertions, mutations)

        total_results["total"] += result["total"]
        total_results["caught"] += result["caught"]
        total_results["missed"] += result["missed"]
        total_results["missed_details"].extend(result["missed_details"])
        for k, v in result["by_type"].items():
            if k not in total_results["by_type"]:
                total_results["by_type"][k] = {"total": 0, "caught": 0}
            total_results["by_type"][k]["total"] += v["total"]
            total_results["by_type"][k]["caught"] += v["caught"]
        break  # Only test the first matching output to avoid double-counting

    if total_results["total"] == 0:
        print(f"No mutations generated for {args.repo}/{args.type}", file=sys.stderr)
        sys.exit(1)

    total_results["catch_rate"] = round(
        total_results["caught"] / total_results["total"] * 100, 1)
    for k, v in total_results["by_type"].items():
        v["rate"] = round(v["caught"] / v["total"] * 100, 1) if v["total"] else 0

    if args.json:
        json.dump(total_results, sys.stdout, indent=2)
        print()
        return

    # Text output
    t = total_results
    print(f"Mutation Test: {args.repo}/{args.type}")
    print(f"{'='*50}")
    print(f"Total mutations: {t['total']}")
    print(f"Caught:          {t['caught']}")
    print(f"Missed:          {t['missed']}")
    print(f"Catch rate:      {t['catch_rate']}%")
    print()
    print("By mutation type:")
    for mtype, v in sorted(t["by_type"].items()):
        print(f"  {mtype:<25s} {v['caught']}/{v['total']} ({v['rate']}%)")
    if t["missed_details"]:
        print(f"\nMissed mutations:")
        for desc in t["missed_details"][:10]:
            print(f"  {desc}")
        if len(t["missed_details"]) > 10:
            print(f"  ... and {len(t['missed_details']) - 10} more")


if __name__ == "__main__":
    main()
