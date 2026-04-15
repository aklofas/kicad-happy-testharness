"""Smoke tests for kicad-happy downstream tools."""

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
KICAD_HAPPY = os.environ.get(
    "KICAD_HAPPY_DIR",
    str(HARNESS_DIR.parent / "kicad-happy"),
)
FORMAT_REPORT = os.path.join(KICAD_HAPPY, "action", "format-report.py")
FAB_GATE = os.path.join(KICAD_HAPPY, "skills", "kicad", "scripts", "fab_release_gate.py")
SUMMARIZE = os.path.join(KICAD_HAPPY, "skills", "kicad", "scripts", "summarize_findings.py")
EXPORT_ISSUES = os.path.join(KICAD_HAPPY, "skills", "kicad", "scripts", "export_issues.py")


def _make_schematic():
    """Schematic output: mixed trust, 10 findings, BOM, some provenance."""
    return {
        "analyzer_type": "schematic",
        "summary": {"total_findings": 10, "by_severity": {"warning": 5, "info": 5}},
        "findings": [
            {"detector": "detect_voltage_dividers", "rule_id": "VD-DET",
             "severity": "info", "confidence": "deterministic",
             "evidence_source": "topology", "summary": f"Divider {i}",
             "description": "test", "category": "signal", "components": [f"R{i}"],
             "nets": [], "pins": [], "recommendation": "",
             "report_context": {"section": "Signal", "impact": "", "standard_ref": ""},
             "provenance": {"evidence": "vd_test", "confidence": "deterministic",
                            "claimed_components": [], "excluded_by": [],
                            "suppressed_candidates": []}}
            for i in range(7)
        ] + [
            {"detector": "suggest_certifications", "rule_id": "CERT-001",
             "severity": "info", "confidence": "heuristic",
             "evidence_source": "topology", "summary": f"Cert {i}",
             "description": "test", "category": "certification", "components": [],
             "nets": [], "pins": [], "recommendation": "",
             "report_context": {"section": "Certification", "impact": "", "standard_ref": ""}}
            for i in range(3)
        ],
        "trust_summary": {
            "total_findings": 10,
            "trust_level": "mixed",
            "by_confidence": {"deterministic": 7, "heuristic": 3, "datasheet-backed": 0},
            "by_evidence_source": {"datasheet": 0, "topology": 10, "heuristic_rule": 0,
                                   "symbol_footprint": 0, "bom": 0, "geometry": 0, "api_lookup": 0},
            "provenance_coverage_pct": 70.0,
            "bom_coverage": {"total_components": 5, "with_mpn": 2, "with_datasheet": 1,
                             "mpn_pct": 40.0, "datasheet_pct": 20.0},
        },
        "statistics": {"total_components": 5},
        "components": [], "bom": [], "nets": {},
    }


def _make_pcb():
    """PCB output: high trust, 5 findings."""
    return {
        "analyzer_type": "pcb",
        "summary": {"total_findings": 5, "by_severity": {"info": 5}},
        "findings": [
            {"detector": "analyze_thermal_pad_vias", "rule_id": "AL-DET",
             "severity": "info", "confidence": "deterministic",
             "evidence_source": "geometry", "summary": f"Pad {i}",
             "description": "test", "category": "assembly", "components": [f"U{i}"],
             "nets": [], "pins": [], "recommendation": "",
             "report_context": {"section": "Assembly", "impact": "", "standard_ref": ""}}
            for i in range(5)
        ],
        "trust_summary": {
            "total_findings": 5,
            "trust_level": "high",
            "by_confidence": {"deterministic": 5, "heuristic": 0, "datasheet-backed": 0},
            "by_evidence_source": {"datasheet": 0, "topology": 0, "heuristic_rule": 0,
                                   "symbol_footprint": 0, "bom": 0, "geometry": 5, "api_lookup": 0},
            "provenance_coverage_pct": 0.0,
        },
        "statistics": {"footprint_count": 5, "routing_complete": True},
        "footprints": [], "board_outline": {"width_mm": 50, "height_mm": 50},
    }


def _make_empty():
    """Pre-Batch-16 output: no trust_summary."""
    return {
        "analyzer_type": "schematic",
        "summary": {"total_findings": 0, "by_severity": {}},
        "findings": [],
        "statistics": {"total_components": 0},
        "components": [], "bom": [], "nets": {},
    }


def _write_json(data, tmpdir, name):
    path = os.path.join(tmpdir, name)
    with open(path, "w") as f:
        json.dump(data, f)
    return path


def _run(args, **kwargs):
    return subprocess.run(
        [sys.executable] + args,
        capture_output=True, text=True, timeout=30, **kwargs)


# === format-report.py ===

def test_format_report_no_crash():
    with tempfile.TemporaryDirectory() as td:
        sch = _write_json(_make_schematic(), td, "sch.json")
        out = os.path.join(td, "report.md")
        r = _run([FORMAT_REPORT, "--schematic", sch, "--severity", "all", "--output", out])
        assert r.returncode == 0, f"Crash: {r.stderr[:300]}"
        assert os.path.exists(out)


