import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import baseline_ledger as bl  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "h0" / "plan6"
SHA = "6a91aaaea124152b2923326c1cf77278e0999cd4"
REF = "0684046000000000000000000000000000000000"
CHECKS = json.loads((FIX / "checks_small.json").read_text())
JUNIT = (FIX / "contract_junit.xml").read_text()
UNITS = (FIX / "units_small.jsonl").read_text().splitlines()
ISSUES = (FIX / "issues_snippet.md").read_text()


def test_check_identities_excludes_aspirational_and_passed():
    ents = bl.check_identities(CHECKS)
    ids = {e["id"] for e in ents}
    assert ids == {"FND-00001759-AST-04", "FND-00002002-AST-04", "FND-00000009-AST-01"}
    kinds = {e["id"]: e["kind"] for e in ents}
    assert kinds["FND-00000009-AST-01"] == "error" and kinds["FND-00002002-AST-04"] == "fail"
    assert all(e["cause"] == "unreviewed" and e["accepted_by"] is None for e in ents)
    assert ents[0]["identity"].count("::") == 1


def test_contract_entries_split_skipped_vs_xfailed():
    ents = bl.contract_entries(JUNIT)
    by = {e["identity"]: e for e in ents}
    assert by["tests/contract/test_x.py::test_known_bad"]["kind"] == "xfailed"
    assert by["tests/contract/test_deep_review_gate.py::test_pdf"]["kind"] == "skipped"
    assert by["tests/contract/test_deep_review_gate.py::test_pdf"]["reason"] == "pdftotext not installed"
    assert len(ents) == 3


def test_timeout_units_both_analyzers():
    ents = bl.timeout_units(UNITS)
    assert {e["identity"] for e in ents} == {"pcb/o/r5/slow", "schematic/o/r6/slowsch"}
    assert ents[0]["elapsed_s"] == 120.0


def test_nondeterminism_entries_only_hash_seed_items():
    ents = bl.nondeterminism_entries(ISSUES)
    assert [e["identity"] for e in ents] == ["KH-421"]
    assert ents[0]["repo"] == "BerkeleyLab/Marble"


def test_build_ledger_shape_and_counts():
    led = bl.build_ledger(product_sha=SHA, references_sha=REF, checks=CHECKS, junit_text=JUNIT,
                          units_lines=UNITS, issues_text=ISSUES,
                          context={"analyzer_diff": "0684046..6a91aaa = PR #51", "expected_corpus_movement": "≈0"})
    assert led["ledger_version"] == 1 and led["product_sha"] == SHA
    assert len(led["checks"]) == 3 and len(led["contract"]) == 3
    assert len(led["timeout_units"]) == 2 and len(led["nondeterminism"]) == 1
    assert led["context"]["analyzer_diff"].startswith("0684046..6a91aaa")


def test_build_refuses_mismatched_sha():
    with pytest.raises(ValueError, match="product_sha"):
        bl.build_ledger(product_sha="0" * 40, references_sha=REF, checks=CHECKS, junit_text=JUNIT,
                        units_lines=UNITS, issues_text=ISSUES, context={})


def test_build_refuses_checks_without_sha():
    checks = dict(CHECKS)
    checks.pop("product_sha")
    with pytest.raises(ValueError, match="product_sha"):
        bl.build_ledger(product_sha=SHA, references_sha=REF, checks=checks, junit_text=JUNIT,
                        units_lines=UNITS, issues_text=ISSUES, context={})


def test_check_identities_tolerates_parse_error_records():
    # run_checks.py JSON-parse-error branch: no repo/project keys
    checks = {"results": [{"file": "broken.kicad_sch", "id": "SEED-00000001", "passed": False,
                           "error": "JSON parse error: Expecting value", "aspirational": False},
                          {"id": "SEED-00000002", "passed": False, "error": "x", "aspirational": False}]}
    ents = bl.check_identities(checks)
    assert [e["identity"] for e in ents] == ["?::SEED-00000002", "broken.kicad_sch::SEED-00000001"]
    assert ents[1]["kind"] == "error" and ents[1]["repo"] is None


