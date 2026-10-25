"""The netlist oracle's children run through the harness resolver and build_env, with a
timeout (arch V8, security end-register)."""
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
from regression import run_netlist_oracle as o  # noqa: E402

pytestmark = pytest.mark.unit

RECORDER = """import json, os, sys
out = sys.argv[sys.argv.index('--output') + 1]
json.dump({"seed": os.environ.get("PYTHONHASHSEED"), "creds": "DIGIKEY_CLIENT_ID" in os.environ,
           "cwd": os.getcwd()}, open(out, "w"))
"""


def _setup(tmp_path, monkeypatch, analyzer_src):
    kh = tmp_path / "kh"
    (kh / "skills" / "kicad" / "scripts").mkdir(parents=True)
    (kh / "skills" / "kicad" / "scripts" / "analyze_schematic.py").write_text(analyzer_src)
    (tmp_path / "board.kicad_sch").write_text("(kicad_sch)")
    monkeypatch.setattr(o, "HARNESS_DIR", tmp_path)
    monkeypatch.setattr(o, "GOLDEN", {"b": "board.kicad_sch"})
    monkeypatch.setattr(o, "export_netlist", lambda s, out, timeout=None: Path(out).write_text(""))
    seen = {}
    monkeypatch.setattr(o, "analyzer_nets", lambda p: seen.update(json.loads(Path(p).read_text())) or {})
    monkeypatch.setattr(o, "parse_netlist", lambda p: {})
    monkeypatch.setattr(o, "compare", lambda a, b: {"pass": True, "split": [], "merged": []})
    monkeypatch.setattr(o, "_apply_nc_divergence", lambda r: None)
    return kh, seen


def test_analyzer_child_gets_the_harness_env_and_a_private_cwd(tmp_path, monkeypatch):
    monkeypatch.setenv("DIGIKEY_CLIENT_ID", "secret")
    monkeypatch.delenv("PYTHONHASHSEED", raising=False)
    kh, seen = _setup(tmp_path, monkeypatch, RECORDER)
    res = o.run_board("b", kh)
    assert "error" not in res, res
    assert seen["seed"] == "0" and seen["creds"] is False
    assert Path(seen["cwd"]).name.startswith("netlist-oracle-b-")


def test_analyzer_child_times_out(tmp_path, monkeypatch):
    kh, _ = _setup(tmp_path, monkeypatch, "import time; time.sleep(30)\n")
    monkeypatch.setattr(o, "ANALYZER_TIMEOUT_S", 1)
    assert "timed out" in o.run_board("b", kh)["error"]


def test_no_home_directory_fallback():
    assert not hasattr(o, "_default_kicad_happy_dir")
    assert "~/Projects" not in (HARNESS / "regression" / "run_netlist_oracle.py").read_text()
