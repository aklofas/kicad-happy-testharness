"""KH-384/KH-385 deep_review_gate.py regression tests (harness; adopt via harness agent).

KH-384: without an explicit --project-dir, evidence.computation.script
paths (project-root-relative) must resolve against --analysis-dir's
parent, not the invoking cwd -- the gate quarantined otherwise-valid
findings when run from anywhere but the project root.

KH-385: datasheet quotes containing a mid-quote elision ('...' or the
Unicode ellipsis '…') must verify segment-wise, in order, against the
cited PDF page; a still-unverifiable quote's quarantine reason must
carry a deterministic nearest-match hint so a reviewer isn't left to
grep the PDF by hand.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:  # pre-push hook runs root tests under bare python3 (no
    # pytest); only decorator applications happen at import time, so a no-op
    # stand-in keeps the file importable — the tests themselves need pytest.
    class _StubMark:
        @staticmethod
        def skipif(*_a, **_k):
            return lambda fn: fn

    class _StubPytest:
        mark = _StubMark

        @staticmethod
        def fixture(*_a, **_k):
            return lambda fn: fn

        @staticmethod
        def skip(reason=""):
            raise SystemExit(0)

    pytest = _StubPytest

KH = Path(os.environ["KICAD_HAPPY_DIR"])
GATE = KH / "skills/kicad/review/scripts/deep_review_gate.py"
ANALYZER = KH / "skills/kicad/scripts/analyze_schematic.py"

SCH = Path(__file__).resolve().parent / "fixtures/simple-project/simple.kicad_sch"
PDF_DIR = Path(__file__).resolve().parent / "fixtures/datasheets-pdfs"

HAS_PDFTOTEXT = shutil.which("pdftotext") is not None


@pytest.fixture(scope="module")
def project(tmp_path_factory):
    """<project>/analysis/schematic.json + a project-root-relative
    helper script -- the on-disk shape deep_review_gate.py expects.
    """
    root = tmp_path_factory.mktemp("kh384_385_project")
    analysis_d = root / "analysis"
    analysis_d.mkdir()
    out = subprocess.run(
        [sys.executable, str(ANALYZER), str(SCH),
         "--output", str(analysis_d / "schematic.json")],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stderr

    helpers = root / "helpers"
    helpers.mkdir()
    (helpers / "check_thing.py").write_text("# stub helper\n")
    return root


def _real_anchors(analysis_dir):
    data = json.loads((analysis_dir / "schematic.json").read_text())
    ref = data["components"][0]["reference"]
    net = next(iter(data["nets"]))
    return ref, net


def _doc(findings):
    return {
        "schema_version": "1.0",
        "produced_for_run_id": "test-run",
        "produced_at": "2026-07-11T12:00:00Z",
        "findings": findings,
        "quarantined": [],
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
                "script": "helpers/check_thing.py",
                "result": "margin = 0.2 V",
            },
        },
    }
    f.update(overrides)
    return f


def _run_gate(path, analysis_dir, *extra, cwd=None):
    return subprocess.run(
        [sys.executable, str(GATE), str(path),
         "--analysis-dir", str(analysis_dir), *extra],
        capture_output=True, text=True, cwd=cwd)


# ---------------------------------------------------------------------
# KH-384: project-dir anchoring
# ---------------------------------------------------------------------

def test_kh384_script_resolves_from_other_cwd_without_project_dir(project, tmp_path):
    """A finding citing a project-relative computation script must
    validate even when the gate is invoked from a cwd that is neither
    the project root nor --analysis-dir -- --project-dir should
    default to --analysis-dir's parent, not '.'."""
    analysis_d = project / "analysis"
    ref, net = _real_anchors(analysis_d)

    dr_path = tmp_path / "deep_review.json"   # deliberately outside project root
    dr_path.write_text(json.dumps(_doc([_finding(ref, net)])))

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    r = _run_gate(dr_path, analysis_d, cwd=str(elsewhere))
    assert r.returncode == 0, r.stdout + r.stderr
    out = json.loads(dr_path.read_text())
    assert out["quarantined"] == [], out["quarantined"]
    assert len(out["findings"]) == 1
    assert out["findings"][0]["evidence_checked"] in ("full", "partial")


