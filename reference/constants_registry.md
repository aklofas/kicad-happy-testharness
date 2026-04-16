# Constants Registry

*Auto-generated from `constants_registry.json` — do not edit manually.*

**Last scan:** 2026-04-16T19:43:14.426459+00:00

## Summary

| Metric | Count |
|--------|-------|
| Total constants | 355 |
| Verified | 197 |
| Unverified | 158 |
| Stale (changed since verification) | 0 |
| Critical risk | 0 |
| High risk | 0 |

## analyze_emc.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-176 | `SEVERITY_WEIGHTS` | datasheet_lookup | 5 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-463 | `CONFIDENCE_WEIGHTS` | datasheet_lookup | 3 | verified | 0.7 | 0.2 | **low** (0.2) |
| CONST-178 | `MAX_FINDINGS_PER_RULE` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-181 | `sev_order` | heuristic_threshold | 5 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-281 | `cat_labels` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-388 | `schema` | keyword_classification | 13 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-389 | `config` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-282 | `counts` | heuristic_threshold | 5 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-390 | `active_counts` | heuristic_threshold | 5 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-395 | `_sev_order` | heuristic_threshold | 5 | unverified | 0.4 | 0.0 | **medium** (0.4) |

## analyze_gerbers.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-210 | `_POWER_KEYWORDS_GERBER` | standard | 12 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-099 | `patterns` | keyword_classification | 22 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-100 | `ext_map` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-103 | `_GERBER_EXTENSIONS` | standard | 17 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-347 | `required_layers` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |

## analyze_pcb.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-322 | `_NUMERIC_STACKUP_KEYS` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-079 | `_float_keys` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-080 | `pad_info` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-081 | `fp_entry` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-101 | `seg_info` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-102 | `arc_info` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-082 | `via_info` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-083 | `zone_info` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-084 | `bbox` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-211 | `_ESD_TVS_PREFIXES` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-213 | `SNAP` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-215 | `SAMPLE_INTERVAL` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-089 | `seg_entry` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-310 | `analyze_ground_domains:2211` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-086 | `type_counts` | standard | 4 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-087 | `type_sizes` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-088 | `annular_ring` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-311 | `analyze_vias:2882` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-090 | `current_facts` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-214 | `rev_pattern` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-312 | `extract_silkscreen:3216` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-313 | `extract_silkscreen:3218` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-314 | `extract_silkscreen:3226` | keyword_classification | 11 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-195 | `_fab_notes_checklist` | heuristic_threshold | 6 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-315 | `extract_silkscreen:3296` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-316 | `extract_silkscreen:3299` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-317 | `extract_silkscreen:3301` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-318 | `extract_silkscreen:3303` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-221 | `_silk_checks` | heuristic_threshold | 5 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-320 | `_RF_MODULE_KEYWORDS` | keyword_classification | 20 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-321 | `_RF_LIB_KEYWORDS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-095 | `LIMITS_STD` | standard | 7 | verified | 0.1 | 0.3 | **low** (0.3) |
| CONST-096 | `LIMITS_ADV` | standard | 4 | verified | 0.1 | 0.2 | **low** (0.2) |
| CONST-266 | `IPC_CLASS_LIMITS` | standard | 3 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-298 | `constraints` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-299 | `checks` | unknown | 3 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-097 | `risk_order` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-098 | `adequacy_order` | heuristic_threshold | 4 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-300 | `_gnd_keywords` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-343 | `analyze_fiducials:5458` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-344 | `finding` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-345 | `_FINDING_LIST_KEYS` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-346 | `sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-302 | `config` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## analyze_schematic.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-078 | `_UUID_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-005 | `_MPN_KEYS` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-010 | `_MANUFACTURER_KEYS` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-012 | `_DIGIKEY_KEYS` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-013 | `_MOUSER_KEYS` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-016 | `_LCSC_KEYS` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-017 | `_ELEMENT14_KEYS` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-001 | `_WIRE_GRID_SIZE` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-002 | `_NET_NAME_PRIORITY` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-158 | `_IC_LIB_PREFIX_MAP` | keyword_classification | 58 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-170 | `_IC_VALUE_KEYWORDS` | unknown | 45 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-186 | `_IC_DESC_KEYWORDS` | unknown | 44 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-003 | `target_types` | keyword_classification | 4 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-004 | `pin_entry` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-018 | `analyze_ic_pinouts:2036` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-006 | `ic_result` | keyword_classification | 14 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-007 | `_LEGACY_PIN_TYPE_MAP` | standard | 11 | verified | 0.6 | 0.0 | **low** (0.0) |
| CONST-008 | `_M` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-009 | `_STANDARD_LIB_PINS` | keyword_classification | 34 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-019 | `sym_def` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-020 | `resolution_info` | keyword_classification | 5 | unverified | 0.3 | 0.3 | **medium** (0.3) |
| CONST-011 | `_MAX_SNAP_DIST` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-021 | `_parse_legacy_single_sheet:2786` | standard | 3 | unverified | 0.1 | 0.2 | **low** (0.2) |
| CONST-014 | `ps` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-022 | `sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-023 | `_pin_source_counts` | heuristic_threshold | 4 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-024 | `_SIGNAL_PIN_TYPES` | standard | 7 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-025 | `_SKIP_PIN_TYPES` | standard | 4 | unverified | 0.1 | 0.1 | **low** (0.1) |
| CONST-015 | `output_types` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-026 | `_classify_nets:3449` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-027 | `_classify_nets:3451` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-028 | `_classify_nets:3453` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-029 | `_classify_nets:3455` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-031 | `_classify_nets:3457` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-036 | `_classify_nets:3459` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-037 | `_classify_nets:3461` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-038 | `_classify_nets:3465` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-040 | `_classify_nets:3469` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-223 | `_io_pin_names` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-224 | `_sense_pin_names` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-225 | `_pwr_pin_to_rail` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-226 | `level_translator_keywords` | keyword_classification | 20 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-227 | `level_translator_desc_keywords` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-030 | `_I2C_MODES` | unknown | 4 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-228 | `_spi_net_kw` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-229 | `_spi_canon` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-230 | `_uart_exclude` | keyword_classification | 23 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-041 | `_detect_uart_buses:4039` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-032 | `_tx_pins` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-034 | `_rx_pins` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-072 | `_detect_uart_buses:4059` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-074 | `_detect_uart_buses:4060` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-232 | `_sdio_prefixes` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-085 | `_detect_sdio_buses:4113` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-234 | `can_keywords` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-235 | `can_transceiver_kw` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-236 | `_rs485_kw` | keyword_classification | 28 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-237 | `buses` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-091 | `_analyze_bus_protocols:4336` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-244 | `_diff_suffix_pairs` | unknown | 14 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-245 | `outputs` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-248 | `drivers` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-042 | `drivers` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-043 | `_STANDARD_FP_LIBS` | keyword_classification | 35 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-044 | `_GENERIC_TRANSISTOR_PREFIXES` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-045 | `_GENERIC_TYPE_LABELS` | standard | 4 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-046 | `_PIN_LETTER_NAMES` | standard | 6 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-092 | `classify_ground_domains:5350` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-093 | `classify_ground_domains:5352` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-094 | `classify_ground_domains:5354` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-111 | `classify_ground_domains:5356` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-051 | `esl_by_pkg` | datasheet_lookup | 8 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-052 | `esr_base_by_pkg` | datasheet_lookup | 8 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-112 | `_is_electrolytic_or_tantalum:5890` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-054 | `cap_entry` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-055 | `rail_result` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-056 | `_iq_estimates_uA` | datasheet_lookup | 16 | verified | 0.9 | 0.0 | **low** (0.0) |
| CONST-120 | `_DERATING_PROFILES` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-113 | `_classify_cap_dielectric:6413` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-119 | `_classify_cap_dielectric:6415` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-217 | `_CAP_DERATING` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-218 | `_RESISTOR_POWER_RATING` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-219 | `pkg_sizes` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-220 | `entry_result` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-179 | `_rs232_keywords` | keyword_classification | 13 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-057 | `ic_current_estimates` | datasheet_lookup | 48 | verified | 1.0 | 0.0 | **low** (0.0) |
| CONST-058 | `rail_info` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-059 | `dep_entry` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-303 | `analyze_power_sequencing:7215` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-304 | `analyze_power_sequencing:7217` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-062 | `pg_entry` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-063 | `debug_keywords` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-064 | `key_net_patterns` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-065 | `easy_smd` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-066 | `hard_ic_patterns` | keyword_classification | 4 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-067 | `medium_hard_ic_patterns` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-068 | `medium_ic_patterns` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-069 | `easy_ic_patterns` | keyword_classification | 16 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-070 | `difficulty_counts` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-305 | `_extract_package_info:7585` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-306 | `analyze_usb_compliance:7724` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-073 | `conn_checks` | heuristic_threshold | 4 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-114 | `_PD_CONTROLLER_KEYWORDS` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-115 | `r_info` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-116 | `cc_detail` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-307 | `analyze_usb_compliance:7950` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-075 | `esd_keywords` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-076 | `all_checks` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-077 | `rail_entry` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-122 | `merged_bus` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-136 | `hierarchy_context` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-308 | `_IC_TYPES` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-309 | `sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-149 | `config` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## emc_formulas.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-206 | `C_0` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-207 | `ETA_0` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-208 | `EPSILON_0` | physics | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-209 | `FCC_CLASS_B_RADIATED` | unknown | 4 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-212 | `FCC_CLASS_A_RADIATED` | unknown | 4 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-257 | `CISPR_25_CLASS5_RADIATED` | unknown | 4 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-258 | `MIL_STD_461_RE102` | unknown | 3 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-260 | `STANDARDS` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-261 | `MLCC_ESL` | datasheet_lookup | 8 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-262 | `MLCC_ESR` | datasheet_lookup | 8 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-288 | `DIFF_PAIR_PROTOCOLS` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-289 | `MARKET_STANDARDS` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-153 | `COPPER_RESISTIVITY_OHM_MM` | physics | 1 | verified | 0.1 | 0.0 | **low** (0.0) |

