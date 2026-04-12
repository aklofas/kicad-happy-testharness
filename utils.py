"""Shared utilities for the kicad-happy test harness.

Provides path resolution, repo naming, project discovery, and constants
used across discover.py, analyzer runners, baselines, and validators.
"""

import functools
import hashlib
import json
from collections import Counter
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path, PurePosixPath

HARNESS_DIR = Path(__file__).resolve().parent
REPOS_DIR = HARNESS_DIR / "repos"
_data_override = os.environ.get("KICAD_HAPPY_TESTHARNESS_DATA_DIR")
DATA_DIR = Path(_data_override) / "reference" if _data_override else HARNESS_DIR / "reference"
OUTPUTS_DIR = Path(_data_override) / "results" / "outputs" if _data_override else HARNESS_DIR / "results" / "outputs"
MANIFESTS_DIR = HARNESS_DIR / "results" / "manifests"
ANALYZER_TYPES = ["schematic", "pcb", "gerber", "spice", "emc", "thermal", "datasheets"]
MISC_CATEGORY = "Miscellaneous KiCad projects"

# Timeout constants (seconds) — used across runners and validators
ANALYZER_TIMEOUT = 120
GIT_TIMEOUT = 60
TEST_TIMEOUT = 120
INTEGRATION_TEST_TIMEOUT = 600

# Default parallelism — use all available CPUs for max throughput
DEFAULT_JOBS = os.cpu_count() or 4

# Filesystem name-length safety (TH-013)
# 143 bytes is the eCryptfs-with-filename-encryption limit; covers plain
# ext4/xfs/btrfs/APFS (255) automatically. Any name longer than this gets
# deterministically truncated with a SHA1[:10] hash suffix.
NAME_MAX_BYTES = 143
_NAME_HASH_LEN = 10


def _truncate_with_hash(name: str, budget: int = NAME_MAX_BYTES) -> str:
    """Truncate a name to fit within `budget` bytes, appending a short stable hash.

    Uses byte-based truncation (not character-based) so that multi-byte UTF-8
    sequences never get cut mid-character. Deterministic — same input always
    produces the same output.
    """
    encoded = name.encode("utf-8")
    if len(encoded) <= budget:
        return name
    digest = hashlib.sha1(encoded).hexdigest()[:_NAME_HASH_LEN]
    # budget = truncated_prefix + "_" + digest
    truncate_to = budget - _NAME_HASH_LEN - 1
    truncated = encoded[:truncate_to].decode("utf-8", errors="ignore")
    return f"{truncated}_{digest}"


def project_key(pdir: str, stem: str) -> str:
    """Flatten a KiCad project's in-repo path + file stem into a safe directory name.

    Used by discover_projects() to build the `reference/{owner}/{repo}/{key}/`
    directory name for each project. Handles three concerns:

    1. **Separator normalization**: turns `/` and `\\` into `_`.
    2. **Stem deduplication**: when the last path component equals the stem
       (KiCad convention — `foo/foo.kicad_pro`), the stem is not re-appended.
       Saves 30-50% on affected names at zero information cost.
    3. **Length cap**: final name is guaranteed to fit within NAME_MAX_BYTES
       via `_truncate_with_hash()`.
    """
    pdir = (pdir or "").replace("\\", "/").strip("/")
    if not pdir or pdir == ".":
        flat = stem
    elif PurePosixPath(pdir).name == stem:
        # Dedupe — directory basename already equals stem
        flat = pdir.replace("/", "_")
    else:
        flat = pdir.replace("/", "_") + "_" + stem
    return _truncate_with_hash(flat)


CROSS_SECTIONS_FILE = HARNESS_DIR / "reference" / "cross_sections.json"


def project_prefix(project_path: str) -> str:
    """Convert a project path to a filename prefix (e.g., 'sub/dir' → 'sub_dir_').

    Applies the TH-013 length cap to the flattened prefix. The trailing
    underscore is preserved so callers that do `prefix + filename` still work,
    but note: for very long paths the prefix itself may be hash-suffixed, and
    the caller should verify the FINAL concatenated name fits in NAME_MAX_BYTES
    (use `_truncate_with_hash` on the final string if unsure).
    """
    if project_path and project_path != ".":
        flat = project_path.replace("/", "_").replace("\\", "_")
        return _truncate_with_hash(flat, budget=NAME_MAX_BYTES - 1) + "_"
    return ""


