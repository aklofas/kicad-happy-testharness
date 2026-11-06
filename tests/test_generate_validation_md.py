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
    return {"total": 4, "passed": 4, "failed": 0, "errors": 0,
            "pass_rate": "100.0%", "results": results}


def _rollup(clean):
    return {"section": "vX_full", "total_units": 170014,
            "totals": {"PASS": 1, "FAIL": 0, "Disappeared": 0,
                       "Downgrades": 0, "Upgrades": 0, "NewKnown": 0 if clean else 5,
                       "NewUpgraded": 0, "NewUnknown": 0, "WARN": 0, "SKIP": 0},
            "pass_criteria": {"clean": clean}}


def test_measured_total_is_authoritative_over_catalog():
    md = gvm.generate_markdown(check_results=_check_results())
    assert "| **Total** | **4** | **100.0000 %** |" in md
    assert "| Regression assertions | 4 at 100.0000 % |" in md


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
    assert "| SEED | 2 | 50.0000 % |" in md and "| FND | 1 | 100.0000 % |" in md
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


# --- v3.0.2: the page must not contradict itself (attributed counters, visible failures) ---

import json  # noqa: E402

import pytest  # noqa: E402


def _results(n_pass, fails=(), errors=()):
    res = [{"id": f"SEED-{i}", "passed": True} for i in range(n_pass)]
    res += [{"id": i, "passed": False, "repo": "o/r", "file": "f.kicad_sch", "actual": 3}
            for i in fails]
    res += [{"id": i, "passed": False, "repo": "o/r", "file": "f.sch",
             "error": "output file not found"} for i in errors]
    total = len(res)
    return {"total": total, "passed": n_pass, "failed": len(fails), "errors": len(errors),
            "pass_rate": "100.0%", "results": res}


def test_pass_rate_shows_failures():
    assert gvm._pct(2717827, 2717836) == "99.9997 %"
    assert gvm._pct(9_999_999, 10_000_000) == "99.9999 %"   # never rounds up to 100 with a failure
    assert gvm._pct(5, 5) == "100.0000 %"
    md = gvm.generate_markdown(check_results=_results(3, fails=["FND-1-AST-01"]))
    assert "| **Total** | **4** | **75.0000 %** |" in md


def test_failures_are_classified_from_the_ledger(tmp_path):
    ledger = tmp_path / "led.json"
    ledger.write_text(json.dumps({"checks": [
        {"id": "FND-1-AST-01", "cause": "TH-900: stale lock, analyzer matches KiCad"},
        {"id": "FND-2-AST-01", "cause": "unreviewed"}]}))
    md = gvm.generate_markdown(
        check_results=_results(3, fails=["FND-1-AST-01", "FND-3-AST-01"], errors=["FND-2-AST-01"]),
        ledger=gvm._load_ledger(ledger))
    table = md.split("| Assertion |")[1].split("\n\n")[0]
    assert "| `FND-1-AST-01` | o/r `f.kicad_sch` | failed (actual 3) | TH-900 | stale lock, analyzer matches KiCad |" in table
    assert "| `FND-2-AST-01` | o/r `f.sch` | error: output file not found | unclassified | |" in table
    assert "| `FND-3-AST-01` | o/r `f.kicad_sch` | failed (actual 3) | unclassified | not in the baseline ledger |" in table


def test_table_total_must_equal_measured_total():
    bad = _results(3)
    bad["total"] = 5
    with pytest.raises(ValueError, match="measured total"):
        gvm.generate_markdown(check_results=bad)


