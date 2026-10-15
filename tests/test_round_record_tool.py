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
