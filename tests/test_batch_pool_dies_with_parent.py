"""Batch pool workers die with a killed parent (TH-067: 32 orphaned run_emc workers drained
the submitted queue against the live corpus after a test timeout killed their parent)."""

TIER = "unit"

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent

CHILD = r"""
import os, sys, time
sys.path.insert(0, sys.argv[1])
from harnesslib.batch import worker_pool

def task(i):
    time.sleep(30)
    return i

if __name__ == "__main__":
    with worker_pool(3) as pool:
        futs = [pool.submit(task, i) for i in range(6)]
        time.sleep(1.0)
        pids = [p for p in pool._processes]
        print(" ".join(map(str, pids)), flush=True)
        time.sleep(60)
"""


def _alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    try:   # a zombie (killed, not yet reaped by a sandbox PID 1) is not running
        return Path(f"/proc/{pid}/stat").read_text().split(")")[-1].split()[0] != "Z"
    except OSError:
        return False


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="PR_SET_PDEATHSIG is Linux-only")
def test_workers_die_when_the_parent_is_killed(tmp_path):
    script = tmp_path / "child.py"
    script.write_text(CHILD)
    proc = subprocess.Popen([sys.executable, str(script), str(HARNESS)], stdout=subprocess.PIPE, text=True)
    try:
        pids = [int(p) for p in proc.stdout.readline().split()]
        assert len(pids) == 3 and all(_alive(p) for p in pids)
        proc.send_signal(signal.SIGKILL)
        proc.wait(timeout=10)
        deadline = time.time() + 10
        while time.time() < deadline and any(_alive(p) for p in pids):
            time.sleep(0.1)
        assert not any(_alive(p) for p in pids), "pool workers outlived their killed parent"
    finally:
        if proc.poll() is None:
            proc.kill()
        for p in pids if "pids" in dir() else []:
            try:
                os.kill(p, signal.SIGKILL)
            except ProcessLookupError:
                pass
