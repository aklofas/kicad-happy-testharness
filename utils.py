"""Shared utilities for the kicad-happy test harness.

Provides path resolution, repo naming, project discovery, and constants
used across discover.py, analyzer runners, baselines, and validators.
"""

import functools
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
REPOS_DIR = HARNESS_DIR / "repos"
DATA_DIR = HARNESS_DIR / "reference"
MANIFESTS_DIR = HARNESS_DIR / "results" / "manifests"
OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"
ANALYZER_TYPES = ["schematic", "pcb", "gerber", "spice", "emc", "datasheets"]

# Timeout constants (seconds) — used across runners and validators
ANALYZER_TIMEOUT = 120
GIT_TIMEOUT = 60
TEST_TIMEOUT = 120
INTEGRATION_TEST_TIMEOUT = 600


def project_prefix(project_path: str) -> str:
    """Convert a project path to a filename prefix (e.g., 'sub/dir' → 'sub_dir_')."""
    if project_path and project_path != ".":
        return project_path.replace("/", "_").replace("\\", "_") + "_"
    return ""


def safe_load_json(path, default=None):
    """Load JSON from a file path, returning default on any error."""
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def resolve_path(data: dict, path: str):
    """Navigate a dotted path through nested dicts. Returns None if any key is missing."""
    parts = path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _path_relative_to_repos(path):
    """Get path relative to the repos/ directory.

    Handles both absolute paths under REPOS_DIR and paths containing 'repos/'.
    Returns the relative path string (e.g., 'OpenMower/Hardware/board.kicad_sch').
    """
    path = str(path)
    repos_str = str(REPOS_DIR)
    if path.startswith(repos_str):
        return path[len(repos_str):].lstrip(os.sep)
    idx = path.find("repos" + os.sep)
    if idx >= 0:
        return path[idx + len("repos") + 1:]
    return path


def repo_name_from_path(path):
    """Extract repo name (first component under repos/).

    Given an absolute or relative path like repos/OpenMower/Hardware/...,
    returns 'OpenMower'.
    """
    rel = _path_relative_to_repos(path)
    parts = rel.replace("\\", "/").split("/")
    return parts[0] if parts and parts[0] else None


def within_repo_path(path):
    """Get the path within a repo (everything after the repo name).

    Given repos/OpenMower/Hardware/board.kicad_sch,
    returns 'Hardware/board.kicad_sch'.
    """
    rel = _path_relative_to_repos(path)
    parts = rel.replace("\\", "/").split("/", 1)
    return parts[1] if len(parts) > 1 else ""


def safe_name(path):
    """Create a flat safe filename from a within-repo path.

    Replaces path separators with underscores.
    """
    return within_repo_path(path).replace(os.sep, "_").replace("/", "_")


def list_repos():
    """List repo directory names under repos/."""
    if not REPOS_DIR.exists():
        return []
    return sorted(d.name for d in REPOS_DIR.iterdir() if d.is_dir() and not d.name.startswith("."))


def resolve_kicad_happy_dir():
    """Resolve path to kicad-happy repo."""
    if "KICAD_HAPPY_DIR" in os.environ:
        p = Path(os.environ["KICAD_HAPPY_DIR"])
        if p.exists():
            return p
        print(f"Error: KICAD_HAPPY_DIR={p} does not exist", file=sys.stderr)
        sys.exit(1)
    fallback = HARNESS_DIR.parent / "kicad-happy"
    if fallback.exists():
        return fallback
    print("Error: Cannot find kicad-happy repo.", file=sys.stderr)
    print("  Set KICAD_HAPPY_DIR or clone it alongside this repo.", file=sys.stderr)
    sys.exit(1)


def filter_project_outputs(type_dir, project_path):
    """Filter output JSON files in type_dir to those matching a project path prefix."""
    prefix = project_prefix(project_path)
    files = sorted(type_dir.glob("*.json"))
    if not prefix:
        return files
    return [f for f in files if f.name.startswith(prefix)]


