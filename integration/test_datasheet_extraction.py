"""
Integration tests for datasheet extraction infrastructure.

Tests datasheet_score.py, datasheet_page_selector.py, datasheet_extract_cache.py,
and SPICE spec fetcher integration. Run from the testharness root:

    python3 integration/test_datasheet_extraction.py

Requires KICAD_HAPPY_DIR set (or ../kicad-happy as sibling).
"""

TIER = "online"

import json
import os
import sys
import tempfile
from pathlib import Path

# Resolve kicad-happy
KICAD_HAPPY_DIR = os.environ.get("KICAD_HAPPY_DIR",
    str(Path(__file__).resolve().parent.parent.parent / "kicad-happy"))
sys.path.insert(0, f"{KICAD_HAPPY_DIR}/skills/kicad/scripts")
sys.path.insert(0, f"{KICAD_HAPPY_DIR}/skills/spice/scripts")

passed = 0
failed = 0
skipped = 0


def report(name, ok, skip=False):
    global passed, failed, skipped
    if skip:
        skipped += 1
        print(f"  SKIP: {name}")
    elif ok:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")


# ===== Group 1: datasheet_score.py =====
print("Group 1: datasheet_score.py")
from datasheet_score import score_extraction

# 1.1 Perfect extraction
perfect = {
    "category": "switching_regulator",
    "pins": [
        {"number": "1", "name": "FB", "type": "analog", "direction": "input",
         "description": "Feedback", "voltage_abs_max": 6.0,
         "required_external": "Resistor divider"},
        {"number": "2", "name": "EN", "type": "digital", "direction": "input",
         "description": "Enable", "threshold_high_v": 1.2, "threshold_low_v": 0.4,
         "has_internal_pulldown": True, "required_external": "VIN for always-on"},
        {"number": "3", "name": "VIN", "type": "power", "direction": "input",
         "description": "Input supply", "voltage_abs_max": 6.0,
         "voltage_operating_min": 0.5, "voltage_operating_max": 5.5,
         "required_external": "10uF input cap"},
        {"number": "4", "name": "GND", "type": "ground", "direction": "passive",
         "description": "Ground"},
        {"number": "5", "name": "SW", "type": "power", "direction": "bidirectional",
         "description": "Switch node", "current_max_ma": 3600,
         "required_external": "Inductor 0.47-2.2uH"},
        {"number": "6", "name": "VOUT", "type": "power", "direction": "output",
         "description": "Output", "voltage_abs_max": 6.0, "voltage_operating_max": 5.5,
         "required_external": "22uF output cap"},
    ],
    "absolute_maximum_ratings": {
        "vin_max_v": 6.0, "vout_max_v": 6.0, "junction_temp_max_c": 150,
        "storage_temp_min_c": -65, "storage_temp_max_c": 150,
        "esd_hbm_v": 2000, "esd_cdm_v": 500,
    },
    "recommended_operating_conditions": {
        "vin_min_v": 0.5, "vin_max_v": 5.5, "vout_min_v": 1.8,
        "vout_max_v": 5.5, "temp_min_c": -40, "temp_max_c": 85,
    },
    "electrical_characteristics": {
        "vref_v": 0.595, "vref_accuracy_pct": 1.0,
        "switching_frequency_khz": 1200, "quiescent_current_ua": 12,
        "output_current_max_ma": 1000,
    },
    "application_circuit": {
        "topology": "boost", "inductor_recommended": "1uH, Isat > 3.6A",
        "input_cap_recommended": "10uF ceramic X5R",
        "output_cap_recommended": "22uF ceramic x2",
        "vout_formula": "Vout = 0.595 * (1 + R1/R2)",
        "notes": ["Keep SW trace short", "Place caps close to IC"],
    },
    "spice_specs": {
        "vref": 0.595, "supply_min": 0.5, "supply_max": 5.5,
        "iq_ua": 12, "iout_max_ma": 1000,
    },
}
r = score_extraction(perfect, expected_pin_count=6)
report("1.1 Perfect extraction >= 9.5", r["total"] >= 9.5 and r["sufficient"])

