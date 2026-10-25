"""analyze_bom_mismatch walks <outputs>/<owner>/<repo>/ and filters by owner/repo
(code A4-F14, arch O7c / TH-088): it globbed one level and found nothing."""
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS / "validate"))
import analyze_bom_mismatch as abm  # noqa: E402

pytestmark = pytest.mark.unit


def test_walks_owner_repo_layout_and_filters_by_owner_repo(tmp_path):
    for repo in ("o/a", "o/b"):
        d = tmp_path / repo
        d.mkdir(parents=True)
        (d / "x.kicad_sch.json").write_text("{}")
        (d / "capability_mode.json").write_text("{}")
    assert [f.parent.name for f in abm.schematic_output_files(tmp_path)] == ["a", "b"]
    assert [f.parent.name for f in abm.schematic_output_files(tmp_path, "o/b")] == ["b"]
