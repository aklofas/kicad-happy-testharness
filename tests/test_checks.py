"""Unit tests for regression/checks.py — assertion evaluation engine."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from checks import evaluate_assertion, _countable, _item_field, _field_strings


def _eval(op, path, data, **check_kwargs):
    """Helper: build assertion dict and evaluate."""
    assertion = {
        "id": "TEST-1",
        "description": f"test {op}",
        "check": {"path": path, "op": op, **check_kwargs},
    }
    return evaluate_assertion(assertion, data)


# === _countable ===

def test_countable():
    assert _countable(None) == 0
    assert _countable(42) == 42
    assert _countable(3.7) == 3
    assert _countable([1, 2, 3]) == 3
    assert _countable({"a": 1}) == 1
    assert _countable("hello") == 0
    assert _countable([]) == 0
    assert _countable({}) == 0


# === _item_field ===

def test_item_field():
    assert _item_field({"a": 1}, "a") == 1
    assert _item_field({"a": {"b": 2}}, "a.b") == 2
    assert _item_field({"a": 1}, "missing") == ""
    assert _item_field("not a dict", "a") == ""
    assert _item_field({}, "a") == ""


# === _field_strings ===

def test_field_strings_scalar():
    assert _field_strings("R5") == ["R5"]
    assert _field_strings(42) == ["42"]
    assert _field_strings("") == [""]

def test_field_strings_list():
    assert _field_strings(["R5", "C3"]) == ["R5", "C3"]
    assert _field_strings([1, 2]) == ["1", "2"]

def test_field_strings_empty_list():
    # Empty list yields no iterations — the outer operator treats the item
    # as non-matching. This is the intended behavior post-TH-031.
    assert _field_strings([]) == []


# === range ===

def test_range_pass():
    r = _eval("range", "count", {"count": 10}, min=8, max=12)
    assert r["passed"]
    assert r["actual"] == 10

def test_range_fail_low():
    r = _eval("range", "count", {"count": 5}, min=8, max=12)
    assert not r["passed"]

def test_range_fail_high():
    r = _eval("range", "count", {"count": 15}, min=8, max=12)
    assert not r["passed"]

def test_range_missing_key():
    r = _eval("range", "missing", {}, min=0, max=10)
    assert r["passed"]  # _countable(None)=0, 0 in [0,10]

def test_range_list_counts_length():
    r = _eval("range", "items", {"items": [1, 2, 3]}, min=2, max=5)
    assert r["passed"]
    assert r["actual"] == 3


# === min_count / max_count ===

def test_min_count_pass():
    r = _eval("min_count", "n", {"n": 10}, value=5)
    assert r["passed"]

def test_min_count_fail():
    r = _eval("min_count", "n", {"n": 3}, value=5)
    assert not r["passed"]

def test_max_count_pass():
    r = _eval("max_count", "n", {"n": 3}, value=5)
    assert r["passed"]

def test_max_count_fail():
    r = _eval("max_count", "n", {"n": 10}, value=5)
    assert not r["passed"]

def test_min_count_non_numeric_threshold():
    r = _eval("min_count", "n", {"n": 10}, value="bad")
    assert not r["passed"]


# === equals ===

def test_equals_int():
    r = _eval("equals", "x", {"x": 42}, value=42)
    assert r["passed"]

def test_equals_string():
    r = _eval("equals", "s", {"s": "hello"}, value="hello")
    assert r["passed"]

def test_equals_list_counts_length():
    r = _eval("equals", "items", {"items": [1, 2, 3]}, value=3)
    assert r["passed"]
    assert r["actual"] == 3

def test_equals_mismatch():
    r = _eval("equals", "x", {"x": 42}, value=43)
    assert not r["passed"]


# === exists / not_exists ===

def test_exists_present():
    r = _eval("exists", "x", {"x": 42})
    assert r["passed"]

def test_exists_none():
    r = _eval("exists", "missing", {})
    assert not r["passed"]

def test_exists_empty_list():
    r = _eval("exists", "x", {"x": []})
    assert not r["passed"]

def test_exists_empty_dict():
    r = _eval("exists", "x", {"x": {}})
    assert not r["passed"]

def test_exists_empty_string():
    r = _eval("exists", "x", {"x": ""})
    assert not r["passed"]

def test_not_exists_missing():
    r = _eval("not_exists", "missing", {})
    assert r["passed"]

def test_not_exists_empty_list():
    r = _eval("not_exists", "x", {"x": []})
    assert r["passed"]

def test_not_exists_empty_dict():
    r = _eval("not_exists", "x", {"x": {}})
    assert r["passed"]

def test_not_exists_empty_string():
    r = _eval("not_exists", "x", {"x": ""})
    assert r["passed"]

def test_not_exists_present():
    r = _eval("not_exists", "x", {"x": 42})
    assert not r["passed"]


# === greater_than / less_than ===

def test_greater_than():
    r = _eval("greater_than", "x", {"x": 10}, value=5)
    assert r["passed"]

def test_greater_than_equal():
    r = _eval("greater_than", "x", {"x": 5}, value=5)
    assert not r["passed"]

def test_less_than():
    r = _eval("less_than", "x", {"x": 3}, value=5)
    assert r["passed"]


# === field_equals ===

def test_field_equals_found():
    data = {"items": [{"ref": "R1", "value": "10k"}, {"ref": "R2", "value": "4.7k"}]}
    r = _eval("field_equals", "items", data,
              match_field="ref", match_value="R1",
              assert_field="value", assert_value="10k")
    assert r["passed"]

def test_field_equals_not_found():
    data = {"items": [{"ref": "R1", "value": "10k"}]}
    r = _eval("field_equals", "items", data,
              match_field="ref", match_value="R99",
              assert_field="value", assert_value="10k")
    assert not r["passed"]

def test_field_equals_not_list():
    r = _eval("field_equals", "x", {"x": "not a list"},
              match_field="ref", match_value="R1",
              assert_field="value", assert_value="10k")
    assert not r["passed"]


# === contains_match / not_contains_match ===

def test_contains_match():
    data = {"sims": [
        {"type": "rc_filter", "components": ["R1", "C1"]},
        {"type": "opamp", "components": ["U1"]},
    ]}
    r = _eval("contains_match", "sims", data, field="type", pattern="^rc_filter$")
    assert r["passed"]

def test_contains_match_no_match():
    data = {"sims": [{"type": "opamp"}]}
    r = _eval("contains_match", "sims", data, field="type", pattern="^rc_filter$")
    assert not r["passed"]

def test_contains_match_not_list():
    r = _eval("contains_match", "x", {"x": "string"}, field="type", pattern=".*")
    assert not r["passed"]

def test_not_contains_match():
    data = {"sims": [{"type": "opamp"}]}
    r = _eval("not_contains_match", "sims", data, field="type", pattern="^rc_filter$")
    assert r["passed"]

def test_not_contains_match_found():
    data = {"sims": [{"type": "rc_filter"}]}
    r = _eval("not_contains_match", "sims", data, field="type", pattern="^rc_filter$")
    assert not r["passed"]


# === count_matches ===

def test_count_matches():
    data = {"sims": [
        {"type": "rc_filter"}, {"type": "rc_filter"}, {"type": "opamp"},
    ]}
    r = _eval("count_matches", "sims", data, field="type", pattern="^rc_filter$", value=2)
    assert r["passed"]
    assert r["actual"] == 2

def test_count_matches_zero():
    data = {"sims": [{"type": "opamp"}]}
    r = _eval("count_matches", "sims", data, field="type", pattern="^rc_filter$", value=0)
    assert r["passed"]

def test_count_matches_not_list():
    r = _eval("count_matches", "x", {"x": "string"}, field="type", pattern=".*", value=0)
    assert r["passed"]
    assert r["actual"] == 0


# === list-field matching (TH-031) ===
# These operators must iterate list-typed field values and regex-match each
# string element, without relying on Python's str([...]) list repr. See
# TH-031 in FIXED.md for rationale.

def test_contains_match_list_field_hit():
    """contains_match finds a ref inside a list-typed field."""
    data = {"findings": [
        {"rule_id": "IO-001", "components": ["J1", "U3"]},
        {"rule_id": "DC-001", "components": ["C1"]},
    ]}
    r = _eval("contains_match", "findings", data,
              field="components", pattern=r"^U3$")
    assert r["passed"], f"Expected match, got {r}"

def test_contains_match_list_field_miss():
    """contains_match returns False when no list element matches."""
    data = {"findings": [
        {"rule_id": "IO-001", "components": ["J1", "U3"]},
    ]}
    r = _eval("contains_match", "findings", data,
              field="components", pattern=r"^R99$")
    assert not r["passed"]

def test_contains_match_list_field_no_repr_leak():
    """Regex must match list elements, not the Python list repr.

    Before TH-031 fix, a pattern like `['U3'` would accidentally match
    because str(['U3', 'J1']) == "['U3', 'J1']". After the fix it must
    not match because no element equals that string.
    """
    data = {"findings": [
        {"rule_id": "IO-001", "components": ["U3", "J1"]},
    ]}
    r = _eval("contains_match", "findings", data,
              field="components", pattern=r"\[")
    assert not r["passed"], "Should not match list-repr characters"

def test_not_contains_match_list_field():
    """not_contains_match passes when no list element matches."""
    data = {"findings": [
        {"rule_id": "IO-001", "components": ["J1", "U3"]},
    ]}
    r = _eval("not_contains_match", "findings", data,
              field="components", pattern=r"^R99$")
    assert r["passed"]

def test_not_contains_match_list_field_hit():
    """not_contains_match fails when a list element matches."""
    data = {"findings": [
        {"rule_id": "IO-001", "components": ["J1", "U3"]},
    ]}
    r = _eval("not_contains_match", "findings", data,
              field="components", pattern=r"^U3$")
    assert not r["passed"], f"Expected no match to pass, got {r}"

def test_count_matches_list_field():
    """count_matches counts items whose list field contains any matching element."""
    data = {"findings": [
        {"rule_id": "IO-001", "components": ["J1", "U3"]},
        {"rule_id": "DC-001", "components": ["U3"]},
        {"rule_id": "GP-002", "components": ["C1"]},
    ]}
    r = _eval("count_matches", "findings", data,
              field="components", pattern=r"^U3$", value=2)
    assert r["passed"], f"Expected count=2, got {r}"
    assert r["actual"] == 2


# === dotted path resolution ===

def test_nested_path():
    data = {"summary": {"pass": 10, "fail": 0}}
    r = _eval("equals", "summary.pass", data, value=10)
    assert r["passed"]

def test_deeply_nested():
    data = {"a": {"b": {"c": 42}}}
    r = _eval("equals", "a.b.c", data, value=42)
    assert r["passed"]


# === unknown operator ===

def test_unknown_op():
    r = _eval("bogus_op", "x", {"x": 1})
    assert not r["passed"]
    assert "unknown op" in r.get("actual", "")


# === Runner ===

if __name__ == "__main__":
    import inspect
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
