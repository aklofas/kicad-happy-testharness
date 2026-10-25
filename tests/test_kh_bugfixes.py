"""Regression tests for KH-218 through KH-227 bugfixes.

Tests are organized by issue number.  Where possible, functions are tested
directly; otherwise we check real corpus outputs.  Tests that require corpus
data skip gracefully when the outputs don't exist.
"""

TIER = "unit"

import json
import os
import sys

import pytest
from collections import Counter
from pathlib import Path
from tests.product_root import PRODUCT_ROOT  # noqa: E402

_HARNESS = Path(__file__).resolve().parent.parent
_KH = str(PRODUCT_ROOT)
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

RESULTS = _HARNESS / "results" / "outputs" / "schematic"


# ---------------------------------------------------------------------------
# Skip support (no pytest dependency)
# ---------------------------------------------------------------------------

def _skip(reason: str):
    pytest.skip(f"{reason} (corpus tier)")


def _load_outputs(repo: str, filename_substring: str = ""):
    """Load all schematic JSON outputs for a repo, optionally filtered."""
    repo_dir = RESULTS / repo
    if not repo_dir.exists():
        _skip(f"corpus output not available: {repo}")
    outputs = []
    for f in sorted(repo_dir.rglob("*.json")):
        if filename_substring and filename_substring not in f.name:
            continue
        outputs.append(json.loads(f.read_text(encoding="utf-8")))
    if not outputs:
        _skip(f"no matching outputs in {repo}")
    return outputs


# ===========================================================================
# 4a. KH-218 — Vref lookup table additions
# ===========================================================================

from kicad_core.parts import lookup_regulator_vref


def test_kh218_tps62912_vref():
    """TPS62912 should resolve to 0.8V via prefix TPS6291."""
    vref, source = lookup_regulator_vref("TPS62912", "")
    assert vref is not None, "TPS62912 not found in Vref lookup"
    assert abs(vref - 0.8) < 0.01, f"Expected 0.8V, got {vref}"
    assert source == "lookup"


def test_kh218_tps73601_vref():
    """TPS73601 should resolve to 1.204V via prefix TPS736."""
    vref, source = lookup_regulator_vref("TPS73601", "")
    assert vref is not None, "TPS73601 not found in Vref lookup"
    assert abs(vref - 1.204) < 0.01, f"Expected ~1.204V, got {vref}"


def test_kh218_lm22676_vref():
    """LM22676 should resolve to 1.285V."""
    vref, source = lookup_regulator_vref("LM22676", "")
    assert vref is not None, "LM22676 not found in Vref lookup"
    assert abs(vref - 1.285) < 0.01, f"Expected 1.285V, got {vref}"


def test_kh218_lm317_unchanged():
    """LM317 should still resolve to 1.25V (existing entry)."""
    vref, source = lookup_regulator_vref("LM317", "")
    assert vref is not None
    assert abs(vref - 1.25) < 0.01, f"Expected 1.25V, got {vref}"
    assert source == "lookup"


# ===========================================================================
# 4c. KH-220 — Oscillator description-based classification
# ===========================================================================

from kicad_core.classify import classify_component


def test_kh220_xo_by_description():
    """ECS-2520MV with 'XTAL OSC XO CMOS' description -> oscillator."""
    result = classify_component(
        ref="X400",
        lib_id="SamacSys_Parts:ECS-2520MV",
        value="ECS-2520MV",
        description="XTAL OSC XO CMOS",
    )
    assert result == "oscillator", f"Expected 'oscillator', got '{result}'"


def test_kh220_crystal_not_oscillator():
    """Y1 with Device:Crystal and 'Crystal' description -> crystal."""
    result = classify_component(
        ref="Y1",
        lib_id="Device:Crystal",
        value="16MHz",
        description="Crystal",
    )
    assert result == "crystal", f"Expected 'crystal', got '{result}'"


def test_kh220_crystal_oscillator_desc_with_crystal_libid():
    """Crystal lib_id should win over 'Crystal Oscillator' description.

    lib_id-based detection (has_xtal/has_osc) runs before description
    detection, and 'crystal' in lib_id returns 'crystal'.
    """
    result = classify_component(
        ref="Y2",
        lib_id="Device:Crystal",
        value="8MHz",
        description="Crystal Oscillator",
    )
    # lib_id says "Crystal" -> crystal wins over description
    assert result == "crystal", f"Expected 'crystal', got '{result}'"


# ===========================================================================
# 4d. KH-221 — TIA vs compensator discrimination
# ===========================================================================

@pytest.mark.corpus
def test_kh221_tia_in_corpus():
    """Corpus should contain at least one transimpedance opamp classification."""
    for repo in ("Ceenzr/StusTM", "jkominek/adcstudy"):
        repo_dir = RESULTS / repo
        if not repo_dir.exists():
            continue
        for f in repo_dir.rglob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            opamps = [f for f in data.get("findings", [])
                      if f.get("detector") in ("detect_opamp_circuits", "detect_opamp_analysis")]
            for o in opamps:
                if o.get("configuration") == "transimpedance":
                    assert "feedback_resistor" in o, \
                        "TIA should have feedback_resistor"
                    return
    _skip("no transimpedance opamps found in available corpus")


