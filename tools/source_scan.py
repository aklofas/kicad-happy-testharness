#!/usr/bin/env python3
"""Shared recursive source walker for every harness scanner (report A2).

Owns: product file discovery, root-relative paths, finding emit-site
extraction under the literal-tag policy (tools/SCANNER_POLICY.md), the
exception ledger (tools/scan_exceptions.json) and the coverage snapshot /
diff used by `check`. Never imports or evals product code: ast only.
"""
from __future__ import annotations

import ast
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


import json

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
            if not s.resolved:
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
