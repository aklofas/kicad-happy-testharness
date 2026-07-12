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
PCB_ANALYZER = (MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"
                / "analyze_pcb.py")
SCH = HARNESS_ROOT / "tests" / "fixtures" / "simple-project" / "simple.kicad_sch"
PCB = HARNESS_ROOT / "tests" / "fixtures" / "simple-project" / "simple.kicad_pcb"
PDF_DIR = HARNESS_ROOT / "tests" / "fixtures" / "datasheets-pdfs"

HAS_PDFTOTEXT = shutil.which("pdftotext") is not None


@pytest.fixture(scope="module")
def analysis_dir(tmp_path_factory):
    """Real analyzer output for the simple-project fixture."""
    d = tmp_path_factory.mktemp("analysis")
    subprocess.run(
        [sys.executable, str(ANALYZER), str(SCH),
         "--output", str(d / "schematic.json")],
        check=True, capture_output=True)
    subprocess.run(
        [sys.executable, str(PCB_ANALYZER), str(PCB),
         "--output", str(d / "pcb.json")],
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


def _pcb_only_net(analysis_dir):
    """A net name pcb.json knows that schematic.json does not (KH-347)."""
    sch = json.loads((analysis_dir / "schematic.json").read_text())
    pcb = json.loads((analysis_dir / "pcb.json").read_text())
    only = set(pcb["net_name_to_id"]) - set(sch["nets"])
    assert only, "fixture regression: no PCB-only net name"
    return sorted(only)[0]


def test_pcb_net_name_accepted(analysis_dir, tmp_path):
    # KH-347: the PCB net name is a valid citation for a net the
    # schematic only knows as __unnamed_N.
    ref, _ = _real_anchors(analysis_dir)
    p = tmp_path / "deep_review.json"
    p.write_text(json.dumps(_doc([_finding(ref, _pcb_only_net(analysis_dir))])))
    r = _run_gate(p, analysis_dir)
    assert r.returncode == 0, r.stderr
    out = json.loads(p.read_text())
    assert out["quarantined"] == []


def test_display_name_accepted(analysis_dir, tmp_path):
    # KH-347: the analyzer's display_name annotation is a valid citation.
    d = tmp_path / "analysis"
    d.mkdir()
    data = json.loads((analysis_dir / "schematic.json").read_text())
    net = next(n for n in data["nets"] if n.startswith("__unnamed_"))
    data["nets"][net]["display_name"] = "U1.VOUT"
    (d / "schematic.json").write_text(json.dumps(data))
    ref = data["components"][0]["reference"]
    p = tmp_path / "deep_review.json"
    p.write_text(json.dumps(_doc([_finding(ref, "U1.VOUT")])))
    r = _run_gate(p, d)
    assert r.returncode == 0, r.stderr


def test_unknown_net_still_quarantined(analysis_dir, tmp_path):
    ref, _ = _real_anchors(analysis_dir)
    p = tmp_path / "deep_review.json"
    p.write_text(json.dumps(_doc([_finding(ref, "NO_SUCH_NET_42")])))
    r = _run_gate(p, analysis_dir)
    assert r.returncode == 1
    out = json.loads(p.read_text())
    assert "NO_SUCH_NET_42" in out["quarantined"][0]["quarantine_reason"]


def test_quote_match_tolerates_unicode_and_hyphenation():
    # KH-347: verbatim quotes must survive degree signs, unit spacing,
    # punctuation variants, and PDF line-wrap hyphenation.
    import importlib.util
    spec = importlib.util.spec_from_file_location("deep_review_gate", GATE)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    pdf_text = ("Maximum resistance of device at 20°C.\n"
                "The over-\nvoltage clamp limit is 5.5 V")
    assert gate._quote_in_text(
        "Maximum resistance of device at 20°C", pdf_text)
    assert gate._quote_in_text(
        "maximum resistance of device at 20 ° C", pdf_text)
    assert gate._quote_in_text("the overvoltage clamp limit is 5.5V", pdf_text)
    assert gate._quote_in_text("over-voltage clamp limit", pdf_text)
    assert not gate._quote_in_text(
        "Maximum resistance of device at 25°C", pdf_text)
