# Constants Registry

*Auto-generated from `constants_registry.json` — do not edit manually.*

**Last scan:** 2026-10-15T18:08:30.566008+00:00

## Summary

| Metric | Count |
|--------|-------|
| Total constants | 718 |
| Verified | 183 |
| Unverified | 535 |
| Stale (changed since verification) | 0 |
| Critical risk | 18 |
| High risk | 8 |

## skills/emc/scripts/analyze_emc.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-176 | `SEVERITY_WEIGHTS` | datasheet_lookup | 3 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-463 | `CONFIDENCE_WEIGHTS` | datasheet_lookup | 3 | verified | 0.7 | 0.2 | **low** (0.2) |
| CONST-178 | `MAX_FINDINGS_PER_RULE` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-181 | `sev_order` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-281 | `cat_labels` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-389 | `config` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-282 | `counts` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-390 | `active_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-395 | `_sev_order` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-287 | `_final_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |

## skills/emc/scripts/emc_formulas.py

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

## skills/emc/scripts/emc_rules.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-263 | `clock_patterns` | keyword_classification | 18 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-264 | `hs_patterns` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-155 | `suggested` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-280 | `_EMC_SEVERITY_MAP` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-460 | `finding` | keyword_classification | 14 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-005 | `check_missing_decoupling:620` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-012 | `check_connector_filtering:789` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-267 | `bands` | unknown | 3 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-384 | `defaults` | datasheet_lookup | 5 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-385 | `ss_keywords` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-363 | `PROXIMITY_MM` | physics | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-292 | `SAMPLE_INTERVAL` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-294 | `connector_sizes` | datasheet_lookup | 19 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-290 | `PDN_RELEVANT_FMAX_HZ` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-291 | `_CAP_UNIT_SCALES` | unknown | 5 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-295 | `plan` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-296 | `protocol_speeds` | datasheet_lookup | 10 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-297 | `coverage_rules` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-279 | `severity_order` | heuristic_threshold | 5 | verified | 0.4 | 0.0 | **low** (0.0) |

## skills/emc/scripts/emc_spice.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-293 | `prefixes` | unknown | 10 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-301 | `measurements` | unknown | 3 | unverified | 0.0 | 0.0 | **low** (0.0) |

## skills/kicad/scripts/analysis_cache.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-310 | `CANONICAL_OUTPUTS` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-311 | `_OUTPUT_SOURCE_EXT` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-312 | `_SEVERITY_ORDER` | heuristic_threshold | 4 | unverified | 0.4 | 0.0 | **medium** (0.4) |

## skills/kicad/scripts/analyze_gerbers.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-210 | `_POWER_KEYWORDS_GERBER` | standard | 12 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-099 | `patterns` | keyword_classification | 22 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-100 | `ext_map` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-103 | `_GERBER_EXTENSIONS` | standard | 17 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-347 | `required_layers` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-313 | `_gerber_exts` | standard | 23 | unverified | 0.1 | 0.0 | **low** (0.1) |

