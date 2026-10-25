TIER = "unit"

import ast
from pathlib import Path

from harnesslib import corpus_read
from harnesslib.corpus_read import SIDECAR_NAMES, assertion_prefix, json_files


def _make(tmp_path):
    for name in ("b.json", "a.json", "_agg.json", "capability_mode.json", "note.txt"):
        (tmp_path / name).write_text("{}")
    return tmp_path


def _names(paths):
    return [p.name for p in paths]


def test_json_files_missing_directory_is_empty(tmp_path):
    assert json_files(tmp_path / "none", sort=True, skip_underscore=True, skip_sidecar=True) == []


def test_json_files_flags(tmp_path):
    d = _make(tmp_path)
    assert SIDECAR_NAMES == frozenset({"capability_mode.json"})
    assert _names(json_files(d, sort=True, skip_underscore=False, skip_sidecar=False)) == [
        "_agg.json", "a.json", "b.json", "capability_mode.json"]
    assert _names(json_files(d, sort=True, skip_underscore=True, skip_sidecar=False)) == [
        "a.json", "b.json", "capability_mode.json"]
    assert _names(json_files(d, sort=True, skip_underscore=False, skip_sidecar=True)) == [
        "_agg.json", "a.json", "b.json"]
    assert _names(json_files(d, sort=True, skip_underscore=True, skip_sidecar=True)) == [
        "a.json", "b.json"]


def test_json_files_unsorted_is_glob_order(tmp_path):
    d = _make(tmp_path)
    got = json_files(d, sort=False, skip_underscore=False, skip_sidecar=False)
    assert got == list(d.glob("*.json"))


def test_assertion_prefix():
    assert assertion_prefix("SEED-1") == "SEED"
    assert assertion_prefix("X") == "OTHER"
    assert assertion_prefix("X", no_dash="") == ""
    assert assertion_prefix("") == "OTHER"


def test_corpus_read_imports_no_harness_layer():
    tree = ast.parse(Path(corpus_read.__file__).read_text(encoding="utf-8"))
    banned = {"utils", "run", "regression", "tools", "validate"}
    for node in ast.walk(tree):
        mods = []
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            mods = [node.module or ""]
        for m in mods:
            assert m.split(".")[0] not in banned, m
