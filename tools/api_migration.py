#!/usr/bin/env python3
"""Adopt the product API inventory as the per-symbol migration checklist (A1).

Commands:
  init-dispositions   generate reference/product_api/dispositions.json from the inventory
  status              counts by disposition/status
  apply-map MAP.json  list every harness site to edit for a round's relocations
  check               no harness site still targets an old owner for `done` entries;
                      `retire`d symbols have zero remaining sites; a done/retire entry on
                      the binding blind list is UNVERIFIABLE (exit 1)
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from round_record import normalize_relocations  # noqa: E402  (sibling in tools/)

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


HARNESS_CODE_DIRS = ("tests", "regression", "run", "tools", "validate", "integration", "harnesslib")
# Product-imitation trees (fake products the scanners walk), not harness code.
# Helper modules elsewhere under tests/ (tests/fixtures/_build_ctx.py,
# tests/datasheets/fixtures/*.py) are harness code and stay in scope.
EXCLUDED_TREES = ("tests/fixtures/h0/",)
BLIND_LIST_PATH = API_DIR / "binding_blind_list.json"


def _dotted_from_owner(owner: str) -> str:
    parts = Path(owner).with_suffix("").parts
    if "scripts" in parts:
        parts = parts[parts.index("scripts") + 1:]
    else:
        parts = parts[2:]          # skills/<skill>/<pkg>/... -> <pkg>...
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _product_shape_flags(path: Path) -> list[bool]:
    """Per entry: True for the product shape {old, new, ...} (aligned with normalize_relocations)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rel = data["relocations"] if isinstance(data, dict) else data
    return [isinstance(r, dict) and "old" in r and "new" in r for r in rel]


def _load_relocations(path: Path, inventory: dict | None = None) -> list[dict]:
    """Record-shape or product-shape relocations (round_record.normalize_relocations)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return normalize_relocations(data, inventory if inventory is not None else load_inventory())


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
            yield from sorted(p for p in base.rglob("*.py")
                              if "__pycache__" not in p.parts
                              and not any(p.relative_to(root).as_posix().startswith(t)
                                          for t in EXCLUDED_TREES))


def _raw_dotted(node):
    """Dotted name of a Name/Attribute chain (no alias resolution), else None."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return ".".join(reversed(parts))


def _chain(node, aliases):
    """Dotted names of a Name/Attribute chain, its root resolved via aliases
    (name -> set of modules); [] when the chain is not rooted at a Name."""
    raw = _raw_dotted(node)
    if raw is None:
        return []
    head, _, rest = raw.partition(".")
    return [m + ("." + rest if rest else "") for m in sorted(aliases.get(head, {head}))]


def _is_patch_name(node) -> bool:
    return (isinstance(node, ast.Name) and node.id == "patch") or \
           (isinstance(node, ast.Attribute) and node.attr == "patch")


def _inventory_index(inventory: dict | None):
    """(module set, product-file basename -> module) from the inventory."""
    if inventory is None:
        inventory = load_inventory() if INVENTORY_PATH.exists() else {"modules": []}
    modules = {m["module"] for m in inventory["modules"]}
    by_file: dict[str, set] = {}
    for m in inventory["modules"]:
        for pp in m.get("product_paths", []):
            by_file.setdefault(Path(pp).name, set()).add(m["module"])
    return modules, by_file


def _str_literals(node, assigns, depth=0):
    """String constants in an expression, following Name -> module assignment."""
    out = []
    if depth > 4 or node is None:
        return out
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            out.append(sub.value)
        elif isinstance(sub, ast.Name) and sub.id in assigns:
            for v in assigns[sub.id]:
                out.extend(_str_literals(v, assigns, depth + 1))
    return out


def _spec_modules(call, assigns, by_file):
    """Module(s) a spec_from_file_location(name, path) call loads: the inventory
    module owning the path's file when it resolves, else the literal name."""
    found = set()
    if len(call.args) >= 2:
        for lit in _str_literals(call.args[1], assigns):
            found |= by_file.get(Path(lit).name, set())
    if not found and call.args and isinstance(call.args[0], ast.Constant) \
            and isinstance(call.args[0].value, str):
        found.add(call.args[0].value)
    return found


def _is_fixture(fn) -> bool:
    for d in fn.decorator_list:
        target = d.func if isinstance(d, ast.Call) else d
        raw = _raw_dotted(target)
        if raw and raw.rsplit(".", 1)[-1] == "fixture":
            return True
    return False


