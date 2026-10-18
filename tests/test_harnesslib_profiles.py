# tests/test_harnesslib_profiles.py
"""harnesslib.profiles: declared execution profiles (spec §7, TH-055 cap plumbing)."""
TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harnesslib.profiles import PROFILES, Profile  # noqa: E402


def test_declared_profiles():
    assert set(PROFILES) == {"standard", "full-chain", "hierarchy", "spice-offline", "long-tail",
                             "distributor-offline"}
    for name, p in PROFILES.items():
        assert isinstance(p, Profile) and p.name == name


def test_standard_profile_matches_historical_gate_recipe():
    p = PROFILES["standard"]
    assert p.analyzers == ("schematic", "pcb", "gerber", "thermal", "emc", "cross_analysis")
    assert p.timeout_s == 120 and p.pcb_full is False
    assert p.schematic_no_hierarchy is True and p.only_deterministic is True and p.offline is True


def test_long_tail_and_full_chain_differ_only_where_declared():
    assert PROFILES["long-tail"].timeout_s == 600
    assert PROFILES["long-tail"].analyzers == PROFILES["standard"].analyzers
    assert PROFILES["full-chain"].pcb_full is True
    # TH-072: Phase B pairs off schematic records, so the chained profile must run schematic
    assert PROFILES["full-chain"].analyzers == ("schematic", "pcb", "emc", "thermal", "cross_analysis")
    assert PROFILES["spice-offline"].analyzers == ("spice",)
    assert PROFILES["distributor-offline"].analyzers == ("distributor",)
    assert PROFILES["distributor-offline"].timeout_s == 120 and PROFILES["distributor-offline"].offline
    assert PROFILES["hierarchy"].schematic_no_hierarchy is False


def test_utils_timeout_comes_from_profile():
    import utils
    assert utils.ANALYZER_TIMEOUT == PROFILES["standard"].timeout_s


def test_run_one_explicit_timeout_cap(tmp_path):
    import utils
    script = tmp_path / "slow.py"
    script.write_text("import time; time.sleep(5)\n")
    outfile, errfile = tmp_path / "o.json", tmp_path / "e.txt"
    result = utils._run_one(script, "unused_input", outfile, errfile, timeout=1)
    assert result[0] is None
    assert "Timed out after 1s" in errfile.read_text()
    assert result[2] < 3
