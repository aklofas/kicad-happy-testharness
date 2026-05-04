"""B5 (d) absorption — per-rule fire-shape tests for 4c lookup detectors.

Per main-repo handoff (LOG #79 §c). The B5 (a/b/c) tests in
test_b5_4b_4c_detector_invariants.py cover schema_era tagging, enum
tightening, and the XT-001 emission gate via static AST + duck-typed
calls. (d) is the integration-level layer: build a real
AnalysisContext, populate cache_dir with A7 gold extraction JSONs, and
exercise each detector's full lookup → finding chain.

Rules covered:
    AM-001  detect_absolute_max_violations    (rail above absolute_max)
    OV-001  detect_vcc_outside_recommended    (rail below/above recommended)
    TJ-001  detect_tj_exceeds_max             (Tj_v14 > Tjmax)
    FT-001  detect_5v_on_non_tolerant_pin     (≥4.5V on is_5v_tolerant=False pin)
    PM-001  detect_wrong_signal_type          (net peripheral hint vs pin alt_functions)
    EX-001  detect_missing_required_components (regulator cin/cout/inductor missing)

Cache strategy: the harness ships A7 gold extractions at
regression/reference_extractions/<slug>/gold_v1.0.json. Each test copies
the relevant gold JSON to a tmp cache_dir as <MPN>.json and points
ctx.cache_dir at it. The PDF is intentionally absent — datasheet_lookup
flags facts._cache_context.is_stale=True but still returns the parsed
DatasheetFacts. trust_gating.best() doesn't consult cache staleness, so
all high-confidence gold specs pass min_confidence='medium'.

Skipping policy: tests skip cleanly when KICAD_HAPPY_DIR points to a
checkout missing lookup_detectors.py or datasheet_types/ (older v1.3
trees) so the file remains green on backwards-compat smoke runs.
"""
from __future__ import annotations

TIER = "unit"

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
KH_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy")))
KH_SCRIPTS = KH_DIR / "skills" / "kicad" / "scripts"
KH_DS_PKG = KH_DIR / "skills" / "datasheets"
KH_DS_SCRIPTS = KH_DS_PKG / "scripts"

for _p in (KH_SCRIPTS, KH_DS_PKG, KH_DS_SCRIPTS):
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# Fixture helpers (build_ctx, ic, resistor, capacitor)
sys.path.insert(0, str(HARNESS_DIR / "tests"))
from fixtures._build_ctx import build_ctx, ic, capacitor  # noqa: E402

GOLD_DIR = HARNESS_DIR / "regression" / "reference_extractions"


# ---------------------------------------------------------------------------
# Lazy-import wrappers — return None when the v1.4 detector tree is absent so
# individual tests skip cleanly rather than the module crashing on import.
# ---------------------------------------------------------------------------

def _lookup_detectors():
    try:
        import lookup_detectors
        return lookup_detectors
    except ImportError:
        return None


def _datasheet_types():
    try:
        import datasheet_types
        return datasheet_types
    except ImportError:
        return None


def _setup_cache(tmp: Path, slug: str, mpn_filename: str) -> Path | None:
    """Copy A7 gold extraction to a tmp cache_dir as <mpn_filename>.json.

    Returns the cache_dir Path or None if the gold file is missing.
    """
    src = GOLD_DIR / slug / "gold_v1.0.json"
    if not src.is_file():
        return None
    cache = tmp / "extracted"
    cache.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, cache / f"{mpn_filename}.json")
    return cache


def _required_finding_keys() -> set[str]:
    """Keys every detector emits via make_finding kwargs."""
    return {
        "detector", "rule_id", "category", "summary", "description",
        "severity", "confidence", "evidence_source", "schema_era",
    }


# ---------------------------------------------------------------------------
# AM-001 — absolute_max violation (5V on STM32F103 VDD, max 4.0V)
# ---------------------------------------------------------------------------

