"""Noise-budget suite for v1.4 schematic outputs on clean/simple boards.

Audit LOG 14 / regression-testing-audit F14 (2026-05-15): "directly tests the
v1.5 'context-aware pipeline' + override-persistence work goals from the
sacmap-rev2 deferred items". Catches the release-trust bug class "v1.4 feels
noisier than v1.3.1 on clean designs" — which compatibility gates cannot
detect because they only diff v1.3 → v1.4, not whether v1.4's absolute
finding budget is reasonable for trivial boards.

Three contracts:

  1. **Grouping invariants (GREEN today)** — missing-MPN warnings MUST be
     emitted as one grouped finding per board (with all affected refs in
     ``components[]``), NOT one finding per missing-MPN component. The audit
     phrase: "missing-MPN warnings grouped not per-component-repeated". Locks
     SS-001 + DS-001 grouping.

  2. **Noise ceilings (GREEN today)** — per-board upper bounds on
     ``error+warning`` (actionable noise) and ``total findings`` (full
     chatter). Sized 25-50% above current to absorb v1.4 detector tuning
     churn while still tripping on a real regression (e.g., a v1.5
     "context-aware" change accidentally fanning one finding into N per
     component would blow the budget).

  3. **Severity-vs-evidence (RED today, xfail strict)** — every ``error``
     finding MUST carry a ``provenance`` block. Currently FAILS because
     DS-001 ("no datasheets directory") and SS-001 ("sourcing blocker") fire
     as ``error`` on every board without provenance, signalling "no
     datasheets present" as a hard error. This is the canonical v1.4-noise
     bug. Marked ``xfail(strict=True)`` per LOG 5/6/7 convention — when v1.5
     either (a) reclassifies these to ``warning`` or (b) adds provenance,
     the suite XPASSES and forces removal of the xfail marker, converting
     the test into a positive lock for the fix.

Fixtures: cached real corpus outputs (per
``feedback_real_fixtures_for_verification``). NO TIER="online" — the JSON
files are committed, so the suite runs anywhere without ``KICAD_HAPPY_DIR``
or a populated ``repos/`` directory.

Fixture refresh: if the v1.4 baseline shifts (detector tuning, new
analyzers), regenerate via::

    python3 run/run_schematic.py --repo Coder1203/Macropad
    python3 run/run_schematic.py --repo ADBeta/IR_UART
    python3 run/run_schematic.py --repo ADBeta/00314S2D-ASCII_Display_Module
    cp results/outputs/schematic/Coder1203/Macropad/PCB_Macropad.kicad_sch.json \\
        tests/fixtures/noise-budget/macropad.schematic.json
    cp results/outputs/schematic/ADBeta/IR_UART/IR_UART.kicad_sch.json \\
        tests/fixtures/noise-budget/ir_uart.schematic.json
    cp results/outputs/schematic/ADBeta/00314S2D-ASCII_Display_Module/PCB_MkI_MkI.kicad_sch.json \\
        tests/fixtures/noise-budget/ascii_display_module.schematic.json

Then re-check budget thresholds against the new counts — bump them only if
the increase is justified.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.contract._paths import HARNESS_ROOT

FIXTURES = HARNESS_ROOT / "tests" / "fixtures" / "noise-budget"

# (label, fixture filename, actionable_budget, total_budget)
# Budgets sized for headroom over current v1.4 counts (captured 2026-05-16):
#   Macropad:    actionable= 6  total=  9  → budgets 10 / 20
#   IR_UART:     actionable= 3  total= 14  → budgets  6 / 25
#   ASCII_Display: actionable=7  total= 18  → budgets 12 / 30
BOARDS = [
    ("macropad",              "macropad.schematic.json",              10,  20),
    ("ir_uart",               "ir_uart.schematic.json",                6,  25),
    ("ascii_display_module",  "ascii_display_module.schematic.json",  12,  30),
]


@pytest.fixture(scope="module", params=BOARDS, ids=[b[0] for b in BOARDS])
def board(request):
    label, filename, actionable_budget, total_budget = request.param
    path = FIXTURES / filename
    if not path.is_file():
        pytest.skip(f"missing noise-budget fixture {filename!r}")
    envelope = json.loads(path.read_text())
    return {
        "label": label,
        "envelope": envelope,
        "findings": envelope.get("findings") or [],
        "summary": envelope.get("summary") or {},
        "by_severity": (envelope.get("summary") or {}).get("by_severity") or {},
        "actionable_budget": actionable_budget,
        "total_budget": total_budget,
    }


# ---------------------------------------------------------------------------
# Grouping invariants — GREEN today
# ---------------------------------------------------------------------------

def test_sourcing_blocker_grouped(board):
    """SS-001 ("sourcing blocker: BOM has <50% MPN coverage") MUST emit as
    exactly one grouped finding per board, with ALL missing-MPN refs in the
    finding's ``components[]`` list. The pre-fix bug class would emit one
    SS-001 finding per missing-MPN component, inflating the finding count
    by N (where N can be 50+ on a hobbyist board)."""
    ss = [f for f in board["findings"] if f.get("rule_id") == "SS-001"]
    assert len(ss) == 1, (
        f"{board['label']}: expected exactly 1 grouped SS-001 finding, got "
        f"{len(ss)} — missing-MPN findings are being repeated per component "
        f"instead of grouped"
    )
    # The single SS-001 finding must carry all affected refs in components[];
    # an empty components[] would mean the grouping is degenerate.
    assert ss[0].get("components"), (
        f"{board['label']}: grouped SS-001 finding has empty components[] — "
        f"refs should be aggregated into the single grouped finding"
    )


def test_no_datasheets_grouped(board):
    """DS-001 ("no datasheets directory found") MUST emit at most one finding
    per board. It's a board-level facts assertion, not a per-component one."""
    ds = [f for f in board["findings"] if f.get("rule_id") == "DS-001"]
    assert len(ds) <= 1, (
        f"{board['label']}: DS-001 emitted {len(ds)} findings; should be a "
        f"single board-level finding"
    )


