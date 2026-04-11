"""Unit tests for validate/verify_parser.py (P1 parser verification).

Tests use tiny hand-built sexp fixtures passed directly into the fact
extractor — no external .kicad_sch files. The analyzer output side is
simulated as plain dicts.
"""

TIER = "unit"

import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
sys.path.insert(0, str(HARNESS_DIR / "validate"))

# verify_parser imports sexp_parser from kicad-happy on its own; we rely on
# whatever path resolution it does at import time.
from verify_parser import extract_sexp_facts


# === extract_sexp_facts: component set ===

def test_extract_sexp_facts_empty_root():
    """An empty kicad_sch root produces empty fact sets."""
    root = ["kicad_sch"]
    facts = extract_sexp_facts(root)
    assert facts["component_refs"] == set()
    assert facts["component_count"] == 0
    assert facts["label_count"] == 0
    assert facts["label_names"] == set()
    assert facts["hierarchical_label_count"] == 0
    assert facts["no_connect_count"] == 0


# === extract_sexp_facts: placed components ===

def test_extract_sexp_facts_single_component():
    """A single placed symbol with reference R1 = value 10k."""
    root = [
        "kicad_sch",
        ["symbol",
            ["lib_id", "Device:R"],
            ["at", 100.0, 50.0, 0.0],
            ["property", "Reference", "R1"],
            ["property", "Value", "10k"],
            ["property", "Footprint", "Resistor_SMD:R_0603_1608Metric"],
        ],
    ]
    facts = extract_sexp_facts(root)
    assert facts["component_refs"] == {"R1"}
    assert facts["component_count"] == 1
    assert facts["component_values"] == {"R1": "10k"}
    assert facts["component_footprints"] == {"R1": "Resistor_SMD:R_0603_1608Metric"}


def test_extract_sexp_facts_multiple_components():
    """Three placed components with different references."""
    root = [
        "kicad_sch",
        ["symbol", ["lib_id", "Device:R"], ["property", "Reference", "R1"], ["property", "Value", "10k"]],
        ["symbol", ["lib_id", "Device:R"], ["property", "Reference", "R2"], ["property", "Value", "20k"]],
        ["symbol", ["lib_id", "Device:C"], ["property", "Reference", "C1"], ["property", "Value", "100nF"]],
    ]
    facts = extract_sexp_facts(root)
    assert facts["component_refs"] == {"R1", "R2", "C1"}
    assert facts["component_count"] == 3
    assert facts["component_values"] == {"R1": "10k", "R2": "20k", "C1": "100nF"}


def test_extract_sexp_facts_lib_name_takes_precedence():
    """KH-083: KiCad 7+ may write `(lib_name "X")` alongside `(lib_id ...)`
    and use lib_name as the actual key into lib_symbols. Power detection
    must look up via lib_name first. Confirmed empirically on
    FarrenMartinus/EMG in 2026-04-10 — placed Simulation_SPICE:0 symbol's
    lib_symbol is keyed as "0_1" with the (power) flag."""
    root = [
        "kicad_sch",
        ["lib_symbols",
            ["symbol", "0_1", ["power"], ["in_bom", "yes"],
             ["property", "Reference", "#GND"]],
            ["symbol", "Device:R"],
        ],
        # Placed: lib_name="0_1" (the key) but lib_id="Simulation_SPICE:0"
        ["symbol",
            ["lib_name", "0_1"],
            ["lib_id", "Simulation_SPICE:0"],
            ["property", "Reference", "#GND02"],
            ["property", "Value", "0"],
        ],
        ["symbol",
            ["lib_id", "Device:R"],
            ["property", "Reference", "R1"],
            ["property", "Value", "10k"],
        ],
    ]
    facts = extract_sexp_facts(root)
    assert facts["component_refs"] == {"R1"}
    assert facts["component_count"] == 1


def test_extract_sexp_facts_filters_flg_ref_fallback():
    """Symbols whose ref starts with `#FLG` are filtered. Mirrors the
    type_map at kicad_utils.py:416 (`#FLG` → "flag") combined with the
    real_components filter at analyze_schematic.py:2784 (excludes "flag"
    type). Confirmed empirically on ForestHubAI/boardsmith in 2026-04-10."""
    root = [
        "kicad_sch",
        ["lib_symbols",
            ["symbol", "boardsmith:PWR_FLAG", ["in_bom", "no"]],
        ],
        ["symbol",
            ["lib_id", "boardsmith:PWR_FLAG"],
            ["in_bom", "no"],
            ["property", "Reference", "#FLG001"],
            ["property", "Value", "GND"],
        ],
        ["symbol",
            ["lib_id", "Device:R"],
            ["property", "Reference", "R1"],
            ["property", "Value", "10k"],
        ],
    ]
    facts = extract_sexp_facts(root)
    assert facts["component_refs"] == {"R1"}
    assert facts["component_count"] == 1


