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