# 1.2 Empty extraction
empty = {
    "category": "switching_regulator", "pins": [],
    "absolute_maximum_ratings": {}, "recommended_operating_conditions": {},
    "electrical_characteristics": {}, "application_circuit": {}, "spice_specs": {},
}
r = score_extraction(empty)
report("1.2 Empty extraction < 2.0", r["total"] < 2.0 and not r["sufficient"])

# 1.3 Missing pins
partial = {
    "category": "linear_regulator",
    "pins": [
        {"number": "1", "name": "VIN", "type": "power", "direction": "input",
         "description": "Input", "voltage_abs_max": 15.0},
        {"number": "2", "name": "GND", "type": "ground", "direction": "passive",
         "description": "Ground"},
        {"number": "3", "name": "VOUT", "type": "power", "direction": "output",
         "description": "Output", "voltage_abs_max": 6.0},
    ],
    "absolute_maximum_ratings": {"vin_max_v": 15.0, "junction_temp_max_c": 150},
    "recommended_operating_conditions": {"vin_min_v": 4.5, "vin_max_v": 12.0, "temp_min_c": -40, "temp_max_c": 125},
    "electrical_characteristics": {"vref_v": 1.25, "quiescent_current_ua": 55, "dropout_mv": 1200},
    "application_circuit": {"topology": "linear", "input_cap_recommended": "1uF", "output_cap_recommended": "10uF"},
    "spice_specs": {"vref": 1.25, "dropout_mv": 1200, "iq_ua": 55},
}
r = score_extraction(partial, expected_pin_count=6)
report("1.3 Missing pins reduces score", r["pin_coverage"] < 8.0)

# 1.4 Opamp missing GBW
opamp = {
    "category": "operational_amplifier",
    "pins": [
        {"number": "1", "name": "OUT", "type": "analog", "direction": "output", "description": "Output"},
        {"number": "2", "name": "V-", "type": "power", "direction": "input", "description": "V-", "voltage_abs_max": 18.0},
        {"number": "3", "name": "IN+", "type": "analog", "direction": "input", "description": "IN+"},
        {"number": "4", "name": "IN-", "type": "analog", "direction": "input", "description": "IN-"},
        {"number": "5", "name": "V+", "type": "power", "direction": "input", "description": "V+", "voltage_abs_max": 18.0},
    ],
    "absolute_maximum_ratings": {"supply_max_v": 18.0, "junction_temp_max_c": 150},
    "recommended_operating_conditions": {"vin_min_v": 3.0, "vin_max_v": 32.0, "temp_min_c": -40, "temp_max_c": 85},
    "electrical_characteristics": {"input_offset_voltage_mv": 2.0},
    "application_circuit": {},
    "spice_specs": {"vos_mv": 2.0, "supply_min": 3.0, "supply_max": 32.0},
}
r = score_extraction(opamp)
report("1.4 Opamp missing GBW penalized", r["electrical_characteristics"] < 7.0)

# ===== Group 2: datasheet_page_selector.py =====
print("\nGroup 2: datasheet_page_selector.py")
from datasheet_page_selector import suggest_pages, _fallback_page_selection

DS_DIR = Path("reference/datasheets_verification")

# 2.1 Page selection returns valid pages
pdf_path = DS_DIR / "OPA4991.pdf"
if pdf_path.exists():
    sel = suggest_pages(str(pdf_path), "OPA4991", "opamp")
    report("2.1 Page selection valid",
           len(sel.pages) > 0 and 1 in sel.pages and sel.total_pages > 0
           and sel.confidence != "error")
else:
    report("2.1 Page selection valid", False, skip=True)

# 2.2 Short datasheet returns all
pdf_path = DS_DIR / "NE5532.pdf"
if pdf_path.exists():
    sel = suggest_pages(str(pdf_path), "NE5532", "opamp")
    if sel.total_pages <= 10:
        report("2.2 Short datasheet returns all",
               sel.confidence == "all_pages" and len(sel.pages) == sel.total_pages)
    else:
        report("2.2 Short datasheet returns all",
               len(sel.pages) < sel.total_pages)
else:
    report("2.2 Short datasheet returns all", False, skip=True)

