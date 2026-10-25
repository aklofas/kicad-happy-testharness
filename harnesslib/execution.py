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
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from .identity import sha256_file

STATUSES = ("ok", "ok_findings_exit", "crash", "timeout", "no_output",
            "invalid_output", "exit_unexpected")

ACCEPTED_EXITS: dict[str, frozenset[int]] = {
    "schematic": frozenset({0}), "pcb": frozenset({0}), "gerber": frozenset({0}),
    "cross_analysis": frozenset({0}),
    "emc": frozenset({0, 1}), "thermal": frozenset({0, 1}),
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


def run_once(make_cmd: Callable[[Path], list[str]], dest: Path, *, analyzer: str,
             timeout: float, env: Mapping[str, str]) -> RunResult:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = dest.with_name(dest.name + f".tmp-{os.getpid()}-{secrets.token_hex(4)}")
    t0 = time.time()

    def fail(status, code, tail, detail):
        _cleanup(temp)
        _quarantine(dest)
        return RunResult(status, code, None, None, time.time() - t0, tail, detail)

    try:
        try:
            cmd = make_cmd(temp)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    env=dict(env), start_new_session=True)
        except Exception as exc:  # make_cmd failure or spawn failure
            return fail("crash", None, "", f"spawn failed: {exc!r}")
        try:
            _out, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_group(proc)
            proc.communicate()
            return fail("timeout", None, "", f"timeout after {timeout}s")
        except BaseException:
            _kill_group(proc)
            proc.communicate()
            raise
        elapsed = time.time() - t0
        tail = "\n".join((err or b"").decode("utf-8", "replace").strip().splitlines()[-5:])
        rc = proc.returncode
        ok, detail = validate_analyzer_envelope(temp, analyzer)
        if not ok:
            status = "crash" if detail == "no_output" and rc != 0 else \
                ("no_output" if detail == "no_output" else "invalid_output")
            return fail(status, rc, tail, detail)
        accepted = ACCEPTED_EXITS.get(analyzer, frozenset({0}))
        if rc not in accepted:
            return fail("exit_unexpected", rc, tail,
                        f"exit {rc} not in {sorted(accepted)}")
        try:
            os.replace(temp, dest)
        except OSError as exc:
            return fail("invalid_output", rc, tail, f"publish failed: {exc}")
        status = "ok" if rc == 0 else "ok_findings_exit"
        return RunResult(status, rc, dest, sha256_file(dest), elapsed, tail, "ok")
    finally:
        _cleanup(temp)  # temp and any sidecars; harmless after a successful publish
