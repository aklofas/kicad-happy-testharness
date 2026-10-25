#!/usr/bin/env python3
"""A/A run: same product SHA in both gate slots, strict compare, volatile-leaf report.

Usage:
  python3 tools/aa_run.py --product "$KICAD_HAPPY_DIR" --gate-dir results/v3_baseline/aa_smoke \
      --cross-section smoke --jobs 32 [--profile standard] [--propose-policy]

  python3 tools/aa_run.py --fixture-trees RAW_A RAW_B --gate-dir results/v3_baseline/aa_fixtures

Writes <gate-dir>/field_report.json (the gate's field_report_strict.json when present, else
from compare_snap_trees) and <gate-dir>/aa_report.json.
With --propose-policy also writes <gate-dir>/volatile-leaves-v1-proposed.json for HUMAN
review; it never edits regression/normalization/*.json.

Exit codes: 0 A/A CLEAN (strict verdict clean and at least one unit compared), 1 A/A DELTAS,
2 A/A ERROR (strict verdict error: missing or unparseable units, policy violation; or zero
units compared) and usage/run errors.

Fixture A/A (--fixture-trees): pytest --basetemp trees hold <stem>.json analyzer envelopes,
never snap.json, so each tree is first snapified: every *.json whose top-level object has
"analyzer_type" becomes <gate-dir>/{baseline,candidate}/<analyzer_type>/<relpath without
.json>/snap.json (run-dir path segments such as 20261015T101500Z-a1b2c3 or 2026-10-15_1015
are renamed RUN-<n> in sorted order so both sides line up), then the two trees are compared
with the strict policy. Recipe — both sessions at the SAME --basetemp so
embedded tmp paths are identical, moving the tree aside between runs:

  BT=$PWD/results/v3_baseline/aa_fixtures/tmp
  FILES="tests/contract/test_finding_invariants.py tests/contract/test_analysis_dir_contract.py
         tests/contract/test_v14_consumer_matrix.py tests/contract/test_finding_id_coverage_e2e.py"
  SEL='offline_contract or online'   # two of the four files are tier online (read repos/)
  .venv/bin/python -m pytest $FILES -m "$SEL" --basetemp "$BT" -p no:cacheprovider -q
  mv "$BT" results/v3_baseline/aa_fixtures/raw_baseline
  .venv/bin/python -m pytest $FILES -m "$SEL" --basetemp "$BT" -p no:cacheprovider -q
  mv "$BT" results/v3_baseline/aa_fixtures/raw_candidate
  python3 tools/aa_run.py --fixture-trees results/v3_baseline/aa_fixtures/raw_baseline \
      results/v3_baseline/aa_fixtures/raw_candidate --gate-dir results/v3_baseline/aa_fixtures/aa

test_finding_id_coverage_e2e.py consumes the session analysis_dir fixture (tests/contract/
conftest.py), which writes all six analyzers' envelopes (schematic, pcb, gerber, thermal,
emc, cross_analysis); test_analysis_dir_contract.py and test_v14_consumer_matrix.py write
--analysis-dir run trees from the local repos/jgrip/commodorelcd checkout (tier online by
legacy marking; no network); test_finding_invariants.py writes schematic envelopes.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[1]
GATE = HARNESS_ROOT / "regression" / "run_corpus_gate.py"
COMPARE = HARNESS_ROOT / "regression" / "compare_snap_trees.py"
POLICY_DIR = HARNESS_ROOT / "regression" / "normalization"

_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")
_RUN_ID = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{6}$")  # field_compare named shape run_id
_INDEX = re.compile(r"/\d+(?=/|$)")


def generalize_pointer(path: str) -> str:
    # Limitation: any all-digit segment is treated as a list index, so a dict key that is
    # purely digits (e.g. a numeric id used as a key) is also generalized to "*".
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
            "run_id_form": all(isinstance(v, str) and _RUN_ID.match(v)
                               for v in values if v is not None) and any(v is not None for v in values),
            "examples": [{"unit": d["unit"], "path": d["path"], "before": d.get("before"),
                          "after": d.get("after")} for d in ds[:3]],
        })
    return {
        "report_version": 1,
        "source_report": {"mode": report.get("mode"), "policy": report.get("policy"),
                          "a_root": report.get("a_root"), "b_root": report.get("b_root")},
        "units_compared": report.get("summary", {}).get("compared", 0),
        "verdict": report.get("verdict"),
        "missing": report.get("summary", {}).get("missing", 0),
        "parse_errors": report.get("summary", {}).get("parse_errors", 0),
        "clean": report.get("verdict") == "clean" and report.get("summary", {}).get("compared", 0) > 0,
        "error": report.get("verdict") == "error" or report.get("summary", {}).get("compared", 0) == 0,
        "leaves": leaves,
        "policy_violations": list(report.get("policy_violations", [])),
    }


_UUID_RX = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
_METADATA_ROOTS = ("/inputs/", "/capability_mode_ref/", "/elapsed_s")
_OUTSIDE_REVIEW = ("pointer is outside metadata roots; a differing finding or component value "
                   "is a determinism bug \u2014 never auto-mask")


def _shape_for(leaf: dict) -> str | None:
    """Shape vocabulary of regression/field_compare (run_id/number/iso8601/regex); None = omit."""
    shape = leaf["shape"]
    if shape == "uuid":
        # named shape run_id is the timestamp form only; uuids need the explicit regex
        return "run_id" if leaf.get("run_id_form") else _UUID_RX
    if leaf.get("run_id_form"):
        return "run_id"
    if shape in ("iso8601", "number"):
        return shape
    return None  # abs_path uses rewrite; string/mixed have no valid shape


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
        entry = {("pointer_glob" if "*" in glob else "pointer"): glob}
        shape = _shape_for(leaf)
        if shape:
            entry["shape"] = shape
        if leaf["shape"] == "abs_path":
            entry["rewrite"] = "strip_root_prefix"
        entry["observed_units"] = leaf["unit_count"]
        entry["observed_deltas"] = leaf["delta_count"]
        inside = glob.startswith(_METADATA_ROOTS)
        if not inside:
            entry["review"] = _OUTSIDE_REVIEW
        elif leaf["shape"] == "number" and leaf["unit_count"] == 1:
            entry["review"] = "singleton numeric leaf \u2014 likely a determinism bug, not a volatile leaf"
        elif leaf["shape"] == "number":
            entry["review"] = ("numeric drift across units \u2014 determinism bug or real change; "
                               "never auto-mask")
        elif leaf["shape"] == "uuid" and shape == _UUID_RX:
            entry["review"] = "uuid-shaped leaf \u2014 confirm it is volatile; regex shape emitted"
        elif leaf["shape"] in ("string", "mixed") and not leaf.get("run_id_form"):
            entry["review"] = "non-volatile-looking shape \u2014 confirm before accepting"
        added.append(entry)
    return {"name": f"{policy['name']}-proposed", "added": added,
            "existing": sorted(known), "note": ("review each 'added' entry; never auto-accept. Before pasting into a policy, "
                     "strip the keys observed_units, observed_deltas and review: load_policy rejects them")}


_RUN_DIR = re.compile(r"^(\d{8}T\d{6}Z-[0-9a-f]{6}|\d{4}-\d{2}-\d{2}_\d{4}(-\d+)?)$")


def snapify(src_root: Path, dst_root: Path) -> int:
    """Lay out every analyzer envelope under a pytest basetemp tree as a snap tree.

    ``<src>/<rel>.json`` with a top-level ``analyzer_type`` becomes
    ``<dst>/<analyzer_type>/<rel>/snap.json``. Run-dir segments (timestamp names) are
    renamed ``RUN-<n>`` by sorted order under their parent. Returns the unit count."""
    src_root, dst_root = Path(src_root), Path(dst_root)
    envs = []
    for p in sorted(src_root.rglob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and isinstance(data.get("analyzer_type"), str) and data["analyzer_type"]:
            envs.append((p.relative_to(src_root).with_suffix("").parts, data["analyzer_type"], p))
    run_dirs: dict[tuple, set] = defaultdict(set)
    for parts, _, _ in envs:
        for i, seg in enumerate(parts[:-1]):
            if _RUN_DIR.match(seg):
                run_dirs[parts[:i]].add(seg)
    rename = {(parent, seg): f"RUN-{n}" for parent, segs in run_dirs.items()
              for n, seg in enumerate(sorted(segs))}
    for parts, atype, p in envs:
        norm = [rename.get((parts[:i], seg), seg) if i < len(parts) - 1 else seg
                for i, seg in enumerate(parts)]
        out = dst_root.joinpath(atype, *norm, "snap.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, out)
    return len(envs)


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
    ap.add_argument("--product", help="product worktree (same SHA used for both slots)")
    ap.add_argument("--gate-dir", required=True)
    ap.add_argument("--profile", default="standard")
    ap.add_argument("--jobs", type=int, default=32)
    sel = ap.add_mutually_exclusive_group()
    sel.add_argument("--repo")
    sel.add_argument("--cross-section")
    sel.add_argument("--repo-list")
    ap.add_argument("--propose-policy", action="store_true")
    ap.add_argument("--skip-run", action="store_true", help="only summarize an existing field_report.json")
    ap.add_argument("--fixture-trees", nargs=2, metavar=("A_BASETEMP", "B_BASETEMP"),
                    help="snapify two pytest --basetemp trees into <gate-dir> and strict-compare them")
    args = ap.parse_args(argv)

    gate_dir = Path(args.gate_dir).resolve()
    if args.fixture_trees:
        if args.product or args.repo or args.cross_section or args.repo_list or args.skip_run:
            ap.error("--fixture-trees takes no --product, selection or --skip-run")
        return _fixture_aa(args, gate_dir)
    if not args.product or not (args.repo or args.cross_section or args.repo_list):
        ap.error("--product and one of --repo/--cross-section/--repo-list are required")
    selection = (["--repo", args.repo] if args.repo else
                 ["--cross-section", args.cross_section] if args.cross_section else
                 ["--repo-list", args.repo_list])
    gate_cmd, cmp_cmd = build_commands(product_dir=Path(args.product).resolve(), gate_dir=gate_dir,
                                       selection=selection, jobs=args.jobs, profile=args.profile)
    strict = gate_dir / "field_report_strict.json"
    if not args.skip_run:
        gate_dir.mkdir(parents=True, exist_ok=True)
        started = time.time()
        r = subprocess.run(gate_cmd)
        if r.returncode not in (0, 1):
            print(f"gate failed with exit code {r.returncode}", file=sys.stderr)
            return 2
        fresh = strict.exists() and strict.stat().st_mtime >= started
        if fresh:
            shutil.copyfile(strict, gate_dir / "field_report.json")
        else:
            rep = gate_dir / "field_report.json"
            rep.unlink(missing_ok=True)  # a leftover report must never be summarized as this run's
            r = subprocess.run(cmp_cmd)
            if r.returncode == 2 and not rep.exists():
                print("compare error", file=sys.stderr)
                return 2
    elif strict.exists():
        shutil.copyfile(strict, gate_dir / "field_report.json")
    elif not (gate_dir / "field_report.json").exists():
        print(f"--skip-run: no field_report.json or field_report_strict.json in {gate_dir}",
              file=sys.stderr)
        return 2
    return _summarize(gate_dir, args.propose_policy)


def _summarize(gate_dir: Path, propose: bool) -> int:
    report = json.loads((gate_dir / "field_report.json").read_text(encoding="utf-8"))
    aa = summarize_strict_report(report)
    (gate_dir / "aa_report.json").write_text(json.dumps(aa, indent=2) + "\n", encoding="utf-8")
    if aa["error"]:
        print(f"A/A ERROR: verdict {aa['verdict']}, compared {aa['units_compared']} "
              f"missing {aa['missing']} parse_errors {aa['parse_errors']} "
              f"policy_violations {len(aa['policy_violations'])} -> {gate_dir / 'aa_report.json'}")
    else:
        print(f"A/A {'CLEAN' if aa['clean'] else 'DELTAS'}: {aa['units_compared']} units, "
              f"{len(aa['leaves'])} differing leaf paths -> {gate_dir / 'aa_report.json'}")
    for leaf in aa["leaves"]:
        print(f"  {leaf['pointer_glob']:50s} units={leaf['unit_count']:6d} shape={leaf['shape']}")
    if propose:
        policy = json.loads((POLICY_DIR / "volatile-leaves-v1.json").read_text(encoding="utf-8"))
        prop = propose_policy(aa, policy)
        out = gate_dir / "volatile-leaves-v1-proposed.json"
        out.write_text(json.dumps(prop, indent=2) + "\n", encoding="utf-8")
        print(f"proposed additions ({len(prop['added'])}) -> {out}  [human review required]")
    if aa["error"]:
        return 2
    return 0 if aa["clean"] else 1


def _fixture_aa(args, gate_dir: Path) -> int:
    srcs = [Path(t).resolve() for t in args.fixture_trees]
    for t in srcs:
        if not t.is_dir():
            print(f"--fixture-trees: not a directory: {t}", file=sys.stderr)
            return 2
    sides = [gate_dir / "baseline", gate_dir / "candidate"]
    for d in sides:
        if d.exists() and any(d.iterdir()):
            print(f"--fixture-trees: {d} already holds a snap tree; use a fresh --gate-dir",
                  file=sys.stderr)
            return 2
    for src, dst in zip(srcs, sides):
        dst.mkdir(parents=True, exist_ok=True)
        print(f"snapified {snapify(src, dst)} analyzer envelopes: {src} -> {dst}")
    _, cmp_cmd = build_commands(product_dir=gate_dir, gate_dir=gate_dir, selection=[], jobs=1,
                                profile="standard")
    rep = gate_dir / "field_report.json"
    rep.unlink(missing_ok=True)
    r = subprocess.run(cmp_cmd)
    if not rep.exists():
        print(f"compare error (exit {r.returncode}, no report)", file=sys.stderr)
        return 2
    return _summarize(gate_dir, args.propose_policy)


if __name__ == "__main__":
    sys.exit(main())
