"""Tests for inputs_builder.build_inputs."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))

from inputs_builder import build_inputs  # noqa: E402


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_basic_build(tmp_path):
    a = tmp_path / "a.txt"
    a.write_text("hello")
    b = tmp_path / "b.txt"
    b.write_text("world")

    result = build_inputs([a, b], run_id="20260418T123456Z-abc123")

    assert result["source_files"] == [str(a), str(b)]
    assert result["source_hashes"] == {
        str(a): _sha(b"hello"),
        str(b): _sha(b"world"),
    }
    assert result["run_id"] == "20260418T123456Z-abc123"
    assert result["config_hash"] is None
    assert result["upstream_artifacts"] == {}


def test_config_hash_populated_when_given(tmp_path):
    cfg = tmp_path / ".kicad-happy.json"
    cfg.write_text('{"version": 1}')
    a = tmp_path / "a.txt"
    a.write_text("hello")

    result = build_inputs([a], config_path=cfg,
                          run_id="20260418T123456Z-abc123")

    assert result["config_hash"] == _sha(b'{"version": 1}')


def test_upstream_artifacts_passed_through():
    upstream = {
        "schematic": {
            "path": "/tmp/schematic.json",
            "sha256": "a" * 64,
            "schema_version": "1.4.0",
            "run_id": "20260418T123456Z-999999",
        }
    }
    result = build_inputs([], run_id="20260418T123456Z-abc123",
                          upstream_artifacts=upstream)
    assert result["upstream_artifacts"] == upstream


def test_run_id_auto_generated_when_omitted(tmp_path):
    a = tmp_path / "a.txt"
    a.write_text("x")
    result = build_inputs([a])
    # Fallback auto-gen still yields a well-formed run_id.
    assert isinstance(result["run_id"], str)
    assert len(result["run_id"]) == 23  # "YYYYMMDDTHHMMSSZ-hhhhhh"


def test_source_files_empty_list_is_allowed(tmp_path):
    """Thermal/EMC read JSONs but we still record their paths via
    source_files — build_inputs with an empty list is allowed for
    synthetic test cases and early-exit edge cases."""
    result = build_inputs([], run_id="20260418T123456Z-abc123")
    assert result["source_files"] == []
    assert result["source_hashes"] == {}


def test_build_upstream_artifact(tmp_path):
    from inputs_builder import build_upstream_artifact
    p = tmp_path / "sch.json"
    p.write_text('{"schema_version": "1.4.0", "inputs": {"run_id": "20260418T123456Z-abc123"}}')
    art = build_upstream_artifact(p, json.loads(p.read_text()))
    assert art["path"] == str(p)
    assert len(art["sha256"]) == 64
    assert art["schema_version"] == "1.4.0"
    assert art["run_id"] == "20260418T123456Z-abc123"


def test_build_upstream_artifact_missing_fields(tmp_path):
    """Tolerate upstream JSONs that predate v1.4 or lack the inputs block."""
    from inputs_builder import build_upstream_artifact
    p = tmp_path / "sch.json"
    p.write_text('{}')
    art = build_upstream_artifact(p, {})
    assert art["schema_version"] == ""
    assert art["run_id"] == ""


def test_build_compat_defaults_v1_4():
    from inputs_builder import build_compat
    compat = build_compat()
    assert compat["minimum_consumer_version"] == "1.4.0"
    assert compat["deprecated_fields"] == []
    assert compat["experimental_fields"] == []


def test_build_compat_accepts_overrides():
    from inputs_builder import build_compat
    compat = build_compat(
        minimum_consumer_version="1.5.0",
        deprecated_fields=["trust_summary.by_confidence.datasheet-backed"],
        experimental_fields=["compat.capability_mode_ref"],
    )
    assert compat["minimum_consumer_version"] == "1.5.0"
    assert compat["deprecated_fields"] == ["trust_summary.by_confidence.datasheet-backed"]
    assert compat["experimental_fields"] == ["compat.capability_mode_ref"]
