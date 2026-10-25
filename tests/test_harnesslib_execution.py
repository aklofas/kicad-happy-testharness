"""harnesslib.execution: hermetic env + temp-then-publish run_once (H0-1, B12)."""
TIER = "unit"

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harnesslib import execution as ex  # noqa: E402
from harnesslib.identity import sha256_file  # noqa: E402

FAKE = Path(__file__).resolve().parent / "fixtures" / "h0" / "plan2" / "fake_analyzer.py"


def _cmd(mode, analyzer="pcb"):
    return lambda out: [sys.executable, str(FAKE), mode, "-o", str(out), "--type", analyzer]


def _env():
    return ex.build_env(offline=True)


def test_build_env_strips_credentials_and_pins_seed():
    base = {"PATH": "/bin", "DIGIKEY_CLIENT_ID": "x", "MOUSER_API_KEY": "y",
            "PYTHONHASHSEED": "7", "HOME": "/h"}
    env = ex.build_env(offline=True, base=base)
    assert "DIGIKEY_CLIENT_ID" not in env and "MOUSER_API_KEY" not in env
    assert env["PYTHONHASHSEED"] == "0" and env["KICAD_HAPPY_OFFLINE"] == "1"
    assert env["PATH"] == "/bin"
    online = ex.build_env(offline=False, base=base)
    assert online["DIGIKEY_CLIENT_ID"] == "x" and "KICAD_HAPPY_OFFLINE" not in online
    assert ex.recorded_env(env) == (("PYTHONHASHSEED", "0"),
                                    ("credentials_present", "false"),
                                    ("offline", "true"))
    assert ex.recorded_env(online) == (("PYTHONHASHSEED", "0"),
                                       ("credentials_present", "true"),
                                       ("offline", "false"))


def test_build_env_strips_every_credential_prefix():
    base = {p + "X": "v" for p in ex.CREDENTIAL_PREFIXES}
    base["PATH"] = "/bin"
    env = ex.build_env(offline=True, base=base)
    assert set(env) == {"PATH", "PYTHONHASHSEED", "KICAD_HAPPY_OFFLINE"}


def test_validate_analyzer_envelope_checks_json_and_analyzer_type(tmp_path):
    p = tmp_path / "o.json"
    assert ex.validate_analyzer_envelope(p, "pcb") == (False, "no_output")
    p.write_text("{")
    assert ex.validate_analyzer_envelope(p, "pcb") == (False, "invalid_output: not JSON")
    p.write_text(json.dumps({"analyzer_type": "thermal"}))
    assert ex.validate_analyzer_envelope(p, "pcb") == (False, "invalid_output: analyzer_type thermal != pcb")
    p.write_text(json.dumps({"analyzer_type": "pcb"}))
    assert ex.validate_analyzer_envelope(p, "pcb") == (True, "ok")
    p.write_text(json.dumps({"summary": {}}))
    assert ex.validate_analyzer_envelope(p, "spice") == (True, "ok")


def test_run_once_ok_publishes_and_hashes(tmp_path):
    dest = tmp_path / "a" / "snap.json"
    r = ex.run_once(_cmd("ok"), dest, analyzer="pcb", timeout=20, env=_env())
    assert r.status == "ok" and r.exit_code == 0
    assert r.output == dest and r.output_sha256 == sha256_file(dest)
    assert not list(dest.parent.glob("*.tmp-*"))


def test_run_once_accepted_exit1_for_emc_is_ok_findings_exit(tmp_path):
    dest = tmp_path / "snap.json"
    r = ex.run_once(_cmd("ok_exit1", "emc"), dest, analyzer="emc", timeout=20, env=_env())
    assert r.status == "ok_findings_exit" and r.exit_code == 1 and dest.exists()


def test_run_once_valid_output_unexpected_exit_is_fail(tmp_path):
    dest = tmp_path / "snap.json"
    r = ex.run_once(_cmd("ok_exit1", "pcb"), dest, analyzer="pcb", timeout=20, env=_env())
    assert r.status == "exit_unexpected" and r.exit_code == 1
    assert not dest.exists(), "valid output with a rejected exit code must not be published"
    assert not [p for p in tmp_path.iterdir() if ".tmp-" in p.name]


def test_run_once_exit2_with_valid_output_is_exit_unexpected(tmp_path):
    dest = tmp_path / "snap.json"
    r = ex.run_once(_cmd("exit2"), dest, analyzer="pcb", timeout=20, env=_env())
    assert r.status == "exit_unexpected" and r.exit_code == 2 and not dest.exists()


def test_run_once_no_output_is_crash_with_stderr(tmp_path):
    dest = tmp_path / "snap.json"
    r = ex.run_once(_cmd("nothing"), dest, analyzer="pcb", timeout=20, env=_env())
    assert r.status == "crash" and r.exit_code == 2 and "boom" in r.stderr_tail
    assert not dest.exists()


def test_run_once_exit0_without_output_is_no_output(tmp_path):
    dest = tmp_path / "snap.json"
    r = ex.run_once(lambda out: [sys.executable, "-c", "pass"], dest, analyzer="pcb",
                    timeout=20, env=_env())
    assert r.status == "no_output" and r.exit_code == 0 and not dest.exists()


