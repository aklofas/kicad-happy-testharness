#!/usr/bin/env python3
"""DEPRECATED name: flag-compatible wrapper over regression/run_corpus_gate.py.

Old slots ``--v131-dir``/``--v14-dir`` map to ``--baseline-dir``/``--candidate-dir``.
Both sides always run ``--only-deterministic`` (the old ``--symmetric`` is the only
mode now). Historical trees under results/*/v131 + v14 are untouched; new runs use
baseline/ + candidate/ (see RUNBOOK Checklist 26). Kept for one release.
"""
from __future__ import annotations

import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from regression import run_corpus_gate as _gate  # noqa: E402
from regression.run_corpus_gate import _compute_pass_criteria, _print_summary  # noqa: E402,F401

_RENAME = {"--v131-dir": "--baseline-dir", "--v14-dir": "--candidate-dir"}
# Defaults of the old CLI (worktree convention in RUNBOOK 26a).
_DEFAULTS = {"--baseline-dir": "/tmp/kh-v131", "--candidate-dir": "/tmp/kh-v14",
             "--gate-dir": "results/v14_gate"}


def _note(msg):
    print(f"note: run_v14_gate.py: {msg}", file=sys.stderr)


def _need(argv, i, flag):
    if i >= len(argv):
        print(f"error: missing value for {flag}", file=sys.stderr)
        raise SystemExit(2)
    return argv[i]


def translate_argv(argv):
    out, i = [], 0
    while i < len(argv):
        a = argv[i]
        flag, eq, val = a.partition("=")
        if a == "--symmetric":
            _note("--symmetric is always on; flag ignored")
            i += 1
        elif flag == "--timeout":
            if not eq:
                i += 1
                val = _need(argv, i, flag)
            i += 1
            try:
                long_tail = int(val) > 120
            except ValueError:
                long_tail = False
            if long_tail:
                _note(f"--timeout {val} -> --profile long-tail")
                out += ["--profile", "long-tail"]
            else:
                _note(f"--timeout {val} ignored (profiles own timeouts; default profile applies)")
        elif flag in _RENAME:
            if not eq:
                i += 1
                val = _need(argv, i, flag)
            out += [_RENAME[flag], val]
            i += 1
        elif flag in ("--baseline-dir", "--candidate-dir", "--gate-dir") and not eq:
            _need(argv, i + 1, flag)
            out += [a, argv[i + 1]]
            i += 2
        else:
            out.append(a)
            i += 1
    for flag, default in _DEFAULTS.items():
        if flag not in out:
            out += [flag, default]
    return out


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    _note("wrapper over regression/run_corpus_gate.py; prefer calling that directly. "
          "Both sides run --only-deterministic.")
    return _gate.main(translate_argv(argv))


if __name__ == "__main__":
    sys.exit(main())