def load_project_metadata(repo_name, project_name):
    """Load baseline metadata for a project. Returns dict (empty if missing)."""
    meta_file = DATA_DIR / repo_name / project_name / "baselines" / "metadata.json"
    try:
        return json.loads(meta_file.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def filter_manifest_by_repo(lines, repo_name):
    """Filter manifest lines to only those belonging to a given repo."""
    repos_str = str(REPOS_DIR)
    prefix = repos_str + os.sep + repo_name + os.sep
    return [l for l in lines if l.startswith(prefix)]


# ---------------------------------------------------------------------------
# Project discovery
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=64)
def discover_projects(repo_name):
    """Discover KiCad projects within a repo.

    A project is identified by a directory containing a .kicad_pro (KiCad 6+)
    or .kicad_pcb file.

    Returns list of dicts sorted by name:
        [{"name": "Hardware_OpenMowerMainboard", "path": "Hardware/OpenMowerMainboard"}, ...]

    The name is the directory path from repo root with / → _.
    For root-level projects, the name is the .kicad_pro/.kicad_pcb stem.
    """
    repo_dir = REPOS_DIR / repo_name
    if not repo_dir.exists():
        return []

    # Find project directories: prefer .kicad_pro, fall back to .kicad_pcb
    project_dirs = {}  # rel_path -> marker_file_stem
    for pro in repo_dir.rglob("*.kicad_pro"):
        rel = str(pro.parent.relative_to(repo_dir))
        if rel not in project_dirs:
            project_dirs[rel] = pro.stem

    for pcb in repo_dir.rglob("*.kicad_pcb"):
        rel = str(pcb.parent.relative_to(repo_dir))
        if rel not in project_dirs:
            project_dirs[rel] = pcb.stem

    # KiCad 4/5 .pro files — check header to confirm KiCad format
    for pro5 in repo_dir.rglob("*.pro"):
        rel = str(pro5.parent.relative_to(repo_dir))
        if rel not in project_dirs:
            try:
                first_line = pro5.read_text(errors="replace").split("\n", 1)[0].strip()
                if (first_line.startswith("update=")
                        or first_line.startswith("[pcbnew")
                        or first_line.startswith("[eeschema")):
                    project_dirs[rel] = pro5.stem
            except OSError:
                pass

    projects = []
    for pdir, stem in sorted(project_dirs.items()):
        if pdir == ".":
            name = stem
        else:
            name = pdir.replace("/", "_").replace("\\", "_") + "_" + stem
        projects.append({"name": name, "path": pdir})

    # Check for uniqueness
    names = [p["name"] for p in projects]
    if len(names) != len(set(names)):
        # Resolve conflicts by appending path hash
        seen = {}
        for p in projects:
            if p["name"] in seen:
                # Conflict — disambiguate with parent dir
                p["name"] = p["path"].replace("/", "_").replace("\\", "_") or p["name"]
            seen[p["name"]] = p

    return sorted(projects, key=lambda p: p["name"])


def data_dir(repo_name, project_name, section=None):
    """Get the data directory for a repo/project (optionally with section).

    section is one of: "baselines", "assertions", or None.
    Returns: DATA_DIR / repo / project [/ section]
    """
    base = DATA_DIR / repo_name / project_name
    return base / section if section else base


def list_projects_in_data(repo_name):
    """List project names that exist in data/ for a repo.

    Useful when repos aren't checked out — reads from the data directory.
    """
    repo_dir = DATA_DIR / repo_name
    if not repo_dir.exists():
        return []
    projects = []
    for d in sorted(repo_dir.iterdir()):
        if d.is_dir() and not d.name.startswith("."):
            # Check it has at least one section subdir
            has_section = any((d / s).exists() for s in ["baselines", "assertions", "findings.json"])
            if has_section:
                projects.append(d.name)
    return projects


# ---------------------------------------------------------------------------
# Output validation
# ---------------------------------------------------------------------------