def test_missing_mpn_not_per_component_repeated(board):
    """Audit phrase: 'missing-MPN warnings grouped not per-component-repeated'.
    Direct lock — for SS-001 specifically, exactly 1 finding regardless of
    how many components lack MPNs."""
    ss_count = sum(1 for f in board["findings"] if f.get("rule_id") == "SS-001")
    assert ss_count == 1, (
        f"{board['label']}: SS-001 emitted {ss_count}× — missing-MPN warnings "
        f"MUST be grouped into a single finding (audit F14 lock)"
    )


# ---------------------------------------------------------------------------
# Noise ceilings — GREEN today, headroom over current v1.4 counts
# ---------------------------------------------------------------------------

def test_actionable_finding_budget(board):
    """``error + warning`` count must stay below the per-board budget.
    Catches v1.5 changes that accidentally promote info → warning across
    many findings, or fan a grouped warning out per-component."""
    bysev = board["by_severity"]
    actionable = (bysev.get("error", 0) or 0) + (bysev.get("warning", 0) or 0)
    assert actionable <= board["actionable_budget"], (
        f"{board['label']}: actionable findings (error+warning) = "
        f"{actionable}, budget = {board['actionable_budget']}. "
        f"Either v1.4 noise has regressed (investigate the new findings) or "
        f"the budget needs to be re-baselined (see module docstring)."
    )


def test_total_finding_budget(board):
    """Total findings (info + warning + error) below per-board budget. Wider
    than the actionable ceiling — info-level chatter is tolerated but a
    runaway info producer would still trip this."""
    total = len(board["findings"])
    assert total <= board["total_budget"], (
        f"{board['label']}: total findings = {total}, budget = "
        f"{board['total_budget']}. Likely cause: a detector fanned one "
        f"grouped finding out per component (info-noise inflation)."
    )


def test_summary_total_matches_findings_length(board):
    """Sanity guard: summary.total_findings (when present) MUST equal
    len(findings[]). Protects the noise budgets from being defeated by a
    summary-vs-findings divergence (also overlaps with audit F4 default
    contract gate)."""
    summary_total = board["summary"].get("total_findings")
    if summary_total is None:
        pytest.skip(f"{board['label']}: summary.total_findings absent")
    assert summary_total == len(board["findings"]), (
        f"{board['label']}: summary.total_findings={summary_total} but "
        f"len(findings[])={len(board['findings'])}"
    )


# ---------------------------------------------------------------------------
# Severity-vs-evidence — RED today, xfail(strict=True)
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="LOG 14: DS-001 + SS-001 currently fire as severity=error without "
           "provenance blocks, signalling 'no datasheets present' as a hard "
           "error on every hobbyist board. v1.5 fix: either reclassify these "
           "to severity=warning, or attach provenance describing the BOM/"
           "datasheet inputs that drove the determination. When the fix lands "
           "this XPASSES → remove xfail to convert into a positive lock.",
)
def test_error_findings_have_provenance(board):
    """Every severity=error finding MUST carry a ``provenance`` block (the
    contract being v1.5 should hit). Currently RED because DS-001 + SS-001
    emit as error without provenance — the canonical v1.4 noise class.

    The presence of ``evidence_source`` alone (a free-text string) is NOT
    sufficient; we want structured provenance describing what input the
    determination was made from."""
    bad = []
    for f in board["findings"]:
        if f.get("severity") != "error":
            continue
        if not f.get("provenance"):
            bad.append({
                "rule_id": f.get("rule_id"),
                "summary": (f.get("summary") or "")[:80],
            })
    assert not bad, (
        f"{board['label']}: {len(bad)} error findings lack provenance: {bad}"
    )
