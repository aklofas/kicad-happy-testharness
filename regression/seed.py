#!/usr/bin/env python3
"""Generate seed assertions from existing analyzer outputs.

Reads schematic/pcb/gerber outputs and creates conservative assertions
that should remain stable across analyzer changes. Useful for
bootstrapping the assertion set for newly tested repos.

Outputs are in results/outputs/{type}/{repo}/.
Assertions are written to data/{repo}/{project}/assertions/{type}/.

Usage:
    python3 regression/seed.py --repo OpenMower
    python3 regression/seed.py --repo OpenMower --type schematic
    python3 regression/seed.py --all
    python3 regression/seed.py --repo OpenMower --filter "dcdc*"
    python3 regression/seed.py --tolerance 0.15
    python3 regression/seed.py --all --type emc --prune-stale --dry-run
"""

import argparse
import fnmatch
import json
import math
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (
    OUTPUTS_DIR, DATA_DIR, ANALYZER_TYPES,
    DEFAULT_JOBS, add_repo_filter_args, resolve_repos,
    discover_projects, data_dir, list_repos,
    project_prefix, filter_project_outputs,
)


# Quality checks: detector field → (field_path, description, regex matching BAD values).
# Each generates a not_contains_match assertion: "no item should have this bad value".
_QUALITY_CHECKS = {
    "voltage_dividers": ("ratio", "non-zero ratio", r"^(0(\.0+)?|None|)$"),
    "rc_filters": ("cutoff_hz", "non-zero cutoff_hz", r"^(0(\.0+)?|None|)$"),
    "lc_filters": ("resonant_hz", "non-zero resonant_hz", r"^(0(\.0+)?|None|)$"),
    "current_sense": ("shunt.ref", "shunt ref present", r"^(None|)$"),
    "power_regulators": ("ref", "ref present", r"^(None|\?|)$"),
    "crystal_circuits": ("reference", "reference present", r"^(None|\?|)$"),
    "opamp_circuits": ("reference", "reference present", r"^(None|\?|)$"),
    "transistor_circuits": ("reference", "reference present", r"^(None|\?|)$"),
    "feedback_networks": ("r_top.ref", "r_top ref present", r"^(None|)$"),
}

# Known detectors loaded dynamically from schema inventory.
# Fallback used only if schema_inventory.json doesn't exist.
_FALLBACK_DETECTORS = [
    "addressable_led_chains", "bms_systems", "bridge_circuits",
    "buzzer_speaker_circuits", "crystal_circuits", "current_sense",
    "ethernet_interfaces", "feedback_networks", "hdmi_dvi_interfaces",
    "isolation_barriers", "key_matrices", "lc_filters", "memory_interfaces",
    "opamp_circuits", "power_regulators", "protection_devices", "rc_filters",
    "rf_chains", "rf_matching", "snubbers", "transistor_circuits",
    "voltage_dividers",
]

_known_detectors_cache = None

def _load_known_detectors():
    """Load known detector names from schema inventory (auto-discovered)."""
    global _known_detectors_cache
    if _known_detectors_cache is not None:
        return _known_detectors_cache
    inventory_file = DATA_DIR / "schema_inventory.json"
    if inventory_file.exists():
        try:
            inv = json.loads(inventory_file.read_text(encoding="utf-8"))
            detectors = sorted(inv.get("schematic", {}).keys())
            if detectors:
                _known_detectors_cache = detectors
                return detectors
        except (json.JSONDecodeError, OSError):
            pass
    _known_detectors_cache = _FALLBACK_DETECTORS
    return _FALLBACK_DETECTORS