# 2.3 max_pages respected
pdf_path = DS_DIR / "OPA4991.pdf"
if pdf_path.exists():
    sel = suggest_pages(str(pdf_path), "OPA4991", "opamp", max_pages=8)
    report("2.3 max_pages respected",
           sel.total_pages > 10 and len(sel.pages) <= 8)
else:
    report("2.3 max_pages respected", False, skip=True)

# 2.4 Fallback without pdftotext
pages = _fallback_page_selection(total_pages=50, max_pages=10)
report("2.4 Fallback selection",
       1 in pages and 50 in pages and len(pages) <= 10 and len(pages) >= 5)

# ===== Group 3: datasheet_extract_cache.py =====
print("\nGroup 3: datasheet_extract_cache.py")
from datasheet_extract_cache import (
    cache_extraction, get_cached_extraction,
    list_extractions, is_extraction_stale, EXTRACTION_VERSION,
    get_extraction_for_review, update_datasheets_index,
)

# 3.1 Write/read/list
with tempfile.TemporaryDirectory() as tmpdir:
    ed = Path(tmpdir) / "datasheets" / "extracted"
    ext = {"mpn": "TEST1", "category": "ic", "pins": [{"number": "1", "name": "VCC", "type": "power"}],
           "extraction_metadata": {"extraction_score": 8.5}}
    cache_extraction(ed, "TEST1", ext)
    cached = get_cached_extraction(ed, "TEST1")
    items = list_extractions(ed)
    report("3.1 Write/read/list",
           cached is not None and cached["mpn"] == "TEST1" and len(items) == 1
           and (ed / "index.json").exists())

# 3.2 Staleness — version upgrade
with tempfile.TemporaryDirectory() as tmpdir:
    ed = Path(tmpdir) / "datasheets" / "extracted"
    ext = {"mpn": "OLD", "category": "ic", "pins": [],
           "extraction_metadata": {"extraction_version": 0, "extraction_score": 8.0,
                                   "extraction_date": "2026-03-31T00:00:00+00:00"}}
    cache_extraction(ed, "OLD", ext)
    stale, reason = is_extraction_stale(ed, "OLD")
    report("3.2 Version upgrade stale", stale and "schema_upgrade" in reason)

# 3.3 Staleness — low score
with tempfile.TemporaryDirectory() as tmpdir:
    ed = Path(tmpdir) / "datasheets" / "extracted"
    ext = {"mpn": "LOW", "category": "ic", "pins": [],
           "extraction_metadata": {"extraction_version": EXTRACTION_VERSION, "extraction_score": 3.5,
                                   "retry_count": 1, "extraction_date": "2026-03-31T00:00:00+00:00"}}
    cache_extraction(ed, "LOW", ext)
    stale, reason = is_extraction_stale(ed, "LOW")
    report("3.3 Low score stale", stale and "low_score" in reason)

# 3.4 Staleness — PDF changed
with tempfile.TemporaryDirectory() as tmpdir:
    ed = Path(tmpdir) / "datasheets" / "extracted"
    dd = Path(tmpdir) / "datasheets"
    dd.mkdir(parents=True, exist_ok=True)
    pdf = dd / "FAKE.pdf"
    pdf.write_bytes(b"%PDF-1.4 v1")
    ext = {"mpn": "FAKE", "category": "ic", "pins": [{"number": "1", "name": "VCC", "type": "power"}],
           "extraction_metadata": {"extraction_version": EXTRACTION_VERSION, "extraction_score": 8.0,
                                   "extraction_date": "2026-03-31T00:00:00+00:00", "source_pdf": "FAKE.pdf"}}
    cache_extraction(ed, "FAKE", ext, source_pdf=str(pdf))
    stale1, _ = is_extraction_stale(ed, "FAKE", datasheets_dir=str(dd))
    pdf.write_bytes(b"%PDF-1.4 v2 modified")
    stale2, reason = is_extraction_stale(ed, "FAKE", datasheets_dir=str(dd))
    report("3.4 PDF hash change", not stale1 and stale2 and "pdf_changed" in reason)

