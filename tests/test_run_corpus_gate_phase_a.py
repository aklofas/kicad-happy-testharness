# tests/test_run_corpus_gate_phase_a.py
"""run_corpus_gate Phase A: baseline/candidate slots, run_once statuses, complete deltas."""
TIER = "unit"

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from regression import run_corpus_gate as gate  # noqa: E402
from harnesslib.profiles import PROFILES  # noqa: E402

FAKE = ROOT / "tests" / "fixtures" / "h0" / "plan2" / "fake_analyzer.py"


def _worktree(tmp_path, name, mode):
    wt = tmp_path / name
    scripts = wt / "skills" / "kicad" / "scripts"
    scripts.mkdir(parents=True)
    # the gate calls <script> <input> -o <out> [flags]; route mode via a wrapper
    (scripts / "analyze_pcb.py").write_text(
        "import sys, subprocess\n"
        f"sys.exit(subprocess.call([sys.executable, {str(FAKE)!r}, {mode!r}, '-o', "
        "sys.argv[sys.argv.index('-o') + 1], '--type', 'pcb']))\n")
    return wt


def test_layout_uses_baseline_candidate_slots(tmp_path):
    lay = gate.GateLayout(tmp_path / "g")
    snap = lay.snap("baseline", "pcb", "o/r", "b.kicad_pcb")
    assert snap == tmp_path / "g" / "baseline" / "pcb" / "o" / "r" / "b.kicad_pcb" / "snap.json"
    assert lay.diff("pcb", "o/r", "b.kicad_pcb") == tmp_path / "g" / "diff" / "pcb" / "o" / "r" / "b.kicad_pcb.json"
    assert lay.manifest == tmp_path / "g" / "manifest.json"


def test_file_cmd_follows_profile():
    std = gate.file_cmd("pcb", "/wt", "/in/b.kicad_pcb", "/out/snap.json", PROFILES["standard"])
    assert std[1].endswith("skills/kicad/scripts/analyze_pcb.py")
    assert "--only-deterministic" in std and "--full" not in std
    full = gate.file_cmd("pcb", "/wt", "/in/b.kicad_pcb", "/out/snap.json", PROFILES["full-chain"])
    assert "--full" in full
    sch = gate.file_cmd("schematic", "/wt", "/in/a.kicad_sch", "/o.json", PROFILES["standard"])
    assert "--no-hierarchy" in sch
    assert "--no-hierarchy" not in gate.file_cmd("schematic", "/wt", "/in/a.kicad_sch", "/o.json", PROFILES["hierarchy"])


def test_phase_a_job_records_both_sides_and_passes(tmp_path):
    base = _worktree(tmp_path, "base", "ok")
    cand = _worktree(tmp_path, "cand", "ok")
    board = tmp_path / "repos" / "o" / "r" / "b.kicad_pcb"
    board.parent.mkdir(parents=True); board.write_text("(kicad_pcb)")
    lay = gate.GateLayout(tmp_path / "g")
    rec = gate.phase_a_job(("pcb", str(board), "o/r", str(base), str(cand),
                            str(lay.root), "standard"))
    assert rec["verdict"] == "PASS" and rec["analyzer"] == "pcb"
    assert rec["baseline"]["status"] == "ok" and rec["candidate"]["status"] == "ok"
    assert len(rec["input_sha256"]) == 64 and rec["unit_id"] == "o/r/b.kicad_pcb"
    assert lay.snap("baseline", "pcb", "o/r", "b.kicad_pcb").exists()
    assert json.loads(lay.diff("pcb", "o/r", "b.kicad_pcb").read_text())["_record"]["verdict"] == "PASS"


def test_phase_a_candidate_unexpected_exit_is_fail(tmp_path):
    base = _worktree(tmp_path, "base", "ok")
    cand = _worktree(tmp_path, "cand", "ok_exit1")
    board = tmp_path / "repos" / "o" / "r" / "b.kicad_pcb"
    board.parent.mkdir(parents=True); board.write_text("(kicad_pcb)")
    lay = gate.GateLayout(tmp_path / "g")
    rec = gate.phase_a_job(("pcb", str(board), "o/r", str(base), str(cand), str(lay.root), "standard"))
    assert rec["verdict"] == "FAIL" and rec["candidate"]["status"] == "exit_unexpected"
    assert rec["candidate"]["exit_code"] == 1


def test_phase_a_both_crash_is_skip_both_failed(tmp_path):
    base = _worktree(tmp_path, "base", "nothing")
    cand = _worktree(tmp_path, "cand", "nothing")
    board = tmp_path / "repos" / "o" / "r" / "b.kicad_pcb"
    board.parent.mkdir(parents=True); board.write_text("(kicad_pcb)")
    lay = gate.GateLayout(tmp_path / "g")
    rec = gate.phase_a_job(("pcb", str(board), "o/r", str(base), str(cand), str(lay.root), "standard"))
    assert rec["verdict"] == "SKIP" and rec["reason"] == "both_failed"


def test_diff_envelopes_keeps_complete_lists(tmp_path):
    a = tmp_path / "a.json"; b = tmp_path / "b.json"
    findings = [{"rule_id": f"XX-00{i}", "detector": "d", "severity": "warning",
                 "summary": f"s{i}", "components": [f"R{i}"]} for i in range(8)]
    a.write_text(json.dumps({"analyzer_type": "schematic", "findings": findings}))
    b.write_text(json.dumps({"analyzer_type": "schematic", "findings": []}))
    d = gate.diff_envelopes(a, b, True, True)
    assert d["verdict"] == "FAIL" and d["disappeared_count"] == 8
    assert len(d["disappeared"]) == 8, "no top-five truncation (report A3)"


def test_expected_census_counts_phase_a_units():
    jobs = [("pcb", "/x.kicad_pcb", "o/r", "", "", "", "standard"),
            ("pcb", "/y.kicad_pcb", "o/r", "", "", "", "standard"),
            ("schematic", "/z.kicad_sch", "o/r", "", "", "", "standard")]
    assert gate.expected_census(jobs) == {"pcb": 2, "schematic": 1}
