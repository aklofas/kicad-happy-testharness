#!/usr/bin/env python3
"""Download datasheets for extracted MPNs.

Reads extracted_mpns.json (output of extract_mpns.py) and downloads
datasheets using kicad-happy's distributor fetch scripts. Tries sources
in order: direct URL from schematic, DigiKey, Mouser, LCSC.

Usage:
    python3 validate/download_datasheets.py
    python3 validate/download_datasheets.py --limit 10
    python3 validate/download_datasheets.py --project OpenMower
    python3 validate/download_datasheets.py --status

Environment:
    DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET
    MOUSER_SEARCH_API_KEY
    KICAD_HAPPY_DIR — path to kicad-happy repo (default: ../kicad-happy)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import HARNESS_DIR
KICAD_HAPPY_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR",
    str(HARNESS_DIR / ".." / "kicad-happy")
)).resolve()

DATASHEETS_DIR = HARNESS_DIR / "results" / "datasheets"
EXTRACTED_MPNS = HARNESS_DIR / "results" / "extracted_mpns.json"
STATUS_FILE = DATASHEETS_DIR / "_status.json"

FETCHERS = {
    "digikey": KICAD_HAPPY_DIR / "skills" / "digikey" / "scripts" / "fetch_datasheet_digikey.py",
    "mouser": KICAD_HAPPY_DIR / "skills" / "mouser" / "scripts" / "fetch_datasheet_mouser.py",
    "lcsc": KICAD_HAPPY_DIR / "skills" / "lcsc" / "scripts" / "fetch_datasheet_lcsc.py",
    "element14": KICAD_HAPPY_DIR / "skills" / "element14" / "scripts" / "fetch_datasheet_element14.py",
}


def safe_filename(mpn: str) -> str:
    """Convert MPN to a safe filename."""
    return mpn.replace("/", "_").replace("\\", "_").replace(" ", "_")


def load_status() -> dict:
    """Load download status tracking."""
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text())
    return {}


def save_status(status: dict):
    """Save download status tracking."""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(status, indent=2) + "\n")


def pdf_exists(mpn: str) -> bool:
    """Check if a datasheet PDF already exists for this MPN."""
    pdf_path = DATASHEETS_DIR / f"{safe_filename(mpn)}.pdf"
    return pdf_path.exists() and pdf_path.stat().st_size > 1000


def try_direct_url(url: str, mpn: str) -> bool:
    """Try downloading a datasheet from a direct URL."""
    if not url or url == "~" or not url.startswith("http"):
        return False

    # Only try URLs that look like PDFs
    if not (url.lower().endswith(".pdf") or "datasheet" in url.lower()):
        return False

    pdf_path = DATASHEETS_DIR / f"{safe_filename(mpn)}.pdf"

    try:
        # Use the digikey fetcher for direct URLs (it accepts a URL positional arg)
        fetcher = FETCHERS.get("digikey")
        if not fetcher or not fetcher.exists():
            return False

        result = subprocess.run(
            [sys.executable, str(fetcher), url, "-o", str(pdf_path), "--json"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and pdf_path.exists() and pdf_path.stat().st_size > 1000:
            return True
    except Exception:
        pass

    # Clean up failed download
    if pdf_path.exists() and pdf_path.stat().st_size <= 1000:
        pdf_path.unlink()
    return False


def try_lcsc_direct(lcsc_id: str, mpn: str) -> bool:
    """Try downloading a datasheet directly from LCSC's product API."""
    if not lcsc_id or not lcsc_id.startswith("C"):
        return False

    pdf_path = DATASHEETS_DIR / f"{safe_filename(mpn)}.pdf"
    try:
        api_url = f"https://wmsc.lcsc.com/ftps/wm/product/detail?productCode={lcsc_id}"
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        })
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        pdf_url = data.get("result", {}).get("pdfUrl", "")
        if not pdf_url:
            return False

        pdf_req = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(pdf_req, timeout=30) as pdf_resp:
            content = pdf_resp.read()
        if len(content) > 1000 and content[:4] == b"%PDF":
            pdf_path.write_bytes(content)
            return True
    except Exception:
        pass

    if pdf_path.exists() and pdf_path.stat().st_size <= 1000:
        pdf_path.unlink()
    return False


