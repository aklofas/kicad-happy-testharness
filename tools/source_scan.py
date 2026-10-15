#!/usr/bin/env python3
"""Shared recursive source walker for every harness scanner (report A2).

Owns: product file discovery, root-relative paths, finding emit-site
extraction under the literal-tag policy (tools/SCANNER_POLICY.md), the
exception ledger (tools/scan_exceptions.json) and the coverage snapshot /
diff used by `check`. Never imports or evals product code: ast only.
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


def iter_product_sources(product_root: Path) -> list[Path]:
    """Every *.py under skills/**/scripts/** (recursive), sorted, no __pycache__."""
    root = Path(product_root)
    out: list[Path] = []
    for scripts_dir in sorted(root.glob("skills/*/scripts")) + sorted(root.glob("skills/*/*/scripts")):
        if not scripts_dir.is_dir():
            continue
        for p in scripts_dir.rglob("*.py"):
            if not p.is_file() or "__pycache__" in p.relative_to(root).parts:
                continue
            out.append(p)
    return sorted(set(out), key=lambda p: rel(root, p))


def rel(product_root: Path, path: Path) -> str:
    """Root-relative POSIX path (the identity used in every scanner output)."""
    return Path(path).resolve().relative_to(Path(product_root).resolve()).as_posix()


def parse_source(path: Path) -> ast.Module:
    """Parse honouring PEP 263 coding cookies / BOM: feed bytes, not text."""
    return ast.parse(Path(path).read_bytes(), filename=str(path))


FACTORY_NAMES = ("make_finding", "_make_finding")
TAG_KEYWORDS = ("detector", "rule_id", "schema_era")
DET_ENUM_FILE = "skills/kicad/scripts/finding_schema.py"


@dataclass(frozen=True)
class EmitSite:
    file: str
    line: int
    callee: str
    detector: str | None
    rule_id: str | None
    schema_era: str | None
    resolved: bool
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


def _callee_name(call: ast.Call) -> str | None:
    f = call.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _str_literal(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def resolve_det_enum(product_root: Path) -> dict[str, str]:
    """Literal `NAME = 'value'` members of class Det in finding_schema.py. No import."""
    path = Path(product_root) / DET_ENUM_FILE
    if not path.exists():
        return {}
    tree = parse_source(path)
    out: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Det":
            for stmt in node.body:
                if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                        and isinstance(stmt.targets[0], ast.Name)):
                    val = _str_literal(stmt.value)
                    if val is not None:
                        out[stmt.targets[0].id] = val
    return out


def _is_emit_call(call: ast.Call, callee: str | None) -> bool:
    if callee in FACTORY_NAMES:
        return True
    kws = {k.arg for k in call.keywords if k.arg}
    return all(k in kws for k in TAG_KEYWORDS)


def emit_sites(product_root: Path, path: Path,
               det_enum: dict[str, str] | None = None) -> list[EmitSite]:
    """Every finding emit site in `path` under the literal-tag policy."""
    file_rel = rel(product_root, path)
    tree = parse_source(path)
    sites: list[EmitSite] = []
    for call in ast.walk(tree):
        if not isinstance(call, ast.Call):
            continue
        callee = _callee_name(call)
        if not _is_emit_call(call, callee):
            continue
        kws = {k.arg: k.value for k in call.keywords if k.arg}
        reasons: list[str] = []
        detector = rule_id = era = None

        if "detector" not in kws and "rule_id" not in kws and callee == "_make_finding" \
                and len(call.args) >= 3:
            cat = _str_literal(call.args[0])
            rid = _str_literal(call.args[2])
            detector = f"emc_{cat}" if cat is not None else None
            rule_id = rid
            sites.append(EmitSite(file_rel, call.lineno, callee, detector, rule_id, None,
                                  False, "positional-emc"))
            continue
        if callee == "_make_finding" and call.args and ("detector" in kws or "rule_id" in kws):
            sites.append(EmitSite(file_rel, call.lineno, callee, None, _str_literal(kws.get("rule_id")),
                                  _str_literal(kws.get("schema_era")), False,
                                  "positional-emc:mixed-shape"))
            continue

        dnode = kws.get("detector")
        if dnode is None:
            reasons.append("detector:absent")
        elif _str_literal(dnode) is not None:
            detector = _str_literal(dnode)
        elif isinstance(dnode, ast.Attribute) and isinstance(dnode.value, ast.Name) \
                and dnode.value.id == "Det":
            if det_enum and dnode.attr in det_enum:
                detector = det_enum[dnode.attr]
                reasons.append("detector:enum-attribute-resolved")
            else:
                reasons.append("detector:enum-attribute")
        else:
            reasons.append("detector:nonliteral")

        rnode = kws.get("rule_id")
        if rnode is None:
            reasons.append("rule_id:absent")
        elif _str_literal(rnode) is not None:
            rule_id = _str_literal(rnode)
        else:
            reasons.append("rule_id:nonliteral")

        enode = kws.get("schema_era")
        if enode is not None:
            era = _str_literal(enode)
            if era is None:
                reasons.append("schema_era:nonliteral")

        hard = [r for r in reasons if r != "detector:enum-attribute-resolved"]
        resolved = detector is not None and rule_id is not None and not hard
        sites.append(EmitSite(file_rel, call.lineno, callee or "<expr>", detector, rule_id,
                              era, resolved, ";".join(reasons)))
    return sites


