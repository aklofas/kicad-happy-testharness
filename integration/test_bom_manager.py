#!/usr/bin/env python3
"""Test harness for bom_manager.py -- analyze, export, and order across test repos.

Finds all root KiCad schematics (those with a matching .kicad_pro) in the repos/
directory, runs the BOM manager against each, and reports results.

Usage:
    python3 test_bom_manager.py
    python3 test_bom_manager.py --repo ecp5-mini
    python3 test_bom_manager.py --stage analyze
    python3 test_bom_manager.py -n 10
    python3 test_bom_manager.py --keep
    python3 test_bom_manager.py -v

Environment:
    KICAD_HAPPY_DIR -- path to kicad-happy repo (default: ../kicad-happy)
"""

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import HARNESS_DIR, REPOS_DIR
KICAD_HAPPY_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR",
    str(HARNESS_DIR / ".." / "kicad-happy")
)).resolve()

BOM_MANAGER = KICAD_HAPPY_DIR / "skills" / "bom" / "scripts" / "bom_manager.py"


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def find_root_schematics(repos_dir: Path, repo_filter: str = "") -> list[Path]:
    roots = []
    for pro in sorted(repos_dir.rglob("*.kicad_pro")):
        sch = pro.with_suffix(".kicad_sch")
        if sch.exists():
            if repo_filter:
                rel = sch.relative_to(repos_dir)
                if repo_filter.lower() not in str(rel.parts[0]).lower():
                    continue
            roots.append(sch)
    return roots


def run_bom_manager(args: list[str], timeout: int = 60) -> dict:
    cmd = [sys.executable, str(BOM_MANAGER)] + args
    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start
        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "elapsed_s": round(elapsed, 2),
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False, "exit_code": -1, "elapsed_s": timeout,
            "stdout": "", "stderr": f"Timed out after {timeout}s",
        }
    except Exception as e:
        return {
            "success": False, "exit_code": -1,
            "elapsed_s": time.time() - start,
            "stdout": "", "stderr": str(e),
        }


def test_analyze(sch_path: Path, verbose: bool = False) -> dict:
    result = run_bom_manager(["analyze", str(sch_path), "--json", "--recursive"])

    report = None
    if result["success"] and result["stdout"].strip():
        try:
            report = json.loads(result["stdout"])
        except json.JSONDecodeError:
            result["success"] = False
            result["stderr"] += "\nFailed to parse JSON output"

    checks = {}
    if report:
        checks["has_convention"] = "convention" in report
        checks["has_stats"] = "stats" in report
        checks["has_bom"] = "bom" in report

        stats = report.get("stats", {})
        checks["active_lines_ge_0"] = stats.get("active_lines", -1) >= 0
        checks["total_components_ge_0"] = stats.get("total_components", -1) >= 0

        conv = report.get("convention", {})
        checks["field_mapping_is_dict"] = isinstance(conv.get("field_mapping"), dict)
        checks["preferred_supplier_valid"] = conv.get("preferred_supplier") in (
            None, "digikey", "mouser", "lcsc", "element14"
        )

        for entry in report.get("bom", []):
            for field in ("references", "quantity", "value", "footprint", "mpn", "type"):
                if field not in entry:
                    checks[f"bom_entry_has_{field}"] = False
                    break
            else:
                checks.setdefault("bom_entries_well_formed", True)

    return {
        "result": result,
        "report": report,
        "checks": checks,
    }


