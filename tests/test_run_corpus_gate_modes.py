"""run_corpus_gate.main() runs the three comparator modes after phase B and ANDs
strict_field_clean into gate_pass (spec 2.4 / 3.5)."""
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
from regression import run_corpus_gate as gate  # noqa: E402

pytestmark = pytest.mark.unit


def test_apply_modes_ands_strict_field_clean():
    report = {"gate_pass": {"pass": True, "strict_clean": True, "census_ok": True, "skips_ok": True},
              "modes": {"findings_summary": "strict_clean"}}
    modes = {"raw": {"verdict": "fail"}, "strict": {"verdict": "deltas"},
             "budgeted": {"verdict": "n/a"}, "strict_field_clean": False}
    out = gate.apply_modes(report, modes)
    assert out["modes"]["strict"]["verdict"] == "deltas"
    assert out["modes"]["findings_summary"] == "strict_clean"
    assert out["gate_pass"]["strict_field_clean"] is False
    assert out["gate_pass"]["pass"] is False


def test_apply_modes_keeps_pass_when_strict_clean():
    report = {"gate_pass": {"pass": True}, "modes": {"findings_summary": "strict_clean"}}
    modes = {"raw": {"verdict": "fail"}, "strict": {"verdict": "clean"},
             "budgeted": {"verdict": "n/a"}, "strict_field_clean": True}
    out = gate.apply_modes(report, modes)
    assert out["gate_pass"]["pass"] is True and out["gate_pass"]["strict_field_clean"] is True


def test_main_accepts_budget_flag(tmp_path):
    ap = gate.build_arg_parser()
    ns = ap.parse_args(["--baseline-dir", "a", "--candidate-dir", "b", "--gate-dir", str(tmp_path),
                        "--repo", "x", "--budget", "regression/budgets/example.json"])
    assert ns.budget == "regression/budgets/example.json"


def test_main_rejects_malformed_budget_before_running(tmp_path, monkeypatch, capsys):
    """A bad --budget fails at argument validation (exit 2), not after phase A/B."""
    import pytest
    monkeypatch.setenv("KICAD_HAPPY_TESTHARNESS_DATA_DIR", str(tmp_path / "data"))
    bad = tmp_path / "bad.json"
    bad.write_text("{\"budget_id\": \"x\"}", encoding="utf-8")
    wt = tmp_path / "wt"
    wt.mkdir()
    with pytest.raises(SystemExit) as ex:
        gate.main(["--baseline-dir", str(wt), "--candidate-dir", str(wt), "--gate-dir", str(tmp_path / "g"),
                   "--repo", "x", "--budget", str(bad)])
    assert ex.value.code == 2
    assert "--budget" in capsys.readouterr().err


# ---- ruling I9: gate exit semantics per kind ---------------------------------

import hashlib  # noqa: E402
import json  # noqa: E402

_VALID_BUDGET = {"budget_id": "t", "classes": [], "unexplained_deltas_allowed": 0,
                 "unexplained_missing_units_allowed": 0, "relock": False}


def _budget_file(tmp_path):
    p = tmp_path / "budget.json"
    p.write_text(json.dumps(_VALID_BUDGET), encoding="utf-8")
    return p


def _run_main_expect_2(tmp_path, monkeypatch, capsys, extra):
    monkeypatch.setenv("KICAD_HAPPY_TESTHARNESS_DATA_DIR", str(tmp_path / "data"))
    wt = tmp_path / "wt"
    wt.mkdir(exist_ok=True)
    with pytest.raises(SystemExit) as ex:
        gate.main(["--baseline-dir", str(wt), "--candidate-dir", str(wt), "--gate-dir", str(tmp_path / "g"),
                   "--repo", "x", *extra])
    assert ex.value.code == 2
    assert not (tmp_path / "g").exists(), "request errors must fire before phase A"
    return capsys.readouterr().err


