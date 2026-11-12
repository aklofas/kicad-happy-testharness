"""Every corpus assertion set must reach an analyzer output, or be retired.

run_checks reports a set whose output file is not found as "output file not found" on
every run; an aspirational assertion in such a set can never graduate. A set may stay
unresolved only while every finding it was created from carries a disposition.
"""
import json

import pytest

from regression.reference_io import find_output_file, resolve_project_path
from utils import DATA_DIR, OUTPUTS_DIR

ITEM_KEYS = ("correct", "incorrect", "missed")


def finding_dispositioned(finding):
    """True when every item of the finding (or the finding itself, for the flat
    shape that carries its own check) records a disposition."""
    items = [i for k in ITEM_KEYS for i in finding.get(k, [])]
    return all(i.get("disposition") for i in (items or [finding]))


def _repo_findings(repo_dir):
    found = {}
    for fj in repo_dir.glob("*/findings.json"):
        for f in json.loads(fj.read_text(encoding="utf-8")).get("findings", []):
            found[f.get("id")] = f
    return found


def unresolved_sets(data_dir):
    """Assertion sets with assertions, no output and an undispositioned source finding."""
    bad = []
    for assertions_dir in sorted(data_dir.glob("*/*/*/assertions")):
        proj_dir = assertions_dir.parent
        repo_dir = proj_dir.parent
        repo = f"{repo_dir.parent.name}/{repo_dir.name}"
        project_path = resolve_project_path(repo, proj_dir.name)
        if project_path is None and not (proj_dir / "baselines").is_dir():
            continue  # load_assertions skips stray project dirs with a warning
        findings = None
        for f in sorted(assertions_dir.glob("*/*.json")):
            aset = json.loads(f.read_text(encoding="utf-8"))
            assertions = aset.get("assertions", [])
            if not assertions:
                continue
            if find_output_file(aset.get("file_pattern", ""), repo, project_path,
                                aset.get("analyzer_type", f.parent.name)):
                continue
            if findings is None:
                findings = _repo_findings(repo_dir)
            sources = {a.get("created_from") or aset.get("created_from") for a in assertions}
            if sources and all(s in findings and finding_dispositioned(findings[s])
                               for s in sources):
                continue
            bad.append(str(f.relative_to(data_dir)))
    return bad


@pytest.mark.unit
def test_finding_dispositioned_shapes():
    item = {"check": {}, "disposition": {"state": "output_not_found"}}
    assert finding_dispositioned({"incorrect": [item], "missed": [dict(item)]})
    assert not finding_dispositioned({"incorrect": [item], "missed": [{"check": {}}]})
    assert finding_dispositioned({"check": {}, "disposition": {"state": "x"}})
    assert not finding_dispositioned({"check": {}})


@pytest.mark.corpus
def test_every_assertion_set_resolves_or_is_retired():
    if not DATA_DIR.is_dir() or not OUTPUTS_DIR.is_dir():
        pytest.skip("corpus reference/ or results/outputs/ not present")
    bad = unresolved_sets(DATA_DIR)
    assert not bad, f"{len(bad)} assertion sets resolve to no output:\n" + "\n".join(bad)
