"""`where` (every listed field must match) and `field: "."` (the list item itself) on the
match operators."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "regression"))
from checks import evaluate_assertion  # noqa: E402

pytestmark = pytest.mark.unit

DATA = {"findings": [
    {"detector": "d", "ref": "R1", "type": "pull_up", "net": "SDA"},
    {"detector": "d", "ref": "R2", "type": "pull_down", "net": "SCL"},
], "rails": ["+3V3", "GND", "VBUS"]}


def _run(check):
    return evaluate_assertion({"id": "T", "check": check}, DATA)["passed"]


def test_contains_match_where_needs_every_field():
    assert _run({"path": "findings", "op": "contains_match",
                 "where": {"ref": "^R1$", "type": "^pull_up$"}})
    assert not _run({"path": "findings", "op": "contains_match",
                     "where": {"ref": "^R1$", "type": "^pull_down$"}})


def test_not_contains_match_where_fails_only_on_a_full_match():
    assert _run({"path": "findings", "op": "not_contains_match",
                 "where": {"ref": "^R2$", "type": "^pull_up$"}})
    assert not _run({"path": "findings", "op": "not_contains_match",
                     "where": {"ref": "^R2$", "type": "^pull_down$"}})


def test_count_matches_where():
    assert _run({"path": "findings", "op": "count_matches", "value": 1,
                 "where": {"net": "^S", "type": "pull"}, "pattern": "R2", "field": "ref"})
    assert _run({"path": "findings", "op": "count_matches", "value": 2, "where": {"net": "^S"}})


def test_where_with_pattern_needs_both():
    assert not _run({"path": "findings", "op": "contains_match", "field": "net",
                     "pattern": "^SCL$", "where": {"ref": "^R1$"}})
    assert _run({"path": "findings", "op": "contains_match", "field": "net",
                 "pattern": "^SDA$", "where": {"ref": "^R1$"}})


def test_where_missing_field_does_not_match():
    assert not _run({"path": "findings", "op": "contains_match", "where": {"value": "."}})


def test_dot_field_matches_scalar_items():
    assert _run({"path": "rails", "op": "contains_match", "field": ".", "pattern": "^VBUS$"})
    assert not _run({"path": "rails", "op": "contains_match", "field": ".", "pattern": "^5V$"})
    assert not _run({"path": "rails", "op": "not_contains_match", "field": ".", "pattern": "^GND$"})
    assert _run({"path": "rails", "op": "count_matches", "field": ".", "pattern": "^\\+", "value": 1})


def test_scalar_items_still_ignored_without_dot_field():
    assert not _run({"path": "rails", "op": "contains_match", "pattern": "VBUS"})
    assert _run({"path": "rails", "op": "not_contains_match", "pattern": "GND"})


def test_where_empty_list_reads_as_empty_string():
    data = {"items": [{"ref": "R1", "pull_ups": []}, {"ref": "R2", "pull_ups": ["R9"]}]}
    run = lambda c: evaluate_assertion({"id": "T", "check": c}, data)["passed"]
    assert run({"path": "items", "op": "contains_match", "where": {"ref": "^R1$", "pull_ups": "^$"}})
    assert not run({"path": "items", "op": "contains_match", "where": {"ref": "^R2$", "pull_ups": "^$"}})