def test_extract_sexp_facts_filters_pwr_ref_fallback():
    """Symbols whose ref starts with `#PWR` are filtered even when their
    lib_symbol lacks the (power) flag. Mirrors the third rule in
    kicad_utils.classify_component():395-396 — confirmed empirically on
    cnlohr/cnhardware KiCad 9 files in 2026-04-10 where KiCad's
    `power:GND` lib_symbol was missing the (power) flag entirely."""
    root = [
        "kicad_sch",
        ["lib_symbols",
            ["symbol", "power:GND", ["in_bom", "yes"]],  # NO (power) flag
        ],
        # The placed power symbol — analyzer drops it via #PWR ref fallback
        ["symbol",
            ["lib_id", "power:GND"],
            ["in_bom", "yes"],  # in_bom=yes, so rule 2 doesn't catch it
            ["property", "Reference", "#PWR01"],
            ["property", "Value", "GND"],
        ],
        ["symbol",
            ["lib_id", "Device:R"],
            ["property", "Reference", "R1"],
            ["property", "Value", "10k"],
        ],
    ]
    facts = extract_sexp_facts(root)
    assert facts["component_refs"] == {"R1"}
    assert facts["component_count"] == 1


def test_extract_sexp_facts_filters_power_prefix_when_not_in_bom():
    """Symbols with lib_id starting with `power:` AND in_bom=no are
    filtered. Mirrors rule 2 in kicad_utils.classify_component():389-390.
    KH-080 carve-out: parts in the power: library that ARE in_bom are
    real components (e.g. DD4012SA buck converter) and must NOT be
    filtered."""
    root = [
        "kicad_sch",
        ["lib_symbols"],
        # Power symbol: power: prefix, in_bom no, no #PWR ref
        ["symbol",
            ["lib_id", "power:+5V"],
            ["in_bom", "no"],
            ["property", "Reference", "FAKEREF1"],
        ],
        # Real BOM part in the power: library — KH-080 carve-out
        ["symbol",
            ["lib_id", "power:DD4012SA"],
            ["in_bom", "yes"],
            ["property", "Reference", "U1"],
            ["property", "Value", "DD4012SA"],
        ],
    ]
    facts = extract_sexp_facts(root)
    assert facts["component_refs"] == {"U1"}
    assert facts["component_values"] == {"U1": "DD4012SA"}


def test_extract_sexp_facts_filters_power_lib_symbols():
    """Symbols whose lib_id resolves to a (power)-flagged lib_symbol are
    filtered out, matching analyze_schematic.py:546 (`is_power_sym = ...`)
    and 2782-2785 (`real_components = [c for c in ... if c['type'] not in
    power_*`]). Reference prefix alone is unreliable — `#G1` (graphic) is
    kept while `#SUPPLY*` (power-flagged) is dropped. Confirmed empirically
    on RoboJackets/robocup-pcb in 2026-04-10."""
    root = [
        "kicad_sch",
        ["lib_symbols",
            ["symbol", "Device:R", ["property", "Reference", "R"]],
            ["symbol", "kicker:GND", ["power"], ["property", "Reference", "#PWR"]],
            ["symbol", "kicker:supply2_+5V", ["power"], ["property", "Reference", "#SUPPLY"]],
            ["symbol", "bitaxe:LOGO", ["property", "Reference", "#G"]],
        ],
        # Real placed components
        ["symbol",
            ["lib_id", "Device:R"],
            ["property", "Reference", "R1"],
            ["property", "Value", "10k"],
        ],
        # Graphic with #G prefix — analyzer keeps these in components[]
        ["symbol",
            ["lib_id", "bitaxe:LOGO"],
            ["property", "Reference", "#G1"],
            ["property", "Value", "LOGO"],
        ],
        # Power supply — analyzer drops these via lib_symbol (power) flag
        ["symbol",
            ["lib_id", "kicker:supply2_+5V"],
            ["property", "Reference", "#SUPPLY93"],
            ["property", "Value", "+5V"],
        ],
        ["symbol",
            ["lib_id", "kicker:GND"],
            ["property", "Reference", "#PWR01"],
            ["property", "Value", "GND"],
        ],
    ]
    facts = extract_sexp_facts(root)
    # R1 (real component) and #G1 (graphic, kept) survive; both power refs are dropped
    assert facts["component_refs"] == {"R1", "#G1"}
    assert facts["component_count"] == 2
    assert facts["component_values"] == {"R1": "10k", "#G1": "LOGO"}


