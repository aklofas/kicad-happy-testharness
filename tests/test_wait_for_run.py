import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import wait_for_run  # noqa: E402

pytestmark = pytest.mark.unit


def test_manifest_marker_requires_finished_at(tmp_path):
    m = tmp_path / "manifest.json"
    assert not wait_for_run.marker_done(m)
    m.write_text(json.dumps({"finished_at": None}))
    assert not wait_for_run.marker_done(m)
    m.write_text("{not json")
    assert not wait_for_run.marker_done(m)
    m.write_text(json.dumps({"finished_at": "2026-01-01T00:00:00+00:00"}))
    assert wait_for_run.marker_done(m)


def test_plain_marker_is_existence(tmp_path):
    d = tmp_path / "done.json"
    assert not wait_for_run.marker_done(d)
    d.write_text("{}")
    assert wait_for_run.marker_done(d)


def test_pid_alive_self_and_missing():
    assert wait_for_run.pid_alive(os.getpid())
    assert not wait_for_run.pid_alive(2**22 - 1)


def test_pid_alive_without_proc_uses_signal_zero(tmp_path):
    none = tmp_path / "none"
    assert wait_for_run.pid_alive(os.getpid(), proc_root=none)
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    assert not wait_for_run.pid_alive(child.pid, proc_root=none)


def test_pid_alive_with_proc_keeps_zombie_detection():
    child = _zombie()
    try:
        assert not wait_for_run.pid_alive(child.pid, proc_root=Path("/proc"))
    finally:
        child.wait()


def _zombie():
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    for _ in range(200):  # exits quickly; stays a zombie until we wait() on it
        stat = Path(f"/proc/{child.pid}/stat").read_text()
        if stat.rsplit(")", 1)[1].split()[0] == "Z":
            return child
        time.sleep(0.01)
    pytest.fail("child never became a zombie")


def test_zombie_counts_as_gone_even_though_kill0_succeeds():
    child = _zombie()
    try:
        os.kill(child.pid, 0)  # the trap: kill -0 still succeeds on a zombie
        assert not wait_for_run.pid_alive(child.pid)
    finally:
        child.wait()


def test_wait_returns_1_when_process_gone_without_marker(tmp_path):
    child = _zombie()
    try:
        rc = wait_for_run.wait(tmp_path / "manifest.json", child.pid, poll=0.01, timeout=5, log=None)
    finally:
        child.wait()
    assert rc == 1


def test_wait_returns_0_on_marker_and_prints_log_tail(tmp_path, capsys):
    (tmp_path / "done.json").write_text("{}")
    log = tmp_path / "run.log"
    log.write_text("\n".join(f"line {i}" for i in range(40)))
    rc = wait_for_run.wait(tmp_path / "done.json", None, poll=0.01, timeout=5, log=log)
    out = capsys.readouterr().out
    assert rc == 0 and "marker satisfied" in out and "line 39" in out and "line 10" not in out


def test_wait_times_out(tmp_path):
    assert wait_for_run.wait(tmp_path / "never.json", None, poll=0.01, timeout=0.05, log=None) == 2


def test_pid_refused_on_windows_without_signalling(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(os, "name", "nt")
    def boom(*a, **k):
        raise AssertionError("os.kill must not be called")
    monkeypatch.setattr(os, "kill", boom)
    rc = wait_for_run.main(["--marker", str(tmp_path / "m"), "--pid", "123"])
    assert rc == 2
    assert "not supported on Windows" in capsys.readouterr().err
