"""The datasheet sync never writes into a corpus clone (sec A1-F2, ruling R12): its output
directory is the harness-owned results/datasheets/<owner>/<repo>/."""
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(HARNESS / "run"))

pytestmark = pytest.mark.unit

RECORDER = """import json, sys
out = sys.argv[sys.argv.index('--output') + 1]
open(sys.argv[0] + '.args', 'w').write(json.dumps({'output': out}))
"""


def test_sync_output_is_harness_owned(tmp_path, monkeypatch):
    import run_datasheets as rd
    clone = tmp_path / "checkouts" / "o" / "r"
    (clone / "datasheets").mkdir(parents=True)
    (clone / "datasheets" / "manifest.json").write_text(json.dumps({"x": {"status": "ok", "file": "/etc/hosts"}}))
    out = tmp_path / "outputs" / "schematic" / "o" / "r"
    out.mkdir(parents=True)
    (out / "x.kicad_sch.json").write_text("{}")
    sync = tmp_path / "sync.py"
    sync.write_text(RECORDER)
    monkeypatch.setattr(rd, "REPOS_DIR", tmp_path / "checkouts")
    monkeypatch.setattr(rd, "OUTPUTS_DIR", tmp_path / "outputs")
    monkeypatch.setattr(rd, "DATA_ROOT", tmp_path / "data")
    rd.download_datasheets("o/r", sync)
    used = Path(json.loads((tmp_path / "sync.py.args").read_text())["output"])
    assert used == tmp_path / "data" / "results" / "datasheets" / "o" / "r"
    assert sorted(p.name for p in (clone / "datasheets").iterdir()) == ["manifest.json"]


def test_validation_reads_the_harness_directory(monkeypatch, tmp_path):
    import run_datasheets as rd
    monkeypatch.setattr(rd, "DATA_ROOT", tmp_path)
    assert rd.datasheets_dir_for("o/r") == tmp_path / "results" / "datasheets" / "o" / "r"