def _build_aliases(tree, modules, by_file):
    """Local name -> set of product modules it is bound to in this file.

    Sources: `import X [as a]`; `from P import M [as a]` when `P.M` is an
    inventory module; `a = importlib.util.module_from_spec(spec)` where
    `spec = spec_from_file_location(...)`; `a = importlib.import_module("lit")`;
    a function whose body returns an aliased name, through `a = fn()` or, for
    a pytest fixture, its same-named parameter. Bindings are file-global by name, so a
    name reused for two modules binds both (over-binding fails loud in check).
    """
    aliases: dict[str, set] = {}
    assigns: dict[str, list] = {}
    dynamic: list[tuple[int, str]] = []     # (line, module) loaded via importlib

    def add(name, mods):
        if mods:
            aliases.setdefault(name, set()).update(mods)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.asname:
                    add(a.asname, {a.name})
                else:
                    add(a.name.split(".")[0], {a.name.split(".")[0]})
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for a in node.names:
                full = f"{node.module}.{a.name}"
                if full in modules:
                    add(a.asname or a.name, {full})
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            assigns.setdefault(node.targets[0].id, []).append(node.value)
    specs: dict[str, set] = {}
    calls = [(n.targets[0].id, n.value) for n in ast.walk(tree)
             if isinstance(n, ast.Assign) and len(n.targets) == 1
             and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Call)]
    for name, call in calls:
        fn = (_raw_dotted(call.func) or "").rsplit(".", 1)[-1]
        if fn == "spec_from_file_location":
            specs.setdefault(name, set()).update(_spec_modules(call, assigns, by_file))
        elif fn == "import_module" and call.args and isinstance(call.args[0], ast.Constant) \
                and isinstance(call.args[0].value, str):
            add(name, {call.args[0].value})
            dynamic.append((call.lineno, call.args[0].value))
    for name, call in calls:
        fn = (_raw_dotted(call.func) or "").rsplit(".", 1)[-1]
        if fn == "module_from_spec" and call.args and isinstance(call.args[0], ast.Name):
            mods = specs.get(call.args[0].id, set())
            add(name, mods)
            dynamic.extend((call.lineno, m) for m in sorted(mods))
    returners: dict[str, set] = {}          # function returning an aliased module
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for r in ast.walk(fn):
                if isinstance(r, ast.Return) and isinstance(r.value, ast.Name) \
                        and r.value.id in aliases:
                    returners.setdefault(fn.name, set()).update(aliases[r.value.id])
            if fn.name in returners and _is_fixture(fn):
                add(fn.name, returners[fn.name])   # injected as a same-named parameter
    for name, call in calls:
        if isinstance(call.func, ast.Name) and call.func.id in returners:
            add(name, returners[call.func.id])     # x = _load_module()
    return aliases, dynamic


def _symbol_aliases(tree, modules):
    """`from M import N [as a]` (N not itself a module) -> {a: {(M, N)}}, so
    `a.x` reads as the inventory's dotted symbol `N.x` of M."""
    out: dict[str, set] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for a in node.names:
                if a.name != "*" and f"{node.module}.{a.name}" not in modules:
                    out.setdefault(a.asname or a.name, set()).add((node.module, a.name))
    return out


def _split_module(dotted, modules):
    """Every (module, symbol) reading of a dotted chain: the root alone, plus
    each longer prefix that is an inventory module (dotted packages)."""
    parts = dotted.split(".")
    out = []
    for k in range(1, len(parts)):
        mod = ".".join(parts[:k])
        if k == 1 or mod in modules:
            out.append((mod, ".".join(parts[k:])))
    return out


