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


def test_kh393_power_rails_threaded(fixture_path, tmp_path):
    """KH-393 (GitHub #40): P1_VBUS doesn't look like a power net by name
    heuristics alone, so without an override it's absent from
    analyze_power_nets's output even though it's a real power rail.
    --power-rails overrides the name-based classification.

    Note: this can't be observed via return_path_continuity on this
    fixture — KH-392's antipad credit (Task 7) is net-agnostic, so
    P1_VBUS (same via/void geometry as SENSE1) already reads 100%
    coverage and is absent from that list whether it's walked as a
    signal net or skipped as a power net (see task-7-report.md
    "Concerns"). GP-001 debug samples are used below to directly prove
    call site #2 (analyze_return_path_continuity) is threaded: with
    rails supplied, P1_VBUS must be skipped *before* sampling, not just
    coincidentally covered.
    """
    # No rails: P1_VBUS doesn't match power-name heuristics -> absent from
    # power routing, classified under "heuristic" resolution.
    base = run_pcb(fixture_path, "--full")
    assert "P1_VBUS" not in {e["net"] for e in base["power_net_routing"]}
    assert base["power_net_resolution"]["source"] == "heuristic"
    assert "P1_VBUS" not in base["power_net_resolution"]["power"]

    # With rails: present in power routing, resolution source is "cli"
    fixed = run_pcb(fixture_path, "--full", "--power-rails", "P1_VBUS")
    assert "P1_VBUS" in {e["net"] for e in fixed["power_net_routing"]}
    assert fixed["power_net_resolution"]["source"] == "cli"
    assert "P1_VBUS" in fixed["power_net_resolution"]["power"]

    # GP-001 debug: P1_VBUS enters the sample loop without rails (its
    # heuristic classification lets it through as a signal net), and is
    # excluded from the loop entirely once rails are supplied.
    base_dbg_dir = tmp_path / "base_dbg"
    base_dbg_dir.mkdir()
    out = subprocess.run(
        [sys.executable, str(PCB), str(fixture_path), "--full",
         "--gp001-debug", "--analysis-dir", str(base_dbg_dir)],
        capture_output=True, text=True, timeout=120,
    )
    assert out.returncode == 0, out.stderr[-2000:]
    base_samples = json.loads((base_dbg_dir / "gp001_debug.json").read_text())["samples"]
    assert any(s["net"] == "P1_VBUS" for s in base_samples)

    fixed_dbg_dir = tmp_path / "fixed_dbg"
    fixed_dbg_dir.mkdir()
    out = subprocess.run(
        [sys.executable, str(PCB), str(fixture_path), "--full",
         "--power-rails", "P1_VBUS", "--gp001-debug",
         "--analysis-dir", str(fixed_dbg_dir)],
        capture_output=True, text=True, timeout=120,
    )
    assert out.returncode == 0, out.stderr[-2000:]
    fixed_samples = json.loads((fixed_dbg_dir / "gp001_debug.json").read_text())["samples"]
    assert not any(s["net"] == "P1_VBUS" for s in fixed_samples)


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
