#!/usr/bin/env python3
"""Test harness for datasheet downloading across distributors.

Verifies feature parity between fetch_datasheet_digikey.py,
fetch_datasheet_mouser.py, fetch_datasheet_lcsc.py, and
fetch_datasheet_element14.py by running all against a set of
known MPNs and comparing results.

Usage:
    python3 test_datasheets.py
    python3 test_datasheets.py --only digikey
    python3 test_datasheets.py --mpn GRM155R71C104KA88D
    python3 test_datasheets.py --keep
    python3 test_datasheets.py -v

Environment:
    DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET
    MOUSER_SEARCH_API_KEY
    ELEMENT14_API_KEY
    KICAD_HAPPY_DIR — path to kicad-happy repo (default: ../kicad-happy)
"""

TIER = "online"

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import HARNESS_DIR
KICAD_HAPPY_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR",
    str(HARNESS_DIR / ".." / "kicad-happy")
)).resolve()

SCRIPTS = {
    "digikey": KICAD_HAPPY_DIR / "skills" / "digikey" / "scripts" / "fetch_datasheet_digikey.py",
    "mouser": KICAD_HAPPY_DIR / "skills" / "mouser" / "scripts" / "fetch_datasheet_mouser.py",
    "lcsc": KICAD_HAPPY_DIR / "skills" / "lcsc" / "scripts" / "fetch_datasheet_lcsc.py",
    "element14": KICAD_HAPPY_DIR / "skills" / "element14" / "scripts" / "fetch_datasheet_element14.py",
}

_TEST_MPNS_FILE = HARNESS_DIR / "reference" / "test_mpns.json"

_DEFAULT_MPNS = [
    {"mpn": "GRM155R71C104KA88J", "category": "passive_cap", "description": "Murata MLCC 0402", "manufacturer": "Murata Electronics"},
    {"mpn": "RC0402FR-0710KL", "category": "passive_res", "description": "YAGEO thick film 0402", "manufacturer": "YAGEO"},
    {"mpn": "TLV62568DBVR", "category": "ic_reg", "description": "TI buck converter", "manufacturer": "Texas Instruments"},
    {"mpn": "STM32G474CEU6", "category": "ic_mcu", "description": "STM32 Cortex-M4", "manufacturer": "STMicroelectronics"},
    {"mpn": "USB4105-GF-A", "category": "conn", "description": "GCT USB-C receptacle", "manufacturer": "GCT"},
]

def _load_test_mpns() -> list[dict]:
    if _TEST_MPNS_FILE.exists():
        with open(_TEST_MPNS_FILE) as f:
            return json.load(f)
    return _DEFAULT_MPNS

TEST_MPNS = _load_test_mpns()

REQUIRED_ENV = {
    "digikey": ["DIGIKEY_CLIENT_ID", "DIGIKEY_CLIENT_SECRET"],
    "mouser": ["MOUSER_SEARCH_API_KEY"],
    "lcsc": [],
    "element14": ["ELEMENT14_API_KEY"],
}


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def check_env(distributor: str) -> bool:
    missing = [v for v in REQUIRED_ENV[distributor] if not os.environ.get(v)]
    if missing:
        print(f"  {Colors.YELLOW}SKIP{Colors.RESET} {distributor}: missing {', '.join(missing)}")
        return False
    return True


def run_fetch(distributor: str, mpn: str, output_path: str,
              manufacturer: str = "", description: str = "",
              timeout: int = 120) -> dict:
    script = SCRIPTS[distributor]
    if not script.exists():
        return {
            "success": False, "exit_code": -1, "elapsed_s": 0,
            "json": {}, "stderr": f"Script not found: {script}",
            "file_exists": False, "file_size": 0, "is_pdf": False,
            "verification": None,
        }

    cmd = [
        sys.executable, str(script),
        "--search", mpn,
        "--output", output_path,
        "--json",
    ]

    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start

        json_output = {}
        if result.stdout.strip():
            try:
                json_output = json.loads(result.stdout.strip())
            except json.JSONDecodeError:
                pass

        is_pdf = _is_pdf(output_path)

        verification = None
        if is_pdf:
            v_mfg = json_output.get("manufacturer", manufacturer)
            v_desc = json_output.get("description", description)
            verification = verify_pdf_content(output_path, mpn, v_mfg, v_desc)

        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "elapsed_s": round(elapsed, 1),
            "json": json_output,
            "stderr": result.stderr.strip(),
            "file_exists": os.path.exists(output_path),
            "file_size": os.path.getsize(output_path) if os.path.exists(output_path) else 0,
            "is_pdf": is_pdf,
            "verification": verification,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False, "exit_code": -1, "elapsed_s": timeout,
            "json": {}, "stderr": f"Timed out after {timeout}s",
            "file_exists": False, "file_size": 0, "is_pdf": False,
            "verification": None,
        }
    except Exception as e:
        return {
            "success": False, "exit_code": -1,
            "elapsed_s": time.time() - start,
            "json": {}, "stderr": str(e),
            "file_exists": False, "file_size": 0, "is_pdf": False,
            "verification": None,
        }


