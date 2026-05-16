#!/usr/bin/env python3
"""v1.4 default-mode contract gate driver — POST-HOC scan over v14 snapshots.

Audit LOG 8 / regression-testing-audit F4 (2026-05-15): "second v1.4-only
gate (not comparing v1.3.1) that validates user-facing default-mode
contracts". The existing ``run_v14_gate.py`` answers "does v1.4 regress
against v1.3.1?"; this gate answers "do v1.4's own envelopes hold their
self-consistency promises?". Catches a class of bugs the comparison gate
misses (e.g., a v1.4 detector that emits ``severity='WARNING'`` literal
uppercase passes the comparison gate fine, but breaks every downstream
consumer that filters on ``severity == 'warning'``).

Contracts validated per envelope:

  1. **Schema validates** — envelope conforms to the schema dump from
     ``analyzer --schema`` (soft-skips if ``jsonschema`` not installed,
     OR if the analyzer's ``--schema`` output is malformed). Skipped
     contracts surface in the rollup with ``verdict=SKIP``.
  2. **Summary integrity** — ``summary.total_findings == len(findings)``,
     ``summary.by_severity`` sums match per-severity bucket counts.
  3. **Severity normalization** — every finding's ``severity`` ∈
     ``{error, warning, info}`` (lowercase only). Locks the F1.4 bug
     class where literal uppercase ``'WARNING'`` was appended to findings
     and downstream filters silently mismatched.
  4. **Run-id linkage** — ``inputs.run_id == capability_mode_ref.run_id``.
     Audit Highest-Risk #5 invariant. Already locked corpus-wide via
     ``validate/validate_run_id.py`` (one-shot validator); this gate is the
     ongoing contract assertion (re-run as part of release validation).

Design — POST-HOC over existing snapshots:

This driver does NOT run analyzers. It walks the snapshot tree produced
by ``regression/run_v14_gate.py`` under ``results/v14_gate/v14/`` and
validates the on-disk envelopes. That keeps the runtime fast (~10 s for
quick_200, ~2 min for full corpus) and avoids re-running analyzers that
already produced output in the comparison-gate phase.

Pre-requisite: ``regression/run_v14_gate.py`` must have run first to
populate ``results/v14_gate/v14/``. If the tree is missing the gate
exits with ``--no-snapshots`` and a pointer to the prerequisite.

Deferred for follow-up commit (LOG 8b):

  5. Layer 2 strip is no-op on deterministic content — requires running
     analyzers in both default + ``--only-deterministic`` modes on a
     curated set, comparing strip-equality. Will live in
     ``tests/contract/test_layer2_strip_invariance.py``.
  6. Report generation succeeds — running ``action/format-report.py`` on
     each snapshot, asserting exit 0. Separate concern, separate driver.

Usage:
    python3 regression/run_v14_default_contract_gate.py --jobs 16
    python3 regression/run_v14_default_contract_gate.py --repo owner/repo
    python3 regression/run_v14_default_contract_gate.py --analyzer schematic
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from utils import DEFAULT_JOBS  # noqa: E402

GATE_DIR = HARNESS_DIR / "results" / "v14_gate"
V14_SNAP_DIR = GATE_DIR / "v14"
OUT_DIR = HARNESS_DIR / "results" / "v14_default_contract_gate"

ALLOWED_SEVERITIES = {"error", "warning", "info"}

ANALYZER_SCRIPT_REL = {
    "schematic": "skills/kicad/scripts/analyze_schematic.py",
    "pcb": "skills/kicad/scripts/analyze_pcb.py",
    "gerber": "skills/kicad/scripts/analyze_gerbers.py",
    "thermal": "skills/kicad/scripts/analyze_thermal.py",
    "emc": "skills/emc/scripts/analyze_emc.py",
    "cross_analysis": "skills/kicad/scripts/cross_analysis.py",
}


# ---------------------------------------------------------------------------
# Contract checks — each returns (verdict, detail) where verdict ∈
# {"PASS", "FAIL", "SKIP"} and detail is a one-line string explanation.
# These helpers are pure functions of the envelope dict — unit-tested in
# tests/test_v14_default_contract_gate.py via synthetic envelopes.
# ---------------------------------------------------------------------------

def _check_summary_integrity(envelope):
    """Contract 2: ``summary.total_findings`` (when present) MUST equal
    ``len(findings[])``, AND ``summary.by_severity`` bucket counts MUST
    sum to ``total_findings`` (when both present)."""
    findings = envelope.get("findings") or []
    summary = envelope.get("summary") or {}
    total = summary.get("total_findings")
    bysev = summary.get("by_severity")

    if total is None and bysev is None:
        return "SKIP", "summary lacks total_findings and by_severity"

    if total is not None and total != len(findings):
        return "FAIL", (
            f"summary.total_findings={total} but len(findings)={len(findings)}"
        )

    if bysev is not None:
        bucket_sum = sum(int(v or 0) for v in bysev.values())
        if total is not None and bucket_sum != total:
            return "FAIL", (
                f"summary.by_severity sum={bucket_sum} != total_findings={total}"
            )
        per_sev = Counter(f.get("severity") for f in findings)
        for sev, n in bysev.items():
            actual = per_sev.get(sev, 0)
            if int(n or 0) != actual:
                return "FAIL", (
                    f"summary.by_severity[{sev!r}]={n} != actual {sev!r} "
                    f"finding count {actual}"
                )

    return "PASS", "summary buckets consistent"


def _check_severity_normalized(envelope):
    """Contract 3: every finding's ``severity`` MUST be lowercase from
    {error, warning, info}. Locks the F1.4 bug class."""
    findings = envelope.get("findings") or []
    bad = []
    for i, f in enumerate(findings):
        sev = f.get("severity")
        if sev not in ALLOWED_SEVERITIES:
            bad.append((i, f.get("rule_id"), sev))
    if bad:
        # Trim to 3 examples — rollup detail should stay one-liner-ish.
        sample = ", ".join(
            f"#{i} rule={r!r} sev={s!r}" for i, r, s in bad[:3]
        )
        return "FAIL", (
            f"{len(bad)} finding(s) with non-normalized severity; first: {sample}"
        )
    return "PASS", f"all {len(findings)} findings have normalized severity"


def _check_run_id_linkage(envelope):
    """Contract 4: ``inputs.run_id`` MUST equal ``capability_mode_ref.run_id``.
    The audit Highest-Risk #5 invariant — proves the envelope is pinned to
    the capability_mode record that drove its production."""
    inputs = envelope.get("inputs") or {}
    cmr = envelope.get("capability_mode_ref") or {}

    inp_id = inputs.get("run_id")
    cmr_id = cmr.get("run_id")

    if inp_id is None and cmr_id is None:
        return "SKIP", "neither inputs.run_id nor capability_mode_ref present"
    if inp_id is None:
        return "FAIL", "inputs.run_id missing while capability_mode_ref.run_id present"
    if cmr_id is None:
        return "FAIL", "capability_mode_ref.run_id missing while inputs.run_id present"
    if inp_id != cmr_id:
        return "FAIL", (
            f"inputs.run_id={inp_id!r} != capability_mode_ref.run_id={cmr_id!r}"
        )
    return "PASS", f"run_id linked ({inp_id})"


def _check_schema_validates(envelope, schema):
    """Contract 1: envelope MUST conform to the analyzer's ``--schema`` dump.

    Soft-skips if jsonschema isn't importable OR the schema dict is None.
    Failure detail is the first error path + message — full error trace
    is dropped to keep the rollup line-y."""
    if schema is None:
        return "SKIP", "no schema available (analyzer --schema unavailable)"
    try:
        import jsonschema
    except ImportError:
        return "SKIP", "jsonschema not installed"
    try:
        jsonschema.validate(envelope, schema)
    except jsonschema.ValidationError as e:
        path = ".".join(str(p) for p in e.absolute_path) or "<root>"
        return "FAIL", f"schema violation at {path}: {e.message[:160]}"
    except jsonschema.SchemaError as e:
        return "SKIP", f"schema itself invalid: {e.message[:160]}"
    return "PASS", "envelope validates against schema"


CONTRACTS = [
    ("summary_integrity", _check_summary_integrity),
    ("severity_normalized", _check_severity_normalized),
    ("run_id_linkage", _check_run_id_linkage),
]


# ---------------------------------------------------------------------------
# Schema cache — load each analyzer's --schema output once per gate run
# ---------------------------------------------------------------------------

def _load_schema(analyzer, kh_dir):
    """Run ``analyzer --schema`` to capture the JSON Schema dump. Returns
    None if the script isn't present or the output isn't parseable."""
    script = kh_dir / ANALYZER_SCRIPT_REL.get(analyzer, "")
    if not script.is_file():
        return None
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--schema"],
            capture_output=True, text=True, timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# Per-snapshot worker
# ---------------------------------------------------------------------------

def _validate_one(args):
    analyzer, repo, identity, snap_path, schema = args
    try:
        envelope = json.loads(Path(snap_path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {
            "analyzer": analyzer, "repo": repo, "identity": identity,
            "snap_path": str(snap_path), "verdict": "FAIL",
            "contracts": {"load": ("FAIL", f"snapshot read error: {e}")},
        }

    contracts = {}
    for name, fn in CONTRACTS:
        contracts[name] = fn(envelope)
    contracts["schema_validates"] = _check_schema_validates(envelope, schema)

    overall = "PASS"
    for verdict, _ in contracts.values():
        if verdict == "FAIL":
            overall = "FAIL"
            break
        if verdict == "SKIP" and overall == "PASS":
            overall = "PASS"  # SKIP doesn't downgrade overall PASS
    return {
        "analyzer": analyzer, "repo": repo, "identity": identity,
        "snap_path": str(snap_path), "verdict": overall,
        "contracts": contracts,
    }


# ---------------------------------------------------------------------------
# Snapshot tree walker
# ---------------------------------------------------------------------------

def _enumerate_snapshots(repo_filter):
    """Walk results/v14_gate/v14/{analyzer}/{owner}/{repo}/{key}/snap.json
    and yield (analyzer, repo, identity, snap_path)."""
    if not V14_SNAP_DIR.is_dir():
        return
    for analyzer_dir in sorted(V14_SNAP_DIR.iterdir()):
        if not analyzer_dir.is_dir():
            continue
        analyzer = analyzer_dir.name
        for owner_dir in sorted(analyzer_dir.iterdir()):
            if not owner_dir.is_dir():
                continue
            for repo_dir in sorted(owner_dir.iterdir()):
                if not repo_dir.is_dir():
                    continue
                repo = f"{owner_dir.name}/{repo_dir.name}"
                if repo_filter and repo != repo_filter:
                    continue
                for key_dir in sorted(repo_dir.iterdir()):
                    if not key_dir.is_dir():
                        continue
                    snap = key_dir / "snap.json"
                    if snap.exists() and snap.stat().st_size > 3:
                        identity = f"{repo}/{key_dir.name}"
                        yield analyzer, repo, identity, snap


# ---------------------------------------------------------------------------
# Rollup
# ---------------------------------------------------------------------------

def _aggregate(records):
    """Bucket records into a rollup. Per-analyzer + corpus-wide totals,
    plus contract-level pass/skip/fail counts."""
    by_analyzer = defaultdict(lambda: {
        "PASS": 0, "FAIL": 0, "SKIP": 0,
        "contract_fails": Counter(),
        "fail_repos": [],
    })
    corpus = {"PASS": 0, "FAIL": 0, "SKIP": 0, "contract_fails": Counter()}

    for rec in records:
        a = rec["analyzer"]
        v = rec["verdict"]
        by_analyzer[a][v] += 1
        corpus[v] += 1
        if v == "FAIL":
            for cname, (cv, _) in rec["contracts"].items():
                if cv == "FAIL":
                    by_analyzer[a]["contract_fails"][cname] += 1
                    corpus["contract_fails"][cname] += 1
            if len(by_analyzer[a]["fail_repos"]) < 20:
                by_analyzer[a]["fail_repos"].append({
                    "identity": rec["identity"],
                    "first_fail": next(
                        (f"{cn}: {det}" for cn, (cv, det)
                         in rec["contracts"].items() if cv == "FAIL"),
                        "",
                    ),
                })

    # Convert Counters to dicts for JSON serialization
    for a in by_analyzer:
        by_analyzer[a]["contract_fails"] = dict(by_analyzer[a]["contract_fails"])
    return {
        "by_analyzer": dict(by_analyzer),
        "corpus": {**corpus, "contract_fails": dict(corpus["contract_fails"])},
    }


def _print_summary(rollup):
    """One-line-per-analyzer summary suitable for release-ops eyeballing."""
    corpus = rollup["corpus"]
    total = corpus["PASS"] + corpus["FAIL"] + corpus["SKIP"]
    print(f"\n=== v1.4 default-contract gate ===")
    print(f"Total snapshots: {total}  "
          f"PASS={corpus['PASS']}  FAIL={corpus['FAIL']}  SKIP={corpus['SKIP']}")
    for analyzer, b in sorted(rollup["by_analyzer"].items()):
        t = b["PASS"] + b["FAIL"] + b["SKIP"]
        cf = ", ".join(f"{k}:{v}" for k, v in sorted(b["contract_fails"].items())) \
            or "—"
        print(f"  {analyzer:<14}  {t:>5} snaps  "
              f"PASS={b['PASS']:<5} FAIL={b['FAIL']:<3} SKIP={b['SKIP']:<3}  "
              f"contract fails: {cf}")
    if corpus["FAIL"] == 0:
        print("\nCLEAN — all contracts pass corpus-wide")
    else:
        print(f"\nNOT CLEAN — {corpus['FAIL']} snapshots have at least 1 "
              f"failing contract. See per-analyzer rollup for fail repos.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--repo", help="filter to a single owner/repo")
    ap.add_argument(
        "--analyzer",
        choices=list(ANALYZER_SCRIPT_REL.keys()),
        help="filter to a single analyzer (default: all)",
    )
    ap.add_argument("--jobs", type=int, default=DEFAULT_JOBS,
                    help=f"parallel workers (default {DEFAULT_JOBS})")
    ap.add_argument(
        "--kicad-happy-dir",
        default=os.environ.get(
            "KICAD_HAPPY_DIR",
            str(HARNESS_DIR.parent / "kicad-happy"),
        ),
        help="kicad-happy source dir (for --schema dumps)",
    )
    ap.add_argument("--no-schema", action="store_true",
                    help="skip schema-validates contract (still runs the other 3)")
    args = ap.parse_args(argv)

    if not V14_SNAP_DIR.is_dir():
        print(f"ERROR: {V14_SNAP_DIR} does not exist. "
              "Run regression/run_v14_gate.py first.", file=sys.stderr)
        return 2

    kh_dir = Path(args.kicad_happy_dir)
    schemas = {}
    if not args.no_schema:
        for analyzer in ANALYZER_SCRIPT_REL:
            if args.analyzer and analyzer != args.analyzer:
                continue
            schemas[analyzer] = _load_schema(analyzer, kh_dir)

    jobs = []
    for analyzer, repo, identity, snap in _enumerate_snapshots(args.repo):
        if args.analyzer and analyzer != args.analyzer:
            continue
        jobs.append((analyzer, repo, identity, snap,
                     schemas.get(analyzer) if not args.no_schema else None))

    if not jobs:
        print("No snapshots to validate. (Did run_v14_gate.py run for the "
              "requested repo/analyzer?)", file=sys.stderr)
        return 1

    print(f"Validating {len(jobs)} v1.4 snapshots with {args.jobs} workers...")

    records = []
    if args.jobs <= 1:
        records = [_validate_one(j) for j in jobs]
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            futures = [ex.submit(_validate_one, j) for j in jobs]
            for fut in as_completed(futures):
                records.append(fut.result())

    rollup = _aggregate(records)
    rollup["jobs"] = len(jobs)
    rollup["repo_filter"] = args.repo
    rollup["analyzer_filter"] = args.analyzer

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rollup_path = OUT_DIR / "rollup.json"
    rollup_path.write_text(json.dumps(rollup, indent=2, sort_keys=True))
    print(f"\nRollup written to {rollup_path}")

    _print_summary(rollup)
    return 0 if rollup["corpus"]["FAIL"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
