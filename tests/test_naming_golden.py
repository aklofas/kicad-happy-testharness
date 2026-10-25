"""Golden outputs of the naming helpers in utils, pinned so moving them keeps every byte."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import utils

pytestmark = pytest.mark.unit

GOLDEN = Path(__file__).resolve().parent / "fixtures" / "wave10" / "naming_golden.json"

# "under" inputs are joined below <repos>/o/r; "raw" inputs are used as given.
INPUTS = [
    {"kind": "under", "rel": "top.kicad_sch"},
    {"kind": "under", "rel": "hw/rev2/board.kicad_pcb"},
    {"kind": "under", "rel": "a" * (143 - len(".kicad_sch")) + ".kicad_sch"},
    {"kind": "under", "rel": "a" * (144 - len(".kicad_sch")) + ".kicad_sch"},
    # bytes 132..134 (1-based) are one 3-byte character, so truncation lands inside it
    {"kind": "under", "rel": "b" * 131 + "€" + "c" * 20 + ".kicad_sch"},
    {"kind": "under", "rel": "hw\\rev2\\board.kicad_pcb"},
    {"kind": "raw", "path": "/srv/other/repos/o/r/hw/board.kicad_sch"},
]


def _resolve(entry, repos_dir):
    if entry["kind"] == "under":
        return str(Path(repos_dir) / "o" / "r" / entry["rel"])
    return entry["path"]


def _split(entry):
    rel = entry["rel"] if entry["kind"] == "under" else entry["path"]
    pdir, _, stem = rel.replace("\\", "/").rpartition("/")
    return pdir, stem


def compute(repos_dir):
    paths = [_resolve(e, repos_dir) for e in INPUTS]
    splits = [_split(e) for e in INPUTS]
    return {
        "inputs": INPUTS,
        "safe_name": [utils.safe_name(p) for p in paths],
        "project_key": [utils.project_key(d, s) for d, s in splits],
        "project_prefix": [utils.project_prefix(d) for d, _ in splits],
        "repo_name_from_path": [utils.repo_name_from_path(p) for p in paths],
        "within_repo_path": [utils.within_repo_path(p) for p in paths],
    }


def test_naming_outputs_match_golden(monkeypatch, tmp_path):
    repos = tmp_path / "repos"
    monkeypatch.setattr(utils, "REPOS_DIR", repos)
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert compute(repos) == golden


def test_golden_covers_the_byte_boundaries():
    names = [e["rel"] for e in INPUTS if e["kind"] == "under"]
    assert {len(n.encode()) for n in names} >= {143, 144}
    assert any(n.encode()[131:134] == "€".encode() for n in names)


def test_naming_reads_repos_dir_at_call_time(monkeypatch, tmp_path):
    monkeypatch.setattr(utils, "REPOS_DIR", tmp_path / "elsewhere")
    assert utils.repo_name_from_path(tmp_path / "elsewhere" / "o" / "r" / "x.kicad_sch") == "o/r"