## skills/kicad/scripts/analyze_pcb.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-314 | `MAX_TESTED_FORMAT_VERSION` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
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
| CONST-315 | `ANTIPAD_CLEARANCE` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-316 | `ANTIPAD_GRID` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-317 | `sample` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-089 | `seg_entry` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-318 | `analyze_ground_domains:2557` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-086 | `type_counts` | standard | 4 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-087 | `type_sizes` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-088 | `annular_ring` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-319 | `analyze_vias:3242` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-090 | `current_facts` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-214 | `rev_pattern` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-323 | `extract_silkscreen:3591` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-324 | `extract_silkscreen:3593` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-325 | `extract_silkscreen:3601` | keyword_classification | 11 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-195 | `_fab_notes_checklist` | heuristic_threshold | 6 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-326 | `extract_silkscreen:3671` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-327 | `extract_silkscreen:3674` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-328 | `extract_silkscreen:3676` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-329 | `extract_silkscreen:3678` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-221 | `_silk_checks` | heuristic_threshold | 5 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-320 | `_RF_MODULE_KEYWORDS` | keyword_classification | 20 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-321 | `_RF_LIB_KEYWORDS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-330 | `_EDGE_MOUNT_LIBRARY_KEYWORDS` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-331 | `MIN_REAL_DRILL_MM` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-095 | `LIMITS_STD` | standard | 7 | verified | 0.1 | 0.3 | **low** (0.3) |
| CONST-096 | `LIMITS_ADV` | standard | 4 | verified | 0.1 | 0.2 | **low** (0.2) |
| CONST-266 | `IPC_CLASS_LIMITS` | standard | 3 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-298 | `constraints` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-299 | `checks` | unknown | 3 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-332 | `v` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-097 | `risk_order` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-098 | `adequacy_order` | heuristic_threshold | 4 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-333 | `_PASSIVE_REF_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-300 | `_gnd_keywords` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-334 | `analyze_copper_presence:6059` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-335 | `analyze_copper_presence:6060` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-336 | `analyze_fiducials:6239` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-344 | `finding` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-345 | `_FINDING_LIST_KEYS` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-346 | `sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-302 | `config` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/analyze_schematic.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-337 | `MAX_TESTED_FORMAT_VERSION` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-078 | `_UUID_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-010 | `_MANUFACTURER_KEYS` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-013 | `_MOUSER_KEYS` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-016 | `_LCSC_KEYS` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-017 | `_ELEMENT14_KEYS` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-338 | `_ANGLE_TRANSFORM` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-001 | `_WIRE_GRID_SIZE` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-002 | `_NET_NAME_PRIORITY` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-339 | `_INTERNAL_LABEL_KEYS` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-158 | `_IC_LIB_PREFIX_MAP` | keyword_classification | 58 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-170 | `_IC_VALUE_KEYWORDS` | unknown | 45 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-186 | `_IC_DESC_KEYWORDS` | unknown | 44 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-003 | `target_types` | keyword_classification | 4 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-004 | `pin_entry` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-018 | `analyze_ic_pinouts:2386` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-006 | `ic_result` | keyword_classification | 14 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-007 | `_LEGACY_PIN_TYPE_MAP` | standard | 11 | verified | 0.6 | 0.0 | **low** (0.0) |
| CONST-008 | `_M` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-009 | `_STANDARD_LIB_PINS` | keyword_classification | 34 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-019 | `sym_def` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-020 | `resolution_info` | keyword_classification | 5 | unverified | 0.3 | 0.3 | **medium** (0.3) |
| CONST-011 | `_MAX_SNAP_DIST` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-021 | `_parse_legacy_single_sheet:3144` | standard | 3 | unverified | 0.1 | 0.2 | **low** (0.2) |
| CONST-014 | `ps` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-022 | `sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-023 | `_pin_source_counts` | heuristic_threshold | 4 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-024 | `_SIGNAL_PIN_TYPES` | standard | 7 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-025 | `_SKIP_PIN_TYPES` | standard | 4 | unverified | 0.1 | 0.1 | **low** (0.1) |
| CONST-015 | `output_types` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-026 | `_classify_nets:3813` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-027 | `_classify_nets:3815` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-028 | `_classify_nets:3817` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-029 | `_classify_nets:3819` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-031 | `_classify_nets:3821` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-036 | `_classify_nets:3823` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-037 | `_classify_nets:3825` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-038 | `_classify_nets:3829` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-040 | `_classify_nets:3833` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-223 | `_io_pin_names` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-224 | `_sense_pin_names` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-225 | `_pwr_pin_to_rail` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-226 | `level_translator_keywords` | keyword_classification | 20 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-227 | `level_translator_desc_keywords` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-030 | `_I2C_MODES` | unknown | 4 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-228 | `_spi_net_kw` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-229 | `_spi_canon` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-230 | `_uart_exclude` | keyword_classification | 23 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-041 | `_detect_uart_buses:4403` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-032 | `_tx_pins` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-034 | `_rx_pins` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-072 | `_detect_uart_buses:4423` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-356 | `_detect_uart_buses:4424` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-232 | `_sdio_prefixes` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-074 | `_detect_sdio_buses:4477` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-234 | `can_keywords` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-235 | `can_transceiver_kw` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-236 | `_rs485_kw` | keyword_classification | 28 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-237 | `buses` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-085 | `_analyze_bus_protocols:4700` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-244 | `_diff_suffix_pairs` | unknown | 14 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-245 | `outputs` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-248 | `drivers` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-042 | `drivers` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-043 | `_STANDARD_FP_LIBS` | keyword_classification | 35 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-364 | `_DS_DIR_NAMES` | keyword_classification | 4 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-044 | `_GENERIC_TRANSISTOR_PREFIXES` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-045 | `_GENERIC_TYPE_LABELS` | standard | 4 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-046 | `_PIN_LETTER_NAMES` | standard | 6 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-091 | `classify_ground_domains:5834` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-092 | `classify_ground_domains:5836` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-093 | `classify_ground_domains:5838` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-094 | `classify_ground_domains:5840` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-051 | `esl_by_pkg` | datasheet_lookup | 8 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-052 | `esr_base_by_pkg` | datasheet_lookup | 8 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-111 | `_is_electrolytic_or_tantalum:6403` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-054 | `cap_entry` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-055 | `rail_result` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-371 | `SLEEP_PULL_MIN_OHM` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-372 | `_battery_rail_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-056 | `_iq_estimates_uA` | datasheet_lookup | 16 | verified | 0.9 | 0.0 | **low** (0.0) |
| CONST-120 | `_DERATING_PROFILES` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-112 | `_classify_cap_dielectric:7062` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-113 | `_classify_cap_dielectric:7064` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-217 | `_CAP_DERATING` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-218 | `_RESISTOR_POWER_RATING` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-219 | `pkg_sizes` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-220 | `entry_result` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-179 | `_rs232_keywords` | keyword_classification | 13 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-057 | `ic_current_estimates` | datasheet_lookup | 48 | verified | 1.0 | 0.0 | **low** (0.0) |
| CONST-058 | `rail_info` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-059 | `dep_entry` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-117 | `analyze_power_sequencing:7951` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-118 | `analyze_power_sequencing:7953` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-062 | `pg_entry` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-063 | `debug_keywords` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-064 | `key_net_patterns` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-065 | `easy_smd` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-066 | `hard_ic_patterns` | keyword_classification | 4 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-067 | `medium_hard_ic_patterns` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-068 | `medium_ic_patterns` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-069 | `easy_ic_patterns` | keyword_classification | 16 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-070 | `difficulty_counts` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-119 | `_extract_package_info:8321` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-123 | `analyze_usb_compliance:8460` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-073 | `conn_checks` | heuristic_threshold | 4 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-114 | `_PD_CONTROLLER_KEYWORDS` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-115 | `r_info` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-116 | `cc_detail` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-075 | `esd_keywords` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-142 | `analyze_usb_compliance:8692` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-381 | `_uc_specs` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-076 | `all_checks` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-077 | `rail_entry` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-122 | `merged_bus` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-308 | `_IC_TYPES` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-309 | `sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-149 | `config` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-110 | `_sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |

## skills/kicad/scripts/analyze_thermal.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-382 | `DEFAULT_AMBIENT_C` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-383 | `DEFAULT_TJ_MAX_C` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-386 | `DEFAULT_RTHETA_JA` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-387 | `MIN_PDISS_W` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-391 | `SEVERITY_WEIGHTS` | datasheet_lookup | 3 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-392 | `MAX_FINDINGS_PER_RULE` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-393 | `SWITCHING_EFFICIENCY` | datasheet_lookup | 4 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-394 | `PACKAGE_THERMAL_RESISTANCE` | unknown | 38 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-150 | `_check_thermal_proximity:683` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-397 | `sev_order` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-398 | `config` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-399 | `counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |

## skills/kicad/scripts/bus_resolver.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-400 | `_VECTOR_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-401 | `_GROUP_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-402 | `_MAX_DEPTH` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-403 | `_EPSILON` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |

## skills/kicad/scripts/check_report_sections.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-404 | `SCHEMATIC_KEY_SECTIONS` | unknown | 11 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-405 | `BASE_SECTIONS` | unknown | 8 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-406 | `ANALYZER_SECTIONS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-407 | `ANALYZER_FILES` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/cross_analysis.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-408 | `_IPC2152_1OZ_10C` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-409 | `_NET_NAME_HEURISTICS` | unknown | 9 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-410 | `_HIGH_SPEED_TYPES` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-411 | `_EXTERNAL_CONNECTOR_KEYWORDS` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-412 | `_EDGE_DISTANCE_ERROR_MM` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-413 | `_EDGE_DISTANCE_WARN_MM` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-414 | `check_plane_splits:755` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-415 | `_SPEED_OF_LIGHT` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-416 | `_EFFECTIVE_ER` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-417 | `_DIFF_PAIR_SUFFIXES` | unknown | 5 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-418 | `sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |

## skills/kicad/scripts/cross_verify.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-419 | `status_counts` | heuristic_threshold | 4 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-420 | `_TOLERANCES` | physics | 7 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-421 | `_intra_pair_tolerance` | physics | 7 | unverified | 0.1 | 0.0 | **low** (0.1) |

## skills/kicad/scripts/detection_schema.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-422 | `SCHEMAS` | keyword_classification | 64 | unverified | 0.5 | 0.0 | **high** (0.5) |

