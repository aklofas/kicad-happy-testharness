"""Batch lifecycle for the manifest-driven runners (schematic, pcb, gerber): selection
filtering, name-collision check, run identity, per-unit execution, unit log, totals.

run_batch returns the process exit code instead of exiting; utils.run_analyzer is the
CLI adapter in front of it."""

import json
import os
import platform
import sys
import time
import uuid
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from harnesslib.corpus import filter_manifest_by_repo, repo_name_from_path, safe_name
from harnesslib.execution import build_env, recorded_env, run_once
from harnesslib.identity import (RunSpec, UNITS_NAME, UnitLog, finish_manifest,
                                 git_worktree_ref, input_digest, manifests_match,
                                 read_manifest, sha256_path, unit_is_current, write_manifest)
from harnesslib.profiles import PROFILES

ANALYZER_TIMEOUT = PROFILES["standard"].timeout_s


@dataclass(frozen=True)
class BatchConfig:
    type_name: str
    analyzer_script: str
    manifest_file: str
    output_subdir: str
    summarize: Callable
    extra_args: tuple[str, ...] = ()


@dataclass(frozen=True)
class BatchSettings:
    jobs: int
    validate: bool
    json: bool
    resume: bool
    online: bool
    timeout: int


@dataclass(frozen=True)
class BatchPaths:
    harness_dir: Path
    product_root: Path
    repos_dir: Path
    outputs_dir: Path
    manifests_dir: Path


# Minimum required top-level keys per analyzer type (signature check)
EXPECTED_KEYS = {
    "schematic": {"components", "statistics", "findings"},
    "pcb": {"footprints", "statistics", "connectivity"},
    "gerber": {"layers", "summary"},
    "emc": {"findings", "summary"},
    "spice": {"simulation_results", "summary"},
    "thermal": {"findings", "summary"},
}


def validate_required_keys(outfile, analyzer_type):
    """Check an output file is valid JSON with expected keys.

    Returns (ok, message).
    """
    if not outfile.exists():
        return False, "output file missing"
    try:
        data = json.loads(outfile.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e}"
    if not isinstance(data, dict):
        return False, f"expected dict, got {type(data).__name__}"
    expected = EXPECTED_KEYS.get(analyzer_type, set())
    missing = expected - set(data.keys())
    if missing:
        return False, f"missing keys: {sorted(missing)}"
    return True, "ok"


def _run_one(analyzer, file_path, outfile, errfile, extra_args=None, timeout=None,
             analyzer_type="schematic", env=None):
    """Run one analyzer subprocess through harnesslib.execution.run_once.

    Returns (returncode, outfile, elapsed_s, status, output_sha256). The output
    is written to a private temp path, validated, and published atomically; a
    stale previous output is quarantined as <outfile>.stale on any failure.
    `timeout` is the per-file cap in seconds (default: standard profile)."""
    cap = ANALYZER_TIMEOUT if timeout is None else timeout

    def make_cmd(out_path):
        cmd = [sys.executable, str(analyzer), file_path, "-o", str(out_path)]
        if extra_args:
            cmd.extend(extra_args)
        return cmd

    res = run_once(make_cmd, Path(outfile), analyzer=analyzer_type, timeout=cap,
                   env=env or build_env(offline=True))
    if res.status == "timeout":
        errfile.write_text(f"Timed out after {cap}s", encoding="utf-8")
    elif res.status in ("ok", "ok_findings_exit"):
        errfile.write_text("", encoding="utf-8")
    else:
        errfile.write_text(res.stderr_tail or res.detail, encoding="utf-8")
    return res.exit_code, outfile, res.elapsed_s, res.status, res.output_sha256


