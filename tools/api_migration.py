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


HARNESS_CODE_DIRS = ("tests", "regression", "run", "tools", "validate", "integration")


def _dotted_from_owner(owner: str) -> str:
    parts = Path(owner).with_suffix("").parts
    if "scripts" in parts:
        parts = parts[parts.index("scripts") + 1:]
    else:
        parts = parts[2:]          # skills/<skill>/<pkg>/... -> <pkg>...
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _load_relocations(path: Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rel = data["relocations"] if isinstance(data, dict) else data
    for r in rel:
        for k in ("symbol", "old_owner", "new_owner", "new_name"):
            if k not in r:
                raise ValueError(f"relocation missing {k!r}: {r}")
        r.setdefault("facade_until", None)
    return rel


def sites_for(inventory: dict, module: str, symbol: str) -> list[dict]:
    for mod in inventory["modules"]:
        if mod["module"] != module:
            continue
        for sym in mod["symbols"]:
            if sym["symbol"] == symbol:
                return list(sym.get("sites", []))
    return []


def plan_edits(inventory: dict, relocations: list[dict]) -> list[dict]:
    edits = []
    for r in relocations:
        module, _, symbol = r["symbol"].rpartition(".")
        for site in sites_for(inventory, module, symbol):
            edits.append({"file": site["file"], "line": site["line"], "kind": site.get("kind", ""),
                          "module": module, "symbol": symbol,
                          "new_owner": r["new_owner"], "new_name": r["new_name"],
                          "new_module": _dotted_from_owner(r["new_owner"]),
                          "facade_until": r.get("facade_until")})
    return sorted(edits, key=lambda e: (e["file"], e["line"]))


def _harness_py_files(harness_root: Path):
    root = Path(harness_root)
    yield from sorted(root.glob("*.py"))
    for d in HARNESS_CODE_DIRS:
        base = root / d
        if base.is_dir():
            yield from sorted(p for p in base.rglob("*.py") if "__pycache__" not in p.parts)


def scan_harness_imports(harness_root: Path) -> list[dict]:
    """Static census of (module, symbol) the harness binds to: imports, patch.object,
    patch('mod.sym'), monkeypatch.setattr(mod, 'sym', ...)."""
    out = []
    root = Path(harness_root)
    for py in _harness_py_files(root):
        try:
            tree = ast.parse(py.read_bytes(), filename=str(py))
        except SyntaxError:
            continue
        relf = py.relative_to(root).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                for a in node.names:
                    out.append({"file": relf, "line": node.lineno, "module": node.module, "symbol": a.name})
            elif isinstance(node, ast.Import):
                for a in node.names:
                    out.append({"file": relf, "line": node.lineno, "module": a.name, "symbol": "<module>"})
            elif isinstance(node, ast.Call):
                fn = node.func
                name = fn.attr if isinstance(fn, ast.Attribute) else fn.id if isinstance(fn, ast.Name) else None
                if name == "object" and isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) \
                        and fn.value.id == "patch" and len(node.args) >= 2 \
                        and isinstance(node.args[0], ast.Name) and isinstance(node.args[1], ast.Constant):
                    out.append({"file": relf, "line": node.lineno, "module": node.args[0].id,
                                "symbol": node.args[1].value})
                elif name == "setattr" and isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) \
                        and fn.value.id == "monkeypatch" and len(node.args) >= 2 \
                        and isinstance(node.args[0], ast.Name) and isinstance(node.args[1], ast.Constant):
                    out.append({"file": relf, "line": node.lineno, "module": node.args[0].id,
                                "symbol": node.args[1].value})
                elif name == "patch" and node.args and isinstance(node.args[0], ast.Constant) \
                        and isinstance(node.args[0].value, str) and "." in node.args[0].value:
                    mod, _, sym = node.args[0].value.rpartition(".")
                    out.append({"file": relf, "line": node.lineno, "module": mod, "symbol": sym})
    return out


def check(dispositions: dict, harness_imports: list[dict]) -> list[str]:
    bound = {}
    for h in harness_imports:
        bound.setdefault((h["module"], h["symbol"]), []).append(f"{h['file']}:{h['line']}")
    violations = []
    for e in dispositions["entries"]:
        key = (e["module"], e["symbol"])
        if e["disposition"] == "retire" and key in bound:
            violations.append(f"{e['module']}.{e['symbol']} is retire but still bound at {bound[key]}")
        if e["status"] == "done" and e.get("new_owner") and key in bound:
            violations.append(f"{e['module']}.{e['symbol']} done -> {e['new_owner']} but still "
                              f"imported from old owner at {bound[key]}")
    return violations


def cmd_status(args) -> int:
    d = json.loads(Path(args.dispositions).read_text(encoding="utf-8"))
    by = {}
    for e in d["entries"]:
        by.setdefault((e["disposition"], e["status"]), 0)
        by[(e["disposition"], e["status"])] += 1
    print(f"{len(d['entries'])} symbols @ {d['product_sha'][:7]}")
    for (disp, st), n in sorted(by.items()):
        print(f"  {disp:14s} {st:5s} {n}")
    return 0


def cmd_apply_map(args) -> int:
    inv = load_inventory(args.inventory)
    rel = _load_relocations(args.map)
    known = {(m["module"], s["symbol"]) for m in inv["modules"] for s in m["symbols"]}
    bad = False
    for r in rel:
        module, _, symbol = r["symbol"].rpartition(".")
        if (module, symbol) not in known:
            print(f"error: {r['symbol']} not in inventory", file=sys.stderr)
            bad = True
        if args.product and not (Path(args.product) / r["new_owner"]).exists():
            print(f"error: {r['symbol']}: new_owner {r['new_owner']} does not exist under {args.product}",
                  file=sys.stderr)
            bad = True
    if bad:
        return 2
    edits = plan_edits(inv, rel)
    if args.json:
        print(json.dumps(edits, indent=1))
    else:
        for e in edits:
            print(f"{e['file']}:{e['line']:<5} {e['kind']:14s} {e['module']}.{e['symbol']} "
                  f"-> {e['new_module']}.{e['new_name']}")
        print(f"{len(edits)} sites to edit")
    return 0


def cmd_check(args) -> int:
    d = json.loads(Path(args.dispositions).read_text(encoding="utf-8"))
    v = check(d, scan_harness_imports(HARNESS_ROOT))
    for line in v:
        print(f"  {line}")
    print("CLEAN" if not v else f"FAIL ({len(v)} violations)")
    return 0 if not v else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init-dispositions")
    p.add_argument("--inventory", type=Path, default=INVENTORY_PATH)
    p.add_argument("-o", "--output", type=Path, default=DISPOSITIONS_PATH)
    p = sub.add_parser("status")
    p.add_argument("--dispositions", type=Path, default=DISPOSITIONS_PATH)
    p = sub.add_parser("apply-map")
    p.add_argument("map", type=Path)
    p.add_argument("--inventory", type=Path, default=INVENTORY_PATH)
    p.add_argument("--product", type=Path, default=None)
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("check")
    p.add_argument("--dispositions", type=Path, default=DISPOSITIONS_PATH)
    args = ap.parse_args(argv)
    return {"init-dispositions": cmd_init, "status": cmd_status,
            "apply-map": cmd_apply_map, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