def test_am_001_fires_on_vdd_above_absolute_max():
    """5V applied to STM32F103C8T6 VDD pin (datasheet absmax 4.0V) fires AM-001."""
    ld = _lookup_detectors()
    if ld is None:
        return  # v1.3 tree, skip
    if _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache is None:
            return  # gold file missing
        # STM32F103 has VDD pins at 24/36/48 with power_domain="VDD".
        # Build a 3-pin minimal ic surfacing pin "24" (VDD_1) connected to
        # an over-voltage rail.
        u1 = ic("U1", "STM32F103C8T6",
                [("24", "VDD_1"), ("8", "VSS_1"), ("2", "PC13-TAMPER-RTC")],
                lib_id="MCU_ST_STM32F1:STM32F103C8Tx",
                mpn="STM32F103C8T6")
        ctx = build_ctx(
            components=[u1],
            nets={
                "OVERVOLT": [("U1", "24")],
                "GND":      [("U1", "8")],
                "PC13_NET": [("U1", "2")],
            },
            known_power_rails={"OVERVOLT", "GND"},
        )
        ctx.cache_dir = cache
        rail_voltages = {"OVERVOLT": 5.0, "GND": 0.0}
        findings = ld.detect_absolute_max_violations(ctx, rail_voltages)

    assert len(findings) >= 1, (
        f"AM-001 must fire when VDD pin sees 5V > 4.0V absmax; got "
        f"{len(findings)} findings."
    )
    f = findings[0]
    assert f["rule_id"] == "AM-001"
    assert f["severity"] == "error"
    assert f["confidence"] == "datasheet-backed"
    assert f["evidence_source"] == "datasheet"
    assert f.get("schema_era") == "v1.4"
    assert "U1" in f.get("components", [])
    assert "OVERVOLT" in f.get("nets", [])
    # Shape lock on AM-001-specific extra fields
    assert f.get("rail_voltage") == 5.0
    assert f.get("absolute_max_v") == 4.0


def test_am_001_silent_when_vdd_within_absolute_max():
    """3.3V applied to STM32F103 VDD pin (max 4.0V) does NOT fire AM-001."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache is None:
            return
        u1 = ic("U1", "STM32F103C8T6",
                [("24", "VDD_1"), ("8", "VSS_1")],
                lib_id="MCU_ST_STM32F1:STM32F103C8Tx",
                mpn="STM32F103C8T6")
        ctx = build_ctx(
            components=[u1],
            nets={"+3V3": [("U1", "24")], "GND": [("U1", "8")]},
            known_power_rails={"+3V3", "GND"},
        )
        ctx.cache_dir = cache
        findings = ld.detect_absolute_max_violations(ctx, {"+3V3": 3.3})

    am_findings = [f for f in findings if f.get("rule_id") == "AM-001"]
    assert am_findings == [], (
        f"AM-001 must be silent for 3.3V on VDD (within 4.0V absmax); "
        f"got {am_findings}"
    )


def test_am_001_silent_when_no_mpn():
    """Component without mpn never invokes lookup; AM-001 silent."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache is None:
            return
        # No mpn= → component_mpn helper returns the value field, but we
        # set value to a string the cache doesn't know about so lookup
        # misses and the detector falls through silently.
        u1 = ic("U1", "UNKNOWN_MPN_XYZ",
                [("24", "VDD_1"), ("8", "VSS_1")])
        ctx = build_ctx(
            components=[u1],
            nets={"OVERVOLT": [("U1", "24")], "GND": [("U1", "8")]},
            known_power_rails={"OVERVOLT", "GND"},
        )
        ctx.cache_dir = cache
        findings = ld.detect_absolute_max_violations(ctx, {"OVERVOLT": 5.0})

    assert findings == [], (
        f"AM-001 must be silent on cache-miss (unknown MPN); got {findings}"
    )


# ---------------------------------------------------------------------------
# OV-001 — VCC outside recommended range (STM32F103 VDD: 2.0V-3.6V)
# ---------------------------------------------------------------------------