# Field specs for domain-specific detectors. Defines expected fields and
# enum constraints. Used by _field_spec_assertions() to auto-generate
# quality assertions during seeding. Add entries for new detectors here.
_DETECTOR_FIELD_SPECS = {
    "battery_chargers": {
        "required_fields": ["charger_reference", "charger_type"],
        "enum_fields": {
            "charger_type": ["single_cell_linear", "single_cell_switching",
                            "standalone_protection"],
        },
    },
    "motor_drivers": {
        "required_fields": ["driver_reference", "driver_type"],
        "enum_fields": {
            "driver_type": ["stepper", "dc_brushed_h_bridge"],
        },
    },
    "esd_coverage_audit": {
        "required_fields": ["connector_ref", "coverage", "risk_level"],
        "enum_fields": {
            "coverage": ["full", "partial", "none"],
            "risk_level": ["high_risk", "medium_risk", "low_risk"],
        },
    },
    "debug_interfaces": {
        "required_fields": ["connector_ref", "interface_type"],
        "enum_fields": {
            "interface_type": ["swd", "jtag", "debug"],
        },
    },
    "power_path": {
        "required_fields": ["ref", "type"],
        "enum_fields": {
            "type": ["load_switch", "ideal_diode", "power_mux",
                     "usb_pd_controller"],
        },
    },
    # Batch 4
    "adc_circuits": {
        "required_fields": ["ref", "type"],
        "enum_fields": {
            "type": ["external_adc", "voltage_reference"],
        },
    },
    "reset_supervisors": {
        "required_fields": ["type"],
        "enum_fields": {
            "type": ["voltage_supervisor", "watchdog", "rc_reset"],
        },
    },
    "clock_distribution": {
        "required_fields": ["ref", "type"],
        "enum_fields": {
            "type": ["clock_generator", "pll", "oscillator_output"],
        },
    },
    # Batch 5
    "display_interfaces": {
        "required_fields": ["ref", "type"],
        "enum_fields": {
            "type": ["display", "touch_controller"],
        },
    },
    "sensor_interfaces": {
        "required_fields": ["ref", "type"],
        "enum_fields": {
            "type": ["motion", "environmental", "magnetic"],
        },
    },
    "level_shifters": {
        "required_fields": ["ref", "type"],
        "enum_fields": {
            "type": ["level_shifter_ic", "discrete_level_shifter"],
        },
    },
    # Batch 6
    "audio_circuits": {
        "required_fields": ["ref", "type"],
        "enum_fields": {
            "type": ["audio_amplifier", "audio_codec"],
        },
    },
    "led_driver_ics": {
        "required_fields": ["ref", "type"],
        "enum_fields": {
            "type": ["pwm_led_driver", "matrix_led_driver",
                     "constant_current_led_driver", "rgb_led_driver",
                     "led_driver"],
        },
    },
    "rtc_circuits": {
        "required_fields": ["ref", "type"],
        "enum_fields": {
            "type": ["rtc"],
        },
    },
    # Batch 7
    "led_audit": {
        "required_fields": ["ref", "type", "drive_method"],
        "enum_fields": {
            "type": ["indicator_led"],
            "drive_method": ["resistor_limited", "direct_drive", "ic_direct"],
        },
    },
    "thermocouple_rtd": {
        "required_fields": ["ref", "type"],
        "enum_fields": {
            "type": ["thermocouple_amplifier", "rtd_interface"],
        },
    },
}


def _field_spec_assertions(sig_type, detections, ast_num):
    """Generate field-spec assertions for domain detectors.

    Returns (assertions_list, next_ast_num).
    """
    spec = _DETECTOR_FIELD_SPECS.get(sig_type)
    if not spec:
        return [], ast_num

    assertions = []

    # Required fields: every item should have non-empty value
    # Skip fields that have enum constraints (the enum check validates them)
    enum_fields = set(spec.get("enum_fields", {}).keys())
    for field in spec.get("required_fields", []):
        if field in enum_fields:
            continue  # validated by enum assertion instead
        has_field = all(
            item.get(field) not in (None, "", [])
            for item in detections
            if isinstance(item, dict)
        )
        if has_field:
            assertions.append({
                "id": f"SEED-{ast_num:08d}",
                "description": f"All {sig_type} have {field}",
                "check": {
                    "path": f"signal_analysis.{sig_type}",
                    "op": "not_contains_match",
                    "field": field,
                    "pattern": r"^$",
                },
            })
            ast_num += 1

    # Enum fields: values must be in allowed set
    for field, allowed in spec.get("enum_fields", {}).items():
        pattern = "^(" + "|".join(allowed) + ")$"
        # Check if all items have valid values before asserting
        all_valid = all(
            item.get(field) in allowed
            for item in detections
            if isinstance(item, dict) and item.get(field) is not None
        )
        if all_valid and any(
            item.get(field) is not None
            for item in detections
            if isinstance(item, dict)
        ):
            assertions.append({
                "id": f"SEED-{ast_num:08d}",
                "description": f"All {sig_type} {field} values are valid",
                "check": {
                    "path": f"signal_analysis.{sig_type}",
                    "op": "count_matches",
                    "field": field,
                    "pattern": pattern,
                    "value": len(detections),
                },
            })
            ast_num += 1

    return assertions, ast_num


def _quality_assertions(sig_type, detections, ast_num):
    """Generate field-completeness assertions for a signal detector type.

    Returns (assertions_list, next_ast_num).
    """
    qc = _QUALITY_CHECKS.get(sig_type)
    if not qc:
        return [], ast_num

    field, desc, pattern = qc
    # Only assert the quality invariant if ALL detections actually satisfy it
    pat = re.compile(pattern)
    for det in detections:
        val = det
        for part in field.split("."):
            val = val.get(part, "") if isinstance(val, dict) else ""
        if pat.match(str(val)):
            return [], ast_num  # At least one violation — don't assert invariant
    assertions = [{
        "id": f"SEED-{ast_num:08d}",
        "description": f"All {sig_type} have {desc}",
        "check": {
            "path": f"signal_analysis.{sig_type}",
            "op": "not_contains_match",
            "field": field,
            "pattern": pattern,
        },
    }]
    return assertions, ast_num + 1