def scan_harness_imports(harness_root: Path, inventory: dict | None = None) -> list[dict]:
    """Static census of (module, symbol) the harness binds to. Covers import
    statements; patch.object / mock.patch.object, patch('mod.sym') and
    monkeypatch.setattr(mod, 'sym', ...) targets; getattr(mod, 'sym'); and
    attribute chains rooted at a module binding (see _build_aliases). Names
    bound only at runtime (a module passed in through an ordinary parameter,
    a computed attribute name) stay invisible: reference/product_api/
    binding_blind_list.json records which inventory symbols that leaves
    unbound, and `check` refuses to verify a done/retire entry on it."""
    modules, by_file = _inventory_index(inventory)
    out = []
    root = Path(harness_root)
    for py in _harness_py_files(root):
        try:
            tree = ast.parse(py.read_bytes(), filename=str(py))
        except SyntaxError:
            continue
        relf = py.relative_to(root).as_posix()
        aliases, dynamic = _build_aliases(tree, modules, by_file)
        sym_aliases = _symbol_aliases(tree, modules)

        def emit(line, module, symbol):
            out.append({"file": relf, "line": line, "module": module, "symbol": symbol})

        for line, mod in dynamic:
            emit(line, mod, "<module>")
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                for a in node.names:
                    emit(node.lineno, node.module, a.name)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    emit(node.lineno, a.name, "<module>")
            elif isinstance(node, ast.Attribute):
                raw = _raw_dotted(node)
                head, _, rest = (raw or "").partition(".")
                if head in aliases:
                    for m in sorted(aliases[head]):
                        dotted = m + ("." + rest if rest else "")
                        seen = set()
                        for mod, sym in _split_module(dotted, modules):
                            seen.add((mod, sym))
                            emit(node.lineno, mod, sym)
                        # the alias's own module boundary: a dotted module the inventory
                        # does not list (a v3 package such as schematic.pipeline) still
                        # binds (module, attr) exactly as `from m import attr` would
                        if rest and (m, rest) not in seen:
                            emit(node.lineno, m, rest)
                for mod, name in sorted(sym_aliases.get(head, ())):
                    emit(node.lineno, mod, f"{name}.{rest}")
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            target = None            # (module-expr node, symbol)
            if isinstance(fn, ast.Attribute) and fn.attr == "object" and _is_patch_name(fn.value) \
                    and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                target = (node.args[0], node.args[1].value)
            elif isinstance(fn, ast.Attribute) and fn.attr == "setattr" \
                    and isinstance(fn.value, ast.Name) and fn.value.id == "monkeypatch" \
                    and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                target = (node.args[0], node.args[1].value)
            elif isinstance(fn, ast.Name) and fn.id == "getattr" and len(node.args) >= 2 \
                    and isinstance(node.args[1], ast.Constant):
                target = (node.args[0], node.args[1].value)
            elif _is_patch_name(fn) and node.args and isinstance(node.args[0], ast.Constant) \
                    and isinstance(node.args[0].value, str) and "." in node.args[0].value:
                mod, _, sym = node.args[0].value.rpartition(".")
                emit(node.lineno, mod, sym)
                continue
            if target and isinstance(target[1], str):
                for dotted in _chain(target[0], aliases):
                    emit(node.lineno, dotted.rsplit(".", 1)[-1], target[1])
                    # a dotted module absent from the inventory (a v3 package such as
                    # pcb.presentation) binds the patch target exactly as the attribute
                    # branch reads `alias.attr` (round-5 patch_targets)
                    if "." in dotted:
                        emit(node.lineno, dotted, target[1])
    return out


def _still_referenced(harness_root: Path, module: str, symbol: str, files: list[str]) -> bool:
    """True when any inventory site file still mentions the symbol's name.

    The inventory is frozen; a round that deletes every site of a symbol (a
    retired consumer) leaves inventory sites behind that no longer exist.
    Those are gone, not blind."""
    if symbol == "<module>":
        # `analyze_pcb.py` in a subprocess path or a docstring names the file, not the
        # module: only `analyze_pcb` followed by anything but `.py` is a reference
        token = module.rsplit(".", 1)[-1]
        pat = re.compile(r"\b" + re.escape(token) + r"\b(?!\.py\b)")
        hit = pat.search
    else:
        token = symbol.split(".")[0]
        hit = lambda text: token in text  # noqa: E731
    for f in files:
        p = Path(harness_root) / f
        try:
            if hit(p.read_text(encoding="utf-8", errors="replace")):
                return True
        except OSError:
            continue
    return False


def blind_symbols(inventory: dict, harness_imports: list[dict],
                  harness_root: Path = HARNESS_ROOT, skip: set | None = None,
                  aliases: dict | None = None) -> list[list[str]]:
    """Inventory (module, symbol) pairs the scanner cannot fully see: some
    inventory site file still mentions the symbol but holds zero scanner
    bindings of it. Per file, so one visible site cannot mask a dynamic one.
    `skip` holds keys to ignore outright. `aliases` maps an old key to the
    (new_module, new_name) a `done` relocation moved it to: a site file that
    binds the NEW key counts as covered, so migrated entries are not flagged,
    while a done entry whose old-owner site is still dynamically bound stays
    visible (it would otherwise pass `check` as CLEAN — the F2 failure mode)."""
    bound: dict[tuple, set] = {}
    for h in harness_imports:
        bound.setdefault((h["module"], h["symbol"]), set()).add(h["file"])
    skip = skip or set()
    aliases = aliases or {}
    out = []
    for m in inventory["modules"]:
        for s in m["symbols"]:
            key = (m["module"], s["symbol"])
            if not s.get("sites") or key in skip:
                continue
            covered = set(bound.get(key, set()))
            if key in aliases:
                covered |= bound.get(tuple(aliases[key]), set())
            files = sorted({x["file"] for x in s["sites"]} - covered)
            if any(_still_referenced(harness_root, *key, [f]) for f in files):
                out.append(list(key))
    return sorted(out)


def done_keys(dispositions: dict) -> set:
    return {(e["module"], e["symbol"]) for e in dispositions["entries"] if e["status"] == "done"}


def done_aliases(dispositions: dict) -> dict:
    """{(module, symbol): (new_module, new_name)} for every `done` entry with a new_owner."""
    out = {}
    for e in dispositions["entries"]:
        if e.get("status") == "done" and e.get("new_owner"):
            out[(e["module"], e["symbol"])] = (_dotted_from_owner(e["new_owner"]),
                                               e.get("new_name") or e["symbol"])
    return out