def _is_pdf(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"%PDF"
    except Exception:
        return False


def _extract_pdf_text(pdf_path: str, max_pages: int = 3) -> str:
    try:
        result = subprocess.run(
            ["pdftotext", "-l", str(max_pages), pdf_path, "-"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    try:
        with open(pdf_path, "rb") as f:
            raw = f.read(200_000)
        import re as _re
        strings = _re.findall(rb"[\x20-\x7e]{4,}", raw)
        return " ".join(s.decode("ascii", errors="ignore") for s in strings)
    except Exception:
        return ""


def verify_pdf_content(pdf_path: str, mpn: str, manufacturer: str = "", description: str = "") -> dict:
    text = _extract_pdf_text(pdf_path)
    if not text or len(text) < 50:
        return {"verified": False, "confidence": "unverified",
                "details": "Could not extract text from PDF"}

    text_upper = text.upper()
    mpn_upper = mpn.upper()

    mpn_found = mpn_upper in text_upper
    if not mpn_found:
        import re as _re
        base_mpn = _re.sub(
            r"(DRLR|DRL|DGKR|DGK|DCKR|DCK|DBVR|DBV|PWPR|PWP|RGER|RGE|"
            r"RGTR|RGT|NRND|TR|CT|ND|LT1G|LT3G|BK|PBF|-ND)$",
            "", mpn_upper,
        )
        if base_mpn and len(base_mpn) >= 4 and base_mpn != mpn_upper:
            mpn_found = base_mpn in text_upper

    mfg_found = False
    if manufacturer:
        mfg_upper = manufacturer.upper()
        mfg_found = mfg_upper in text_upper
        if not mfg_found:
            first_word = mfg_upper.split()[0] if " " in mfg_upper else ""
            if first_word and len(first_word) >= 4:
                mfg_found = first_word in text_upper

    if mpn_found:
        return {"verified": True, "confidence": "verified",
                "details": f"MPN '{mpn}' found in PDF"}
    elif mfg_found:
        return {"verified": False, "confidence": "likely",
                "details": f"MPN not found but manufacturer present"}
    else:
        return {"verified": False, "confidence": "unverified",
                "details": f"Neither MPN nor manufacturer found in PDF"}


def format_size(size: int) -> str:
    if size == 0:
        return "0"
    if size < 1024:
        return f"{size}B"
    if size < 1024 * 1024:
        return f"{size / 1024:.0f}KB"
    return f"{size / (1024 * 1024):.1f}MB"


def print_result(distributor: str, mpn: str, result: dict, verbose: bool = False):
    if result["success"] and result["is_pdf"]:
        vr = result.get("verification")
        if vr and vr["confidence"] == "verified":
            status = f"{Colors.GREEN}PASS{Colors.RESET}"
        elif vr and vr["confidence"] == "wrong":
            status = f"{Colors.RED}WRONG{Colors.RESET}"
        elif vr and vr["confidence"] == "likely":
            status = f"{Colors.GREEN}PASS{Colors.RESET}"
        else:
            status = f"{Colors.YELLOW}PASS?{Colors.RESET}"

        detail = f"{format_size(result['file_size'])} in {result['elapsed_s']}s"
        source = result["json"].get("source", "")
        if source:
            detail += f" (via {source})"
        if vr:
            conf = vr["confidence"]
            if conf == "verified":
                detail += f" {Colors.GREEN}[verified]{Colors.RESET}"
            elif conf == "likely":
                detail += f" {Colors.GREEN}[likely]{Colors.RESET}"
            elif conf == "wrong":
                detail += f" {Colors.RED}[WRONG]{Colors.RESET}"
            else:
                detail += f" {Colors.YELLOW}[unverified]{Colors.RESET}"
    elif result["success"] and not result["is_pdf"]:
        status = f"{Colors.RED}FAIL{Colors.RESET}"
        detail = "downloaded but not a valid PDF"
    else:
        status = f"{Colors.RED}FAIL{Colors.RESET}"
        detail = result["stderr"].split("\n")[-1] if result["stderr"] else f"exit {result['exit_code']}"
        if len(detail) > 80:
            detail = detail[:77] + "..."

    print(f"  {status} {distributor:8s} {mpn:30s} {detail}")

    if verbose:
        vr = result.get("verification")
        if vr:
            print(f"    {Colors.DIM}Verification: {vr['details']}{Colors.RESET}")
        if result["stderr"]:
            for line in result["stderr"].split("\n"):
                print(f"    {Colors.DIM}{line}{Colors.RESET}")


def print_summary(all_results: dict):
    distributors = sorted(all_results.keys())
    mpns = sorted({mpn for d in all_results.values() for mpn in d})

    print(f"\n{Colors.BOLD}{'='*80}")
    print(f"Summary: Datasheet Download Feature Parity")
    print(f"{'='*80}{Colors.RESET}\n")

    header = f"{'MPN':30s}"
    for dist in distributors:
        header += f"  {dist:>12s}"
    print(header)
    print("-" * (30 + 14 * len(distributors)))

    parity_count = 0
    total_count = 0
    for mpn in mpns:
        row = f"{mpn:30s}"
        results_for_mpn = []
        for dist in distributors:
            r = all_results.get(dist, {}).get(mpn)
            if r is None:
                row += f"  {'skip':>12s}"
                results_for_mpn.append(None)
            elif r["success"] and r["is_pdf"]:
                size_str = format_size(r["file_size"])
                row += f"  {Colors.GREEN}{size_str:>12s}{Colors.RESET}"
                results_for_mpn.append(True)
            else:
                row += f"  {Colors.RED}{'FAIL':>12s}{Colors.RESET}"
                results_for_mpn.append(False)
        print(row)

        active = [r for r in results_for_mpn if r is not None]
        if len(active) >= 2:
            total_count += 1
            if all(r == active[0] for r in active):
                parity_count += 1

    print("-" * (30 + 14 * len(distributors)))

    for dist in distributors:
        results = all_results.get(dist, {})
        passed = sum(1 for r in results.values() if r["success"] and r["is_pdf"])
        verified = sum(
            1 for r in results.values()
            if r.get("verification") and r["verification"]["confidence"] == "verified"
        )
        likely = sum(
            1 for r in results.values()
            if r.get("verification") and r["verification"]["confidence"] == "likely"
        )
        wrong = sum(
            1 for r in results.values()
            if r.get("verification") and r["verification"]["confidence"] == "wrong"
        )
        total = len(results)
        verify_str = f" (verified: {verified}, likely: {likely}"
        if wrong:
            verify_str += f", {Colors.RED}WRONG: {wrong}{Colors.RESET}"
        verify_str += ")"
        print(f"  {dist}: {passed}/{total} downloaded{verify_str}")

    if total_count > 0:
        print(f"\n  Feature parity: {parity_count}/{total_count} MPNs have matching results across distributors")


def main():
    parser = argparse.ArgumentParser(description="Test datasheet downloading across distributors")
    parser.add_argument("--only", choices=["digikey", "mouser", "lcsc", "element14"], help="Test only one distributor")
    parser.add_argument("--mpn", help="Test a single MPN instead of the full set")
    parser.add_argument("--category", help="Filter by category prefix (e.g. 'ic_', 'passive', 'conn')")
    parser.add_argument("--limit", "-n", type=int, default=0, help="Limit number of MPNs to test (0=all)")
    parser.add_argument("--keep", action="store_true", help="Keep downloaded PDFs (saved to ./test_datasheets_out/)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show stderr from scripts")
    parser.add_argument("--timeout", type=int, default=120, help="Per-download timeout in seconds (default: 120)")
    args = parser.parse_args()

    distributors = [args.only] if args.only else ["digikey", "mouser", "lcsc", "element14"]
    if args.mpn:
        test_mpns = [{"mpn": args.mpn, "category": "", "description": "", "manufacturer": ""}]
    else:
        test_mpns = TEST_MPNS
        if args.category:
            test_mpns = [m for m in test_mpns if m.get("category", "").startswith(args.category)]
        if args.limit:
            test_mpns = test_mpns[:args.limit]

    active_distributors = []
    for dist in distributors:
        if check_env(dist):
            active_distributors.append(dist)
    if not active_distributors:
        print("No distributors available (missing API keys). Exiting.")
        sys.exit(2)

    if args.keep:
        out_dir = Path("test_datasheets_out")
        out_dir.mkdir(exist_ok=True)
        print(f"Saving PDFs to {out_dir.resolve()}/\n")
    else:
        tmp_dir = tempfile.mkdtemp(prefix="datasheet_test_")
        out_dir = Path(tmp_dir)

    all_results: dict[str, dict[str, dict]] = {d: {} for d in active_distributors}

    print(f"{Colors.BOLD}Testing datasheet downloads: {len(test_mpns)} MPNs x {len(active_distributors)} distributors{Colors.RESET}\n")

    for mpn_info in test_mpns:
        mpn = mpn_info["mpn"]
        desc = mpn_info.get("description", "")
        if desc:
            print(f"{Colors.CYAN}{mpn}{Colors.RESET} ({desc})")
        else:
            print(f"{Colors.CYAN}{mpn}{Colors.RESET}")

        for dist in active_distributors:
            output_path = str(out_dir / f"{mpn}_{dist}.pdf")
            result = run_fetch(
                dist, mpn, output_path,
                manufacturer=mpn_info.get("manufacturer", ""),
                description=mpn_info.get("description", ""),
                timeout=args.timeout,
            )
            all_results[dist][mpn] = result
            print_result(dist, mpn, result, verbose=args.verbose)

            if not args.keep and os.path.exists(output_path):
                os.remove(output_path)

        print()

    print_summary(all_results)

    if not args.keep:
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass

    any_fail = any(
        not r["success"] or not r["is_pdf"]
        for d in all_results.values()
        for r in d.values()
    )
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