## skills/kicad/scripts/diff_analysis.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-469 | `MAX_TEXT_ITEMS` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-470 | `diff_funcs` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/diff_engine.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-151 | `stat_paths` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-154 | `comp_diff` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-156 | `bom_diff` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-157 | `stat_paths` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-159 | `fp_diff` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-160 | `sev_paths` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-161 | `findings_diff` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-162 | `sum_paths` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-163 | `stat_paths` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-164 | `findings_diff` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/domain_detectors.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-471 | `iso_keywords` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-165 | `detect_isolation_barriers:313` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-474 | `detect_isolation_barriers:345` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-166 | `detect_isolation_barriers:347` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-475 | `eth_phy_keywords` | keyword_classification | 21 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-476 | `magnetics_keywords` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-167 | `detect_ethernet_interfaces:437` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-478 | `_eth_tx_rx_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-479 | `_eth_net_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-480 | `bob_smith` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-481 | `_bridge_kw` | keyword_classification | 22 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-482 | `_hdmi_conn_kw` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-483 | `_tmds_pin_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-484 | `_tmds_net_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-485 | `_lvds_keywords` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-486 | `_serializer_hints` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-487 | `_deserializer_hints` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-488 | `memory_keywords` | keyword_classification | 30 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-489 | `processor_keywords` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-490 | `RF_IC_BANDS` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-491 | `RF_ROLE_GAIN_DB` | datasheet_lookup | 10 | unverified | 0.7 | 0.1 | **critical** (0.7) |
| CONST-492 | `rf_switch_keywords` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-493 | `rf_mixer_keywords` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-494 | `rf_amp_keywords` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-495 | `rf_transceiver_keywords` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-496 | `rf_filter_keywords` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-497 | `rf_attenuator_keywords` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-498 | `rf_coupler_keywords` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-499 | `rf_power_detector_keywords` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-500 | `rf_freq_multiplier_keywords` | standard | 3 | unverified | 0.1 | 0.1 | **low** (0.1) |
| CONST-168 | `detect_rf_chains:1096` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-502 | `_RF_REFERENCE_DESIGNS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-503 | `_ant_keywords` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-504 | `_ant_lib_keywords` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-169 | `detect_rf_matching:1408` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-506 | `_rf_keywords` | keyword_classification | 29 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-507 | `bms_ic_keywords` | keyword_classification | 15 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-171 | `detect_bms_systems:1610` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-509 | `power_path_keywords` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-510 | `_CHARGER_PROG_FORMULAS` | keyword_classification | 25 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-511 | `_CELL_PROTECTION_KEYWORDS` | keyword_classification | 14 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-512 | `_PROG_PIN_NAMES` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-513 | `_STATUS_PIN_NAMES` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-514 | `_BAT_PIN_NAMES` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-515 | `_VIN_PIN_NAMES` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-516 | `prog_info` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-172 | `detect_battery_chargers:1863` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-173 | `detect_battery_chargers:1868` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-519 | `prot_entry` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-520 | `_MOTOR_DRIVER_KEYWORDS` | keyword_classification | 42 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-521 | `_GATE_DRIVER_KEYWORDS` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-522 | `_STEPPER_PIN_NAMES` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-523 | `_MOTOR_OUTPUT_PIN_NAMES` | keyword_classification | 41 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-524 | `_GATE_OUTPUT_PIN_NAMES` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-525 | `_BOOTSTRAP_PIN_NAMES` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-526 | `_INDUCTIVE_LOAD_KEYWORDS` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-527 | `addr_keywords` | keyword_classification | 13 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-174 | `_get_protocol:2270` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-529 | `din_names` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-530 | `dout_names` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-531 | `_ESD_HIGH_RISK_KEYWORDS` | keyword_classification | 13 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-532 | `_ESD_MEDIUM_RISK_KEYWORDS` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-533 | `_ESD_LOW_RISK_KEYWORDS` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-534 | `detail` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-535 | `_JTAG_ALIASES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-536 | `_RESET_ALIASES` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-537 | `_DEBUG_CONNECTOR_KEYWORDS` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-538 | `required` | keyword_classification | 4 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-539 | `_LOAD_SWITCH_KEYWORDS` | keyword_classification | 25 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-540 | `_IDEAL_DIODE_KEYWORDS` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-541 | `_USB_PD_KEYWORDS` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-542 | `_POWER_IN_PINS` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-543 | `_POWER_OUT_PINS` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-544 | `_ENABLE_PINS` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-545 | `_CC_PINS` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-546 | `_SBU_PINS` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-177 | `detect_power_path:2831` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-548 | `_ADC_IC_KEYWORDS` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-549 | `_VREF_IC_KEYWORDS` | keyword_classification | 18 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-550 | `_ADC_PIN_PREFIXES` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-551 | `_VREF_PIN_NAMES` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-552 | `_SPI_PIN_NAMES` | keyword_classification | 13 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-553 | `_ADC_RESOLUTION_MAP` | datasheet_lookup | 29 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-554 | `_SUPERVISOR_IC_KEYWORDS` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-555 | `_WATCHDOG_IC_KEYWORDS` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-556 | `_RESET_OUTPUT_PINS` | keyword_classification | 15 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-557 | `_RESET_INPUT_PINS` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-558 | `_WDI_PINS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-559 | `_SUPERVISOR_VIN_PINS` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-180 | `_is_reset_net_name:3359` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-561 | `_CLOCK_BUFFER_KEYWORDS` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-562 | `_PLL_KEYWORDS` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-563 | `_CLOCK_INPUT_PINS` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-564 | `_CLOCK_OUTPUT_PINS` | keyword_classification | 22 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-565 | `_DISPLAY_IC_KEYWORDS` | keyword_classification | 22 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-566 | `_TOUCH_IC_KEYWORDS` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-567 | `_DISPLAY_CONTROL_PINS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-568 | `_BACKLIGHT_PINS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-569 | `_DISPLAY_RESET_PINS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-570 | `_OLED_KEYWORDS` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-571 | `_EPAPER_KEYWORDS` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-572 | `_IMU_KEYWORDS` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-573 | `_ENV_SENSOR_KEYWORDS` | keyword_classification | 15 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-574 | `_MAG_KEYWORDS` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-575 | `_SENSOR_INT_PINS` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-576 | `_SENSOR_SPI_PINS` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-577 | `_LEVEL_SHIFTER_KEYWORDS` | keyword_classification | 24 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-578 | `_VCCA_PINS` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-579 | `_VCCB_PINS` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-580 | `_LS_ENABLE_PINS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-581 | `_BIDIR_KEYWORDS` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-582 | `_UNIDIR_KEYWORDS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-583 | `_logic_gate_patterns` | keyword_classification | 22 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-182 | `detect_level_shifters:4265` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-585 | `_AUDIO_AMP_KEYWORDS` | keyword_classification | 18 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-586 | `_AUDIO_CODEC_KEYWORDS` | keyword_classification | 18 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-587 | `_I2S_PINS` | keyword_classification | 13 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-588 | `_AUDIO_OUTPUT_PINS` | keyword_classification | 20 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-589 | `_AUDIO_INPUT_PINS` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-590 | `_CLASS_D_KEYWORDS` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-183 | `detect_audio_circuits:4442` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-592 | `_LED_DRIVER_IC_KEYWORDS` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-593 | `_LED_PWM_KEYWORDS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-594 | `_LED_CC_KEYWORDS` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-595 | `_LED_CURRENT_SET_PINS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-596 | `_LED_OUTPUT_PREFIXES` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-597 | `_RTC_IC_KEYWORDS` | keyword_classification | 24 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-598 | `_VBAT_PINS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-599 | `_RTC_INT_PINS` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-600 | `_RTC_SQW_PINS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-601 | `_INTERNAL_OSC_KEYWORDS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-187 | `detect_rtc_circuits:4726` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-603 | `battery_backup` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-604 | `_LED_VF` | datasheet_lookup | 8 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-605 | `_LED_VF_FLOOR` | datasheet_lookup | 8 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-606 | `addr_keywords` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-607 | `_TC_IC_KEYWORDS` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-608 | `_RTD_IC_KEYWORDS` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-609 | `_TC_INPUT_PINS` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-610 | `_RTD_REF_PINS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-611 | `_RTD_FORCE_PINS` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-612 | `_INTERNAL_CJC_KEYWORDS` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-613 | `_EN_PIN_NAMES` | keyword_classification | 14 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-614 | `_PG_PIN_NAMES` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-615 | `tree_entry` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-192 | `suggest_certifications:5617` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-617 | `_WIFI_BLE_KEYWORDS` | keyword_classification | 28 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-618 | `_LORA_KEYWORDS` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-619 | `_CELLULAR_KEYWORDS` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-620 | `_GPS_KEYWORDS` | keyword_classification | 15 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-621 | `_ANTENNA_PIN_NAMES` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-622 | `_SIM_PIN_NAMES` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-623 | `_FLYBACK_CONTROLLER_KEYWORDS` | keyword_classification | 25 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-624 | `_OPTOCOUPLER_KEYWORDS` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-625 | `_TL431_KEYWORDS` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-626 | `_I2C_DEVICE_ADDRESSES` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-627 | `_HARVESTER_KEYWORDS` | keyword_classification | 18 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-628 | `_SUPERCAP_KEYWORDS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-629 | `_HP_JACK_KEYWORDS` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-630 | `_HP_DET_PIN_NAMES` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/export_issues.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-631 | `_SEV_RANK` | datasheet_lookup | 7 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-632 | `cmd` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-633 | `known` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-634 | `payload` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/fab_release_gate.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-635 | `check_gerbers:243` | standard | 10 | unverified | 0.1 | 0.2 | **low** (0.2) |
| CONST-636 | `posture` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-637 | `counts` | heuristic_threshold | 4 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-638 | `_STATUS_ICONS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-639 | `_OVERALL_ICONS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/finding_schema.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-640 | `VALID_SEVERITIES` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-641 | `VALID_CONFIDENCES` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-642 | `VALID_EVIDENCE_SOURCES` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-643 | `VALID_FIX_TYPES` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-644 | `_RULE_CODE_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-645 | `_SEVERITY_NORMALIZE` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-646 | `finding` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-647 | `bom_coverage` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-648 | `by_confidence_out` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-649 | `DETECTOR_TO_SCHEMA_KEY` | keyword_classification | 48 | unverified | 0.5 | 0.0 | **high** (0.5) |

