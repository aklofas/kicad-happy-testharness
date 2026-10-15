import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import round_record  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "h0" / "plan6"
SHA_A = "6a91aaaea124152b2923326c1cf77278e0999cd4"
SHA_B = "0000000000000000000000000000000000000001"
TOOL = str(ROOT / "tools" / "round_record.py")


def test_new_request_is_valid_request():
    doc = round_record.new_request("r01-dead-leaves", SHA_A, SHA_B, "structural", ["standard"])
    assert round_record.validate_record(doc) == "request"
    assert doc["relocations"] == [] and doc["budget"] is None and doc["relock"] is False


def test_validate_fixtures():
    req = json.loads((FIX / "round_request_ok.json").read_text())
    resp = json.loads((FIX / "round_response_ok.json").read_text())
    assert round_record.validate_record(req) == "request"
    assert round_record.validate_record(resp) == "response"


def test_validate_rejects_bad_sha():
    doc = round_record.new_request("r01-x", "6a91aaa", SHA_B, "structural", ["standard"])
    with pytest.raises(ValueError, match="baseline_sha"):
        round_record.validate_record(doc)


def test_validate_rejects_unknown_kind():
    doc = round_record.new_request("r01-x", SHA_A, SHA_B, "cosmetic", ["standard"])
    with pytest.raises(ValueError, match="kind"):
        round_record.validate_record(doc)


def test_validate_rejects_bad_round_id_and_facade_until():
    doc = round_record.new_request("bogus", SHA_A, SHA_B, "structural", ["standard"])
    with pytest.raises(ValueError, match="round_id"):
        round_record.validate_record(doc)
    doc = round_record.new_request("r01-x", SHA_A, SHA_B, "structural", ["standard"])
    doc["relocations"] = [{"symbol": "a.b", "old_owner": "skills/a.py", "new_owner": "skills/c.py",
                           "new_name": "b", "facade_until": "later"}]
    with pytest.raises(ValueError, match="facade_until"):
        round_record.validate_record(doc)


def test_validate_rejects_bad_verdict_word_and_missing_report():
    resp = json.loads((FIX / "round_response_ok.json").read_text())
    resp["verdicts"]["raw"] = "fail"
    with pytest.raises(ValueError, match="verdicts.raw"):
        round_record.validate_record(resp)
    resp = json.loads((FIX / "round_response_ok.json").read_text())
    resp["deltas"].update(residuals=2, complete_report=None)
    with pytest.raises(ValueError, match="complete_report"):
        round_record.validate_record(resp)


def test_summarize_response_paragraph():
    resp = json.loads((FIX / "round_response_ok.json").read_text())
    text = round_record.summarize_response(resp)
    assert text.startswith("- **r03-schematic-reader-split** harness `5cdc70a32fd`")
    assert "strict clean" in text and "raw deltas" in text and "budgeted n/a" in text
    assert "41,012 units" in text and "residuals 0" in text and "verdict accept" in text
    assert text == round_record.summarize_response(resp)


