#!/usr/bin/env python3
"""Validate extracted MPNs against DigiKey and Mouser APIs.

Searches each MPN on both distributors and records whether it was found,
the matched MPN, manufacturer, and datasheet URL. Outputs a clean test
set of MPNs that are findable on at least one distributor.

Usage:
    python3 validate_mpns.py [--limit N] [--output validated_mpns.json]

Environment:
    DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET
    MOUSER_SEARCH_API_KEY
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent


def get_digikey_token():
    client_id = os.environ.get("DIGIKEY_CLIENT_ID", "")
    client_secret = os.environ.get("DIGIKEY_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return None, None
    try:
        data = urllib.parse.urlencode({
            "client_id": client_id, "client_secret": client_secret,
            "grant_type": "client_credentials",
        }).encode()
        req = urllib.request.Request(
            "https://api.digikey.com/v1/oauth2/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            token = json.loads(resp.read()).get("access_token", "")
        return token, client_id
    except Exception as e:
        print(f"DigiKey auth failed: {e}", file=sys.stderr)
        return None, None


def search_digikey(mpn: str, token: str, client_id: str) -> dict | None:
    body = json.dumps({"Keywords": mpn, "Limit": 3, "Offset": 0}).encode()
    req = urllib.request.Request(
        "https://api.digikey.com/products/v4/search/keyword",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-DIGIKEY-Client-Id": client_id,
            "Authorization": f"Bearer {token}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
        products = data.get("Products", [])
        if not products:
            return None
        mpn_upper = mpn.upper()
        for p in products:
            if p.get("ManufacturerProductNumber", "").upper() == mpn_upper:
                return {
                    "mpn": p["ManufacturerProductNumber"],
                    "manufacturer": p.get("Manufacturer", {}).get("Name", ""),
                    "datasheet_url": p.get("DatasheetUrl", ""),
                    "description": p.get("Description", {}).get("ProductDescription", ""),
                    "in_stock": p.get("QuantityAvailable", 0),
                    "exact_match": True,
                }
        p = products[0]
        return {
            "mpn": p.get("ManufacturerProductNumber", ""),
            "manufacturer": p.get("Manufacturer", {}).get("Name", ""),
            "datasheet_url": p.get("DatasheetUrl", ""),
            "description": p.get("Description", {}).get("ProductDescription", ""),
            "in_stock": p.get("QuantityAvailable", 0),
            "exact_match": False,
        }
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("  DigiKey rate limited, waiting 5s...", file=sys.stderr)
            time.sleep(5)
            return search_digikey(mpn, token, client_id)
        return None
    except Exception:
        return None


def search_mouser(mpn: str, api_key: str) -> dict | None:
    url = f"https://api.mouser.com/api/v1/search/partnumber?apiKey={api_key}"
    body = json.dumps({
        "SearchByPartRequest": {
            "mouserPartNumber": mpn,
            "partSearchOptions": "Exact",
        }
    }).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
        parts = (data.get("SearchResults") or {}).get("Parts", [])
        if not parts:
            return None
        mpn_upper = mpn.upper()
        for p in parts:
            if p.get("ManufacturerPartNumber", "").upper() == mpn_upper:
                return {
                    "mpn": p["ManufacturerPartNumber"],
                    "manufacturer": p.get("Manufacturer", ""),
                    "datasheet_url": p.get("DataSheetUrl", ""),
                    "description": p.get("Description", ""),
                    "in_stock": int(p.get("AvailabilityInStock", "0") or "0"),
                    "exact_match": True,
                }
        p = parts[0]
        return {
            "mpn": p.get("ManufacturerPartNumber", ""),
            "manufacturer": p.get("Manufacturer", ""),
            "datasheet_url": p.get("DataSheetUrl", ""),
            "description": p.get("Description", ""),
            "in_stock": int(p.get("AvailabilityInStock", "0") or "0"),
            "exact_match": False,
        }
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Validate MPNs against distributor APIs")
    parser.add_argument("--input", default=str(HARNESS_DIR / "results" / "extracted_mpns.json"),
                        help="Input JSON file with extracted MPNs")
    parser.add_argument("--limit", type=int, default=0, help="Limit MPNs to validate (0=all)")
    parser.add_argument("--output", "-o", default=str(HARNESS_DIR / "results" / "validated_mpns.json"),
                        help="Output JSON file path")
    args = parser.parse_args()

    with open(args.input) as f:
        extracted = json.load(f)

    # Deduplicate by MPN
    seen = set()
    unique = []
    for entry in extracted:
        mpn = entry["mpn"].strip()
        if mpn not in seen:
            seen.add(mpn)
            unique.append(entry)

    if args.limit:
        unique = unique[:args.limit]

    print(f"Validating {len(unique)} unique MPNs...", file=sys.stderr)

    dk_token, dk_client_id = get_digikey_token()
    mouser_key = os.environ.get("MOUSER_SEARCH_API_KEY", "")

    results = []
    for i, entry in enumerate(unique):
        mpn = entry["mpn"]
        sys.stderr.write(f"\r  [{i+1}/{len(unique)}] {mpn:40s}")
        sys.stderr.flush()

        dk_result = None
        mouser_result = None

        if dk_token:
            dk_result = search_digikey(mpn, dk_token, dk_client_id)
            time.sleep(0.3)

        if mouser_key:
            mouser_result = search_mouser(mpn, mouser_key)
            time.sleep(0.3)

        result = {
            "mpn": mpn,
            "source_manufacturer": entry.get("manufacturer", ""),
            "source_project": entry.get("source_project", ""),
            "digikey": dk_result,
            "mouser": mouser_result,
        }
        results.append(result)

    print(file=sys.stderr)

    both = dk_only = mouser_only = neither = 0
    for r in results:
        dk_exact = r["digikey"] and r["digikey"]["exact_match"]
        mo_exact = r["mouser"] and r["mouser"]["exact_match"]
        if dk_exact and mo_exact:
            both += 1
        elif dk_exact:
            dk_only += 1
        elif mo_exact:
            mouser_only += 1
        else:
            neither += 1

    print(f"\nResults (exact matches):", file=sys.stderr)
    print(f"  Both distributors: {both}", file=sys.stderr)
    print(f"  DigiKey only:      {dk_only}", file=sys.stderr)
    print(f"  Mouser only:       {mouser_only}", file=sys.stderr)
    print(f"  Neither:           {neither}", file=sys.stderr)

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
