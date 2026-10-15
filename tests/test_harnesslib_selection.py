# tests/test_harnesslib_selection.py
"""harnesslib.selection: None means all, [] is an error (report B12, TH-049)."""
TIER = "unit"

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harnesslib import selection as sel  # noqa: E402


def test_single_repo():
    repos, src = sel.resolve_selection(repo="o/r", cross_section=None, repo_list=None,
                                       all_=False, require_explicit_all=True)
    assert repos == ["o/r"] and src == "repo:o/r"


def test_cross_section_uses_loader():
    repos, src = sel.resolve_selection(repo=None, cross_section="smoke", repo_list=None,
                                       all_=False, require_explicit_all=True,
                                       load_cross_section=lambda n: ["a/b", "c/d"])
    assert repos == ["a/b", "c/d"] and src == "cross_section:smoke"


def test_cross_section_empty_raises():
    with pytest.raises(sel.EmptySelection, match="cross_section:empty"):
        sel.resolve_selection(repo=None, cross_section="empty", repo_list=None,
                              all_=False, require_explicit_all=False,
                              load_cross_section=lambda n: [])


def test_resolve_selection_empty_repo_list_raises(tmp_path):
    f = tmp_path / "repos.txt"
    f.write_text("# only comments\n\n")
    with pytest.raises(sel.EmptySelection, match="repo-list:"):
        sel.resolve_selection(repo=None, cross_section=None, repo_list=str(f),
                              all_=False, require_explicit_all=False)


def test_repo_list_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        sel.resolve_selection(repo=None, cross_section=None,
                              repo_list=str(tmp_path / "nope.txt"),
                              all_=False, require_explicit_all=False)


def test_nothing_given_requires_explicit_all():
    with pytest.raises(sel.NoSelection):
        sel.resolve_selection(repo=None, cross_section=None, repo_list=None,
                              all_=False, require_explicit_all=True)
    repos, src = sel.resolve_selection(repo=None, cross_section=None, repo_list=None,
                                       all_=True, require_explicit_all=True)
    assert repos is None and src == "all"
    repos, src = sel.resolve_selection(repo=None, cross_section=None, repo_list=None,
                                       all_=False, require_explicit_all=False)
    assert repos is None and src == "all"


def test_filter_units_none_keeps_all_and_list_filters():
    units = ["a/b/x.kicad_sch", "c/d/y.kicad_sch"]
    assert sel.filter_units(units, None) == units
    assert sel.filter_units(units, ["c/d"]) == ["c/d/y.kicad_sch"]
    assert sel.filter_units(units, []) == []
