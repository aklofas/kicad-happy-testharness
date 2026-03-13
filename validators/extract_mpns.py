#!/usr/bin/env python3
"""Extract MPN + Manufacturer pairs from KiCad schematic files."""

import argparse
import json
import re
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent

# Regex to match property lines: (property "Key" "Value" ...)
PROP_RE = re.compile(r'\(property\s+"([^"]+)"\s+"([^"]*)"\s')

# MPN property names
MPN_KEYS = {"MPN", "MPN2", "Manufacturer Part #", "Manufacturer Part",
            "Manufacturer Part Number", "Manufacturer_Part_Number",
            "Manufacturer Product Number "}
# Manufacturer property names (just the mfr name, not part number)
MFR_KEYS = {"Manufacturer", "Manufacturer_Name"}


def is_valid_mpn(mpn: str) -> bool:
    mpn = mpn.strip()
    if not mpn:
        return False
    if "\n" in mpn or "\r" in mpn:
        return False
    if mpn.upper() in ("DNP", "DNA", "N/A", "NA", "TBD", "~", "-", "--", "?", ""):
        return False
    if re.match(r'^MF-(RES|CAP|LED|IND|FER|DIO|TVS)', mpn, re.IGNORECASE):
        return False
    if re.match(r'^[RC]\d{4}\s', mpn):
        return False
    if re.match(r'^\d{1,3}$', mpn):
        return False
    return True


def extract_from_file(filepath: Path):
    """Extract (mpn, manufacturer) pairs from a .kicad_sch file."""
    try:
        content = filepath.read_text(errors='replace')
    except Exception:
        return []

    results = []
    lines = content.split('\n')

    in_symbol = False
    symbol_depth = 0
    symbol_props = {}
    in_lib_symbols = False
    lib_symbols_depth = 0

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('(lib_symbols'):
            in_lib_symbols = True
            lib_symbols_depth = line.count('(') - line.count(')')
            continue

        if in_lib_symbols:
            lib_symbols_depth += line.count('(') - line.count(')')
            if lib_symbols_depth <= 0:
                in_lib_symbols = False
            continue

        if not in_symbol and '(symbol' in stripped and '(lib_id' in stripped:
            in_symbol = True
            symbol_depth = line.count('(') - line.count(')')
            symbol_props = {}
            m = PROP_RE.search(stripped)
            if m:
                symbol_props[m.group(1)] = m.group(2)
            continue

        if in_symbol:
            symbol_depth += line.count('(') - line.count(')')

            m = PROP_RE.search(stripped)
            if m:
                key, value = m.group(1), m.group(2)
                if key not in symbol_props:
                    symbol_props[key] = value

            if symbol_depth <= 0:
                mpn = None
                manufacturer = None

                for mk in ["MPN", "MPN2", "Manufacturer Part Number",
                            "Manufacturer_Part_Number", "Manufacturer Part #",
                            "Manufacturer Part", "Manufacturer Product Number "]:
                    val = symbol_props.get(mk, "").strip()
                    if val:
                        mpn = val
                        break

                for mk in ["Manufacturer", "Manufacturer_Name"]:
                    val = symbol_props.get(mk, "").strip()
                    if val:
                        manufacturer = val
                        break

                if mpn and is_valid_mpn(mpn):
                    results.append((mpn, manufacturer or ""))

                in_symbol = False
                symbol_props = {}

    return results


def get_project_name(filepath: Path, repos_dir: Path) -> str:
    rel = filepath.relative_to(repos_dir)
    return rel.parts[0]


def main():
    parser = argparse.ArgumentParser(description="Extract MPNs from KiCad schematics")
    parser.add_argument("--repos-dir", default=str(HARNESS_DIR / "repos"),
                        help="Directory containing cloned repos")
    parser.add_argument("--output", "-o", default=str(HARNESS_DIR / "results" / "extracted_mpns.json"),
                        help="Output JSON file path")
    args = parser.parse_args()

    repos_dir = Path(args.repos_dir)
    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    seen = set()
    entries = []

    for sch_file in sorted(repos_dir.rglob("*.kicad_sch")):
        project = get_project_name(sch_file, repos_dir)
        pairs = extract_from_file(sch_file)

        for mpn, manufacturer in pairs:
            key = (mpn, manufacturer, project)
            if key not in seen:
                seen.add(key)
                entries.append({
                    "mpn": mpn,
                    "manufacturer": manufacturer,
                    "source_project": project
                })

    entries.sort(key=lambda e: (e["manufacturer"].lower(), e["mpn"].lower()))

    output_file.write_text(json.dumps(entries, indent=2) + "\n")
    print(f"Extracted {len(entries)} unique MPN entries from "
          f"{len(set(e['source_project'] for e in entries))} projects")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
