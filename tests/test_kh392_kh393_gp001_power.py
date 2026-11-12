"""KH-392/KH-393 GP-001 antipad + power-net regression tests (harness; adopt via harness agent).

Shared fixture: tests/fixtures/kh392-antipad/board.kicad_pcb (see gen_fixture.py
in the same directory for the generator + geometry docstring). This file starts
with the KH-392 (GitHub #39) via-antipad-credit coverage; KH-393 (GitHub #40)
extends it with the P1_VBUS/VBUS power-net-detection assertions against the
same fixture.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import pytest
except ImportError:  # pre-push hook runs root tests under bare python3 (no
    # pytest); only decorator applications happen at import time, so a no-op
    # stand-in keeps the file importable — the tests themselves need pytest.
    class _StubMark:
        @staticmethod
        def skipif(*_a, **_k):
            return lambda fn: fn

    class _StubPytest:
        mark = _StubMark

        @staticmethod
        def fixture(*_a, **_k):
            return lambda fn: fn

        @staticmethod
        def skip(reason=""):
            raise SystemExit(0)

    pytest = _StubPytest

KH = Path(os.environ["KICAD_HAPPY_DIR"])
PCB = KH / "skills/kicad/scripts/analyze_pcb.py"

FIXTURE = Path(__file__).resolve().parent / "fixtures/kh392-antipad/board.kicad_pcb"


@pytest.fixture(scope="module")
def fixture_board_json(tmp_path_factory):
    """Run analyze_pcb.py --full on the kh392-antipad fixture, parse JSON."""
    outfile = tmp_path_factory.mktemp("kh392") / "board.json"
    out = subprocess.run(
        [sys.executable, str(PCB), str(FIXTURE), "--full", "--output", str(outfile)],
        capture_output=True, text=True, timeout=120,
    )
    assert out.returncode == 0, out.stderr[-2000:]
    with open(outfile) as f:
        return json.load(f)


def test_kh392_via_antipad_not_a_gap(fixture_board_json):
    """KH-392: a via's own antipad on the opposite layer must not be
    mistaken for a reference-plane gap under the trace that ends at it.

    SENSE1 (0.8mm via, 0.55mm void half-width) and SENSE2 (0.6mm via,
    0.45mm void half-width) both terminate inside their own antipad on
    B.Cu — the GP-001 sampler must credit that expected void as a hit.
    """
    rpc = fixture_board_json.get("return_path_continuity", [])
    nets = {e["net"] for e in rpc}
    assert "SENSE1" not in nets  # FAILS pre-fix: 50.0% coverage entry
    assert "SENSE2" not in nets


def test_kh392_real_gap_still_fires(fixture_board_json):
    """KH-392 control: a genuine reference-plane gap (no copper anywhere
    on the opposite layer, no via at all) must still be reported — the
    antipad fix must not blanket-suppress real GP-001 findings.
    """
    rpc = fixture_board_json.get("return_path_continuity", [])
    by_net = {e["net"]: e for e in rpc}
    assert "SENSE3" in by_net
    assert by_net["SENSE3"]["reference_plane_coverage_pct"] < 95


@pytest.fixture(scope="module")
def fixture_path():
    return FIXTURE


def run_pcb(path, *args):
    """Run analyze_pcb.py on `path` with extra CLI args, return parsed stdout JSON."""
    out = subprocess.run(
        [sys.executable, str(PCB), str(path), *args],
        capture_output=True, text=True, timeout=120,
    )
    assert out.returncode == 0, out.stderr[-2000:]
    return json.loads(out.stdout)


def _gp001_sample_nets(path, tmp_path, *args):
    """Run analyze_pcb.py --full --gp001-debug, return the set of sampled nets."""
    dbg_dir = tmp_path / "dbg"
    dbg_dir.mkdir(parents=True)
    out = subprocess.run(
        [sys.executable, str(PCB), str(path), "--full", *args,
         "--gp001-debug", "--analysis-dir", str(dbg_dir)],
        capture_output=True, text=True, timeout=120,
    )
    assert out.returncode == 0, out.stderr[-2000:]
    return {s["net"] for s in json.loads((dbg_dir / "gp001_debug.json").read_text())["samples"]}


def test_kh393_power_rails_override(fixture_path):
    """KH-393 (GitHub #40): --power-rails P1_VBUS marks the rail power and
    records the CLI as the resolution source. (P1_VBUS itself is also a
    power name to the heuristics since PR #44, so the no-override half
    lives in the SENSE1 test below.)
    """
    fixed = run_pcb(fixture_path, "--full", "--power-rails", "P1_VBUS")
    assert "P1_VBUS" in {e["net"] for e in fixed["power_net_routing"]}
    assert fixed["power_net_resolution"]["source"] == "cli"
    assert "P1_VBUS" in fixed["power_net_resolution"]["power"]


def test_kh393_power_rails_threaded(fixture_path, tmp_path):
    """KH-393: a net the name heuristics do not match (SENSE1) is absent
    from power routing without an override and present with one, and
    both call sites honour it.

    GP-001 debug samples prove call site #2 (analyze_return_path_continuity)
    is threaded: return_path_continuity cannot show it on this fixture,
    because KH-392's antipad credit already gives SENSE1 100 % coverage.
    With the rail supplied, SENSE1 must be skipped before sampling.
    """
    base = run_pcb(fixture_path, "--full")
    assert "SENSE1" not in {e["net"] for e in base["power_net_routing"]}
    assert base["power_net_resolution"]["source"] == "heuristic"
    assert "SENSE1" not in base["power_net_resolution"]["power"]

    fixed = run_pcb(fixture_path, "--full", "--power-rails", "SENSE1")
    assert "SENSE1" in {e["net"] for e in fixed["power_net_routing"]}
    assert fixed["power_net_resolution"]["source"] == "cli"
    assert "SENSE1" in fixed["power_net_resolution"]["power"]

    assert "SENSE1" in _gp001_sample_nets(fixture_path, tmp_path / "base")
    assert "SENSE1" not in _gp001_sample_nets(
        fixture_path, tmp_path / "fixed", "--power-rails", "SENSE1")


def test_kh393_rails_from_schematic_json(fixture_path, tmp_path):
    """Rails auto-read from --schematic when no --power-rails flag is given.

    power_rails lives under `statistics` in real analyze_schematic.py
    output (envelopes/schematic.py: PowerRailEntry is a Statistics field,
    not a top-level one) — this fixture mirrors that real shape.
    """
    sch_json = tmp_path / "schematic.json"
    sch_json.write_text(json.dumps({
        "findings": [],
        "statistics": {"power_rails": [{"name": "P1_VBUS", "voltage": 5.0}]},
    }))
    fixed = run_pcb(fixture_path, "--full", "--schematic", str(sch_json))
    assert "P1_VBUS" in {e["net"] for e in fixed["power_net_routing"]}
    assert fixed["power_net_resolution"]["source"] == "schematic"
    assert "P1_VBUS" in fixed["power_net_resolution"]["power"]
