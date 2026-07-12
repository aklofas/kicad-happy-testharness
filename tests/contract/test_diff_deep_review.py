"""diff_analysis.py contract test for deep_review support (v2.0 spec §3.C)."""
import json
import subprocess
import sys

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

DIFF = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "diff_analysis.py"
GATE = (MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"
        / "deep_review_gate.py")
ANALYZER = (MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"
            / "analyze_schematic.py")
SCH = HARNESS_ROOT / "tests" / "fixtures" / "simple-project" / "simple.kicad_sch"


@pytest.fixture(scope="module")
def analysis_dir(tmp_path_factory):
    """Real analyzer output for the simple-project fixture."""
    d = tmp_path_factory.mktemp("analysis_dr_diff")
    out = d / "schematic.json"
    subprocess.run(
        [sys.executable, str(ANALYZER), str(SCH), "--output", str(out)],
        check=True, capture_output=True)
    return d


def _real_anchors(analysis_dir):
    data = json.loads((analysis_dir / "schematic.json").read_text())
    ref = data["components"][0]["reference"]
    net = next(iter(data["nets"]))
    return ref, net


def _doc(findings, quarantined=None):
    return {
        "schema_version": "1.0",
        "produced_for_run_id": "test-run",
        "produced_at": "2026-07-11T12:00:00Z",
        "findings": findings,
        "quarantined": quarantined or [],
    }


def _finding(ref, category, summary, **overrides):
    """Minimal valid finding (computation-only, no datasheet needed)."""
    f = {
        "detector": "deep_review",
        "category": category,
        "severity": "warning",
        "confidence": "medium",
        "summary": summary,
        "evidence": {
            "components": [ref],
            "computation": {
                "description": "margin check",
                "result": "margin = 0.2 V",
            },
        },
    }
    f.update(overrides)
    return f


def _run_gate(path, analysis_dir):
    return subprocess.run(
        [sys.executable, str(GATE), str(path),
         "--analysis-dir", str(analysis_dir)],
        capture_output=True, text=True)


@pytest.fixture(scope="module")
def gated_base(analysis_dir, tmp_path_factory):
    """Gated deep_review.json with findings A + B."""
    ref, _net = _real_anchors(analysis_dir)
    d = tmp_path_factory.mktemp("dr_base")
    p = d / "deep_review.json"
    # A: shared finding (same in both files)
    finding_a = _finding(ref, "power_input", f"{ref} supply margin is thin")
    # B: only in base (to be "fixed" in head)
    finding_b = _finding(ref, "power_input",
                         f"{ref} decoupling capacitor is undersized")
    p.write_text(json.dumps(_doc([finding_a, finding_b])))
    r = _run_gate(p, analysis_dir)
    assert r.returncode == 0, f"gate failed on base: {r.stderr}"
    return p


@pytest.fixture(scope="module")
def gated_head(analysis_dir, tmp_path_factory):
    """Gated deep_review.json with findings A + C (C shares B's category+components)."""
    ref, _net = _real_anchors(analysis_dir)
    d = tmp_path_factory.mktemp("dr_head")
    p = d / "deep_review.json"
    # A: identical to base finding A (same finding_id expected)
    finding_a = _finding(ref, "power_input", f"{ref} supply margin is thin")
    # C: different summary from B but same category + same evidence components
    finding_c = _finding(ref, "power_input",
                         f"{ref} decoupling cap value differs from BOM (reworded)")
    p.write_text(json.dumps(_doc([finding_a, finding_c])))
    r = _run_gate(p, analysis_dir)
    assert r.returncode == 0, f"gate failed on head: {r.stderr}"
    return p


def _read_findings_by_summary(path):
    """Return {summary: finding_id} from a gated file."""
    data = json.loads(path.read_text())
    return {f["summary"]: f["finding_id"] for f in data["findings"]}


def test_deep_review_diff_exact_and_fuzzy(gated_base, gated_head, analysis_dir):
    # Read the stamped IDs from the gated files
    base_ids = _read_findings_by_summary(gated_base)
    head_ids = _read_findings_by_summary(gated_head)

    ref, _net = _real_anchors(analysis_dir)
    A_ID = base_ids[f"{ref} supply margin is thin"]
    B_ID = base_ids[f"{ref} decoupling capacitor is undersized"]
    C_ID = head_ids[f"{ref} decoupling cap value differs from BOM (reworded)"]

    # A_ID must be the same in both (same category + anchors + summary)
    assert head_ids[f"{ref} supply margin is thin"] == A_ID, \
        "finding A must get the same id in base and head"

    r = subprocess.run(
        [sys.executable, str(DIFF), str(gated_base), str(gated_head)],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    dr = out["deep_review"]

    fixed_ids = {f["finding_id"] for f in dr["fixed"]}
    new_ids = {f["finding_id"] for f in dr["new"]}
    open_ids = {f["finding_id"] for f in dr["still_open"]}

    assert B_ID in fixed_ids
    assert C_ID in new_ids
    assert A_ID in open_ids

    assert dr["reworded_candidates"] == [{
        "base_finding_id": B_ID,
        "head_finding_id": C_ID,
        "category": "power_input",
        "note": "likely same finding, reworded (advisory)",
    }]


def test_deep_review_diff_quarantined_head_count(gated_base, gated_head):
    """quarantined_head reflects the head file's quarantined list length."""
    head_data = json.loads(gated_head.read_text())
    expected_quarantined = len(head_data.get("quarantined", []))

    r = subprocess.run(
        [sys.executable, str(DIFF), str(gated_base), str(gated_head)],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["deep_review"]["quarantined_head"] == expected_quarantined


def test_deep_review_diff_text_smoke(gated_base, gated_head):
    """--text output contains expected section labels."""
    r = subprocess.run(
        [sys.executable, str(DIFF), str(gated_base), str(gated_head), "--text"],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    text = r.stdout
    assert "fixed" in text.lower()
    assert "new" in text.lower()
    assert "reworded" in text.lower()


def test_detect_type_returns_deep_review(gated_base):
    """detect_type() must return 'deep_review' for a gated file."""
    # Run via subprocess to avoid polluting the test process's sys.path
    script = (
        "import sys, json\n"
        f"sys.path.insert(0, '{DIFF.parent}')\n"
        "import diff_analysis\n"
        f"data = json.loads(open('{gated_base}').read())\n"
        "print(diff_analysis.detect_type(data))\n"
    )
    r = subprocess.run([sys.executable, "-c", script],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "deep_review"