def try_manufacturer_scrape(mpn: str) -> bool:
    """Try scraping manufacturer websites for datasheet PDFs.

    Uses requests to fetch product pages and extract PDF links.
    Handles: Panasonic, TDK, Vishay, Würth, TE Connectivity.
    """
    try:
        import requests as _req
    except ImportError:
        return False

    pdf_path = DATASHEETS_DIR / f"{safe_filename(mpn)}.pdf"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"}

    def _download_pdf(url: str) -> bool:
        try:
            r = _req.get(url, headers=headers, timeout=20, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 1000 and r.content[:4] == b"%PDF":
                pdf_path.write_bytes(r.content)
                return True
        except Exception:
            pass
        return False

    def _scrape_page(page_url: str) -> bool:
        try:
            r = _req.get(page_url, headers=headers, timeout=15, allow_redirects=True)
            if r.status_code != 200:
                return False
            pdfs = re.findall(r'https?://[^\"\s<>\']+\.pdf', r.text, re.IGNORECASE)
            for pdf_url in pdfs[:3]:
                if _download_pdf(pdf_url):
                    return True
        except Exception:
            pass
        return False

    mpn_upper = mpn.upper()

    # Panasonic resistors — use known catalog PDFs by series prefix
    panasonic_resistor_catalogs = {
        "ERJ": "https://industrial.panasonic.com/cdbs/www-data/pdf/RDA0000/AOA0000C301.pdf",
        "EXB": "https://industrial.panasonic.com/cdbs/www-data/pdf/RDO0000/AOA0000C332.pdf",
    }
    for prefix, catalog_url in panasonic_resistor_catalogs.items():
        if mpn_upper.startswith(prefix):
            if _download_pdf(catalog_url):
                return True

    # Vishay CRCW thick film resistors — direct catalog PDF
    if mpn_upper.startswith("CRCW"):
        if _download_pdf("https://www.vishay.com/docs/20035/dcrcwe3.pdf"):
            return True

    # TDK MLCCs — try direct datasheet URL patterns
    if re.match(r'^C\d{4}', mpn_upper):
        # TDK uses product-specific URLs but also has a general catalog
        if _download_pdf(f"https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/en/mlcc_automotive_general_en.pdf"):
            return True

    # TDK inductors/ferrites (VLP, MPZ)
    if mpn_upper.startswith(("VLP", "MPZ")):
        if _download_pdf(f"https://product.tdk.com/system/files/dam/doc/product/inductor/inductor/smd/catalog/inductor_automotive_power_vlp_en.pdf"):
            return True

    # Molex connectors — predictable PDF URL pattern
    if re.match(r'^00\d{8}$', mpn):
        # Molex drawing URL: https://www.molex.com/pdm_docs/sd/<part>_sd.pdf
        if _download_pdf(f"https://www.molex.com/pdm_docs/sd/{mpn}_sd.pdf"):
            return True

    # Würth Elektronik
    if re.match(r'^74\d{7}', mpn):
        if _scrape_page(f"https://www.we-online.com/en/components/products/{mpn}"):
            return True

    return False


def try_fetcher(source: str, mpn: str) -> bool:
    """Try downloading a datasheet using a distributor fetcher."""
    fetcher = FETCHERS.get(source)
    if not fetcher or not fetcher.exists():
        return False

    pdf_path = DATASHEETS_DIR / f"{safe_filename(mpn)}.pdf"

    try:
        result = subprocess.run(
            [sys.executable, str(fetcher), "--search", mpn, "-o", str(pdf_path), "--json"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0 and pdf_path.exists() and pdf_path.stat().st_size > 1000:
            return True
    except Exception:
        pass

    # Clean up failed download
    if pdf_path.exists() and pdf_path.stat().st_size <= 1000:
        pdf_path.unlink()
    return False


def print_status(status: dict, entries: list):
    """Print download status summary."""
    total = len(entries)
    downloaded = sum(1 for s in status.values() if s.get("downloaded"))
    failed = sum(1 for s in status.values() if not s.get("downloaded"))
    pending = total - len(status)

    print(f"Total MPNs: {total}")
    print(f"Downloaded: {downloaded}")
    print(f"Failed:     {failed}")
    print(f"Pending:    {pending}")

    if downloaded:
        by_source = {}
        for s in status.values():
            if s.get("downloaded"):
                src = s.get("source", "unknown")
                by_source[src] = by_source.get(src, 0) + 1
        print("\nBy source:")
        for src, count in sorted(by_source.items()):
            print(f"  {src}: {count}")


def download_one(entry: dict, sources: list[str]) -> dict:
    """Download a single datasheet. Returns result dict."""
    mpn = entry["mpn"]

    for source in sources:
        if source == "url":
            ds_url = entry.get("datasheet", "")
            if try_direct_url(ds_url, mpn):
                return {"mpn": mpn, "downloaded": True, "source": "direct_url"}
        elif source == "lcsc_direct":
            lcsc_id = entry.get("lcsc", "")
            if try_lcsc_direct(lcsc_id, mpn):
                return {"mpn": mpn, "downloaded": True, "source": "lcsc_direct"}
        elif source == "mfr_scrape":
            if try_manufacturer_scrape(mpn):
                return {"mpn": mpn, "downloaded": True, "source": "mfr_scrape"}
        else:
            if try_fetcher(source, mpn):
                return {"mpn": mpn, "downloaded": True, "source": source}

    return {"mpn": mpn, "downloaded": False, "tried": sources}


def main():
    parser = argparse.ArgumentParser(description="Download datasheets for extracted MPNs")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max number of new downloads (0=unlimited)")
    parser.add_argument("--project", help="Only download for a specific project")
    parser.add_argument("--status", action="store_true",
                        help="Show download status and exit")
    parser.add_argument("--sources", default="url,lcsc_direct,digikey,mouser,lcsc,element14,mfr_scrape",
                        help="Comma-separated list of sources to try")
    parser.add_argument("--input", default=str(EXTRACTED_MPNS),
                        help="Input extracted MPNs JSON file")
    parser.add_argument("--workers", type=int, default=8,
                        help="Number of parallel download workers (default: 8)")
    parser.add_argument("--retry", action="store_true",
                        help="Retry previously failed MPNs")
    args = parser.parse_args()

    input_file = Path(args.input)
    if not input_file.exists():
        print(f"Error: {input_file} not found. Run extract_mpns.py first.")
        sys.exit(1)

    entries = json.loads(input_file.read_text())

    if args.project:
        entries = [e for e in entries if e["source_project"] == args.project]

    DATASHEETS_DIR.mkdir(parents=True, exist_ok=True)
    status = load_status()

    if args.status:
        print_status(status, entries)
        return

    sources = [s.strip() for s in args.sources.split(",")]

    # Filter to entries that need downloading
    todo = []
    skipped = 0
    for entry in entries:
        mpn = entry["mpn"]
        if pdf_exists(mpn):
            skipped += 1
            continue
        if mpn in status and not status[mpn].get("downloaded") and not args.retry:
            skipped += 1
            continue
        todo.append(entry)

    if args.limit:
        todo = todo[:args.limit]

    print(f"=== Downloading datasheets ===")
    print(f"MPNs: {len(todo)} to download, {skipped} skipped, {args.workers} workers")
    print(f"Sources: {', '.join(sources)}")
    print()

    downloaded = 0
    failed = 0
    status_lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(download_one, entry, sources): entry for entry in todo}

        for future in as_completed(futures):
            result = future.result()
            mpn = result["mpn"]

            with status_lock:
                status[mpn] = {k: v for k, v in result.items() if k != "mpn"}
                if result["downloaded"]:
                    downloaded += 1
                    print(f"  OK [{downloaded + failed}] {mpn} ({result['source']})")
                else:
                    failed += 1
                    print(f"FAIL [{downloaded + failed}] {mpn}")
                save_status(status)

    print()
    print(f"=== Results ===")
    print(f"Downloaded: {downloaded}")
    print(f"Skipped:    {skipped} (already done)")
    print(f"Failed:     {failed}")
    print_status(status, entries)


if __name__ == "__main__":
    main()
