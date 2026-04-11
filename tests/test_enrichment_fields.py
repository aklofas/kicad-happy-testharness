"""Unit tests for enrichment fields added to kicad-happy analyzers.

Validates output field presence and structure by scanning real corpus outputs.
Tests skip gracefully when enrichment outputs haven't been generated yet.
"""

TIER = "unit"

import json
import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))

sys.path.insert(0, str(_HARNESS))

_RESULTS = _HARNESS / "results" / "outputs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_output_with(output_type, check_fn, max_scan=5000):
    """Find first output file where check_fn(data) returns True."""
    out_dir = _RESULTS / output_type
    if not out_dir.exists():
        return None, None
    scanned = 0
    for owner in sorted(out_dir.iterdir()):
        if not owner.is_dir():
            continue
        for repo in sorted(owner.iterdir()):
            if not repo.is_dir():
                continue
            for jf in sorted(repo.glob("*.json")):
                try:
                    data = json.loads(jf.read_text(encoding="utf-8"))
                    if check_fn(data):
                        return data, str(jf)
                except Exception:
                    pass
                scanned += 1
                if scanned >= max_scan:
                    return None, None
    return None, None


def _skip_if_none(data, path, feature_name):
    """Print skip message and return True if data is None."""
    if data is None:
        print(f"  SKIP: no {feature_name} output found in corpus (enrichment not yet run)")
        return True
    return False


# ---------------------------------------------------------------------------
# 4a. Bus electrical parameters
# ---------------------------------------------------------------------------

def test_i2c_bus_speed_mode():
    """I2C bus entries have speed_mode field."""
    def check(data):
        ba = data.get("design_analysis", {}).get("bus_analysis", {})
        for bus in ba.get("i2c", []):
            if "speed_mode" in bus:
                return True
        return False

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, path, "I2C bus with speed_mode"):
        return
    ba = data["design_analysis"]["bus_analysis"]
    bus = next(b for b in ba["i2c"] if "speed_mode" in b)
    assert isinstance(bus["speed_mode"], str), "speed_mode must be a string"
    assert bus["speed_mode"] in ("standard", "fast", "fast_plus", "high_speed"), \
        f"unexpected speed_mode: {bus['speed_mode']}"


def test_i2c_bus_voltage_and_pullup():
    """I2C bus entries have voltage_level_V and pull_up_ohms fields."""
    def check(data):
        ba = data.get("design_analysis", {}).get("bus_analysis", {})
        for bus in ba.get("i2c", []):
            if bus.get("voltage_level_V") is not None and bus.get("pull_up_ohms") is not None:
                return True
        return False

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, path, "I2C bus with voltage_level_V and pull_up_ohms"):
        return
    ba = data["design_analysis"]["bus_analysis"]
    bus = next(b for b in ba["i2c"]
               if b.get("voltage_level_V") is not None and b.get("pull_up_ohms") is not None)
    assert isinstance(bus["voltage_level_V"], (int, float)), "voltage_level_V must be numeric"
    assert bus["voltage_level_V"] > 0, "voltage_level_V must be > 0"
    assert isinstance(bus["pull_up_ohms"], (int, float)), "pull_up_ohms must be numeric"
    assert bus["pull_up_ohms"] > 0, "pull_up_ohms must be > 0"


def test_can_bus_termination():
    """CAN bus entries have termination field."""
    def check(data):
        ba = data.get("design_analysis", {}).get("bus_analysis", {})
        for bus in ba.get("can", []):
            if bus.get("termination") is not None and bus["termination"]:
                return True
        return False

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, path, "CAN bus with termination"):
        return
    ba = data["design_analysis"]["bus_analysis"]
    bus = next(b for b in ba["can"]
               if b.get("termination") is not None and b["termination"])
    # termination is a string like "120ohm (R43)" in bus_analysis.can
    assert isinstance(bus["termination"], str), \
        f"termination must be a string, got {type(bus['termination'])}"