EXCEPTIONS_PATH = Path(__file__).resolve().parent / "scan_exceptions.json"


def load_exceptions(path: Path | None = None) -> dict:
    p = Path(path) if path else EXCEPTIONS_PATH
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("version") != 1 or "exceptions" not in data:
        raise ValueError(f"{p}: not a version-1 scan_exceptions file")
    return data


def apply_exceptions(sites: list[EmitSite], exceptions: dict
                     ) -> tuple[list[EmitSite], dict[str, int], list[str]]:
    """Absorb unresolved sites matched by an exception (file+callee+reason).

    Returns (still_unresolved, matched_counts_by_exception_id, violations).
    A violation is an exception matching more sites than its recorded count,
    or matching zero sites (a stale entry that must be removed).
    """
    counts: dict[str, int] = {e["id"]: 0 for e in exceptions["exceptions"]}
    remaining: list[EmitSite] = []
    for s in sites:
        if s.resolved and s.reason == "":
            continue          # fully literal site: nothing to absorb
        matched = None
        for e in exceptions["exceptions"]:
            if s.file == e["file"] and s.callee == e["callee"] and s.reason == e["reason"]:
                matched = e
                break
        if matched is None:
            remaining.append(s)
            continue
        counts[matched["id"]] += 1
    violations: list[str] = []
    for e in exceptions["exceptions"]:
        n = counts[e["id"]]
        if n > e["count"]:
            violations.append(f"exception {e['id']} grew: matched {n} > recorded {e['count']}")
        if n == 0:
            violations.append(f"exception {e['id']} matched 0 sites (stale entry; remove it)")
    return remaining, counts, violations


HARNESS_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = HARNESS_ROOT / "reference" / "scan_coverage_baseline.json"


