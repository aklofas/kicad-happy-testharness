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
    greater_than, less_than, field_equals, contains_match,
    not_contains_match, count_matches
"""

import fnmatch
import functools
import json
import re
import sys
from pathlib import Path


@functools.lru_cache(maxsize=256)
def _compile(pattern):
    """Compile and cache a regex pattern (case-insensitive)."""
    return re.compile(pattern, re.IGNORECASE)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import resolve_path, load_project_metadata

# All supported assertion operators — validated at load time
KNOWN_OPS = frozenset({
    "range", "min_count", "max_count", "equals", "exists", "not_exists",
    "greater_than", "less_than", "field_equals", "contains_match",
    "not_contains_match", "count_matches",
})


def validate_assertion_structure(assertion, source_file=None):
    """Validate assertion structure at load time. Returns list of warning strings."""
    warnings = []
    prefix = f"{source_file}: " if source_file else ""

    if not isinstance(assertion, dict):
        warnings.append(f"{prefix}assertion is not a dict")
        return warnings

    aid = assertion.get("id", "?")

    if "id" not in assertion:
        warnings.append(f"{prefix}assertion missing 'id'")
    if "description" not in assertion:
        warnings.append(f"{prefix}[{aid}] missing 'description'")

    check = assertion.get("check")
    if not isinstance(check, dict):
        warnings.append(f"{prefix}[{aid}] missing or invalid 'check'")
        return warnings

    if "path" not in check:
        warnings.append(f"{prefix}[{aid}] check missing 'path'")
    if "op" not in check:
        warnings.append(f"{prefix}[{aid}] check missing 'op'")
    elif check["op"] not in KNOWN_OPS:
        warnings.append(f"{prefix}[{aid}] unknown operator '{check['op']}'")

    return warnings


def _item_field(item, field):
    """Get a field value from a dict, supporting dotted paths (e.g., 'r_top.ref')."""
    if not isinstance(item, dict):
        return ""
    parts = field.split(".")
    val = item
    for part in parts:
        if isinstance(val, dict):
            val = val.get(part, "")
        else:
            return ""
    return val


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

    # detector_filter: pre-filter findings[] by detector name before evaluation
    detector_filter = check.get("detector_filter")
    if detector_filter and isinstance(val, list):
        val = [item for item in val
               if isinstance(item, dict) and item.get("detector") == detector_filter]

    if op == "range":
        count = _countable(val)
        lo, hi = check.get("min", 0), check.get("max", float("inf"))
        result["passed"] = lo <= count <= hi
        result["actual"] = count
        result["expected"] = f"{lo}-{hi}"
    elif op == "min_count":
        count = _countable(val)
        threshold = check.get("value", 0)
        if not isinstance(threshold, (int, float)):
            result["passed"] = False
            result["actual"] = count
            result["expected"] = threshold
        else:
            result["passed"] = count >= threshold
            result["actual"] = count
            result["expected"] = f">= {threshold}"
    elif op == "max_count":
        count = _countable(val)
        threshold = check.get("value", 0)
        if not isinstance(threshold, (int, float)):
            result["passed"] = False
            result["actual"] = count
            result["expected"] = threshold
        else:
            result["passed"] = count <= threshold
            result["actual"] = count
            result["expected"] = f"<= {threshold}"
    elif op == "equals":
        expected = check.get("value")
        # When comparing a list/dict to a number, compare count
        if isinstance(val, (list, dict)) and isinstance(expected, (int, float)):
            actual = len(val)
            result["passed"] = actual == expected
            result["actual"] = actual
        else:
            result["passed"] = val == expected
            result["actual"] = val
        result["expected"] = expected
    elif op == "exists":
        result["passed"] = val is not None and val != [] and val != {} and val != ""
        result["actual"] = "present" if result["passed"] else "missing"
        result["expected"] = "present"
    elif op == "not_exists":
        result["passed"] = val is None or val == [] or val == {} or val == ""
        result["actual"] = "missing" if result["passed"] else "present"
        result["expected"] = "missing"
    elif op == "greater_than":
        count = _countable(val)
        threshold = check.get("value", 0)
        if not isinstance(threshold, (int, float)):
            result["passed"] = False
            result["actual"] = count
            result["expected"] = threshold
        else:
            result["passed"] = count > threshold
            result["actual"] = count
            result["expected"] = f"> {threshold}"
    elif op == "less_than":
        count = _countable(val)
        threshold = check.get("value", 0)
        if not isinstance(threshold, (int, float)):
            result["passed"] = False
            result["actual"] = count
            result["expected"] = threshold
        else:
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
                field_val = str(_item_field(item, field))
                if _compile(pattern).search(field_val):
                    result["passed"] = True
                    result["actual"] = field_val
                    result["expected"] = f"match for /{pattern}/"
                    return result
        result["actual"] = f"no match in {len(val)} items"
        result["expected"] = f"match for /{pattern}/"
    elif op == "not_contains_match":
        if not isinstance(val, list):
            result["passed"] = True
            result["actual"] = "not a list"
            return result
        field = check.get("field", "")
        pattern = check.get("pattern", "")
        for item in val:
            if isinstance(item, dict):
                field_val = str(_item_field(item, field))
                if _compile(pattern).search(field_val):
                    result["passed"] = False
                    result["actual"] = field_val
                    result["expected"] = f"no match for /{pattern}/"
                    return result
        result["passed"] = True
        result["actual"] = f"no match in {len(val)} items"
        result["expected"] = f"no match for /{pattern}/"
    elif op == "count_matches":
        if not isinstance(val, list):
            result["actual"] = 0
        else:
            field = check.get("field", "")
            pattern = check.get("pattern", ".*")
            pat = _compile(pattern)
            count = sum(1 for item in val if isinstance(item, dict)
                        and pat.search(str(_item_field(item, field))))
            result["actual"] = count
        expected = check.get("value", 0)
        result["passed"] = result["actual"] == expected
        result["expected"] = f"exactly {expected} matches"
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

    # Walk data/{owner}/{repo}/{project}/assertions/{type}/*.json
    repo_dirs = []
    if repo_name:
        rd = data_dir / repo_name
        if rd.exists() and rd.is_dir():
            repo_dirs.append(rd)
    else:
        for owner_dir in sorted(data_dir.iterdir()):
            if not owner_dir.is_dir() or owner_dir.name.startswith("."):
                continue
            for repo_dir in sorted(owner_dir.iterdir()):
                if repo_dir.is_dir() and not repo_dir.name.startswith("."):
                    repo_dirs.append(repo_dir)

    for repo_dir in repo_dirs:
        for proj_dir in sorted(repo_dir.iterdir()):
            if not proj_dir.is_dir():
                continue
            assertions_dir = proj_dir / "assertions"
            if not assertions_dir.exists():
                continue

            # Resolve project_path for output file mapping.
            # Try baselines metadata first, then discover from repo.
            repo_key = f"{repo_dir.parent.name}/{repo_dir.name}"
            project_path = load_project_metadata(
                repo_key, proj_dir.name).get("project_path")
            if project_path is None:
                # Fallback: look up from discover_projects if repo is checked out
                try:
                    from utils import discover_projects
                    for p in discover_projects(repo_key):
                        if p["name"] == proj_dir.name:
                            project_path = p["path"]
                            break
                except (ImportError, OSError):
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
                        data = json.loads(f.read_text(encoding="utf-8"))
                        if file_pattern:
                            fp = data.get("file_pattern", "")
                            if not fnmatch.fnmatch(fp, file_pattern):
                                continue
                        # Validate assertion structure at load time
                        for a in data.get("assertions", []):
                            warnings = validate_assertion_structure(a, str(f))
                            for w in warnings:
                                print(f"WARNING: {w}", file=sys.stderr)
                        # Annotate with location info for output mapping
                        data["_repo"] = repo_key
                        data["_project"] = proj_dir.name
                        data["_project_path"] = project_path
                        data["_source_file"] = str(f)
                        all_assertions.append(data)
                    except (json.JSONDecodeError, OSError):
                        continue

    return all_assertions
