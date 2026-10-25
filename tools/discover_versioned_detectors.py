#!/usr/bin/env python3
"""Discover versioned detector functions from kicad-happy analyzer source.

AST-parses (via tools/source_scan.py) $KICAD_HAPPY_DIR/skills/kicad/scripts/**/*.py for emit-sites of
callables with detector=<str>, rule_id=<str>, AND schema_era=<target>
keywords. The detector literal is what each finding self-declares and is
what regression assertions match via detector_filter; it is also what
private helpers (e.g. _make_ex_001) use when the enclosing function name
diverges from the finding's detector field.

Groups by the explicit detector literal. Emits
regression/v{N}_changed_detectors.json with per-detector rule_ids,
primary rule, source files, gating summary. Grouping uses the emitted
detector literal, never the enclosing function name.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source_scan  # noqa: E402  (harness sibling module)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harnesslib.source_audit import sources  # noqa: E402


def _resolve_kicad_happy() -> Path:
    raw = os.environ.get("KICAD_HAPPY_DIR")
    if raw:
        return Path(raw)
    # Fallback: sibling directory relative to this repo root
    return Path(__file__).resolve().parent.parent.parent / "kicad-happy"


def _scripts_dir(kicad_happy: Path) -> Path:
    return kicad_happy / "skills" / "kicad" / "scripts"


def _git_commit_and_branch(repo: Path) -> tuple[str, str]:
    try:
        commit = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        branch = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return commit, branch
    except subprocess.CalledProcessError:
        return "unknown", "unknown"


def _collect_detector_rule_pairs(kicad_happy: Path, source_path: Path, era: str,
                                 det_enum: dict[str, str]) -> tuple[list[tuple[str, str]], list[dict]]:
    """(resolved (detector, rule_id) pairs tagged with `era`, unresolved site records)."""
    pairs: list[tuple[str, str]] = []
    unresolved: list[dict] = []
    for s in source_scan.emit_sites(kicad_happy, source_path, det_enum):
        if not s.resolved:
            if s.reason == "positional-emc" and s.detector and s.rule_id:
                # EMC's positional _make_finding(category, severity, rule_id, ...) carries the
                # era in **extra; the scanner keeps the site unresolved for coverage but
                # resolves detector/rule_id, which is all discovery needs
                if s.schema_era == era:
                    pairs.append((s.detector, s.rule_id))
            elif s.reason != "positional-emc":
                unresolved.append({"file": s.file, "line": s.line, "callee": s.callee,
                                   "reason": s.reason})
            continue
        if s.schema_era == era:
            pairs.append((s.detector, s.rule_id))
    pairs.extend(_dict_literal_pairs(source_path, era))
    return pairs, unresolved


def _dict_literal_pairs(source_path: Path, era: str) -> list[tuple[str, str]]:
    """Findings built as dict literals (RS-001 / PP-001 in signal_detectors) with literal
    ``detector``, ``rule_id`` and ``schema_era`` keys; the scanner's call walk cannot see them."""
    out: list[tuple[str, str]] = []
    for node in ast.walk(source_scan.parse_source(source_path)):
        if not isinstance(node, ast.Dict):
            continue
        lit = {}
        for k, v in zip(node.keys, node.values):
            key = sources.str_literal(k) if k is not None else None
            if key in ("detector", "rule_id", "schema_era"):
                lit[key] = sources.str_literal(v)
        if lit.get("detector") and lit.get("rule_id") and lit.get("schema_era") == era:
            out.append((lit["detector"], lit["rule_id"]))
    return out


def _fallback_summary(detector: str, era: str, rules: list[str]) -> str:
    return f"{detector} versioned in {era} (rules: {','.join(rules)})"


