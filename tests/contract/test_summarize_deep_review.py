"""Contract tests: summarize_findings.py includes deep_review findings (v2.0 spec §3.C)."""
import json
import subprocess
import sys

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

SUMMARIZE = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "summarize_findings.py"
GATE = (MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"
        / "deep_review_gate.py")
ANALYZER = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
SCH = HARNESS_ROOT / "tests" / "fixtures" / "simple-project" / "simple.kicad_sch"

RUN_ID = "test-summarize-run"


@pytest.fixture(scope="module")
def analysis_tree(tmp_path_factory):
    """Build a real analysis/ tree with schematic.json, manifest.json, and a
    gated deep_review.json (1 included finding, 1 quarantined entry)."""
    d = tmp_path_factory.mktemp("analysis")

    # 1. Run analyzer to get schematic.json in the run subdir.
    run_dir = d / RUN_ID
    run_dir.mkdir()
    sch_out = run_dir / "schematic.json"
    subprocess.run(
        [sys.executable, str(ANALYZER), str(SCH), "--output", str(sch_out)],
        check=True, capture_output=True)

    # 2. Write a minimal manifest.json.
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

    # 3. Extract real anchors from schematic output for the deep_review finding.
    sch_data = json.loads(sch_out.read_text())
    ref = sch_data["components"][0]["reference"]
    net = next(iter(sch_data["nets"]))

    # 4. Write an un-gated deep_review.json with one valid finding + one quarantined.
    #    Datasheet cites MISSING-PART (no PDF in tmp dir) -> evidence_checked=partial,
    #    so the finding passes the gate (no quarantine from missing PDF).
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
        "quarantined": [
            {
                "detector": "deep_review",
                "category": "thermal",
                "severity": "warning",
                "confidence": "low",
                "summary": f"{ref} may exceed junction limits at full load",
                "evidence": {"components": [ref]},
                "quarantine_reason": (
                    "no evidence source: finding cites anchors but no "
                    "datasheet quote or computation"
                ),
            }
        ],
    }
    dr_path = d / "deep_review.json"
    dr_path.write_text(json.dumps(doc, indent=2))

    # 5. Run the gate — exit 1 is expected (quarantined entry present).
    empty_ds = tmp_path_factory.mktemp("empty-ds")
    result = subprocess.run(
        [sys.executable, str(GATE), str(dr_path),
         "--analysis-dir", str(d),
         "--datasheets-dir", str(empty_ds)],
        capture_output=True, text=True)
    # Gate exits 1 when quarantined is non-empty — that's expected here.
    assert result.returncode in (0, 1), (
        f"Gate exited {result.returncode}: {result.stderr}")

    return d


def test_summarize_includes_deep_review_by_category(analysis_tree):
    r = subprocess.run(
        [sys.executable, str(SUMMARIZE), str(analysis_tree)],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "power_input" in r.stdout        # category shown where rule_id goes
    assert "deep_review" in r.stdout        # detector column
    assert "quarantined" in r.stdout        # visibility line


def test_summarize_json_reports_deep_review_totals(analysis_tree):
    r = subprocess.run(
        [sys.executable, str(SUMMARIZE), str(analysis_tree), "--json"],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["deep_review"] == {"included": 1, "quarantined": 1}


def test_no_deep_review_flag_excludes(analysis_tree):
    r = subprocess.run(
        [sys.executable, str(SUMMARIZE), str(analysis_tree), "--no-deep-review"],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "power_input" not in r.stdout