## skills/kicad/scripts/gen_output_schema_md.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-650 | `out` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/kicad_core/classify.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-193 | `type_map` | standard | 65 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-194 | `classify_component:86` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-196 | `_lib_type_overrides` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-204 | `classify_component:114` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-205 | `_osc_internal_phrases` | keyword_classification | 4 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-216 | `_clock_pin_names` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-231 | `classify_component:136` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-243 | `classify_component:141` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-249 | `classify_component:144` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-250 | `classify_component:146` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-251 | `classify_component:150` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-252 | `classify_component:153` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-253 | `classify_component:163` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-254 | `classify_component:176` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-255 | `classify_component:179` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-256 | `classify_component:205` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-259 | `classify_component:216` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-265 | `classify_component:220` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-268 | `classify_component:224` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-277 | `classify_component:228` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-278 | `classify_component:266` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-283 | `classify_component:268` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-284 | `classify_component:272` | keyword_classification | 22 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-303 | `classify_component:286` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-304 | `classify_component:288` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-305 | `_ic_lib_prefixes` | keyword_classification | 20 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-306 | `classify_component:335` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-307 | `classify_component:359` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-355 | `classify_ic_function:384` | keyword_classification | 22 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-388 | `classify_ic_function:392` | keyword_classification | 14 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-423 | `classify_ic_function:398` | keyword_classification | 14 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-425 | `classify_ic_function:404` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-435 | `classify_ic_function:409` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-436 | `classify_ic_function:414` | keyword_classification | 14 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-439 | `classify_ic_function:420` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-440 | `classify_ic_function:426` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-441 | `classify_ic_function:431` | keyword_classification | 11 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-443 | `classify_ic_function:437` | keyword_classification | 24 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-444 | `classify_ic_function:445` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-446 | `classify_ic_function:451` | keyword_classification | 27 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-447 | `classify_ic_function:461` | keyword_classification | 22 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-448 | `classify_ic_function:470` | keyword_classification | 18 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-449 | `classify_connector:490` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-450 | `classify_connector:492` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-451 | `classify_connector:499` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-452 | `classify_connector:513` | keyword_classification | 26 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-453 | `classify_connector:520` | keyword_classification | 12 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-454 | `classify_connector:525` | keyword_classification | 12 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-455 | `classify_connector:529` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |

## skills/kicad/scripts/kicad_core/fields.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-456 | `MPN_FIELD_ALIASES_PRIMARY` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-457 | `MPN_FIELD_ALIASES_GENERIC` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-826 | `DIGIKEY_FIELD_ALIASES` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/kicad_core/netnames.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-827 | `USB_DATA_NET_MARKERS` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-828 | `_SIGNAL_PREFIXES` | keyword_classification | 40 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-829 | `_POWER_PREFIXES` | keyword_classification | 25 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-830 | `_SUPPLY_TAILS` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-831 | `_RAIL_TAILS_GATED` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-832 | `_VOLTAGE_SIGNAL_SUFFIXES` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/kicad_core/parts.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-833 | `_REGULATOR_VREF` | datasheet_lookup | 114 | unverified | 1.0 | 0.0 | **critical** (1.0) |
| CONST-834 | `_LOAD_TYPE_KEYWORDS` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-835 | `_KNOWN_FREQS` | datasheet_lookup | 105 | unverified | 0.8 | 0.0 | **critical** (0.8) |

## skills/kicad/scripts/kicad_core/passives.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-836 | `_CAP_PKG_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-837 | `_CAP_PKG_EIA_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-838 | `_CAP_ESR_TABLE` | unknown | 16 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-839 | `_CAP_ESL` | datasheet_lookup | 7 | unverified | 0.8 | 0.0 | **critical** (0.8) |
| CONST-840 | `eia_to_imperial` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-841 | `_DC_BIAS_DERATING` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-842 | `_SHIELDED_PATTERNS` | keyword_classification | 15 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-843 | `_SEMI_SHIELDED_PATTERNS` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-844 | `_UNSHIELDED_PATTERNS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/kicad_core/values.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-845 | `COORD_EPSILON` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-846 | `_MIL_MM` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-847 | `multipliers` | standard | 11 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-848 | `_E_SERIES` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-849 | `_RATED_V_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |

## skills/kicad/scripts/lifecycle_audit.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-706 | `_TEMP_PRESETS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-707 | `_LIFECYCLE_STATUS_RULES` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-708 | `_STATUS_NORMALIZE` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-709 | `_GENERIC_VALUE_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-710 | `_SKIP_TYPES` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-711 | `api_fns` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-712 | `temp_data` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-713 | `_non_active` | keyword_classification | 4 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-714 | `status_counts` | heuristic_threshold | 6 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-715 | `finding` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-716 | `alert_map` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-717 | `labels` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-718 | `sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |

## skills/kicad/scripts/lookup_detectors.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-719 | `VDD_SYNONYMS` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-720 | `TJ_SYNONYMS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-721 | `THETA_JA_SYNONYMS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-722 | `_FT_001_THRESHOLD_V` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-723 | `_PERIPHERAL_HINTS` | unknown | 6 | unverified | 0.0 | 0.0 | **low** (0.0) |

## skills/kicad/scripts/output_filters.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-724 | `STAGES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-725 | `_STAGE_RULES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-726 | `lines` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/pcb_connectivity.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-727 | `node_a` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-728 | `node_b` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/project_config.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-729 | `VALID_MARKETS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-730 | `VALID_DERATING_PROFILES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-731 | `VALID_BOARD_CLASSES` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-732 | `VALID_SUPPLIERS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-733 | `VALID_BOM_GROUP_BY` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-734 | `DEFAULT_CONFIG` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-735 | `_IPC_CONTEXT_PATTERN` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-736 | `VALID_TARGET_MARKETS` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-737 | `VALID_PASSIVE_SIZES` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-850 | `resolve_design_intent:450` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-851 | `resolve_design_intent:541` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-740 | `defaults` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-741 | `SEVERITY_WEIGHTS` | datasheet_lookup | 5 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-742 | `CONFIDENCE_WEIGHTS` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-743 | `RESPIN_CATEGORIES` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-744 | `BRINGUP_CATEGORIES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-745 | `MANUFACTURING_CATEGORIES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-746 | `BUCKET_BOOSTS` | datasheet_lookup | 3 | unverified | 0.7 | 0.1 | **critical** (0.7) |
| CONST-747 | `buckets` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/run_id.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-748 | `_HEX_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |

## skills/kicad/scripts/schema_codec.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-749 | `out` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/sexp_parser.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-357 | `_BRACE_ESCAPES` | keyword_classification | 14 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-358 | `_BRACE_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |

## skills/kicad/scripts/signal_detectors.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-365 | `defaults` | datasheet_lookup | 5 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-434 | `_CRYSTAL_DEFAULT_CL` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-852 | `_classify_divider_purpose:201` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-853 | `_classify_divider_purpose:207` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-854 | `_classify_divider_purpose:210` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-855 | `_classify_divider_purpose:213` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-124 | `divider` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-125 | `rc_entry` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-126 | `lc_entry` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-856 | `detect_crystal_circuits:910` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
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
| CONST-857 | `detect_power_regulators:1685` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-137 | `_rf_exclude` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-138 | `_power_mux_exclude` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-858 | `detect_power_regulators:1703` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-442 | `_opamp_adc_exclude` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-139 | `reg_info` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-140 | `_switching_kw` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-373 | `_charge_pump_kw` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-859 | `detect_power_regulators:1793` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-141 | `inverting_kw` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-860 | `detect_power_regulators:1958` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-445 | `cap_entry` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-143 | `_ldo_pin_names` | keyword_classification | 14 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-242 | `_non_reg_ic_keywords` | keyword_classification | 22 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-144 | `protection_types` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-145 | `tvs_keywords` | keyword_classification | 15 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-146 | `esd_ic_keywords` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-147 | `opamp_lib_keywords` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-148 | `opamp_value_keywords` | keyword_classification | 25 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-861 | `detect_opamp_circuits:2539` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-862 | `detect_opamp_circuits:2545` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-863 | `detect_opamp_circuits:2862` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-864 | `detect_opamp_circuits:2864` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-865 | `detect_opamp_circuits:2877` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-866 | `detect_transistor_circuits:3060` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-867 | `detect_transistor_circuits:3063` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-868 | `detect_transistor_circuits:3066` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-869 | `detect_transistor_circuits:3070` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-246 | `snubber_data` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-152 | `source_sense` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-247 | `_jfet_kw` | keyword_classification | 20 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-870 | `postfilter_vd_and_dedup:3351` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-871 | `detect_design_observations:3591` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-175 | `obs` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-872 | `detect_design_observations:3764` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-769 | `SHORTABLE` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-770 | `MASS_SHORT_THRESHOLD` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-771 | `_MODULE_INTERNAL_RAIL_PATTERNS` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-458 | `MAX_HOPS` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |

