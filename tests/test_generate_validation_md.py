"""tools/generate_validation_md.py — the measured run_checks total is
authoritative, the gate section is release-agnostic, and output-file counts
exclude the capability_mode.json sidecars (v2.3.0 ship handoff, 2026-10-04:
VALIDATION.md needed a manual post-process at 4cdff1b)."""

TIER = "unit"

import sys
import tempfile
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HARNESS / "tools"))

import generate_validation_md as gvm  # noqa: E402


def _check_results():
    results = [
        {"id": "SEED-0001", "passed": True},
        {"id": "SEED-0002", "passed": True},
        {"id": "STRUCT-0001", "passed": True},
        {"id": "BUGFIX-KH-001-01", "passed": True},
        {"id": "FND-00000001-AST-01", "passed": False, "aspirational": True},
    ]
    return {"total": 1234567, "passed": 1234560, "failed": 7, "errors": 0,
            "pass_rate": "100.0%", "results": results}


def _rollup(clean):
    return {"section": "vX_full", "total_units": 170014,
            "totals": {"PASS": 1, "FAIL": 0 if clean else 5, "Disappeared": 0,
                       "Downgrades": 0, "Upgrades": 0, "NewKnown": 0,
                       "NewUpgraded": 0, "NewUnknown": 0, "WARN": 0, "SKIP": 0},
            "pass_criteria": {"clean": clean}}


def test_measured_total_is_authoritative_over_catalog():
    md = gvm.generate_markdown(check_results=_check_results())
    assert "| **Total** | **1,234,567** |" in md
    assert "| Regression assertions | 1,234,567 at 100.0% |" in md


def test_assertion_breakdown_comes_from_measured_results():
    md = gvm.generate_markdown(check_results=_check_results())
    assert "| SEED | 2 |" in md
    assert "| STRUCT | 1 |" in md
    assert "| BUGFIX | 1 |" in md
    assert "| FND | 1 |" in md


def test_gate_section_is_release_agnostic():
    md = gvm.generate_markdown(check_results=_check_results(),
                               gate_rollup=_rollup(clean=True))
    assert "### Layer 1 regression gate (pre-tag requirement)" in md
    assert "v1.4" not in md.split("### Layer 1 regression gate")[1].split("## Signal")[0]
    assert "Verdict: **CLEAN**" in md


def test_gate_label_and_verdict_are_injected():
    md = gvm.generate_markdown(
        check_results=_check_results(), gate_rollup=_rollup(clean=False),
        gate_label="the v9.9.9 batch gate (`aaaaaaa` → `bbbbbbb`, `results/x/adjudication.md`)",
        gate_verdict="CLEAN under the batch budget — every moved unit attributed")
    assert "the v9.9.9 batch gate (`aaaaaaa` → `bbbbbbb`" in md
    assert "Verdict: **CLEAN under the batch budget — every moved unit attributed**" in md


def test_budgeted_rollup_without_verdict_is_refused():
    try:
        gvm.generate_markdown(check_results=_check_results(),
                              gate_rollup=_rollup(clean=False))
    except ValueError as e:
        assert "gate-verdict" in str(e)
    else:
        raise AssertionError("non-clean rollup without an explicit verdict must raise")


def test_output_file_count_excludes_sidecars_and_aggregates():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "schematic" / "owner" / "repo"
        d.mkdir(parents=True)
        for name in ("a.kicad_sch.json", "b.sch.json", "_autosave-c.kicad_sch.json",
                     "capability_mode.json", "_timing.json", "_aggregate.json",
                     "_aggregate_phase1.json", "a.kicad_sch.err"):
            (d / name).write_text("{}")
        saved = gvm.OUTPUTS_DIR
        gvm.OUTPUTS_DIR = Path(td)
        try:
            assert gvm._count_output_files("schematic") == 3
        finally:
            gvm.OUTPUTS_DIR = saved


if __name__ == "__main__":
    import traceback
    ok = fail = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                ok += 1
            except Exception:  # noqa: BLE001
                fail += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)
