"""run_spice passes --workdir, strips credentials by default, uses run_once (TH-059)."""
TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "run"))

from run_spice import run_one_spice, unit_workdir  # noqa: E402

RECORDER = """import json, os, sys
argv = sys.argv[1:]
out = argv[argv.index('--output') + 1]
wd = argv[argv.index('--workdir') + 1] if '--workdir' in argv else None
json.dump({"summary": {"total": 1, "pass": 1}, "workdir": wd,
           "has_creds": "DIGIKEY_CLIENT_ID" in os.environ,
           "offline": os.environ.get("KICAD_HAPPY_OFFLINE")}, open(out, "w"))
"""


def test_workdir_and_offline_env_reach_simulator(tmp_path, monkeypatch):
    monkeypatch.setenv("DIGIKEY_CLIENT_ID", "secret")
    sim = tmp_path / "sim.py"; sim.write_text(RECORDER)
    inp = tmp_path / "x.kicad_sch.json"; inp.write_text("{}")
    out = tmp_path / "out.json"
    wd = tmp_path / "work"
    rc, summary, _ = run_one_spice(sim, inp, out, workdir=wd)
    assert rc == 0 and summary == {"total": 1, "pass": 1}
    doc = json.loads(out.read_text())
    assert doc["workdir"] == str(wd) and doc["has_creds"] is False and doc["offline"] == "1"


def test_online_opt_in_keeps_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv("DIGIKEY_CLIENT_ID", "secret")
    from harnesslib.execution import build_env
    sim = tmp_path / "sim.py"; sim.write_text(RECORDER)
    inp = tmp_path / "x.kicad_sch.json"; inp.write_text("{}")
    out = tmp_path / "out.json"
    rc, _, _ = run_one_spice(sim, inp, out, workdir=tmp_path / "w", env=build_env(offline=False))
    assert rc == 0 and json.loads(out.read_text())["has_creds"] is True


def test_crash_leaves_no_output(tmp_path):
    sim = tmp_path / "sim.py"; sim.write_text("import sys; sys.stderr.write('x\\n'); sys.exit(3)")
    inp = tmp_path / "x.kicad_sch.json"; inp.write_text("{}")
    out = tmp_path / "out.json"
    rc, summary, _ = run_one_spice(sim, inp, out, workdir=tmp_path / "w")
    assert rc == 3 and summary is None and not out.exists() and out.with_suffix(".err").exists()


def test_success_removes_stale_err(tmp_path):
    sim = tmp_path / "sim.py"; sim.write_text(RECORDER)
    inp = tmp_path / "x.kicad_sch.json"; inp.write_text("{}")
    out = tmp_path / "out.json"
    out.with_suffix(".err").write_text("stale")
    rc, _, _ = run_one_spice(sim, inp, out, workdir=tmp_path / "w")
    assert rc == 0 and not out.with_suffix(".err").exists()


def test_outer_timeout_default_from_profile():
    import inspect
    from harnesslib.profiles import PROFILES
    default = inspect.signature(run_one_spice).parameters["outer_timeout"].default
    assert default == PROFILES["spice-offline"].timeout_s == 60


def test_unqualified_run_exits_2_without_all(tmp_path):
    env = {**os.environ, "KICAD_HAPPY_TESTHARNESS_DATA_DIR": str(tmp_path)}
    r = subprocess.run([sys.executable, str(ROOT / "run" / "run_spice.py")],
                       capture_output=True, text=True, env=env, timeout=60)
    assert r.returncode == 2, (r.returncode, r.stdout, r.stderr)
    assert "--all" in r.stderr
    assert list(tmp_path.rglob("*")) == []


def test_unit_workdir_has_no_characters_ngspice_redirects_choke_on():
    root = Path("/w")
    wd = unit_workdir(root, "0Prashant/Kicad", "LED ARRAY CIRCUIT_LED ARRAY CIRCUIT.sch")
    for part in wd.relative_to(root).parts:
        assert not any(ch.isspace() or ch in ",&'\u00b5:" for ch in part), part
    assert unit_workdir(root, "owner/repo", "plain.kicad_sch") == root / "owner/repo/plain.kicad_sch"
    assert unit_workdir(root, "o/r", "a b") != unit_workdir(root, "o/r", "a,b")
    assert unit_workdir(root, "o/r", "a b") != unit_workdir(root, "o/r", "a_b")
