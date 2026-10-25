"""Helpers shared by the runners that chain off other analyzers' outputs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import resolve_repos_with_source


def expand_selection(args, finder):
    """Resolve the repo selection and gather finder(repo) results in order;
    finder(None) when the selection is every repo."""
    repo_list, _selection_source = resolve_repos_with_source(
        args, require_explicit_all=True)
    if repo_list is not None:
        inputs = []
        for rn in repo_list:
            inputs.extend(finder(rn))
        return inputs
    return finder(None)


def err_first_line(err_file):
    """First line of the .err file: the 'status: detail' summary."""
    try:
        lines = err_file.read_text(encoding="utf-8").strip().splitlines()
        return lines[0] if lines else "unknown error"
    except OSError:
        return "unknown error"