def discover(kicad_happy: Path, era: str,
             gating_notes: dict[str, str] | None = None) -> dict:
    """Run AST discovery and return the output dict."""
    scripts = _scripts_dir(kicad_happy)
    if not scripts.exists():
        raise FileNotFoundError(f"kicad-happy scripts dir not found: {scripts}")

    detector_data: dict[str, dict] = defaultdict(
        lambda: {"rules": set(), "source_files": set(), "emit_line_count": 0}
    )
    det_enum = source_scan.resolve_det_enum(kicad_happy)
    files = list(source_scan.iter_product_sources(kicad_happy))   # every skills/*/scripts tree (EMC emits too)
    scanned = [source_scan.rel(kicad_happy, p) for p in files]
    unresolved_sites: list[dict] = []
    for path in files:
        pairs, unresolved = _collect_detector_rule_pairs(kicad_happy, path, era, det_enum)
        unresolved_sites.extend(unresolved)
        relp = source_scan.rel(kicad_happy, path)
        for detector, rule_id in pairs:
            detector_data[detector]["rules"].add(rule_id)
            detector_data[detector]["source_files"].add(relp)
            detector_data[detector]["emit_line_count"] += 1

    # Typo-check: every non-metadata gating-notes key must be a discovered detector
    if gating_notes:
        real_keys = {k for k in gating_notes if not k.startswith("_")}
        unknown = real_keys - set(detector_data.keys())
        if unknown:
            raise ValueError(
                f"gating-notes keys reference unknown detectors: {sorted(unknown)}"
            )

    commit, branch = _git_commit_and_branch(kicad_happy)

    detectors: dict[str, dict] = {}
    for detector_name in sorted(detector_data):
        rules_sorted = sorted(detector_data[detector_name]["rules"])
        source_files = sorted(detector_data[detector_name]["source_files"])
        summary = None
        if gating_notes:
            summary = gating_notes.get(detector_name)
        if not summary:
            summary = _fallback_summary(detector_name, era, rules_sorted)
        detectors[detector_name] = {
            "rules": rules_sorted,
            "primary_rule": rules_sorted[0],
            "source_file": source_files[0] if len(source_files) == 1 else ",".join(source_files),
            "emit_line_count": detector_data[detector_name]["emit_line_count"],
            "gating_summary": summary,
        }

    return {
        "era": era,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "kicad_happy_commit": commit,
        "kicad_happy_branch": branch,
        "source_files_scanned": sorted(scanned),
        "source_files_scanned_count": len(scanned),
        "unresolved_sites": sorted(unresolved_sites, key=lambda u: (u["file"], u["line"])),
        "detectors": detectors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--era", required=True,
                        help="Target era (e.g. v1.4). Determines schema_era= filter.")
    parser.add_argument("--gating-notes", type=Path, default=None,
                        help="Hand-curated {detector: summary} JSON merged into output.")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output JSON path. Default: regression/v{era_short}_changed_detectors.json")
    args = parser.parse_args()

    kicad_happy = _resolve_kicad_happy()
    try:
        kicad_happy.resolve(strict=True)
    except (FileNotFoundError, OSError):
        print(f"ERROR: KICAD_HAPPY_DIR not found: {kicad_happy}", file=sys.stderr)
        return 1

    gating_notes = None
    if args.gating_notes:
        gating_notes = json.loads(args.gating_notes.read_text())

    try:
        result = discover(kicad_happy, args.era, gating_notes=gating_notes)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.output:
        out_path = args.output
    else:
        era_short = args.era.lstrip("v").replace(".", "")
        out_path = Path(__file__).resolve().parent.parent / "regression" / f"v{era_short}_changed_detectors.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n")

    branch = result["kicad_happy_branch"]
    if args.era == "v1.4" and branch not in ("v1.4-dev", "main"):
        print(f"WARN: discovered against branch {branch!r} (expected v1.4-dev or main)",
              file=sys.stderr)

    n_detectors = len(result["detectors"])
    n_rules = sum(len(d["rules"]) for d in result["detectors"].values())
    n_files = len(result["source_files_scanned"])
    print(f"Discovered {n_detectors} versioned detectors, "
          f"{n_rules} total rule_ids, "
          f"from {n_files} source files")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
