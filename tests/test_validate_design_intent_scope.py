"""validate_design_intent filters a multi-repo selection (arch O7b / TH-087)."""
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS / "validate"))
sys.path.insert(0, str(HARNESS))
import validate_design_intent as vdi  # noqa: E402

pytestmark = pytest.mark.unit


def test_multi_repo_selection_is_filtered(tmp_path, monkeypatch):
    for repo in ("o/a", "o/b", "o/c"):
        d = tmp_path / "schematic" / repo
        d.mkdir(parents=True)
        (d / "x.json").write_text(json.dumps({}))
    monkeypatch.setattr(vdi, "OUTPUTS_DIR", tmp_path)
    _, stats = vdi._scan_outputs(["o/a", "o/c"], analyzer_types=("schematic",))
    assert stats["files_checked"] == 2
    _, stats = vdi._scan_outputs(None, analyzer_types=("schematic",))
    assert stats["files_checked"] == 3
