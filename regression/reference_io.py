"""Output lookup, project-path resolution and per-set output loading.

Single owner of how an assertion set is mapped to its analyzer output file.
"""

import fnmatch
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import OUTPUTS_DIR, project_prefix, discover_projects, load_project_metadata


OUTPUT_NOT_FOUND = "output file not found"


def find_output_file(file_pattern, repo_name, project_path, analyzer_type):
    """Find the output JSON file for an assertion.

    Reconstructs the output safe_name from project_path + file_pattern.
    For root-level projects (project_path is "." or None), no prefix is added.
    """
    type_dir = OUTPUTS_DIR / analyzer_type / repo_name
    if not type_dir.exists():
        return None

    # Build prefix from project_path (not project_name)
    prefix = project_prefix(project_path)

    safe_name = prefix + file_pattern

    # Try exact match first
    candidate = type_dir / (safe_name + ".json")
    if candidate.exists():
        return candidate

    # Try with .json already in pattern
    candidate = type_dir / safe_name
    if candidate.exists():
        return candidate

    # Fallback: glob match
    for json_file in type_dir.glob("*.json"):
        if fnmatch.fnmatch(json_file.name, safe_name + ".json"):
            return json_file
        if fnmatch.fnmatch(json_file.stem, safe_name):
            return json_file

    return None


def resolve_project_path(repo_name, project_name):
    """Project path for output lookup: baselines metadata, then discovery."""
    pp = load_project_metadata(repo_name, project_name).get("project_path")
    if pp is not None:
        return pp
    try:
        for p in discover_projects(repo_name):
            if p["name"] == project_name:
                return p["path"]
    except (ImportError, OSError):
        pass
    return None


def load_set_output(aset):
    """Load the analyzer output for an assertion set.

    Returns (data, None), (None, OUTPUT_NOT_FOUND) or
    (None, "JSON parse error: <e>").
    """
    output_file = find_output_file(
        aset.get("file_pattern", ""), aset.get("_repo", ""),
        aset.get("_project_path"), aset.get("analyzer_type", "schematic"))
    if not output_file:
        return None, OUTPUT_NOT_FOUND
    try:
        return json.loads(output_file.read_text(encoding="utf-8")), None
    except Exception as e:
        return None, f"JSON parse error: {e}"


def write_assertion_file(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
