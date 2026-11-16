"""The schematic detector summary counts only the outputs this run wrote, not the whole
corpus output tree (a --repo run used to re-read all ~45k schematic outputs)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesslib.batch import _print_detector_aggregate  # noqa: E402

pytestmark = pytest.mark.unit


def test_aggregate_counts_only_the_given_outputs(tmp_path, capsys):
    mine = tmp_path / "o" / "mine" / "a.json"
    other = tmp_path / "o" / "other" / "b.json"
    for p, det in ((mine, "detect_x"), (other, "detect_y")):
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps({"findings": [{"detector": det}, {"detector": det}]}))
    _print_detector_aggregate([mine, tmp_path / "missing.json"])
    out = capsys.readouterr().out
    assert "detect_x" in out and "1 files" in out and "2 items" in out
    assert "detect_y" not in out
