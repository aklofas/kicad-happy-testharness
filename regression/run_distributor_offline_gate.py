#!/usr/bin/env python3
"""distributor-offline profile: the product's offline distributor oracle, run both ways.

The oracle (`tools/distributor_offline.py` + `tools/tests/fixtures/distributor/` in the
product) replays every distributor sync/fetch CLI in process over recorded provider
responses and compares the artefacts byte-for-byte with an expected set frozen at an
earlier product commit. This runner is the harness-side evidence for that profile (declared in
harnesslib.profiles; run_corpus_gate.py refuses it because it runs no corpus analyzer):

  1. candidate direction: `--all --expected <candidate>/tools/tests/fixtures/distributor/expected`
     must exit 0 (`sync-offline: OK (<n> runs)`);
  2. baseline direction: the oracle + fixtures at --runner-rev (the candidate-repo revision
     whose patch targets match the BASELINE layout, e.g. the pre-move runner) are overlaid
     on an export of the baseline tree, `--all --write-expected <gate-dir>/baseline_expected`
     runs there, and the result must be byte-identical to the candidate's frozen set.

Both product trees are exported with `git archive HEAD` into <gate-dir>/{baseline,candidate}_tree,
so the clones are never written to (the corpus gate refuses dirty trees).

Usage:
  python3 regression/run_distributor_offline_gate.py \
      --baseline-dir results/v3_baseline/product_6a91aaa --candidate-dir results/v3_baseline/product_30cbfcb \
      --runner-rev 19327c9 --gate-dir results/<label>_gate_do [--label L] [--fixtures tests/fixtures]

Writes <gate-dir>/distributor_offline.json and <gate-dir>/{candidate,baseline}.{stdout,stderr}.txt.
Exit 0 = gate_pass, 1 = a direction failed or the sets differ, 2 = usage / export error.
"""
from __future__ import annotations

import argparse
import dataclasses
import io
import json
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from harnesslib.identity import git_worktree_ref  # noqa: E402
from harnesslib.profiles import PROFILES  # noqa: E402

PROFILE = PROFILES["distributor-offline"]
ORACLE = "tools/distributor_offline.py"
FIXTURES = "tools/tests/fixtures/distributor"
EXPECTED = FIXTURES + "/expected"
CRITERION = ("candidate --expected exit 0 AND baseline --write-expected exit 0 AND the baseline "
             "set byte-identical to the candidate's frozen expected set")


def git_archive(repo: Path, rev: str, dest: Path, paths: tuple[str, ...] = ()) -> None:
    """Export `rev` of `repo` (only `paths` when given) into `dest`, overlaying what is there."""
    cmd = ["git", "-C", str(repo), "archive", "--format=tar", rev]
    if paths:
        cmd += ["--", *paths]
    out = subprocess.run(cmd, check=True, capture_output=True).stdout
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(out)) as tar:
        tar.extractall(dest, filter="data")


def compare_dirs(expected: Path, actual: Path) -> list[str]:
    """Sorted relative paths that differ: present on one side only, or different bytes."""
    rel_e = {p.relative_to(expected).as_posix() for p in expected.rglob("*") if p.is_file()}
    rel_a = {p.relative_to(actual).as_posix() for p in actual.rglob("*") if p.is_file()} if actual.is_dir() else set()
    diffs = []
    for rel in sorted(rel_e | rel_a):
        if rel not in rel_e or rel not in rel_a or (expected / rel).read_bytes() != (actual / rel).read_bytes():
            diffs.append(rel)
    return diffs


def run_oracle(tree: Path, fixtures: Path, mode_args: list[str]) -> dict:
    cmd = [sys.executable, str(tree / ORACLE), "--product", str(tree), "--all",
           "--fixtures", str(fixtures), *mode_args]
    try:
        r = subprocess.run(cmd, cwd=tree, capture_output=True, text=True, timeout=PROFILE.timeout_s)
        return {"argv": cmd[1:], "exit_code": r.returncode, "timed_out": False,
                "stdout": r.stdout, "stderr": r.stderr}
    except subprocess.TimeoutExpired as e:
        # TimeoutExpired carries bytes even under text=True
        return {"argv": cmd[1:], "exit_code": None, "timed_out": True,
                "stdout": _text(e.stdout), "stderr": _text(e.stderr)}


def _text(b) -> str:
    return b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")


def gate_pass(candidate: dict, baseline: dict, diffs: list[str], expected_artefacts: int) -> bool:
    """Both directions exit 0, no differing artefact, and a non-empty frozen set (an empty
    expected set compares equal to anything and is no evidence)."""
    return (candidate["exit_code"] == 0 and baseline["exit_code"] == 0 and not diffs
            and expected_artefacts > 0)


