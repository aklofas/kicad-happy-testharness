"""Spice summary line must tolerate reports without total_elapsed_s
(degenerate/legacy inputs — regen-flagged 2026-09-01, pre-existing at 43dad23)."""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "spice", "scripts"))

from simulate_subcircuits import _summary_line  # noqa: E402


def test_summary_line_without_elapsed():
    report = {"summary": {"total": 0, "pass": 0, "warn": 0, "fail": 0, "skip": 0}}
    line = _summary_line(report)
    assert "0 subcircuits" in line and "(0.0s)" in line


def test_summary_line_with_elapsed():
    report = {"summary": {"total": 2, "pass": 1, "warn": 0, "fail": 1, "skip": 0}, "total_elapsed_s": 1.234}
    assert "(1.2s)" in _summary_line(report)


if __name__ == "__main__":
    import sys
    import traceback
    ok = fail = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                ok += 1
            except Exception:  # noqa: BLE001
                fail += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)