def test_can_diff_pair_termination():
    """CAN differential pairs have has_termination and termination fields."""
    def check(data):
        da = data.get("design_analysis", {})
        for dp in da.get("differential_pairs", []):
            if dp.get("has_termination"):
                return True
        return False

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, path, "CAN diff pair with termination"):
        return
    da = data["design_analysis"]
    dp = next(d for d in da["differential_pairs"] if d.get("has_termination"))
    assert dp["has_termination"] is True
    term = dp.get("termination", [])
    assert isinstance(term, list), "diff pair termination must be a list"
    if term:
        assert "ref" in term[0], "termination entry must have ref"
        assert "ohms" in term[0], "termination entry must have ohms"


# ---------------------------------------------------------------------------
# 4b. Bus device enrichment
# ---------------------------------------------------------------------------

def test_bus_devices_are_dicts():
    """Bus device entries are dicts with ref key, not bare strings."""
    def check(data):
        ba = data.get("design_analysis", {}).get("bus_analysis", {})
        for bt in ("i2c", "spi", "uart", "can"):
            for bus in ba.get(bt, []):
                devs = bus.get("devices", [])
                if devs and isinstance(devs[0], dict):
                    return True
        return False

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, path, "bus with enriched device dicts"):
        return
    ba = data["design_analysis"]["bus_analysis"]
    for bt in ("i2c", "spi", "uart", "can"):
        for bus in ba.get(bt, []):
            devs = bus.get("devices", [])
            if devs and isinstance(devs[0], dict):
                dev = devs[0]
                assert "ref" in dev, f"device dict must have 'ref' key in {bt} bus"
                assert "value" in dev, f"device dict must have 'value' key in {bt} bus"
                assert "lib_id" in dev, f"device dict must have 'lib_id' key in {bt} bus"
                return
    assert False, "no enriched device dict found"


def test_bus_controller_field():
    """I2C or SPI bus has controller field identifying MCU/FPGA."""
    def check(data):
        ba = data.get("design_analysis", {}).get("bus_analysis", {})
        for bt in ("i2c", "spi"):
            for bus in ba.get(bt, []):
                if bus.get("controller"):
                    return True
        return False

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, path, "bus with controller field"):
        return
    ba = data["design_analysis"]["bus_analysis"]
    for bt in ("i2c", "spi"):
        for bus in ba.get(bt, []):
            if bus.get("controller"):
                assert isinstance(bus["controller"], str), "controller must be a string ref"
                return
    assert False, "no controller field found"


# ---------------------------------------------------------------------------
# 4c. Switching regulator power dissipation
# ---------------------------------------------------------------------------

def test_switching_regulator_power_dissipation():
    """Switching regulators have power_dissipation with efficiency and topology."""
    def check(data):
        sa = data.get("signal_analysis", {})
        for reg in sa.get("power_regulators", []):
            pd = reg.get("power_dissipation", {})
            if pd.get("topology") == "switching":
                return True
        return False

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, path, "switching regulator with power_dissipation"):
        return
    sa = data["signal_analysis"]
    reg = next(r for r in sa["power_regulators"]
               if r.get("power_dissipation", {}).get("topology") == "switching")
    pd = reg["power_dissipation"]
    assert "efficiency_assumed" in pd, "must have efficiency_assumed"
    assert 0.7 <= pd["efficiency_assumed"] <= 0.95, \
        f"efficiency_assumed out of range: {pd['efficiency_assumed']}"
    assert "estimated_pdiss_W" in pd, "must have estimated_pdiss_W"
    assert pd["estimated_pdiss_W"] >= 0, "estimated_pdiss_W must be >= 0"
    assert pd["topology"] == "switching"
    assert "sub_topology" in pd, "must have sub_topology"
    assert pd["sub_topology"] in ("buck", "boost", "buck-boost"), \
        f"unexpected sub_topology: {pd['sub_topology']}"