def test_open_issue_lines_break_down_by_severity(tmp_path, monkeypatch):
    issues = tmp_path / "ISSUES.md"
    fixed = tmp_path / "FIXED.md"
    issues.write_text(
        "### KH-010: a\n\n**Severity:** HIGH (why)\n\n"
        "### KH-011: b\n\n**Severity:** LOW-MEDIUM\n\n"
        "### KH-012: c\n\nno severity line\n\n"
        "### KH-013 (LOW) / KH-014 (LOW): d\n\n**Severity:** LOW\n\n"
        "### TH-020: e\n\n**Severity:** MEDIUM\n", encoding="utf-8")
    fixed.write_text("## 2026-11-03 — KH-009: dated\n", encoding="utf-8")
    monkeypatch.setattr(gvm, "ISSUES_FILE", issues)
    monkeypatch.setattr(gvm, "FIXED_FILE", fixed)
    assert gvm._open_by_severity("KH") == {"HIGH": 1, "MEDIUM": 1, "LOW": 2, "unclassified": 1}
    md = gvm.generate_markdown(check_results=_results(1))
    assert ("analyzer issues (6 filed, 1 closed, 5 open: 1 HIGH, 1 MEDIUM, 2 LOW, "
            "1 unclassified; LOW-MEDIUM counts as MEDIUM)") in md
    assert "harness infrastructure issues (1 filed, 0 closed, 1 open: 1 MEDIUM)" in md
    assert "| Open issues | 5 analyzer (1 HIGH, 1 MEDIUM, 2 LOW, 1 unclassified) + 1 harness (1 MEDIUM) |" in md


def _gate_files(tmp_path, *, residual_unit=False, budget_format="stream"):
    units = [
        {"analyzer": "pcb", "unit_id": "o/r/a.kicad_pcb", "verdict": "FAIL",
         "severity_downgrades": 2, "disappeared_count": 0, "new_unknown_count": 0},
        {"analyzer": "emc", "unit_id": "o/r/a.kicad_sch", "verdict": "FAIL",
         "severity_downgrades": 0, "disappeared_count": 3, "new_unknown_count": 0},
        {"analyzer": "emc", "unit_id": "o/r/b.kicad_sch", "verdict": "WARN",
         "severity_downgrades": 0, "disappeared_count": 0, "new_unknown_count": 1},
        {"analyzer": "schematic", "unit_id": "o/r/a.kicad_sch", "verdict": "PASS"},
        {"analyzer": "gerber", "unit_id": "o/r/g", "verdict": "SKIP", "reason": "not_applicable"},
    ]
    up = tmp_path / "units.jsonl"
    up.write_text("".join(json.dumps(u) + "\n" for u in units))
    claims = {"pcb/o/r/a.kicad_pcb": {"PCB-x": 4}, "emc/o/r/a.kicad_sch": {"EMC-x": 3},
              "emc/o/r/b.kicad_sch": {"EMC-x": 1}}
    if budget_format == "stream":
        bp = tmp_path / "b.units.jsonl"
        bp.write_text("".join(json.dumps({"unit": k, "claimed": v,
                                          "residuals": 1 if residual_unit and k.startswith("pcb") else 0}) + "\n"
                              for k, v in claims.items()))
    else:
        bp = tmp_path / "field_report_budgeted.json"
        bp.write_text(json.dumps({"mode": "budgeted", "budget": {
            "claimed": {c: [{"unit": k} for k, v in claims.items() if c in v for _ in range(v[c])]
                        for c in ("PCB-x", "EMC-x")},
            "residuals": [{"unit": "pcb/o/r/a.kicad_pcb"}] if residual_unit else []}}))
    budget = tmp_path / "budget.json"
    budget.write_text(json.dumps({"budget_id": "b-x", "classes": [
        {"id": "PCB-x", "analyzer": "pcb", "evidence": "PM-001 per courtyard layer. /abs/path/x.json"},
        {"id": "EMC-x", "analyzer": "emc", "evidence": "stages -> layout"}],
        "acknowledged_overruns": [{"class": "c1", "declared": "0", "measured": "2",
                                   "ruling": "acknowledged"}]}))
    return up, bp, budget


def _budgeted_rollup():
    return {"section": "vX_range", "total_units": 5,
            "totals": {"PASS": 1, "FAIL": 2, "Disappeared": 3, "Downgrades": 2, "Upgrades": 0,
                       "NewKnown": 0, "NewUpgraded": 0, "NewUnknown": 1, "WARN": 1, "SKIP": 1},
            "pass_criteria": {"clean": False},
            "gate_pass": {"skip_breakdown": {"not_applicable": 1, "both_failed": 0},
                          "ledgered_skips": 0, "unledgered_skips": []}}