def load_blind_list(path: Path = BLIND_LIST_PATH) -> set:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("version") != 1 or "blind" not in data:
        raise ValueError(f"{path}: not a version-1 binding blind list")
    return {tuple(x) for x in data["blind"]}


def check(dispositions: dict, harness_imports: list[dict], blind: set | None = None) -> list[str]:
    """Violations; a done/retire entry the scanner cannot see (on the blind
    list) is UNVERIFIABLE rather than silently clean."""
    blind = blind or set()
    bound = {}
    for h in harness_imports:
        bound.setdefault((h["module"], h["symbol"]), []).append(f"{h['file']}:{h['line']}")
    violations = []
    for e in dispositions["entries"]:
        key = (e["module"], e["symbol"])
        if (e["disposition"] == "retire" or e["status"] == "done") and key in blind:
            violations.append(f"{e['module']}.{e['symbol']} UNVERIFIABLE (dynamic binding; "
                              "verify with apply-map)")
            continue
        if e["disposition"] == "retire" and key in bound:
            violations.append(f"{e['module']}.{e['symbol']} is retire but still bound at {bound[key]}")
        if e["status"] == "done" and e.get("new_owner") and key in bound:
            violations.append(f"{e['module']}.{e['symbol']} done -> {e['new_owner']} but still "
                              f"imported from old owner at {bound[key]}")
    return violations


def _defined_names(path: Path) -> set | None:
    """Top-level names a module defines or imports (None when it cannot be parsed)."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names |= {t.id for t in targets if isinstance(t, ast.Name)}
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names |= {(a.asname or a.name).split(".")[0] for a in node.names}
    return names


def missing_destinations(dispositions: dict, product_root: Path) -> list[str]:
    """`done` migrations whose destination does not exist in the product: the new owner file,
    and the symbol in it (module-level `<module>` entries need only the file)."""
    out = []
    for e in dispositions["entries"]:
        if e.get("status") != "done" or not e.get("new_owner"):
            continue
        dest = Path(product_root) / e["new_owner"]
        name = e.get("new_name") or e["symbol"]
        if not dest.is_file():
            out.append(f"{e['module']}.{e['symbol']} done -> {e['new_owner']}: file missing")
            continue
        if name == "<module>":
            continue
        names = _defined_names(dest)
        if names is None or name.split(".")[0] not in names:
            out.append(f"{e['module']}.{e['symbol']} done -> {e['new_owner']}: {name} not defined there")
    return out


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
    try:
        rel = _load_relocations(args.map, inv)
        product_shape = _product_shape_flags(args.map)
    except (ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    known = {(m["module"], s["symbol"]) for m in inv["modules"] for s in m["symbols"]}
    bad = False
    for r in rel:
        if args.product and not (Path(args.product) / r["new_owner"]).exists():
            print(f"error: {r['symbol']}: new_owner {r['new_owner']} does not exist under {args.product}",
                  file=sys.stderr)
            bad = True
    if bad:
        return 2
    # a product-shape map lists everything it moved: names the harness never bound have no sites
    # (skipped, one note); a record-shape entry is hand-written, so an unknown symbol is a typo
    kept, skipped = [], 0
    for r, prod in zip(rel, product_shape):
        if tuple(r["symbol"].rpartition(".")[::2]) in known:
            kept.append(r)
        elif prod:
            skipped += 1
        else:
            print(f"error: {r['symbol']} not in inventory", file=sys.stderr)
            bad = True
    if skipped:
        print(f"note: {skipped} relocations name symbols the harness never bound (skipped)", file=sys.stderr)
    if bad:
        return 2
    rel = kept
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
    imports = scan_harness_imports(HARNESS_ROOT)
    live = {tuple(k) for k in blind_symbols(load_inventory(), imports, HARNESS_ROOT, aliases=done_aliases(d))}
    v = check(d, imports, load_blind_list(args.blind_list) | live)
    if args.product:
        v += missing_destinations(d, args.product)
    for line in v:
        print(f"  {line}")
    print("CLEAN" if not v else f"FAIL ({len(v)} violations)")
    return 0 if not v else 1


def _default_product():
    env = os.environ.get("KICAD_HAPPY_DIR")
    return Path(env) if env else None


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
    p.add_argument("--blind-list", type=Path, default=BLIND_LIST_PATH)
    p.add_argument("--product", type=Path, default=_default_product(),
                   help="product tree whose migration destinations must exist "
                        "(default: $KICAD_HAPPY_DIR when set)")
    args = ap.parse_args(argv)
    return {"init-dispositions": cmd_init, "status": cmd_status,
            "apply-map": cmd_apply_map, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