def test_ov_001_fires_above_recommended_max():
    """4V VDD (max recommended 3.6V, abs_max 4.0V) fires OV-001 warning."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache is None:
            return
        u1 = ic("U1", "STM32F103C8T6",
                [("24", "VDD_1"), ("8", "VSS_1")],
                mpn="STM32F103C8T6")
        ctx = build_ctx(
            components=[u1],
            nets={"+4V": [("U1", "24")], "GND": [("U1", "8")]},
            known_power_rails={"+4V", "GND"},
        )
        ctx.cache_dir = cache
        # 4.0V is at absolute_max boundary (not exceeded by ≤), so AM-001
        # silent; but OV-001 fires (4.0 > recommended max 3.6).
        findings = ld.detect_vcc_outside_recommended(ctx, {"+4V": 4.0})

    ov = [f for f in findings if f.get("rule_id") == "OV-001"]
    assert len(ov) >= 1, f"OV-001 must fire above 3.6V max; got {findings}"
    f = ov[0]
    assert f["severity"] == "warning"
    assert f["confidence"] == "datasheet-backed"
    assert f.get("schema_era") == "v1.4"
    assert f.get("recommended_max") == 3.6
    assert f.get("rail_voltage") == 4.0


def test_ov_001_fires_below_recommended_min():
    """1.5V VDD (min recommended 2.0V) fires OV-001 (under-voltage warning)."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache is None:
            return
        u1 = ic("U1", "STM32F103C8T6",
                [("24", "VDD_1"), ("8", "VSS_1")],
                mpn="STM32F103C8T6")
        ctx = build_ctx(
            components=[u1],
            nets={"+1V5": [("U1", "24")], "GND": [("U1", "8")]},
            known_power_rails={"+1V5", "GND"},
        )
        ctx.cache_dir = cache
        findings = ld.detect_vcc_outside_recommended(ctx, {"+1V5": 1.5})

    ov = [f for f in findings if f.get("rule_id") == "OV-001"]
    assert len(ov) >= 1, f"OV-001 must fire below 2.0V min; got {findings}"
    assert ov[0].get("recommended_min") == 2.0
    assert ov[0].get("rail_voltage") == 1.5


def test_ov_001_silent_within_recommended_range():
    """3.3V VDD (in 2.0-3.6V range) does NOT fire OV-001."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache is None:
            return
        u1 = ic("U1", "STM32F103C8T6",
                [("24", "VDD_1"), ("8", "VSS_1")],
                mpn="STM32F103C8T6")
        ctx = build_ctx(
            components=[u1],
            nets={"+3V3": [("U1", "24")], "GND": [("U1", "8")]},
            known_power_rails={"+3V3", "GND"},
        )
        ctx.cache_dir = cache
        findings = ld.detect_vcc_outside_recommended(ctx, {"+3V3": 3.3})

    ov = [f for f in findings if f.get("rule_id") == "OV-001"]
    assert ov == [], (
        f"OV-001 must be silent for 3.3V (within 2.0-3.6V); got {ov}"
    )


# ---------------------------------------------------------------------------
# TJ-001 — junction temperature exceeds max (LM2596-ADJ TJmax 150°C, θJA 55°C/W)
# ---------------------------------------------------------------------------
# Note: STM32F103C8T6 has theta_ja typ=55°C/W and TJmax=150°C as well, but
# our gold for LM2596-ADJ also has theta_ja and TJmax — pick whichever has
# both cleanly. STM32F103 publishes both, use it for consistency.

def test_tj_001_fires_when_tj_estimate_exceeds_max():
    """STM32F103 TJmax=150°C, θJA=55°C/W. Ambient 25°C + 3W → 190°C → fires."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache is None:
            return
        # detect_tj_exceeds_max takes assessments (not ctx) per signature.
        assessments = [{
            "ref": "U1",
            "mpn": "STM32F103C8T6",
            "ambient_c": 25.0,
            "pdiss_w": 3.0,
        }]
        findings = ld.detect_tj_exceeds_max(
            assessments, source="test", cache_dir=cache,
        )

    tj = [f for f in findings if f.get("rule_id") == "TJ-001"]
    assert len(tj) >= 1, f"TJ-001 must fire at 25+55*3=190°C > 150°C; got {findings}"
    f = tj[0]
    assert f["severity"] == "error"
    assert f["category"] == "thermal"
    assert f.get("schema_era") == "v1.4"
    assert f.get("tj_max_c") == 150.0
    assert f.get("theta_ja") == 55.0
    assert f.get("pdiss_w") == 3.0
    assert f.get("ambient_c") == 25.0


