"""validate_candidates clones only well-formed https candidates into a scratch dir each job
owns, and cleans up only that dir (sec A1-F1)."""
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS / "tools"))
import validate_candidates as vc  # noqa: E402

pytestmark = pytest.mark.unit

OK = {"owner": "acme", "repo": "board", "url": "https://github.com/acme/board"}


@pytest.mark.parametrize("bad", [
    {"repo": "/etc"}, {"repo": "../../victim"}, {"owner": ".."}, {"repo": "a/../b"},
    {"repo": ""}, {"owner": "a/b"}, {"url": "ext::sh -c x"}, {"url": "http://github.com/acme/board"},
    {"url": "file:///tmp/x"},
])
def test_malformed_candidates_are_rejected(bad):
    assert vc.candidate_rejection({**OK, **bad})


def test_gitlab_subgroup_repo_is_accepted():
    assert vc.candidate_rejection({**OK, "repo": "group/sub-proj.v2"}) is None


def test_failed_clone_cleans_only_its_own_job_dir(tmp_path, monkeypatch):
    keep = tmp_path / "acme" / "board"
    keep.mkdir(parents=True)
    (keep / "precious.txt").write_text("x")
    monkeypatch.setattr(vc, "_shallow_clone", lambda url, dest, timeout=60: False)
    assert vc.validate_one(OK, str(tmp_path), 10)[2] == "clone_failed"
    assert (keep / "precious.txt").exists()
    assert not list(tmp_path.glob("job_*"))
    assert vc.validate_one({**OK, "repo": "/etc"}, str(tmp_path), 10)[2] == "invalid_candidate"


def test_resume_merge_dedupes_by_owner_repo():
    """code A5-F9: the incremental save wrote this run's passes, then the final merge added
    them again (existing + passed)."""
    old = [{"owner": "a", "repo": "x", "v": 1}, {"owner": "b", "repo": "y", "v": 1}]
    new = [{"owner": "b", "repo": "y", "v": 2}, {"owner": "c", "repo": "z", "v": 2}]
    merged = vc.merge_validated(old + new[:1], new)
    assert [(c["owner"], c["v"]) for c in merged] == [("a", 1), ("b", 2), ("c", 2)]