def test_export(sch_path: Path, output_csv: Path, verbose: bool = False) -> dict:
    result = run_bom_manager(["export", str(sch_path), "-o", str(output_csv), "--recursive"])

    checks = {}
    if result["success"]:
        checks["csv_created"] = output_csv.exists()

        if output_csv.exists():
            with open(output_csv, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                headers = reader.fieldnames or []

            checks["has_reference_col"] = "Reference" in headers
            checks["has_mpn_col"] = "MPN" in headers
            checks["has_value_col"] = "Value" in headers
            checks["has_chosen_supplier_col"] = "Chosen_Supplier" in headers

            supplier_cols = [h for h in headers if h in ("DigiKey", "Mouser", "LCSC", "element14")]
            stock_cols = [h for h in headers if h in ("DK_Stock", "MO_Stock", "LC_Stock", "E14_Stock")]
            checks["supplier_cols_have_matching_stock"] = len(supplier_cols) == len(stock_cols)

            for col in supplier_cols:
                has_data = any(row.get(col, "").strip() for row in rows)
                if has_data:
                    checks[f"supplier_col_{col}_populated"] = True

            checks["row_count"] = len(rows)
            checks["supplier_columns"] = supplier_cols

    return {
        "result": result,
        "checks": checks,
    }


def test_order(csv_path: Path, output_dir: Path, verbose: bool = False) -> dict:
    if not csv_path.exists():
        return {
            "result": {"success": False, "stderr": "CSV not found"},
            "checks": {"skipped": True},
        }

    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        rows = list(reader)

    if not rows:
        return {
            "result": {"success": True, "stderr": ""},
            "checks": {"skipped_empty": True},
        }

    supplier_priority = [
        ("DigiKey", "DigiKey"),
        ("Mouser", "Mouser"),
        ("LCSC", "LCSC"),
        ("element14", "element14"),
    ]
    available_cols = set(headers)
    modified = False
    for row in rows:
        if row.get("DNP", "").strip().lower() in ("yes", "true", "1", "dnp"):
            continue
        if row.get("Chosen_Supplier", "").strip():
            continue
        for col, supplier_label in supplier_priority:
            if col in available_cols and col in row and row[col].strip():
                row["Chosen_Supplier"] = supplier_label
                modified = True
                break

    if modified:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    result = run_bom_manager(["order", str(csv_path), "-o", str(output_dir), "--json"])

    checks = {}
    if result["success"] and result["stdout"].strip():
        try:
            order_result = json.loads(result["stdout"])
        except json.JSONDecodeError:
            checks["json_parse_failed"] = True
            return {"result": result, "checks": checks}

        orders = order_result.get("orders", {})
        errors = order_result.get("errors", [])

        checks["has_orders"] = len(orders) > 0 or not any(
            row.get("Chosen_Supplier", "").strip()
            for row in rows
            if row.get("DNP", "").strip().lower() not in ("yes", "true", "1", "dnp")
        )
        checks["no_errors"] = len(errors) == 0
        if errors:
            checks["errors"] = errors

        for supplier, info in orders.items():
            fpath = Path(info["file"])
            checks[f"order_{supplier}_exists"] = fpath.exists()
            if fpath.exists():
                content = fpath.read_text().strip()
                checks[f"order_{supplier}_not_empty"] = len(content) > 0
                checks[f"order_{supplier}_lines"] = info["lines"]

    return {
        "result": result,
        "checks": checks,
    }


def test_export_merge(sch_path: Path, output_csv: Path, verbose: bool = False) -> dict:
    if not output_csv.exists():
        return {"result": {"success": False}, "checks": {"skipped": True}}

    with open(output_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        rows = list(reader)

    if not rows:
        return {"result": {"success": True}, "checks": {"skipped_empty": True}}

    marker = "TEST_MERGE_MARKER_12345"
    target_row = rows[0]
    for row in rows:
        if row.get("MPN", "").strip():
            target_row = row
            break
    target_row["Notes"] = marker
    first_ref = target_row.get("Reference", "")
    target_mpn = target_row.get("MPN", "").strip()

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    result = run_bom_manager(["export", str(sch_path), "-o", str(output_csv), "--recursive"])

    checks = {}
    if result["success"] and output_csv.exists():
        with open(output_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            new_rows = list(reader)

        found_marker = False
        for row in new_rows:
            matched = False
            if target_mpn and row.get("MPN", "").strip() == target_mpn:
                matched = True
            elif row.get("Reference", "").startswith(first_ref.split(",")[0]):
                matched = True
            if matched:
                if row.get("Notes", "") == marker:
                    found_marker = True
                break

        checks["marker_preserved"] = found_marker

    return {
        "result": result,
        "checks": checks,
    }


def print_check_result(name: str, checks: dict, verbose: bool = False):
    if not checks:
        print(f"    {Colors.YELLOW}NO CHECKS{Colors.RESET}")
        return

    skip_keys = {"row_count", "supplier_columns", "errors", "skipped", "skipped_empty"}
    failed = {k: v for k, v in checks.items() if k not in skip_keys and v is False}
    passed = {k: v for k, v in checks.items() if k not in skip_keys and v is True}

    if failed:
        for k in failed:
            print(f"    {Colors.RED}FAIL{Colors.RESET} {k}")
        if checks.get("errors"):
            for err in checks["errors"][:3]:
                print(f"      {Colors.DIM}{err}{Colors.RESET}")
    elif checks.get("skipped") or checks.get("skipped_empty"):
        print(f"    {Colors.DIM}skipped{Colors.RESET}")
    else:
        summary_parts = []
        if "row_count" in checks:
            summary_parts.append(f"{checks['row_count']} rows")
        if "supplier_columns" in checks:
            summary_parts.append(f"suppliers: {','.join(checks['supplier_columns']) or 'none'}")
        for k, v in checks.items():
            if k.startswith("order_") and k.endswith("_lines"):
                supplier = k.replace("order_", "").replace("_lines", "")
                summary_parts.append(f"{supplier}: {v} lines")
        detail = f" ({', '.join(summary_parts)})" if summary_parts else ""
        print(f"    {Colors.GREEN}PASS{Colors.RESET} {len(passed)} checks{detail}")

    if verbose:
        for k, v in sorted(checks.items()):
            if k in skip_keys:
                continue
            status = f"{Colors.GREEN}ok{Colors.RESET}" if v else f"{Colors.RED}FAIL{Colors.RESET}"
            print(f"      {status} {k}")


def main():
    parser = argparse.ArgumentParser(description="Test BOM manager against test repos")
    parser.add_argument("--repo", help="Filter to repos matching this name")
    parser.add_argument("--stage", choices=["analyze", "export", "order", "merge"],
                        help="Run only one test stage")
    parser.add_argument("-n", "--limit", type=int, default=0, help="Limit number of schematics")
    parser.add_argument("--keep", action="store_true", help="Keep generated CSV/order files")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if not BOM_MANAGER.exists():
        print(f"Error: bom_manager.py not found at {BOM_MANAGER}")
        print(f"Set KICAD_HAPPY_DIR or ensure ../kicad-happy exists")
        sys.exit(1)

    schematics = find_root_schematics(REPOS_DIR, repo_filter=args.repo or "")
    if args.limit:
        schematics = schematics[:args.limit]

    if not schematics:
        print("No schematics found. Run checkout.sh and discover.sh first.")
        sys.exit(1)

    if args.keep:
        out_base = HARNESS_DIR / "test_bom_out"
        out_base.mkdir(exist_ok=True)
    else:
        out_base = Path(tempfile.mkdtemp(prefix="bom_test_"))

    stages = [args.stage] if args.stage else ["analyze", "export", "order", "merge"]

    print(f"{Colors.BOLD}Testing BOM Manager: {len(schematics)} schematics, stages: {', '.join(stages)}{Colors.RESET}\n")

    totals = {stage: {"pass": 0, "fail": 0, "skip": 0} for stage in stages}
    failures = []
    timings = []

    for i, sch in enumerate(schematics, 1):
        rel = sch.relative_to(REPOS_DIR)
        repo_name = rel.parts[0]
        print(f"{Colors.CYAN}[{i}/{len(schematics)}] {rel}{Colors.RESET}")

        sch_out = out_base / repo_name / sch.stem
        sch_out.mkdir(parents=True, exist_ok=True)
        csv_path = sch_out / "bom.csv"
        order_dir = sch_out / "orders"

        sch_start = time.time()

        if "analyze" in stages:
            analyze_result = test_analyze(sch, verbose=args.verbose)
            ar = analyze_result["result"]
            ac = analyze_result["checks"]

            any_fail = any(v is False for k, v in ac.items())
            if any_fail:
                totals["analyze"]["fail"] += 1
                failures.append(("analyze", str(rel), ac))
            elif not ac:
                totals["analyze"]["skip"] += 1
            else:
                totals["analyze"]["pass"] += 1

            print(f"  analyze ({ar['elapsed_s']}s):")
            print_check_result("analyze", ac, verbose=args.verbose)

            if args.verbose and ar["stderr"]:
                for line in ar["stderr"].split("\n")[:5]:
                    print(f"      {Colors.DIM}{line}{Colors.RESET}")
        else:
            pass

        if "export" in stages:
            export_result = test_export(sch, csv_path, verbose=args.verbose)
            er = export_result["result"]
            ec = export_result["checks"]

            any_fail = any(v is False for k, v in ec.items()
                          if k not in ("row_count", "supplier_columns"))
            if any_fail:
                totals["export"]["fail"] += 1
                failures.append(("export", str(rel), ec))
            else:
                totals["export"]["pass"] += 1

            print(f"  export ({er['elapsed_s']}s):")
            print_check_result("export", ec, verbose=args.verbose)

        if "order" in stages:
            order_result = test_order(csv_path, order_dir, verbose=args.verbose)
            oc = order_result["checks"]

            if oc.get("skipped") or oc.get("skipped_empty"):
                totals["order"]["skip"] += 1
            elif any(v is False for k, v in oc.items()
                     if not k.startswith("errors") and k not in ("skipped", "skipped_empty")):
                totals["order"]["fail"] += 1
                failures.append(("order", str(rel), oc))
            else:
                totals["order"]["pass"] += 1

            print(f"  order:")
            print_check_result("order", oc, verbose=args.verbose)

        if "merge" in stages and csv_path.exists():
            merge_result = test_export_merge(sch, csv_path, verbose=args.verbose)
            mc = merge_result["checks"]

            if mc.get("skipped") or mc.get("skipped_empty"):
                totals["merge"]["skip"] += 1
            elif any(v is False for k, v in mc.items()
                     if k not in ("skipped", "skipped_empty")):
                totals["merge"]["fail"] += 1
                failures.append(("merge", str(rel), mc))
            else:
                totals["merge"]["pass"] += 1

            print(f"  merge:")
            print_check_result("merge", mc, verbose=args.verbose)

        sch_elapsed = round(time.time() - sch_start, 2)
        timings.append((str(rel), sch_elapsed))
        print()

    # Summary
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"Summary: BOM Manager Tests")
    print(f"{'='*70}{Colors.RESET}\n")

    total_pass = 0
    total_fail = 0
    total_skip = 0
    for stage in stages:
        s = totals[stage]
        total_pass += s["pass"]
        total_fail += s["fail"]
        total_skip += s["skip"]
        color = Colors.GREEN if s["fail"] == 0 else Colors.RED
        print(f"  {stage:10s}  {color}{s['pass']} pass{Colors.RESET}, "
              f"{Colors.RED + str(s['fail']) + ' fail' + Colors.RESET if s['fail'] else '0 fail'}, "
              f"{s['skip']} skip")

    print(f"\n  Total: {Colors.GREEN}{total_pass} pass{Colors.RESET}, "
          f"{Colors.RED}{total_fail} fail{Colors.RESET}, {total_skip} skip")

    if failures:
        print(f"\n{Colors.RED}Failures:{Colors.RESET}")
        for stage, rel, checks in failures:
            failed_checks = [k for k, v in checks.items() if v is False]
            print(f"  {stage} {rel}: {', '.join(failed_checks)}")

    if timings:
        times = [t for _, t in timings]
        avg = sum(times) / len(times)
        slowest = sorted(timings, key=lambda x: x[1], reverse=True)[:3]
        print(f"\n  Avg time: {avg:.2f}s, Total: {sum(times):.1f}s")
        if len(timings) > 5:
            print(f"  Slowest:")
            for name, t in slowest:
                print(f"    {t:.2f}s  {name}")

    if not args.keep:
        shutil.rmtree(out_base, ignore_errors=True)
    else:
        print(f"\n  Output saved to: {out_base}")

    sys.exit(1 if total_fail > 0 else 0)


if __name__ == "__main__":
    main()