@pytest.mark.parametrize("kind", ["structural", "aa", "baseline", "gate"])
def test_budget_rejected_for_structural_kinds(tmp_path, monkeypatch, capsys, kind):
    err = _run_main_expect_2(tmp_path, monkeypatch, capsys,
                             ["--kind", kind, "--budget", str(_budget_file(tmp_path))])
    k = "structural" if kind == "gate" else kind
    assert (f"Error: --budget is not allowed for kind={k}: a structural round's budget MUST be empty "
            f"(ruling I9, spec §2.4)") in err


@pytest.mark.parametrize("kind", ["output-changing", "relock"])
def test_budget_required_for_output_changing_kinds(tmp_path, monkeypatch, capsys, kind):
    err = _run_main_expect_2(tmp_path, monkeypatch, capsys, ["--kind", kind])
    assert f"Error: kind={kind} requires --budget (ruling I9)" in err


def test_kind_choices_and_default():
    ap = gate.build_arg_parser()
    base = ["--baseline-dir", "a", "--candidate-dir", "b", "--gate-dir", "g", "--repo", "x"]
    assert ap.parse_args(base).kind == "structural"
    for k in ("structural", "output-changing", "relock", "aa", "baseline", "gate"):
        assert ap.parse_args(base + ["--kind", k]).kind == k
    with pytest.raises(SystemExit):
        ap.parse_args(base + ["--kind", "bogus"])


def test_gate_alias_resolves_to_structural(capsys):
    assert gate.resolve_kind("gate") == "structural"
    assert "note: --kind gate is an alias for structural" in capsys.readouterr().err
    assert gate.resolve_kind("relock") == "relock"
    assert capsys.readouterr().err == ""


def _gp(strict_clean, census_ok=True, skips_ok=True):
    return {"gate_pass": {"pass": strict_clean and census_ok and skips_ok, "strict_clean": strict_clean,
                          "census_ok": census_ok, "skips_ok": skips_ok},
            "modes": {"findings_summary": "x"}, "identity": {}}


def _modes(budgeted_verdict, strict_field_clean=None):
    sfc = budgeted_verdict == "clean" if strict_field_clean is None else strict_field_clean
    return {"raw": {"verdict": "fail"}, "strict": {"verdict": "deltas"},
            "budgeted": {"verdict": budgeted_verdict, "budget_id": "t"}, "strict_field_clean": sfc}


@pytest.mark.parametrize("kind", ["output-changing", "relock"])
def test_output_changing_passes_on_clean_budget_despite_findings(kind):
    out = gate.apply_modes(_gp(strict_clean=False), _modes("clean"), kind=kind)
    gp = out["gate_pass"]
    assert gp["pass"] is True
    assert gp["strict_clean"] is False  # kept as information
    assert gp["kind"] == kind
    assert gp["criterion"] == f"{kind}: census_ok AND skips_ok AND budgeted verdict clean"


@pytest.mark.parametrize("verdict", ["residuals", "over_budget", "error"])
def test_output_changing_fails_on_unclean_budget(verdict):
    out = gate.apply_modes(_gp(strict_clean=True), _modes(verdict), kind="output-changing")
    assert out["gate_pass"]["pass"] is False


@pytest.mark.parametrize("census_ok,skips_ok", [(False, True), (True, False)])
def test_output_changing_still_needs_census_and_skips(census_ok, skips_ok):
    out = gate.apply_modes(_gp(False, census_ok, skips_ok), _modes("clean"), kind="relock")
    assert out["gate_pass"]["pass"] is False


def test_structural_unchanged_and_criterion():
    crit = "structural: findings strict_clean AND strict_field_clean AND census_ok AND skips_ok"
    out = gate.apply_modes(_gp(strict_clean=False), _modes("n/a", strict_field_clean=True))
    assert out["gate_pass"]["pass"] is False
    assert out["gate_pass"]["kind"] == "structural" and out["gate_pass"]["criterion"] == crit
    out = gate.apply_modes(_gp(strict_clean=True), _modes("n/a", strict_field_clean=True), kind="structural")
    assert out["gate_pass"]["pass"] is True
    out = gate.apply_modes(_gp(strict_clean=True), _modes("n/a", strict_field_clean=False), kind="aa")
    assert out["gate_pass"]["pass"] is False