def safe_load_json(path, default=None):
    """Load JSON from a file path, returning default on any error."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def resolve_path(data: dict, path: str):
    """Navigate a dotted path through nested dicts/lists.

    Supports bracket notation for array indexing: "items[0].name".
    Returns None if any key is missing or index is out of range.
    """
    parts = path.split(".")
    current = data
    for part in parts:
        if current is None:
            return None
        m = re.match(r'^(\w+)\[(\d+)\]$', part)
        if m:
            key, idx = m.group(1), int(m.group(2))
            current = current.get(key) if isinstance(current, dict) else None
            if isinstance(current, list) and idx < len(current):
                current = current[idx]
            else:
                return None
        elif isinstance(current, dict) and part in current:
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
    """Extract repo name (owner/repo under repos/).

    Given an absolute or relative path like repos/owner/OpenMower/Hardware/...,
    returns 'owner/OpenMower'.
    """
    rel = _path_relative_to_repos(path)
    parts = rel.replace("\\", "/").split("/")
    if len(parts) >= 2 and parts[0] and parts[1]:
        return f"{parts[0]}/{parts[1]}"
    return parts[0] if parts and parts[0] else None


def within_repo_path(path):
    """Get the path within a repo (everything after the owner/repo).

    Given repos/owner/OpenMower/Hardware/board.kicad_sch,
    returns 'Hardware/board.kicad_sch'.
    """
    rel = _path_relative_to_repos(path)
    parts = rel.replace("\\", "/").split("/", 2)
    return parts[2] if len(parts) > 2 else ""


def safe_name(path):
    """Create a flat safe filename from a within-repo path.

    Replaces path separators with underscores and applies the TH-013 length
    cap. Returned name is guaranteed ≤ NAME_MAX_BYTES.
    """
    flat = within_repo_path(path).replace(os.sep, "_").replace("/", "_")
    return _truncate_with_hash(flat)


def list_repos():
    """List repo names (owner/repo) under repos/."""
    if not REPOS_DIR.exists():
        return []
    repos = []
    for owner_dir in sorted(REPOS_DIR.iterdir()):
        if not owner_dir.is_dir() or owner_dir.name.startswith("."):
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if repo_dir.is_dir() and not repo_dir.name.startswith("."):
                repos.append(f"{owner_dir.name}/{repo_dir.name}")
    return repos


def load_cross_section(name):
    """Load a named cross-section from reference/cross_sections.json.

    Returns a list of repo name strings (owner/repo).
    For the "full" section (repos=null), returns list_repos().
    """
    if not CROSS_SECTIONS_FILE.exists():
        print(f"Error: {CROSS_SECTIONS_FILE} not found. "
              "Run: python3 generate_cross_sections.py", file=sys.stderr)
        sys.exit(1)
    data = json.loads(CROSS_SECTIONS_FILE.read_text(encoding="utf-8"))
    sections = data.get("sections", {})
    if name not in sections:
        available = ", ".join(sorted(sections.keys()))
        print(f"Error: cross-section '{name}' not found. "
              f"Available: {available}", file=sys.stderr)
        sys.exit(1)
    repos = sections[name].get("repos")
    if repos is None:
        return list_repos()
    return repos


def add_repo_filter_args(parser):
    """Add --repo, --cross-section, and --repo-list to an argparse parser.

    These are mutually exclusive options for selecting which repos to process.
    """
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--repo", help="Process only this repo (owner/repo)")
    group.add_argument("--cross-section",
                       help="Process repos in a named cross-section "
                            "(from reference/cross_sections.json)")
    group.add_argument("--repo-list",
                       help="Process repos listed in a file (one per line)")
    return group


def resolve_repos(args):
    """Resolve the repo list from parsed args.

    Returns a list of repo names, or None (meaning all repos).
    Uses --repo, --cross-section, or --repo-list from add_repo_filter_args().
    """
    repo = getattr(args, "repo", None)
    cross_section = getattr(args, "cross_section", None)
    repo_list = getattr(args, "repo_list", None)

    if repo:
        return [repo]
    if cross_section:
        return load_cross_section(cross_section)
    if repo_list:
        path = Path(repo_list)
        if not path.exists():
            print(f"Error: {path} not found", file=sys.stderr)
            sys.exit(1)
        repos = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                repos.append(line)
        return repos
    return None


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
        return json.loads(meta_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def filter_manifest_by_repo(lines, repo_name):
    """Filter manifest lines to only those belonging to a given repo.

    repo_name is 'owner/repo' format. Matches against the repos/ directory path.
    """
    marker = f"repos/{repo_name}/"
    marker_os = f"repos{os.sep}{repo_name.replace('/', os.sep)}{os.sep}"
    return [l for l in lines if marker in l or marker_os in l]


# ---------------------------------------------------------------------------
# Project discovery
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=64)
def discover_projects(repo_name):
    """Discover KiCad projects within a repo.

    A project is identified by a directory containing a .kicad_pro (KiCad 6+)
    or .kicad_pcb file.

    Returns list of dicts sorted by name. Each dict has three fields:
        [{"name": "Hardware_OpenMowerMainboard",
          "path": "Hardware/OpenMowerMainboard",
          "stem": "OpenMowerMainboard"}, ...]

    The name is built via `project_key(path, stem)` which handles separator
    normalization, stem deduplication (when the directory basename equals the
    stem, per KiCad convention), and the TH-013 length cap. The stem is the
    basename of the .kicad_pro/.kicad_pcb/.pro marker file (without extension)
    and is retained in the dict so tools like the TH-013 migration script can
    reconstruct the original (pdir, stem) tuple without re-scanning repos/.
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
                first_line = pro5.read_text(errors="replace", encoding="utf-8").split("\n", 1)[0].strip()
                if (first_line.startswith("update=")
                        or first_line.startswith("[pcbnew")
                        or first_line.startswith("[eeschema")):
                    project_dirs[rel] = pro5.stem
            except OSError:
                pass

    projects = []
    for pdir, stem in sorted(project_dirs.items()):
        projects.append({"name": project_key(pdir, stem), "path": pdir, "stem": stem})

    # Resolve conflicts symmetrically: if two or more projects share a name,
    # ALL of them get disambiguated with a path-derived hash. The old code
    # only hashed the second-seen entry, leaving the first with an ambiguous
    # name. Pre-computing the collision set fixes that asymmetry.
    name_counts = Counter(p["name"] for p in projects)
    if any(c > 1 for c in name_counts.values()):
        for p in projects:
            if name_counts[p["name"]] > 1:
                pdir_hash = hashlib.sha1(p["path"].encode("utf-8")).hexdigest()[:_NAME_HASH_LEN]
                p["name"] = _truncate_with_hash(f"{p['name']}_{pdir_hash}")

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
# Resume / skip helpers
# ---------------------------------------------------------------------------