def test_tj_001_silent_when_tj_estimate_within_max():
    """Ambient 25°C + 0.5W * 55°C/W = 52.5°C → silent."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache is None:
            return
        assessments = [{
            "ref": "U1",
            "mpn": "STM32F103C8T6",
            "ambient_c": 25.0,
            "pdiss_w": 0.5,
        }]
        findings = ld.detect_tj_exceeds_max(
            assessments, source="test", cache_dir=cache,
        )

    tj = [f for f in findings if f.get("rule_id") == "TJ-001"]
    assert tj == [], (
        f"TJ-001 must be silent at 25+55*0.5=52.5°C ≤ 150°C; got {tj}"
    )


# ---------------------------------------------------------------------------
# FT-001 — 5V on non-5V-tolerant pin (STM32F103 PC13 is_5v_tolerant=False)
# ---------------------------------------------------------------------------

def test_ft_001_fires_on_5v_to_non_tolerant_pin():
    """5V on STM32F103 PC13 (pin 2, is_5v_tolerant=False) fires FT-001."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache is None:
            return
        u1 = ic("U1", "STM32F103C8T6",
                [("2", "PC13-TAMPER-RTC"), ("8", "VSS_1")],
                mpn="STM32F103C8T6")
        ctx = build_ctx(
            components=[u1],
            nets={"+5V": [("U1", "2")], "GND": [("U1", "8")]},
            known_power_rails={"+5V", "GND"},
        )
        ctx.cache_dir = cache
        findings = ld.detect_5v_on_non_tolerant_pin(ctx, {"+5V": 5.0})

    ft = [f for f in findings if f.get("rule_id") == "FT-001"]
    assert len(ft) >= 1, (
        f"FT-001 must fire when 5V hits PC13 (is_5v_tolerant=False); "
        f"got {findings}"
    )
    f = ft[0]
    assert f["severity"] == "error"
    assert f["confidence"] == "datasheet-backed"
    assert f.get("schema_era") == "v1.4"
    assert f.get("signal_voltage") == 5.0
    assert f.get("is_5v_tolerant") is False


def test_ft_001_silent_below_threshold():
    """3.3V on PC13 (non-5V-tolerant) below 4.5V threshold → silent."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache is None:
            return
        u1 = ic("U1", "STM32F103C8T6",
                [("2", "PC13-TAMPER-RTC"), ("8", "VSS_1")],
                mpn="STM32F103C8T6")
        ctx = build_ctx(
            components=[u1],
            nets={"+3V3": [("U1", "2")], "GND": [("U1", "8")]},
            known_power_rails={"+3V3", "GND"},
        )
        ctx.cache_dir = cache
        findings = ld.detect_5v_on_non_tolerant_pin(ctx, {"+3V3": 3.3})

    ft = [f for f in findings if f.get("rule_id") == "FT-001"]
    assert ft == [], (
        f"FT-001 must be silent for 3.3V (below 4.5V threshold); got {ft}"
    )


# ---------------------------------------------------------------------------
# PM-001 — pin signal-type mismatch (net hint vs alt_functions)
# ---------------------------------------------------------------------------

def test_pm_001_fires_when_i2c_net_on_non_i2c_pin():
    """STM32F103 PC13 has only RTC alt-function. Net 'I2C1_SDA' fires PM-001."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache is None:
            return
        u1 = ic("U1", "STM32F103C8T6",
                [("2", "PC13-TAMPER-RTC"), ("8", "VSS_1")],
                mpn="STM32F103C8T6")
        ctx = build_ctx(
            components=[u1],
            nets={"I2C1_SDA": [("U1", "2")], "GND": [("U1", "8")]},
            known_power_rails={"GND"},
        )
        ctx.cache_dir = cache
        findings = ld.detect_wrong_signal_type(ctx)

    pm = [f for f in findings if f.get("rule_id") == "PM-001"]
    assert len(pm) >= 1, (
        f"PM-001 must fire for net I2C1_SDA on RTC-only pin; got {findings}"
    )
    f = pm[0]
    assert f["severity"] == "warning"
    assert f["confidence"] == "datasheet-backed"
    assert f.get("schema_era") == "v1.4"
    assert f.get("inferred_peripheral") == "USART" or f.get("inferred_peripheral") == "I2C"
    # PM-001 specifically — both should be present
    assert "I2C1_SDA" in f.get("nets", [])


