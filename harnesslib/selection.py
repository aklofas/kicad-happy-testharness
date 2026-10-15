# harnesslib/selection.py
"""Repo selection semantics (report B12 / TH-049).

None means "all repos". An explicit empty selection is an error, never all.
Mutating all-corpus runs must say --all when require_explicit_all is True.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable


class EmptySelection(ValueError):
    """The named selection resolved to zero repos."""


class NoSelection(ValueError):
    """No selector given and --all was required."""


def _read_repo_list(path_str: str) -> list[str]:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"repo list not found: {path}")
    repos = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            repos.append(line)
    return repos


def resolve_selection(*, repo: str | None, cross_section: str | None,
                      repo_list: str | None, all_: bool, require_explicit_all: bool,
                      load_cross_section: Callable[[str], list[str]] | None = None
                      ) -> tuple[list[str] | None, str]:
    if repo:
        return [repo], f"repo:{repo}"
    if cross_section:
        if load_cross_section is None:
            raise ValueError("cross_section given but no loader supplied")
        repos = list(load_cross_section(cross_section))
        src = f"cross_section:{cross_section}"
        if not repos:
            raise EmptySelection(f"{src} resolved to zero repos")
        return repos, src
    if repo_list:
        repos = _read_repo_list(repo_list)
        src = f"repo-list:{repo_list}"
        if not repos:
            raise EmptySelection(f"{src} resolved to zero repos")
        return repos, src
    if require_explicit_all and not all_:
        raise NoSelection("no --repo/--cross-section/--repo-list given; "
                          "pass --all to run the whole corpus")
    return None, "all"


def filter_units(units: Iterable[str], repos: list[str] | None) -> list[str]:
    units = list(units)
    if repos is None:
        return units
    wanted = set(repos)
    out = []
    for u in units:
        parts = u.split("/")
        if len(parts) >= 2 and f"{parts[0]}/{parts[1]}" in wanted:
            out.append(u)
    return out