def _print_detector_aggregate(sch_output_dir):
    """Print per-detector hit summary after a schematic batch run."""
    detector_files = defaultdict(int)
    detector_items = defaultdict(int)
    for owner_dir in sorted(sch_output_dir.iterdir()):
        if not owner_dir.is_dir():
            continue
        for repo_dir in owner_dir.iterdir():
            if not repo_dir.is_dir():
                continue
            for f in repo_dir.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    grouped = {}
                    for finding in data.get("findings", []):
                        det = finding.get("detector", "")
                        if det:
                            grouped.setdefault(det, []).append(finding)
                    for det, items in grouped.items():
                        detector_files[det] += 1
                        detector_items[det] += len(items)
                except Exception:
                    continue
    if detector_files:
        print(f"\n=== Detector Summary ===")
        for det in sorted(detector_files, key=lambda d: -detector_files[d]):
            print(f"  {det:30s} {detector_files[det]:5d} files, "
                  f"{detector_items[det]:6d} items")


def preflight(config, paths):
    """Check the analyzer script and the manifest exist; print the error and return 1 if
    not, else 0. The CLI adapter runs this before resolving the selection so the user
    sees the same error order as always."""
    analyzer = paths.product_root / "skills" / "kicad" / "scripts" / config.analyzer_script

    if not analyzer.exists():
        print(f"Error: {analyzer} not found", file=sys.stderr)
        return 1

    manifest = paths.manifests_dir / config.manifest_file

    if not manifest.exists():
        print(f"Error: {config.manifest_file} not found. Run discover.py first.", file=sys.stderr)
        return 1
    return 0


