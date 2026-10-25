"""Wait for a long harness run (gate, baseline, full-chain) to finish — without pgrep.

Polls until the completion marker is satisfied or the launched process is gone.
"Gone" includes zombies: a `setsid nohup ... &` parent whose launching shell has
exited lingers in state Z, and `kill -0` keeps succeeding on it, so PID-only
waiters never return. Command lines are never matched, so the waiter cannot
match itself the way `pgrep -f "<pattern>"` does when the pattern sits in the
waiter's own argv.

Zombie detection needs Linux /proc; where /proc is absent, --pid checks existence only
(signal 0).

Markers:
  <gate-dir>/manifest.json   run_corpus_gate — done when "finished_at" is non-null
  <out>/done.json            full_chain_baseline — done when the file exists
  any other path             done when the file exists

Usage:
  python3 tools/wait_for_run.py --marker results/<gate>/manifest.json [--pid N]
                                [--poll 30] [--timeout 43200] [--log results/<gate>.log]

Exit 0: marker satisfied. 1: process gone (dead or zombie) without a marker.
2: timeout or bad arguments.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


def marker_done(path: Path) -> bool:
    if not path.exists():
        return False
    if path.name != "manifest.json":
        return True
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("finished_at") is not None
    except (OSError, ValueError):
        return False  # being rewritten; try again next poll


def pid_alive(pid: int, proc_root: Path = Path("/proc")) -> bool:
    """True while the process exists and, with /proc, is not a zombie/dead."""
    if not proc_root.is_dir():
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True
    try:
        stat = (proc_root / str(pid) / "stat").read_text()
    except OSError:
        return False
    state = stat.rsplit(")", 1)[1].split()[0]  # field after the parenthesised comm
    return state not in ("Z", "X")


def wait(marker: Path, pid: int | None, poll: float, timeout: float, log: Path | None) -> int:
    deadline = time.monotonic() + timeout
    while True:
        if marker_done(marker):
            rc = 0
            break
        if pid is not None and not pid_alive(pid):
            rc = 1
            break
        if time.monotonic() >= deadline:
            rc = 2
            break
        time.sleep(poll)
    print({0: "done: marker satisfied", 1: "process gone without marker", 2: "timeout"}[rc],
          f"({marker})")
    if log and log.exists():
        tail = log.read_text(encoding="utf-8", errors="replace").splitlines()[-15:]
        print("\n".join(tail))
    return rc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--marker", required=True, type=Path)
    ap.add_argument("--pid", type=int)
    ap.add_argument("--poll", type=float, default=30.0)
    ap.add_argument("--timeout", type=float, default=12 * 3600)
    ap.add_argument("--log", type=Path)
    args = ap.parse_args(argv)
    if args.poll <= 0 or args.timeout <= 0:
        print("--poll and --timeout must be positive", file=sys.stderr)
        return 2
    return wait(args.marker, args.pid, args.poll, args.timeout, args.log)


if __name__ == "__main__":
    sys.exit(main())
