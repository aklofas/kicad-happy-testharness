"""One subprocess recipe for every analyzer run.

- hermetic env (seed pinned, credentials stripped unless online)
- output written to a private temp path, validated, published atomically
- real exit code recorded; accepted-exit table per analyzer
- any failure removes the temp file and quarantines a pre-existing dest
"""
from __future__ import annotations

import json
import glob
import os
import secrets
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from .identity import sha256_file

STATUSES = ("ok", "crash", "timeout", "no_output",
            "invalid_output", "exit_unexpected")

ACCEPTED_EXITS: dict[str, frozenset[int]] = {
    "schematic": frozenset({0}), "pcb": frozenset({0}), "gerber": frozenset({0}),
    "cross_analysis": frozenset({0}),
    "emc": frozenset({0}), "thermal": frozenset({0}),
    "spice": frozenset({0}), "datasheets": frozenset({0}),
}

EXPECTED_ANALYZER_TYPE: dict[str, str] = {
    a: a for a in ("schematic", "pcb", "gerber", "thermal", "emc", "cross_analysis")
}

CREDENTIAL_PREFIXES = ("DIGIKEY_", "MOUSER_", "ELEMENT14_", "FARNELL_", "NEWARK_", "LCSC_")
OFFLINE_ENV = "KICAD_HAPPY_OFFLINE"


def build_env(*, offline: bool = True, hash_seed: str = "0",
              base: Mapping[str, str] | None = None) -> dict[str, str]:
    src = dict(os.environ if base is None else base)
    if offline:
        src = {k: v for k, v in src.items() if not k.startswith(CREDENTIAL_PREFIXES)}
        src[OFFLINE_ENV] = "1"
    else:
        src.pop(OFFLINE_ENV, None)
    src["PYTHONHASHSEED"] = hash_seed
    return src


