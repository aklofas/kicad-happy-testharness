#!/usr/bin/env python3
"""Discover versioned detector functions from kicad-happy analyzer source.

AST-parses $KICAD_HAPPY_DIR/skills/kicad/scripts/*.py for emit-sites of
callables with detector=<str>, rule_id=<str>, AND schema_era=<target>
keywords. The detector literal is what each finding self-declares and is
what regression assertions match via detector_filter; it is also what
private helpers (e.g. _make_ex_001) use when the enclosing function name
diverges from the finding's detector field.

Groups by the explicit detector literal. Emits
regression/v{N}_changed_detectors.json with per-detector rule_ids,
primary rule, source files, gating summary.

Design: docs/superpowers/specs/2026-05-16-a8-schema-era-tagging-design.md §4
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


def _collect_detector_rule_pairs(source_path: Path, era: str) -> list[tuple[str, str]]:
    """Return list of (detector, rule_id) for every emit-site whose call
    has detector=<str>, rule_id=<str>, AND schema_era=<era> keywords.

    Walks every Call in the module, not just those inside detector-prefixed
    functions, so emit-sites inside private helpers (e.g. _make_ex_001)
    are captured. Grouping by the explicit `detector=` literal matches
    what regression assertions filter on, which decouples discovery from
    the helper's function name.
    """
    tree = ast.parse(source_path.read_text())
    pairs: list[tuple[str, str]] = []
    for call in ast.walk(tree):
        if not isinstance(call, ast.Call):
            continue
        detector = None
        rule_id = None
        schema_era_val = None
        for kw in call.keywords:
            if kw.arg == "detector" and isinstance(kw.value, ast.Constant):
                detector = kw.value.value
            elif kw.arg == "rule_id" and isinstance(kw.value, ast.Constant):
                rule_id = kw.value.value
            elif kw.arg == "schema_era" and isinstance(kw.value, ast.Constant):
                schema_era_val = kw.value.value
        if detector and rule_id and schema_era_val == era:
            pairs.append((detector, rule_id))
    return pairs


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
    scanned: list[str] = []

    for path in sorted(scripts.glob("*.py")):
        pairs = _collect_detector_rule_pairs(path, era)
        if not pairs:
            continue
        scanned.append(path.name)
        for detector, rule_id in pairs:
            detector_data[detector]["rules"].add(rule_id)
            detector_data[detector]["source_files"].add(path.name)
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
