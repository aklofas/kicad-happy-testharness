"""Assertion data model and evaluation for analyzer outputs.

Assertions are machine-checkable facts about what an analyzer should
find in a specific file. They live in data/assertions/ and are checked
into git, providing permanent regression protection.

Assertion format:
{
    "file_pattern": "hackrf_hardware_..._hackrf_one.kicad_sch",
    "analyzer_type": "schematic",
    "assertions": [
        {
            "id": "AST-0001",
            "description": "Should have 40-55 components",
            "check": {
                "path": "statistics.total_components",
                "op": "range",
                "min": 40,
                "max": 55
            }
        }
    ]
}

Supported operators:
    range         - value in [min, max]
    min_count     - list/int >= value
    max_count     - list/int <= value
    equals        - value == expected
    exists        - key exists and is non-empty
    not_exists    - key does not exist
    greater_than  - value > threshold
    less_than     - value < threshold
    field_equals  - find item in list by match_field, assert field value
    contains_match - list contains item where field matches pattern
"""

import fnmatch
import json
import re
from pathlib import Path


def resolve_path(data, path):
    """Navigate a dotted path through nested dicts."""
    parts = path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _countable(val):
    """Get a countable value — len for list/dict, int for numbers."""
    if val is None:
        return 0
    if isinstance(val, (list, dict)):
        return len(val)
    if isinstance(val, (int, float)):
        return int(val)
    return 0


def evaluate_assertion(assertion, data):
    """Evaluate a single assertion against analyzer output.

    Returns: {"id", "passed", "description", "actual", "expected", "detail"}
    """
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
        # Find item in list by match_field, then check assert_field
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
        # List contains item where field matches regex
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


def load_assertions(assertions_dir, analyzer_type=None, file_pattern=None):
    """Load assertion files, optionally filtered."""
    if not assertions_dir.exists():
        return []

    all_assertions = []

    # Walk type subdirectories
    dirs_to_scan = []
    if analyzer_type:
        type_dir = assertions_dir / analyzer_type
        if type_dir.exists():
            dirs_to_scan.append(type_dir)
    else:
        for d in assertions_dir.iterdir():
            if d.is_dir():
                dirs_to_scan.append(d)

    for d in dirs_to_scan:
        for f in sorted(d.glob("*.json")):
            try:
                data = json.loads(f.read_text())
                if file_pattern:
                    fp = data.get("file_pattern", "")
                    if not fnmatch.fnmatch(fp, file_pattern):
                        continue
                all_assertions.append(data)
            except Exception:
                continue

    return all_assertions