@pytest.mark.parametrize("fmt", ["stream", "report"])
def test_every_nonzero_counter_is_attributed(tmp_path, fmt):
    up, bp, budget = _gate_files(tmp_path, budget_format=fmt)
    md = gvm.generate_markdown(
        check_results=_results(1), gate_rollup=_budgeted_rollup(), gate_verdict="CLEAN UNDER BUDGET",
        gate_attribution=gvm._attribute_gate(up, bp), gate_budget=json.loads(budget.read_text()))
    assert "| Outcome | Count | Attribution |" in md
    assert "| Downgrades | 2 | 2 findings in 1 unit, attributed to `PCB-x` |" in md
    assert "| FAIL | 2 | attributed to `EMC-x` (1 unit), `PCB-x` (1 unit) |" in md
    assert "| Disappeared | 3 | 3 findings in 1 unit, attributed to `EMC-x` |" in md
    assert "| NewUnknown | 1 | 1 finding in 1 unit, attributed to `EMC-x` |" in md
    assert "| SKIP | 1 | 1 not applicable |" in md
    assert "| PASS | 1 | |" in md
    assert "- `PCB-x` (pcb): PM-001 per courtyard layer" in md and "/abs/path" not in md
    assert "Acknowledged overruns" in md and "c1" in md
    rule = md.split("| SKIP |")[1]
    assert "Downgrades" in rule.split("\n\n")[1] and "Downgrades == 0" not in md


def test_clean_verdict_with_an_unattributed_counter_is_refused(tmp_path):
    up, bp, budget = _gate_files(tmp_path, residual_unit=True)
    with pytest.raises(ValueError, match="Downgrades"):
        gvm.generate_markdown(
            check_results=_results(1), gate_rollup=_budgeted_rollup(),
            gate_verdict="CLEAN UNDER BUDGET", gate_attribution=gvm._attribute_gate(up, bp))


def test_clean_verdict_without_attribution_data_is_refused():
    with pytest.raises(ValueError, match="unattributed"):
        gvm.generate_markdown(check_results=_results(1), gate_rollup=_budgeted_rollup(),
                              gate_verdict="CLEAN UNDER BUDGET")


def test_non_clean_verdict_may_show_unattributed_counters(tmp_path):
    up, bp, _ = _gate_files(tmp_path, residual_unit=True)
    md = gvm.generate_markdown(
        check_results=_results(1), gate_rollup=_budgeted_rollup(), gate_verdict="NOT CLEAN",
        gate_attribution=gvm._attribute_gate(up, bp))
    assert "| Downgrades | 2 | 2 findings in 1 unit, 1 unit unattributed |" in md


def test_units_file_must_match_the_rollup(tmp_path):
    up, bp, _ = _gate_files(tmp_path)
    roll = _budgeted_rollup()
    roll["totals"]["Downgrades"] = 5
    with pytest.raises(ValueError, match="units file"):
        gvm.generate_markdown(check_results=_results(1), gate_rollup=roll,
                              gate_verdict="CLEAN UNDER BUDGET",
                              gate_attribution=gvm._attribute_gate(up, bp))


def test_main_reads_arguments_from_a_file_and_exits_nonzero_on_a_contradiction(tmp_path, monkeypatch):
    cr = tmp_path / "checks.json"
    cr.write_text(json.dumps(_results(1)))
    roll = tmp_path / "rollup.json"
    roll.write_text(json.dumps(_budgeted_rollup()))
    args = tmp_path / "args.txt"
    out = tmp_path / "out.md"
    common = f"--check-results\n{cr}\n--gate-rollup\n{roll}\n--output\n{out}\n"
    args.write_text(common + "--gate-verdict\nNOT CLEAN — `x` → `y`\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["generate_validation_md.py", f"@{args}"])
    gvm.main()
    assert "Verdict: **NOT CLEAN — `x` → `y`**" in out.read_text(encoding="utf-8")
    out.unlink()
    args.write_text(common + "--gate-verdict\nCLEAN UNDER BUDGET\n", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        gvm.main()
    assert e.value.code not in (0, None)
    assert not out.exists()
