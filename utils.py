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
from pathlib import Path

from harnesslib import batch as _batch
from harnesslib import corpus as _corpus
from harnesslib.batch import EXPECTED_KEYS, _print_detector_aggregate, _run_one  # noqa: F401
from harnesslib.corpus import (  # noqa: F401
    NAME_MAX_BYTES, _NAME_HASH_LEN, _truncate_with_hash, filter_manifest_by_repo,
    project_key, project_prefix,
)
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

# Default parallelism — use all available CPUs for max throughput
DEFAULT_JOBS = os.cpu_count() or 4

CROSS_SECTIONS_FILE = DATA_DIR / "cross_sections.json"


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
    return _corpus._path_relative_to_repos(path, REPOS_DIR)


def repo_name_from_path(path):
    """Extract repo name (owner/repo under repos/).

    Given an absolute or relative path like repos/owner/OpenMower/Hardware/...,
    returns 'owner/OpenMower'.
    """
    return _corpus.repo_name_from_path(path, REPOS_DIR)


def within_repo_path(path):
    """Get the path within a repo (everything after the owner/repo).

    Given repos/owner/OpenMower/Hardware/board.kicad_sch,
    returns 'Hardware/board.kicad_sch'.
    """
    return _corpus.within_repo_path(path, REPOS_DIR)


def safe_name(path):
    """Create a flat safe filename from a within-repo path.

    Replaces path separators with underscores and applies the TH-013 length
    cap. Returned name is guaranteed ≤ NAME_MAX_BYTES.
    """
    return _corpus.safe_name(path, REPOS_DIR)


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
    whole-corpus switch required by mutating batch runs (TH-049).
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
    and is retained in the dict so name migration tools can
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
# Shared analyzer runner
# ---------------------------------------------------------------------------

def run_analyzer(config, args=None, argv=None):
    """Shared runner for all analyzer types: parse the CLI, resolve the selection, and run
    harnesslib.batch.run_batch with paths read from this module's globals at call time.

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

    batch_config = _batch.BatchConfig(
        type_name=config["type_name"], analyzer_script=config["analyzer_script"],
        manifest_file=config["manifest_file"], output_subdir=config["output_subdir"],
        summarize=config["summarize"], extra_args=tuple(config.get("extra_args") or ()))
    settings = _batch.BatchSettings(
        jobs=getattr(args, "jobs", 1), validate=getattr(args, "validate", False),
        json=getattr(args, "json", False), resume=getattr(args, "resume", False),
        online=getattr(args, "online", False), timeout=getattr(args, "timeout", ANALYZER_TIMEOUT))
    paths = _batch.BatchPaths(harness_dir=HARNESS_DIR, product_root=resolve_kicad_happy_dir(),
                              repos_dir=REPOS_DIR, outputs_dir=OUTPUTS_DIR,
                              manifests_dir=MANIFESTS_DIR)

    rc = _batch.preflight(batch_config, paths)
    if rc:
        sys.exit(rc)
    repo_list, selection_source = resolve_repos_with_source(args, require_explicit_all=True)
    rc = _batch.run_batch(batch_config, settings, paths, repo_list=repo_list,
                          selection_source=selection_source,
                          argv=tuple(sys.argv[1:] if argv is None else argv))
    if rc:
        sys.exit(rc)
