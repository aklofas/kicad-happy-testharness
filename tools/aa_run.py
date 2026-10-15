#!/usr/bin/env python3
"""A/A run: same product SHA in both gate slots, strict compare, volatile-leaf report.

Usage:
  python3 tools/aa_run.py --product "$KICAD_HAPPY_DIR" --gate-dir results/v3_baseline/aa_smoke \
      --cross-section smoke --jobs 32 [--profile standard] [--propose-policy]

Writes <gate-dir>/field_report.json (the gate's field_report_strict.json when present, else
from compare_snap_trees) and <gate-dir>/aa_report.json.
With --propose-policy also writes <gate-dir>/volatile-leaves-v1-proposed.json for HUMAN
review; it never edits regression/normalization/*.json.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[1]
GATE = HARNESS_ROOT / "regression" / "run_corpus_gate.py"
COMPARE = HARNESS_ROOT / "regression" / "compare_snap_trees.py"
POLICY_DIR = HARNESS_ROOT / "regression" / "normalization"

_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")
_INDEX = re.compile(r"/\d+(?=/|$)")


def generalize_pointer(path: str) -> str:
    return _INDEX.sub("/*", path)


def guess_shape(values: list) -> str:
    kinds = set()
    for v in values:
        if isinstance(v, bool):
            kinds.add("mixed")
        elif isinstance(v, (int, float)):
            kinds.add("number")
        elif isinstance(v, str):
            if _UUID.match(v):
                kinds.add("uuid")
            elif _ISO.match(v):
                kinds.add("iso8601")
            elif v.startswith("/") and "/" in v[1:]:
                kinds.add("abs_path")
            else:
                kinds.add("string")
        else:
            kinds.add("mixed")
    return kinds.pop() if len(kinds) == 1 else "mixed"


def summarize_strict_report(report: dict) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for d in report.get("deltas", []):
        groups[generalize_pointer(d["path"])].append(d)
    leaves = []
    for glob, ds in sorted(groups.items()):
        values = [d.get("before") for d in ds] + [d.get("after") for d in ds]
        leaves.append({
            "pointer_glob": glob,
            "unit_count": len({d["unit"] for d in ds}),
            "delta_count": len(ds),
            "ops": dict(Counter(d["op"] for d in ds)),
            "shape": guess_shape([v for v in values if v is not None]),
            "examples": [{"unit": d["unit"], "path": d["path"], "before": d.get("before"),
                          "after": d.get("after")} for d in ds[:3]],
        })
    return {
        "report_version": 1,
        "source_report": {"mode": report.get("mode"), "policy": report.get("policy"),
                          "a_root": report.get("a_root"), "b_root": report.get("b_root")},
        "units_compared": report.get("summary", {}).get("compared", 0),
        "clean": not report.get("deltas") and not report.get("policy_violations"),
        "leaves": leaves,
        "policy_violations": list(report.get("policy_violations", [])),
    }


_SHAPE_RULE = {"uuid": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
               "iso8601": "iso8601", "number": "number", "abs_path": "strip_root_prefix",
               "string": "string", "mixed": "mixed"}


def propose_policy(aa_report: dict, policy: dict) -> dict:
    known = set()
    for leaf in policy.get("leaves", []):
        key = leaf.get("pointer") or leaf.get("pointer_glob")
        if key:
            known.add(key)
    added = []
    for leaf in aa_report["leaves"]:
        glob = leaf["pointer_glob"]
        if glob in known:
            continue
        entry = {("pointer_glob" if "*" in glob else "pointer"): glob,
                 "shape": _SHAPE_RULE[leaf["shape"]],
                 "observed_units": leaf["unit_count"], "observed_deltas": leaf["delta_count"]}
        if leaf["shape"] == "abs_path":
            entry["rewrite"] = "strip_root_prefix"
        if leaf["shape"] == "number" and leaf["unit_count"] == 1:
            entry["review"] = "singleton numeric leaf — likely a determinism bug, not a volatile leaf"
        elif leaf["shape"] in ("string", "mixed"):
            entry["review"] = "non-volatile-looking shape — confirm before accepting"
        added.append(entry)
    return {"name": f"{policy['name']}-proposed", "added": added,
            "existing": sorted(known), "note": "review each 'added' entry; never auto-accept"}


def build_commands(*, product_dir: Path, gate_dir: Path, selection: list[str], jobs: int,
                   profile: str) -> tuple[list[str], list[str]]:
    gate = [sys.executable, str(GATE), "--baseline-dir", str(product_dir), "--candidate-dir",
            str(product_dir), "--gate-dir", str(gate_dir), "--kind", "aa", "--profile", profile,
            "--jobs", str(jobs), *selection]
    cmp = [sys.executable, str(COMPARE), str(gate_dir / "baseline"), str(gate_dir / "candidate"),
           "--mode", "strict", "--policy", "volatile-leaves-v1", "-o", str(gate_dir / "field_report.json")]
    return gate, cmp


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--product", required=True, help="product worktree (same SHA used for both slots)")
    ap.add_argument("--gate-dir", required=True)
    ap.add_argument("--profile", default="standard")
    ap.add_argument("--jobs", type=int, default=32)
    sel = ap.add_mutually_exclusive_group(required=True)
    sel.add_argument("--repo")
    sel.add_argument("--cross-section")
    sel.add_argument("--repo-list")
    ap.add_argument("--propose-policy", action="store_true")
    ap.add_argument("--skip-run", action="store_true", help="only summarize an existing field_report.json")
    args = ap.parse_args(argv)

    gate_dir = Path(args.gate_dir).resolve()
    selection = (["--repo", args.repo] if args.repo else
                 ["--cross-section", args.cross_section] if args.cross_section else
                 ["--repo-list", args.repo_list])
    gate_cmd, cmp_cmd = build_commands(product_dir=Path(args.product).resolve(), gate_dir=gate_dir,
                                       selection=selection, jobs=args.jobs, profile=args.profile)
    if not args.skip_run:
        gate_dir.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(gate_cmd)
        if r.returncode == 2:
            print("gate usage/identity error", file=sys.stderr)
            return 2
    strict = gate_dir / "field_report_strict.json"
    if strict.exists():
        shutil.copyfile(strict, gate_dir / "field_report.json")
    elif not args.skip_run:
        r = subprocess.run(cmp_cmd)
        if r.returncode == 2:
            print("compare error", file=sys.stderr)
            return 2
    report = json.loads((gate_dir / "field_report.json").read_text(encoding="utf-8"))
    aa = summarize_strict_report(report)
    (gate_dir / "aa_report.json").write_text(json.dumps(aa, indent=2) + "\n", encoding="utf-8")
    print(f"A/A {'CLEAN' if aa['clean'] else 'DELTAS'}: {aa['units_compared']} units, "
          f"{len(aa['leaves'])} differing leaf paths -> {gate_dir / 'aa_report.json'}")
    for leaf in aa["leaves"]:
        print(f"  {leaf['pointer_glob']:50s} units={leaf['unit_count']:6d} shape={leaf['shape']}")
    if args.propose_policy:
        policy = json.loads((POLICY_DIR / "volatile-leaves-v1.json").read_text(encoding="utf-8"))
        prop = propose_policy(aa, policy)
        out = gate_dir / "volatile-leaves-v1-proposed.json"
        out.write_text(json.dumps(prop, indent=2) + "\n", encoding="utf-8")
        print(f"proposed additions ({len(prop['added'])}) -> {out}  [human review required]")
    return 0 if aa["clean"] else 1


if __name__ == "__main__":
    sys.exit(main())