def test_run_once_garbage_output_is_invalid_output(tmp_path):
    dest = tmp_path / "snap.json"
    r = ex.run_once(_cmd("garbage"), dest, analyzer="pcb", timeout=20, env=_env())
    assert r.status == "invalid_output" and not dest.exists()
    assert not [p for p in tmp_path.iterdir() if ".tmp-" in p.name]


def test_run_once_wrong_analyzer_type_is_invalid_output(tmp_path):
    dest = tmp_path / "snap.json"
    r = ex.run_once(_cmd("ok_wrong_type"), dest, analyzer="pcb", timeout=20, env=_env())
    assert r.status == "invalid_output" and "thermal != pcb" in r.detail


def test_run_once_timeout_quarantines_and_cleans(tmp_path):
    dest = tmp_path / "snap.json"
    dest.write_text('{"analyzer_type": "pcb", "old": true}')
    r = ex.run_once(_cmd("sleep"), dest, analyzer="pcb", timeout=1, env=_env())
    assert r.status == "timeout" and r.exit_code is None
    assert not dest.exists()
    stale = dest.with_name(dest.name + ".stale")
    assert stale.exists() and json.loads(stale.read_text())["old"] is True
    assert not [p for p in tmp_path.iterdir() if ".tmp-" in p.name]


def test_run_once_failure_quarantines_previous_output(tmp_path):
    dest = tmp_path / "snap.json"
    dest.write_text('{"analyzer_type": "pcb"}')
    ex.run_once(_cmd("nothing"), dest, analyzer="pcb", timeout=20, env=_env())
    assert not dest.exists() and dest.with_name("snap.json.stale").exists()


def test_statuses_vocabulary():
    assert ex.STATUSES == ("ok", "ok_findings_exit", "crash", "timeout", "no_output",
                           "invalid_output", "exit_unexpected")


def _no_temp(tmp_path):
    return not [p for p in tmp_path.iterdir() if ".tmp-" in p.name]


def test_run_once_binary_output_is_invalid_output(tmp_path):
    dest = tmp_path / "snap.json"
    r = ex.run_once(_cmd("binary"), dest, analyzer="pcb", timeout=20, env=_env())
    assert r.status == "invalid_output" and not dest.exists() and _no_temp(tmp_path)


def test_run_once_non_utf8_stderr_is_decoded(tmp_path):
    dest = tmp_path / "snap.json"
    r = ex.run_once(_cmd("badstderr"), dest, analyzer="pcb", timeout=20, env=_env())
    assert r.status == "ok" and "bad" in r.stderr_tail and dest.exists()


def test_run_once_missing_executable_is_crash_and_quarantines(tmp_path):
    dest = tmp_path / "snap.json"
    dest.write_text('{"analyzer_type": "pcb"}')
    r = ex.run_once(lambda out: [str(tmp_path / "no-such-exe"), str(out)], dest,
                    analyzer="pcb", timeout=20, env=_env())
    assert r.status == "crash" and r.exit_code is None
    assert not dest.exists() and dest.with_name("snap.json.stale").exists()
    assert _no_temp(tmp_path)


def test_run_once_make_cmd_exception_is_crash(tmp_path):
    def boom(out):
        raise ValueError("bad cmd")
    r = ex.run_once(boom, tmp_path / "snap.json", analyzer="pcb", timeout=5, env=_env())
    assert r.status == "crash" and "bad cmd" in r.detail and _no_temp(tmp_path)


def test_run_once_publish_failure_is_invalid_output(tmp_path, monkeypatch):
    dest = tmp_path / "snap.json"
    real = os.replace

    def flaky(src, dst):
        if str(dst) == str(dest):
            raise OSError("disk full")
        return real(src, dst)
    monkeypatch.setattr(ex.os, "replace", flaky)
    r = ex.run_once(_cmd("ok"), dest, analyzer="pcb", timeout=20, env=_env())
    assert r.status == "invalid_output" and r.detail.startswith("publish failed")
    assert not dest.exists() and _no_temp(tmp_path)


def test_run_once_timeout_with_grandchild_returns_promptly(tmp_path):
    import time
    dest = tmp_path / "snap.json"
    t0 = time.time()
    r = ex.run_once(_cmd("sleep-grandchild"), dest, analyzer="pcb", timeout=1, env=_env())
    assert r.status == "timeout"
    assert time.time() - t0 < 6
    assert _no_temp(tmp_path)


def test_timeout_reaches_quarantine_without_killpg(tmp_path, monkeypatch):
    """code A3-F12: where os.killpg does not exist the AttributeError escaped _kill_group and
    skipped the timeout quarantine."""
    dest = tmp_path / "out.json"
    dest.write_text('{"old": true}')
    monkeypatch.delattr(ex.os, "killpg")
    r = ex.run_once(_cmd("sleep"), dest, analyzer="pcb", timeout=1, env=_env())
    assert r.status == "timeout" and not dest.exists()
    assert dest.with_name("out.json.stale").exists()