def _range_bounds(value, tolerance):
    """Compute [lo, hi] range with tolerance around a value.

    Scales tolerance inversely with count for tighter bounds on large values:
      count < 10:   ±2 absolute (minimum spread)
      count 10-50:  base tolerance (default 10%)
      count 50-200: tolerance * 0.5 (e.g., 5%)
      count > 200:  tolerance * 0.3 (e.g., 3%)
    """
    if value > 200:
        effective_tol = tolerance * 0.3
    elif value > 50:
        effective_tol = tolerance * 0.5
    else:
        effective_tol = tolerance
    lo = max(0, math.floor(value * (1 - effective_tol)))
    hi = math.ceil(value * (1 + effective_tol))
    # Ensure minimum spread of 2 for small values
    if hi - lo < 2:
        lo = max(0, value - 1)
        hi = value + 1
    return lo, hi


def generate_schematic_assertions(data, tolerance=0.10, include_empty=False):
    """Generate assertions from a schematic analyzer output dict."""
    stats = data.get("statistics", {})
    sa = data.get("signal_analysis", {})
    bom = data.get("bom", [])

    assertions = []
    ast_num = 1

    # Component count range
    total_comps = stats.get("total_components", 0)
    if total_comps > 0:
        lo, hi = _range_bounds(total_comps, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Component count ~{total_comps} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.total_components", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Net count range
    total_nets = stats.get("total_nets", 0)
    if total_nets > 0:
        lo, hi = _range_bounds(total_nets, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Net count ~{total_nets} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.total_nets", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # BOM exists
    if bom:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "BOM is non-empty",
            "check": {"path": "bom", "op": "min_count", "value": 1},
        })
        ast_num += 1

    # Signal analysis exists
    if sa:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "Signal analysis section exists",
            "check": {"path": "signal_analysis", "op": "exists"},
        })
        ast_num += 1

    # Assertions for each detected signal type with count > 0
    for sig_type, detections in sorted(sa.items()):
        if not isinstance(detections, list) or len(detections) == 0:
            continue
        count = len(detections)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{count} {sig_type} detected",
            "check": {"path": f"signal_analysis.{sig_type}",
                      "op": "min_count", "value": 1},
        })
        ast_num += 1

        # Field-completeness: critical fields must be non-zero/present
        qa, ast_num = _quality_assertions(sig_type, detections, ast_num)
        assertions.extend(qa)
        fsa, ast_num = _field_spec_assertions(sig_type, detections, ast_num)
        assertions.extend(fsa)

    # Empty-detector assertions: detectors with 0 items stay at 0
    # Only for schematics with enough components to be meaningful
    if include_empty and total_comps >= 50:
        for det in _load_known_detectors():
            det_items = sa.get(det, [])
            if isinstance(det_items, list) and len(det_items) == 0:
                assertions.append({
                    "id": f"SEED-{ast_num:08d}",
                    "description": f"No {det} expected",
                    "check": {"path": f"signal_analysis.{det}",
                              "op": "max_count", "value": 0},
                })
                ast_num += 1

    # Component types exist
    comp_types = stats.get("component_types", {})
    for ctype, count in sorted(comp_types.items()):
        if count >= 5:  # Only assert types with significant presence
            assertions.append({
                "id": f"SEED-{ast_num:08d}",
                "description": f"Has {count} {ctype}(s)",
                "check": {"path": f"statistics.component_types.{ctype}",
                          "op": "min_count", "value": max(1, int(count * 0.75))},
            })
            ast_num += 1

    return assertions