def test_kh384_explicit_project_dir_still_honored(project, tmp_path):
    """Regression: an explicit --project-dir must still override the
    default (unchanged prior behavior)."""
    analysis_d = project / "analysis"
    ref, net = _real_anchors(analysis_d)

    bad = _finding(ref, net)
    bad["evidence"]["computation"]["script"] = "helpers/does_not_exist.py"
    dr_path = tmp_path / "deep_review.json"
    dr_path.write_text(json.dumps(_doc([bad])))

    r = _run_gate(dr_path, analysis_d, "--project-dir", str(project))
    assert r.returncode == 1
    out = json.loads(dr_path.read_text())
    assert "does_not_exist.py" in out["quarantined"][0]["quarantine_reason"]


# ---------------------------------------------------------------------
# KH-385: elision-tolerant quote matching + nearest-match hints
# ---------------------------------------------------------------------

def test_elision_segments_matched_in_order():
    """Unit-level: both '...' and the Unicode '…' split a quote into
    segments that must each appear in the text, in order."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("deep_review_gate", GATE)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)

    text = "alpha bravo charlie delta echo foxtrot"
    assert gate._quote_in_text("alpha bravo ... echo foxtrot", text)
    assert gate._quote_in_text("alpha bravo … echo foxtrot", text)
    # segments present but out of order -> not a match
    assert not gate._quote_in_text("echo foxtrot ... alpha bravo", text)
    # first segment real, second fabricated -> not a match
    assert not gate._quote_in_text("alpha bravo ... not present anywhere", text)
    # non-elided behavior (KH-347) must be unchanged
    assert gate._quote_in_text("alpha bravo charlie", text)
    assert not gate._quote_in_text("alpha zulu charlie", text)


def test_nearest_match_is_deterministic_and_nonempty():
    """Unit-level: the stride-40/window-80 search must be repeatable
    (fixed stride, first-best-wins tie-breaking)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("deep_review_gate", GATE)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)

    text = "the quick brown fox jumps over the lazy dog. " * 5
    a = gate._nearest_match("the quick brown fox jumps over the lazy cat", text)
    b = gate._nearest_match("the quick brown fox jumps over the lazy cat", text)
    assert a == b
    assert isinstance(a, str) and a


@pytest.mark.skipif(not HAS_PDFTOTEXT, reason="pdftotext not installed")
def test_kh385_elided_quote_passes_fabricated_quote_quarantines_with_nearest_match(
        project, tmp_path):
    """End-to-end through the real pdftotext extraction path (mirrors
    check_datasheet, not a monkeypatch of it)."""
    analysis_d = project / "analysis"
    ref, net = _real_anchors(analysis_d)

    txt = subprocess.run(
        ["pdftotext", "-f", "1", "-l", "1",
         str(PDF_DIR / "LM2596-ADJ.pdf"), "-"],
        capture_output=True, text=True, check=True).stdout
    words = txt.split()
    assert len(words) >= 20, "fixture regression: page 1 too short"
    seg1 = " ".join(words[:4])
    seg2 = " ".join(words[10:14])

    ds_dir = tmp_path / "datasheets"
    ds_dir.mkdir()
    shutil.copy(PDF_DIR / "LM2596-ADJ.pdf", ds_dir / "LM2596-ADJ.pdf")

    good = _finding(ref, net, summary=f"{ref} elided-quote finding on {net}")
    good["evidence"]["datasheet"] = [
        {"mpn": "LM2596-ADJ", "page": 1, "quote": f"{seg1} … {seg2}"}]

    bad = _finding(ref, net, summary=f"{ref} fabricated-quote finding on {net}")
    bad["evidence"]["datasheet"] = [
        {"mpn": "LM2596-ADJ", "page": 1,
         "quote": f"{seg1} ... this text is not on the page zzqx nowhere"}]

    dr_path = tmp_path / "deep_review.json"
    dr_path.write_text(json.dumps(_doc([good, bad])))

    r = _run_gate(dr_path, analysis_d, "--datasheets-dir", str(ds_dir))
    assert r.returncode == 1, r.stdout + r.stderr
    out = json.loads(dr_path.read_text())
    assert len(out["findings"]) == 1
    assert out["findings"][0]["summary"] == good["summary"]
    assert len(out["quarantined"]) == 1
    reason = out["quarantined"][0]["quarantine_reason"]
    assert "quote not found" in reason
    assert "nearest match" in reason