def test_budget_sha256_recorded(tmp_path):
    p = _budget_file(tmp_path)
    sha = gate.budget_file_sha256(p)
    assert sha == hashlib.sha256(p.read_bytes()).hexdigest()
    assert gate.budget_file_sha256(None) is None
    out = gate.apply_modes(_gp(False), _modes("clean"), kind="output-changing", budget_sha256=sha)
    assert out["modes"]["budgeted"]["budget_sha256"] == sha
    assert out["identity"]["budget_sha256"] == sha


def test_budget_sha256_null_without_budget():
    out = gate.apply_modes(_gp(True), _modes("n/a", strict_field_clean=True))
    assert out["modes"]["budgeted"]["budget_sha256"] is None
    assert out["identity"]["budget_sha256"] is None


def test_print_summary_shows_kind_criterion_and_budget(capsys):
    report = gate.apply_modes(_gp(False), _modes("over_budget"), kind="output-changing",
                              budget_sha256="ab" * 32)
    report["modes"]["budgeted"]["over_budget"] = ["C1", "C2"]
    report.update({"section": "s", "total_units": 0, "rollup": [], "fail_repo_count": 0, "fail_repos": [],
                   "new_known_rule_distribution": {}, "new_upgraded_rule_distribution": {},
                   "new_unknown_rule_distribution": {},
                   "totals": {k: 0 for k in ("PASS", "WARN", "FAIL", "SKIP", "Disappeared", "Downgrades",
                                             "NewKnown", "NewUnknown")},
                   "pass_criteria": {"disappeared_count": 0, "severity_downgrades": 0, "fail_verdicts": 0,
                                     "new_unknown_count": 0, "new_upgraded_count": 0, "warn_count": 1,
                                     "clean": True, "strict_clean": False}})
    gate._print_summary(report)
    out = capsys.readouterr().out
    assert "kind: output-changing" in out
    assert "output-changing: census_ok AND skips_ok AND budgeted verdict clean" in out
    assert "budget: t" in out and "abababababab" in out
    assert "over_budget: C1, C2" in out


# ---- Task D: ledger-aware skips_ok ----------------------------------------------

def _crit():
    totals = {"PASS": 1, "WARN": 0, "FAIL": 0, "SKIP": 0, "Disappeared": 0, "Downgrades": 0,
              "Upgrades": 0, "NewKnown": 0, "NewUpgraded": 0, "NewUnknown": 0}
    return gate._compute_pass_criteria(totals)


def _skiprec(analyzer, unit_id, reason, base, cand):
    return {"analyzer": analyzer, "repo": unit_id.rsplit("/", 1)[0], "unit_id": unit_id, "identity": unit_id,
            "verdict": "SKIP", "reason": reason, "baseline": {"status": base}, "candidate": {"status": cand}}


SCH = "cristobalcuevas/Kicad/LT3514_LT3514.kicad_sch"
PCB = "hackclub/OnBoard/projects_tofyKeeb_src_tofyKeeb.kicad_pcb"
LEDGER_SCH = {"timeout_units": [{"identity": f"schematic/{SCH}"}]}


def _skips(records):
    bd = {"not_applicable": 0, "both_failed": 0, "dependency_missing": 0, "snapshot_read_error": 0}
    for r in records:
        bd[r["reason"]] += 1
    return bd


def _round2_like():
    return [_skiprec("schematic", SCH, "both_failed", "timeout", "timeout"),
            *(_skiprec(a, SCH, "dependency_missing", "skipped", "skipped") for a in ("thermal", "emc", "cross_analysis"))]


def test_ledgered_both_failed_and_dependents_keep_skips_ok():
    recs = _round2_like()
    gp = gate.compute_gate_pass(_crit(), _skips(recs), {}, {}, skip_records=recs, ledger=LEDGER_SCH)
    assert gp["skips_ok"] is True and gp["pass"] is True
    assert gp["ledgered_skips"] == 4 and gp["unledgered_skips"] == []