def test_cli_validate_exit_codes(tmp_path):
    r = subprocess.run([sys.executable, TOOL, "validate", str(FIX / "round_request_ok.json")],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "request" in r.stdout
    bad = tmp_path / "bad.json"
    bad.write_text("{}")
    r = subprocess.run([sys.executable, TOOL, "validate", str(bad)], capture_output=True, text=True)
    assert r.returncode == 1 and "record_version" in r.stderr


def test_cli_new_request_and_summarize(tmp_path):
    out = tmp_path / "req.json"
    r = subprocess.run([sys.executable, TOOL, "new-request", "--round-id", "r01-x", "--baseline", SHA_A,
                        "--candidate", SHA_B, "--kind", "structural", "--profile", "standard",
                        "-o", str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert round_record.validate_record(json.loads(out.read_text())) == "request"
    r = subprocess.run([sys.executable, TOOL, "summarize", str(FIX / "round_response_ok.json")],
                       capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.startswith("- **r03-")


# ---- parity: runtime checker vs the JSON Schema (jsonschema is test-only) ----
jsonschema = pytest.importorskip("jsonschema")
SCHEMA = json.loads((ROOT / "regression" / "round_record.schema.json").read_text())


def _load(name):
    return json.loads((FIX / name).read_text())


def _mut(name, fn):
    d = _load(name)
    fn(d)
    return d


MUTATIONS = {
    "bad_filing": ("round_response_ok.json", lambda d: d.update(filings=["KH-1"])),
    "empty_run_ids": ("round_response_ok.json", lambda d: d.update(run_ids=[])),
    "short_run_id": ("round_response_ok.json", lambda d: d.update(run_ids=["abc"])),
    "bad_policy": ("round_response_ok.json", lambda d: d.update(normalization_policy="loose")),
    "unknown_key_resp": ("round_response_ok.json", lambda d: d.update(extra=1)),
    "unknown_key_req": ("round_request_ok.json", lambda d: d.update(extra=1)),
    "bad_facade_until": ("round_request_ok.json",
                         lambda d: d["relocations"][0].update(facade_until="later")),
    "empty_symbol": ("round_request_ok.json", lambda d: d["relocations"][0].update(symbol="")),
    "bad_kind": ("round_request_ok.json", lambda d: d.update(kind="cosmetic")),
    "bad_sha": ("round_request_ok.json", lambda d: d.update(baseline_sha="6a91aaa")),
    "residuals_null_report": ("round_response_ok.json",
                              lambda d: d["deltas"].update(residuals=3, complete_report=None)),
    "missing_evidence_rollup": ("round_response_ok.json", lambda d: d["evidence"].pop("rollup")),
    "census_missing_key": ("round_response_ok.json", lambda d: d["census"].pop("skip_reasons")),
    "bad_verdict_word": ("round_response_ok.json", lambda d: d["verdicts"].update(raw="fail")),
}


@pytest.mark.parametrize("name", ["round_request_ok.json", "round_response_ok.json"])
def test_parity_fixtures_pass_both(name):
    doc = _load(name)
    jsonschema.validate(doc, SCHEMA)
    round_record.validate_record(doc)


def test_parity_new_request_passes_both():
    doc = round_record.new_request("r01-x", SHA_A, SHA_B, "structural", ["standard"])
    jsonschema.validate(doc, SCHEMA)
    round_record.validate_record(doc)


@pytest.mark.parametrize("case", sorted(MUTATIONS))
def test_parity_mutations_rejected_by_both(case):
    fixture, fn = MUTATIONS[case]
    doc = _mut(fixture, fn)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(doc, SCHEMA)
    with pytest.raises(ValueError):
        round_record.validate_record(doc)


@pytest.mark.parametrize("bad", [
    {"record_version": 1, "round_id": "r01-x", "baseline_sha": SHA_A, "candidate_sha": SHA_B,
     "kind": "structural", "relocations": "nope", "profiles": ["standard"], "budget": None,
     "old_artifact_checks": [], "relock": False},
    {"record_version": 1, "round_id": "r01-x", "baseline_sha": SHA_A, "candidate_sha": SHA_B,
     "kind": "structural", "relocations": [5], "profiles": "standard", "budget": None,
     "old_artifact_checks": [], "relock": False},
])
def test_malformed_shapes_raise_valueerror(bad):
    with pytest.raises(ValueError):
        round_record.validate_record(bad)


def test_malformed_response_shapes_raise_valueerror():
    for key, val in [("verdicts", "x"), ("executed", []), ("census", 3), ("deltas", None),
                     ("evidence", "x"), ("relocation_status", 1), ("filings", "KH-001")]:
        resp = _load("round_response_ok.json")
        resp[key] = val
        with pytest.raises(ValueError, match=key):
            round_record.validate_record(resp)
