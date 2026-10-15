"""run_emc / run_thermal use the shared run_once recipe: accepted exit {0,1},
unexpected exit is a failure, previous output quarantined (B12).

Runner subprocesses must always set KICAD_HAPPY_TESTHARNESS_DATA_DIR to tmp_path
— never run a mutating runner against the live tree in a test.
"""
TIER = "unit"

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "run"))

from run_emc import run_one_emc  # noqa: E402
from run_thermal import run_one_thermal  # noqa: E402

FAKE = ROOT / "tests" / "fixtures" / "h0" / "plan2" / "fake_analyzer.py"


def _script(tmp_path, mode, atype):
    # chained analyzers take --schematic/--output; the fake reads -o, so wrap it
    s = tmp_path / f"fake_{atype}.py"
    s.write_text(
        "import sys, subprocess\n"
        "argv = sys.argv[1:]\n"
        "out = argv[argv.index('--output') + 1]\n"
        f"sys.exit(subprocess.call([sys.executable, {str(FAKE)!r}, {mode!r}, '-o', out, "
        f"'--type', {atype!r}]))\n")
    return s


def _inputs(tmp_path):
    sch = tmp_path / "x.kicad_sch.json"
    sch.write_text("{}")
    pcb = tmp_path / "x.kicad_pcb.json"
    pcb.write_text("{}")
    return sch, pcb


def test_emc_exit1_with_output_is_success(tmp_path):
    sch, _ = _inputs(tmp_path)
    out = tmp_path / "emc.json"
    rc, summary, _ = run_one_emc(_script(tmp_path, "ok_exit1", "emc"), sch, None, out)
    assert rc == 0 and summary == {"total_findings": 0} and out.exists()


def test_emc_exit2_is_failure_and_quarantines(tmp_path):
    sch, _ = _inputs(tmp_path)
    out = tmp_path / "emc.json"
    out.write_text('{"analyzer_type": "emc", "old": 1}')
    rc, summary, _ = run_one_emc(_script(tmp_path, "exit2", "emc"), sch, None, out)
    assert rc == 2 and summary is None
    assert not out.exists() and out.with_name("emc.json.stale").exists()
    assert out.with_suffix(".err").exists()


def test_emc_timeout_returns_none_and_no_output(tmp_path):
    sch, _ = _inputs(tmp_path)
    out = tmp_path / "emc.json"
    rc, summary, _ = run_one_emc(_script(tmp_path, "sleep", "emc"), sch, None, out,
                                 timeout=1)
    assert rc is None and summary is None and not out.exists()
    assert "timeout" in out.with_suffix(".err").read_text()


def test_emc_flags_and_pcb_pairing_reach_analyzer(tmp_path):
    sch, pcb = _inputs(tmp_path)
    argv_log = tmp_path / "argv.txt"
    s = tmp_path / "rec.py"
    s.write_text(
        "import sys, json\n"
        f"open({str(argv_log)!r}, 'w').write(' '.join(sys.argv[1:]))\n"
        "out = sys.argv[sys.argv.index('--output') + 1]\n"
        "json.dump({'analyzer_type': 'emc', 'summary': {}}, open(out, 'w'))\n")
    out = tmp_path / "emc.json"
    rc, _, _ = run_one_emc(s, sch, pcb, out, standard="cispr-class-b",
                           spice_enhanced=True, compact=True)
    argv = argv_log.read_text().split()
    assert rc == 0
    assert argv[argv.index("--standard") + 1] == "cispr-class-b"
    assert argv[argv.index("--pcb") + 1] == str(pcb)
    assert "--compact" in argv and "--spice-enhanced" in argv


def test_thermal_exit1_with_output_is_success(tmp_path):
    sch, pcb = _inputs(tmp_path)
    out = tmp_path / "x_thermal.json"
    rc, summary, _ = run_one_thermal(_script(tmp_path, "ok_exit1", "thermal"),
                                     sch, pcb, out)
    assert rc == 0 and summary == {"total_findings": 0} and out.exists()


def test_thermal_garbage_output_is_failure(tmp_path):
    sch, pcb = _inputs(tmp_path)
    out = tmp_path / "x_thermal.json"
    rc, summary, _ = run_one_thermal(_script(tmp_path, "garbage", "thermal"), sch, pcb, out)
    assert rc == 0 and summary is None and not out.exists()
    assert "invalid_output" in out.with_suffix(".err").read_text()


def test_thermal_crash_quarantines_stale(tmp_path):
    sch, pcb = _inputs(tmp_path)
    out = tmp_path / "x_thermal.json"
    out.write_text('{"analyzer_type": "thermal"}')
    rc, summary, _ = run_one_thermal(_script(tmp_path, "nothing", "thermal"), sch, pcb, out)
    assert rc == 2 and summary is None
    assert not out.exists() and out.with_name("x_thermal.json.stale").exists()


def test_thermal_default_timeout_from_standard_profile():
    from harnesslib.profiles import PROFILES
    import run_thermal
    assert run_thermal.ANALYZER_TIMEOUT == PROFILES["standard"].timeout_s


def test_unqualified_runs_exit_2_without_all(tmp_path):
    env = {**os.environ, "KICAD_HAPPY_TESTHARNESS_DATA_DIR": str(tmp_path)}
    for name in ("run_emc.py", "run_thermal.py"):
        r = subprocess.run([sys.executable, str(ROOT / "run" / name)],
                           capture_output=True, text=True, env=env, timeout=60)
        assert r.returncode == 2, (name, r.returncode, r.stderr)
        assert "--all" in r.stderr
    assert not any((tmp_path / "outputs").rglob("*")) if (tmp_path / "outputs").exists() else True


def test_success_removes_stale_err(tmp_path):
    sch, pcb = _inputs(tmp_path)
    out = tmp_path / "x_thermal.json"
    out.with_suffix(".err").write_text("old failure")
    rc, _, _ = run_one_thermal(_script(tmp_path, "ok", "thermal"), sch, pcb, out)
    assert rc == 0 and not out.with_suffix(".err").exists()