## emc_rules.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-263 | `clock_patterns` | keyword_classification | 18 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-264 | `hs_patterns` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-155 | `suggested` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-460 | `finding` | keyword_classification | 14 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-461 | `check_missing_decoupling:525` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-462 | `check_connector_filtering:650` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-267 | `bands` | unknown | 3 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-384 | `defaults` | datasheet_lookup | 5 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-385 | `ss_keywords` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-363 | `PROXIMITY_MM` | physics | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-292 | `SAMPLE_INTERVAL` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-294 | `connector_sizes` | datasheet_lookup | 19 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-295 | `plan` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-296 | `protocol_speeds` | datasheet_lookup | 10 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-297 | `coverage_rules` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-279 | `severity_order` | heuristic_threshold | 5 | verified | 0.4 | 0.0 | **low** (0.0) |

## kicad_utils.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-104 | `COORD_EPSILON` | physics | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-105 | `_MIL_MM` | physics | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-106 | `_REGULATOR_VREF` | datasheet_lookup | 114 | verified | 1.0 | 0.0 | **low** (0.0) |
| CONST-107 | `_LOAD_TYPE_KEYWORDS` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-108 | `multipliers` | standard | 11 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-222 | `_E_SERIES` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-109 | `type_map` | standard | 65 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-348 | `classify_component:495` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-233 | `_lib_type_overrides` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-349 | `classify_component:523` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-350 | `classify_component:532` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-351 | `classify_component:537` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-352 | `classify_component:540` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-353 | `classify_component:542` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-354 | `classify_component:546` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-355 | `classify_component:549` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-356 | `classify_component:559` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-396 | `classify_component:572` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-397 | `classify_component:575` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-398 | `classify_component:595` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-399 | `classify_component:606` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-400 | `classify_component:610` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-285 | `classify_component:614` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-286 | `classify_component:618` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-401 | `classify_component:656` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-402 | `classify_component:658` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-403 | `classify_component:662` | keyword_classification | 22 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-404 | `classify_component:676` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-405 | `classify_component:678` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-121 | `_ic_lib_prefixes` | keyword_classification | 20 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-406 | `classify_component:725` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-407 | `classify_component:744` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-408 | `classify_ic_function:769` | keyword_classification | 22 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-409 | `classify_ic_function:777` | keyword_classification | 14 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-410 | `classify_ic_function:783` | keyword_classification | 14 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-411 | `classify_ic_function:789` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-412 | `classify_ic_function:794` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-413 | `classify_ic_function:799` | keyword_classification | 14 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-414 | `classify_ic_function:805` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-337 | `classify_ic_function:811` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-415 | `classify_ic_function:816` | keyword_classification | 11 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-416 | `classify_ic_function:822` | keyword_classification | 24 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-417 | `classify_ic_function:830` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-418 | `classify_ic_function:836` | keyword_classification | 27 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-419 | `classify_ic_function:846` | keyword_classification | 22 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-420 | `classify_ic_function:855` | keyword_classification | 18 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-421 | `classify_connector:875` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-422 | `classify_connector:877` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-423 | `classify_connector:884` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-424 | `classify_connector:898` | keyword_classification | 26 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-425 | `classify_connector:905` | keyword_classification | 12 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-426 | `classify_connector:910` | keyword_classification | 12 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-427 | `classify_connector:914` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-188 | `_CAP_PKG_RE` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-189 | `_CAP_PKG_EIA_RE` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-184 | `_CAP_ESR_TABLE` | unknown | 16 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-190 | `_CAP_ESL` | datasheet_lookup | 7 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-191 | `eia_to_imperial` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-428 | `_DC_BIAS_DERATING` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-429 | `_SHIELDED_PATTERNS` | keyword_classification | 15 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-430 | `_SEMI_SHIELDED_PATTERNS` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-431 | `_UNSHIELDED_PATTERNS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-432 | `_RATED_V_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-433 | `_KNOWN_FREQS` | datasheet_lookup | 105 | unverified | 0.8 | 0.0 | **low** (0.0) |