def generate_pcb_assertions(data, tolerance=0.10):
    """Generate assertions from a PCB analyzer output dict."""
    stats = data.get("statistics", {})
    conn = data.get("connectivity", {})
    dfm = data.get("dfm", {})

    assertions = []
    ast_num = 1

    # Footprint count range
    fp_count = stats.get("footprint_count", 0)
    if fp_count > 0:
        lo, hi = _range_bounds(fp_count, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Footprint count ~{fp_count} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.footprint_count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Net count range
    net_count = stats.get("net_count", 0)
    if net_count > 0:
        lo, hi = _range_bounds(net_count, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Net count ~{net_count} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.net_count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Copper layers used
    cu_layers = stats.get("copper_layers_used", 0)
    if cu_layers > 0:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{cu_layers} copper layer(s) used",
            "check": {"path": "statistics.copper_layers_used", "op": "equals",
                      "value": cu_layers},
        })
        ast_num += 1

    # Track segment count range
    track_segs = stats.get("track_segments", 0)
    if track_segs > 0:
        lo, hi = _range_bounds(track_segs, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Track segments ~{track_segs} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.track_segments", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Via count range
    via_count = stats.get("via_count", 0)
    if via_count > 0:
        lo, hi = _range_bounds(via_count, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Via count ~{via_count} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.via_count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Zone count
    zone_count = stats.get("zone_count", 0)
    if zone_count > 0:
        lo, hi = _range_bounds(zone_count, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Zone count ~{zone_count} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.zone_count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # SMD vs THT breakdown
    smd = stats.get("smd_count", 0)
    if smd > 0:
        lo, hi = _range_bounds(smd, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"SMD count ~{smd} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.smd_count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    tht = stats.get("tht_count", 0)
    if tht > 0:
        lo, hi = _range_bounds(tht, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"THT count ~{tht} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.tht_count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Routing completeness
    routing_complete = stats.get("routing_complete")
    if routing_complete is not None:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "Routing completeness status",
            "check": {"path": "statistics.routing_complete", "op": "equals",
                      "value": routing_complete},
        })
        ast_num += 1

    # Connectivity section exists
    if conn:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "Connectivity analysis present",
            "check": {"path": "connectivity", "op": "exists"},
        })
        ast_num += 1

    # DFM section exists
    if dfm:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "DFM analysis present",
            "check": {"path": "dfm", "op": "exists"},
        })
        ast_num += 1

        # DFM tier
        tier = dfm.get("dfm_tier", "")
        if tier:
            assertions.append({
                "id": f"SEED-{ast_num:08d}",
                "description": f"DFM tier is '{tier}'",
                "check": {"path": "dfm.dfm_tier", "op": "equals", "value": tier},
            })
            ast_num += 1

    # Decoupling placement (if present)
    decoupling = data.get("decoupling_placement", [])
    if decoupling:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{len(decoupling)} decoupling placement(s) analyzed",
            "check": {"path": "decoupling_placement", "op": "min_count", "value": 1},
        })
        ast_num += 1

    # Power net routing (if present)
    power_routing = data.get("power_net_routing", [])
    if power_routing:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{len(power_routing)} power net(s) analyzed",
            "check": {"path": "power_net_routing", "op": "min_count", "value": 1},
        })
        ast_num += 1

    # Thermal analysis (if present)
    thermal = data.get("thermal_analysis", {})
    if thermal:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "Thermal analysis present",
            "check": {"path": "thermal_analysis", "op": "exists"},
        })
        ast_num += 1

    # Placement analysis (if present)
    placement = data.get("placement_analysis", {})
    if placement:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "Placement analysis present",
            "check": {"path": "placement_analysis", "op": "exists"},
        })
        ast_num += 1

    return assertions