def test_unledgered_both_failed_fails_and_is_listed():
    recs = _round2_like() + [_skiprec("pcb", PCB, "both_failed", "crash", "crash")]
    gp = gate.compute_gate_pass(_crit(), _skips(recs), {}, {}, skip_records=recs, ledger=LEDGER_SCH)
    assert gp["skips_ok"] is False and gp["pass"] is False
    assert gp["ledgered_skips"] == 4
    assert gp["unledgered_skips"] == [f"both_failed pcb {PCB}"]


def test_no_ledger_is_todays_behaviour():
    recs = _round2_like()
    gp = gate.compute_gate_pass(_crit(), _skips(recs), {}, {}, skip_records=recs, ledger=None)
    assert gp["skips_ok"] is False and gp["ledgered_skips"] == 0
    assert gp["unledgered_skips"] == [f"both_failed schematic {SCH}"] + [
        f"dependency_missing {a} {SCH}" for a in ("cross_analysis", "emc", "thermal")]
    na = [_skiprec("thermal", SCH, "not_applicable", "skipped", "skipped")]
    assert gate.compute_gate_pass(_crit(), _skips(na), {}, {}, skip_records=na)["skips_ok"] is True


def test_resolve_ledger_default_explicit_and_none(tmp_path, monkeypatch):
    sha = "6a91aaaea124152b2923326c1cf77278e0999cd4"
    monkeypatch.setattr(gate, "HARNESS_DIR", tmp_path)
    assert gate.resolve_ledger(None, sha) is None
    want = tmp_path.joinpath("reference", "baseline_debts", "6a91aaa.json")
    want.parent.mkdir(parents=True)
    want.write_text("{}")
    assert gate.resolve_ledger(None, sha) == want
    assert gate.resolve_ledger(None, "f" * 40) is None
    explicit = tmp_path / "l.json"
    explicit.write_text("{}")
    assert gate.resolve_ledger(str(explicit), sha) == explicit
    with pytest.raises(FileNotFoundError):
        gate.resolve_ledger(str(tmp_path / "missing.json"), sha)


def test_ledger_identity_recorded(tmp_path):
    p = tmp_path / "l.json"
    p.write_text(json.dumps(LEDGER_SCH))
    info = gate.ledger_identity(p)
    assert info == {"ledger": str(p), "ledger_sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    assert gate.ledger_identity(None) == {"ledger": None, "ledger_sha256": None}


def test_explicit_missing_ledger_exits_2_before_phase_a(tmp_path, monkeypatch, capsys):
    err = _run_main_expect_2(tmp_path, monkeypatch, capsys, ["--ledger", str(tmp_path / "nope.json")])
    assert "Error: --ledger" in err and "not found" in err


def test_round2_real_skips_against_real_ledger():
    """The seven round-2 bad skips (6a91aaa->8912a5a) against the 6a91aaa ledger's timeout_units
    (fixture copy): the schematic timeout and its three dependents are ledgered; the three pcb
    crashes are not, because the ledger records timeouts only."""
    ledger = json.loads(Path(__file__).resolve().parent.joinpath(
        "fixtures", "h0", "round2", "ledger_6a91aaa_timeouts.json").read_text())
    crashes = ["BrettHallen/Conversion_Boards/TFC_10-pin_TFC_10-pin 2.kicad_pcb",
               "hackclub/OnBoard/projects_holy60-3d_src_holy60-3d.kicad_pcb", PCB]
    recs = _round2_like() + [_skiprec("pcb", u, "both_failed", "crash", "crash") for u in crashes]
    gp = gate.compute_gate_pass(_crit(), _skips(recs), {}, {}, skip_records=recs, ledger=ledger)
    assert gp["ledgered_skips"] == 4
    assert gp["unledgered_skips"] == sorted(f"both_failed pcb {u}" for u in crashes)