## sexp_parser.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-357 | `_BRACE_ESCAPES` | keyword_classification | 14 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-358 | `_BRACE_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |

## signal_detectors.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-365 | `defaults` | datasheet_lookup | 5 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-434 | `_CRYSTAL_DEFAULT_CL` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-435 | `_classify_divider_purpose:197` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-436 | `_classify_divider_purpose:203` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-437 | `_classify_divider_purpose:206` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-438 | `_classify_divider_purpose:209` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-124 | `divider` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-125 | `rc_entry` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-126 | `lc_entry` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-439 | `detect_crystal_circuits:884` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-127 | `xtal_entry` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-128 | `_osc_keywords` | keyword_classification | 15 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-129 | `_osc_exclude` | keyword_classification | 16 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-130 | `_xtal_pin_re` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-131 | `_SENSE_PIN_PREFIXES` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-132 | `_SENSE_IC_KEYWORDS` | keyword_classification | 31 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-238 | `_SENSE_IC_EXCLUDE` | keyword_classification | 30 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-133 | `_integrated_csa_pins` | keyword_classification | 20 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-134 | `_non_reg_exclude` | keyword_classification | 32 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-239 | `_kw_pmic` | keyword_classification | 18 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-135 | `reg_lib_keywords` | keyword_classification | 52 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-440 | `detect_power_regulators:1644` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-137 | `_rf_exclude` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-138 | `_power_mux_exclude` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-441 | `detect_power_regulators:1662` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-442 | `_opamp_adc_exclude` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-139 | `reg_info` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-140 | `_switching_kw` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-373 | `_charge_pump_kw` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-443 | `detect_power_regulators:1752` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-141 | `inverting_kw` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-444 | `detect_power_regulators:1917` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-445 | `cap_entry` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-143 | `_ldo_pin_names` | keyword_classification | 14 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-242 | `_non_reg_ic_keywords` | keyword_classification | 22 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-144 | `protection_types` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-145 | `tvs_keywords` | keyword_classification | 15 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-146 | `esd_ic_keywords` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-147 | `opamp_lib_keywords` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-148 | `opamp_value_keywords` | keyword_classification | 25 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-446 | `detect_opamp_circuits:2488` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-447 | `detect_opamp_circuits:2494` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-448 | `detect_opamp_circuits:2811` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-449 | `detect_opamp_circuits:2813` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-450 | `detect_opamp_circuits:2826` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-451 | `detect_transistor_circuits:3008` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-452 | `detect_transistor_circuits:3011` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-453 | `detect_transistor_circuits:3014` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-454 | `detect_transistor_circuits:3018` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-246 | `snubber_data` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-152 | `source_sense` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-247 | `_jfet_kw` | keyword_classification | 20 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-455 | `postfilter_vd_and_dedup:3299` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-456 | `detect_design_observations:3535` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-175 | `obs` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-457 | `detect_design_observations:3708` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-458 | `MAX_HOPS` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |

## simulate_subcircuits.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-071 | `_SINGULAR` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |

## spice_model_cache.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-061 | `_GENERATORS` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |

## spice_models.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-047 | `ELEMENT_PREFIX` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-048 | `DEFAULT_MODEL` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-185 | `suffixes` | unknown | 10 | verified | 0.0 | 0.0 | **low** (0.0) |

## spice_part_library.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-049 | `OPAMP_SPECS` | keyword_classification | 49 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-050 | `LDO_SPECS` | keyword_classification | 35 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-053 | `COMPARATOR_SPECS` | keyword_classification | 9 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-060 | `VREF_SPECS` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-276 | `MOSFET_SPECS` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-269 | `CRYSTAL_DRIVER_SPECS` | keyword_classification | 24 | verified | 0.4 | 0.0 | **low** (0.0) |

## spice_results.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-035 | `EVALUATOR_REGISTRY` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-039 | `counts` | heuristic_threshold | 4 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-459 | `report` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## spice_templates.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-197 | `measurements` | unknown | 8 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-198 | `measurements` | unknown | 8 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-199 | `measurements` | unknown | 4 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-200 | `measurements` | unknown | 4 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-201 | `measurements` | unknown | 3 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-202 | `measurements` | unknown | 5 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-203 | `measurements` | unknown | 3 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-240 | `measurements` | unknown | 5 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-241 | `measurements` | unknown | 3 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-270 | `extra` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-271 | `measurements` | unknown | 6 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-272 | `measurements` | unknown | 4 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-273 | `measurements` | unknown | 3 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-274 | `measurements` | unknown | 3 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-275 | `extra` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-033 | `TEMPLATE_REGISTRY` | keyword_classification | 16 | verified | 0.4 | 0.0 | **low** (0.0) |

