"""Shared utilities for the kicad-happy test harness.

Provides path resolution, repo naming, project discovery, and constants
used across discover.py, analyzer runners, baselines, and validators.
"""

import functools
import hashlib
import json
from collections import Counter, defaultdict
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path, PurePosixPath

from harnesslib.profiles import PROFILES as _PROFILES

HARNESS_DIR = Path(__file__).resolve().parent
# KICAD_HAPPY_TESTHARNESS_DATA_DIR moves every corpus data path at once (checkouts,
# reference data, outputs, manifests), so a redirected run never reads or writes the live tree
_data_override = os.environ.get("KICAD_HAPPY_TESTHARNESS_DATA_DIR")
DATA_ROOT = Path(_data_override) if _data_override else HARNESS_DIR
REPOS_DIR = DATA_ROOT / "repos"
DATA_DIR = DATA_ROOT / "reference"
OUTPUTS_DIR = DATA_ROOT / "results" / "outputs"
MANIFESTS_DIR = DATA_ROOT / "results" / "manifests"
ANALYZER_TYPES = ["schematic", "pcb", "gerber", "spice", "emc", "thermal", "datasheets"]
MISC_CATEGORY = "Miscellaneous KiCad projects"

# Timeout constants (seconds). ANALYZER_TIMEOUT is the standard profile's cap;
# runners take an explicit --timeout and pass it down (TH-055).
ANALYZER_TIMEOUT = _PROFILES["standard"].timeout_s
GIT_TIMEOUT = 60
TEST_TIMEOUT = 120
INTEGRATION_TEST_TIMEOUT = 600

# H0: shared mechanics live in harnesslib/; re-exported so existing importers keep working.
from harnesslib.execution import (run_once, build_env, recorded_env,  # noqa: F401,E402
                                  RunResult, STATUSES, ACCEPTED_EXITS)
from harnesslib.identity import (RunSpec, WorktreeRef, git_worktree_ref,  # noqa: F401,E402
                                 sha256_file, sha256_path, UnitLog, unit_is_current)
from harnesslib.selection import EmptySelection, NoSelection, filter_units  # noqa: F401,E402

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


CROSS_SECTIONS_FILE = DATA_DIR / "cross_sections.json"


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


def atomic_write_text(path, text):
    """Write a tracked source-of-truth file through a temp file and os.replace, so a crash
    or a concurrent reader never sees a torn file."""
    path = Path(path)
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


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
    """Add --repo, --cross-section, --repo-list and --all to an argparse parser.

    The first three are mutually exclusive selectors; --all is the explicit
    whole-corpus switch required by mutating batch runs (B12/TH-049).
    """
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--repo", help="Process only this repo (owner/repo)")
    group.add_argument("--cross-section",
                       help="Process repos in a named cross-section "
                            "(from reference/cross_sections.json)")
    group.add_argument("--repo-list",
                       help="Process repos listed in a file (one per line)")
    group.add_argument("--all", dest="all_repos", action="store_true",
                       help="Process the whole corpus (required for mutating runs)")
    return group


