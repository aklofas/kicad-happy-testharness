import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import baseline_ledger as bl  # noqa: E402
import baseline_ledger_check as blc  # noqa: E402

pytestmark = pytest.mark.unit

FIX = ROOT / "tests" / "fixtures" / "h0" / "plan6"
SHA = "6a91aaaea124152b2923326c1cf77278e0999cd4"
CHECKS = json.loads((FIX / "checks_small.json").read_text())
JUNIT = (FIX / "contract_junit.xml").read_text()
UNITS = (FIX / "units_small.jsonl").read_text().splitlines()
LEDGER = bl.build_ledger(product_sha=SHA, references_sha="0" * 40, checks=CHECKS, junit_text=JUNIT,
                         units_lines=UNITS, issues_text="", context={})


def test_same_inputs_yield_no_new_identities():
    new = blc.new_identities(LEDGER, units_lines=UNITS, checks=CHECKS, junit_text=JUNIT)
    assert new == {"checks": [], "contract": [], "timeout_units": []}


def test_new_failed_check_is_reported():
    checks = json.loads(json.dumps(CHECKS))
    checks["results"].append({"id": "SEED-00000099", "passed": False, "actual": 1, "expected": 2,
                              "file": "z.kicad_sch", "repo": "o/r9", "project": "z", "aspirational": False})
    new = blc.new_identities(LEDGER, checks=checks)
    assert new["checks"] == ["o/r9/z/z.kicad_sch::SEED-00000099"]


def test_check_flags_candidate_only_timeout():
    units = list(UNITS) + [json.dumps({
        "unit_id": "o/r1/a", "analyzer": "pcb", "input_sha256": "aa",
        "baseline": {"exit_code": 0, "status": "ok", "output_sha256": "x", "elapsed_s": 3.0},
        "candidate": {"exit_code": None, "status": "timeout", "output_sha256": None, "elapsed_s": 120.0},
        "verdict": "FAIL", "reason": "candidate timeout"})]
    new = blc.new_identities(LEDGER, units_lines=units)
    assert new["timeout_units"] == ["pcb/o/r1/a (candidate)"]


def test_ledgered_baseline_timeout_is_not_new():
    new = blc.new_identities(LEDGER, units_lines=UNITS)
    assert new["timeout_units"] == []


def _timeout_side():
    return {"exit_code": None, "status": "timeout", "output_sha256": None, "elapsed_s": 120.0}


def test_ledgered_both_side_timeout_is_not_new():
    # A/A self-check shape: the ledgered unit times out on BOTH sides
    rec = json.loads(UNITS[1])
    assert rec["baseline"]["status"] == rec["candidate"]["status"] == "timeout"
    new = blc.new_identities(LEDGER, units_lines=[UNITS[1]])
    assert new["timeout_units"] == []


def test_unledgered_both_side_timeout_is_new():
    rec = {"unit_id": "o/r8/x", "analyzer": "pcb", "input_sha256": "ee", "baseline": _timeout_side(),
           "candidate": _timeout_side(), "verdict": "SKIP", "reason": "both_failed"}
    new = blc.new_identities(LEDGER, units_lines=[json.dumps(rec)])
    assert new["timeout_units"] == ["pcb/o/r8/x"]


def test_candidate_only_timeout_on_ledgered_identity_is_new():
    # ledgered as a baseline timeout, but this time only the candidate timed out
    rec = json.loads(UNITS[1])
    rec["baseline"] = {"exit_code": 0, "status": "ok", "output_sha256": "y", "elapsed_s": 90.0}
    rec["verdict"], rec["reason"] = "FAIL", "candidate timeout"
    new = blc.new_identities(LEDGER, units_lines=[json.dumps(rec)])
    assert new["timeout_units"] == ["pcb/o/r5/slow (candidate)"]


def test_run_check_exit_codes(tmp_path, capsys):
    led = tmp_path / "ledger.json"
    led.write_text(json.dumps(LEDGER))
    units = tmp_path / "units.jsonl"
    units.write_text("\n".join(UNITS) + "\n")
    rc = bl.main(["check", "--ledger", str(led), "--units", str(units)])
    assert rc == 0
    units.write_text("\n".join(UNITS) + "\n" + json.dumps({
        "unit_id": "o/r7/new", "analyzer": "pcb", "input_sha256": "dd",
        "baseline": {"exit_code": None, "status": "timeout", "output_sha256": None, "elapsed_s": 120.0},
        "candidate": {"exit_code": None, "status": "timeout", "output_sha256": None, "elapsed_s": 120.0},
        "verdict": "SKIP", "reason": "both_failed"}) + "\n")
    rc = bl.main(["check", "--ledger", str(led), "--units", str(units)])
    assert rc == 1
    assert "pcb/o/r7/new" in capsys.readouterr().out


# ---- gate SKIP coverage (Task D): one identity rule shared with new_identities ----

def _skip(analyzer, unit_id, reason, base="timeout", cand="timeout"):
    return {"analyzer": analyzer, "unit_id": unit_id, "identity": unit_id, "verdict": "SKIP", "reason": reason,
            "baseline": {"status": base}, "candidate": {"status": cand}}


KNOWN_LEDGER = {"timeout_units": [{"identity": "schematic/o/r/a.kicad_sch"}]}


def test_both_failed_timeout_covered_only_when_ledgered():
    known = blc.ledgered_timeouts(KNOWN_LEDGER)
    assert blc.skip_is_ledgered(_skip("schematic", "o/r/a.kicad_sch", "both_failed"), known) is True
    assert blc.skip_is_ledgered(_skip("schematic", "o/r/b.kicad_sch", "both_failed"), known) is False


def test_both_failed_crash_never_covered_by_a_timeout_ledger():
    known = blc.ledgered_timeouts({"timeout_units": [{"identity": "pcb/o/r/a.kicad_pcb"}]})
    assert blc.skip_is_ledgered(_skip("pcb", "o/r/a.kicad_pcb", "both_failed", "crash", "crash"), known) is False


def test_dependency_missing_covered_through_its_ledgered_upstream():
    known = blc.ledgered_timeouts(KNOWN_LEDGER)
    up_ok = _skip("schematic", "o/r/a.kicad_sch", "both_failed")
    up_new = _skip("schematic", "o/r/b.kicad_sch", "both_failed")
    dep = _skip("emc", "o/r/a.kicad_sch", "dependency_missing", "skipped", "skipped")
    assert blc.skip_is_ledgered(dep, known, upstream=up_ok) is True
    assert blc.skip_is_ledgered(dict(dep, unit_id="o/r/b.kicad_sch"), known, upstream=up_new) is False
    assert blc.skip_is_ledgered(dep, known, upstream=None) is False


def test_snapshot_read_error_never_covered():
    known = blc.ledgered_timeouts(KNOWN_LEDGER)
    assert blc.skip_is_ledgered(_skip("schematic", "o/r/a.kicad_sch", "snapshot_read_error"), known) is False