def run_batch(config, settings, paths, *, repo_list, selection_source, argv):
    """Run one analyzer over the manifest units in the selection and return the process
    exit code: 0 all passed, 1 a failure (or missing inputs, or an empty selection),
    2 colliding output names. `argv` is the CLI argv recorded in the run manifest."""
    rc = preflight(config, paths)
    if rc:
        return rc
    analyzer = paths.product_root / "skills" / "kicad" / "scripts" / config.analyzer_script
    manifest = paths.manifests_dir / config.manifest_file

    files = [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]

    if repo_list is not None:
        filtered = []
        for rn in repo_list:
            filtered.extend(filter_manifest_by_repo(files, rn))
        files = filtered
        if not files:
            label = repo_list[0] if len(repo_list) == 1 else f"{len(repo_list)} repos"
            print(f"No {config.type_name}s found for {label}", file=sys.stderr)
            return 1

    # safe_name flattens "/" to "_": two inputs with one flat name would share an output
    # file and a unit id, the second silently overwriting the first
    by_name = defaultdict(list)
    for f in files:
        by_name[(repo_name_from_path(f, paths.repos_dir), safe_name(f, paths.repos_dir))].append(f)
    dups = {k: v for k, v in by_name.items() if len(v) > 1}
    if dups:
        print(f"Error: {len(dups)} output names collide after path flattening:", file=sys.stderr)
        for (repo, name), paths_ in sorted(dups.items()):
            print(f"  {repo}/{name}: {', '.join(sorted(paths_))}", file=sys.stderr)
        return 2

    type_name = config.type_name
    output_subdir = config.output_subdir
    summarize = config.summarize
    extra_args = config.extra_args
    jobs = settings.jobs

    env = build_env(offline=not settings.online)
    out_root = paths.outputs_dir / output_subdir
    out_root.mkdir(parents=True, exist_ok=True)

    def _uid(f):
        return f"{repo_name_from_path(f, paths.repos_dir)}/{safe_name(f, paths.repos_dir)}"

    unit_ids = sorted(_uid(f) for f in files)
    spec = RunSpec(kind="batch", profile="standard", harness=git_worktree_ref(paths.harness_dir),
                   baseline=None, candidate=git_worktree_ref(paths.product_root),
                   argv=tuple(a for a in argv if a != "--resume") + tuple(extra_args or ()),
                   selection_source=selection_source, unit_ids=tuple(unit_ids),
                   normalization_policy="volatile-leaves-v1", env=recorded_env(env))
    input_hashes = {f: sha256_path(f) for f in files}
    do_resume = settings.resume
    try:
        prev = read_manifest(out_root)
    except (OSError, ValueError):
        prev = None
    run_id = str(uuid.uuid4())

    def _write(rid):
        write_manifest(out_root, spec, run_id=rid,
                       expected_census={output_subdir: len(files)},
                       input_digest=input_digest((_uid(f), h) for f, h in input_hashes.items()),
                       runtime={"python": platform.python_version(),
                                "platform": platform.platform()})

    _write(run_id)
    if do_resume:
        if prev is None:
            print("resume disabled: no prior manifest")
            do_resume = False
        else:
            same, reasons = manifests_match(prev, read_manifest(out_root))
            if not same:
                print("resume disabled: " + "; ".join(reasons))
                do_resume = False
    if do_resume:
        # continue the matched run: its records stay current only under its run_id
        run_id = prev.get("run_id") or run_id
        _write(run_id)
    elif prev is not None and (out_root / UNITS_NAME).exists():
        # never let a later resume see records from an earlier, different run
        old_id = prev.get("run_id") or "unknown"
        os.replace(out_root / UNITS_NAME, out_root / f"units.{old_id}.jsonl")
    log = UnitLog(out_root)

    print(f"=== Running {type_name} analysis ===")
    print(f"Analyzer: {analyzer}")
    print(f"Files: {len(files)}")
    if jobs > 1:
        print(f"Jobs: {jobs}")
    print()

    passed = failed = 0
    timings = []  # (relpath, elapsed_s)
    t_start = time.time()
    repos_str = str(paths.repos_dir)

    def _prepare(file_path):
        repo = repo_name_from_path(file_path, paths.repos_dir)
        sname = safe_name(file_path, paths.repos_dir)
        relpath = file_path[len(repos_str):].lstrip(os.sep) if file_path.startswith(repos_str) else file_path
        repo_out_dir = paths.outputs_dir / output_subdir / repo
        repo_out_dir.mkdir(parents=True, exist_ok=True)
        outfile = repo_out_dir / f"{sname}.json"
        errfile = repo_out_dir / f"{sname}.err"
        return relpath, outfile, errfile

    do_validate = settings.validate
    skipped = 0

    def _format_result(i, relpath, returncode, outfile, status):
        if status in ("ok", "ok_findings_exit"):
            if do_validate:
                ok, msg = validate_required_keys(outfile, output_subdir)
                if not ok:
                    return False, f"VFAIL [{i}] {relpath}\n     {msg}"
            with open(outfile) as f:
                summary = summarize(json.load(f))
            return True, f"PASS [{i}] {relpath} ({summary})"
        if status == "timeout":
            return False, f"FAIL [{i}] {relpath}\n     Timed out"
        err_path = outfile.with_suffix(".err")
        err_lines = err_path.read_text(encoding="utf-8").strip().splitlines() if err_path.exists() else []
        err_msg = err_lines[-1] if err_lines else f"exit {returncode}"
        return False, f"FAIL [{i}] {relpath}\n     {status}: {err_msg}"

    def _recorded_status(ok, status):
        # a published output that fails --validate is a failure, never an ok unit a
        # later --resume would skip
        return "validation_failed" if not ok and status in ("ok", "ok_findings_exit") else status

    def _record(file_path, returncode, elapsed, status, out_sha):
        log.append({"analyzer": output_subdir, "unit_id": _uid(file_path),
                    "run_id": run_id, "input_sha256": input_hashes[file_path], "status": status,
                    "exit_code": returncode, "output_sha256": out_sha,
                    "elapsed_s": round(elapsed, 3)})

    def _current(file_path, outfile):
        return do_resume and unit_is_current(log, output_subdir, _uid(file_path),
                                             input_hashes[file_path], outfile,
                                             run_id=run_id)

    cap = settings.timeout
    status_totals = Counter()
    if jobs <= 1:
        for i, file_path in enumerate(files, 1):
            relpath, outfile, errfile = _prepare(file_path)
            if _current(file_path, outfile):
                skipped += 1
                continue
            returncode, _, elapsed, status, out_sha = _run_one(
                analyzer, file_path, outfile, errfile, extra_args, cap, output_subdir, env)
            ok, msg = _format_result(i, relpath, returncode, outfile, status)
            status = _recorded_status(ok, status)
            _record(file_path, returncode, elapsed, status, out_sha)
            status_totals[status] += 1
            timings.append((relpath, elapsed))
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)
            print(msg)
    else:
        tasks = {}
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            for i, file_path in enumerate(files, 1):
                relpath, outfile, errfile = _prepare(file_path)
                if _current(file_path, outfile):
                    skipped += 1
                    continue
                future = pool.submit(_run_one, analyzer, file_path, outfile, errfile,
                                     extra_args, cap, output_subdir, env)
                tasks[future] = (i, relpath, outfile, file_path)
            for future in as_completed(tasks):
                i, relpath, outfile, file_path = tasks[future]
                returncode, _, elapsed, status, out_sha = future.result()
                ok, msg = _format_result(i, relpath, returncode, outfile, status)
                status = _recorded_status(ok, status)
                _record(file_path, returncode, elapsed, status, out_sha)
                status_totals[status] += 1
                timings.append((relpath, elapsed))
                passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)
                print(msg)

    total = passed + failed
    total_elapsed = time.time() - t_start
    avg_elapsed = sum(t for _, t in timings) / len(timings) if timings else 0
    slowest = sorted(timings, key=lambda x: -x[1])[:5]

    print(f"\n=== Results ===")
    print(f"Total: {total}")
    print(f"Pass:  {passed}")
    print(f"Fail:  {failed}")
    if skipped:
        print(f"Skip:  {skipped} (existing output, --resume)")
    if total > 0:
        print(f"Rate:  {passed * 100 / total:.1f}%")
    print(f"Time:  {total_elapsed:.1f}s total, {avg_elapsed:.2f}s avg per file")
    if slowest:
        print(f"Slowest:")
        for path, t in slowest:
            print(f"  {t:6.1f}s  {path}")

    # Write timing data
    timing_file = paths.outputs_dir / output_subdir / "_timing.json"
    timing_file.parent.mkdir(parents=True, exist_ok=True)
    timing_data = {
        "total_files": total,
        "total_elapsed_s": round(total_elapsed, 2),
        "avg_per_file_s": round(avg_elapsed, 3),
        "slowest": [{"file": p, "elapsed_s": round(t, 3)} for p, t in slowest],
        "all": [{"file": p, "elapsed_s": round(t, 3)} for p, t in
                sorted(timings, key=lambda x: x[0])],
    }
    timing_file.write_text(json.dumps(timing_data, indent=2), encoding="utf-8")

    finish_manifest(out_root, {**dict(status_totals), "skipped": skipped})

    # Detector aggregate for schematic runs
    if output_subdir == "schematic":
        _print_detector_aggregate(paths.outputs_dir / output_subdir)

    # JSON summary line (for machine consumption by run_corpus.py)
    if settings.json:
        summary = {
            "type": output_subdir,
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{passed * 100 / total:.1f}%" if total > 0 else "N/A",
            "elapsed_s": round(total_elapsed, 2),
            "avg_per_file_s": round(avg_elapsed, 3) if total > 0 else 0,
        }
        print(json.dumps(summary))
    if failed:
        return 1
    return 0


def map_units(fn, units, jobs, *, unpack=False):
    """Apply fn to each unit; results come back in input order whatever the
    completion order. Sequential when jobs <= 1. With unpack, each unit is a sequence
    spread as fn(*unit)."""
    units = list(units)
    if jobs <= 1:
        return [fn(*u) if unpack else fn(u) for u in units]
    results = [None] * len(units)
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        futures = {(pool.submit(fn, *u) if unpack else pool.submit(fn, u)): i
                   for i, u in enumerate(units)}
        for future in as_completed(futures):
            results[futures[future]] = future.result()
    return results
