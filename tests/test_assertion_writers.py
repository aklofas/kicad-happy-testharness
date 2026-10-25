"""One writer for assertion files, one constructor for era payloads."""
import json
import pytest

from regression.reference_io import write_assertion_file
from regression.schema_era import era_payload, stamp_schema_era
from regression.tag_assertions import _insert_schema_era

pytestmark = pytest.mark.unit


def test_write_assertion_file_bytes(tmp_path):
    d = {"assertions": [{"description": "Ω résistance", "x": [1, [2, 3]]}], "b": 1, "a": 2}
    p = tmp_path / "a.json"
    write_assertion_file(p, d)
    assert p.read_bytes() == (json.dumps(d, indent=2) + "\n").encode("utf-8")


def test_era_payload_shape():
    p = era_payload("v1.4", "R", "T", "why")
    assert list(p) == ["era", "tagged_by_rule", "tagged_at", "tagged_reason"]
    assert p == {"era": "v1.4", "tagged_by_rule": "R", "tagged_at": "T", "tagged_reason": "why"}


def test_insert_after_check_and_stamp_appends():
    a = {"id": "x", "check": {}, "z": 1}
    _insert_schema_era(a, "v1.4", "R", "T", "why")
    assert list(a) == ["id", "check", "schema_era", "z"]
    assert a["schema_era"] == era_payload("v1.4", "R", "T", "why")
    b = {"id": "x", "check": {"detector_filter": "detect_pullups"}, "z": 1}
    if stamp_schema_era(b, tagged_at="T"):
        assert list(b)[-1] == "schema_era"