# ===========================================================================
# 4e. KH-222 — Multi-unit deduplication
# ===========================================================================

@pytest.mark.corpus
def test_kh222_no_duplicate_led_audit_refs():
    """biomimetics/MRIRobot_PCB led_audit should have no duplicate refs."""
    outputs = _load_outputs("biomimetics/MRIRobot_PCB")
    for data in outputs:
        la = [f for f in data.get("findings", [])
              if f.get("detector") == "audit_led_circuits"]
        if not la:
            continue
        refs = [e.get("reference", e.get("ref", "")) for e in la]
        counts = Counter(refs)
        dups = {r: c for r, c in counts.items() if c > 1 and r}
        assert not dups, f"Duplicate refs in led_audit: {dups}"


@pytest.mark.corpus
def test_kh222_no_duplicate_usb_connectors():
    """biomimetics/MRIRobot_PCB usb_compliance connectors should have no dups."""
    outputs = _load_outputs("biomimetics/MRIRobot_PCB")
    found_any = False
    for data in outputs:
        usb = data.get("usb_compliance", {})
        if not usb or not isinstance(usb, dict):
            continue
        conns = usb.get("connectors", [])
        if not conns:
            continue
        found_any = True
        refs = [c.get("connector", c.get("reference", "")) for c in conns]
        counts = Counter(refs)
        dups = {r: c for r, c in counts.items() if c > 1 and r}
        assert not dups, f"Duplicate connector refs: {dups}"
    if not found_any:
        _skip("no USB compliance connectors in biomimetics outputs")


# ===========================================================================
# 4f. KH-223 — Power sequencing pin name normalization
# ===========================================================================

@pytest.mark.corpus
def test_kh223_power_sequencing_has_controlled_enables():
    """Zebra-X power_sequencing should detect controlled enable pins.

    KH-223 fixed ~{EN} overbar normalization so EN pins are found.
    """
    outputs = _load_outputs("Dylanfg123/Zebra-X")
    for data in outputs:
        ps = data.get("power_sequencing", {})
        if not ps:
            continue
        deps = ps.get("dependencies", [])
        if not deps:
            continue
        sources = {d.get("en_source") for d in deps}
        assert "controlled" in sources, \
            f"Expected 'controlled' enable sources, got: {sources}"
        return
    _skip("no power_sequencing data in Zebra-X outputs")


@pytest.mark.corpus
def test_kh223_power_good_signals_detected():
    """Zebra-X should have power-good (PG) signals detected."""
    outputs = _load_outputs("Dylanfg123/Zebra-X")
    for data in outputs:
        ps = data.get("power_sequencing", {})
        pgs = ps.get("power_good_signals", [])
        if pgs:
            assert len(pgs) >= 2, \
                f"Expected multiple PG signals, got {len(pgs)}"
            for pg in pgs:
                assert pg.get("pg_net"), "PG signal missing pg_net"
            return
    _skip("no power_good_signals in Zebra-X outputs")


# ===========================================================================
# 4g. KH-224 — Multi-unit IC power domain accumulation
# ===========================================================================

@pytest.mark.corpus
def test_kh224_zynq_multiple_power_rails():
    """U200 (Zynq) in Zebra-X should have >1 power rail.

    KH-224 fixed multi-unit IC rail accumulation: rails from all units
    are merged so that multi-bank FPGAs get all their power pins.
    The root schematic (ZeBra-X.kicad_sch) aggregates all sub-sheets,
    so U200 should show all power rails there.
    """
    outputs = _load_outputs("Dylanfg123/Zebra-X")
    max_rails = 0
    for data in outputs:
        da = data.get("design_analysis", {})
        pd = da.get("power_domains", {})
        if not isinstance(pd, dict):
            continue
        ic_rails = pd.get("ic_power_rails", pd)
        if not isinstance(ic_rails, dict):
            continue
        if "U200" in ic_rails:
            u200 = ic_rails["U200"]
            rails = u200.get("power_rails", [])
            max_rails = max(max_rails, len(rails))
    assert max_rails > 1, \
        f"U200 should have >1 power rail in at least one output, best={max_rails}"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback

    tests = [(name, obj) for name, obj in sorted(globals().items())
             if name.startswith("test_") and callable(obj)]
    passed = failed = skipped = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f"  PASS  {name}")
        except pytest.skip.Exception as e:
            skipped += 1
            print(f"  SKIP  {name}: {e}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"  ERROR {name}: {e}")
            traceback.print_exc()
    total = passed + failed + skipped
    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped ({total} total)")
    sys.exit(1 if failed else 0)
