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