def recorded_env(env: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    creds = any(k.startswith(CREDENTIAL_PREFIXES) for k in env)
    return (("PYTHONHASHSEED", env.get("PYTHONHASHSEED", "")),
            ("credentials_present", "true" if creds else "false"),
            ("offline", "true" if env.get(OFFLINE_ENV) == "1" else "false"))


def validate_analyzer_envelope(path: Path, analyzer: str) -> tuple[bool, str]:
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return False, "no_output"
    try:
        doc = json.loads(path.read_bytes())
    except (ValueError, RecursionError, OSError):
        return False, "invalid_output: not JSON"
    expected = EXPECTED_ANALYZER_TYPE.get(analyzer)
    if expected is not None:
        got = doc.get("analyzer_type") if isinstance(doc, dict) else None
        if got != expected:
            return False, f"invalid_output: analyzer_type {got} != {expected}"
    elif not isinstance(doc, dict):
        return False, "invalid_output: not an object"
    return True, "ok"


@dataclass
class RunResult:
    status: str
    exit_code: int | None
    output: Path | None
    output_sha256: str | None
    elapsed_s: float
    stderr_tail: str
    detail: str
    peak_rss_mb: float | None = None   # the child's ru_maxrss (None where wait4 is unavailable)


def _quarantine(dest: Path) -> None:
    if dest.exists():
        os.replace(dest, dest.with_name(dest.name + ".stale"))


def _cleanup(temp: Path) -> None:
    for p in temp.parent.glob(glob.escape(temp.name) + "*"):
        try:
            p.unlink()
        except OSError:
            pass


def _kill_group(proc: subprocess.Popen) -> None:
    """Kill the child's process group (Linux, the supported platform); where killpg does not
    exist, kill the child alone. Never raises, so the caller always reaches its quarantine."""
    killpg = getattr(os, "killpg", None)
    try:
        if killpg is not None:
            killpg(proc.pid, signal.SIGKILL)
            return
    except (ProcessLookupError, PermissionError):
        pass
    try:
        proc.kill()
    except OSError:
        pass


class _Reaped:
    """Collect a child's stdout/stderr on threads and reap it with os.wait4, so its own peak
    RSS is known (Popen.communicate reaps with waitpid and loses the rusage)."""

    def __init__(self, proc: subprocess.Popen):
        self.proc, self.out, self.err, self.rss_mb = proc, b"", b"", None
        self._readers = [threading.Thread(target=self._read, args=(name,), daemon=True)
                         for name in ("stdout", "stderr")]
        self._waiter = threading.Thread(target=self._wait, daemon=True)
        for t in (*self._readers, self._waiter):
            t.start()

    def _read(self, name):
        data = getattr(self.proc, name).read()
        setattr(self, "out" if name == "stdout" else "err", data)

    def _wait(self):
        if not hasattr(os, "wait4"):   # Windows: no rusage, peak RSS stays None
            self.proc.wait()
            return
        _pid, status, usage = os.wait4(self.proc.pid, 0)
        self.proc.returncode = os.waitstatus_to_exitcode(status)
        self.rss_mb = usage.ru_maxrss / 1024.0   # KiB on Linux

    def join(self, timeout=None) -> bool:
        """True when the child exited (and its pipes closed) within `timeout`."""
        self._waiter.join(timeout)
        if self._waiter.is_alive():
            return False
        for t in self._readers:
            t.join()
        return True


def _limit_memory(proc: subprocess.Popen, mem_limit_mb: int | None) -> None:
    if mem_limit_mb and sys.platform.startswith("linux"):
        import resource
        limit = int(mem_limit_mb) * 1024 * 1024
        try:
            resource.prlimit(proc.pid, resource.RLIMIT_AS, (limit, limit))
        except (OSError, ValueError):
            pass


def run_once(make_cmd: Callable[[Path], list[str]], dest: Path, *, analyzer: str,
             timeout: float, env: Mapping[str, str], mem_limit_mb: int | None = None) -> RunResult:
    """Run one analyzer subprocess. `mem_limit_mb` caps the child's address space (Linux
    RLIMIT_AS) so a runaway unit crashes instead of driving the host into OOM (TH-071)."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = dest.with_name(dest.name + f".tmp-{os.getpid()}-{secrets.token_hex(4)}")
    t0 = time.time()

    rss = [None]

    def fail(status, code, tail, detail):
        _cleanup(temp)
        _quarantine(dest)
        return RunResult(status, code, None, None, time.time() - t0, tail, detail, rss[0])

    try:
        try:
            cmd = make_cmd(temp)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    env=dict(env), start_new_session=True)
        except Exception as exc:  # make_cmd failure or spawn failure
            return fail("crash", None, "", f"spawn failed: {exc!r}")
        _limit_memory(proc, mem_limit_mb)
        child = _Reaped(proc)
        try:
            exited = child.join(timeout)
        except BaseException:
            _kill_group(proc)
            child.join()
            raise
        if not exited:
            _kill_group(proc)
            child.join()
            return fail("timeout", None, "", f"timeout after {timeout}s")
        err = child.err
        rss[0] = child.rss_mb
        elapsed = time.time() - t0
        tail = "\n".join((err or b"").decode("utf-8", "replace").strip().splitlines()[-5:])
        rc = proc.returncode
        ok, detail = validate_analyzer_envelope(temp, analyzer)
        if not ok:
            status = "crash" if detail == "no_output" and rc != 0 else \
                ("no_output" if detail == "no_output" else "invalid_output")
            if mem_limit_mb and "MemoryError" in tail:
                detail = f"{detail}: memory limit {mem_limit_mb} MB (MemoryError)"
            return fail(status, rc, tail, detail)
        accepted = ACCEPTED_EXITS.get(analyzer, frozenset({0}))
        if rc not in accepted:
            return fail("exit_unexpected", rc, tail,
                        f"exit {rc} not in {sorted(accepted)}")
        try:
            os.replace(temp, dest)
        except OSError as exc:
            return fail("invalid_output", rc, tail, f"publish failed: {exc}")
        return RunResult("ok", rc, dest, sha256_file(dest), elapsed, tail, "ok", rss[0])
    finally:
        _cleanup(temp)  # temp and any sidecars; harmless after a successful publish