def should_skip_resume(outfile, resume):
    """Check if output file exists and is valid JSON (for --resume)."""
    if not resume:
        return False
    outfile = Path(outfile)
    if not outfile.exists() or outfile.stat().st_size < 3:
        return False
    try:
        json.loads(outfile.read_text(encoding="utf-8"))
        return True
    except (json.JSONDecodeError, OSError):
        return False


# ---------------------------------------------------------------------------
# Schematic/PCB output finders (used by SPICE, EMC, cross-validation)
# ---------------------------------------------------------------------------

def find_schematic_outputs(repo_filter=None):
    """Find all schematic JSON outputs in results/outputs/schematic/."""
    schematic_dir = OUTPUTS_DIR / "schematic"
    if not schematic_dir.exists():
        return []

    outputs = []
    for owner_dir in sorted(schematic_dir.iterdir()):
        if not owner_dir.is_dir():
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir():
                continue
            repo_key = f"{owner_dir.name}/{repo_dir.name}"
            if repo_filter and repo_key != repo_filter:
                continue
            for json_file in sorted(repo_dir.glob("*.json")):
                if json_file.stat().st_size == 0:
                    continue
                outputs.append(json_file)
    return outputs


def find_pcb_output(schematic_json):
    """Find matching PCB output for a schematic output.

    Given results/outputs/schematic/{repo}/{name}.kicad_sch.json,
    looks for results/outputs/pcb/{repo}/{name}.kicad_pcb.json.
    """
    repo_name = f"{schematic_json.parent.parent.name}/{schematic_json.parent.name}"
    pcb_dir = OUTPUTS_DIR / "pcb" / repo_name
    if not pcb_dir.exists():
        return None

    stem = schematic_json.name
    for old, new in [(".kicad_sch.json", ".kicad_pcb.json"),
                     (".sch.json", ".kicad_pcb.json")]:
        if stem.endswith(old):
            pcb_path = pcb_dir / stem.replace(old, new)
            if pcb_path.exists() and pcb_path.stat().st_size > 0:
                return pcb_path
    return None


