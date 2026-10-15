import json

from regression.field_compare import (
    Delta, OPS, Policy, compare_strict, escape_token, join_pointer, resolve_pointer,
    split_pointer,
)

U = dict(unit="schematic/o/r/k", analyzer="schematic")


def _paths(deltas, op=None):
    return sorted(d.path for d in deltas if op is None or d.op == op)


def json_copy(o):
    return json.loads(json.dumps(o))


def test_pointer_helpers_follow_rfc6901():
    assert escape_token("a/b~c") == "a~1b~0c"
    assert join_pointer("", "findings") == "/findings"
    assert join_pointer("/findings", 0) == "/findings/0"
    doc = {"a~b": {"x/y": [10, 20]}}
    assert resolve_pointer(doc, "/a~0b/x~1y/1") == (True, 20)
    assert resolve_pointer(doc, "/a~0b/missing") == (False, None)
    assert resolve_pointer(doc, "") == (True, doc)


def test_pointer_escape_round_trips():
    for key in ["a/b~c", "~1", "~0/", "plain", "//"]:
        assert split_pointer(join_pointer("", key)) == [key]


def test_identical_docs_have_no_deltas():
    doc = {"a": 1, "b": [1, {"c": None}], "d": {"e": "x"}}
    deltas, violations = compare_strict(doc, json_copy(doc), None, **U)
    assert deltas == [] and violations == []


def test_empty_policy_accepted():
    deltas, violations = compare_strict({"a": 1}, {"a": 1}, Policy(name="x"), **U)
    assert deltas == [] and violations == []


def test_changed_scalar():
    deltas, _ = compare_strict({"a": 1}, {"a": 2}, None, **U)
    assert deltas == [Delta(path="/a", op="changed", before=1, after=2, **U)]


def test_delta_frozen_and_hashable():
    d = Delta(path="/a", op="changed", before=1, after=2, **U)
    assert hash(d) == hash(Delta(path="/a", op="changed", before=1, after=2, **U))
    try:
        d.path = "/b"
    except Exception:
        pass
    else:
        raise AssertionError("Delta must be frozen")


def test_absent_vs_null_is_removed():
    deltas, _ = compare_strict({"a": None}, {}, None, **U)
    assert [(d.op, d.path, d.before, d.after) for d in deltas] == [("removed", "/a", None, None)]
    deltas, _ = compare_strict({}, {"a": None}, None, **U)
    assert [(d.op, d.path) for d in deltas] == [("added", "/a")]


def test_null_vs_value_is_type_changed():
    deltas, _ = compare_strict({"a": None}, {"a": 0}, None, **U)
    assert [(d.op, d.path) for d in deltas] == [("type_changed", "/a")]


def test_removed_subtree_is_one_delta_with_whole_value():
    deltas, _ = compare_strict({"f": {"aliases": ["12V", "X"]}}, {"f": {}}, None, **U)
    assert len(deltas) == 1
    assert deltas[0].op == "removed" and deltas[0].path == "/f/aliases"
    assert deltas[0].before == ["12V", "X"] and deltas[0].after is None


def test_bool_vs_number_is_type_changed():
    deltas, _ = compare_strict({"a": True}, {"a": 1}, None, **U)
    assert [(d.op, d.path) for d in deltas] == [("type_changed", "/a")]


def test_int_vs_float_equal_value_is_equal_in_strict():
    deltas, _ = compare_strict({"a": 1}, {"a": 1.0}, None, **U)
    assert deltas == []


def test_container_type_change_is_single_delta():
    deltas, _ = compare_strict({"a": [1]}, {"a": {"0": 1}}, None, **U)
    assert [(d.op, d.path) for d in deltas] == [("type_changed", "/a")]


def test_list_order_is_significant_and_tail_reported():
    deltas, _ = compare_strict({"l": [1, 2, 3]}, {"l": [2, 1]}, None, **U)
    assert _paths(deltas, "changed") == ["/l/0", "/l/1"]
    assert _paths(deltas, "removed") == ["/l/2"]
    deltas, _ = compare_strict({"l": [1]}, {"l": [1, 9]}, None, **U)
    assert _paths(deltas, "added") == ["/l/1"]


def test_deep_recursion_into_lists_of_dicts():
    a = {"findings": [{"id": 1, "pins": [{"n": "A"}]}, {"id": 2}]}
    b = {"findings": [{"id": 1, "pins": [{"n": "B"}]}, {"id": 2, "x": 1}]}
    deltas, _ = compare_strict(a, b, None, **U)
    assert [(d.op, d.path) for d in deltas] == [
        ("changed", "/findings/0/pins/0/n"), ("added", "/findings/1/x")]


def test_nested_pointer_paths_are_escaped():
    deltas, _ = compare_strict({"a/b": {"c~d": 1}}, {"a/b": {"c~d": 2}}, None, **U)
    assert deltas[0].path == "/a~1b/c~0d"


def test_key_order_opt_in():
    a = {"x": 1, "y": 2}
    b = {"y": 2, "x": 1}
    deltas, _ = compare_strict(a, b, None, **U)
    assert deltas == []
    deltas, _ = compare_strict(a, b, None, key_order=True, **U)
    assert [(d.op, d.path, d.before, d.after) for d in deltas] == [
        ("key_order", "", ["x", "y"], ["y", "x"])]


def test_ops_vocabulary_is_closed():
    assert OPS == ("added", "removed", "changed", "type_changed", "key_order", "bytes", "lexical_numeric")


def test_nan_equal_to_nan_but_not_to_number():
    doc = json_copy({"x": float("nan")})
    assert compare_strict(doc, json_copy(doc), None, **U)[0] == []
    deltas, _ = compare_strict({"x": float("nan")}, {"x": 1.0}, None, **U)
    assert [(d.op, d.path) for d in deltas] == [("changed", "/x")]


def test_list_tail_honours_masked():
    from regression.field_compare import _Ctx, _walk
    ctx = _Ctx("u", "schematic", False)
    ctx.masked.add("/l/1")
    ctx.masked.add("/m/1")
    _walk({"l": [1, 2, 3], "m": [1]}, {"l": [1], "m": [1, 9]}, "", ctx)
    assert [d.path for d in ctx.deltas] == ["/l/2"]


def test_resolve_pointer_rejects_nonconforming_indices():
    doc = {"list": [1, 2]}
    assert resolve_pointer(doc, "/list/01") == (False, None)
    assert resolve_pointer(doc, "/list/²") == (False, None)
    assert resolve_pointer(doc, "/list/0") == (True, 1)


def test_key_order_nested_and_equal_order():
    a = {"o": {"x": 1, "y": 2}}
    b = {"o": {"y": 2, "x": 1}}
    deltas, _ = compare_strict(a, b, None, key_order=True, **U)
    assert [(d.op, d.path) for d in deltas] == [("key_order", "/o")]
    assert compare_strict(a, json_copy(a), None, key_order=True, **U)[0] == []
