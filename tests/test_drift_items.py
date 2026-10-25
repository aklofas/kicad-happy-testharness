"""Drift results carry the item index they belong to, so cleanup and refresh need not
re-derive it."""
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
FIXTURE = HARNESS / "tests" / "fixtures" / "wave10" / "drift"
pytestmark = pytest.mark.unit


@pytest.fixture
def drift(monkeypatch):
    sys.path.insert(0, str(HARNESS))
    import regression.drift as d
    monkeypatch.setattr(d, "OUTPUTS_DIR", FIXTURE / "outputs")
    return d


def _findings():
    root = FIXTURE / "reference"
    return [f for ff in sorted(root.rglob("findings.json"))
            for f in json.loads(ff.read_text())["findings"]]


def test_results_match_the_checkable_item_order(drift):
    seen = 0
    for f in _findings():
        results = drift.validate_finding_items(f)
        assert drift.validate_finding(f) == [(r.category, r.item_type, r.description)
                                             for r in results]
        real = [r for r in results if r.item_type]
        if not real:
            assert len(results) == 1 and results[0].index is None
            continue
        expected = [(t, i) for t in ("correct", "incorrect", "missed")
                    for i, _ in drift.checkable_items(f, t)]
        assert [(r.item_type, r.index) for r in real] == expected
        for r in real:
            item = f[r.item_type][r.index]
            assert r.has_check == bool(item.get("check"))
            assert item.get("analyzer_section") and not item.get("disposition")
        seen += len(real)
    assert seen


def test_sentinel_has_no_item(drift):
    r, = drift.validate_finding_items({"repo": "x/y", "analyzer_type": "schematic",
                                       "source_file": "missing.json"})
    assert (r.item_type, r.index, r.category, r.has_check) == (None, None, "no_output", False)