def test_pm_001_silent_when_alt_functions_empty():
    """Pin with no alt_functions skips silently (datasheet didn't publish map)."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache is None:
            return
        # VBAT is pin 1, has no alt_functions in the gold.
        u1 = ic("U1", "STM32F103C8T6",
                [("1", "VBAT"), ("8", "VSS_1")],
                mpn="STM32F103C8T6")
        ctx = build_ctx(
            components=[u1],
            nets={"I2C1_SDA": [("U1", "1")], "GND": [("U1", "8")]},
            known_power_rails={"GND"},
        )
        ctx.cache_dir = cache
        findings = ld.detect_wrong_signal_type(ctx)

    pm = [f for f in findings if f.get("rule_id") == "PM-001"]
    assert pm == [], (
        f"PM-001 must be silent on pin with empty alt_functions; got {pm}"
    )


# ---------------------------------------------------------------------------
# EX-001 — missing required components (LM2596-ADJ regulator)
# ---------------------------------------------------------------------------

def test_ex_001_fires_when_input_capacitor_missing():
    """LM2596-ADJ requires Cin per datasheet. Empty input rail fires EX-001."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "lm2596-adj", "LM2596-ADJ")
        if cache is None:
            return
        # Only the regulator IC + an unrelated component — no caps anywhere.
        u1 = ic("U1", "LM2596-ADJ",
                [("1", "VIN"), ("3", "Ground")],
                mpn="LM2596-ADJ")
        ctx = build_ctx(
            components=[u1],
            nets={"VIN": [("U1", "1")], "GND": [("U1", "3")]},
            known_power_rails={"VIN", "GND"},
        )
        ctx.cache_dir = cache
        # power_regulators is the second arg — pre-built dict with rails
        # for the regulator the detector should check.
        regs = [{
            "ref": "U1",
            "mpn": "LM2596-ADJ",
            "input_rail": "VIN",
            "output_rail": None,  # silence cout check; we want cin here.
            "inductor": "L1",     # silence inductor check.
        }]
        findings = ld.detect_missing_required_components(ctx, regs)

    ex = [f for f in findings if f.get("rule_id") == "EX-001"]
    assert len(ex) >= 1, (
        f"EX-001 must fire when Cin missing on regulator's input_rail; "
        f"got {findings}"
    )
    f = ex[0]
    assert f["severity"] == "error"
    assert f["confidence"] == "datasheet-backed"
    assert f.get("schema_era") == "v1.4"
    assert f.get("missing_kind") == "input cap"
    assert f.get("datasheet_field") == "regulator.cin_min"
    assert "U1" in f.get("components", [])
    assert "VIN" in f.get("nets", [])