def _summary_line(text: str) -> str:
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline-dir", required=True)
    ap.add_argument("--candidate-dir", required=True)
    ap.add_argument("--gate-dir", required=True)
    ap.add_argument("--runner-rev", required=True,
                    help="candidate-repo revision of the oracle + fixtures overlaid on the baseline export")
    ap.add_argument("--fixtures", default=str(HARNESS_DIR / "tests" / "fixtures"),
                    help="harness fixtures root (the DigiKey sync-sch-dry run reads simple-project/)")
    ap.add_argument("--label", default="distributor_offline")
    args = ap.parse_args(argv)

    gate = Path(args.gate_dir).resolve()   # the oracle runs with cwd=<tree>; keep every path absolute
    if gate.exists() and any(gate.iterdir()):
        print(f"Error: gate dir {gate} is not empty", file=sys.stderr)
        return 2
    base_dir, cand_dir = Path(args.baseline_dir).resolve(), Path(args.candidate_dir).resolve()
    for d in (base_dir, cand_dir):
        if not (d / ".git").exists():
            print(f"Error: {d} is not a git worktree", file=sys.stderr)
            return 2
    gate.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    base_ref, cand_ref = git_worktree_ref(base_dir), git_worktree_ref(cand_dir)

    base_tree, cand_tree = gate / "baseline_tree", gate / "candidate_tree"
    try:
        git_archive(cand_dir, "HEAD", cand_tree)
        git_archive(base_dir, "HEAD", base_tree)
        git_archive(cand_dir, args.runner_rev, base_tree, (ORACLE, FIXTURES))
        runner_sha = subprocess.run(["git", "-C", str(cand_dir), "rev-parse", f"{args.runner_rev}^{{commit}}"],
                                    check=True, capture_output=True, text=True).stdout.strip()
    except subprocess.CalledProcessError as e:
        err = e.stderr.decode(errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
        print(f"Error: git archive failed: {err.strip()}", file=sys.stderr)
        return 2
    frozen = cand_tree / EXPECTED
    if not frozen.is_dir():
        print(f"Error: candidate has no frozen expected set at {EXPECTED}", file=sys.stderr)
        return 2

    fixtures = Path(args.fixtures).resolve()
    candidate = run_oracle(cand_tree, fixtures, ["--expected", str(frozen)])
    base_expected = gate / "baseline_expected"
    baseline = run_oracle(base_tree, fixtures, ["--write-expected", str(base_expected)])
    diffs = compare_dirs(frozen, base_expected)
    n_expected = sum(1 for p in frozen.rglob("*") if p.is_file())
    ok = gate_pass(candidate, baseline, diffs, n_expected)

    sides = {}
    for name, res, ref in (("candidate", candidate, cand_ref), ("baseline", baseline, base_ref)):
        (gate / f"{name}.stdout.txt").write_text(res["stdout"], encoding="utf-8")
        (gate / f"{name}.stderr.txt").write_text(res["stderr"], encoding="utf-8")
        sides[name] = {"sha": ref.sha, "dirty": ref.dirty, "path": ref.path, "argv": res["argv"],
                       "exit_code": res["exit_code"], "timed_out": res["timed_out"],
                       "summary": _summary_line(res["stdout"])}
    sides["baseline"]["runner_rev"] = args.runner_rev
    sides["baseline"]["runner_sha"] = runner_sha
    record = {
        "profile": PROFILE.name, "label": args.label, "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "timeout_s": PROFILE.timeout_s, "fixtures": str(fixtures),
        "harness": dataclasses.asdict(git_worktree_ref(HARNESS_DIR)),
        "candidate": sides["candidate"], "baseline": sides["baseline"],
        "expected_artefacts": n_expected,
        "diffs": diffs,
        "gate_pass": {"pass": ok, "criterion": CRITERION},
    }
    (gate / "distributor_offline.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(f"=== distributor-offline gate ({args.label}) ===\n"
          f"  candidate {cand_ref.sha[:12]}: exit {candidate['exit_code']}  {sides['candidate']['summary']}\n"
          f"  baseline  {base_ref.sha[:12]} + runner {runner_sha[:12]}: exit {baseline['exit_code']}  "
          f"{sides['baseline']['summary']}\n"
          f"  expected artefacts: {record['expected_artefacts']}   differing: {len(diffs)}\n"
          f"  gate_pass: {'PASS' if ok else 'FAIL'}")
    for rel in diffs[:20]:
        print(f"    differs: {rel}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
