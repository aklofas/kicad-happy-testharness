"""Shared scheduler and selection helpers for the chained runners."""

TIER = "unit"

import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harnesslib.batch import map_units
from run import _chained
from run._chained import err_first_line, expand_selection


def _sleepy(pair):
    i, delay = pair
    time.sleep(delay)
    return i


def _add(a, b):
    return a + b


def _boom(x):
    raise ValueError(x)


def test_map_units_keeps_input_order_when_completion_is_reversed():
    units = [(0, 0.3), (1, 0.2), (2, 0.1)]
    assert map_units(_sleepy, units, 3) == [0, 1, 2]


def test_map_units_sequential_and_parallel_agree():
    units = [(i, 0.05 * (5 - i)) for i in range(6)]
    assert map_units(_sleepy, units, 1) == map_units(_sleepy, units, 3) == list(range(6))


def test_map_units_unpack_passes_pairs_as_two_args():
    assert map_units(_add, [(1, 2), (3, 4)], 2, unpack=True) == [3, 7]
    assert map_units(_add, [(1, 2), (3, 4)], 1, unpack=True) == [3, 7]


@pytest.mark.parametrize("jobs", [1, 2])
def test_map_units_propagates_worker_exception(jobs):
    with pytest.raises(ValueError):
        map_units(_boom, [1, 2], jobs)


def test_expand_selection_calls_finder_per_repo_in_order(monkeypatch):
    monkeypatch.setattr(_chained, "resolve_repos_with_source",
                        lambda args, require_explicit_all: (["a", "b"], "repo-list"))
    calls = []
    seen = {}

    def resolve(args, require_explicit_all):
        seen["require_explicit_all"] = require_explicit_all
        return ["a", "b"], "repo-list"
    monkeypatch.setattr(_chained, "resolve_repos_with_source", resolve)

    def finder(rn):
        calls.append(rn)
        return [f"{rn}1", f"{rn}2"]

    assert expand_selection(SimpleNamespace(), finder) == (["a", "b"], ["a1", "a2", "b1", "b2"])
    assert calls == ["a", "b"]
    assert seen["require_explicit_all"] is True


def test_expand_selection_all_calls_finder_with_none(monkeypatch):
    monkeypatch.setattr(_chained, "resolve_repos_with_source",
                        lambda args, require_explicit_all: (None, "all"))
    calls = []

    def finder(rn):
        calls.append(rn)
        return ["x"]

    assert expand_selection(SimpleNamespace(), finder) == (None, ["x"])
    assert calls == [None]


def test_err_first_line(tmp_path):
    f = tmp_path / "a.err"
    f.write_text("status: x\nmore\n", encoding="utf-8")
    assert err_first_line(f) == "status: x"
    assert err_first_line(tmp_path / "missing.err") == "unknown error"
    f.write_text("", encoding="utf-8")
    assert err_first_line(f) == "unknown error"
