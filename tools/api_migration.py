#!/usr/bin/env python3
"""Adopt the product API inventory as the per-symbol migration checklist (A1).

Commands:
  init-dispositions   generate reference/product_api/dispositions.json from the inventory
  status              counts by disposition/status
  apply-map MAP.json  list every harness site to edit for a round's relocations
  check               no harness site still targets an old owner for `done` entries;
                      `retire`d symbols have zero remaining sites
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import sys
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[1]
API_DIR = HARNESS_ROOT / "reference" / "product_api"
INVENTORY_PATH = API_DIR / "inventory_6a91aaa.json"
DISPOSITIONS_PATH = API_DIR / "dispositions.json"

KEEP_CONTRACT_MODULES = (
    "analyzer_envelope", "finding_schema", "schema_codec", "kicad_types",
    "capability_mode", "run_id", "inputs_builder", "datasheet_types", "datasheet_types.*",
    "_mini_jsonschema", "detection_schema",
)
RETIRE_SYMBOLS = {
    ("finding_schema", "_apply_severity_tuning"),
    ("finding_schema", "normalize_severity"),
}
RETIRE_NAME_FRAGMENTS = ("enrich_from_hierarchy", "build_hierarchy_context")


def load_inventory(path: Path = INVENTORY_PATH) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "modules" not in data or "product_head" not in data:
        raise ValueError(f"{path}: not an API inventory")
    return data


def iter_symbols(inventory: dict) -> list[dict]:
    out = []
    for mod in inventory["modules"]:
        for sym in mod["symbols"]:
            out.append({"module": mod["module"], "symbol": sym["symbol"],
                        "private": bool(sym.get("private")), "sites": len(sym.get("sites", [])),
                        "files": sorted(sym.get("files", [])),
                        "product_paths": list(mod.get("product_paths", []))})
    return out


def initial_disposition(module: str, symbol: str, private: bool) -> str:
    if (module, symbol) in RETIRE_SYMBOLS or any(f in symbol for f in RETIRE_NAME_FRAGMENTS):
        return "retire"
    if private:                      # spec §4.4: every underscore entry migrates
        return "migrate"
    if any(fnmatch.fnmatchcase(module, pat) for pat in KEEP_CONTRACT_MODULES):
        return "keep-contract"
    return "undecided"


def build_dispositions(inventory: dict) -> dict:
    entries = []
    for s in iter_symbols(inventory):
        entries.append({"module": s["module"], "symbol": s["symbol"],
                        "disposition": initial_disposition(s["module"], s["symbol"], s["private"]),
                        "new_owner": None, "round": None, "status": "open", "sites": s["sites"]})
    return {"version": 1, "inventory": INVENTORY_PATH.name,
            "product_sha": inventory["product_head"], "entries": entries}


def cmd_init(args) -> int:
    inv = load_inventory(args.inventory)
    d = build_dispositions(inv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(d, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {args.output}: {len(d['entries'])} entries")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init-dispositions")
    p.add_argument("--inventory", type=Path, default=INVENTORY_PATH)
    p.add_argument("-o", "--output", type=Path, default=DISPOSITIONS_PATH)
    args = ap.parse_args(argv)
    if args.cmd == "init-dispositions":
        return cmd_init(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
