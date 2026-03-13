"""Shared utilities for the kicad-happy test harness.

Provides path resolution, repo naming, project discovery, and constants
used across discover.py, analyzer runners, baselines, and validators.
"""

import os
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
REPOS_DIR = HARNESS_DIR / "repos"
DATA_DIR = HARNESS_DIR / "reference"
MANIFESTS_DIR = HARNESS_DIR / "results" / "manifests"
OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"
ANALYZER_TYPES = ["schematic", "pcb", "gerber"]


def repo_name_from_path(path):
    """Extract repo name (first component under repos/).

    Given an absolute or relative path like repos/OpenMower/Hardware/...,
    returns 'OpenMower'.
    """
    path = str(path)
    repos_str = str(REPOS_DIR)
    if path.startswith(repos_str):
        rel = path[len(repos_str):].lstrip(os.sep)
    else:
        idx = path.find("repos" + os.sep)
        if idx >= 0:
            rel = path[idx + len("repos") + 1:]
        else:
            rel = path
    parts = rel.replace("\\", "/").split("/")
    return parts[0] if parts and parts[0] else None


def within_repo_path(path):
    """Get the path within a repo (everything after the repo name).

    Given repos/OpenMower/Hardware/board.kicad_sch,
    returns 'Hardware/board.kicad_sch'.
    """
    path = str(path)
    repos_str = str(REPOS_DIR)
    if path.startswith(repos_str):
        rel = path[len(repos_str):].lstrip(os.sep)
    else:
        idx = path.find("repos" + os.sep)
        if idx >= 0:
            rel = path[idx + len("repos") + 1:]
        else:
            rel = path
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


def filter_manifest_by_repo(lines, repo_name):
    """Filter manifest lines to only those belonging to a given repo."""
    repos_str = str(REPOS_DIR)
    prefix = repos_str + os.sep + repo_name + os.sep
    return [l for l in lines if l.startswith(prefix)]


# ---------------------------------------------------------------------------
# Project discovery
# ---------------------------------------------------------------------------

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


def project_for_file(file_path, repo_name=None):
    """Determine which project a KiCad file belongs to.

    Returns {"name": str, "path": str} for the project, or None.
    Matches the file to the project whose directory is the closest ancestor.
    """
    if repo_name is None:
        repo_name = repo_name_from_path(file_path)
    if not repo_name:
        return None

    projects = discover_projects(repo_name)
    if not projects:
        return None

    wrp = within_repo_path(file_path).replace("\\", "/")
    file_dir = str(Path(wrp).parent) if "/" in wrp else "."

    # Find longest matching project path (closest ancestor)
    best = None
    for proj in projects:
        ppath = proj["path"]
        if ppath == ".":
            # Root project matches everything
            if best is None:
                best = proj
        elif file_dir == ppath or file_dir.startswith(ppath + "/"):
            if best is None or len(ppath) > len(best["path"]):
                best = proj

    return best


def safe_name_in_project(file_path, project_path):
    """Get the safe filename for a file relative to its project directory.

    Given file at Hardware/OpenMowerMainboard/dcdc.kicad_sch and
    project_path "Hardware/OpenMowerMainboard", returns "dcdc.kicad_sch".

    For files in subdirectories of the project, encodes with _:
    Given SubDir/sheet.kicad_sch in project "ProjectDir",
    returns "SubDir_sheet.kicad_sch".
    """
    wrp = within_repo_path(file_path).replace("\\", "/")
    if project_path and project_path != ".":
        prefix = project_path + "/"
        if wrp.startswith(prefix):
            within = wrp[len(prefix):]
        else:
            within = wrp
    else:
        within = wrp
    return within.replace("/", "_").replace(os.sep, "_")


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