def _product_sha(product_root: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(product_root), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _constants(product_root: Path) -> list[str]:
    sys.path.insert(0, str(HARNESS_ROOT / "validate"))
    import audit_constants  # noqa: E402  (harness module, not product)
    return sorted({f"{r['file']}|{r['scope']}|{r['name']}"
                   for r in audit_constants.iter_constant_records(product_root)})


def _equations(product_root: Path) -> dict[str, str]:
    sys.path.insert(0, str(HARNESS_ROOT / "validate"))
    import audit_equations  # noqa: E402
    return {e["eq_id"]: e["file"] for e in audit_equations.iter_equations(product_root)}


def coverage_snapshot(product_root: Path, exceptions: dict | None = None) -> dict:
    root = Path(product_root)
    exceptions = exceptions or load_exceptions()
    enum = resolve_det_enum(root)
    files = iter_product_sources(root)
    sites = [s for p in files for s in emit_sites(root, p, enum)]
    remaining, counts, violations = apply_exceptions(sites, exceptions)
    emit: dict[str, int] = {}
    for s in sites:
        if s.resolved:
            key = f"{s.detector}|{s.rule_id}"
        elif s in remaining:
            continue
        else:
            key = f"<unresolved>|{s.reason}|{s.file}"
        emit[key] = emit.get(key, 0) + 1
    return {
        "snapshot_version": 1,
        "product_sha": _product_sha(root),
        "files": [rel(root, p) for p in files],
        "emit_sites": dict(sorted(emit.items())),
        "untagged_era_sites": sum(1 for s in sites if s.resolved and s.schema_era is None),
        "unresolved": [s.to_dict() for s in remaining],
        "exception_counts": counts,
        "exception_violations": violations,
        "eq_ids": dict(sorted(_equations(root).items())),
        "constants": _constants(root),
    }


def coverage_diff(baseline: dict, current: dict) -> dict:
    lost_sites = sorted(k for k, n in baseline["emit_sites"].items()
                        if current["emit_sites"].get(k, 0) < n)
    out = {
        "lost_files": sorted(set(baseline["files"]) - set(current["files"])),
        "lost_sites": lost_sites,
        "lost_eq": sorted(set(baseline["eq_ids"]) - set(current["eq_ids"])),
        "lost_constants": sorted(set(baseline["constants"]) - set(current["constants"])),
        "unresolved": current["unresolved"],
        "exception_violations": current["exception_violations"],
        "new_untagged_era": max(0, current["untagged_era_sites"] - baseline["untagged_era_sites"]),
    }
    out["clean"] = not any(out[k] for k in ("lost_files", "lost_sites", "lost_eq", "lost_constants",
                                            "unresolved", "exception_violations")) \
        and out["new_untagged_era"] == 0
    return out


def _print_diff(d: dict) -> None:
    for key in ("lost_files", "lost_sites", "lost_eq", "lost_constants", "exception_violations"):
        for item in d[key]:
            print(f"  {key}: {item}")
    for s in d["unresolved"]:
        print(f"  unresolved: {s['file']}:{s['line']} {s['callee']} {s['reason']}")
    if d["new_untagged_era"]:
        print(f"  new emit sites without schema_era: {d['new_untagged_era']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "snapshot", "sites"):
        p = sub.add_parser(name)
        p.add_argument("--product", required=True, type=Path)
        p.add_argument("--exceptions", type=Path, default=None)
    sub.choices["check"].add_argument("--baseline", type=Path, default=BASELINE_PATH)
    sub.choices["check"].add_argument("--accept-baseline", action="store_true")
    sub.choices["snapshot"].add_argument("-o", "--output", type=Path, default=BASELINE_PATH)
    sub.choices["sites"].add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = args.product
    if not (root / "skills").is_dir():
        print(f"error: {root} has no skills/ directory", file=sys.stderr)
        return 2
    exceptions = load_exceptions(args.exceptions) if args.exceptions else load_exceptions()

    if args.cmd == "sites":
        enum = resolve_det_enum(root)
        sites = [s for p in iter_product_sources(root) for s in emit_sites(root, p, enum)]
        if args.json:
            print(json.dumps([s.to_dict() for s in sites], indent=1))
        else:
            for s in sites:
                flag = "ok " if s.resolved else "UNR"
                print(f"{flag} {s.file}:{s.line} {s.callee} {s.detector} {s.rule_id} {s.schema_era} {s.reason}")
        return 0

    current = coverage_snapshot(root, exceptions)
    if args.cmd == "snapshot":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(current, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {args.output} ({len(current['files'])} files, "
              f"{sum(current['emit_sites'].values())} sites, {len(current['eq_ids'])} EQ, "
              f"{len(current['constants'])} constants)")
        return 0

    if not args.baseline.exists():
        print(f"error: baseline {args.baseline} missing; run `snapshot` first", file=sys.stderr)
        return 2
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    d = coverage_diff(baseline, current)
    print(f"scan coverage vs {args.baseline.name} (baseline sha {baseline['product_sha'][:7]}, "
          f"current {current['product_sha'][:7]})")
    _print_diff(d)
    if d["clean"]:
        print("CLEAN")
        return 0
    if args.accept_baseline and not d["unresolved"] and not d["exception_violations"]:
        args.baseline.write_text(json.dumps(current, indent=1) + "\n", encoding="utf-8")
        print(f"ACCEPTED: baseline rewritten at {args.baseline}")
        return 0
    print("FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
