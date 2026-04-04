# Constants Registry

*Auto-generated from `constants_registry.json` — do not edit manually.*

**Last scan:** 2026-04-03T00:34:13.886197+00:00

## Summary

| Metric | Count |
|--------|-------|
| Total constants | 298 |
| Verified | 298 |
| Unverified | 0 |
| Stale (changed since verification) | 0 |
| Critical risk | 0 |
| High risk | 0 |

## analyze_emc.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-176 | `SEVERITY_WEIGHTS` | heuristic_threshold | 5 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-178 | `MAX_FINDINGS_PER_RULE` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-181 | `sev_order` | heuristic_threshold | 5 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-281 | `cat_labels` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-282 | `counts` | heuristic_threshold | 5 | verified | 0.4 | 0.0 | **low** (0.0) |

## analyze_gerbers.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-210 | `_POWER_KEYWORDS_GERBER` | standard | 12 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-099 | `patterns` | keyword_classification | 22 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-100 | `ext_map` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-103 | `_GERBER_EXTENSIONS` | standard | 17 | verified | 0.1 | 0.0 | **low** (0.0) |

## analyze_pcb.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-322 | `_NUMERIC_STACKUP_KEYS` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-079 | `_float_keys` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-080 | `pad_info` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-081 | `fp_entry` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-101 | `seg_info` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-102 | `arc_info` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-082 | `via_info` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-083 | `zone_info` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-084 | `bbox` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-211 | `_ESD_TVS_PREFIXES` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-213 | `SNAP` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-215 | `SAMPLE_INTERVAL` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-089 | `seg_entry` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-323 | `analyze_ground_domains:1848` | keyword_classification | 3 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-086 | `type_counts` | standard | 3 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-087 | `type_sizes` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-088 | `annular_ring` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-324 | `analyze_vias:2437` | keyword_classification | 10 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-090 | `current_facts` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-214 | `rev_pattern` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-325 | `extract_silkscreen:2771` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-326 | `extract_silkscreen:2773` | keyword_classification | 3 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-327 | `extract_silkscreen:2781` | keyword_classification | 11 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-095 | `LIMITS_STD` | standard | 7 | verified | 0.1 | 0.3 | **low** (0.3) |
| CONST-096 | `LIMITS_ADV` | standard | 4 | verified | 0.1 | 0.2 | **low** (0.2) |
| CONST-097 | `risk_order` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-098 | `adequacy_order` | heuristic_threshold | 4 | verified | 0.4 | 0.1 | **low** (0.1) |

