"""Evidence-gate contract for deep_review_gate.py (v2.0 spec 3.D)."""
import json
import shutil
import subprocess
import sys

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

GATE = (MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"
        / "deep_review_gate.py")
ANALYZER = (MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"
            / "analyze_schematic.py")
SCH = HARNESS_ROOT / "tests" / "fixtures" / "simple-project" / "simple.kicad_sch"
PDF_DIR = HARNESS_ROOT / "tests" / "fixtures" / "datasheets-pdfs"

HAS_PDFTOTEXT = shutil.which("pdftotext") is not None


@pytest.fixture(scope="module")
def analysis_dir(tmp_path_factory):
    """Real analyzer output for the simple-project fixture."""
    d = tmp_path_factory.mktemp("analysis")
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


def _finding(ref, net, **overrides):
    f = {
        "detector": "deep_review",
        "category": "power_input",
        "severity": "warning",
        "confidence": "medium",
        "summary": f"{ref} supply margin is thin on {net}",
        "evidence": {
            "components": [ref],
            "nets": [net],
            "computation": {
                "description": "margin check",
                "result": "margin = 0.2 V",
            },
        },
    }
    f.update(overrides)
    return f


def _run_gate(path, analysis_dir, *extra):
    return subprocess.run(
        [sys.executable, str(GATE), str(path),
         "--analysis-dir", str(analysis_dir), *extra],
        capture_output=True, text=True)


def test_valid_finding_passes_and_is_stamped(analysis_dir, tmp_path):
    ref, net = _real_anchors(analysis_dir)
    p = tmp_path / "deep_review.json"
    p.write_text(json.dumps(_doc([_finding(ref, net)])))
    r = _run_gate(p, analysis_dir)
    assert r.returncode == 0, r.stderr
    out = json.loads(p.read_text())
    f = out["findings"][0]
    assert f["finding_id"].startswith("deep_review:")
    assert f["evidence_checked"] in ("full", "partial")
    assert f["components"] == [ref]          # anchors mirrored top-level
    assert out["quarantined"] == []


def test_unknown_component_is_quarantined(analysis_dir, tmp_path):
    ref, net = _real_anchors(analysis_dir)
    bad = _finding(ref, net)
    bad["evidence"]["components"] = ["U999"]
    p = tmp_path / "deep_review.json"
    p.write_text(json.dumps(_doc([bad])))
    r = _run_gate(p, analysis_dir)
    assert r.returncode == 1
    out = json.loads(p.read_text())
    assert out["findings"] == []
    assert len(out["quarantined"]) == 1
    assert "U999" in out["quarantined"][0]["quarantine_reason"]


def test_anchor_without_source_is_quarantined(analysis_dir, tmp_path):
    ref, net = _real_anchors(analysis_dir)
    bad = _finding(ref, net)
    del bad["evidence"]["computation"]        # anchors only, no source
    p = tmp_path / "deep_review.json"
    p.write_text(json.dumps(_doc([bad])))
    r = _run_gate(p, analysis_dir)
    assert r.returncode == 1
    out = json.loads(p.read_text())
    assert "evidence source" in out["quarantined"][0]["quarantine_reason"]


def test_missing_computation_script_is_quarantined(analysis_dir, tmp_path):
    ref, net = _real_anchors(analysis_dir)
    bad = _finding(ref, net)
    bad["evidence"]["computation"]["script"] = "analysis/helpers/nope.py"
    p = tmp_path / "deep_review.json"
    p.write_text(json.dumps(_doc([bad])))
    r = _run_gate(p, analysis_dir, "--project-dir", str(tmp_path))
    assert r.returncode == 1


def test_regate_promotes_fixed_quarantined_entry(analysis_dir, tmp_path):
    ref, net = _real_anchors(analysis_dir)
    fixed = _finding(ref, net)
    fixed["quarantine_reason"] = "stale reason from previous gate run"
    p = tmp_path / "deep_review.json"
    p.write_text(json.dumps(_doc([], quarantined=[fixed])))
    r = _run_gate(p, analysis_dir)
    assert r.returncode == 0
    out = json.loads(p.read_text())
    assert len(out["findings"]) == 1
    assert "quarantine_reason" not in out["findings"][0]


def test_gate_is_byte_stable(analysis_dir, tmp_path):
    ref, net = _real_anchors(analysis_dir)
    p = tmp_path / "deep_review.json"
    p.write_text(json.dumps(_doc([_finding(ref, net)])))
    _run_gate(p, analysis_dir)
    first = p.read_bytes()
    _run_gate(p, analysis_dir)
    assert p.read_bytes() == first


@pytest.mark.skipif(not HAS_PDFTOTEXT, reason="pdftotext not installed")
def test_datasheet_quote_check(analysis_dir, tmp_path):
    ref, net = _real_anchors(analysis_dir)
    # Pull a real phrase off page 1 of a real fixture PDF.
    txt = subprocess.run(
        ["pdftotext", "-f", "1", "-l", "1",
         str(PDF_DIR / "LM2596-ADJ.pdf"), "-"],
        capture_output=True, text=True, check=True).stdout
    words = txt.split()
    quote = " ".join(words[:6])
    ds_dir = tmp_path / "datasheets"
    ds_dir.mkdir()
    shutil.copy(PDF_DIR / "LM2596-ADJ.pdf", ds_dir / "LM2596-ADJ.pdf")

    good = _finding(ref, net)
    good["evidence"]["datasheet"] = [
        {"mpn": "LM2596-ADJ", "page": 1, "quote": quote}]
    bad = _finding(ref, net, summary=f"{ref} second finding on {net}")
    bad["evidence"]["datasheet"] = [
        {"mpn": "LM2596-ADJ", "page": 1,
         "quote": "THIS STRING IS NOT IN THE DATASHEET zzqx"}]
    p = tmp_path / "deep_review.json"
    p.write_text(json.dumps(_doc([good, bad])))
    r = _run_gate(p, analysis_dir, "--datasheets-dir", str(ds_dir))
    assert r.returncode == 1
    out = json.loads(p.read_text())
    assert len(out["findings"]) == 1
    assert out["findings"][0]["evidence_checked"] == "full"
    assert len(out["quarantined"]) == 1
    assert "quote not found" in out["quarantined"][0]["quarantine_reason"]


def test_missing_pdf_marks_partial_not_quarantined(analysis_dir, tmp_path):
    ref, net = _real_anchors(analysis_dir)
    f = _finding(ref, net)
    f["evidence"]["datasheet"] = [
        {"mpn": "NO-SUCH-PART", "page": 3, "quote": "anything"}]
    ds_dir = tmp_path / "empty-datasheets"
    ds_dir.mkdir()
    p = tmp_path / "deep_review.json"
    p.write_text(json.dumps(_doc([f])))
    r = _run_gate(p, analysis_dir, "--datasheets-dir", str(ds_dir))
    assert r.returncode == 0
    out = json.loads(p.read_text())
    assert out["findings"][0]["evidence_checked"] == "partial"