def test_ex_001_silent_when_input_capacitor_present():
    """LM2596-ADJ with a capacitor on VIN does NOT fire EX-001 for cin."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "lm2596-adj", "LM2596-ADJ")
        if cache is None:
            return
        u1 = ic("U1", "LM2596-ADJ",
                [("1", "VIN"), ("3", "Ground")],
                mpn="LM2596-ADJ")
        c1 = capacitor("C1", "470uF")
        ctx = build_ctx(
            components=[u1, c1],
            nets={
                "VIN": [("U1", "1"), ("C1", "1")],
                "GND": [("U1", "3"), ("C1", "2")],
            },
            known_power_rails={"VIN", "GND"},
        )
        ctx.cache_dir = cache
        regs = [{
            "ref": "U1",
            "mpn": "LM2596-ADJ",
            "input_rail": "VIN",
            "output_rail": None,
            "inductor": "L1",
        }]
        findings = ld.detect_missing_required_components(ctx, regs)

    ex_cin = [f for f in findings if f.get("rule_id") == "EX-001"
              and f.get("missing_kind") == "input cap"]
    assert ex_cin == [], (
        f"EX-001 (input cap) must be silent when C1 sits on VIN; got {ex_cin}"
    )


def test_ex_001_fires_when_inductor_missing_in_switching():
    """LM2596-ADJ requires an inductor (regulator.inductor_range). Empty fires."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    with tempfile.TemporaryDirectory() as td:
        cache = _setup_cache(Path(td), "lm2596-adj", "LM2596-ADJ")
        if cache is None:
            return
        u1 = ic("U1", "LM2596-ADJ",
                [("1", "VIN"), ("3", "Ground")],
                mpn="LM2596-ADJ")
        c_in = capacitor("C1", "470uF")
        c_out = capacitor("C2", "220uF")
        ctx = build_ctx(
            components=[u1, c_in, c_out],
            nets={
                "VIN":  [("U1", "1"), ("C1", "1")],
                "VOUT": [("C2", "1")],
                "GND":  [("U1", "3"), ("C1", "2"), ("C2", "2")],
            },
            known_power_rails={"VIN", "VOUT", "GND"},
        )
        ctx.cache_dir = cache
        regs = [{
            "ref": "U1",
            "mpn": "LM2596-ADJ",
            "input_rail": "VIN",
            "output_rail": "VOUT",
            "inductor": None,  # missing — should fire.
        }]
        findings = ld.detect_missing_required_components(ctx, regs)

    ex_l = [f for f in findings if f.get("rule_id") == "EX-001"
            and f.get("missing_kind") == "inductor"]
    assert len(ex_l) >= 1, (
        f"EX-001 (inductor) must fire when reg['inductor'] is None; "
        f"got {findings}"
    )
    assert ex_l[0].get("datasheet_field") == "regulator.inductor_range"


# ---------------------------------------------------------------------------
# Cross-rule shape lock — every fire-shape carries the standard envelope keys
# ---------------------------------------------------------------------------