## analyze_schematic.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-005 | `_MPN_KEYS` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-010 | `_MANUFACTURER_KEYS` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-012 | `_DIGIKEY_KEYS` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-013 | `_MOUSER_KEYS` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-016 | `_LCSC_KEYS` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-017 | `_ELEMENT14_KEYS` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-001 | `_WIRE_GRID_SIZE` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-158 | `_IC_LIB_PREFIX_MAP` | keyword_classification | 58 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-170 | `_IC_VALUE_KEYWORDS` | unknown | 45 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-186 | `_IC_DESC_KEYWORDS` | unknown | 44 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-003 | `target_types` | keyword_classification | 4 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-004 | `pin_entry` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-187 | `analyze_ic_pinouts:1578` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-006 | `ic_result` | keyword_classification | 14 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-007 | `_LEGACY_PIN_TYPE_MAP` | standard | 11 | verified | 0.6 | 0.0 | **low** (0.0) |
| CONST-008 | `_M` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-009 | `_STANDARD_LIB_PINS` | keyword_classification | 34 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-019 | `sym_def` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-011 | `_MAX_SNAP_DIST` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-192 | `_parse_legacy_single_sheet:2306` | standard | 3 | verified | 0.1 | 0.2 | **low** (0.2) |
| CONST-014 | `ps` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-015 | `output_types` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-193 | `_classify_nets:2814` | keyword_classification | 7 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-194 | `_classify_nets:2816` | keyword_classification | 8 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-195 | `_classify_nets:2818` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-196 | `_classify_nets:2820` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-204 | `_classify_nets:2822` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-205 | `_classify_nets:2824` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-216 | `_classify_nets:2826` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-221 | `_classify_nets:2830` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-222 | `_classify_nets:2834` | keyword_classification | 9 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-223 | `_io_pin_names` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-224 | `_sense_pin_names` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-225 | `_pwr_pin_to_rail` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-226 | `level_translator_keywords` | keyword_classification | 20 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-227 | `level_translator_desc_keywords` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-228 | `_spi_net_kw` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-229 | `_spi_canon` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-230 | `_uart_exclude` | keyword_classification | 23 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-231 | `_detect_uart_buses:3269` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-232 | `_sdio_prefixes` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-233 | `_detect_sdio_buses:3301` | keyword_classification | 10 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-234 | `can_keywords` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-235 | `can_transceiver_kw` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-236 | `_rs485_kw` | keyword_classification | 28 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-237 | `buses` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-243 | `_analyze_bus_protocols:3493` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-244 | `_diff_suffix_pairs` | unknown | 14 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-245 | `outputs` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-248 | `drivers` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-042 | `drivers` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-043 | `_STANDARD_FP_LIBS` | keyword_classification | 35 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-044 | `_GENERIC_TRANSISTOR_PREFIXES` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-045 | `_GENERIC_TYPE_LABELS` | standard | 4 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-046 | `_PIN_LETTER_NAMES` | standard | 6 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-249 | `classify_ground_domains:4195` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-250 | `classify_ground_domains:4197` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-277 | `classify_ground_domains:4199` | keyword_classification | 3 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-278 | `classify_ground_domains:4201` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-051 | `esl_by_pkg` | datasheet_lookup | 8 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-052 | `esr_base_by_pkg` | datasheet_lookup | 8 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-280 | `_is_electrolytic_or_tantalum:4735` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-054 | `cap_entry` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-055 | `rail_result` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-056 | `_iq_estimates_uA` | datasheet_lookup | 16 | verified | 0.9 | 0.0 | **low** (0.0) |
| CONST-120 | `_DERATING_PROFILES` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-283 | `_classify_cap_dielectric:5180` | keyword_classification | 10 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-284 | `_classify_cap_dielectric:5182` | keyword_classification | 3 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-217 | `_CAP_DERATING` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-218 | `_RESISTOR_POWER_RATING` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-219 | `pkg_sizes` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-220 | `entry_result` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-057 | `ic_current_estimates` | datasheet_lookup | 48 | verified | 1.0 | 0.0 | **low** (0.0) |
| CONST-058 | `rail_info` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-059 | `dep_entry` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-285 | `analyze_power_sequencing:5818` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-286 | `analyze_power_sequencing:5820` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-062 | `pg_entry` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-063 | `debug_keywords` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-064 | `key_net_patterns` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-065 | `easy_smd` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-066 | `hard_ic_patterns` | keyword_classification | 4 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-067 | `medium_hard_ic_patterns` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-068 | `medium_ic_patterns` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-069 | `easy_ic_patterns` | keyword_classification | 16 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-070 | `difficulty_counts` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-287 | `_extract_package_info:6188` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-290 | `analyze_usb_compliance:6322` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-073 | `conn_checks` | heuristic_threshold | 4 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-291 | `analyze_usb_compliance:6430` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-075 | `esd_keywords` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-076 | `all_checks` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-077 | `rail_entry` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-078 | `merged_bus` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |

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
| CONST-288 | `DIFF_PAIR_PROTOCOLS` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-289 | `MARKET_STANDARDS` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-153 | `COPPER_RESISTIVITY_OHM_MM` | physics | 1 | verified | 0.1 | 0.0 | **low** (0.0) |

## emc_rules.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-263 | `clock_patterns` | keyword_classification | 18 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-264 | `hs_patterns` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-155 | `suggested` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-382 | `check_missing_decoupling:475` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-383 | `check_connector_filtering:600` | keyword_classification | 10 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-267 | `bands` | unknown | 3 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-268 | `known_freqs` | datasheet_lookup | 21 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-384 | `defaults` | datasheet_lookup | 5 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-385 | `ss_keywords` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-363 | `PROXIMITY_MM` | physics | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-292 | `SAMPLE_INTERVAL` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-293 | `_DC_BIAS_DERATING` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
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
| CONST-106 | `_REGULATOR_VREF` | datasheet_lookup | 65 | verified | 1.0 | 0.2 | **low** (0.2) |
| CONST-107 | `_LOAD_TYPE_KEYWORDS` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-108 | `multipliers` | standard | 11 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-109 | `type_map` | standard | 65 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-328 | `classify_component:388` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-329 | `classify_component:405` | keyword_classification | 6 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-330 | `classify_component:410` | keyword_classification | 6 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-331 | `classify_component:413` | keyword_classification | 3 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-110 | `classify_component:415` | keyword_classification | 8 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-332 | `classify_component:419` | keyword_classification | 3 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-333 | `classify_component:422` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-334 | `classify_component:432` | keyword_classification | 9 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-335 | `classify_component:445` | keyword_classification | 6 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-336 | `classify_component:448` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-337 | `classify_component:468` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-117 | `classify_component:477` | keyword_classification | 6 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-118 | `classify_component:481` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-338 | `classify_component:485` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-339 | `classify_component:521` | keyword_classification | 3 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-123 | `classify_component:523` | keyword_classification | 8 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-340 | `classify_component:527` | keyword_classification | 22 | verified | 0.4 | 0.2 | **low** (0.2) |
| CONST-341 | `classify_component:541` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-342 | `classify_component:543` | keyword_classification | 10 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-121 | `_ic_lib_prefixes` | keyword_classification | 19 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-361 | `classify_component:589` | keyword_classification | 8 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-362 | `classify_component:608` | keyword_classification | 6 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-188 | `_CAP_PKG_RE` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-189 | `_CAP_PKG_EIA_RE` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-184 | `_CAP_ESR_TABLE` | unknown | 16 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-190 | `_CAP_ESL` | datasheet_lookup | 7 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-191 | `eia_to_imperial` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |

## signal_detectors.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-124 | `divider` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-125 | `rc_entry` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-126 | `lc_entry` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-364 | `detect_crystal_circuits:697` | keyword_classification | 3 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-127 | `xtal_entry` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-128 | `_osc_keywords` | keyword_classification | 15 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-129 | `_osc_exclude` | keyword_classification | 16 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-130 | `_xtal_pin_re` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-131 | `_SENSE_PIN_PREFIXES` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-132 | `_SENSE_IC_KEYWORDS` | keyword_classification | 31 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-238 | `_SENSE_IC_EXCLUDE` | keyword_classification | 30 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-133 | `_integrated_csa_pins` | keyword_classification | 20 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-134 | `_non_reg_exclude` | keyword_classification | 25 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-239 | `_kw_pmic` | keyword_classification | 18 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-135 | `reg_lib_keywords` | keyword_classification | 52 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-365 | `detect_power_regulators:1304` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-137 | `_rf_exclude` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-138 | `_power_mux_exclude` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-139 | `reg_info` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-140 | `_switching_kw` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-141 | `inverting_kw` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-366 | `detect_power_regulators:1521` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-143 | `_ldo_pin_names` | keyword_classification | 14 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-242 | `_non_reg_ic_keywords` | keyword_classification | 22 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-144 | `protection_types` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-145 | `tvs_keywords` | keyword_classification | 15 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-146 | `esd_ic_keywords` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-147 | `opamp_lib_keywords` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-148 | `opamp_value_keywords` | keyword_classification | 27 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-367 | `detect_opamp_circuits:1892` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-368 | `detect_opamp_circuits:2169` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-369 | `detect_opamp_circuits:2171` | keyword_classification | 6 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-370 | `detect_opamp_circuits:2184` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-371 | `detect_transistor_circuits:2349` | keyword_classification | 6 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-372 | `detect_transistor_circuits:2354` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-246 | `snubber_data` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-152 | `source_sense` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-247 | `_jfet_kw` | keyword_classification | 20 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-373 | `postfilter_vd_and_dedup:2606` | keyword_classification | 3 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-154 | `iso_keywords` | keyword_classification | 19 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-374 | `detect_isolation_barriers:2914` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-156 | `eth_phy_keywords` | keyword_classification | 21 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-157 | `magnetics_keywords` | keyword_classification | 9 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-375 | `detect_ethernet_interfaces:2965` | keyword_classification | 10 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-159 | `_eth_tx_rx_re` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-160 | `_eth_net_re` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-161 | `_bridge_kw` | keyword_classification | 22 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-162 | `_hdmi_conn_kw` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-163 | `memory_keywords` | keyword_classification | 30 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-164 | `processor_keywords` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-251 | `RF_IC_BANDS` | keyword_classification | 16 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-252 | `RF_ROLE_GAIN_DB` | datasheet_lookup | 10 | verified | 0.7 | 0.1 | **low** (0.1) |
| CONST-165 | `rf_switch_keywords` | keyword_classification | 16 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-166 | `rf_mixer_keywords` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-167 | `rf_amp_keywords` | keyword_classification | 19 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-168 | `rf_transceiver_keywords` | keyword_classification | 19 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-169 | `rf_filter_keywords` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-253 | `rf_attenuator_keywords` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-254 | `rf_coupler_keywords` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-255 | `rf_power_detector_keywords` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-256 | `rf_freq_multiplier_keywords` | standard | 3 | verified | 0.1 | 0.1 | **low** (0.1) |
| CONST-376 | `detect_rf_chains:3348` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-171 | `_ant_keywords` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-172 | `_ant_lib_keywords` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-377 | `detect_rf_matching:3561` | keyword_classification | 3 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-259 | `_rf_keywords` | keyword_classification | 29 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-173 | `bms_ic_keywords` | keyword_classification | 15 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-378 | `detect_bms_systems:3736` | keyword_classification | 9 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-174 | `power_path_keywords` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-379 | `detect_design_observations:3911` | keyword_classification | 4 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-175 | `obs` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-380 | `detect_design_observations:4032` | keyword_classification | 5 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-177 | `addr_keywords` | keyword_classification | 13 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-381 | `_get_protocol:4112` | keyword_classification | 3 | verified | 0.3 | 0.2 | **low** (0.2) |
| CONST-179 | `din_names` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-180 | `dout_names` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |

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

