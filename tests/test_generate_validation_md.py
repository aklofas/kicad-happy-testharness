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
    assert "| FND |" not in md   # aspirational: outside the total, outside the rows (TH-079)


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


def test_missing_evidence_path_is_an_error(tmp_path):
    """code A5-F7 / arch A3-F7: a mistyped --check-results path published "100%"."""
    import pytest
    with pytest.raises(FileNotFoundError):
        gvm._load_check_results(tmp_path / "nope.json")
    with pytest.raises(FileNotFoundError):
        gvm._load_gate_rollup(tmp_path / "nope.json")
    assert gvm._load_check_results(None) is None


def test_category_rows_share_the_total_denominator():
    """TH-079: the category rows counted aspirational results the total excludes."""
    results = {"total": 3, "passed": 2, "failed": 1, "errors": 0, "pass_rate": "66.7%",
               "results": [{"id": "SEED-1", "passed": True}, {"id": "SEED-2", "passed": False},
                           {"id": "FND-1", "passed": True}, {"id": "FND-2", "passed": False,
                                                              "aspirational": True}]}
    stats = gvm._measured_assertion_stats(results)
    assert sum(stats["by_type"].values()) == stats["total"] == 3
    md = gvm.generate_markdown(check_results=results)
    assert "| SEED | 2 | 50.0% |" in md and "| FND | 1 | 100.0% |" in md
    assert "100%" not in md.split("### Crash testing")[1].split("### Regression")[0]


def test_spice_count_is_labelled_as_analyzer_runs():
    """The SPICE count is one output file per schematic run, not one per simulation."""
    md = gvm.generate_markdown(check_results=_check_results())
    assert "| SPICE simulations |" not in md
    assert "| SPICE analyzer runs |" in md
    assert "Python 3.10+" in md and "Python 3.8" not in md


def test_issue_counts_read_both_heading_formats(tmp_path, monkeypatch):
    """TH-104: FIXED.md entries headed `## <date> — TH-NNN` were not counted, so the
    filed total shrank as open issues closed."""
    issues = tmp_path / "ISSUES.md"
    fixed = tmp_path / "FIXED.md"
    issues.write_text(
        "## Test Harness Issues\n\n"
        "### TH-010: open one\n\n"
        "### TH-012: open two, narrowed in FIXED.md\n\n"
        "### KH-247 (HIGH): TH-001/PDN rule id in the title\n", encoding="utf-8")
    fixed.write_text(
        "## 2026-11-03 — TH-011: dated heading\n\n"
        "### TH-003: old heading\n\n"
        "## 2026-10-01 — TH-012: half fixed\n\n"
        "### TH-004 (LOW) / TH-005 (LOW): two ids\n\n"
        "## Pre-2026-03-13 — Earlier fixes (KH-001 through KH-011, TH-001 through TH-006)\n",
        encoding="utf-8")
    monkeypatch.setattr(gvm, "ISSUES_FILE", issues)
    monkeypatch.setattr(gvm, "FIXED_FILE", fixed)
    assert gvm._count_th_issues() == (2, 4, 12)
    assert gvm._count_kh_issues() == (1, 0, 247)


def test_gate_paragraph_names_the_wave_chained_baseline():
    md = gvm.generate_markdown(check_results=_check_results(),
                               gate_rollup=_rollup(clean=True))
    gate = md.split("### Layer 1 regression gate (pre-tag requirement)\n\n")[1]
    assert gate.startswith(
        "Before any release is tagged, the harness runs the candidate over the full corpus "
        "and diffs every analyzer envelope unit by unit against a baseline: the previous "
        "release, or, for a release built in gated waves, the previous accepted candidate "
        "of each wave.")


def test_version_table_note_counts_multi_version_and_uncounted_repos(tmp_path, monkeypatch):
    import json
    catalog = [{"kicad_versions": ["8.0", "8.99"]},      # two strings, both KiCad 8
               {"kicad_versions": ["6.0", "9.0"]},
               {"kicad_versions": ["7.0"]},
               {"kicad_versions": ["unknown"]},
               {"kicad_versions": []},
               {"kicad_versions": ["4.0"]}]
    path = tmp_path / "repo_catalog.json"
    path.write_text(json.dumps(catalog))
    monkeypatch.setattr(gvm, "CATALOG_FILE", path)
    md = gvm.generate_markdown(check_results=_check_results())
    assert "| KiCad 8 | 2 |" in md
    table_end = md.split("**KiCad version distribution:**")[1].split("**Category distribution:**")[0]
    assert ("A repo is counted once for each KiCad version string found in its files, so "
            "the 2 repos that hold files from more than one version appear in more than one "
            "row (KiCad 8.0 and 8.99 both count under KiCad 8); the 3 repos whose version "
            "the harness catalog records as unknown, empty or older than KiCad 5 are not "
            "counted.") in table_end
