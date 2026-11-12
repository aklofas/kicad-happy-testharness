"""TH-109: check shapes that cannot fail, or that read the wrong finding.

A regex/count op without `pattern` compiled "" (matches anything) or ".*"; a `range` without
`min`/`max` read 0..inf; `findings[<n>]` with a `detector_filter` indexed the unfiltered list,
so it read the n-th finding of any detector (and the filter then emptied a nested list)."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from checks import assertion_errors, evaluate_assertion

import pytest


def _a(**check):
    return {"id": "FND-1-AST-01", "description": "d", "check": check}


@pytest.mark.parametrize("op", ["contains_match", "not_contains_match", "count_matches"])
def test_regex_op_without_pattern_is_a_load_error(op):
    errs = assertion_errors(_a(path="findings", op=op, value="/x/"))
    assert errs == [f"{op} without 'pattern' or 'where'"]


@pytest.mark.parametrize("op", ["contains_match", "not_contains_match", "count_matches"])
def test_regex_op_with_pattern_is_valid(op):
    assert assertion_errors(_a(path="findings", op=op, field="ref", pattern="^U1$", value=1)) == []


@pytest.mark.parametrize("op", ["contains_match", "not_contains_match", "count_matches"])
def test_regex_op_with_only_where_is_valid(op):
    """`where` carries the match; the field pattern defaults to match-any."""
    assert assertion_errors(_a(path="findings", op=op, where={"ref": "^U1$"}, value=1)) == []


@pytest.mark.parametrize("op", ["contains_match", "not_contains_match", "count_matches"])
def test_regex_op_with_empty_where_is_a_load_error(op):
    assert assertion_errors(_a(path="findings", op=op, where={}, value=1)) == [
        f"{op} without 'pattern' or 'where'"]


def test_where_only_check_can_fail():
    data = {"findings": [{"detector": "d", "ref": "U1", "topology": "LDO"}]}
    hit = evaluate_assertion(_a(path="findings", op="contains_match", detector_filter="d",
                                where={"ref": "^U1$", "topology": "^LDO$"}), data)
    miss = evaluate_assertion(_a(path="findings", op="contains_match", detector_filter="d",
                                 where={"ref": "^U1$", "topology": "^switching$"}), data)
    assert hit["passed"] and not miss["passed"]


def test_range_without_bounds_is_a_load_error():
    assert assertion_errors(_a(path="x", op="range", value=[1, 2])) == ["range without 'min' or 'max'"]


def test_range_with_one_bound_is_valid():
    assert assertion_errors(_a(path="x", op="range", min=1)) == []
    assert assertion_errors(_a(path="x", op="range", max=1)) == []


def test_shape_errors_apply_to_aspirational_locks_too():
    a = _a(path="findings", op="contains_match", value="/x/")
    a["aspirational"] = True
    assert assertion_errors(a)


_DATA = {"findings": [
    {"detector": "detect_rc_filters", "ref": "R1", "caps": []},
    {"detector": "detect_crystal_circuits", "ref": "Y1", "load_caps": [{"ref": "C1"}, {"ref": "C2"}]},
    {"detector": "detect_crystal_circuits", "ref": "Y2", "load_caps": []},
]}


def test_indexed_findings_path_reads_the_nth_finding_of_the_filtered_detector():
    r = evaluate_assertion(_a(path="findings[0].ref", op="equals", value="Y1",
                              detector_filter="detect_crystal_circuits"), _DATA)
    assert r["passed"] and r["actual"] == "Y1"
    r = evaluate_assertion(_a(path="findings[1].ref", op="equals", value="Y2",
                              detector_filter="detect_crystal_circuits"), _DATA)
    assert r["passed"]


def test_indexed_findings_path_does_not_filter_the_nested_list():
    """findings[0].load_caps used to be filtered by detector too: [] and max_count 0 passed."""
    r = evaluate_assertion(_a(path="findings[0].load_caps", op="max_count", value=0,
                              detector_filter="detect_crystal_circuits"), _DATA)
    assert not r["passed"] and r["actual"] == 2


def test_indexed_findings_path_past_the_filtered_list_is_missing():
    r = evaluate_assertion(_a(path="findings[2].ref", op="exists",
                              detector_filter="detect_crystal_circuits"), _DATA)
    assert not r["passed"]


def test_whole_list_filter_unchanged():
    r = evaluate_assertion(_a(path="findings", op="equals", value=2,
                              detector_filter="detect_crystal_circuits"), _DATA)
    assert r["passed"]


def test_indexed_path_without_filter_unchanged():
    r = evaluate_assertion(_a(path="findings[0].ref", op="equals", value="R1"), _DATA)
    assert r["passed"]