def test_extract_sexp_facts_ignores_lib_symbols_template():
    """Symbols inside a (lib_symbols ...) block are definitions, not placed components."""
    root = [
        "kicad_sch",
        ["lib_symbols",
            ["symbol", "Device:R",
                ["property", "Reference", "R"],
                ["property", "Value", "R"],
            ],
        ],
        ["symbol",
            ["lib_id", "Device:R"],
            ["property", "Reference", "R1"],
            ["property", "Value", "10k"],
        ],
    ]
    facts = extract_sexp_facts(root)
    # Only R1 (the placed symbol), not the R template from lib_symbols
    assert facts["component_refs"] == {"R1"}
    assert facts["component_count"] == 1


# === extract_sexp_facts: labels ===

def test_extract_sexp_facts_local_labels():
    """Local (label ...) nodes contribute to label_count and label_names."""
    root = [
        "kicad_sch",
        ["label", "SDA", ["at", 10.0, 20.0, 0.0]],
        ["label", "SCL", ["at", 10.0, 30.0, 0.0]],
    ]
    facts = extract_sexp_facts(root)
    assert facts["label_count"] == 2
    assert facts["label_names"] == {"SDA", "SCL"}
    assert facts["hierarchical_label_count"] == 0


def test_extract_sexp_facts_hierarchical_and_global_labels():
    """Hierarchical and global labels add to total label count."""
    root = [
        "kicad_sch",
        ["label", "LOCAL_NET", ["at", 10.0, 20.0, 0.0]],
        ["global_label", "PWR_EN", ["shape", "input"], ["at", 30.0, 20.0, 0.0]],
        ["hierarchical_label", "UART_TX", ["shape", "output"], ["at", 50.0, 20.0, 0.0]],
        ["hierarchical_label", "UART_RX", ["shape", "input"], ["at", 50.0, 25.0, 0.0]],
        ["directive_label", "~{RESET}", ["at", 70.0, 20.0, 0.0]],
    ]
    facts = extract_sexp_facts(root)
    assert facts["label_count"] == 5
    assert facts["label_names"] == {"LOCAL_NET", "PWR_EN", "UART_TX", "UART_RX", "~{RESET}"}
    assert facts["hierarchical_label_count"] == 2


def test_extract_sexp_facts_no_labels():
    """A schematic with no labels reports zero counts and empty set."""
    root = ["kicad_sch", ["symbol", ["lib_id", "Device:R"], ["property", "Reference", "R1"]]]
    facts = extract_sexp_facts(root)
    assert facts["label_count"] == 0
    assert facts["label_names"] == set()
    assert facts["hierarchical_label_count"] == 0


# === extract_sexp_facts: no_connects ===

def test_extract_sexp_facts_no_connects():
    """(no_connect ...) nodes contribute to no_connect_count."""
    root = [
        "kicad_sch",
        ["no_connect", ["at", 10.0, 20.0]],
        ["no_connect", ["at", 10.0, 30.0]],
        ["no_connect", ["at", 10.0, 40.0]],
    ]
    facts = extract_sexp_facts(root)
    assert facts["no_connect_count"] == 3
    assert facts["component_count"] == 0
    assert facts["label_count"] == 0


# === extract_analyzer_facts ===

from verify_parser import extract_analyzer_facts


def test_extract_analyzer_facts_empty():
    """Empty analyzer output produces empty fact sets."""
    output = {
        "components": [],
        "labels": [],
        "no_connects": [],
    }
    facts = extract_analyzer_facts(output)
    assert facts["component_refs"] == set()
    assert facts["component_count"] == 0
    assert facts["label_count"] == 0
    assert facts["label_names"] == set()
    assert facts["hierarchical_label_count"] == 0
    assert facts["no_connect_count"] == 0


