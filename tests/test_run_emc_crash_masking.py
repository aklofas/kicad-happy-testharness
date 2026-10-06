"""run_emc.run_one_emc must not report success when the analyzer exits 1
without rewriting the output (TH-054: a stale output from an earlier run
masked a per-repo analyzer crash across 36k units for two regens)."""

TIER = "unit"

import os
import sys
import tempfile
import time
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HARNESS / "run"))
sys.path.insert(0, str(_HARNESS))

from run_emc import run_one_emc  # noqa: E402

CRASHING = """import sys
sys.stderr.write("Traceback (most recent call last):\\n  KeyError: 'run_id'\\n")
sys.exit(1)
"""
WRITING_RC1 = """import sys, json
out = sys.argv[sys.argv.index('--output') + 1]
json.dump({"summary": {"total_findings": 3, "critical": 1}}, open(out, 'w'))
sys.exit(1)  # exit 1 = critical findings, still valid output
"""


def _run(script_src, stale):
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        script = td / "fake_emc.py"
        script.write_text(script_src)
        sch = td / "x.kicad_sch.json"
        sch.write_text("{}")
        out = td / "x.kicad_sch.json.out"
        if stale:
            out.write_text('{"summary": {"total_findings": 99}}')
            old = time.time() - 3600
            os.utime(out, (old, old))
        rc, summary, _ = run_one_emc(script, sch, None, out)
        return rc, summary, out.with_suffix(".err").exists()


def test_crash_with_stale_output_is_reported_as_failure():
    rc, summary, err_written = _run(CRASHING, stale=True)
    assert rc != 0, "exit-1 crash behind a stale output must not be a PASS"
    assert summary is None
    assert err_written


def test_crash_without_stale_output_is_reported_as_failure():
    rc, summary, err_written = _run(CRASHING, stale=False)
    assert rc != 0 and summary is None and err_written


def test_exit_one_with_fresh_output_is_still_success():
    rc, summary, _ = _run(WRITING_RC1, stale=True)
    assert rc == 0
    assert summary == {"total_findings": 3, "critical": 1}


if __name__ == "__main__":
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
