"""KH-366/367/382 determinism regression tests (harness; adopt via harness agent)."""
import json, os, subprocess, sys, tempfile
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
SCH = KH / "skills/kicad/scripts/analyze_schematic.py"
PCB = KH / "skills/kicad/scripts/analyze_pcb.py"
CROSS = KH / "skills/kicad/scripts/cross_analysis.py"

REPOS = Path(__file__).resolve().parents[1] / "repos"
SEEDS = (0, 1, 2, 42, 12345, 99999)


def _run(script, target, seed, args=None, tmpdir=None):
    """Run analyzer with given PYTHONHASHSEED and return JSON output (normalized)."""
    env = dict(os.environ, PYTHONHASHSEED=str(seed))

    if tmpdir is None:
        tmpdir = tempfile.mkdtemp()
    outfile = Path(tmpdir) / f"out_{seed}.json"

    cmd = [sys.executable, str(script), str(target), "--output", str(outfile)]
    if args:
        cmd.extend(args)
    out = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=300)
    assert out.returncode == 0, out.stderr[-2000:]

    with open(outfile) as f:
        d = json.load(f)
    # Pop both inputs and capability_mode_ref to ensure byte-stability
    # across runs (run_id varies unless reusing same analysis dir)
    d.pop("inputs", None)
    d.pop("capability_mode_ref", None)
    return json.dumps(d, sort_keys=True)


def test_do_det_rail_order_stable():
    """Byte-stability regression net across PYTHONHASHSEED variation.

    Runs analyze_schematic.py 6 times on simple-project fixture with different
    hash seeds; asserts all outputs are byte-identical (minus inputs/run_id).
    General regression test for the KH-366/367/382 determinism class.
    Note: simple-project does not trigger DO-DET findings specifically;
    board-specific DO-DET validation occurs in Task 3 corpus repro.
    """
    fixture = Path(__file__).parent / "fixtures/simple-project"
    sch = next(fixture.glob("*.kicad_sch"))

    # Share ONE tmpdir across all 6 runs to keep analysis-dir stable
    tmpdir = tempfile.mkdtemp()

    outs = {_run(SCH, sch, seed, tmpdir=tmpdir) for seed in (0, 1, 2, 42, 12345, 99999)}
    assert len(outs) == 1, f"Expected 1 unique output, got {len(outs)}"


def test_xv_002_ref_order_stable():
    """KH-382: XV-002 reference iteration order must be deterministic."""
    # Generate schematic and PCB analysis on simple-project fixture
    fixture = Path(__file__).parent / "fixtures/simple-project"
    sch = next(fixture.glob("*.kicad_sch"))
    pcb = next(fixture.glob("*.kicad_pcb"))

    tmpdir = tempfile.mkdtemp()

    # Generate both analyses with seed 0
    sch_out = Path(tmpdir) / "sch.json"
    pcb_out = Path(tmpdir) / "pcb.json"

    subprocess.run([sys.executable, str(SCH), str(sch), "--output", str(sch_out)],
                   env=dict(os.environ, PYTHONHASHSEED="0"), check=True, timeout=300)
    subprocess.run([sys.executable, str(PCB), str(pcb), "--output", str(pcb_out), "--full"],
                   env=dict(os.environ, PYTHONHASHSEED="0"), check=True, timeout=300)

    # Run cross_analysis twice with different seeds; output must be byte-identical
    def _run_cross(seed):
        env = dict(os.environ, PYTHONHASHSEED=str(seed))
        outfile = Path(tmpdir) / f"cross_{seed}.json"
        out = subprocess.run([sys.executable, str(CROSS), "--schematic", str(sch_out), "--pcb", str(pcb_out), "--output", str(outfile)],
                             capture_output=True, text=True, env=env, timeout=300)
        assert out.returncode == 0, out.stderr[-2000:]
        with open(outfile) as f:
            d = json.load(f)
        d.pop("inputs", None)
        d.pop("capability_mode_ref", None)
        return json.dumps(d, sort_keys=True)

    out1 = _run_cross(0)
    out2 = _run_cross(12345)
    assert out1 == out2, "XV-002 output differs across hash seeds"


PID_SCH = REPOS / "bec5-group/pid-controller/pid/pid.sch"
M68K_SCH = REPOS / "ehbc-project/ehbc-proto1-board/projects/m68k-hbc/m68k-hbc.kicad_sch"


@pytest.mark.skipif(not PID_SCH.exists(), reason="corpus repo not present")
def test_rc_det_candidate_pick_stable():
    """KH-366: RC-DET parallel-cap candidate pick must not follow set hash order.

    Pre-fix this board produced 3 distinct outputs across these 6 seeds: the
    ``candidate_caps`` set in detect_rc_filters was iterated directly, so which
    cap won the parallel-cap merge (and the resulting cutoff_hz / finding_id)
    varied per run.
    """
    tmpdir = tempfile.mkdtemp()
    outs = {_run(SCH, PID_SCH, seed, tmpdir=tmpdir) for seed in SEEDS}
    assert len(outs) == 1, f"pid.sch: expected 1 unique output, got {len(outs)}"


@pytest.mark.skipif(not M68K_SCH.exists(), reason="corpus repo not present")
def test_en_net_identity_stable():
    """KH-367: power-sequencing EN-pin resolution must not follow set hash order.

    U20 is a multi-channel buck exposing EN1/EN2/EN3. ``_match_pin`` iterated the
    ``_EN_PIN_NAMES`` set, so power_sequencing_validation.issues[].en_net flipped
    between __unnamed_61/46/73 across runs. Post-fix it resolves to EN1.
    """
    tmpdir = tempfile.mkdtemp()
    outs = {_run(SCH, M68K_SCH, seed, tmpdir=tmpdir) for seed in SEEDS}
    assert len(outs) == 1, f"m68k-hbc: expected 1 unique output, got {len(outs)}"
