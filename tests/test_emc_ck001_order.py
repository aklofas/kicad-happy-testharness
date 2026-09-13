"""EMC CK-001 (check_clock_routing) finding order was hash-seed dependent.

``for net_name in clock_nets:`` iterated a set built up from schematic
crystal/bus nets plus name-matched PCB nets -- iteration order followed
Python's string hash, so the CK-001 finding order (and therefore
``finding_id`` assignment order for same-severity findings) flipped across
interpreter runs with different ``PYTHONHASHSEED``. Fixed by sorting the
net names before iterating. This is a pre-existing bug, unrelated to any
specific corpus board -- reproduced on hackrf-one (has multiple clock nets:
crystal + SPI/I2S/name-matched)."""

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
ANALYZE_EMC = os.path.join(_KH, "skills", "emc", "scripts", "analyze_emc.py")

# Corpus outputs of greatscottgadgets/hackrf hackrf-one (the 13 MB schematic
# JSON is too large to carry as a fixture; any analyzer version of the board
# works for a seed-invariance check). Skipped when the corpus outputs are
# absent (fresh checkout / CI).
_OUT = _HARNESS / "results" / "outputs"
SCH = _OUT / "schematic" / "greatscottgadgets" / "hackrf" / "hardware_hackrf-one_hackrf-one.kicad_sch.json"
PCB = _OUT / "pcb" / "greatscottgadgets" / "hackrf" / "hardware_hackrf-one_hackrf-one.kicad_pcb.json"

SEEDS = (1, 7, 123)


def _run(seed, tmpdir):
    env = dict(os.environ, PYTHONHASHSEED=str(seed))
    outfile = Path(tmpdir) / f"emc_{seed}.json"
    cmd = [sys.executable, ANALYZE_EMC,
           "--schematic", str(SCH), "--pcb", str(PCB),
           "--output", str(outfile)]
    out = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=300)
    assert out.returncode == 0, out.stderr[-2000:]
    with open(outfile) as f:
        d = json.load(f)
    for key in ("inputs", "capability_mode_ref", "elapsed_s"):
        d.pop(key, None)
    return json.dumps(d, sort_keys=True)


def test_ck001_order_stable_across_hash_seeds():
    if not (SCH.exists() and PCB.exists()):
        return  # corpus outputs absent -- nothing to check
    tmpdir = tempfile.mkdtemp()
    outs = {seed: _run(seed, tmpdir) for seed in SEEDS}
    unique = set(outs.values())
    assert len(unique) == 1, (
        f"analyze_emc.py output differs across PYTHONHASHSEED "
        f"{sorted(outs.keys())}: expected 1 unique output, got {len(unique)}"
    )


if __name__ == "__main__":
    if not (SCH.exists() and PCB.exists()):
        print("0 passed, 0 failed, 1 skipped")
        sys.exit(0)
    test_ck001_order_stable_across_hash_seeds()
    print("1 passed, 0 failed")
