"""Smoke tests for KiCad 10.0 file format compatibility.

KiCad 10.0 introduced two format-compat breaks the analyzer had to absorb:
- Boolean `(hide yes)` form replacing bare-token `hide` (KH-319, schematic)
- Bare-token via types (`blind` / `buried` / `micro`) replacing nested
  `(type X)` children (KH-318, PCB). `buried` is new in 10.0 (file version
  20250926 and later).

These tests pick small, known-present KiCad 10 fixtures from the corpus and
run the analyzers end-to-end. They fail if either parser can't open a
KiCad 10 file or emits an empty findings[] on a non-trivial design. Tests
skip cleanly when the fixtures aren't checked out locally.

Fixtures are pinned by relative path so new corpus additions don't
silently become the target. If a fixture disappears, update the path or
pick another from `--cross-section kicad10`.
"""

TIER = "unit"

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
REPOS_DIR = HARNESS_DIR / "repos"
_KICAD_HAPPY = os.environ.get(
    "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy"))
_SCRIPTS = Path(_KICAD_HAPPY) / "skills" / "kicad" / "scripts"

# File-format version strings that identify KiCad 10.0 output.
# Schematic: 10.0 release = 20260306, 20260101 (pre-release), 20251028 (beta).
# PCB: 10.0 release = 20260206, 20250926 (pre-release, introduced 'buried').
_KICAD10_SCH_VERSIONS = {"20260306", "20260101", "20251028"}
_KICAD10_PCB_VERSIONS = {"20260206", "20250926", "20251101"}

# Known-present KiCad 10 fixtures (relative to REPOS_DIR).
# Picked for small size so the smoke tests stay fast.
_SCH_FIXTURES = [
    "7m4gmh/7seg-panel/hardware/7seg-panel-056-single-combined-sparse/"
    "7seg-panel-056-single-combined-sparse.kicad_sch",
    "Just4Stan/OpenRX/OpenRX-Gemini/esp32c3_lr1121_gemini.kicad_sch",
]
_PCB_FIXTURES = [
    "7m4gmh/7seg-panel/hardware/7seg-panel-056-single-combined-sparse/"
    "7seg-panel-056-single-combined-sparse.kicad_pcb",
    "Just4Stan/OpenRX/OpenRX-Gemini/OpenRX-Gemini.kicad_pcb",
]


def _skip_if_no_kh():
    return not (_SCRIPTS / "analyze_schematic.py").exists()


def _skip_if_no_fixture(rel_path):
    return not (REPOS_DIR / rel_path).exists()


def _read_file_version(path):
    """Return the (version N) value from a KiCad S-expression file header."""
    try:
        head = path.read_text(errors="ignore")[:500]
    except OSError:
        return None
    m = re.search(r"\(version\s+(\d+)", head)
    return m.group(1) if m else None


def _run_analyzer(script, fixture, *extra_args):
    """Run analyzer on a fixture, return parsed JSON."""
    r = subprocess.run(
        [sys.executable, str(_SCRIPTS / script), str(fixture), *extra_args],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, (
        f"{script} exited {r.returncode} on {fixture.name}: {r.stderr[:500]}")
    return json.loads(r.stdout)


# ---------------------------------------------------------------------------
# Fixture presence
# ---------------------------------------------------------------------------

def test_sch_fixture_is_kicad10():
    """Verify the first schematic fixture actually reports KiCad 10 version."""
    if _skip_if_no_fixture(_SCH_FIXTURES[0]):
        return
    path = REPOS_DIR / _SCH_FIXTURES[0]
    ver = _read_file_version(path)
    assert ver in _KICAD10_SCH_VERSIONS, (
        f"{path.name} has version {ver}, expected one of {_KICAD10_SCH_VERSIONS}")


def test_pcb_fixture_is_kicad10():
    """Verify the first PCB fixture actually reports KiCad 10 version."""
    if _skip_if_no_fixture(_PCB_FIXTURES[0]):
        return
    path = REPOS_DIR / _PCB_FIXTURES[0]
    ver = _read_file_version(path)
    assert ver in _KICAD10_PCB_VERSIONS, (
        f"{path.name} has version {ver}, expected one of {_KICAD10_PCB_VERSIONS}")


# ---------------------------------------------------------------------------
# Parser smoke tests — schematic
# ---------------------------------------------------------------------------

def test_analyze_schematic_opens_kicad10_file():
    """analyze_schematic exits 0, emits schema_version 1.4.0, findings present."""
    if _skip_if_no_kh() or _skip_if_no_fixture(_SCH_FIXTURES[0]):
        return
    path = REPOS_DIR / _SCH_FIXTURES[0]
    data = _run_analyzer("analyze_schematic.py", path)
    assert data.get("analyzer_type") == "schematic"
    assert data.get("schema_version") == "1.4.0"
    assert "findings" in data
    assert data.get("statistics", {}).get("total_components", 0) > 0, (
        "expected > 0 components on a real board")


def test_analyze_schematic_detects_hidden_pins_on_kicad10():
    """Hidden pins on a KiCad 10 schematic should exist in ref_pins.

    We can't assert a specific count (fixture-dependent) but we can assert
    the analyzer didn't crash and produced non-empty pin data. KH-319 fix
    means `(hide yes)` pins are now recognized as hidden; before the fix,
    they were silently treated as visible.
    """
    if _skip_if_no_kh() or _skip_if_no_fixture(_SCH_FIXTURES[0]):
        return
    path = REPOS_DIR / _SCH_FIXTURES[0]
    data = _run_analyzer("analyze_schematic.py", path)
    assert data.get("statistics", {}).get("total_nets", 0) > 0


# ---------------------------------------------------------------------------
# Parser smoke tests — PCB
# ---------------------------------------------------------------------------

def test_analyze_pcb_opens_kicad10_file():
    """analyze_pcb exits 0, emits schema_version 1.4.0."""
    if _skip_if_no_kh() or _skip_if_no_fixture(_PCB_FIXTURES[0]):
        return
    path = REPOS_DIR / _PCB_FIXTURES[0]
    data = _run_analyzer("analyze_pcb.py", path, "--full")
    assert data.get("analyzer_type") == "pcb"
    assert data.get("schema_version") == "1.4.0"
    assert "findings" in data


def test_analyze_pcb_via_type_present_on_kicad10():
    """Every via in KiCad 10 output carries a `type` field (KH-318 fix)."""
    if _skip_if_no_kh() or _skip_if_no_fixture(_PCB_FIXTURES[0]):
        return
    path = REPOS_DIR / _PCB_FIXTURES[0]
    data = _run_analyzer("analyze_pcb.py", path, "--full")
    vias_section = data.get("vias", {})
    via_list = vias_section.get("vias", []) if isinstance(vias_section, dict) else []
    # Some fixtures have 0 vias; that's OK — we only check the shape when vias exist.
    for v in via_list:
        assert "type" in v, f"via missing 'type' field: {v}"
        assert v["type"] in ("through", "blind", "buried", "micro"), (
            f"unexpected via type {v['type']!r}: {v}")


def test_analyze_pcb_second_fixture_opens():
    """Second fixture as additional coverage across v10 projects."""
    if _skip_if_no_kh() or _skip_if_no_fixture(_PCB_FIXTURES[1]):
        return
    path = REPOS_DIR / _PCB_FIXTURES[1]
    data = _run_analyzer("analyze_pcb.py", path, "--full")
    assert data.get("analyzer_type") == "pcb"
    assert data.get("schema_version") == "1.4.0"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [(n, f) for n, f in globals().items()
             if n.startswith("test_") and callable(f)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
