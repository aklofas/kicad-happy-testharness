#!/usr/bin/env python3
"""Verify analyzer constants against DigiKey parametric data.

For constants with part-number-like keys (e.g., _REGULATOR_VREF, known_freqs,
_iq_estimates_uA), looks up the part on DigiKey and compares stored values
against datasheet parametric data where available.

Usage:
    python3 validate/verify_constants_online.py --dry-run
    python3 validate/verify_constants_online.py --limit 10
    python3 validate/verify_constants_online.py --constant _REGULATOR_VREF
    python3 validate/verify_constants_online.py --json
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import DATA_DIR

REGISTRY_FILE = DATA_DIR / "constants_registry.json"

# Constants that have part-number-keyed entries worth verifying
VERIFIABLE_CONSTANTS = {
    "_REGULATOR_VREF": "reference_voltage",
    "known_freqs": "switching_frequency",
    "_iq_estimates_uA": "quiescent_current",
}


def get_digikey_token():
    """Get OAuth token for DigiKey API."""
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


def search_digikey(mpn, token, client_id):
    """Search DigiKey for a part and return parametric data."""
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
        # Prefer exact match
        mpn_upper = mpn.upper()
        for p in products:
            if p.get("ManufacturerProductNumber", "").upper().startswith(mpn_upper):
                return p
        return products[0]
    except Exception:
        return None


def extract_parametric(product, param_type):
    """Extract a parametric value from a DigiKey product response."""
    params = product.get("Parameters", [])
    if not params:
        return None

    # Map param_type to DigiKey parameter name substrings
    param_names = {
        "reference_voltage": ["voltage - output (min", "reference voltage",
                              "voltage - output", "feedback voltage"],
        "switching_frequency": ["frequency - switching", "switching frequency"],
        "quiescent_current": ["current - quiescent", "quiescent current",
                              "current - supply"],
    }

    target_names = param_names.get(param_type, [])
    for p in params:
        pname = (p.get("ParameterText", "") or p.get("Parameter", "")).lower()
        if any(t in pname for t in target_names):
            val_text = p.get("ValueText", "") or p.get("Value", "")
            return val_text

    return None


def load_verifiable_entries(constant_filter=None):
    """Load constants registry and extract verifiable entries.

    Returns list of {constant_name, mpn_prefix, stored_value, param_type}.
    """
    if not REGISTRY_FILE.exists():
        return []

    data = json.loads(REGISTRY_FILE.read_text())
    entries = []

    for c in data.get("constants", []):
        name = c.get("name", "")
        if name not in VERIFIABLE_CONSTANTS:
            continue
        if constant_filter and name != constant_filter:
            continue

        param_type = VERIFIABLE_CONSTANTS[name]
        for key, val_info in c.get("entries", {}).items():
            # Skip non-MPN keys (pure numbers, single chars)
            if not any(ch.isalpha() for ch in key) or len(key) < 2:
                continue
            stored = val_info.get("value") if isinstance(val_info, dict) else val_info
            if stored is None:
                continue
            entries.append({
                "constant_name": name,
                "mpn_prefix": key,
                "stored_value": stored,
                "param_type": param_type,
                "status": val_info.get("status", "unknown") if isinstance(val_info, dict) else "unknown",
            })

    return entries


def main():
    parser = argparse.ArgumentParser(
        description="Verify constants against DigiKey parametric data")
    parser.add_argument("--constant", help="Only verify this constant name")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max entries to check (0=all)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be checked without API calls")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    entries = load_verifiable_entries(args.constant)
    if not entries:
        print("No verifiable entries found", file=sys.stderr)
        sys.exit(1)

    if args.limit:
        entries = entries[:args.limit]

    print(f"Verifiable entries: {len(entries)}")
    by_const = {}
    for e in entries:
        by_const.setdefault(e["constant_name"], []).append(e)
    for name, items in by_const.items():
        print(f"  {name}: {len(items)} entries ({VERIFIABLE_CONSTANTS[name]})")

    if args.dry_run:
        print("\nDry run — would query DigiKey for:")
        for e in entries[:20]:
            print(f"  {e['mpn_prefix']}: stored {e['param_type']}={e['stored_value']}")
        if len(entries) > 20:
            print(f"  ... and {len(entries) - 20} more")
        return

    # Authenticate
    token, client_id = get_digikey_token()
    if not token:
        print("Error: DigiKey authentication failed. "
              "Set DIGIKEY_CLIENT_ID and DIGIKEY_CLIENT_SECRET.", file=sys.stderr)
        sys.exit(1)

    # Query each entry
    results = []
    for i, e in enumerate(entries):
        product = search_digikey(e["mpn_prefix"], token, client_id)
        time.sleep(0.3)  # Rate limit

        if not product:
            results.append({**e, "digikey_value": None, "match": "not_found"})
            continue

        actual_mpn = product.get("ManufacturerProductNumber", "")
        dk_val_text = extract_parametric(product, e["param_type"])

        results.append({
            **e,
            "digikey_mpn": actual_mpn,
            "digikey_value_text": dk_val_text,
            "match": "found" if dk_val_text else "no_param",
        })

        if (i + 1) % 10 == 0:
            print(f"  Checked {i+1}/{len(entries)}...", file=sys.stderr)

    if args.json:
        json.dump(results, sys.stdout, indent=2)
        print()
        return

    # Text summary
    found = sum(1 for r in results if r["match"] == "found")
    not_found = sum(1 for r in results if r["match"] == "not_found")
    no_param = sum(1 for r in results if r["match"] == "no_param")

    print(f"\nResults: {found} found with parameter, "
          f"{no_param} found without parameter, {not_found} not found")

    if found:
        print(f"\nVerifiable entries:")
        for r in results:
            if r["match"] == "found":
                print(f"  {r['mpn_prefix']}: stored={r['stored_value']} "
                      f"digikey=\"{r['digikey_value_text']}\" "
                      f"(matched {r.get('digikey_mpn', '?')})")


if __name__ == "__main__":
    main()
