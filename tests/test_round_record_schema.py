"""Round record schema (spec §9) — request/response shapes are machine-validated."""
import copy
import json
from pathlib import Path

import jsonschema
import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "regression" / "round_record.schema.json").read_text())
FIX = ROOT / "tests" / "fixtures" / "h0" / "plan6"


def _validator(defn):
    schema = dict(SCHEMA)
    schema["$ref"] = f"#/$defs/{defn}"
    return jsonschema.Draft202012Validator(schema)


def test_request_fixture_valid():
    _validator("request").validate(json.loads((FIX / "round_request_ok.json").read_text()))


def test_response_fixture_valid():
    _validator("response").validate(json.loads((FIX / "round_response_ok.json").read_text()))


def test_request_rejects_owner_outside_skills():
    req = json.loads((FIX / "round_request_ok.json").read_text())
    req["relocations"][0]["new_owner"] = "tools/reader.py"
    with pytest.raises(jsonschema.ValidationError):
        _validator("request").validate(req)


def test_request_rejects_short_sha():
    req = json.loads((FIX / "round_request_ok.json").read_text())
    req["baseline_sha"] = "6a91aaa"
    with pytest.raises(jsonschema.ValidationError):
        _validator("request").validate(req)


def test_facade_until_accepts_round_id_rejects_date():
    req = json.loads((FIX / "round_request_ok.json").read_text())
    req["relocations"][0]["facade_until"] = "r05"
    _validator("request").validate(req)
    req["relocations"][0]["facade_until"] = "2026-10-15"
    with pytest.raises(jsonschema.ValidationError):
        _validator("request").validate(req)


def test_response_rejects_unknown_verdict_word():
    resp = json.loads((FIX / "round_response_ok.json").read_text())
    resp["verdicts"]["strict"] = "mostly clean"
    with pytest.raises(jsonschema.ValidationError):
        _validator("response").validate(resp)


def test_response_requires_complete_report_when_residuals_positive():
    resp = copy.deepcopy(json.loads((FIX / "round_response_ok.json").read_text()))
    resp["deltas"] = {"complete_report": None, "by_class": {}, "residuals": 3}
    with pytest.raises(jsonschema.ValidationError):
        _validator("response").validate(resp)


def test_top_level_oneof_distinguishes_kinds():
    v = jsonschema.Draft202012Validator(SCHEMA)
    v.validate(json.loads((FIX / "round_request_ok.json").read_text()))
    v.validate(json.loads((FIX / "round_response_ok.json").read_text()))


def test_response_accepts_over_budget_verdict():
    resp = json.loads((FIX / "round_response_ok.json").read_text())
    resp["verdicts"]["budgeted"] = "over_budget"
    _validator("response").validate(resp)


# ---- record additions (round 2): every new field optional, declared, validated ----

R2 = ROOT / "tests" / "fixtures" / "h0" / "round2"


def test_full_request_with_new_fields_valid():
    _validator("request").validate(json.loads((R2 / "round_request_full.json").read_text()))


def test_full_response_with_new_fields_valid():
    _validator("response").validate(json.loads((R2 / "round_response_full.json").read_text()))


def test_new_fields_optional_and_nullables():
    resp = json.loads((R2 / "round_response_full.json").read_text())
    resp.update(accept_baseline_diff=None, budget_sha256=None, scan_coverage_verdict="not_run")
    _validator("response").validate(resp)
    req = json.loads((R2 / "round_request_full.json").read_text())
    req["known_defects_deferred"][0]["fix_round"] = "r03"
    _validator("request").validate(req)


REQ_BAD = {
    "removed_empty_symbol": lambda d: d["removed"][0].update(symbol=""),
    "removed_refs_not_list": lambda d: d["removed"][0].update(harness_refs="tests/x.py"),
    "defect_line_zero": lambda d: d["known_defects_deferred"][0].update(line=0),
    "defect_file_not_skill": lambda d: d["known_defects_deferred"][0].update(file="tools/x.py"),
    "defect_bad_fix_round": lambda d: d["known_defects_deferred"][0].update(fix_round="later"),
    "defect_unknown_key": lambda d: d["known_defects_deferred"][0].update(decision="deferred"),
    "sidecar_leaf_no_slash": lambda d: d["expected_sidecar_changes"][0].update(leaf="schema_versions"),
    "evidence_missing_pinned": lambda d: d["product_evidence"].pop("pinned_harness"),
    "evidence_schema_not_bool": lambda d: d["product_evidence"].update(schema_identical="yes"),
}
RESP_BAD = {
    "apply_map_negative": lambda d: d["apply_map_result"].update(sites_migrated=-1),
    "apply_map_missing_files": lambda d: d["apply_map_result"].pop("files"),
    "accept_diff_not_string": lambda d: d.update(accept_baseline_diff=5),
    "scan_verdict_unknown": lambda d: d.update(scan_coverage_verdict="maybe"),
    "budget_sha_short": lambda d: d.update(budget_sha256="abc"),
}


@pytest.mark.parametrize("case", sorted(REQ_BAD))
def test_request_new_field_invalid(case):
    req = json.loads((R2 / "round_request_full.json").read_text())
    REQ_BAD[case](req)
    with pytest.raises(jsonschema.ValidationError):
        _validator("request").validate(req)


@pytest.mark.parametrize("case", sorted(RESP_BAD))
def test_response_new_field_invalid(case):
    resp = json.loads((R2 / "round_response_full.json").read_text())
    RESP_BAD[case](resp)
    with pytest.raises(jsonschema.ValidationError):
        _validator("response").validate(resp)
