#!/usr/bin/env python3
"""v1.4 hierarchy regression gate — curated sub-sheets, fresh paired runs.

Audit LOG 9 / regression-testing-audit F9 (2026-05-15): the existing
``run_v14_gate.py`` intentionally passes ``--no-hierarchy`` to both v1.3.1 and
v1.4 sides so the comparison stays apples-to-apples. That leaves a coverage
hole: a v1.5 change that accidentally turns hierarchy auto-discovery into a
no-op (or fans hierarchy expansion out per-component) would NOT be caught by
the default gate. This driver runs a curated set of hierarchical sub-sheets
in BOTH modes (default = auto-discover parent; ``--no-hierarchy`` = treat as
standalone) and validates three contracts on the differential.

Why sub-sheets specifically: on top-level project files, ``--no-hierarchy`` is
effectively a no-op — both modes walk the full project tree. The flag's
behavior only meaningfully differs when the input file is a SUB-SHEET that
needs to auto-discover its parent project. The curated set is hand-picked for
this reason (the cross-section generator's ``hierarchical`` bucket reads 0 —
filed separately as a TH-* follow-up).

Contracts per board:

  1. **hierarchy_expansion_evident** — default mode must report at LEAST as
     many components/findings/subcircuits as ``--no-hierarchy`` mode AND must
     NOT have a ``hierarchy_warning`` populated. ``--no-hierarchy`` mode must
     populate ``hierarchy_warning`` with the "appears to be a sub-sheet" text
     (proving the analyzer DID try to discover the parent and was overridden).
     Locks "the ``--no-hierarchy`` flag is wired up AND default mode does
     auto-discover parents".

  2. **finding_set_superset** — default-mode finding count >= no-hier finding
     count, AND any ``rule_id`` no-hier emitted MUST also appear in default
     mode UNLESS it's listed in the board's ``known_suppressions`` allowlist.
     Hierarchy reveals sub-sheet detail; it should NEVER silently hide a
     finding the standalone-mode analyzer produced. Known exception:
     hierarchy auto-discovery of a parent project legitimately resolves
     context-bound findings like SS-002 ("BOM has 1/2 MPNs") when the parent
     BOM completes the picture. These cases are declared per-board so any
     NEW suppression beyond the allowlist trips the gate.

  3. **hierarchy_determinism** — with hierarchy enabled and
     ``PYTHONHASHSEED=0``, two consecutive runs MUST produce byte-equal
     envelopes modulo volatile fields (``timestamp``, ``run_id``,
     ``capability_mode_ref``). Distinct from the LOG 7 contract
     (``test_only_deterministic_hash_seed``): that one is RED-xfail and
     tests cross-seed invariance (a v1.5 product fix); this one tests
     intra-seed reproducibility and should be GREEN today.

Curated set (3 sub-sheets with confirmed differentials, 2026-05-16):

  * ``chof747/kicad-building-blocks/mcu_3v3_pwr_regulation.kicad_sch``
    — small (12 findings hier / 9 no-hier)
  * ``daykin/levelshift-pcb/12_to_3v3.kicad_sch``
    — medium (36 / 6)
  * ``PySpice-org/kicad-rw/.../Analog_inputs.kicad_sch``
    — large (434 / 48)

If a board's underlying sub-sheet stops producing a meaningful differential
(e.g., the parent .kicad_pro is renamed), the gate flips to FAIL on
hierarchy_expansion_evident for that board, surfacing the corpus drift.

Usage:

    python3 regression/run_hierarchy_regression_gate.py
    python3 regression/run_hierarchy_regression_gate.py --board chof747-mcu-3v3
    python3 regression/run_hierarchy_regression_gate.py --skip-determinism

Rollup: ``results/v14_hierarchy_gate/rollup.json`` (gitignored).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from utils import DEFAULT_JOBS  # noqa: E402

OUT_DIR = HARNESS_DIR / "results" / "v14_hierarchy_gate"
REPOS_DIR = HARNESS_DIR / "repos"
ANALYZER_SCRIPT_REL = "skills/kicad/scripts/analyze_schematic.py"

SUBPROC_TIMEOUT_S = 240

CURATED_SET = [
    {
        "name": "chof747-mcu-3v3",
        "sch_path_rel": "chof747/kicad-building-blocks/mcu_3v3_pwr_regulation.kicad_sch",
        # SS-002 fires in --no-hierarchy because the sub-sheet's standalone
        # BOM has 1/2 MPNs (50%); auto-hierarchy discovers the parent project
        # whose full BOM resolves the gap. Documented, not a bug.
        "known_suppressions": ["SS-002"],
    },
    {
        "name": "daykin-12-to-3v3",
        "sch_path_rel": "daykin/levelshift-pcb/12_to_3v3.kicad_sch",
        "known_suppressions": [],
    },
    {
        "name": "pyspice-analog-inputs",
        "sch_path_rel": (
            "PySpice-org/kicad-rw/kicad-examples/electrolab-cta-control-board/"
            "Analog_inputs.kicad_sch"
        ),
        "known_suppressions": [],
    },
]


# ---------------------------------------------------------------------------
# Volatile-field stripping for determinism comparison
# ---------------------------------------------------------------------------

VOLATILE_TOP_KEYS = ("generated_at", "timestamp", "ran_at", "capability_mode_ref")
VOLATILE_INPUT_KEYS = ("run_id", "timestamp", "ran_at")


def _strip_volatile(envelope):
    """Drop fields that legitimately vary between runs. Hash-seed determinism
    is about finding/list ORDER + value stability, not about provenance
    fields that change every invocation."""
    blob = json.loads(json.dumps(envelope))
    for k in VOLATILE_TOP_KEYS:
        blob.pop(k, None)
    inputs = blob.get("inputs")
    if isinstance(inputs, dict):
        for k in VOLATILE_INPUT_KEYS:
            inputs.pop(k, None)
        blob["inputs"] = inputs
    return blob


def _envelope_hash(envelope):
    """Stable hash for byte-equality comparison after volatile-field strip."""
    return hashlib.sha256(
        json.dumps(envelope, sort_keys=True, default=str).encode()
    ).hexdigest()


# ---------------------------------------------------------------------------
# Contract checks — each returns (verdict, detail) where verdict ∈
# {"PASS", "FAIL", "SKIP"}. Pure functions, unit-tested via synthetic
# envelopes in tests/test_v14_hierarchy_gate.py.
# ---------------------------------------------------------------------------

def _check_hierarchy_expansion(hier_env, nohier_env):
    """Contract 1: ``--no-hierarchy`` mode must populate ``hierarchy_warning``
    (proving the analyzer DID try to discover the parent and was overridden),
    AND default mode must report >= as many components as ``--no-hierarchy``
    (proving auto-discovery actually expanded the analysis)."""
    h_warn_hier = hier_env.get("hierarchy_warning")
    h_warn_no = nohier_env.get("hierarchy_warning")

    if not h_warn_no:
        return "FAIL", (
            f"--no-hierarchy mode did NOT populate hierarchy_warning — "
            f"either input isn't a sub-sheet or --no-hierarchy flag is "
            f"unwired (got {h_warn_no!r})"
        )
    if h_warn_hier:
        return "FAIL", (
            f"default-hierarchy mode populated hierarchy_warning "
            f"({h_warn_hier!r:.80}) — auto-discovery failed to find parent"
        )

    h_components = len(hier_env.get("components") or [])
    n_components = len(nohier_env.get("components") or [])
    if h_components < n_components:
        return "FAIL", (
            f"default-hierarchy components={h_components} < "
            f"--no-hierarchy components={n_components}; hierarchy must "
            f"expand, never shrink"
        )

    h_subcircuits = len(hier_env.get("subcircuits") or [])
    n_subcircuits = len(nohier_env.get("subcircuits") or [])
    if h_subcircuits < n_subcircuits:
        return "FAIL", (
            f"default-hierarchy subcircuits={h_subcircuits} < "
            f"--no-hierarchy subcircuits={n_subcircuits}; hierarchy must "
            f"expand, never shrink"
        )

    return "PASS", (
        f"hierarchy expands: components {n_components}→{h_components}, "
        f"subcircuits {n_subcircuits}→{h_subcircuits}"
    )


def _check_finding_superset(hier_env, nohier_env, known_suppressions=()):
    """Contract 2: default-mode rule_id set ⊇ ``--no-hierarchy`` rule_id set
    (excluding any rule_id declared in ``known_suppressions``), AND
    default-mode finding count >= (no-hier count - len(declared suppressed)).
    Hierarchy reveals sub-sheet detail — any UNDECLARED suppression trips
    the gate."""
    hier_findings = hier_env.get("findings") or []
    nohier_findings = nohier_env.get("findings") or []
    declared = set(known_suppressions or ())

    hier_rule_ids = {f.get("rule_id") for f in hier_findings if f.get("rule_id")}
    nohier_rule_ids = {f.get("rule_id") for f in nohier_findings if f.get("rule_id")}

    suppressed = nohier_rule_ids - hier_rule_ids
    undeclared = suppressed - declared
    if undeclared:
        return "FAIL", (
            f"--no-hierarchy emitted rule_id(s) {sorted(undeclared)} that "
            f"default-hierarchy mode dropped without being in "
            f"known_suppressions={sorted(declared)}"
        )

    nohier_suppressed_count = sum(
        1 for f in nohier_findings
        if f.get("rule_id") in (suppressed & declared)
    )
    expected_min_hier = len(nohier_findings) - nohier_suppressed_count
    if len(hier_findings) < expected_min_hier:
        return "FAIL", (
            f"default-hierarchy findings={len(hier_findings)} < expected "
            f"minimum {expected_min_hier} (no-hier {len(nohier_findings)} "
            f"minus {nohier_suppressed_count} declared-suppressed)"
        )

    detail = (
        f"superset OK: {len(nohier_findings)} no-hier findings ⊆ "
        f"{len(hier_findings)} hier findings"
    )
    if suppressed:
        detail += f" (declared suppressions used: {sorted(suppressed)})"
    return "PASS", detail


def _check_determinism(env_a, env_b):
    """Contract 3: two consecutive default-mode runs (PYTHONHASHSEED=0) MUST
    produce byte-equal envelopes after stripping volatile fields. Distinct
    from LOG 7 (cross-seed invariance, RED-xfail) — this is intra-seed
    reproducibility, GREEN today."""
    stripped_a = _strip_volatile(env_a)
    stripped_b = _strip_volatile(env_b)
    h_a = _envelope_hash(stripped_a)
    h_b = _envelope_hash(stripped_b)
    if h_a != h_b:
        return "FAIL", (
            f"two consecutive runs produced different envelopes "
            f"(sha256 {h_a[:12]} vs {h_b[:12]}) — likely a missing sort "
            f"on a collection iterated during emit"
        )
    return "PASS", f"two runs byte-equal post-strip ({h_a[:12]})"


# ---------------------------------------------------------------------------
# Analyzer runner
# ---------------------------------------------------------------------------

def _run_schematic(sch_path, kh_dir, tmp_dir, *, hierarchy, label):
    """Invoke analyze_schematic.py once and return the parsed envelope.
    PYTHONHASHSEED=0 is pinned across all invocations (the gate's
    determinism contract needs intra-seed reproducibility)."""
    analyzer = kh_dir / ANALYZER_SCRIPT_REL
    out_path = Path(tmp_dir) / f"{label}.json"
    cmd = [sys.executable, str(analyzer), str(sch_path), "--output", str(out_path)]
    if not hierarchy:
        cmd.append("--no-hierarchy")
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S, env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"analyze_schematic rc={proc.returncode} on {sch_path} "
            f"(hier={hierarchy}); stderr tail: {proc.stderr[-300:]}"
        )
    if not out_path.is_file():
        raise RuntimeError(
            f"analyze_schematic claimed success but did not write {out_path}"
        )
    return json.loads(out_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Per-board worker
# ---------------------------------------------------------------------------

def _process_board(args):
    spec, kh_dir, skip_determinism = args
    name = spec["name"]
    sch_path = REPOS_DIR / spec["sch_path_rel"]

    if not sch_path.is_file():
        return {
            "board": name,
            "verdict": "SKIP",
            "contracts": {
                "setup": ("SKIP", f"missing sub-sheet {sch_path}")
            },
        }

    contracts = {}
    try:
        with tempfile.TemporaryDirectory(prefix=f"hier-gate-{name}-") as td:
            hier_env = _run_schematic(
                sch_path, kh_dir, td, hierarchy=True, label="hier_a"
            )
            nohier_env = _run_schematic(
                sch_path, kh_dir, td, hierarchy=False, label="nohier"
            )

            contracts["hierarchy_expansion_evident"] = (
                _check_hierarchy_expansion(hier_env, nohier_env)
            )
            contracts["finding_set_superset"] = (
                _check_finding_superset(
                    hier_env, nohier_env,
                    known_suppressions=spec.get("known_suppressions") or (),
                )
            )

            if skip_determinism:
                contracts["hierarchy_determinism"] = (
                    "SKIP", "--skip-determinism in effect"
                )
            else:
                hier_env_b = _run_schematic(
                    sch_path, kh_dir, td, hierarchy=True, label="hier_b"
                )
                contracts["hierarchy_determinism"] = (
                    _check_determinism(hier_env, hier_env_b)
                )
    except (RuntimeError, subprocess.TimeoutExpired) as e:
        return {
            "board": name,
            "verdict": "FAIL",
            "contracts": {
                **contracts,
                "run": ("FAIL", str(e)[:300]),
            },
        }

    overall = "PASS"
    for verdict, _ in contracts.values():
        if verdict == "FAIL":
            overall = "FAIL"
            break

    return {"board": name, "verdict": overall, "contracts": contracts}


# ---------------------------------------------------------------------------
# Rollup
# ---------------------------------------------------------------------------

def _aggregate(records):
    """Bucket records into a rollup. Per-board verdicts + contract-level
    pass/skip/fail tallies."""
    summary = {"PASS": 0, "FAIL": 0, "SKIP": 0, "contract_fails": Counter()}
    boards = {}
    for rec in records:
        v = rec["verdict"]
        summary[v] += 1
        boards[rec["board"]] = {
            "verdict": v,
            "contracts": {
                cn: {"verdict": cv, "detail": cd}
                for cn, (cv, cd) in rec["contracts"].items()
            },
        }
        if v == "FAIL":
            for cn, (cv, _) in rec["contracts"].items():
                if cv == "FAIL":
                    summary["contract_fails"][cn] += 1
    return {
        "summary": {**summary, "contract_fails": dict(summary["contract_fails"])},
        "boards": boards,
    }


def _print_summary(rollup):
    """One-line-per-board summary suitable for release-ops eyeballing."""
    s = rollup["summary"]
    total = s["PASS"] + s["FAIL"] + s["SKIP"]
    print(f"\n=== v1.4 hierarchy regression gate ===")
    print(f"Total boards: {total}  "
          f"PASS={s['PASS']}  FAIL={s['FAIL']}  SKIP={s['SKIP']}")
    for name, b in sorted(rollup["boards"].items()):
        cf = [
            f"{cn}={c['verdict']}"
            for cn, c in b["contracts"].items()
            if c["verdict"] != "PASS"
        ]
        cf_str = ", ".join(cf) if cf else "all PASS"
        print(f"  {name:<28}  {b['verdict']:<4}  {cf_str}")
    if s["FAIL"] == 0:
        print("\nCLEAN — hierarchy contracts hold corpus-wide")
    else:
        print(f"\nNOT CLEAN — {s['FAIL']} board(s) failed. "
              f"See rollup for per-contract details.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--board", help="filter to a single curated board name")
    ap.add_argument(
        "--jobs",
        type=int,
        default=min(DEFAULT_JOBS, len(CURATED_SET)),
        help=f"parallel boards (default min({DEFAULT_JOBS}, {len(CURATED_SET)}))",
    )
    ap.add_argument(
        "--kicad-happy-dir",
        default=os.environ.get(
            "KICAD_HAPPY_DIR",
            str(HARNESS_DIR.parent / "kicad-happy"),
        ),
        help="kicad-happy source dir",
    )
    ap.add_argument(
        "--skip-determinism",
        action="store_true",
        help="skip the intra-seed reproducibility contract (one less run per board)",
    )
    args = ap.parse_args(argv)

    kh_dir = Path(args.kicad_happy_dir)
    analyzer = kh_dir / ANALYZER_SCRIPT_REL
    if not analyzer.is_file():
        print(f"ERROR: analyzer not found at {analyzer}. "
              "Set KICAD_HAPPY_DIR or --kicad-happy-dir.", file=sys.stderr)
        return 2

    boards = [b for b in CURATED_SET if not args.board or b["name"] == args.board]
    if not boards:
        print(f"No boards matched --board={args.board!r}", file=sys.stderr)
        return 1

    print(f"Running hierarchy gate on {len(boards)} board(s) "
          f"with {args.jobs} worker(s)...")

    work = [(b, kh_dir, args.skip_determinism) for b in boards]
    records = []
    if args.jobs <= 1 or len(work) == 1:
        records = [_process_board(w) for w in work]
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            futures = [ex.submit(_process_board, w) for w in work]
            for fut in as_completed(futures):
                records.append(fut.result())

    rollup = _aggregate(records)
    rollup["board_filter"] = args.board
    rollup["skip_determinism"] = args.skip_determinism

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rollup_path = OUT_DIR / "rollup.json"
    rollup_path.write_text(json.dumps(rollup, indent=2, sort_keys=True))
    print(f"\nRollup written to {rollup_path}")

    _print_summary(rollup)
    return 0 if rollup["summary"]["FAIL"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