def test_extract_analyzer_facts_components_and_labels():
    """Typical analyzer output with a few components and labels."""
    output = {
        "components": [
            {"reference": "R1", "value": "10k", "footprint": "R_0603", "type": "resistor"},
            {"reference": "R2", "value": "20k", "footprint": "R_0603", "type": "resistor"},
            {"reference": "C1", "value": "100nF", "footprint": "C_0402", "type": "capacitor"},
        ],
        "labels": [
            {"name": "SDA", "type": "label", "x": 10.0, "y": 20.0},
            {"name": "SCL", "type": "label", "x": 10.0, "y": 30.0},
            {"name": "UART_TX", "type": "hierarchical_label", "x": 50.0, "y": 20.0},
        ],
        "no_connects": [{"x": 5.0, "y": 5.0}, {"x": 6.0, "y": 6.0}],
    }
    facts = extract_analyzer_facts(output)
    assert facts["component_refs"] == {"R1", "R2", "C1"}
    assert facts["component_count"] == 3
    assert facts["component_values"] == {"R1": "10k", "R2": "20k", "C1": "100nF"}
    assert facts["component_footprints"] == {"R1": "R_0603", "R2": "R_0603", "C1": "C_0402"}
    assert facts["label_count"] == 3
    assert facts["label_names"] == {"SDA", "SCL", "UART_TX"}
    assert facts["hierarchical_label_count"] == 1
    assert facts["no_connect_count"] == 2


def test_extract_analyzer_facts_filters_synthetic_sheet_pin_labels():
    """Labels with `/<uuid>/<name>` shape are sheet-pin stubs synthesized
    by analyze_schematic.py:2885-2898 from each (pin "NAME") inside a
    (sheet ...) block. They aren't in the source file and would otherwise
    show up as `extra_item` mismatches. Confirmed empirically on
    skot/bitaxe in 2026-04-10 (29 synthetic `/<uuid>/...` hier labels).

    Real labels can include slashes too: leading-slash labels (`/CE`,
    `/BBE`) and slash-containing alt-function names (`PA1/VMUTE/3V3`)
    must be preserved. Both observed in 2026-04-10 on gav-vdm/G_Pad_Max
    and fachat/cbm_ultipet. The UUID regex precisely targets the
    synthetic format and avoids those false positives."""
    output = {
        "components": [],
        "labels": [
            {"name": "REAL_LABEL", "type": "label", "_sheet": 0},
            {"name": "/CE", "type": "label", "_sheet": 0},  # real, leading-slash
            {"name": "/BBE", "type": "label", "_sheet": 0},  # real, leading-slash
            {"name": "PA1/VMUTE/3V3", "type": "label", "_sheet": 0},  # real, alt-function
            {"name": "PB5/SSPIM_~{CS}/3V3", "type": "label", "_sheet": 0},  # real, alt-function
            {"name": "/WR + /MREQ", "type": "label", "_sheet": 0},  # real, logic notation
            {"name": "/4cf9c075-d009-4c35-9949-adda70ae20c7/TX",
             "type": "hierarchical_label", "_sheet": 0},  # synthetic UUID
            {"name": "/4cf9c075-d009-4c35-9949-adda70ae20c7/RX",
             "type": "hierarchical_label", "_sheet": 0},  # synthetic UUID
            {"name": "/sheet-clock-1/CLK0",
             "type": "hierarchical_label", "_sheet": 0},  # synthetic non-UUID
            {"name": "/sheet-debug-1/JTAG_TCK",
             "type": "hierarchical_label", "_sheet": 0},  # synthetic non-UUID
        ],
        "no_connects": [],
    }
    facts = extract_analyzer_facts(output)
    assert facts["label_names"] == {
        "REAL_LABEL", "/CE", "/BBE", "PA1/VMUTE/3V3", "PB5/SSPIM_~{CS}/3V3",
        "/WR + /MREQ",
    }
    assert facts["label_count"] == 6
    assert facts["hierarchical_label_count"] == 0


def test_extract_sexp_facts_counts_anonymous_symbols():
    """Symbols with empty/missing Reference property are still counted
    (analyzer keeps them in components[] with `reference=""`), but they
    don't get added to component_refs since there's no name to compare.
    Confirmed empirically on ltwmori/designGuardDesktopApp test fixtures
    in 2026-04-10 — case_04_empty_property_values.kicad_sch deliberately
    has 2 symbols with empty refs."""
    root = [
        "kicad_sch",
        ["lib_symbols"],
        # R1 — normal
        ["symbol",
            ["lib_id", "Device:R"],
            ["property", "Reference", "R1"],
            ["property", "Value", "10k"],
        ],
        # Empty Reference property
        ["symbol",
            ["lib_id", "Device:R"],
            ["property", "Reference", ""],
            ["property", "Value", "10k"],
        ],
        # No Reference property at all
        ["symbol",
            ["lib_id", "Device:C"],
            ["property", "Value", "100nF"],
        ],
    ]
    facts = extract_sexp_facts(root)
    assert facts["component_count"] == 3
    assert facts["component_refs"] == {"R1"}
    assert facts["component_values"] == {"R1": "10k"}