def test_format_report_trust_section_present():
    with tempfile.TemporaryDirectory() as td:
        sch = _write_json(_make_schematic(), td, "sch.json")
        out = os.path.join(td, "report.md")
        _run([FORMAT_REPORT, "--schematic", sch, "--severity", "all", "--output", out])
        report = open(out).read()
        assert "Trust / Evidence" in report


def test_format_report_trust_section_absent_for_empty():
    with tempfile.TemporaryDirectory() as td:
        sch = _write_json(_make_empty(), td, "sch.json")
        out = os.path.join(td, "report.md")
        _run([FORMAT_REPORT, "--schematic", sch, "--severity", "all", "--output", out])
        report = open(out).read()
        assert "Trust / Evidence" not in report


def test_format_report_icon_matches_trust_level():
    with tempfile.TemporaryDirectory() as td:
        sch = _write_json(_make_schematic(), td, "sch.json")
        out = os.path.join(td, "report.md")
        _run([FORMAT_REPORT, "--schematic", sch, "--severity", "all", "--output", out])
        report = open(out).read()
        assert "\u26a0\ufe0f" in report  # warning sign for mixed


# === fab_release_gate.py ===

def test_fab_gate_no_crash():
    with tempfile.TemporaryDirectory() as td:
        sch = _write_json(_make_schematic(), td, "sch.json")
        pcb = _write_json(_make_pcb(), td, "pcb.json")
        r = _run([FAB_GATE, "--schematic", sch, "--pcb", pcb])
        assert r.returncode == 0, f"Crash: {r.stderr[:300]}"


def test_fab_gate_trust_posture():
    with tempfile.TemporaryDirectory() as td:
        sch = _write_json(_make_schematic(), td, "sch.json")
        pcb = _write_json(_make_pcb(), td, "pcb.json")
        r = _run([FAB_GATE, "--schematic", sch, "--pcb", pcb])
        gate = json.loads(r.stdout)
        tp = gate.get("trust_posture")
        assert tp is not None, "trust_posture missing"
        assert tp["trust_level"] in ("high", "mixed", "low")
        assert tp["per_analyzer"]["schematic"] == "mixed"
        assert tp["per_analyzer"]["pcb"] == "high"


def test_fab_gate_backward_compat():
    with tempfile.TemporaryDirectory() as td:
        sch = _write_json(_make_empty(), td, "sch.json")
        pcb = _write_json(_make_pcb(), td, "pcb.json")
        r = _run([FAB_GATE, "--schematic", sch, "--pcb", pcb])
        assert r.returncode == 0, f"Crash: {r.stderr[:300]}"


# === summarize_findings.py ===

def _make_analysis_dir(td):
    """Create a temp analysis dir with manifest for summarize_findings."""
    run_dir = os.path.join(td, "run_001")
    os.makedirs(run_dir)
    sch = _make_schematic()
    with open(os.path.join(run_dir, "schematic.json"), "w") as f:
        json.dump(sch, f)
    manifest = {
        "current": "run_001",
        "runs": {"run_001": {"timestamp": "2026-04-15",
                              "files": {"schematic": "schematic.json"}}},
    }
    with open(os.path.join(td, "manifest.json"), "w") as f:
        json.dump(manifest, f)
    return td


def test_summarize_findings_default():
    with tempfile.TemporaryDirectory() as td:
        adir = _make_analysis_dir(td)
        r = _run([SUMMARIZE, adir, "--top", "5"])
        assert r.returncode == 0, f"Crash: {r.stderr[:300]}"
        assert "det" in r.stdout.lower() or "heu" in r.stdout.lower()


def test_summarize_findings_json():
    with tempfile.TemporaryDirectory() as td:
        adir = _make_analysis_dir(td)
        r = _run([SUMMARIZE, adir, "--json"])
        assert r.returncode == 0, f"Crash: {r.stderr[:300]}"
        data = json.loads(r.stdout)
        assert "by_confidence" in data["totals"]


def test_summarize_findings_by_confidence():
    with tempfile.TemporaryDirectory() as td:
        adir = _make_analysis_dir(td)
        r = _run([SUMMARIZE, adir, "--by-confidence"])
        assert r.returncode == 0, f"Crash: {r.stderr[:300]}"
        assert "deterministic" in r.stdout.lower()


# === export_issues.py ===

def test_export_issues_no_crash():
    with tempfile.TemporaryDirectory() as td:
        sch = _write_json(_make_schematic(), td, "sch.json")
        r = _run([EXPORT_ISSUES, sch, "--repo", "test/test", "--json"])
        assert r.returncode == 0, f"Crash: {r.stderr[:300]}"


def test_export_issues_confidence_labels():
    with tempfile.TemporaryDirectory() as td:
        sch = _write_json(_make_schematic(), td, "sch.json")
        r = _run([EXPORT_ISSUES, sch, "--repo", "test/test", "--json"])
        data = json.loads(r.stdout)
        for issue in data["issues"]:
            labels = issue["labels"]
            assert any(l.startswith("confidence:") for l in labels), \
                f"Missing confidence label: {labels}"
            assert any(l.startswith("evidence:") for l in labels), \
                f"Missing evidence label: {labels}"


# === Runner ===

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except (AssertionError, Exception) as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
