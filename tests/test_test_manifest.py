"""tools/test_manifest.py — collection manifest and legacy-count comparison."""
import json
import os
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
from tools.test_manifest import compare_legacy  # noqa: E402


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
    env = {**os.environ, "KICAD_HAPPY_DIR": os.environ.get(
        "KICAD_HAPPY_DIR", str(Path.home() / "Projects" / "kicad-happy"))}
    proc = subprocess.run([sys.executable, "tools/test_manifest.py", "--out", str(out),
                           "--paths", "tests/fixtures/h0/plan1/sample_tree", "--all-tiers"],
                          capture_output=True, text=True, cwd=HARNESS, env=env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = json.loads(out.read_text())
    assert len(data) == 5
    assert data["tests/fixtures/h0/plan1/sample_tree/test_online_decl.py::test_online_declared"] == ["online"]