def test_extract_analyzer_facts_filters_walked_child_sheets():
    """Components/labels/no_connects with _sheet > 0 belong to walked
    child sheets and must be excluded — they aren't in the file the
    sexp parser is reading. Verified empirically on skot/bitaxe in
    2026-04-10: root file had 16 sexp components but the analyzer
    returned 136 because it walked 4 child sheets."""
    output = {
        "components": [
            {"reference": "R1", "value": "10k", "_sheet": 0},  # this file
            {"reference": "R2", "value": "20k", "_sheet": 1},  # child sheet
            {"reference": "R3", "value": "30k", "_sheet": 2},  # child sheet
        ],
        "labels": [
            {"name": "OWN", "type": "label", "_sheet": 0},
            {"name": "CHILD", "type": "label", "_sheet": 1},
        ],
        "no_connects": [
            {"x": 0, "y": 0, "_sheet": 0},
            {"x": 1, "y": 1, "_sheet": 1},
        ],
    }
    facts = extract_analyzer_facts(output)
    assert facts["component_refs"] == {"R1"}
    assert facts["component_count"] == 1
    assert facts["label_count"] == 1
    assert facts["label_names"] == {"OWN"}
    assert facts["no_connect_count"] == 1


def test_extract_analyzer_facts_missing_optional_fields():
    """Components without footprint or labels without name should be handled gracefully."""
    output = {
        "components": [
            {"reference": "R1", "value": "10k"},  # no footprint
            {"reference": "U1"},  # no value, no footprint
        ],
        "labels": [
            {"name": "", "type": "label", "x": 0, "y": 0},  # empty name
        ],
        "no_connects": [],
    }
    facts = extract_analyzer_facts(output)
    assert facts["component_refs"] == {"R1", "U1"}
    assert facts["component_count"] == 2
    assert facts["component_values"] == {"R1": "10k"}  # U1 omitted
    assert facts["component_footprints"] == {}  # both omitted
    assert facts["label_count"] == 1
    assert facts["label_names"] == set()  # empty name filtered out


# === compare_facts ===

from verify_parser import compare_facts


def test_compare_facts_identical_agrees():
    """Identical fact dicts produce no mismatches."""
    sexp = {
        "component_refs": {"R1", "R2"},
        "component_count": 2,
        "component_values": {"R1": "10k", "R2": "20k"},
        "component_footprints": {},
        "label_count": 0,
        "label_names": set(),
        "hierarchical_label_count": 0,
        "no_connect_count": 0,
    }
    analyzer = dict(sexp)
    analyzer["component_refs"] = {"R1", "R2"}  # new set, same values
    analyzer["component_values"] = {"R1": "10k", "R2": "20k"}
    mismatches = compare_facts(sexp, analyzer)
    assert mismatches == []


def test_compare_facts_missing_component_in_analyzer():
    """If the analyzer is missing a component the sexp has, report `missing_item`."""
    sexp = {
        "component_refs": {"R1", "R2", "R3"},
        "component_count": 3,
        "component_values": {},
        "component_footprints": {},
        "label_count": 0,
        "label_names": set(),
        "hierarchical_label_count": 0,
        "no_connect_count": 0,
    }
    analyzer = dict(sexp)
    analyzer["component_refs"] = {"R1", "R2"}
    analyzer["component_count"] = 2
    mismatches = compare_facts(sexp, analyzer)
    kinds = {m["kind"] for m in mismatches}
    assert "missing_item" in kinds
    missing = [m for m in mismatches if m["kind"] == "missing_item"]
    assert any("R3" in m["detail"] for m in missing)


def test_compare_facts_extra_component_in_analyzer():
    """If the analyzer reports a component the sexp doesn't have, report `extra_item`."""
    sexp = {
        "component_refs": {"R1"},
        "component_count": 1,
        "component_values": {},
        "component_footprints": {},
        "label_count": 0,
        "label_names": set(),
        "hierarchical_label_count": 0,
        "no_connect_count": 0,
    }
    analyzer = {
        "component_refs": {"R1", "R_PHANTOM"},
        "component_count": 2,
        "component_values": {},
        "component_footprints": {},
        "label_count": 0,
        "label_names": set(),
        "hierarchical_label_count": 0,
        "no_connect_count": 0,
    }
    mismatches = compare_facts(sexp, analyzer)
    kinds = {m["kind"] for m in mismatches}
    assert "extra_item" in kinds
    extras = [m for m in mismatches if m["kind"] == "extra_item"]
    assert any("R_PHANTOM" in m["detail"] for m in extras)


