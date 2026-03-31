# Constants Registry

*Auto-generated from `constants_registry.json` — do not edit manually.*

**Last scan:** 2026-03-31T03:16:12.788377+00:00

## Summary

| Metric | Count |
|--------|-------|
| Total constants | 212 |
| Verified | 0 |
| Unverified | 212 |
| Stale (changed since verification) | 0 |
| Critical risk | 7 |
| High risk | 8 |

## analyze_gerbers.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-210 | `_POWER_KEYWORDS_GERBER` | standard | 12 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-099 | `patterns` | keyword_classification | 22 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-100 | `ext_map` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-103 | `_GERBER_EXTENSIONS` | standard | 17 | unverified | 0.1 | 0.0 | **low** (0.1) |

## analyze_pcb.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-079 | `_float_keys` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-080 | `pad_info` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-081 | `fp_entry` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-101 | `seg_info` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-102 | `arc_info` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-082 | `via_info` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-083 | `zone_info` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-084 | `bbox` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-211 | `_ESD_TVS_PREFIXES` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-212 | `analyze_ground_domains:1252` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-086 | `type_counts` | standard | 3 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-087 | `type_sizes` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-088 | `annular_ring` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-213 | `analyze_vias:1825` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-090 | `current_facts` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-214 | `rev_pattern` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-215 | `extract_silkscreen:2159` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-216 | `extract_silkscreen:2161` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-217 | `extract_silkscreen:2169` | keyword_classification | 11 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-095 | `LIMITS_STD` | standard | 7 | unverified | 0.1 | 0.3 | **low** (0.3) |
| CONST-096 | `LIMITS_ADV` | standard | 4 | unverified | 0.1 | 0.2 | **low** (0.2) |
| CONST-097 | `risk_order` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-098 | `adequacy_order` | heuristic_threshold | 4 | unverified | 0.4 | 0.1 | **medium** (0.4) |

## analyze_schematic.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-005 | `_MPN_KEYS` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-010 | `_MANUFACTURER_KEYS` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-012 | `_DIGIKEY_KEYS` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-013 | `_MOUSER_KEYS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-016 | `_LCSC_KEYS` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-017 | `_ELEMENT14_KEYS` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-001 | `_WIRE_GRID_SIZE` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-002 | `_LIB_PREFIX_MAP` | keyword_classification | 58 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-003 | `target_types` | keyword_classification | 4 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-004 | `pin_entry` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-018 | `analyze_ic_pinouts:1522` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-006 | `ic_result` | keyword_classification | 14 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-007 | `_LEGACY_PIN_TYPE_MAP` | standard | 11 | unverified | 0.6 | 0.0 | **high** (0.6) |
| CONST-008 | `_M` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-009 | `_STANDARD_LIB_PINS` | keyword_classification | 34 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-019 | `sym_def` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-011 | `_MAX_SNAP_DIST` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-020 | `_parse_legacy_single_sheet:2247` | standard | 3 | unverified | 0.1 | 0.2 | **low** (0.2) |
| CONST-014 | `ps` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-015 | `output_types` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-021 | `analyze_design_rules:2772` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-022 | `analyze_design_rules:2774` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-023 | `analyze_design_rules:2776` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-033 | `analyze_design_rules:2778` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-035 | `analyze_design_rules:2780` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-039 | `analyze_design_rules:2782` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-047 | `analyze_design_rules:2784` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-048 | `analyze_design_rules:2788` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-049 | `analyze_design_rules:2792` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-024 | `_io_pin_names` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-025 | `_sense_pin_names` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-026 | `_pwr_pin_to_rail` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-027 | `level_translator_keywords` | keyword_classification | 20 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-028 | `level_translator_desc_keywords` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-029 | `buses` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-030 | `_spi_net_kw` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-031 | `_spi_canon` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-032 | `_uart_exclude` | keyword_classification | 23 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-050 | `analyze_design_rules:3163` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-034 | `_sdio_prefixes` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-053 | `analyze_design_rules:3188` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-036 | `can_keywords` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-037 | `can_transceiver_kw` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-038 | `_rs485_kw` | keyword_classification | 28 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-060 | `analyze_design_rules:3342` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-040 | `outputs` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-041 | `drivers` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-042 | `drivers` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-043 | `_STANDARD_FP_LIBS` | keyword_classification | 35 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-044 | `_GENERIC_TRANSISTOR_PREFIXES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-045 | `_GENERIC_TYPE_LABELS` | standard | 4 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-046 | `_PIN_LETTER_NAMES` | standard | 6 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-061 | `classify_ground_domains:4022` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-071 | `classify_ground_domains:4024` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-072 | `classify_ground_domains:4026` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-074 | `classify_ground_domains:4028` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-051 | `esl_by_pkg` | datasheet_lookup | 8 | unverified | 0.8 | 0.0 | **critical** (0.8) |
| CONST-052 | `esr_base_by_pkg` | datasheet_lookup | 8 | unverified | 0.8 | 0.0 | **critical** (0.8) |
| CONST-085 | `_is_electrolytic_or_tantalum:4551` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-054 | `cap_entry` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-055 | `rail_result` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-056 | `_iq_estimates_uA` | datasheet_lookup | 16 | unverified | 0.9 | 0.0 | **critical** (0.9) |
| CONST-057 | `ic_current_estimates` | datasheet_lookup | 48 | unverified | 1.0 | 0.0 | **critical** (1.0) |
| CONST-058 | `rail_info` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-059 | `dep_entry` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-089 | `analyze_power_sequencing:5266` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-091 | `analyze_power_sequencing:5268` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-062 | `pg_entry` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-063 | `debug_keywords` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-064 | `key_net_patterns` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-065 | `easy_smd` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-066 | `hard_ic_patterns` | keyword_classification | 4 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-067 | `medium_hard_ic_patterns` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-068 | `medium_ic_patterns` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-069 | `easy_ic_patterns` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-070 | `difficulty_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-092 | `_extract_package_info:5631` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-093 | `analyze_usb_compliance:5760` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-073 | `conn_checks` | heuristic_threshold | 4 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-094 | `analyze_usb_compliance:5868` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-075 | `esd_keywords` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-076 | `all_checks` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-077 | `rail_entry` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-078 | `merged_bus` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## kicad_utils.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-104 | `COORD_EPSILON` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-105 | `_MIL_MM` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-106 | `_REGULATOR_VREF` | datasheet_lookup | 96 | unverified | 1.0 | 0.0 | **critical** (1.0) |
| CONST-107 | `_LOAD_TYPE_KEYWORDS` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-108 | `multipliers` | standard | 11 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-109 | `type_map` | standard | 65 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-218 | `classify_component:355` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-219 | `classify_component:372` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-220 | `classify_component:377` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-221 | `classify_component:380` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-222 | `classify_component:382` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-223 | `classify_component:386` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-224 | `classify_component:389` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-225 | `classify_component:399` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-226 | `classify_component:412` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-227 | `classify_component:415` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-119 | `classify_component:435` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-228 | `classify_component:444` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-120 | `classify_component:448` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-229 | `classify_component:452` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-230 | `classify_component:488` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-231 | `classify_component:490` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-232 | `classify_component:494` | keyword_classification | 22 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-233 | `classify_component:508` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-234 | `classify_component:510` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-121 | `_ic_lib_prefixes` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-235 | `classify_component:556` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-236 | `classify_component:575` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |

## signal_detectors.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-124 | `divider` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-125 | `rc_entry` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-126 | `lc_entry` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-237 | `detect_crystal_circuits:697` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-127 | `xtal_entry` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-128 | `_osc_keywords` | keyword_classification | 15 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-129 | `_osc_exclude` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-130 | `_xtal_pin_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-131 | `_SENSE_PIN_PREFIXES` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-132 | `_SENSE_IC_KEYWORDS` | keyword_classification | 31 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-238 | `_SENSE_IC_EXCLUDE` | keyword_classification | 30 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-133 | `_integrated_csa_pins` | keyword_classification | 20 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-134 | `_non_reg_exclude` | keyword_classification | 25 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-239 | `_kw_pmic` | keyword_classification | 18 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-135 | `reg_lib_keywords` | keyword_classification | 52 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-240 | `detect_power_regulators:1288` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-137 | `_rf_exclude` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-138 | `_power_mux_exclude` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-139 | `reg_info` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-140 | `_switching_kw` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-141 | `inverting_kw` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-241 | `detect_power_regulators:1504` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-143 | `_ldo_pin_names` | keyword_classification | 14 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-242 | `_non_reg_ic_keywords` | keyword_classification | 22 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-144 | `protection_types` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-145 | `tvs_keywords` | keyword_classification | 15 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-146 | `esd_ic_keywords` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-147 | `opamp_lib_keywords` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-148 | `opamp_value_keywords` | keyword_classification | 27 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-243 | `detect_opamp_circuits:1773` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-244 | `detect_transistor_circuits:2140` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-245 | `detect_transistor_circuits:2145` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-246 | `snubber_data` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-152 | `source_sense` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-247 | `_jfet_kw` | keyword_classification | 20 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-248 | `postfilter_vd_and_dedup:2397` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-154 | `iso_keywords` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-249 | `detect_isolation_barriers:2705` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-156 | `eth_phy_keywords` | keyword_classification | 21 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-157 | `magnetics_keywords` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-250 | `detect_ethernet_interfaces:2756` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-159 | `_eth_tx_rx_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-160 | `_eth_net_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-161 | `_bridge_kw` | keyword_classification | 22 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-162 | `_hdmi_conn_kw` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-163 | `memory_keywords` | keyword_classification | 30 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-164 | `processor_keywords` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-251 | `RF_IC_BANDS` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-252 | `RF_ROLE_GAIN_DB` | datasheet_lookup | 10 | unverified | 0.7 | 0.1 | **critical** (0.7) |
| CONST-165 | `rf_switch_keywords` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-166 | `rf_mixer_keywords` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-167 | `rf_amp_keywords` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-168 | `rf_transceiver_keywords` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-169 | `rf_filter_keywords` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-253 | `rf_attenuator_keywords` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-254 | `rf_coupler_keywords` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-255 | `rf_power_detector_keywords` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-256 | `rf_freq_multiplier_keywords` | standard | 3 | unverified | 0.1 | 0.1 | **low** (0.1) |
| CONST-257 | `detect_rf_chains:3145` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-171 | `_ant_keywords` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-172 | `_ant_lib_keywords` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-258 | `detect_rf_matching:3360` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-259 | `_rf_keywords` | keyword_classification | 29 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-173 | `bms_ic_keywords` | keyword_classification | 15 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-260 | `detect_bms_systems:3537` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-174 | `power_path_keywords` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-261 | `detect_design_observations:3713` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-175 | `obs` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-262 | `detect_design_observations:3834` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-177 | `addr_keywords` | keyword_classification | 13 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-263 | `_get_protocol:3914` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-179 | `din_names` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-180 | `dout_names` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |

