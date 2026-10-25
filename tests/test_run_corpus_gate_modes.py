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
    assert gp["criterion"] == (f"{kind}: census_ok AND skips_ok AND budgeted verdict clean AND candidate_failures == 0 "
                               "AND worker_exceptions == 0 AND compared_units > 0")


@pytest.mark.parametrize("verdict", ["residuals", "over_budget", "error"])
def test_output_changing_fails_on_unclean_budget(verdict):
    out = gate.apply_modes(_gp(strict_clean=True), _modes(verdict), kind="output-changing")
    assert out["gate_pass"]["pass"] is False


@pytest.mark.parametrize("census_ok,skips_ok", [(False, True), (True, False)])
def test_output_changing_still_needs_census_and_skips(census_ok, skips_ok):
    out = gate.apply_modes(_gp(False, census_ok, skips_ok), _modes("clean"), kind="relock")
    assert out["gate_pass"]["pass"] is False


def test_structural_unchanged_and_criterion():
    crit = ("structural: findings strict_clean AND strict_field_clean AND census_ok AND skips_ok "
            "AND candidate_failures == 0 AND worker_exceptions == 0 AND compared_units > 0")
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
    assert "output-changing: census_ok AND skips_ok AND budgeted verdict clean AND candidate_failures == 0" in out
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
        if r["verdict"] == "SKIP":
            bd[r["reason"]] += 1
    return bd


def _round2_like():
    return [_skiprec("schematic", SCH, "both_failed", "timeout", "timeout"),
            *(_skiprec(a, SCH, "dependency_missing", "skipped", "skipped") for a in ("thermal", "emc", "cross_analysis"))]


def _compared(uid="o/r/ok.kicad_sch"):
    return {"analyzer": "schematic", "repo": "o/r", "unit_id": uid, "identity": uid, "verdict": "PASS",
            "baseline": {"status": "ok"}, "candidate": {"status": "ok"}}


def test_ledgered_both_failed_and_dependents_keep_skips_ok():
    recs = _round2_like() + [_compared()]
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
    (fixture copy, no crash_units group): the schematic timeout and its three dependents are
    ledgered; the three both-sided pcb crashes are not."""
    ledger = json.loads(Path(__file__).resolve().parent.joinpath(
        "fixtures", "h0", "round2", "ledger_6a91aaa_timeouts.json").read_text())
    crashes = ["BrettHallen/Conversion_Boards/TFC_10-pin_TFC_10-pin 2.kicad_pcb",
               "hackclub/OnBoard/projects_holy60-3d_src_holy60-3d.kicad_pcb", PCB]
    recs = _round2_like() + [_skiprec("pcb", u, "both_failed", "crash", "crash") for u in crashes]
    gp = gate.compute_gate_pass(_crit(), _skips(recs), {}, {}, skip_records=recs, ledger=ledger)
    assert gp["ledgered_skips"] == 4
    assert gp["unledgered_skips"] == sorted(f"both_failed pcb {u}" for u in crashes)


# ---- --recheck: re-evaluate gate_pass from a finished gate dir with a ledger -------

import shutil  # noqa: E402

R2_FIX = Path(__file__).resolve().parent.joinpath("fixtures", "h0", "round2")
RECHECK = R2_FIX / "recheck_gate"
LEDGER_FIX = R2_FIX / "ledger_6a91aaa_timeouts.json"
CRASHES = sorted(["BrettHallen/Conversion_Boards/TFC_10-pin_TFC_10-pin 2.kicad_pcb",
                  "hackclub/OnBoard/projects_holy60-3d_src_holy60-3d.kicad_pcb",
                  "hackclub/OnBoard/projects_tofyKeeb_src_tofyKeeb.kicad_pcb"])


def test_recheck_round2_records_ledger_covers_timeout_not_crashes():
    out = gate.recheck_gate_pass(RECHECK, ledger=str(LEDGER_FIX))
    gp = out["gate_pass"]
    assert gp["census_ok"] is True and gp["strict_clean"] is True and gp["strict_field_clean"] is True
    assert gp["ledgered_skips"] == 4
    assert gp["unledgered_skips"] == [f"both_failed pcb {u}" for u in CRASHES]
    assert gp["pass"] is False and gp["kind"] == "structural"
    assert out["ledger"] == str(LEDGER_FIX)
    assert out["ledger_sha256"] == hashlib.sha256(LEDGER_FIX.read_bytes()).hexdigest()


def test_recheck_passes_when_every_bad_skip_is_ledgered(tmp_path):
    d = tmp_path / "g"
    shutil.copytree(RECHECK, d)
    recs = [json.loads(ln) for ln in (d / "units.jsonl").read_text().splitlines()]
    recs = [r for r in recs if r["analyzer"] != "pcb"]
    (d / "units.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))
    roll = json.loads((d / "rollup_round2_quick200.json").read_text())
    roll["gate_pass"]["expected_census"] = {"schematic": 3}
    (d / "rollup_round2_quick200.json").write_text(json.dumps(roll))
    gp = gate.recheck_gate_pass(d, ledger=str(LEDGER_FIX))["gate_pass"]
    assert gp["pass"] is True and gp["ledgered_skips"] == 4 and gp["unledgered_skips"] == []
    assert gate.recheck_gate_pass(d, ledger=None, use_default_ledger=False)["gate_pass"]["pass"] is False


def test_recheck_cli_exit_code_and_summary(capsys):
    with pytest.raises(SystemExit) as ex:
        gate.main(["--recheck", str(RECHECK), "--ledger", str(LEDGER_FIX)])
    assert ex.value.code == 1
    out = capsys.readouterr().out
    assert "ledgered_skips=4" in out and f"unledgered: both_failed pcb {CRASHES[0]}" in out


def test_recheck_round2_passes_with_crash_units_ledgered(tmp_path):
    led = json.loads(LEDGER_FIX.read_text())
    codes = {CRASHES[0]: 2, CRASHES[1]: 1, CRASHES[2]: 1}   # as recorded in the round-2 units
    led["crash_units"] = [{"identity": f"pcb/{u}", "analyzer": "pcb", "unit_id": u, "exit_code": codes[u],
                           "detail": "no_output", "accepted_by": None} for u in CRASHES]
    p = tmp_path / "ledger.json"
    p.write_text(json.dumps(led))
    gp = gate.recheck_gate_pass(RECHECK, ledger=str(p))["gate_pass"]
    assert gp["pass"] is True and gp["ledgered_skips"] == 7 and gp["unledgered_skips"] == []
    assert gp["ledgered_unaccepted"]["count"] == 4   # 3 crashes + the LT3514 timeout, all unstamped
    led["crash_units"][1]["exit_code"] = 2           # ruling Q3: a changed exit code is a round delta
    p.write_text(json.dumps(led))
    gp = gate.recheck_gate_pass(RECHECK, ledger=str(p))["gate_pass"]
    assert gp["unledgered_skips"] == [f"both_failed pcb {CRASHES[1]}"]


# ---- review I3a: covering ledger entries without accepted_by are reported ------------

def test_ledgered_unaccepted_reported_skips_ok_unchanged():
    recs = _round2_like()
    led = {"timeout_units": [{"identity": f"schematic/{SCH}", "accepted_by": None}]}
    gp = gate.compute_gate_pass(_crit(), _skips(recs), {}, {}, skip_records=recs, ledger=led)
    assert gp["skips_ok"] is True and gp["ledgered_skips"] == 4
    assert gp["ledgered_unaccepted"] == {"count": 1, "identities": [f"schematic/{SCH}"]}
    led["timeout_units"][0]["accepted_by"] = "LOG later (4)"
    gp = gate.compute_gate_pass(_crit(), _skips(recs), {}, {}, skip_records=recs, ledger=led)
    assert gp["ledgered_unaccepted"] == {"count": 0, "identities": []}
    gp = gate.compute_gate_pass(_crit(), _skips(recs), {}, {}, skip_records=recs, ledger=None)
    assert gp["ledgered_unaccepted"] == {"count": 0, "identities": []}


# ---- review I2: candidate-only failures are never budgetable ------------------------

def _cand_fail(analyzer="pcb", uid="o/r/x.kicad_pcb"):
    return {"analyzer": analyzer, "repo": "o/r", "unit_id": uid, "identity": uid, "verdict": "FAIL",
            "reason": gate.CANDIDATE_FAILED_REASON, "baseline": {"status": "ok"}, "candidate": {"status": "crash"}}


def test_diff_envelopes_uses_candidate_failed_reason(tmp_path):
    a = tmp_path / "a.json"
    a.write_text("{}")
    assert gate.diff_envelopes(a, tmp_path / "missing.json", True, False)["reason"] == gate.CANDIDATE_FAILED_REASON


def test_candidate_failures_counted_and_gate_every_kind():
    recs = [_cand_fail(), {"analyzer": "pcb", "unit_id": "o/r/y", "identity": "o/r/y", "verdict": "FAIL",
                           "reason": "worker_exception"}]
    gp = gate.compute_gate_pass(_crit(), _skips([]), {}, {}, skip_records=recs)
    assert gp["candidate_failures"] == 1 and gp["pass"] is False
    for kind in ("output-changing", "relock"):
        rep = {"gate_pass": {"pass": False, "strict_clean": False, "census_ok": True, "skips_ok": True,
                             "candidate_failures": 1}, "modes": {}, "identity": {}}
        out = gate.apply_modes(rep, _modes("clean"), kind=kind)
        assert out["gate_pass"]["pass"] is False, kind
        assert "candidate_failures == 0" in out["gate_pass"]["criterion"]
    rep = {"gate_pass": {"pass": True, "strict_clean": True, "census_ok": True, "skips_ok": True,
                         "candidate_failures": 0}, "modes": {}, "identity": {}}
    assert gate.apply_modes(rep, _modes("clean"), kind="relock")["gate_pass"]["pass"] is True
    assert "candidate_failures == 0" in gate.apply_modes(rep, _modes("n/a", True))["gate_pass"]["criterion"]


def test_print_summary_shows_candidate_failures(capsys):
    report = gate.apply_modes({"gate_pass": {"pass": False, "strict_clean": False, "census_ok": True,
                                             "skips_ok": True, "candidate_failures": 2},
                               "modes": {}, "identity": {}}, _modes("clean"), kind="output-changing")
    report.update({"section": "s", "total_units": 0, "rollup": [], "fail_repo_count": 0, "fail_repos": [],
                   "new_known_rule_distribution": {}, "new_upgraded_rule_distribution": {},
                   "new_unknown_rule_distribution": {},
                   "totals": {k: 0 for k in ("PASS", "WARN", "FAIL", "SKIP", "Disappeared", "Downgrades",
                                             "NewKnown", "NewUnknown")},
                   "pass_criteria": {"disappeared_count": 0, "severity_downgrades": 0, "fail_verdicts": 2,
                                     "new_unknown_count": 0, "new_upgraded_count": 0, "warn_count": 0,
                                     "clean": False, "strict_clean": False}})
    gate._print_summary(report)
    assert "candidate_failures=2" in capsys.readouterr().out


# ---- review I3b: the ledger must belong to the run's baseline ----------------------

def test_check_ledger_sha_full_prefix_and_mismatch(tmp_path):
    full = "6a91aaaea124152b2923326c1cf77278e0999cd4"
    gate.check_ledger_sha({"product_sha": full}, "l.json", full)
    gate.check_ledger_sha({"product_sha": "6a91aaa"}, "l.json", full)
    with pytest.raises(gate.LedgerError, match=r"--ledger l.json product_sha 0000000 != baseline 6a91aaae"):
        gate.check_ledger_sha({"product_sha": "0000000"}, "l.json", full)
    with pytest.raises(gate.LedgerError, match="product_sha None"):
        gate.check_ledger_sha({}, "l.json", full)


def test_recheck_rejects_ledger_for_another_baseline(tmp_path, capsys):
    led = json.loads(LEDGER_FIX.read_text())
    led["product_sha"] = "f" * 40
    p = tmp_path / "other.json"
    p.write_text(json.dumps(led))
    with pytest.raises(gate.LedgerError):
        gate.recheck_gate_pass(RECHECK, ledger=str(p))
    with pytest.raises(SystemExit) as ex:
        gate.main(["--recheck", str(RECHECK), "--ledger", str(p)])
    assert ex.value.code == 2
    assert f"Error: --ledger {p} product_sha {'f' * 40} != baseline" in capsys.readouterr().err


def _git_repo(path):
    import subprocess
    path.mkdir()
    subprocess.run(["git", "-C", str(path), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(path), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "x"], check=True)
    return path


def test_main_rejects_ledger_for_another_baseline_before_phase_a(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("KICAD_HAPPY_TESTHARNESS_DATA_DIR", str(tmp_path / "data"))
    base, cand = _git_repo(tmp_path / "base"), _git_repo(tmp_path / "cand")
    p = tmp_path / "l.json"
    p.write_text(json.dumps({"product_sha": "f" * 40, "timeout_units": []}))
    with pytest.raises(SystemExit) as ex:
        gate.main(["--baseline-dir", str(base), "--candidate-dir", str(cand), "--gate-dir", str(tmp_path / "g"),
                   "--repo", "x", "--ledger", str(p)])
    assert ex.value.code == 2 and not (tmp_path / "g").exists()
    assert f"Error: --ledger {p} product_sha {'f' * 40} != baseline" in capsys.readouterr().err


# ---- review M3: recheck warns when the manifest has no kind ---------------------------

def test_recheck_warns_when_manifest_has_no_kind(tmp_path, capsys):
    d = tmp_path / "g"
    shutil.copytree(RECHECK, d)
    m = json.loads((d / "manifest.json").read_text())
    m.pop("kind")
    (d / "manifest.json").write_text(json.dumps(m))
    gp = gate.recheck_gate_pass(d, ledger=str(LEDGER_FIX))["gate_pass"]
    assert gp["kind"] == "structural"
    assert "warning: manifest has no kind; rechecking as structural" in capsys.readouterr().err
