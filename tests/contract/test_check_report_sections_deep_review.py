"""check_report_sections: Deep Review slot (v2.0 spec §3.E)."""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

CHECKER = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "check_report_sections.py"
ANALYZER = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
SCH = HARNESS_ROOT / "tests" / "fixtures" / "simple-project" / "simple.kicad_sch"

RUN_ID = "test-check-report-run"


def _build_analysis_tree(tmp_path_factory, *, with_deep_review: bool):
    """Build a real analysis/ tree with schematic.json + manifest.json.

    Optionally also writes deep_review.json at the flat analysis-dir level.
    Copied from test_summarize_deep_review.py fixture pattern — contract tests
    stay self-contained.
    """
    d = tmp_path_factory.mktemp("check-report-analysis")

    # Run schematic analyzer to produce a real schematic.json.
    run_dir = d / RUN_ID
    run_dir.mkdir()
    sch_out = run_dir / "schematic.json"
    subprocess.run(
        [sys.executable, str(ANALYZER), str(SCH), "--output", str(sch_out)],
        check=True, capture_output=True)

    # Write a minimal manifest.json.
    manifest = {
        "version": 1,
        "project": "simple.kicad_pro",
        "current": RUN_ID,
        "runs": {
            RUN_ID: {
                "source_hashes": {},
                "outputs": {"schematic": "schematic.json"},
                "scripts": {},
                "generated": "2026-07-11T12:00:00Z",
                "pinned": False,
            }
        },
    }
    (d / "manifest.json").write_text(json.dumps(manifest, indent=2))

    if with_deep_review:
        # Extract real anchors from schematic output.
        sch_data = json.loads(sch_out.read_text())
        ref = sch_data["components"][0]["reference"]
        net = next(iter(sch_data["nets"]))

        doc = {
            "schema_version": "1.0",
            "produced_for_run_id": RUN_ID,
            "produced_at": "2026-07-11T12:00:00Z",
            "findings": [
                {
                    "detector": "deep_review",
                    "category": "power_input",
                    "severity": "error",
                    "confidence": "high",
                    "summary": f"{ref} supply voltage exceeds rating on {net}",
                    "recommendation": "Reduce supply voltage",
                    "evidence": {
                        "components": [ref],
                        "nets": [net],
                        "pins": [f"{ref}.1"],
                        "datasheet": [
                            {"mpn": "MISSING-PART", "page": 1, "quote": "max 3.3 V"}
                        ],
                        "computation": {
                            "description": "voltage margin check",
                            "result": "V=5V > 3.3V max",
                        },
                    },
                }
            ],
            "quarantined": [],
        }
        (d / "deep_review.json").write_text(json.dumps(doc, indent=2))

    return d


@pytest.fixture(scope="module")
def analysis_tree(tmp_path_factory):
    """Analysis tree WITH deep_review.json present."""
    return _build_analysis_tree(tmp_path_factory, with_deep_review=True)


@pytest.fixture(scope="module")
def analysis_tree_no_dr(tmp_path_factory):
    """Analysis tree WITHOUT deep_review.json."""
    return _build_analysis_tree(tmp_path_factory, with_deep_review=False)


def test_deep_review_section_required_when_file_present(analysis_tree):
    r = subprocess.run(
        [sys.executable, str(CHECKER), "--analysis-dir", str(analysis_tree)],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "Deep Review" in r.stdout


def test_deep_review_section_not_required_without_file(analysis_tree_no_dr):
    r = subprocess.run(
        [sys.executable, str(CHECKER), "--analysis-dir", str(analysis_tree_no_dr)],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "Deep Review" not in r.stdout


def test_report_mode_flags_missing_deep_review_heading(analysis_tree, tmp_path):
    report = tmp_path / "review.md"
    report.write_text("# Review\n## Overview\n...")   # no Deep Review heading
    r = subprocess.run(
        [sys.executable, str(CHECKER), "--analysis-dir", str(analysis_tree),
         "--report", str(report)],
        capture_output=True, text=True)
    # Missing sections: exit 1 (same semantics as other missing sections)
    assert r.returncode == 1
    assert "Deep Review" in r.stdout + r.stderr       # reported as missing


def test_report_mode_passes_with_deep_review_heading(analysis_tree, tmp_path):
    """A report that includes a ## Deep Review heading satisfies the requirement."""
    # Build a report with at minimum overview + deep review.
    # The checker requires ALL base sections too, so we need to satisfy those.
    # We only care that Deep Review specifically is checked — a targeted test
    # is to verify exit 0 when Deep Review is present vs exit 1 when absent
    # (already covered). Here we just confirm "deep review" alias matches.
    report = tmp_path / "review_with_dr.md"
    # Write a heading that matches the "deep review" alias.
    report.write_text("# Review\n## Deep Review\nSome content here.\n")
    r = subprocess.run(
        [sys.executable, str(CHECKER), "--analysis-dir", str(analysis_tree),
         "--report", str(report)],
        capture_output=True, text=True)
    # Deep Review is present — it should NOT appear in the MISSING list.
    # Other base sections will still be missing (exit 1), but not Deep Review.
    assert r.returncode == 1
    assert "MISSING" in r.stdout
    assert "Deep Review" not in r.stdout.split("MISSING")[1]
