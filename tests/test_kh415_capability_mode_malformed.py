"""KH-415 — capability_mode.get_or_create_capability_mode accepted ANY JSON
dict at <analysis_dir>/capability_mode.json as the run record, and
get_capability_mode_ref indexed record["run_id"] unguarded: a sidecar holding
an analyzer envelope (TH-050 harness garbage, 5,843 dirs) crashed every
analyzer at startup with KeyError: 'run_id' and no output (TH-054).
Now: malformed → stderr warning, file untouched, fresh in-memory record.
"""

TIER = "unit"

import io
import json
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy")))
sys.path.insert(0, str(_KH / "skills" / "kicad" / "scripts"))

import capability_mode

GARBAGE = {"analyzer_type": "emc", "schema_version": "1.0", "findings": []}


def _dir_with(content: str):
    d = Path(tempfile.mkdtemp(prefix="kh415-"))
    (d / "capability_mode.json").write_text(content)
    return d


def test_envelope_as_sidecar_does_not_crash_and_is_left_alone():
    d = _dir_with(json.dumps(GARBAGE))
    before = (d / "capability_mode.json").read_bytes()
    err = io.StringIO()
    with redirect_stderr(err):
        ref = capability_mode.get_capability_mode_ref(d)
    assert set(ref) == {"source", "run_id"} and isinstance(ref["run_id"], str) and ref["run_id"], ref
    assert (d / "capability_mode.json").read_bytes() == before
    assert "capability_mode.json" in err.getvalue() and "run_id" in err.getvalue(), err.getvalue()


def test_non_dict_json_sidecar_does_not_crash():
    for content in ("[]", '"x"', "42"):
        d = _dir_with(content)
        with redirect_stderr(io.StringIO()):
            rid = capability_mode.get_or_create_run_id(d)
        assert isinstance(rid, str) and rid, (content, rid)
        assert (d / "capability_mode.json").read_text() == content


def test_valid_record_returned_verbatim():
    d = Path(tempfile.mkdtemp(prefix="kh415-"))
    first = capability_mode.get_or_create_capability_mode(d)
    again = capability_mode.get_or_create_capability_mode(d)
    assert again == first and again["run_id"] == first["run_id"]


def test_is_valid_record():
    ok = capability_mode._is_valid_record
    assert ok({"run_id": "20261005T000000Z-abc123"})
    assert not ok({"run_id": ""})
    assert not ok({"run_id": 5})
    assert not ok(GARBAGE)
    assert not ok([]) and not ok(None) and not ok("x")


def test_analyzers_run_end_to_end_with_garbage_sidecar():
    sch = _HARNESS / "tests/fixtures/simple-project/simple.kicad_sch"
    d = _dir_with(json.dumps(GARBAGE))
    out = subprocess.run([sys.executable, str(_KH / "skills/kicad/scripts/analyze_schematic.py"),
                          str(sch), "--output", str(d / "schematic.json")],
                         capture_output=True, text=True, timeout=180)
    assert out.returncode == 0, out.stderr[-2000:]
    assert (d / "schematic.json").exists()
    emc = subprocess.run([sys.executable, str(_KH / "skills/emc/scripts/analyze_emc.py"),
                          "--schematic", str(d / "schematic.json"), "--output", str(d / "emc.json")],
                         capture_output=True, text=True, timeout=180)
    assert emc.returncode == 0, emc.stderr[-2000:]
    assert (d / "emc.json").exists()


if __name__ == "__main__":
    import sys as _sys
    tests = [(name, fn) for name, fn in globals().items()
             if name.startswith("test_") and callable(fn)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except (AssertionError, KeyError, AttributeError) as e:
            failed += 1
            print(f"  FAIL: {name}: {e!r}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    _sys.exit(1 if failed else 0)
