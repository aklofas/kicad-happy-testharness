"""Assertion data model and evaluation for analyzer outputs.

Assertions are machine-checkable facts about what an analyzer should
find in a specific file. They live in data/{repo}/{project}/assertions/{type}/
and are checked into git, providing permanent regression protection.

Assertion format:
{
    "file_pattern": "dcdc.kicad_sch",
    "analyzer_type": "schematic",
    "assertions": [...]
}

Supported operators:
    range, min_count, max_count, equals, exists, not_exists,
    greater_than, less_than, field_equals, contains_match
"""

import fnmatch
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import resolve_path, load_project_metadata


def _countable(val):
    if val is None:
        return 0
    if isinstance(val, (list, dict)):
        return len(val)
    if isinstance(val, (int, float)):
        return int(val)
    return 0


def evaluate_assertion(assertion, data):
    """Evaluate a single assertion against analyzer output."""
    check = assertion.get("check", {})
    path = check.get("path", "")
    op = check.get("op", "")
    desc = assertion.get("description", "")
    aid = assertion.get("id", "?")

    result = {"id": aid, "description": desc, "passed": False}
    val = resolve_path(data, path)

    if op == "range":
        count = _countable(val)
        lo, hi = check.get("min", 0), check.get("max", float("inf"))
        result["passed"] = lo <= count <= hi
        result["actual"] = count
        result["expected"] = f"{lo}-{hi}"
    elif op == "min_count":
        count = _countable(val)
        threshold = check.get("value", 0)
        result["passed"] = count >= threshold
        result["actual"] = count
        result["expected"] = f">= {threshold}"
    elif op == "max_count":
        count = _countable(val)
        threshold = check.get("value", 0)
        result["passed"] = count <= threshold
        result["actual"] = count
        result["expected"] = f"<= {threshold}"
    elif op == "equals":
        expected = check.get("value")
        result["passed"] = val == expected
        result["actual"] = val
        result["expected"] = expected
    elif op == "exists":
        result["passed"] = val is not None and val != [] and val != {} and val != ""
        result["actual"] = "present" if result["passed"] else "missing"
        result["expected"] = "present"
    elif op == "not_exists":
        result["passed"] = val is None
        result["actual"] = "missing" if val is None else "present"
        result["expected"] = "missing"
    elif op == "greater_than":
        count = _countable(val)
        threshold = check.get("value", 0)
        result["passed"] = count > threshold
        result["actual"] = count
        result["expected"] = f"> {threshold}"
    elif op == "less_than":
        count = _countable(val)
        threshold = check.get("value", 0)
        result["passed"] = count < threshold
        result["actual"] = count
        result["expected"] = f"< {threshold}"
    elif op == "field_equals":
        if not isinstance(val, list):
            result["actual"] = "not a list"
            result["expected"] = check.get("assert_value")
            return result
        match_field = check.get("match_field", "")
        match_value = check.get("match_value", "")
        assert_field = check.get("assert_field", "")
        assert_value = check.get("assert_value", "")
        found = False
        for item in val:
            if isinstance(item, dict) and item.get(match_field) == match_value:
                actual = item.get(assert_field)
                result["actual"] = actual
                result["expected"] = assert_value
                result["passed"] = actual == assert_value
                found = True
                break
        if not found:
            result["actual"] = f"{match_field}={match_value} not found"
            result["expected"] = assert_value
    elif op == "contains_match":
        if not isinstance(val, list):
            result["actual"] = "not a list"
            return result
        field = check.get("field", "")
        pattern = check.get("pattern", "")
        for item in val:
            if isinstance(item, dict):
                field_val = str(item.get(field, ""))
                if re.search(pattern, field_val, re.IGNORECASE):
                    result["passed"] = True
                    result["actual"] = field_val
                    result["expected"] = f"match for /{pattern}/"
                    return result
        result["actual"] = f"no match in {len(val)} items"
        result["expected"] = f"match for /{pattern}/"
    else:
        result["actual"] = f"unknown op: {op}"

    return result


def load_assertions(data_dir, analyzer_type=None, file_pattern=None, repo_name=None):
    """Load assertion files from data/{repo}/{project}/assertions/{type}/.

    Args:
        data_dir: Path to the data/ directory
        analyzer_type: Filter to one type (schematic, pcb, gerber)
        file_pattern: Filter by file_pattern glob
        repo_name: Filter to one repo

    Returns list of assertion set dicts, each with extra 'repo', 'project',
    'project_path' keys for mapping back to outputs.
    """
    if not data_dir.exists():
        return []

    all_assertions = []

    # Walk data/{repo}/{project}/assertions/{type}/*.json
    repo_dirs = []
    if repo_name:
        rd = data_dir / repo_name
        if rd.exists() and rd.is_dir():
            repo_dirs.append(rd)
    else:
        for d in sorted(data_dir.iterdir()):
            if d.is_dir() and not d.name.startswith("."):
                repo_dirs.append(d)

    for repo_dir in repo_dirs:
        for proj_dir in sorted(repo_dir.iterdir()):
            if not proj_dir.is_dir():
                continue
            assertions_dir = proj_dir / "assertions"
            if not assertions_dir.exists():
                continue

            # Resolve project_path for output file mapping.
            # Try baselines metadata first, then discover from repo.
            project_path = load_project_metadata(
                repo_dir.name, proj_dir.name).get("project_path")
            if project_path is None:
                # Fallback: look up from discover_projects if repo is checked out
                try:
                    from utils import discover_projects
                    for p in discover_projects(repo_dir.name):
                        if p["name"] == proj_dir.name:
                            project_path = p["path"]
                            break
                except Exception:
                    pass

            type_dirs = []
            if analyzer_type:
                td = assertions_dir / analyzer_type
                if td.exists() and td.is_dir():
                    type_dirs.append(td)
            else:
                for d in sorted(assertions_dir.iterdir()):
                    if d.is_dir():
                        type_dirs.append(d)

            for type_dir in type_dirs:
                for f in sorted(type_dir.glob("*.json")):
                    try:
                        data = json.loads(f.read_text())
                        if file_pattern:
                            fp = data.get("file_pattern", "")
                            if not fnmatch.fnmatch(fp, file_pattern):
                                continue
                        # Annotate with location info for output mapping
                        data["_repo"] = repo_dir.name
                        data["_project"] = proj_dir.name
                        data["_project_path"] = project_path
                        all_assertions.append(data)
                    except Exception:
                        continue

    return all_assertions
