"""End-to-end Layer 2 merge against REAL analyzer output.

``test_merge_annotations.py`` builds SYNTHETIC envelopes whose findings always
carry a finding_id, so it never exercised the actual producer→merge path. That
gap is why the no-op shipped: real analyzer findings (most not routed through
``make_finding``) had no finding_id, so ``merge_annotations._find_finding``
matched nothing and ``applied_count`` was 0 while the merge still "succeeded".

This test runs the real analyzers (via the ``analysis_dir`` fixture), references
their real finding_ids in a synthesized ``review_annotations.json``, runs the
merge, and asserts every annotation actually lands — which the pre-F3 code,
lacking ``assign_finding_ids``, would fail (applied_count==0, all orphaned).
"""

from tests.contract._paths import MAIN_REPO_ROOT
from tests.contract.conftest import ANALYZER_STEMS

import json
import sys
from pathlib import Path

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"))

REVIEW_RUN_ID = "20260528T000000Z-aaaaaa"


def _annotation(finding_id: str) -> dict:
    return {
        "finding_id": finding_id,
        "status": "confirmed",
        "reason": "Confirmed against real analyzer output for the e2e merge test.",
        "confidence": "high",
        "reviewed_at": "2026-05-28T00:00:00Z",
    }


def _all_findings(analysis_dir: Path):
    """Yield (stem, finding) for every finding across all real envelopes."""
    for stem in ANALYZER_STEMS:
        env = json.loads((analysis_dir / f"{stem}.json").read_text())
        for f in env.get("findings", []):
            yield stem, f


def test_merge_applies_real_finding_ids(analysis_dir, tmp_path):
    """Reference EVERY real finding by its id and assert the merge lands all of
    them. The pre-F3 producer fails this two ways: most findings have no
    finding_id (so ``len(ids) == total`` breaks — they aren't addressable at
    all), and any annotation that did slip through would orphan."""
    from merge_annotations import merge

    findings = list(_all_findings(analysis_dir))
    total = len(findings)
    assert total > 0, "fixture produced no findings across any analyzer"

    ids = [f["finding_id"] for _, f in findings if f.get("finding_id")]
    # Full addressability: every real finding carries an id. This is the
    # condition the no-op violated (most findings had none).
    assert len(ids) == total, (
        f"{total - len(ids)} of {total} real findings are not addressable "
        f"(no finding_id) — the Layer 2 merge would silently skip them")

    unique_ids = list(dict.fromkeys(ids))  # dedup any aliased duplicates
    review = {
        "schema_version": "1.0",
        "produced_for_run_id": REVIEW_RUN_ID,
        "produced_at": "2026-05-28T00:00:00Z",
        "annotations": [_annotation(fid) for fid in unique_ids],
        "reviewer_observations": [],
    }
    review_path = tmp_path / "review_annotations.json"
    review_path.write_text(json.dumps(review))
    merged_dir = tmp_path / "merged"

    report = merge(analysis_dir, review_path, merged_dir)

    assert report["annotation_count"] == len(unique_ids)
    assert report["applied_count"] == len(unique_ids)  # no-op would give 0
    assert report["orphan_annotations"] == []
    assert report["invariant_violations"] == []

    # Overlays actually landed on the referenced findings in merged output.
    landed = set()
    for stem in ANALYZER_STEMS:
        env = json.loads((merged_dir / f"{stem}.json").read_text())
        for f in env.get("findings", []):
            if f.get("finding_id") in unique_ids and "llm_review" in f:
                assert f["llm_review"]["status"] == "confirmed"
                landed.add(f["finding_id"])
    assert landed == set(unique_ids)


def test_merge_orphans_unknown_finding_id(analysis_dir, tmp_path):
    """Control: an annotation that references a non-existent finding_id is
    orphaned and not applied — proving the e2e success above isn't a fluke
    where everything matches regardless."""
    from merge_annotations import merge

    review = {
        "schema_version": "1.0",
        "produced_for_run_id": REVIEW_RUN_ID,
        "produced_at": "2026-05-28T00:00:00Z",
        "annotations": [_annotation("schematic:VM-001:does-not-exist")],
        "reviewer_observations": [],
    }
    review_path = tmp_path / "review_annotations.json"
    review_path.write_text(json.dumps(review))
    merged_dir = tmp_path / "merged"

    report = merge(analysis_dir, review_path, merged_dir)
    assert report["applied_count"] == 0
    assert len(report["orphan_annotations"]) == 1
    assert report["orphan_annotations"][0]["finding_id"] == "schematic:VM-001:does-not-exist"
