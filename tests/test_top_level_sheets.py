"""Regression test for top_level_sheets multi-page Altium imports.

Validates analyze_schematic.py merges all pages declared in
``.kicad_pro``'s ``schematic.top_level_sheets`` — including power
symbols — and leaves non-Altium projects alone.

Bug guard: PR #19's first revision extended ``parsed['components']``
from the peer sheets but never refreshed ``parsed['power_symbols']``,
silently dropping every power symbol from peer pages.

Fixtures
--------
- ``synthetic_top_level_sheets/``  3-page Altium-flat project
    synthetic.kicad_pro            top_level_sheets: [page1, page2, page3]
    page{1,2,3}.kicad_sch          3 components + 2 power symbols each
- ``simple-project/``               single-sheet, no top_level_sheets in
                                    .kicad_pro — covers the "single-sheet
                                    project (no .kicad_pro top_level_sheets)"
                                    test-plan item

Hierarchical-project regression (test-plan item 1) is covered at corpus
scope: the 422 schematics in the 45 affected repos all produced
semantically-identical output on pr-19 vs main, so existing hierarchical
projects are unaffected. No tracked hierarchical fixture exists in
tests/fixtures/ to assert against in this unit test.
"""
from __future__ import annotations

TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
KH_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy")))
ANALYZER = KH_DIR / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
KH_PYTHON = KH_DIR / ".venv" / "bin" / "python"

FIXTURE_ROOT = HARNESS_DIR / "tests" / "fixtures"
SYNTHETIC_PAGE1 = FIXTURE_ROOT / "synthetic_top_level_sheets" / "page1.kicad_sch"
SIMPLE_SCH = FIXTURE_ROOT / "simple-project" / "simple.kicad_sch"


def _python() -> str:
    """Prefer the kicad-happy venv python if present (jsonschema available)."""
    return str(KH_PYTHON) if KH_PYTHON.exists() else sys.executable


def _run_analyzer(sch_path: Path) -> tuple[dict, str] | None:
    """Run analyze_schematic.py on a schematic.

    Returns ``(envelope, stderr_text)``, or ``None`` if the analyzer or
    fixture is missing (test will SKIP).
    """
    if not ANALYZER.exists() or not sch_path.exists():
        return None
    proc = subprocess.run(
        [_python(), str(ANALYZER), str(sch_path)],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"analyzer failed (exit {proc.returncode}): {proc.stderr[:400]}")
    return json.loads(proc.stdout), proc.stderr


# ─── synthetic 3-page Altium-flat project — merge path active ─────────────

def test_merge_path_fires_and_sheets_count_is_three():
    """Envelope ``sheets`` lists all three pages — merge happened."""
    result = _run_analyzer(SYNTHETIC_PAGE1)
    if result is None:
        print("  SKIP: analyzer or fixture missing")
        return
    env, stderr = result
    assert "discovered 2 additional top-level sheets" in stderr, \
        f"expected merge-notice in stderr, got: {stderr[:200]!r}"
    sheets = env.get("sheets")
    assert isinstance(sheets, list), \
        f"envelope.sheets missing or not a list: {type(sheets).__name__}"
    assert len(sheets) == 3, \
        f"expected 3 sheets after merge, got {len(sheets)}: {sheets}"


def test_components_merged_from_all_pages():
    """All three pages contribute components — peer sheets are not dropped."""
    result = _run_analyzer(SYNTHETIC_PAGE1)
    if result is None:
        print("  SKIP")
        return
    env, _ = result
    comps = env.get("components", [])
    assert len(comps) == 9, \
        f"expected 9 components (3 per page × 3 pages), got {len(comps)}"
    sheets = sorted({c.get("_sheet") for c in comps})
    assert sheets == [0, 1, 2], \
        f"components should cover all 3 sheets, got sheets={sheets}"


def test_power_symbols_refreshed_after_peer_merge():
    """power_symbols includes peer-sheet symbols, not just the root sheet.

    Pre-fix, this returned 2 (only root sheet GND/+5V), missing the
    4 power symbols on pages 2-3.
    """
    result = _run_analyzer(SYNTHETIC_PAGE1)
    if result is None:
        print("  SKIP")
        return
    env, _ = result
    ps = env.get("power_symbols", [])
    assert len(ps) == 6, (
        f"expected 6 power_symbols (2 per page × 3 pages), got {len(ps)} — "
        f"likely missing power_symbols refresh after extra-sheet merge")
    sheets = sorted({p.get("_sheet") for p in ps})
    assert sheets == [0, 1, 2], (
        f"power_symbols should cover all 3 sheets, got sheets={sheets} — "
        f"peer-sheet power symbols dropped during merge")


# ─── single-sheet project (no top_level_sheets) — merge path skipped ─────

def test_single_sheet_no_top_level_sheets_skips_merge():
    """Project with no ``top_level_sheets`` in .kicad_pro: guard skips merge.

    Verifies the new code path does not interfere with a normal
    single-sheet project. The stderr ``discovered N additional`` notice
    must NOT appear; component / power-symbol counts must match the
    single-sheet baseline (3 components, 2 power symbols).
    """
    result = _run_analyzer(SIMPLE_SCH)
    if result is None:
        print("  SKIP")
        return
    env, stderr = result
    assert "additional top-level sheets" not in stderr, (
        f"merge path should not fire on simple-project (no top_level_sheets); "
        f"stderr leaked merge-notice: {stderr[:200]!r}")
    n_comps = len(env.get("components", []))
    assert n_comps == 3, (
        f"simple-project single-sheet baseline: expected 3 components "
        f"(R/LED/J), got {n_comps} — merge may have wrongly fired")
    n_ps = len(env.get("power_symbols", []))
    assert n_ps == 2, (
        f"simple-project single-sheet baseline: expected 2 power symbols "
        f"(GND/+5V), got {n_ps}")


KNOWN_FAILURES: dict[str, str] = {}


# ─── custom-runner __main__ block (harness convention) ──────────────────

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = xfailed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            if name in KNOWN_FAILURES:
                passed += 1
                print(f"  XPASS (remove from KNOWN_FAILURES, "
                      f"{KNOWN_FAILURES[name]} may be fixed): {name}")
            else:
                passed += 1
                print(f"  PASS: {name}")
        except (AssertionError, Exception) as e:
            if name in KNOWN_FAILURES:
                xfailed += 1
                print(f"  XFAIL ({KNOWN_FAILURES[name]}): {name}: "
                      f"{type(e).__name__}: {e}")
            else:
                failed += 1
                print(f"  FAIL: {name}: {type(e).__name__}: {e}")
    total = passed + failed + xfailed
    print(f"\n{passed} passed, {failed} failed, {xfailed} xfailed "
          f"({total} total)")
    sys.exit(1 if failed else 0)