# Minimum required top-level keys per analyzer type (signature check)
EXPECTED_KEYS = {
    "schematic": {"components", "statistics", "signal_analysis"},
    "pcb": {"footprints", "statistics", "connectivity"},
    "gerber": {"layers", "summary"},
    "emc": {"findings", "summary"},
    "spice": {"simulation_results", "summary"},
}


def validate_output(outfile, analyzer_type):
    """Check an output file is valid JSON with expected keys.

    Returns (ok, message).
    """
    if not outfile.exists():
        return False, "output file missing"
    try:
        data = json.loads(outfile.read_text())
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e}"
    if not isinstance(data, dict):
        return False, f"expected dict, got {type(data).__name__}"
    expected = EXPECTED_KEYS.get(analyzer_type, set())
    missing = expected - set(data.keys())
    if missing:
        return False, f"missing keys: {sorted(missing)}"
    return True, "ok"


# ---------------------------------------------------------------------------
# Shared analyzer runner
# ---------------------------------------------------------------------------

def _run_one(analyzer, file_path, outfile, errfile, extra_args=None):
    """Run a single analyzer subprocess. Returns (returncode, outfile, elapsed_s)."""
    cmd = [sys.executable, str(analyzer), file_path, "-o", str(outfile)]
    if extra_args:
        cmd.extend(extra_args)
    t0 = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=ANALYZER_TIMEOUT,
        )
        errfile.write_text(result.stderr)
        return result.returncode, outfile, time.time() - t0
    except subprocess.TimeoutExpired:
        errfile.write_text(f"Timed out after {ANALYZER_TIMEOUT}s")
        return None, outfile, time.time() - t0