def resolve_repos_with_source(args, require_explicit_all=False):
    """Resolve (repos, selection_source) from parsed args.

    repos is a list, or None meaning all repos. An explicit empty selection
    exits 2; a run with no selector and no --all exits 2 when
    require_explicit_all is set.
    """
    from harnesslib.selection import resolve_selection, EmptySelection, NoSelection
    try:
        return resolve_selection(
            repo=getattr(args, "repo", None),
            cross_section=getattr(args, "cross_section", None),
            repo_list=getattr(args, "repo_list", None),
            all_=getattr(args, "all_repos", False),
            require_explicit_all=require_explicit_all,
            load_cross_section=load_cross_section)
    except NoSelection as e:
        print(f"Error: {e} ({len(list_repos())} repos in corpus)", file=sys.stderr)
        sys.exit(2)
    except (EmptySelection, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


def resolve_repos(args, require_explicit_all=False):
    """Resolve the repo list from parsed args: a list, or None (all repos)."""
    return resolve_repos_with_source(args, require_explicit_all)[0]


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
    # TH-046: a line may be exactly the repo directory with nothing after it
    # (root-level gerber sets) — match it too, on a path-component boundary.
    root = f"/{marker[:-1]}"
    root_os = f"{os.sep}repos{os.sep}{repo_name.replace('/', os.sep)}"
    return [l for l in lines
            if marker in l or marker_os in l
            or l.endswith(root) or l.endswith(root_os)]


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

    # Find projects: each .kicad_pro is a separate project (multiple can share a dir)
    seen = set()  # (rel_dir, stem) dedup
    project_entries = []  # list of (rel_dir, stem)

    for pro in sorted(repo_dir.rglob("*.kicad_pro")):
        rel = str(pro.parent.relative_to(repo_dir))
        key = (rel, pro.stem)
        if key not in seen:
            seen.add(key)
            project_entries.append(key)

    # Fall back to .kicad_pcb for dirs with no .kicad_pro
    dirs_with_pro = {rel for rel, _ in project_entries}
    for pcb in sorted(repo_dir.rglob("*.kicad_pcb")):
        rel = str(pcb.parent.relative_to(repo_dir))
        if rel not in dirs_with_pro:
            key = (rel, pcb.stem)
            if key not in seen:
                seen.add(key)
                project_entries.append(key)
                dirs_with_pro.add(rel)

    # KiCad 4/5 .pro files — check header to confirm KiCad format
    for pro5 in sorted(repo_dir.rglob("*.pro")):
        rel = str(pro5.parent.relative_to(repo_dir))
        if rel not in dirs_with_pro:
            key = (rel, pro5.stem)
            if key not in seen:
                try:
                    first_line = pro5.read_text(errors="replace", encoding="utf-8").split("\n", 1)[0].strip()
                    if (first_line.startswith("update=")
                            or first_line.startswith("[pcbnew")
                            or first_line.startswith("[eeschema")):
                        seen.add(key)
                        project_entries.append(key)
                        dirs_with_pro.add(rel)
                except OSError:
                    pass

    projects = []
    for pdir, stem in sorted(project_entries):
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
    """DEPRECATED (TH-049): parses-as-JSON is not identity. Use harnesslib.identity.unit_is_current."""
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
                # capability_mode.json is the analyzer's run-metadata sidecar,
                # not an analysis output — feeding it to the spice/emc/thermal
                # consumers produces garbage units that collide with those
                # analyzers' own sidecars (TH-050).
                if json_file.name == "capability_mode.json":
                    continue
                outputs.append(json_file)
    return outputs


def retire_orphaned_outputs(out_dir, repo_list, expected):
    """Quarantine (rename to .stale) every downstream output in the run's scope whose upstream
    no longer exists. A chained runner walks its upstream outputs and never submits a unit
    whose schematic/PCB output is missing or quarantined, so without this the old downstream
    output stayed live for run_checks. `expected` maps repo -> output names that have a
    current upstream; `repo_list` None means every repo under out_dir. Returns the retired
    paths."""
    out_dir = Path(out_dir)
    if repo_list is None:
        repo_list = sorted(f"{o.name}/{r.name}" for o in out_dir.iterdir() if o.is_dir()
                           for r in o.iterdir() if r.is_dir()) if out_dir.is_dir() else []
    retired = []
    for repo in repo_list:
        keep = expected.get(repo, set())
        for f in sorted((out_dir / repo).glob("*.json")):
            if (f.name.startswith("_") or f.name == "capability_mode.json"
                    or f.name.endswith(".parasitics.json") or f.name in keep):
                continue
            os.replace(f, f.with_name(f.name + ".stale"))
            retired.append(f)
    return retired


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
    # a hash-truncated name lost its suffix: pair through the repo's manifest instead
    return _pcb_output_by_manifest(repo_name, stem, pcb_dir)


def _pcb_output_by_manifest(repo_name, sch_output_name, pcb_dir):
    """The PCB output paired with a schematic output whose name was hash-truncated
    (TH-013 cap): map the output name back to its input through the per-repo schematic
    manifest, swap the input's suffix for .kicad_pcb, and name that the runner's way."""
    manifest = MANIFESTS_DIR / repo_name / "schematics.txt"
    if not manifest.exists():
        return None
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or safe_name(line) + ".json" != sch_output_name:
            continue
        for suffix in (".kicad_sch", ".sch"):
            if line.endswith(suffix):
                pcb_path = pcb_dir / (safe_name(line[: -len(suffix)] + ".kicad_pcb") + ".json")
                if pcb_path.exists() and pcb_path.stat().st_size > 0:
                    return pcb_path
        return None
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


def iter_output_files(output_type, repos=None):
    """Yield (json_path, repo_name) for all output files of a given type.

    Args:
        output_type: One of 'schematic', 'pcb', 'emc', 'thermal', 'gerber', 'spice'.
        repos: Optional list of 'owner/repo' strings to filter. None = all.
    """
    type_dir = OUTPUTS_DIR / output_type
    if not type_dir.exists():
        return
    repo_set = set(repos) if repos else None
    for repo_name, repo_dir in iter_output_repos(type_dir, repo_filter=None):
        if repo_set and repo_name not in repo_set:
            continue
        for jf in sorted(repo_dir.glob("*.json")):
            if jf.name.startswith("_"):
                continue
            yield jf, repo_name


# ---------------------------------------------------------------------------
# Output validation
# ---------------------------------------------------------------------------

# Minimum required top-level keys per analyzer type (signature check)
EXPECTED_KEYS = {
    "schematic": {"components", "statistics", "findings"},
    "pcb": {"footprints", "statistics", "connectivity"},
    "gerber": {"layers", "summary"},
    "emc": {"findings", "summary"},
    "spice": {"simulation_results", "summary"},
    "thermal": {"findings", "summary"},
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

def _run_one(analyzer, file_path, outfile, errfile, extra_args=None, timeout=None,
             analyzer_type="schematic", env=None):
    """Run one analyzer subprocess through harnesslib.execution.run_once.

    Returns (returncode, outfile, elapsed_s, status, output_sha256). The output
    is written to a private temp path, validated, and published atomically; a
    stale previous output is quarantined as <outfile>.stale on any failure (B12).
    `timeout` is the per-file cap in seconds (default: standard profile)."""
    from harnesslib.execution import run_once, build_env
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
                            help="Skip units whose input and output match the recorded run identity")
        parser.add_argument("--online", action="store_true",
                            help="keep distributor credentials in the analyzer environment")
        parser.add_argument("--timeout", type=int, default=ANALYZER_TIMEOUT,
                            help=f"Per-file analyzer cap in seconds (default {ANALYZER_TIMEOUT})")
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

    repo_list, selection_source = resolve_repos_with_source(args, require_explicit_all=True)
    if repo_list is not None:
        filtered = []
        for rn in repo_list:
            filtered.extend(filter_manifest_by_repo(files, rn))
        files = filtered
        if not files:
            label = repo_list[0] if len(repo_list) == 1 else f"{len(repo_list)} repos"
            print(f"No {config['type_name']}s found for {label}", file=sys.stderr)
            sys.exit(1)

    # safe_name flattens "/" to "_": two inputs with one flat name would share an output
    # file and a unit id, the second silently overwriting the first
    by_name = defaultdict(list)
    for f in files:
        by_name[(repo_name_from_path(f), safe_name(f))].append(f)
    dups = {k: v for k, v in by_name.items() if len(v) > 1}
    if dups:
        print(f"Error: {len(dups)} output names collide after path flattening:", file=sys.stderr)
        for (repo, name), paths in sorted(dups.items()):
            print(f"  {repo}/{name}: {', '.join(sorted(paths))}", file=sys.stderr)
        sys.exit(2)

    type_name = config["type_name"]
    output_subdir = config["output_subdir"]
    summarize = config["summarize"]
    extra_args = config.get("extra_args")
    jobs = getattr(args, "jobs", 1)

    from harnesslib.execution import build_env, recorded_env
    from harnesslib.identity import (RunSpec, git_worktree_ref, write_manifest,
                                     finish_manifest, UnitLog, unit_is_current,
                                     sha256_path, input_digest)
    import platform, uuid
    env = build_env(offline=not getattr(args, "online", False))
    out_root = OUTPUTS_DIR / output_subdir
    out_root.mkdir(parents=True, exist_ok=True)

    def _uid(f):
        return f"{repo_name_from_path(f)}/{safe_name(f)}"

    unit_ids = sorted(_uid(f) for f in files)
    spec = RunSpec(kind="batch", profile="standard", harness=git_worktree_ref(HARNESS_DIR),
                   baseline=None, candidate=git_worktree_ref(kicad_happy),
                   argv=tuple(a for a in sys.argv[1:] if a != "--resume") + tuple(extra_args or ()),
                   selection_source=selection_source, unit_ids=tuple(unit_ids),
                   normalization_policy="volatile-leaves-v1", env=recorded_env(env))
    input_hashes = {f: sha256_path(f) for f in files}
    from harnesslib.identity import read_manifest, manifests_match, UNITS_NAME
    do_resume = getattr(args, "resume", False)
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
    skipped = 0

    def _format_result(i, relpath, returncode, outfile, status):
        if status in ("ok", "ok_findings_exit"):
            if do_validate:
                ok, msg = validate_output(outfile, output_subdir)
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

    cap = getattr(args, "timeout", ANALYZER_TIMEOUT)
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

    finish_manifest(out_root, {**dict(status_totals), "skipped": skipped})

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
    if failed:
        sys.exit(1)