def generate_gerber_assertions(data, tolerance=0.10):
    """Generate assertions from a gerber analyzer output dict."""
    stats = data.get("statistics", {})
    comp = data.get("completeness", {})
    alignment = data.get("alignment", {})
    drill_class = data.get("drill_classification", {})

    assertions = []
    ast_num = 1

    # Layer count
    layer_count = data.get("layer_count", 0)
    if layer_count > 0:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{layer_count} copper layer(s)",
            "check": {"path": "layer_count", "op": "equals", "value": layer_count},
        })
        ast_num += 1

    # Gerber file count range
    gerber_files = stats.get("gerber_files", 0)
    if gerber_files > 0:
        lo, hi = _range_bounds(gerber_files, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Gerber file count ~{gerber_files} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.gerber_files", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Drill file count
    drill_files = stats.get("drill_files", 0)
    if drill_files > 0:
        lo, hi = _range_bounds(drill_files, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Drill file count ~{drill_files} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.drill_files", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Total holes range
    total_holes = stats.get("total_holes", 0)
    if total_holes > 0:
        lo, hi = _range_bounds(total_holes, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Total holes ~{total_holes} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.total_holes", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Total flashes range
    total_flashes = stats.get("total_flashes", 0)
    if total_flashes > 0:
        lo, hi = _range_bounds(total_flashes, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Total flashes ~{total_flashes} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.total_flashes", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Completeness
    complete = comp.get("complete")
    if complete is not None:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Completeness is {complete}",
            "check": {"path": "completeness.complete", "op": "equals",
                      "value": complete},
        })
        ast_num += 1

    # Found layers count
    found_layers = comp.get("found_layers", [])
    if found_layers:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{len(found_layers)} layer(s) found",
            "check": {"path": "completeness.found_layers", "op": "min_count",
                      "value": len(found_layers)},
        })
        ast_num += 1

    # Alignment
    aligned = alignment.get("aligned")
    if aligned is not None:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Alignment is {aligned}",
            "check": {"path": "alignment.aligned", "op": "equals",
                      "value": aligned},
        })
        ast_num += 1

    # Drill classification - vias
    via_count = drill_class.get("vias", {}).get("count", 0)
    if via_count > 0:
        lo, hi = _range_bounds(via_count, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Via holes ~{via_count} (tolerance {tolerance:.0%})",
            "check": {"path": "drill_classification.vias.count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Drill classification - component holes
    comp_holes = drill_class.get("component_holes", {}).get("count", 0)
    if comp_holes > 0:
        lo, hi = _range_bounds(comp_holes, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Component holes ~{comp_holes} (tolerance {tolerance:.0%})",
            "check": {"path": "drill_classification.component_holes.count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Drill classification - mounting holes
    mount_holes = drill_class.get("mounting_holes", {}).get("count", 0)
    if mount_holes > 0:
        lo, hi = _range_bounds(mount_holes, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Mounting holes ~{mount_holes} (tolerance {tolerance:.0%})",
            "check": {"path": "drill_classification.mounting_holes.count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    return assertions


def generate_datasheets_assertions(data, tolerance=0.10):
    """Generate assertions from a datasheets validation report."""
    parts = data.get("parts", {})
    assertions = []
    ast_num = 1

    extracted = data.get("extracted", 0)
    if extracted == 0:
        return assertions

    # Extraction count
    lo, hi = _range_bounds(extracted, tolerance)
    assertions.append({
        "id": f"SEED-{ast_num:08d}",
        "description": f"Extraction count ~{extracted} (tolerance {tolerance:.0%})",
        "check": {"path": "extracted", "op": "range", "min": lo, "max": hi},
    })
    ast_num += 1

    # Sufficient count (score >= 6.0)
    sufficient = data.get("sufficient", 0)
    if sufficient > 0:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"At least {sufficient} sufficient extraction(s)",
            "check": {"path": "sufficient", "op": "min_count", "value": sufficient},
        })
        ast_num += 1

    # Per-category counts
    for cat, count in sorted(data.get("by_category", {}).items()):
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{count} {cat} extraction(s)",
            "check": {"path": f"by_category.{cat}", "op": "equals", "value": count},
        })
        ast_num += 1

    return assertions


def generate_emc_assertions(data, tolerance=0.10):
    """Generate assertions from an EMC analysis output dict."""
    summary = data.get("summary", {})
    findings = data.get("findings", [])

    assertions = []
    ast_num = 1

    total = summary.get("total_findings", summary.get("total_checks", 0))
    if total == 0:
        return assertions

    # Total findings count range — use total_findings (KH-246 rename)
    total_key = "summary.total_findings" if "total_findings" in summary else "summary.total_checks"
    lo, hi = _range_bounds(total, tolerance)
    assertions.append({
        "id": f"SEED-{ast_num:08d}",
        "description": f"Finding count ~{total} (tolerance {tolerance:.0%})",
        "check": {"path": total_key, "op": "range",
                  "min": lo, "max": hi},
    })
    ast_num += 1

    # Per-severity counts (range for non-zero)
    for sev in ("critical", "high", "medium", "low"):
        count = summary.get(sev, 0)
        if count > 0:
            lo, hi = _range_bounds(count, tolerance)
            assertions.append({
                "id": f"SEED-{ast_num:08d}",
                "description": f"{sev} count ~{count}",
                "check": {"path": f"summary.{sev}", "op": "range",
                          "min": lo, "max": hi},
            })
            ast_num += 1

    # EMC risk score range
    score = summary.get("emc_risk_score", 0)
    slo = max(0, score - 10)
    shi = min(100, score + 10)
    assertions.append({
        "id": f"SEED-{ast_num:08d}",
        "description": f"EMC risk score ~{score} (+-10)",
        "check": {"path": "summary.emc_risk_score", "op": "range",
                  "min": slo, "max": shi},
    })
    ast_num += 1

    # Per-category counts
    by_category = {}
    for f in findings:
        cat = f.get("category", "other")
        by_category[cat] = by_category.get(cat, 0) + 1

    for cat, count in sorted(by_category.items()):
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{count} {cat} finding(s)",
            "check": {"path": "findings",
                      "op": "count_matches",
                      "field": "category",
                      "pattern": f"^{cat}$",
                      "value": count},
        })
        ast_num += 1

    # Target standard
    standard = data.get("target_standard", "")
    if standard:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Target standard is {standard}",
            "check": {"path": "target_standard", "op": "equals",
                      "value": standard},
        })
        ast_num += 1

    # Test plan section (Phase 2+)
    test_plan = data.get("test_plan", {})
    if test_plan:
        fb_count = len(test_plan.get("frequency_bands", []))
        if fb_count > 0:
            assertions.append({
                "id": f"SEED-{ast_num:08d}",
                "description": f"{fb_count} frequency band(s) in test plan",
                "check": {"path": "test_plan.frequency_bands",
                          "op": "min_count", "value": fb_count},
            })
            ast_num += 1

        pp_count = len(test_plan.get("probe_points", []))
        if pp_count > 0:
            lo, hi = _range_bounds(pp_count, tolerance)
            assertions.append({
                "id": f"SEED-{ast_num:08d}",
                "description": f"~{pp_count} probe point(s) in test plan",
                "check": {"path": "test_plan.probe_points",
                          "op": "min_count", "value": max(1, lo)},
            })
            ast_num += 1

    # Regulatory coverage section (Phase 2+)
    reg = data.get("regulatory_coverage", {})
    if reg:
        market = reg.get("market", "")
        if market:
            assertions.append({
                "id": f"SEED-{ast_num:08d}",
                "description": f"Regulatory market is {market}",
                "check": {"path": "regulatory_coverage.market",
                          "op": "equals", "value": market},
            })
            ast_num += 1

        std_count = len(reg.get("applicable_standards", []))
        if std_count > 0:
            assertions.append({
                "id": f"SEED-{ast_num:08d}",
                "description": f"{std_count} applicable standard(s)",
                "check": {"path": "regulatory_coverage.applicable_standards",
                          "op": "min_count", "value": std_count},
            })
            ast_num += 1

    # Per-net scores (Final Features)
    per_net = data.get("per_net_scores", [])
    if per_net:
        lo, hi = _range_bounds(len(per_net), tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"~{len(per_net)} net(s) with EMC scores",
            "check": {"path": "per_net_scores",
                      "op": "min_count", "value": max(1, lo)},
        })
        ast_num += 1

    return assertions