## skills/kicad/scripts/summarize_findings.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-772 | `_SEV_RANK` | datasheet_lookup | 6 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-773 | `payload` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-774 | `severity_totals` | datasheet_lookup | 3 | unverified | 0.7 | 0.0 | **critical** (0.7) |

## skills/kicad/scripts/validation_detectors.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-775 | `_HAS_DS` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-776 | `_PULLUP_PIN_NAMES` | keyword_classification | 49 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-777 | `_PULLDOWN_PIN_NAMES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-778 | `_OPEN_DRAIN_IC_KEYWORDS` | keyword_classification | 20 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-779 | `_PULLUP_MIN_OHMS` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-780 | `_PULLUP_MAX_OHMS` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-781 | `_INTERNAL_EN_PULLUP_REGULATOR_PREFIXES` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-873 | `validate_pullups:300` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-783 | `_VOLTAGE_THRESHOLDS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-784 | `_EN_PIN_PATTERNS` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-874 | `validate_voltage_levels:590` | keyword_classification | 18 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-786 | `_I2C_IC_KEYWORDS` | keyword_classification | 51 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-787 | `_I2C_SDA_NAMES` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-788 | `_I2C_SCL_NAMES` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-789 | `_I2C_PULLUP_RANGES` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-790 | `_SPI_IC_KEYWORDS` | keyword_classification | 29 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-791 | `_SPI_CS_NAMES` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-792 | `_CAN_IC_KEYWORDS` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-793 | `_CAN_H_NAMES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-794 | `_CAN_L_NAMES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-795 | `_USB_DP_NAMES` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-796 | `_USB_DM_NAMES` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-797 | `_ENABLE_PIN_NAMES` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-798 | `_PG_PIN_NAMES` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-799 | `_SEQUENCING_SENSITIVE_KEYWORDS` | keyword_classification | 21 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-800 | `_LED_VF_BY_COLOR` | datasheet_lookup | 9 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-801 | `_LED_VF_DEFAULT` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-802 | `_LED_IF_MAX_DEFAULT_MA` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-803 | `_LED_IF_RECOMMENDED_MA` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-804 | `_REQUIRES_COMPENSATION_KEYWORDS` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-805 | `_INTERNALLY_COMPENSATED_KEYWORDS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-806 | `_FB_PIN_NAMES` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-807 | `_FB_IMPEDANCE_MIN` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-808 | `_FB_IMPEDANCE_MAX` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |

## skills/kicad/scripts/what_if.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-809 | `_VALUE_UNITS` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-810 | `_DEFAULT_TOL` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-811 | `_RHO_CU` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-812 | `_CU_THICKNESS_1OZ` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-813 | `_FOOTPRINT_MAX_CAP` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-814 | `pkg_upgrade` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/spice/scripts/extract_parasitics.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-815 | `RHO_CU` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-816 | `EPS_0` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-817 | `VIA_PLATING_UM` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-818 | `net_entry` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/spice/scripts/simulate_subcircuits.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-071 | `_SINGULAR` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |

## skills/spice/scripts/spice_model_cache.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-061 | `_GENERATORS` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |

## skills/spice/scripts/spice_models.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-047 | `ELEMENT_PREFIX` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-048 | `DEFAULT_MODEL` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-185 | `suffixes` | unknown | 10 | verified | 0.0 | 0.0 | **low** (0.0) |

## skills/spice/scripts/spice_part_library.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-049 | `OPAMP_SPECS` | keyword_classification | 49 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-050 | `LDO_SPECS` | keyword_classification | 35 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-053 | `COMPARATOR_SPECS` | keyword_classification | 9 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-060 | `VREF_SPECS` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-276 | `MOSFET_SPECS` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-269 | `CRYSTAL_DRIVER_SPECS` | keyword_classification | 24 | verified | 0.4 | 0.0 | **low** (0.0) |

## skills/spice/scripts/spice_results.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-035 | `EVALUATOR_REGISTRY` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-039 | `counts` | heuristic_threshold | 4 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-459 | `report` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/spice/scripts/spice_simulator.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-819 | `BACKENDS` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/spice/scripts/spice_spec_fetcher.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-820 | `_OPAMP_PARAM_MAP` | unknown | 10 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-821 | `_LDO_PARAM_MAP` | unknown | 4 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-822 | `mult` | datasheet_lookup | 4 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-823 | `mult` | datasheet_lookup | 3 | unverified | 0.7 | 0.0 | **critical** (0.7) |

## skills/spice/scripts/spice_templates.py

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

## skills/spice/scripts/spice_tolerance.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-824 | `DEFAULT_TOLERANCE` | physics | 3 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-825 | `_VALUE_KEYS` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

