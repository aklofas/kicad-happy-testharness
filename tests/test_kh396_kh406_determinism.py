"""KH-406 / KH-396 — hash-seed-dependent list/dict order in schematic output.

KH-406: `differential_pairs[].esd_protection` iterated the set `shared`
unsorted (analyze_schematic.py ~4874) — the sibling `shared_ics` was already
sorted. Needs >=2 IC-type parts shared by both halves of a diff pair.
KH-396: `rf_chains[].component_roles` was a dict comprehension over the set
`all_rf_refs` (domain_detectors.py ~1215); `rf_ref_list = sorted(all_rf_refs)`
existed a few lines up for a different field.
Both run the analyzer in fresh processes under PYTHONHASHSEED 1/7/123.
"""

TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
SCH = os.path.join(_KH, "skills", "kicad", "scripts", "analyze_schematic.py")
FIX = _HARNESS / "tests" / "fixtures" / "determinism" / "usb_dual_esd.kicad_sch"
HACKRF = _HARNESS / "repos" / "greatscottgadgets" / "hackrf" / "hardware" / "hackrf-one" / "hackrf-one.kicad_sch"


def _norm(path, seed):
    env = dict(os.environ, PYTHONHASHSEED=str(seed))
    r = subprocess.run([sys.executable, SCH, str(path), "--compact"],
                       capture_output=True, text=True, env=env, timeout=300)
    assert r.returncode == 0, r.stderr[-1500:]
    d = json.loads(r.stdout)
    d.pop("inputs", None)
    d.pop("capability_mode_ref", None)
    return d


def test_esd_protection_order_is_seed_independent():
    runs = [_norm(FIX, s) for s in (1, 7, 123)]
    pairs = runs[0]["design_analysis"]["differential_pairs"]
    assert pairs and pairs[0].get("esd_protection"), "fixture must yield a diff pair with 2 ESD ICs"
    assert pairs[0]["esd_protection"] == sorted(pairs[0]["esd_protection"])
    assert json.dumps(runs[0], sort_keys=True) == json.dumps(runs[1], sort_keys=True) == json.dumps(runs[2], sort_keys=True)


def test_rf_component_roles_order_is_seed_independent():
    if not HACKRF.exists():
        import pytest
        pytest.skip("hackrf-one corpus board not present")
    runs = [_norm(HACKRF, s) for s in (1, 7, 123)]
    chains = [f for f in runs[0]["findings"] if f.get("rule_id") == "RF-DET"]
    assert chains, "hackrf-one must produce an RF-DET finding"
    roles = chains[0]["component_roles"]
    assert list(roles) == sorted(roles)
    assert json.dumps(runs[0], sort_keys=True) == json.dumps(runs[1], sort_keys=True) == json.dumps(runs[2], sort_keys=True)


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