def generate_thermal_assertions(data, tolerance=0.10):
    """Generate assertions from a thermal analysis output dict."""
    summary = data.get("summary", {})

    assertions = []
    ast_num = 1

    total = summary.get("total_findings", summary.get("total_checks", 0))
    components_analyzed = summary.get("components_analyzed", 0)
    if total == 0 and components_analyzed == 0:
        return assertions

    # Total findings count range — use total_findings (with total_checks fallback)
    total_key = "summary.total_findings" if "total_findings" in summary else "summary.total_checks"
    if total > 0:
        lo, hi = _range_bounds(total, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Finding count ~{total} (tolerance {tolerance:.0%})",
            "check": {"path": total_key, "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Per-severity counts (range for non-zero)
    for sev in ("critical", "high", "medium", "low"):
        count = summary.get(sev, 0)
        if count > 0:
            lo, hi = _range_bounds(count, tolerance)
            assertions.append({
                "id": f"SEED-{ast_num:08d}",
                "description": f"{sev} count ~{count}",
                "check": {"path": f"summary.{sev}", "op": "range",
                          "min": lo, "max": hi},
            })
            ast_num += 1

    # Components analyzed count range
    if components_analyzed > 0:
        lo, hi = _range_bounds(components_analyzed, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Components analyzed ~{components_analyzed} (tolerance {tolerance:.0%})",
            "check": {"path": "summary.components_analyzed", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Thermal score range (0-100)
    score = summary.get("thermal_score", 0)
    if score > 0:
        slo = max(0, score - 10)
        shi = min(100, score + 10)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Thermal score ~{score} (+-10)",
            "check": {"path": "summary.thermal_score", "op": "range",
                      "min": slo, "max": shi},
        })
        ast_num += 1

    return assertions


def generate_spice_assertions(data, tolerance=0.10):
    """Generate assertions from a SPICE simulation output dict."""
    summary = data.get("summary", {})
    results = data.get("simulation_results", [])

    assertions = []
    ast_num = 1

    total = summary.get("total", 0)
    if total == 0:
        return assertions

    # Total simulation count range
    lo, hi = _range_bounds(total, tolerance)
    assertions.append({
        "id": f"SEED-{ast_num:08d}",
        "description": f"Simulation count ~{total} (tolerance {tolerance:.0%})",
        "check": {"path": "summary.total", "op": "range",
                  "min": lo, "max": hi},
    })
    ast_num += 1

    # Pass count (minimum — at least 80% of current)
    pass_count = summary.get("pass", 0)
    if pass_count > 0:
        min_pass = max(1, int(pass_count * 0.8))
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"At least {min_pass} passing simulation(s)",
            "check": {"path": "summary.pass", "op": "min_count",
                      "value": min_pass},
        })
        ast_num += 1

    # Per subcircuit type count
    by_type = {}
    for r in results:
        t = r.get("subcircuit_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    for stype, count in sorted(by_type.items()):
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{count} {stype} simulation(s)",
            "check": {"path": "simulation_results",
                      "op": "count_matches",
                      "field": "subcircuit_type",
                      "pattern": f"^{stype}$",
                      "value": count},
        })
        ast_num += 1

    return assertions


def _meets_seeding_threshold(data, atype, min_components=10):
    """Check if output data meets the minimum threshold for seeding."""
    if atype == "schematic":
        return data.get("statistics", {}).get("total_components", 0) >= min_components
    elif atype == "pcb":
        return data.get("statistics", {}).get("footprint_count", 0) >= min_components
    elif atype == "gerber":
        return data.get("statistics", {}).get("gerber_files", 0) >= 2
    elif atype == "spice":
        return data.get("summary", {}).get("total", 0) >= 1
    elif atype == "emc":
        s = data.get("summary", {})
        return s.get("total_findings", s.get("total_checks", 0)) >= 1
    elif atype == "datasheets":
        return data.get("extracted", 0) >= 1
    elif atype == "thermal":
        s = data.get("summary", {})
        return s.get("total_findings", s.get("total_checks", 0)) >= 1 or s.get("components_analyzed", 0) >= 1
    return False


