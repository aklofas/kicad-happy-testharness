"""tools/test_manifest.py — collection manifest and legacy-count comparison."""
import json
import os
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
from tools.test_manifest import compare_legacy  # noqa: E402
from tests.product_root import PRODUCT_ROOT  # noqa: E402


def test_compare_legacy_rows():
    legacy = {"files": [
        {"file": "tests/test_a.py", "passed": 3, "failed": 0, "status": "pass"},
        {"file": "tests/test_phantom.py", "passed": 1, "failed": 0, "status": "pass",
         "parsed": False},
    ]}
    manifest = {"tests/test_a.py::test_1": ["unit"], "tests/test_a.py::test_2": ["unit"],
                "tests/test_a.py::test_3": ["unit"],
                "tests/test_phantom.py::test_x": ["unit"], "tests/test_phantom.py::test_y": ["unit"],
                "tests/test_new.py::test_z": ["unit"]}
    rows = {r["file"]: r for r in compare_legacy(legacy, manifest)}
    assert rows["tests/test_a.py"]["delta"] == 0
    assert rows["tests/test_phantom.py"]["delta"] == 1
    assert rows["tests/test_phantom.py"]["note"] == "legacy count was a phantom pass"
    assert rows["tests/test_new.py"]["legacy_passed"] == 0
    assert rows["tests/test_new.py"]["note"] == "not in legacy run"


def test_cli_writes_manifest(tmp_path):
    out = tmp_path / "m.json"
    env = {**os.environ, "KICAD_HAPPY_DIR": str(PRODUCT_ROOT)}
    proc = subprocess.run([sys.executable, "tools/test_manifest.py", "--out", str(out),
                           "--paths", "tests/fixtures/h0/plan1/sample_tree", "--all-tiers"],
                          capture_output=True, text=True, cwd=HARNESS, env=env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = json.loads(out.read_text())
    assert len(data) == 5
    assert data["tests/fixtures/h0/plan1/sample_tree/test_online_decl.py::test_online_declared"] == ["online"]


SAMPLE = "tests/fixtures/h0/plan1/sample_tree"


def _manifest_cli(tmp_path, *flags):
    out = tmp_path / "m.json"
    env = {**os.environ, "KICAD_HAPPY_DIR": str(PRODUCT_ROOT)}
    proc = subprocess.run([sys.executable, "tools/test_manifest.py", "--out", str(out),
                           "--paths", SAMPLE, *flags],
                          capture_output=True, text=True, cwd=HARNESS, env=env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.loads(out.read_text())


def test_cli_unit_marker_selects_only_unit_items(tmp_path):
    data = _manifest_cli(tmp_path, "-m", "unit")
    assert len(data) == 2
    assert all(markers == ["unit"] for markers in data.values())
    assert {k.rsplit("::", 1)[1] for k in data} == {"test_unit_default", "test_cheap"}


def test_cli_default_selection_matches_unit_and_contract(tmp_path):
    data = _manifest_cli(tmp_path)
    assert {k.rsplit("::", 1)[1] for k in data} == {"test_unit_default", "test_cheap"}
    assert all(markers == ["unit"] for markers in data.values())


def test_phantom_file_with_zero_collected_is_missing():
    legacy = {"files": [{"file": "tests/test_gone.py", "passed": 1, "failed": 0,
                         "status": "pass", "parsed": False}]}
    rows = {r["file"]: r for r in compare_legacy(legacy, {})}
    assert rows["tests/test_gone.py"]["note"].startswith("MISSING")


def test_tier_move_is_not_missing():
    legacy = {"files": [{"file": "tests/test_moved.py", "passed": 7, "failed": 0,
                         "status": "pass", "parsed": True}]}
    manifest = {f"tests/test_moved.py::test_{i}": ["corpus"] for i in range(7)}
    rows = {r["file"]: r for r in compare_legacy(legacy, manifest, tier="unit")}
    row = rows["tests/test_moved.py"]
    assert row["collected"] == 0
    assert row["note"].startswith("moved to tier(s) corpus")
    assert not row["note"].startswith("MISSING")


def test_file_absent_from_manifest_is_missing():
    legacy = {"files": [{"file": "tests/test_gone.py", "passed": 2, "failed": 0,
                         "status": "pass", "parsed": True}]}
    manifest = {"tests/test_other.py::test_x": ["unit"]}
    rows = {r["file"]: r for r in compare_legacy(legacy, manifest, tier="unit")}
    assert rows["tests/test_gone.py"]["note"].startswith("MISSING")


def test_no_legacy_row_in_other_tier_is_not_a_move():
    manifest = {"tests/contract/test_new_contract.py::test_a": ["offline_contract"]}
    rows = {r["file"]: r for r in compare_legacy({"files": []}, manifest, tier="unit")}
    row = rows["tests/contract/test_new_contract.py"]
    assert row["note"] == "not in legacy run (tiers: offline_contract)"
    assert row["collected"] == 0


def test_partial_tier_move_is_annotated():
    legacy = {"files": [{"file": "tests/test_p.py", "passed": 4, "failed": 0, "status": "pass"}]}
    manifest = {"tests/test_p.py::a": ["unit"], "tests/test_p.py::b": ["unit"],
                "tests/test_p.py::c": ["corpus"], "tests/test_p.py::d": ["corpus"]}
    row = compare_legacy(legacy, manifest)[0]
    assert row["delta"] == -2
    assert row["note"] == "2 moved to tier(s) corpus"