# 3.5 get_extraction_for_review
with tempfile.TemporaryDirectory() as tmpdir:
    ed = Path(tmpdir) / "datasheets" / "extracted"
    ext1, st1 = get_extraction_for_review("MISSING", ed)
    ext = {"mpn": "OK", "category": "ic", "pins": [{"number": "1", "name": "VCC", "type": "power"}],
           "extraction_metadata": {"extraction_version": EXTRACTION_VERSION, "extraction_score": 9.0,
                                   "extraction_date": "2026-03-31T00:00:00+00:00"}}
    cache_extraction(ed, "OK", ext)
    ext2, st2 = get_extraction_for_review("OK", ed)
    report("3.5 Review status", ext1 is None and st1 == "missing" and ext2 is not None and st2 == "cached")

# ===== Group 4: SPICE integration =====
print("\nGroup 4: SPICE integration")
from spice_spec_fetcher import fetch_specs_from_extraction, fetch_specs

# 4.1 Read from cache
with tempfile.TemporaryDirectory() as tmpdir:
    ed = Path(tmpdir) / "datasheets" / "extracted"
    ed.mkdir(parents=True, exist_ok=True)
    ext = {"mpn": "LM358DR", "category": "operational_amplifier",
           "spice_specs": {"gbw_hz": 1e6, "slew_vus": 0.3, "vos_mv": 2.0, "supply_min": 3.0, "supply_max": 32.0},
           "extraction_metadata": {"extraction_version": EXTRACTION_VERSION}}
    cache_extraction(ed, "LM358DR", ext)
    specs = fetch_specs_from_extraction("LM358DR", tmpdir)
    report("4.1 Fetch from cache",
           specs is not None and specs["gbw_hz"] == 1e6 and "_source" in specs)

# 4.2 Missing returns None
empty_dir = os.path.join(tempfile.gettempdir(), "kicad_happy_empty_nonexistent")
specs = fetch_specs_from_extraction("NOPE", empty_dir)
report("4.2 Missing returns None", specs is None)

# 4.3 Full cascade
specs, source = fetch_specs("DEFINITELY_NOT_REAL_12345", project_dir=empty_dir)
report("4.3 Cascade missing part", specs is None)

# ===== Group 5: End-to-end =====
print("\nGroup 5: End-to-end with real datasheets")
ds_dir = Path("repos/Arduino_shield_kicad/datasheets")
if ds_dir.exists() and (ds_dir / "index.json").exists():
    with open(ds_dir / "index.json") as f:
        index = json.load(f)
    count = 0
    for mpn, entry in index.get("parts", {}).items():
        if entry.get("status") != "ok":
            continue
        pdf_path = ds_dir / entry["file"]
        if not pdf_path.exists():
            continue
        sel = suggest_pages(str(pdf_path), mpn)
        assert len(sel.pages) > 0 and sel.confidence != "error"
        count += 1
    report(f"5.1 Page selection on {count} real datasheets", count > 0)
else:
    report("5.1 Page selection on real datasheets", False, skip=True)

# 5.3 update_datasheets_index
with tempfile.TemporaryDirectory() as tmpdir:
    dd = Path(tmpdir) / "datasheets"
    dd.mkdir()
    ed = dd / "extracted"
    ds_index = {"parts": {"TEST": {"file": "TEST.pdf", "status": "ok"}}}
    with open(dd / "index.json", "w") as f:
        json.dump(ds_index, f)
    ext = {"mpn": "TEST", "category": "ic", "pins": [{"number": "1", "name": "VCC", "type": "power"}],
           "extraction_metadata": {"extraction_score": 7.5, "extraction_date": "2026-03-31"}}
    cache_extraction(ed, "TEST", ext)
    update_datasheets_index(str(dd), "TEST", ext)
    with open(dd / "index.json") as f:
        updated = json.load(f)
    report("5.3 update_datasheets_index",
           "extraction" in updated["parts"]["TEST"]
           and updated["parts"]["TEST"]["extraction"]["score"] == 7.5)

# ===== Summary =====
total = passed + failed + skipped
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed, {skipped} skipped ({total} total)")
print(f"{'='*50}")
sys.exit(1 if failed > 0 else 0)