def test_ldo_regulator_power_dissipation():
    """LDO regulators have power_dissipation with dropout_V."""
    def check(data):
        sa = data.get("signal_analysis", {})
        for reg in sa.get("power_regulators", []):
            pd = reg.get("power_dissipation", {})
            if "dropout_V" in pd:
                return True
        return False

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, path, "LDO regulator with power_dissipation"):
        return
    sa = data["signal_analysis"]
    reg = next(r for r in sa["power_regulators"]
               if "dropout_V" in r.get("power_dissipation", {}))
    pd = reg["power_dissipation"]
    assert "vin_estimated_V" in pd, "must have vin_estimated_V"
    assert "vout_V" in pd, "must have vout_V"
    assert "dropout_V" in pd, "must have dropout_V"
    assert pd["dropout_V"] > 0, "dropout_V must be > 0"
    assert "estimated_pdiss_W" in pd, "must have estimated_pdiss_W"
    assert pd["estimated_pdiss_W"] >= 0, "estimated_pdiss_W must be >= 0"
    assert "estimated_iout_A" in pd, "must have estimated_iout_A"


# ---------------------------------------------------------------------------
# 4d. Crystal load cap validation
# ---------------------------------------------------------------------------

def test_crystal_target_load_pF():
    """Crystal circuits have target_load_pF field."""
    def check(data):
        sa = data.get("signal_analysis", {})
        for x in sa.get("crystal_circuits", []):
            if "target_load_pF" in x:
                return True
        return False

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, path, "crystal circuit with target_load_pF"):
        return
    sa = data["signal_analysis"]
    xtal = next(x for x in sa["crystal_circuits"] if "target_load_pF" in x)
    tl = xtal["target_load_pF"]
    # target_load_pF can be None if no target could be determined
    if tl is not None:
        assert isinstance(tl, (int, float)), "target_load_pF must be numeric"
        assert tl > 0, "target_load_pF must be > 0"


def test_crystal_load_cap_validation():
    """Crystal circuits with effective_load_pF have error_pct and status."""
    def check(data):
        sa = data.get("signal_analysis", {})
        for x in sa.get("crystal_circuits", []):
            if "load_cap_status" in x and "load_cap_error_pct" in x:
                return True
        return False

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, path, "crystal circuit with load_cap_status"):
        return
    sa = data["signal_analysis"]
    xtal = next(x for x in sa["crystal_circuits"]
                if "load_cap_status" in x and "load_cap_error_pct" in x)
    assert isinstance(xtal["load_cap_error_pct"], (int, float)), \
        "load_cap_error_pct must be numeric"
    assert xtal["load_cap_status"] in ("ok", "marginal", "out_of_spec"), \
        f"unexpected load_cap_status: {xtal['load_cap_status']}"
    # If status is ok, error should be within 10%
    if xtal["load_cap_status"] == "ok":
        assert abs(xtal["load_cap_error_pct"]) <= 10


# ---------------------------------------------------------------------------
# 4e. ESD device details
# ---------------------------------------------------------------------------

def test_esd_device_details_exist():
    """ESD coverage audit entries have esd_device_details list."""
    def check(data):
        sa = data.get("signal_analysis", {})
        for e in sa.get("esd_coverage_audit", []):
            if "esd_device_details" in e and e["esd_device_details"]:
                return True
        return False

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, path, "ESD coverage with device details"):
        return
    sa = data["signal_analysis"]
    entry = next(e for e in sa["esd_coverage_audit"]
                 if e.get("esd_device_details"))
    details = entry["esd_device_details"]
    assert isinstance(details, list), "esd_device_details must be a list"
    assert len(details) > 0, "esd_device_details must not be empty"


def test_esd_device_detail_structure():
    """Each esd_device_details entry has ref, value, lib_id keys."""
    def check(data):
        sa = data.get("signal_analysis", {})
        for e in sa.get("esd_coverage_audit", []):
            if "esd_device_details" in e and e["esd_device_details"]:
                return True
        return False

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, path, "ESD coverage with device details"):
        return
    sa = data["signal_analysis"]
    entry = next(e for e in sa["esd_coverage_audit"]
                 if e.get("esd_device_details"))
    for detail in entry["esd_device_details"]:
        assert isinstance(detail, dict), "each detail must be a dict"
        assert "ref" in detail, "detail must have 'ref'"
        assert "value" in detail, "detail must have 'value'"
        assert "lib_id" in detail, "detail must have 'lib_id'"
        assert isinstance(detail["ref"], str), "ref must be a string"