def test_compare_facts_wrong_value_for_matched_ref():
    """Same refs but different Value property reports `wrong_value`."""
    sexp = {
        "component_refs": {"R1"},
        "component_count": 1,
        "component_values": {"R1": "10k"},
        "component_footprints": {},
        "label_count": 0,
        "label_names": set(),
        "hierarchical_label_count": 0,
        "no_connect_count": 0,
    }
    analyzer = dict(sexp)
    analyzer["component_refs"] = {"R1"}
    analyzer["component_values"] = {"R1": "1k"}
    mismatches = compare_facts(sexp, analyzer)
    kinds = {m["kind"] for m in mismatches}
    assert "wrong_value" in kinds
    wrongs = [m for m in mismatches if m["kind"] == "wrong_value"]
    assert any("R1" in m["detail"] and "10k" in m["detail"] and "1k" in m["detail"]
               for m in wrongs)


def test_compare_facts_wrong_count():
    """Different counts report `wrong_count` with the field name."""
    sexp = {
        "component_refs": set(),
        "component_count": 0,
        "component_values": {},
        "component_footprints": {},
        "label_count": 0,
        "label_names": set(),
        "hierarchical_label_count": 0,
        "no_connect_count": 5,
    }
    analyzer = dict(sexp)
    analyzer["no_connect_count"] = 3
    mismatches = compare_facts(sexp, analyzer)
    kinds = {m["kind"] for m in mismatches}
    assert "wrong_count" in kinds
    wrongs = [m for m in mismatches if m["kind"] == "wrong_count"]
    assert any("no_connect" in m["field"] for m in wrongs)


# === check_schematic_file ===

import tempfile
from verify_parser import check_schematic_file


def test_check_schematic_file_clean_match():
    """A hand-built sexp file that matches its hand-built analyzer output dict produces zero mismatches."""
    with tempfile.TemporaryDirectory() as td:
        sch = Path(td) / "test.kicad_sch"
        sch.write_text(
            '(kicad_sch\n'
            '  (symbol (lib_id "Device:R") (at 10 20 0)\n'
            '    (property "Reference" "R1") (property "Value" "10k")\n'
            '    (property "Footprint" "R_0603"))\n'
            '  (label "SDA" (at 30 40 0))\n'
            ')\n', encoding="utf-8"
        )
        analyzer_output = {
            "components": [{"reference": "R1", "value": "10k", "footprint": "R_0603"}],
            "labels": [{"name": "SDA", "type": "label", "x": 30, "y": 40}],
            "no_connects": [],
        }
        mismatches = check_schematic_file(str(sch), analyzer_output)
        assert mismatches == [], f"expected no mismatches, got: {mismatches}"


def test_check_schematic_file_missing_component():
    """A sexp with R2 that the analyzer output lacks reports a missing_item."""
    with tempfile.TemporaryDirectory() as td:
        sch = Path(td) / "test.kicad_sch"
        sch.write_text(
            '(kicad_sch\n'
            '  (symbol (lib_id "Device:R") (at 10 20 0) (property "Reference" "R1") (property "Value" "10k"))\n'
            '  (symbol (lib_id "Device:R") (at 30 20 0) (property "Reference" "R2") (property "Value" "20k"))\n'
            ')\n', encoding="utf-8"
        )
        analyzer_output = {
            "components": [{"reference": "R1", "value": "10k", "footprint": ""}],
            "labels": [],
            "no_connects": [],
        }
        mismatches = check_schematic_file(str(sch), analyzer_output)
        assert any(m["kind"] == "missing_item" and "R2" in m["detail"] for m in mismatches), \
            f"expected missing_item R2, got: {mismatches}"


def test_check_schematic_file_nonexistent_file():
    """A missing file returns a single parse_error record."""
    result = check_schematic_file("/nonexistent/path/missing.kicad_sch", {})
    assert len(result) == 1
    assert result[0]["kind"] == "parse_error"
    assert result[0]["field"] == "file"
    assert "missing.kicad_sch" in result[0]["detail"]


# === Runner ===

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
