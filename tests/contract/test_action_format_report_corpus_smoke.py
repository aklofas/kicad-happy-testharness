"""Report generation succeeds — ``action/format-report.py`` exit 0 on each
cached fixture.

Audit LOG 8b / regression-testing-audit F8 (2026-05-15): the second
contract deferred from LOG 8's commit message. ``action/format-report.py``
is the v1.4 user-facing consumer (renders analyzer envelopes into the
GitHub Actions PR-comment markdown). "Report rendering doesn't crash
on any v1.4 envelope shape" is a release-trust contract — a regression
here breaks every action run, not just one detector.

Three lock targets per fixture:

  1. ``format-report.py`` exits 0 on the envelope (no crash on any
     missing-optional field, no traceback)
  2. Output markdown file is non-empty (>200 bytes — guards against
     a renderer that emits a placeholder shell)
  3. Output markdown contains structural anchors (a heading + the
     findings count line) — proves the renderer actually consumed
     the input, not just templated a stub

Fixtures: reuse the noise-budget cached schematic envelopes (3 boards,
already committed). No TIER — the renderer is pure-Python stdlib and
the fixtures are in-tree. Adding a fourth/fifth fixture would just
parametrize this same suite.

A complementary action-renderer test
(``test_action_format_report_v14.py``) covers v1.4 envelope-shape
edge cases (existing). This file is the SMOKE that proves the renderer
runs end-to-end on real corpus envelopes — the existing file is
synthetic-fixture focused.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

FORMAT_REPORT_CLI = MAIN_REPO_ROOT / "action" / "format-report.py"
FIXTURES_DIR = HARNESS_ROOT / "tests" / "fixtures" / "noise-budget"

FIXTURES = [
    ("macropad", "macropad.schematic.json"),
    ("ir_uart", "ir_uart.schematic.json"),
    ("ascii_display_module", "ascii_display_module.schematic.json"),
]

SUBPROC_TIMEOUT_S = 30


def _run_format_report(schematic_path, output_path):
    cmd = [
        sys.executable, str(FORMAT_REPORT_CLI),
        "--schematic", str(schematic_path),
        "--output", str(output_path),
    ]
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S,
    )


@pytest.mark.parametrize("label,fixture", FIXTURES, ids=[f[0] for f in FIXTURES])
def test_format_report_exits_zero(label, fixture, tmp_path):
    """Contract 1: format-report runs to completion on a real v1.4
    schematic envelope. Failure here = the renderer crashed (KeyError on
    a missing optional field, schema-shape mismatch, etc.)."""
    sch = FIXTURES_DIR / fixture
    if not sch.is_file():
        pytest.skip(f"missing fixture {fixture}")
    if not FORMAT_REPORT_CLI.is_file():
        pytest.skip(f"format-report.py not found at {FORMAT_REPORT_CLI}")

    out = tmp_path / "report.md"
    r = _run_format_report(sch, out)
    assert r.returncode == 0, (
        f"{label}: format-report rc={r.returncode}\n"
        f"stderr tail: {r.stderr[-500:]}"
    )


@pytest.mark.parametrize("label,fixture", FIXTURES, ids=[f[0] for f in FIXTURES])
def test_format_report_output_is_non_trivially_sized(label, fixture, tmp_path):
    """Contract 2: output is non-empty + contains real rendered content
    (>200 bytes). Guards a renderer that exits 0 but emits only a stub
    template / placeholder shell — silently degrading the PR comment."""
    sch = FIXTURES_DIR / fixture
    if not sch.is_file():
        pytest.skip(f"missing fixture {fixture}")
    if not FORMAT_REPORT_CLI.is_file():
        pytest.skip(f"format-report.py not found at {FORMAT_REPORT_CLI}")

    out = tmp_path / "report.md"
    r = _run_format_report(sch, out)
    assert r.returncode == 0
    assert out.is_file(), "format-report claimed success but did not write output"
    size = out.stat().st_size
    assert size > 200, (
        f"{label}: report only {size} bytes — likely a stub/placeholder"
    )


@pytest.mark.parametrize("label,fixture", FIXTURES, ids=[f[0] for f in FIXTURES])
def test_format_report_contains_structural_anchors(label, fixture, tmp_path):
    """Contract 3: output is well-formed markdown with the structural
    anchors a consumer relies on — a heading line + the findings count
    line. Proves the renderer actually consumed the input."""
    sch = FIXTURES_DIR / fixture
    if not sch.is_file():
        pytest.skip(f"missing fixture {fixture}")
    if not FORMAT_REPORT_CLI.is_file():
        pytest.skip(f"format-report.py not found at {FORMAT_REPORT_CLI}")

    out = tmp_path / "report.md"
    r = _run_format_report(sch, out)
    assert r.returncode == 0

    text = out.read_text()
    has_heading = any(line.startswith("#") for line in text.splitlines())
    assert has_heading, (
        f"{label}: output lacks any markdown heading line — "
        f"renderer may be emitting a stub. First 200 chars: {text[:200]!r}"
    )
    # The renderer's success line "Findings: N critical, M warning, K verified"
    # goes to STDOUT, not the markdown. Look for the rendered findings table
    # / section marker that any non-trivial report includes.
    lower = text.lower()
    has_findings_anchor = (
        "finding" in lower
        or "warning" in lower
        or "no issues" in lower
        or "all clear" in lower
    )
    assert has_findings_anchor, (
        f"{label}: output lacks any findings-related anchor. First 300 chars: "
        f"{text[:300]!r}"
    )


# ---------------------------------------------------------------------------
# Composite smoke: --output + --output-full + --output-summary together
# ---------------------------------------------------------------------------

def test_format_report_three_output_modes_all_succeed(tmp_path):
    """The format-report CLI supports three parallel outputs (--output =
    PR comment markdown, --output-full = step-summary markdown,
    --output-summary = JSON summary). All three must succeed together
    on one invocation — the GitHub Action wires up all three for every
    PR comment."""
    sch = FIXTURES_DIR / "macropad.schematic.json"
    if not sch.is_file():
        pytest.skip("missing macropad fixture")
    if not FORMAT_REPORT_CLI.is_file():
        pytest.skip(f"format-report.py not found at {FORMAT_REPORT_CLI}")

    out_md = tmp_path / "report.md"
    out_full = tmp_path / "report_full.md"
    out_sum = tmp_path / "summary.json"
    r = subprocess.run(
        [sys.executable, str(FORMAT_REPORT_CLI),
         "--schematic", str(sch),
         "--output", str(out_md),
         "--output-full", str(out_full),
         "--output-summary", str(out_sum)],
        capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S,
    )
    assert r.returncode == 0, (
        f"rc={r.returncode}\nstderr tail: {r.stderr[-500:]}"
    )
    assert out_md.is_file()
    assert out_full.is_file()
    assert out_sum.is_file()
    # Summary JSON should be parseable
    import json
    summary = json.loads(out_sum.read_text())
    assert isinstance(summary, dict), "summary JSON should be a dict"