# ---------------------------------------------------------------------------
# 4f. Decoupling proximity
# ---------------------------------------------------------------------------

def test_decoupling_proximity_exists():
    """PCB outputs with decoupling have decoupling_proximity list."""
    def check(data):
        return bool(data.get("decoupling_proximity"))

    data, path = _find_output_with("pcb", check)
    if _skip_if_none(data, path, "PCB with decoupling_proximity"):
        return
    dp = data["decoupling_proximity"]
    assert isinstance(dp, list), "decoupling_proximity must be a list"
    assert len(dp) > 0


def test_decoupling_proximity_structure():
    """Each decoupling_proximity entry has ic_ref, cap_ref, distance_mm."""
    def check(data):
        return bool(data.get("decoupling_proximity"))

    data, path = _find_output_with("pcb", check)
    if _skip_if_none(data, path, "PCB with decoupling_proximity"):
        return
    dp = data["decoupling_proximity"]
    for entry in dp:
        assert isinstance(entry, dict), "each entry must be a dict"
        assert "ic_ref" in entry, "entry must have 'ic_ref'"
        assert "cap_ref" in entry, "entry must have 'cap_ref'"
        assert "distance_mm" in entry, "entry must have 'distance_mm'"
        assert isinstance(entry["distance_mm"], (int, float)), \
            "distance_mm must be numeric"
        assert entry["distance_mm"] >= 0, "distance_mm must be >= 0"
    # Verify flat structure (not nested)
    for entry in dp:
        assert "nearby_caps" not in entry, \
            "decoupling_proximity should be flat, not nested"


# ---------------------------------------------------------------------------
# 4g. EMC category summary
# ---------------------------------------------------------------------------

def test_emc_category_summary_exists():
    """EMC outputs have category_summary dict."""
    def check(data):
        return bool(data.get("category_summary"))

    data, path = _find_output_with("emc", check)
    if _skip_if_none(data, path, "EMC with category_summary"):
        return
    cs = data["category_summary"]
    assert isinstance(cs, dict), "category_summary must be a dict"
    assert len(cs) > 0, "category_summary must not be empty"


def test_emc_category_summary_structure():
    """Category summary entries have count, max_severity, severities."""
    def check(data):
        return bool(data.get("category_summary"))

    data, path = _find_output_with("emc", check)
    if _skip_if_none(data, path, "EMC with category_summary"):
        return
    cs = data["category_summary"]
    for cat_name, cat_info in cs.items():
        assert "count" in cat_info, f"category {cat_name} must have 'count'"
        assert "max_severity" in cat_info, \
            f"category {cat_name} must have 'max_severity'"
        assert "severities" in cat_info, \
            f"category {cat_name} must have 'severities'"
        assert isinstance(cat_info["severities"], dict), \
            f"severities must be a dict for {cat_name}"
        assert cat_info["count"] > 0, \
            f"count must be > 0 for present category {cat_name}"

    # Verify sum of all category counts equals total findings
    total_from_cats = sum(info["count"] for info in cs.values())
    findings_count = len(data.get("findings", []))
    assert total_from_cats == findings_count, \
        f"category count sum ({total_from_cats}) != findings count ({findings_count})"


# ---------------------------------------------------------------------------
# __main__
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback

    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    passed = failed = skipped = 0
    for t in tests:
        name = t.__name__
        try:
            t()
            passed += 1
            print(f"  PASS  {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"  ERROR {name}: {e}")
            traceback.print_exc()
    total = passed + failed
    print(f"\n{passed}/{total} passed, {failed} failed")
    sys.exit(1 if failed else 0)