# ---------------------------------------------------------------------------
# Pipeline step runner (used by add_repos.py)
# ---------------------------------------------------------------------------

def run_pipeline_step(name, cmd, timeout=600):
    """Run a subprocess pipeline step. Returns (success, detail_string)."""
    t0 = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(HARNESS_DIR),
        )
        elapsed = time.time() - t0
        ok = result.returncode == 0
        # Get last non-empty line of output as detail
        lines = result.stdout.strip().splitlines()
        detail = lines[-1] if lines else ""
        if not ok and result.stderr:
            detail = result.stderr.strip().splitlines()[-1]
        return ok, f"[{'OK' if ok else 'FAIL'}] {name} ({elapsed:.1f}s) {detail}"
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        return False, f"[TIMEOUT] {name} ({elapsed:.1f}s)"
    except Exception as e:
        elapsed = time.time() - t0
        return False, f"[ERROR] {name} ({elapsed:.1f}s) {e}"


# ---------------------------------------------------------------------------
# Output repo iteration
# ---------------------------------------------------------------------------

def iter_output_repos(base_dir, repo_filter=None):
    """Yield (repo_name, repo_dir_path) for owner/repo dirs under base_dir."""
    base = Path(base_dir)
    if not base.exists():
        return
    for owner_dir in sorted(base.iterdir()):
        if not owner_dir.is_dir() or owner_dir.name.startswith("."):
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir() or repo_dir.name.startswith("."):
                continue
            repo_name = f"{owner_dir.name}/{repo_dir.name}"
            if repo_filter and repo_name != repo_filter:
                continue
            yield repo_name, repo_dir


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
    "thermal": {"findings", "summary", "thermal_assessments"},
}


def validate_output(outfile, analyzer_type):
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
        errfile.write_text(result.stderr, encoding="utf-8")
        return result.returncode, outfile, time.time() - t0
    except subprocess.TimeoutExpired:
        errfile.write_text(f"Timed out after {ANALYZER_TIMEOUT}s", encoding="utf-8")
        return None, outfile, time.time() - t0


def _print_detector_aggregate(sch_output_dir):
    """Print per-detector hit summary after a schematic batch run."""
    from collections import defaultdict
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
                    sa = data.get("signal_analysis", {})
                    for det, items in sa.items():
                        if isinstance(items, list) and items:
                            detector_files[det] += 1
                            detector_items[det] += len(items)
                except Exception:
                    continue
    if detector_files:
        print(f"\n=== Detector Summary ===")
        for det in sorted(detector_files, key=lambda d: -detector_files[d]):
            print(f"  {det:30s} {detector_files[det]:5d} files, "
                  f"{detector_items[det]:6d} items")


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
        add_repo_filter_args(parser)
        parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                            help=f"Number of parallel analyzer processes (default: {DEFAULT_JOBS})")
        parser.add_argument("--validate", action="store_true",
                            help="Validate output JSON structure after each run")
        parser.add_argument("--json", action="store_true",
                            help="Print JSON summary line at end of output")
        parser.add_argument("--resume", action="store_true",
                            help="Skip files that already have valid output JSON")
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

    files = [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]

    repo_list = resolve_repos(args)
    if repo_list:
        filtered = []
        for rn in repo_list:
            filtered.extend(filter_manifest_by_repo(files, rn))
        files = filtered
        if not files:
            label = repo_list[0] if len(repo_list) == 1 else f"{len(repo_list)} repos"
            print(f"No {config['type_name']}s found for {label}", file=sys.stderr)
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
    do_resume = getattr(args, "resume", False)
    skipped = 0

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
            err_lines = err_path.read_text(encoding="utf-8").strip().splitlines() if err_path.exists() else []
            err_msg = err_lines[-1] if err_lines else f"exit {returncode}"
            return False, f"FAIL [{i}] {relpath}\n     {err_msg}"

    if jobs <= 1:
        for i, file_path in enumerate(files, 1):
            relpath, outfile, errfile = _prepare(file_path)
            if should_skip_resume(outfile, do_resume):
                skipped += 1
                continue
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
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            for i, file_path in enumerate(files, 1):
                relpath, outfile, errfile = _prepare(file_path)
                if should_skip_resume(outfile, do_resume):
                    skipped += 1
                    continue
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
    timing_file.write_text(json.dumps(timing_data, indent=2), encoding="utf-8")

    # Detector aggregate for schematic runs
    if output_subdir == "schematic":
        _print_detector_aggregate(OUTPUTS_DIR / output_subdir)

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
