"""GitHub #52 - cross_analysis.py crashed with IsADirectoryError when
--schematic / --pcb was a directory (bare open()), and with a
JSONDecodeError traceback when it was a .kicad_sch. Both are now argparse
usage errors (exit 2) naming the flag.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

import subprocess
import tempfile

_SCRIPT = os.path.join(_KH, "skills", "kicad", "scripts", "cross_analysis.py")


def _run(*args):
    return subprocess.run([sys.executable, _SCRIPT, *args],
                          capture_output=True, text=True, timeout=60)


def test_schematic_directory_is_usage_error():
    with tempfile.TemporaryDirectory() as d:
        r = _run("--schematic", d, "--pcb", d)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "Traceback" not in r.stderr, r.stderr
    assert "--schematic" in r.stderr and "directory" in r.stderr, r.stderr


def test_pcb_directory_is_usage_error():
    with tempfile.TemporaryDirectory() as d:
        sch = os.path.join(d, "schematic.json")
        with open(sch, "w") as f:
            f.write('{"components": [], "findings": [], "nets": {}}')
        r = _run("--schematic", sch, "--pcb", d)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "Traceback" not in r.stderr, r.stderr
    assert "--pcb" in r.stderr and "directory" in r.stderr, r.stderr


def test_non_json_schematic_is_usage_error():
    with tempfile.TemporaryDirectory() as d:
        sch = os.path.join(d, "board.kicad_sch")
        with open(sch, "w") as f:
            f.write("(kicad_sch (version 20260306))\n")
        r = _run("--schematic", sch)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "Traceback" not in r.stderr, r.stderr
    assert "not JSON" in r.stderr, r.stderr


def test_valid_schematic_json_still_runs():
    with tempfile.TemporaryDirectory() as d:
        sch = os.path.join(d, "schematic.json")
        with open(sch, "w") as f:
            f.write('{"components": [], "findings": [], "nets": {}}')
        r = _run("--schematic", sch, "--output", os.path.join(d, "out.json"))
    assert r.returncode == 0, (r.returncode, r.stderr)


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