def run_analyzer(config, args=None):
    """Shared runner for all analyzer types.

    config keys:
        type_name:       Display name (e.g., "schematic")
        analyzer_script: Script filename (e.g., "analyze_schematic.py")
        manifest_file:   Manifest filename (e.g., "all_schematics.txt")
        output_subdir:   Output subdir (e.g., "schematic")
        summarize:       callable(json_data) -> str, extracts summary from output
    """
    import argparse as _argparse

    if args is None:
        parser = _argparse.ArgumentParser(
            description=f"Run {config['type_name']} analysis"
        )
        parser.add_argument("--repo", help=f"Only analyze {config['type_name']}s for this repo")
        parser.add_argument("--jobs", "-j", type=int, default=1,
                            help="Number of parallel analyzer processes (default: 1)")
        parser.add_argument("--validate", action="store_true",
                            help="Validate output JSON structure after each run")
        parser.add_argument("--json", action="store_true",
                            help="Print JSON summary line at end of output")
        args = parser.parse_args()

    kicad_happy = resolve_kicad_happy_dir()
    analyzer = kicad_happy / "skills" / "kicad" / "scripts" / config["analyzer_script"]

    if not analyzer.exists():
        print(f"Error: {analyzer} not found", file=sys.stderr)
        sys.exit(1)

    manifest = MANIFESTS_DIR / config["manifest_file"]

    if not manifest.exists():
        print(f"Error: {config['manifest_file']} not found. Run discover.py first.", file=sys.stderr)
        sys.exit(1)

    files = [line.strip() for line in manifest.read_text().splitlines() if line.strip()]

    if args.repo:
        files = filter_manifest_by_repo(files, args.repo)
        if not files:
            print(f"No {config['type_name']}s found for repo '{args.repo}'", file=sys.stderr)
            sys.exit(1)

    type_name = config["type_name"]
    output_subdir = config["output_subdir"]
    summarize = config["summarize"]
    extra_args = config.get("extra_args")
    jobs = getattr(args, "jobs", 1)

    print(f"=== Running {type_name} analysis ===")
    print(f"Analyzer: {analyzer}")
    print(f"Files: {len(files)}")
    if jobs > 1:
        print(f"Jobs: {jobs}")
    print()

    passed = failed = 0
    timings = []  # (relpath, elapsed_s)
    t_start = time.time()
    repos_str = str(REPOS_DIR)

    def _prepare(file_path):
        repo = repo_name_from_path(file_path)
        sname = safe_name(file_path)
        relpath = file_path[len(repos_str):].lstrip(os.sep) if file_path.startswith(repos_str) else file_path
        repo_out_dir = OUTPUTS_DIR / output_subdir / repo
        repo_out_dir.mkdir(parents=True, exist_ok=True)
        outfile = repo_out_dir / f"{sname}.json"
        errfile = repo_out_dir / f"{sname}.err"
        return relpath, outfile, errfile

    do_validate = getattr(args, "validate", False)

    def _format_result(i, relpath, returncode, outfile):
        if returncode == 0:
            if do_validate:
                ok, msg = validate_output(outfile, output_subdir)
                if not ok:
                    return False, f"VFAIL [{i}] {relpath}\n     {msg}"
            try:
                with open(outfile) as f:
                    d = json.load(f)
                summary = summarize(d)
                return True, f"PASS [{i}] {relpath} ({summary})"
            except Exception:
                return True, f"PASS [{i}] {relpath} (parse_error)"
        elif returncode is None:
            return False, f"FAIL [{i}] {relpath}\n     Timed out"
        else:
            err_path = outfile.with_suffix(".err")
            err_lines = err_path.read_text().strip().splitlines() if err_path.exists() else []
            err_msg = err_lines[-1] if err_lines else f"exit {returncode}"
            return False, f"FAIL [{i}] {relpath}\n     {err_msg}"

    if jobs <= 1:
        for i, file_path in enumerate(files, 1):
            relpath, outfile, errfile = _prepare(file_path)
            returncode, _, elapsed = _run_one(analyzer, file_path, outfile, errfile, extra_args)
            timings.append((relpath, elapsed))
            ok, msg = _format_result(i, relpath, returncode, outfile)
            if ok:
                passed += 1
            else:
                failed += 1
            print(msg)
    else:
        # Parallel execution
        tasks = {}
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            for i, file_path in enumerate(files, 1):
                relpath, outfile, errfile = _prepare(file_path)
                future = pool.submit(_run_one, analyzer, file_path, outfile, errfile, extra_args)
                tasks[future] = (i, relpath, outfile)
            for future in as_completed(tasks):
                i, relpath, outfile = tasks[future]
                returncode, _, elapsed = future.result()
                timings.append((relpath, elapsed))
                ok, msg = _format_result(i, relpath, returncode, outfile)
                if ok:
                    passed += 1
                else:
                    failed += 1
                print(msg)

    total = passed + failed
    total_elapsed = time.time() - t_start
    avg_elapsed = sum(t for _, t in timings) / len(timings) if timings else 0
    slowest = sorted(timings, key=lambda x: -x[1])[:5]

    print(f"\n=== Results ===")
    print(f"Total: {total}")
    print(f"Pass:  {passed}")
    print(f"Fail:  {failed}")
    if total > 0:
        print(f"Rate:  {passed * 100 / total:.1f}%")
    print(f"Time:  {total_elapsed:.1f}s total, {avg_elapsed:.2f}s avg per file")
    if slowest:
        print(f"Slowest:")
        for path, t in slowest:
            print(f"  {t:6.1f}s  {path}")

    # Write timing data
    timing_file = OUTPUTS_DIR / output_subdir / "_timing.json"
    timing_file.parent.mkdir(parents=True, exist_ok=True)
    timing_data = {
        "total_files": total,
        "total_elapsed_s": round(total_elapsed, 2),
        "avg_per_file_s": round(avg_elapsed, 3),
        "slowest": [{"file": p, "elapsed_s": round(t, 3)} for p, t in slowest],
        "all": [{"file": p, "elapsed_s": round(t, 3)} for p, t in
                sorted(timings, key=lambda x: x[0])],
    }
    timing_file.write_text(json.dumps(timing_data, indent=2))

    # JSON summary line (for machine consumption by run_corpus.py)
    if getattr(args, "json", False):
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