def prune_stale_assertions(repo_name, atype, min_components, dry_run=True):
    """Remove seed assertion files whose outputs no longer meet thresholds.

    Returns (pruned_count, checked_count).
    """
    from run_checks import find_output_file

    repo_dir = DATA_DIR / repo_name
    if not repo_dir.exists():
        return 0, 0

    pruned = checked = 0
    for proj_dir in sorted(repo_dir.iterdir()):
        if not proj_dir.is_dir():
            continue
        type_dir = proj_dir / "assertions" / atype
        if not type_dir.exists():
            continue

        # Resolve project_path for output file lookup
        from checks import load_project_metadata
        pp = load_project_metadata(repo_name, proj_dir.name).get("project_path")
        if pp is None:
            try:
                for p in discover_projects(repo_name):
                    if p["name"] == proj_dir.name:
                        pp = p["path"]
                        break
            except (ImportError, OSError):
                pass

        for af in sorted(type_dir.glob("*.json")):
            # Only prune SEED assertions
            try:
                adata = json.loads(af.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if adata.get("generated_by") != "seed.py":
                continue

            checked += 1
            file_pattern = adata.get("file_pattern", "")
            out = find_output_file(file_pattern, repo_name, pp, atype)

            should_prune = False
            reason = ""
            if out is None:
                should_prune = True
                reason = "output missing"
            else:
                try:
                    odata = json.loads(out.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    should_prune = True
                    reason = "output unreadable"
                else:
                    if not _meets_seeding_threshold(odata, atype, min_components):
                        should_prune = True
                        reason = "below threshold"

            if should_prune:
                if dry_run:
                    print(f"  [PRUNE] {repo_name}/{proj_dir.name}/{atype}/{af.name} "
                          f"({reason})")
                else:
                    af.unlink()
                    print(f"  Pruned {repo_name}/{proj_dir.name}/{atype}/{af.name} "
                          f"({reason})")
                pruned += 1

    return pruned, checked


def generate_for_repo(repo_name, atype, tolerance, min_components,
                      file_filter, dry_run, include_empty=False,
                      resume=False):
    """Generate seed assertions for one repo."""
    type_dir = OUTPUTS_DIR / atype / repo_name
    if not type_dir.exists():
        return 0, 0, 0

    projects = discover_projects(repo_name)
    if not projects:
        return 0, 0, 0

    # --resume: skip if all projects already have assertion files for this type
    if resume and not dry_run:
        all_have_assertions = True
        for proj in projects:
            assertion_dir = data_dir(repo_name, proj["name"], "assertions") / atype
            if not assertion_dir.exists() or not any(assertion_dir.glob("*.json")):
                all_have_assertions = False
                break
        if all_have_assertions:
            return 0, 0, 0

    total_files = 0
    total_assertions = 0
    skipped = 0

    for proj in projects:
        proj_name = proj["name"]
        proj_path = proj["path"]
        prefix = project_prefix(proj_path)

        # Find output files for this project (filter_project_outputs
        # only matches *.json which excludes .err files)
        proj_outputs = filter_project_outputs(type_dir, proj_path)

        if file_filter:
            patterns = [p.strip() for p in file_filter.split(",")]
            proj_outputs = [f for f in proj_outputs
                            if any(fnmatch.fnmatch(f.name, p) or
                                   fnmatch.fnmatch(f.name[len(prefix):], p)
                                   for p in patterns)]

        for output_file in proj_outputs:
            try:
                data_content = json.loads(output_file.read_text(encoding="utf-8"))
            except Exception:
                continue

            if not _meets_seeding_threshold(data_content, atype, min_components):
                skipped += 1
                continue

            if atype == "schematic":
                assertions = generate_schematic_assertions(
                    data_content, tolerance, include_empty=include_empty)
            elif atype == "pcb":
                assertions = generate_pcb_assertions(data_content, tolerance)
            elif atype == "gerber":
                assertions = generate_gerber_assertions(data_content, tolerance)
            elif atype == "spice":
                assertions = generate_spice_assertions(data_content, tolerance)
            elif atype == "emc":
                assertions = generate_emc_assertions(data_content, tolerance)
            elif atype == "thermal":
                assertions = generate_thermal_assertions(data_content, tolerance)
            elif atype == "datasheets":
                assertions = generate_datasheets_assertions(data_content, tolerance)
            else:
                continue

            if not assertions:
                continue

            # file_pattern is the filename within the project (prefix stripped)
            if prefix:
                file_pattern = output_file.stem[len(prefix):]
            else:
                file_pattern = output_file.stem

            assertion_data = {
                "file_pattern": file_pattern,
                "analyzer_type": atype,
                "generated_by": "seed.py",
                "evidence_source": "auto_seeded",
                "assertions": assertions,
            }

            if dry_run:
                print(f"\n  {repo_name}/{proj_name}: {file_pattern}")
                for a in assertions:
                    print(f"    {a['id']}: {a['description']}")
                total_files += 1
                total_assertions += len(assertions)
                continue

            # Write to data/{repo}/{project}/assertions/{type}/
            out_dir = data_dir(repo_name, proj_name, "assertions") / atype
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"{file_pattern}.json"

            if out_file.exists():
                existing = json.loads(out_file.read_text(encoding="utf-8"))
                if existing.get("generated_by") != "seed.py":
                    continue

            out_file.write_text(json.dumps(assertion_data, indent=2) + "\n", encoding="utf-8")
            total_files += 1
            total_assertions += len(assertions)

    return total_files, total_assertions, skipped


def _seed_one_repo(repo, atype, tolerance, min_components, file_filter,
                   dry_run, include_empty, resume=False):
    """Worker function for parallel seed generation. Must be top-level for pickling."""
    return generate_for_repo(repo, atype, tolerance, min_components,
                             file_filter, dry_run, include_empty=include_empty,
                             resume=resume)


def _prune_one_repo(repo, atype, min_components, dry_run):
    """Worker function for parallel prune. Must be top-level for pickling."""
    return prune_stale_assertions(repo, atype, min_components, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser(description="Generate seed assertions from outputs")
    group = add_repo_filter_args(parser)
    parser.add_argument("--all", action="store_true", help="Generate for all repos")
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Number of parallel workers (default: {DEFAULT_JOBS})")
    parser.add_argument("--type", choices=ANALYZER_TYPES,
                        default="schematic", help="Analyzer type (default: schematic)")
    parser.add_argument("--filter", default="",
                        help="Glob pattern to filter output filenames")
    parser.add_argument("--tolerance", type=float, default=0.10,
                        help="Tolerance for range assertions (default: 0.10 = 10%%)")
    parser.add_argument("--min-components", type=int, default=10,
                        help="Skip files with fewer components (default: 10)")
    parser.add_argument("--include-empty", action="store_true",
                        help="Add max_count=0 assertions for absent detectors "
                             "(schematics with 50+ components)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print assertions without writing files")
    parser.add_argument("--prune-stale", action="store_true",
                        help="Remove seed assertions whose outputs no longer meet thresholds")
    parser.add_argument("--resume", action="store_true",
                        help="Skip repos that already have assertion files")
    args = parser.parse_args()

    repos = resolve_repos(args)
    if repos is None:
        if args.all:
            repos = list_repos()
        else:
            parser.print_help()
            sys.exit(1)

    jobs = args.jobs

    if args.prune_stale:
        grand_pruned = grand_checked = 0
        if jobs > 1 and len(repos) > 1:
            with ProcessPoolExecutor(max_workers=min(jobs, len(repos))) as pool:
                futures = {pool.submit(_prune_one_repo, repo, args.type,
                                       args.min_components, args.dry_run): repo
                           for repo in repos}
                for future in as_completed(futures):
                    pruned, checked = future.result()
                    grand_pruned += pruned
                    grand_checked += checked
        else:
            for repo in repos:
                pruned, checked = prune_stale_assertions(
                    repo, args.type, args.min_components,
                    dry_run=args.dry_run)
                grand_pruned += pruned
                grand_checked += checked
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}"
              f"Pruned {grand_pruned} stale seed assertions "
              f"(checked {grand_checked})")
        sys.exit(0)

    grand_files = grand_assertions = grand_skipped = 0
    include_empty = getattr(args, "include_empty", False)

    resume = getattr(args, "resume", False)
    if jobs > 1 and len(repos) > 1:
        with ProcessPoolExecutor(max_workers=min(jobs, len(repos))) as pool:
            futures = {pool.submit(_seed_one_repo, repo, args.type,
                                   args.tolerance, args.min_components,
                                   args.filter, args.dry_run,
                                   include_empty, resume): repo
                       for repo in repos}
            for future in as_completed(futures):
                files, assertions, skipped = future.result()
                grand_files += files
                grand_assertions += assertions
                grand_skipped += skipped
    else:
        for repo in repos:
            files, assertions, skipped = generate_for_repo(
                repo, args.type, args.tolerance, args.min_components,
                args.filter, args.dry_run,
                include_empty=include_empty, resume=resume)
            grand_files += files
            grand_assertions += assertions
            grand_skipped += skipped

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Generated {grand_assertions} assertions "
          f"across {grand_files} files (skipped {grand_skipped} small files)")


if __name__ == "__main__":
    main()
