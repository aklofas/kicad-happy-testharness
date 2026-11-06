"""tools/generate_analytics.py issue counts read both heading formats (TH-106)."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import generate_analytics as ga  # noqa: E402
import generate_validation_md as gvm  # noqa: E402


def test_issue_counts_read_both_heading_formats_and_body_severity(tmp_path, monkeypatch):
    issues = tmp_path / "ISSUES.md"
    fixed = tmp_path / "FIXED.md"
    issues.write_text("### KH-010: open\n\n**Severity:** LOW\n\n### TH-020: open\n\n**Severity:** LOW\n",
                      encoding="utf-8")
    fixed.write_text(
        "## 2026-11-03 — KH-011: dated heading\n\n**Severity:** HIGH (why)\n\n"
        "### KH-012 (MEDIUM) / KH-013 (LOW): old heading, severities in it\n\n"
        "## 2026-10-01 — KH-010: a fixed half of an open issue\n\n**Severity:** HIGH\n\n"
        "## 2026-11-04 — TH-021: dated TH\n\n**Severity:** LOW\n", encoding="utf-8")
    monkeypatch.setattr(gvm, "ISSUES_FILE", issues)
    monkeypatch.setattr(gvm, "FIXED_FILE", fixed)
    kh_closed, th_closed, by_sev = ga.collect_issue_data()
    assert (kh_closed, th_closed) == (3, 1)
    assert by_sev == {"HIGH": 1, "MEDIUM": 1, "LOW": 1}
    assert ga.collect_open_issues() == (1, 1)
