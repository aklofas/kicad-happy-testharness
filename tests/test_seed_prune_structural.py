"""seed.py --prune-stale removes STRUCT files whose output is gone, not only SEED files (TH-112)."""

TIER = "unit"

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
import reference_io  # noqa: E402
import seed  # noqa: E402

pytestmark = pytest.mark.unit


def _write(path, generated_by, pattern):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"file_pattern": pattern, "analyzer_type": "pcb",
                                "generated_by": generated_by, "assertions": []}))


@pytest.fixture
def ref(tmp_path, monkeypatch):
    data = tmp_path / "reference"
    out = tmp_path / "out.json"
    out.write_text(json.dumps({"footprints": []}))   # below any seeding threshold
    adir = data / "o" / "r" / "proj" / "assertions" / "pcb"
    _write(adir / "gone.kicad_pcb.json", "seed.py", "gone.kicad_pcb")
    _write(adir / "gone.kicad_pcb_structural.json", "seed_structural.py", "gone.kicad_pcb")
    _write(adir / "small.kicad_pcb.json", "seed.py", "small.kicad_pcb")
    _write(adir / "small.kicad_pcb_structural.json", "seed_structural.py", "small.kicad_pcb")
    _write(adir / "gone.kicad_pcb_finding.json", "findings.py promote", "gone.kicad_pcb")
    monkeypatch.setattr(seed, "DATA_DIR", data)
    monkeypatch.setattr(reference_io, "resolve_project_path", lambda repo, proj: ".")
    monkeypatch.setattr(reference_io, "find_output_file",
                        lambda pattern, repo, pp, atype: out if pattern == "small.kicad_pcb" else None)
    return adir


def test_structural_file_pruned_when_output_missing(ref):
    pruned, _ = seed.prune_stale_assertions("o/r", "pcb", min_components=10, dry_run=False)
    assert not (ref / "gone.kicad_pcb_structural.json").exists()
    assert not (ref / "gone.kicad_pcb.json").exists()
    assert pruned == 3


def test_structural_file_kept_below_seed_threshold(ref):
    # the seeding threshold is a SEED rule; structural files are pruned only when the output is gone
    seed.prune_stale_assertions("o/r", "pcb", min_components=10, dry_run=False)
    assert (ref / "small.kicad_pcb_structural.json").exists()
    assert not (ref / "small.kicad_pcb.json").exists()


def test_curated_files_never_pruned(ref):
    seed.prune_stale_assertions("o/r", "pcb", min_components=10, dry_run=False)
    assert (ref / "gone.kicad_pcb_finding.json").exists()


def test_dry_run_writes_nothing(ref):
    pruned, _ = seed.prune_stale_assertions("o/r", "pcb", min_components=10, dry_run=True)
    assert pruned == 3
    assert (ref / "gone.kicad_pcb_structural.json").exists()