def test_all_fired_findings_carry_required_envelope_keys():
    """Each rule's positive-fire produces a finding with the envelope keys
    every consumer expects: detector, rule_id, category, summary, description,
    severity, confidence, evidence_source, schema_era. Plus components list."""
    ld = _lookup_detectors()
    if ld is None or _datasheet_types() is None:
        return

    required = _required_finding_keys()
    findings_to_check: list[dict] = []

    with tempfile.TemporaryDirectory() as td:
        # AM-001 fire
        cache_stm = _setup_cache(Path(td), "stm32f103c8t6", "STM32F103C8T6")
        if cache_stm is None:
            return
        cache_lm = _setup_cache(Path(td), "lm2596-adj", "LM2596-ADJ")
        if cache_lm is None:
            return

        u1 = ic("U1", "STM32F103C8T6",
                [("24", "VDD_1"), ("2", "PC13-TAMPER-RTC"), ("8", "VSS_1")],
                mpn="STM32F103C8T6")
        ctx_stm = build_ctx(
            components=[u1],
            nets={
                "OVERVOLT": [("U1", "24")],
                "I2C1_SDA": [("U1", "2")],
                "GND":      [("U1", "8")],
            },
            known_power_rails={"OVERVOLT", "GND"},
        )
        ctx_stm.cache_dir = cache_stm

        findings_to_check += ld.detect_absolute_max_violations(
            ctx_stm, {"OVERVOLT": 5.0})
        findings_to_check += ld.detect_5v_on_non_tolerant_pin(
            ctx_stm, {"I2C1_SDA": 5.0})
        findings_to_check += ld.detect_wrong_signal_type(ctx_stm)
        findings_to_check += ld.detect_tj_exceeds_max(
            [{"ref": "U1", "mpn": "STM32F103C8T6",
              "ambient_c": 25.0, "pdiss_w": 3.0}],
            source="test", cache_dir=cache_stm,
        )

        # EX-001 fire on a separate ctx (LM2596-ADJ regulator with no caps)
        u2 = ic("U2", "LM2596-ADJ",
                [("1", "VIN"), ("3", "Ground")], mpn="LM2596-ADJ")
        ctx_lm = build_ctx(
            components=[u2],
            nets={"VIN_RAIL": [("U2", "1")], "GND2": [("U2", "3")]},
            known_power_rails={"VIN_RAIL", "GND2"},
        )
        ctx_lm.cache_dir = cache_lm
        findings_to_check += ld.detect_missing_required_components(ctx_lm, [{
            "ref": "U2", "mpn": "LM2596-ADJ",
            "input_rail": "VIN_RAIL", "output_rail": None,
            "inductor": "L1",
        }])

    rule_ids_seen = {f["rule_id"] for f in findings_to_check}
    assert "AM-001" in rule_ids_seen, "AM-001 must fire in this fixture"
    assert "FT-001" in rule_ids_seen, "FT-001 must fire in this fixture"
    assert "TJ-001" in rule_ids_seen, "TJ-001 must fire in this fixture"
    assert "EX-001" in rule_ids_seen, "EX-001 must fire in this fixture"

    for f in findings_to_check:
        missing = required - set(f.keys())
        assert not missing, (
            f"Finding for {f.get('rule_id')} missing envelope keys: {missing}"
        )
        assert f.get("schema_era") == "v1.4", (
            f"schema_era must be 'v1.4' on every 4c finding; "
            f"got {f.get('schema_era')!r} for {f.get('rule_id')}"
        )
        assert f.get("confidence") == "datasheet-backed", (
            f"4c findings always datasheet-backed; got "
            f"{f.get('confidence')!r} for {f.get('rule_id')}"
        )
        assert f.get("evidence_source") == "datasheet"


# ---------------------------------------------------------------------------
# __main__ runner — mirror the convention used by other harness unit tests
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import traceback

    tests = [
        # AM-001
        test_am_001_fires_on_vdd_above_absolute_max,
        test_am_001_silent_when_vdd_within_absolute_max,
        test_am_001_silent_when_no_mpn,
        # OV-001
        test_ov_001_fires_above_recommended_max,
        test_ov_001_fires_below_recommended_min,
        test_ov_001_silent_within_recommended_range,
        # TJ-001
        test_tj_001_fires_when_tj_estimate_exceeds_max,
        test_tj_001_silent_when_tj_estimate_within_max,
        # FT-001
        test_ft_001_fires_on_5v_to_non_tolerant_pin,
        test_ft_001_silent_below_threshold,
        # PM-001
        test_pm_001_fires_when_i2c_net_on_non_i2c_pin,
        test_pm_001_silent_when_alt_functions_empty,
        # EX-001
        test_ex_001_fires_when_input_capacitor_missing,
        test_ex_001_silent_when_input_capacitor_present,
        test_ex_001_fires_when_inductor_missing_in_switching,
        # cross-rule
        test_all_fired_findings_carry_required_envelope_keys,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception:
            failed += 1
            print(f"FAIL: {t.__name__}")
            traceback.print_exc()
    total = passed + failed
    print(f"\n{passed} passed, {failed} failed ({total} total)")
    sys.exit(0 if failed == 0 else 1)
