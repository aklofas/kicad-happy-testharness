"""run_pcb flag normalization is pure; run_analyzer records the argv it parsed."""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit

HARNESS = Path(__file__).resolve().parent.parent
for p in (HARNESS, HARNESS / "run"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import utils  # noqa: E402
from run_pcb import normalize_pcb_argv  # noqa: E402


@pytest.mark.parametrize("flags, recorded", [
    ([], ["--repo", "o/r", "--jobs", "1", "--full", "--proximity"]),
    (["--no-proximity"], ["--repo", "o/r", "--jobs", "1", "--full"]),
    (["--no-full"], ["--repo", "o/r", "--jobs", "1", "--proximity"]),
    (["--no-full", "--no-proximity"], ["--repo", "o/r", "--jobs", "1"]),
    (["--full", "--proximity", "--full"], ["--repo", "o/r", "--jobs", "1", "--full", "--proximity"]),
    (["--resume"], ["--repo", "o/r", "--jobs", "1", "--full", "--proximity"]),
])
def test_normalize_matches_recorded_argv(flags, recorded):
    remaining, extra = normalize_pcb_argv(["--repo", "o/r", "--jobs", "1", *flags])
    assert [a for a in remaining if a != "--resume"] + extra == recorded


def test_normalize_does_not_mutate_its_input():
    argv = ["--repo", "o/r", "--no-full", "--full"]
    normalize_pcb_argv(argv)
    assert argv == ["--repo", "o/r", "--no-full", "--full"]


def _capture_run_batch(monkeypatch):
    seen = {}
    monkeypatch.setattr(utils._batch, "preflight", lambda *a, **k: 0)
    monkeypatch.setattr(utils, "resolve_repos_with_source", lambda *a, **k: (["o/r"], "test"))
    monkeypatch.setattr(utils, "resolve_kicad_happy_dir", lambda: Path("/nonexistent"))

    def fake(config, settings, paths, *, repo_list, selection_source, argv):
        seen["argv"] = argv
        return 0
    monkeypatch.setattr(utils._batch, "run_batch", fake)
    return seen


_CONFIG = {"type_name": "pcb", "analyzer_script": "analyze_pcb.py", "manifest_file": "all_pcbs.txt",
           "output_subdir": "pcb", "summarize": lambda d: ""}


def test_run_analyzer_with_args_records_process_argv(monkeypatch):
    seen = _capture_run_batch(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["prog", "--repo", "o/r"])
    utils.run_analyzer(dict(_CONFIG), args=SimpleNamespace(jobs=1))
    assert list(seen["argv"]) == ["--repo", "o/r"]


def test_run_analyzer_parses_and_records_explicit_argv(monkeypatch):
    seen = _capture_run_batch(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["prog", "--bogus"])
    utils.run_analyzer(dict(_CONFIG), argv=["--repo", "o/r", "--jobs", "1"])
    assert list(seen["argv"]) == ["--repo", "o/r", "--jobs", "1"]