# ---- Task E: crash_units group + --carry-accepted-from ---------------------------

def _crash(unit_id, analyzer="pcb", base="crash", cand="crash", code=2):
    side = lambda st: {"status": st, "exit_code": code if st == "crash" else 0,  # noqa: E731
                       "detail": "no_output" if st == "crash" else None, "elapsed_s": 0.1, "output_sha256": None}
    return json.dumps({"unit_id": unit_id, "analyzer": analyzer, "input_sha256": "cc", "baseline": side(base),
                       "candidate": side(cand), "verdict": "SKIP" if cand == "crash" else "WARN",
                       "reason": "both_failed"})


CRASH_LINES = [_crash("o/r7/boom.kicad_pcb"), _crash("o/r8/one.kicad_pcb", cand="ok")]


def test_crash_units_both_sided_only():
    ents = bl.crash_units(UNITS + CRASH_LINES)
    assert ents == [{"identity": "pcb/o/r7/boom.kicad_pcb", "analyzer": "pcb", "unit_id": "o/r7/boom.kicad_pcb",
                     "exit_code": 2, "detail": "no_output", "accepted_by": None}]


def test_build_ledger_emits_crash_units_group():
    led = bl.build_ledger(product_sha=SHA, references_sha=REF, checks=CHECKS, junit_text=JUNIT,
                          units_lines=UNITS + CRASH_LINES, issues_text=ISSUES, context={})
    assert led["ledger_version"] == 1
    assert [e["identity"] for e in led["crash_units"]] == ["pcb/o/r7/boom.kicad_pcb"]


def test_carry_accepted_preserves_stamps_by_identity():
    new = bl.build_ledger(product_sha=SHA, references_sha=REF, checks=CHECKS, junit_text=JUNIT,
                          units_lines=UNITS + CRASH_LINES, issues_text=ISSUES, context={})
    prior = json.loads(json.dumps(new))
    prior["checks"][0]["accepted_by"] = "LOG later (4)"
    prior["timeout_units"][0]["accepted_by"] = "LOG timeouts"
    prior["contract"] = prior["contract"][1:]          # drop one: its rebuilt twin stays null
    del prior["crash_units"]                           # an older ledger without the group
    out = bl.carry_accepted(new, prior)
    assert out["checks"][0]["accepted_by"] == "LOG later (4)"
    assert out["timeout_units"][0]["accepted_by"] == "LOG timeouts"
    assert out["contract"][0]["accepted_by"] is None
    assert all(e["accepted_by"] is None for e in out["crash_units"])


def test_build_cli_carry_accepted_from(tmp_path):
    import subprocess
    units = tmp_path / "units.jsonl"
    units.write_text("\n".join(UNITS + CRASH_LINES) + "\n")
    checks = tmp_path / "checks.json"
    checks.write_text(json.dumps(CHECKS))
    common = [sys.executable, str(ROOT / "tools" / "baseline_ledger.py"), "build", "--product-sha", SHA,
              "--references-sha", REF, "--checks", str(checks), "--junit", str(FIX / "contract_junit.xml"),
              "--units", str(units), "--issues", str(FIX / "issues_snippet.md"),
              "--analyzer-diff", "d", "--expected-movement", "m"]
    first = tmp_path / "a.json"
    assert subprocess.run(common + ["-o", str(first)], capture_output=True).returncode == 0
    led = json.loads(first.read_text())
    led["crash_units"][0]["accepted_by"] = "maintainer LOG later (4)"
    first.write_text(json.dumps(led))
    second = tmp_path / "b.json"
    r = subprocess.run(common + ["--carry-accepted-from", str(first), "-o", str(second)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "crashes 1" in r.stdout
    assert json.loads(second.read_text())["crash_units"][0]["accepted_by"] == "maintainer LOG later (4)"
