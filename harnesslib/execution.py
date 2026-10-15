"""One subprocess recipe for every analyzer run (report B12/A3).

- hermetic env (seed pinned, credentials stripped unless online)
- output written to a private temp path, validated, published atomically
- real exit code recorded; accepted-exit table per analyzer
- any failure removes the temp file and quarantines a pre-existing dest
"""
from __future__ import annotations

import json
import os
import secrets
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


def validate_output(path: Path, analyzer: str) -> tuple[bool, str]:
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return False, "no_output"
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
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
    for p in temp.parent.glob(temp.name + "*"):
        try:
            p.unlink()
        except OSError:
            pass


def run_once(make_cmd: Callable[[Path], list[str]], dest: Path, *, analyzer: str,
             timeout: float, env: Mapping[str, str]) -> RunResult:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = dest.with_name(dest.name + f".tmp-{os.getpid()}-{secrets.token_hex(4)}")
    cmd = make_cmd(temp)
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, env=dict(env))
    except subprocess.TimeoutExpired:
        _cleanup(temp)
        _quarantine(dest)
        return RunResult("timeout", None, None, None, time.time() - t0, "",
                         f"timeout after {timeout}s")
    elapsed = time.time() - t0
    tail = "\n".join((proc.stderr or "").strip().splitlines()[-5:])
    ok, detail = validate_output(temp, analyzer)
    if not ok:
        _cleanup(temp)
        _quarantine(dest)
        status = "crash" if detail == "no_output" and proc.returncode != 0 else \
            ("no_output" if detail == "no_output" else "invalid_output")
        return RunResult(status, proc.returncode, None, None, elapsed, tail, detail)
    accepted = ACCEPTED_EXITS.get(analyzer, frozenset({0}))
    if proc.returncode not in accepted:
        _cleanup(temp)
        _quarantine(dest)
        return RunResult("exit_unexpected", proc.returncode, None, None, elapsed, tail,
                         f"exit {proc.returncode} not in {sorted(accepted)}")
    os.replace(temp, dest)
    _cleanup(temp)  # sidecars the analyzer may have written next to the temp name
    status = "ok" if proc.returncode == 0 else "ok_findings_exit"
    return RunResult(status, proc.returncode, dest, sha256_file(dest), elapsed, tail, "ok")
