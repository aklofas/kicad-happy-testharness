# Constants Registry

*Auto-generated from `constants_registry.json` — do not edit manually.*

**Last scan:** 2026-10-23T22:24:25.961885+00:00

## Summary

| Metric | Count |
|--------|-------|
| Total constants | 722 |
| Verified | 229 |
| Unverified | 493 |
| Stale (changed since verification) | 0 |
| Critical risk | 5 |
| High risk | 7 |

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
| CONST-188 | `check_missing_decoupling:628` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-189 | `check_connector_filtering:797` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-267 | `bands` | unknown | 3 | verified | 0.0 | 0.0 | **low** (0.0) |
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

## skills/kicad/scripts/analyze_thermal.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-382 | `DEFAULT_AMBIENT_C` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-383 | `DEFAULT_TJ_MAX_C` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-386 | `DEFAULT_RTHETA_JA` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-387 | `MIN_PDISS_W` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-391 | `SEVERITY_WEIGHTS` | datasheet_lookup | 3 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-392 | `MAX_FINDINGS_PER_RULE` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-393 | `SWITCHING_EFFICIENCY` | datasheet_lookup | 4 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-394 | `PACKAGE_THERMAL_RESISTANCE` | unknown | 38 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-190 | `_check_thermal_proximity:686` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-397 | `sev_order` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-398 | `config` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-399 | `counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |

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
| CONST-191 | `check_plane_splits:767` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
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
| CONST-471 | `iso_keywords` | keyword_classification | 19 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-165 | `detect_isolation_barriers:313` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-474 | `detect_isolation_barriers:345` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-166 | `detect_isolation_barriers:347` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-475 | `eth_phy_keywords` | keyword_classification | 21 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-476 | `magnetics_keywords` | keyword_classification | 9 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-167 | `detect_ethernet_interfaces:437` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-478 | `_eth_tx_rx_re` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-479 | `_eth_net_re` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-480 | `bob_smith` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-481 | `_bridge_kw` | keyword_classification | 22 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-482 | `_hdmi_conn_kw` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-483 | `_tmds_pin_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-484 | `_tmds_net_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-485 | `_lvds_keywords` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-486 | `_serializer_hints` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-487 | `_deserializer_hints` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-488 | `memory_keywords` | keyword_classification | 30 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-489 | `processor_keywords` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-490 | `RF_IC_BANDS` | keyword_classification | 16 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-491 | `RF_ROLE_GAIN_DB` | datasheet_lookup | 10 | verified | 0.7 | 0.1 | **low** (0.1) |
| CONST-492 | `rf_switch_keywords` | keyword_classification | 16 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-493 | `rf_mixer_keywords` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-494 | `rf_amp_keywords` | keyword_classification | 19 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-495 | `rf_transceiver_keywords` | keyword_classification | 19 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-496 | `rf_filter_keywords` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-497 | `rf_attenuator_keywords` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-498 | `rf_coupler_keywords` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-499 | `rf_power_detector_keywords` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-500 | `rf_freq_multiplier_keywords` | standard | 3 | verified | 0.1 | 0.1 | **low** (0.1) |
| CONST-168 | `detect_rf_chains:1096` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-502 | `_RF_REFERENCE_DESIGNS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-503 | `_ant_keywords` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-504 | `_ant_lib_keywords` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-169 | `detect_rf_matching:1408` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-506 | `_rf_keywords` | keyword_classification | 29 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-507 | `bms_ic_keywords` | keyword_classification | 15 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-171 | `detect_bms_systems:1610` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-509 | `power_path_keywords` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
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
| CONST-527 | `addr_keywords` | keyword_classification | 13 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-174 | `_get_protocol:2270` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-529 | `din_names` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-530 | `dout_names` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
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
| CONST-587 | `_I2S_PINS` | keyword_classification | 13 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-588 | `_AUDIO_OUTPUT_PINS` | keyword_classification | 20 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-589 | `_AUDIO_INPUT_PINS` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-590 | `_CLASS_D_KEYWORDS` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-222 | `detect_audio_circuits:4432` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
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
| CONST-233 | `detect_rtc_circuits:4716` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
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
| CONST-285 | `suggest_certifications:5607` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
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
| CONST-586 | `_AUDIO_CODEC_KEYWORDS` | keyword_classification | 27 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-629 | `_HP_JACK_KEYWORDS` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-630 | `_HP_DET_PIN_NAMES` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/export_issues.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-631 | `_SEV_RANK` | datasheet_lookup | 7 | verified | 0.7 | 0.0 | **low** (0.0) |
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
| CONST-286 | `NON_COMPONENT_TYPES` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-193 | `type_map` | standard | 65 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-302 | `classify_component:91` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-196 | `_lib_type_overrides` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-308 | `classify_component:119` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-205 | `_osc_internal_phrases` | keyword_classification | 4 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-216 | `_clock_pin_names` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-243 | `classify_component:141` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-250 | `classify_component:146` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-309 | `classify_component:149` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-318 | `classify_component:151` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-319 | `classify_component:155` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-323 | `classify_component:158` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-324 | `classify_component:168` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-325 | `classify_component:181` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-326 | `classify_component:184` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-327 | `classify_component:210` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-328 | `classify_component:221` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-329 | `classify_component:225` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-334 | `classify_component:229` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-335 | `classify_component:233` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-336 | `classify_component:271` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-340 | `classify_component:273` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-341 | `classify_component:277` | keyword_classification | 22 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-342 | `classify_component:291` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-343 | `classify_component:293` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-305 | `_ic_lib_prefixes` | keyword_classification | 20 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-345 | `classify_component:340` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-346 | `classify_component:364` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-348 | `classify_ic_function:389` | keyword_classification | 22 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-349 | `classify_ic_function:397` | keyword_classification | 14 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-350 | `classify_ic_function:403` | keyword_classification | 14 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-435 | `classify_ic_function:409` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-436 | `classify_ic_function:414` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-351 | `classify_ic_function:419` | keyword_classification | 14 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-352 | `classify_ic_function:425` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-441 | `classify_ic_function:431` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-353 | `classify_ic_function:436` | keyword_classification | 11 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-354 | `classify_ic_function:442` | keyword_classification | 24 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-366 | `classify_ic_function:450` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-367 | `classify_ic_function:456` | keyword_classification | 27 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-433 | `classify_ic_function:466` | keyword_classification | 22 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-437 | `classify_ic_function:475` | keyword_classification | 18 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-472 | `classify_connector:495` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-473 | `classify_connector:497` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-477 | `classify_connector:504` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-501 | `classify_connector:518` | keyword_classification | 26 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-454 | `classify_connector:525` | keyword_classification | 12 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-505 | `classify_connector:530` | keyword_classification | 12 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-508 | `classify_connector:534` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |

## skills/kicad/scripts/kicad_core/cli.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-517 | `STAGES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-518 | `AUDIENCES` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

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
| CONST-078 | `_UUID_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |

## skills/kicad/scripts/kicad_core/netquery.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-359 | `_BRIDGE_KINDS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-360 | `_ZERO_OHM_SPELLINGS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/kicad_core/parts.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-833 | `_REGULATOR_VREF` | datasheet_lookup | 114 | verified | 1.0 | 0.0 | **low** (0.0) |
| CONST-834 | `_LOAD_TYPE_KEYWORDS` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-835 | `_KNOWN_FREQS` | datasheet_lookup | 105 | unverified | 0.8 | 0.0 | **low** (0.0) |
| CONST-384 | `defaults` | datasheet_lookup | 5 | verified | 0.7 | 0.0 | **low** (0.0) |

## skills/kicad/scripts/kicad_core/passives.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-836 | `_CAP_PKG_RE` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-837 | `_CAP_PKG_EIA_RE` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-838 | `_CAP_ESR_TABLE` | unknown | 16 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-839 | `_CAP_ESL` | datasheet_lookup | 7 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-840 | `eia_to_imperial` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-841 | `_DC_BIAS_DERATING` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-842 | `_SHIELDED_PATTERNS` | keyword_classification | 15 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-843 | `_SEMI_SHIELDED_PATTERNS` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-844 | `_UNSHIELDED_PATTERNS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/kicad_core/render.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-528 | `SEVERITY_ALIASES` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/kicad_core/sexp.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-361 | `_BRACE_ESCAPES` | keyword_classification | 14 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-362 | `_BRACE_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |

## skills/kicad/scripts/kicad_core/values.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-845 | `COORD_EPSILON` | physics | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-846 | `_MIL_MM` | physics | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-847 | `multipliers` | standard | 11 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-848 | `_E_SERIES` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-849 | `_RATED_V_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |

## skills/kicad/scripts/lifecycle_audit.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-706 | `_TEMP_PRESETS` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-707 | `_LIFECYCLE_STATUS_RULES` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-708 | `_STATUS_NORMALIZE` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-547 | `_EOL_STATUSES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-709 | `_GENERIC_VALUE_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-710 | `_SKIP_TYPES` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-711 | `api_fns` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-712 | `temp_data` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
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

## skills/kicad/scripts/pcb/assembly.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-211 | `_ESD_TVS_PREFIXES` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-320 | `_RF_MODULE_KEYWORDS` | keyword_classification | 20 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-321 | `_RF_LIB_KEYWORDS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-330 | `_EDGE_MOUNT_LIBRARY_KEYWORDS` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-097 | `risk_order` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-014 | `analyze_fiducials:745` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-344 | `finding` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |

## skills/kicad/scripts/pcb/connectivity.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-727 | `node_a` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-728 | `node_b` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/pcb/copper.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-086 | `type_counts` | standard | 4 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-087 | `type_sizes` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-088 | `annular_ring` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-022 | `analyze_vias:412` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-090 | `current_facts` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-098 | `adequacy_order` | heuristic_threshold | 4 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-333 | `_PASSIVE_REF_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-300 | `_gnd_keywords` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-023 | `analyze_copper_presence:1160` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-104 | `analyze_copper_presence:1161` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |

## skills/kicad/scripts/pcb/dfm.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-331 | `MIN_REAL_DRILL_MM` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-095 | `JLCPCB_LIMITS_STANDARD` | standard | 7 | verified | 0.1 | 0.3 | **low** (0.3) |
| CONST-096 | `JLCPCB_LIMITS_ADVANCED` | standard | 4 | verified | 0.1 | 0.2 | **low** (0.2) |
| CONST-266 | `IPC_CLASS_LIMITS` | standard | 3 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-560 | `constraints` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-299 | `checks` | unknown | 3 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-332 | `v` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/pcb/pipeline.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-314 | `MAX_TESTED_FORMAT_VERSION` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |

## skills/kicad/scripts/pcb/presentation.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-105 | `_FINDING_LIST_KEYS` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-106 | `sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |

## skills/kicad/scripts/pcb/reader.py

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
| CONST-214 | `rev_pattern` | standard | 1 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-107 | `extract_silkscreen:1261` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-108 | `extract_silkscreen:1263` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-109 | `extract_silkscreen:1271` | keyword_classification | 11 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-195 | `_fab_notes_checklist` | heuristic_threshold | 6 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-110 | `extract_silkscreen:1341` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-121 | `extract_silkscreen:1344` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-136 | `extract_silkscreen:1346` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-149 | `extract_silkscreen:1348` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-221 | `_silk_checks` | heuristic_threshold | 5 | unverified | 0.4 | 0.0 | **medium** (0.4) |

## skills/kicad/scripts/pcb/routing.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-213 | `SNAP` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-215 | `SAMPLE_INTERVAL` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-315 | `ANTIPAD_CLEARANCE` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-316 | `ANTIPAD_GRID` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-317 | `sample` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-089 | `seg_entry` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-184 | `analyze_ground_domains:816` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |

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
| CONST-018 | `resolve_design_intent:392` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-021 | `resolve_design_intent:483` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-740 | `defaults` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-741 | `SEVERITY_WEIGHTS` | datasheet_lookup | 5 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-742 | `CONFIDENCE_WEIGHTS` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-743 | `RESPIN_CATEGORIES` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-744 | `BRINGUP_CATEGORIES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-745 | `MANUFACTURING_CATEGORIES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-746 | `BUCKET_BOOSTS` | datasheet_lookup | 3 | verified | 0.7 | 0.1 | **low** (0.1) |
| CONST-747 | `buckets` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/run_id.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-748 | `_HEX_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |

## skills/kicad/scripts/schema_codec.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-749 | `out` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/schematic/audits.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-042 | `drivers` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-043 | `_STANDARD_FP_LIBS` | keyword_classification | 35 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-364 | `_DS_DIR_NAMES` | keyword_classification | 4 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-044 | `_GENERIC_TRANSISTOR_PREFIXES` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-045 | `_GENERIC_TYPE_LABELS` | standard | 4 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-046 | `_PIN_LETTER_NAMES` | standard | 6 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-584 | `classify_ground_domains:833` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-591 | `classify_ground_domains:835` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-602 | `classify_ground_domains:837` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-616 | `classify_ground_domains:839` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |

## skills/kicad/scripts/schematic/connectivity.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-400 | `_VECTOR_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-401 | `_GROUP_RE` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-402 | `_MAX_DEPTH` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-403 | `_EPSILON` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-001 | `_WIRE_GRID_SIZE` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-002 | `_NET_NAME_PRIORITY` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-339 | `_INTERNAL_LABEL_KEYS` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/schematic/hierarchy.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-122 | `merged_bus` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/schematic/ic_analysis.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-158 | `_IC_LIB_PREFIX_MAP` | keyword_classification | 58 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-170 | `_IC_VALUE_KEYWORDS` | unknown | 45 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-186 | `_IC_DESC_KEYWORDS` | unknown | 44 | verified | 0.1 | 0.0 | **low** (0.0) |
| CONST-003 | `target_types` | keyword_classification | 4 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-004 | `pin_entry` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-651 | `analyze_ic_pinouts:399` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-006 | `ic_result` | keyword_classification | 14 | verified | 0.3 | 0.0 | **low** (0.0) |

## skills/kicad/scripts/schematic/legacy_reader.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-007 | `_LEGACY_PIN_TYPE_MAP` | standard | 11 | verified | 0.6 | 0.0 | **low** (0.0) |
| CONST-008 | `_M` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-009 | `_STANDARD_LIB_PINS` | keyword_classification | 34 | verified | 0.5 | 0.0 | **low** (0.0) |
| CONST-019 | `sym_def` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-020 | `resolution_info` | keyword_classification | 5 | unverified | 0.3 | 0.3 | **medium** (0.3) |
| CONST-011 | `_MAX_SNAP_DIST` | heuristic_threshold | 1 | verified | 0.4 | 0.1 | **low** (0.1) |
| CONST-036 | `_parse_legacy_single_sheet:653` | standard | 3 | unverified | 0.1 | 0.2 | **low** (0.2) |

## skills/kicad/scripts/schematic/net_analysis.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-024 | `_SIGNAL_PIN_TYPES` | standard | 7 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-025 | `_SKIP_PIN_TYPES` | standard | 4 | unverified | 0.1 | 0.1 | **low** (0.1) |
| CONST-015 | `output_types` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-037 | `_classify_nets:203` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-038 | `_classify_nets:205` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-040 | `_classify_nets:207` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-041 | `_classify_nets:209` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-072 | `_classify_nets:211` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-074 | `_classify_nets:213` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-085 | `_classify_nets:215` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-091 | `_classify_nets:219` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-092 | `_classify_nets:223` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-223 | `_io_pin_names` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-224 | `_sense_pin_names` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-225 | `_pwr_pin_to_rail` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-226 | `level_translator_keywords` | keyword_classification | 20 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-227 | `level_translator_desc_keywords` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-030 | `_I2C_MODES` | unknown | 4 | unverified | 0.0 | 0.0 | **low** (0.0) |
| CONST-228 | `_spi_net_kw` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-229 | `_spi_canon` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-230 | `_uart_exclude` | keyword_classification | 23 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-093 | `_detect_uart_buses:793` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-032 | `_tx_pins` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-034 | `_rx_pins` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-094 | `_detect_uart_buses:813` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-111 | `_detect_uart_buses:814` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-232 | `_sdio_prefixes` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-112 | `_detect_sdio_buses:867` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-234 | `can_keywords` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-235 | `can_transceiver_kw` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-236 | `_rs485_kw` | keyword_classification | 28 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-237 | `buses` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-113 | `_analyze_bus_protocols:1090` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-244 | `_diff_suffix_pairs` | unknown | 14 | verified | 0.0 | 0.0 | **low** (0.0) |
| CONST-245 | `outputs` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-248 | `drivers` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |

## skills/kicad/scripts/schematic/pipeline.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-337 | `MAX_TESTED_FORMAT_VERSION` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-117 | `ps` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-118 | `_sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |

## skills/kicad/scripts/schematic/presentation.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-119 | `_IC_TYPES` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-123 | `sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-142 | `sev_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-356 | `_pin_source_counts` | heuristic_threshold | 4 | unverified | 0.4 | 0.1 | **medium** (0.4) |

## skills/kicad/scripts/schematic/reader.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-010 | `_MANUFACTURER_KEYS` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-013 | `_MOUSER_KEYS` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-016 | `_LCSC_KEYS` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-017 | `_ELEMENT14_KEYS` | keyword_classification | 11 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-338 | `_ANGLE_TRANSFORM` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## skills/kicad/scripts/schematic/system_analyses.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-051 | `esl_by_pkg` | datasheet_lookup | 8 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-052 | `esr_base_by_pkg` | datasheet_lookup | 8 | verified | 0.8 | 0.0 | **low** (0.0) |
| CONST-357 | `_is_electrolytic_or_tantalum:75` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-054 | `cap_entry` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-055 | `rail_result` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-371 | `SLEEP_PULL_MIN_OHM` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-372 | `_battery_rail_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-056 | `_iq_estimates_uA` | datasheet_lookup | 16 | verified | 0.9 | 0.0 | **low** (0.0) |
| CONST-120 | `_DERATING_PROFILES` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-358 | `_classify_cap_dielectric:734` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-438 | `_classify_cap_dielectric:736` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-217 | `_CAP_DERATING` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-218 | `_RESISTOR_POWER_RATING` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-219 | `pkg_sizes` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-220 | `entry_result` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-179 | `_rs232_keywords` | keyword_classification | 13 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-057 | `ic_current_estimates` | datasheet_lookup | 48 | verified | 1.0 | 0.0 | **low** (0.0) |
| CONST-058 | `rail_info` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-059 | `dep_entry` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-461 | `analyze_power_sequencing:1623` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-462 | `analyze_power_sequencing:1625` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-062 | `pg_entry` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-063 | `debug_keywords` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-064 | `key_net_patterns` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-065 | `easy_smd` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-066 | `hard_ic_patterns` | keyword_classification | 4 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-067 | `medium_hard_ic_patterns` | keyword_classification | 7 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-068 | `medium_ic_patterns` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-069 | `easy_ic_patterns` | keyword_classification | 16 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-070 | `difficulty_counts` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-464 | `_extract_package_info:1993` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-465 | `analyze_usb_compliance:2132` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-073 | `conn_checks` | heuristic_threshold | 4 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-114 | `_PD_CONTROLLER_KEYWORDS` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-115 | `r_info` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-116 | `cc_detail` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-075 | `esd_keywords` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-466 | `analyze_usb_compliance:2364` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-381 | `_uc_specs` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-076 | `all_checks` | heuristic_threshold | 3 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-077 | `rail_entry` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |

## skills/kicad/scripts/signal_detectors.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-652 | `_BOOTSTRAP_PIN_TOKENS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-653 | `_VOUT_PIN_NAMES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-434 | `_CRYSTAL_DEFAULT_CL` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-654 | `_classify_divider_purpose:198` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-655 | `_classify_divider_purpose:204` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-656 | `_classify_divider_purpose:207` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-657 | `_classify_divider_purpose:210` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-124 | `divider` | keyword_classification | 6 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-125 | `rc_entry` | keyword_classification | 8 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-126 | `lc_entry` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-658 | `detect_crystal_circuits:907` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
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
| CONST-659 | `_screen_regulator_candidate:1715` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-137 | `_rf_exclude` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-138 | `_power_mux_exclude` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-660 | `_screen_regulator_candidate:1733` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-442 | `_opamp_adc_exclude` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-661 | `reg_info` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-140 | `_switching_kw` | keyword_classification | 12 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-373 | `_charge_pump_kw` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-662 | `_build_regulator_record:1845` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-141 | `inverting_kw` | keyword_classification | 5 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-663 | `_build_regulator_record:2010` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-664 | `cap_entry` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-143 | `_ldo_pin_names` | keyword_classification | 14 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-242 | `_non_reg_ic_keywords` | keyword_classification | 22 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-144 | `protection_types` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-145 | `tvs_keywords` | keyword_classification | 15 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-146 | `esd_ic_keywords` | keyword_classification | 17 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-147 | `opamp_lib_keywords` | keyword_classification | 3 | verified | 0.3 | 0.1 | **low** (0.1) |
| CONST-148 | `opamp_value_keywords` | keyword_classification | 25 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-665 | `detect_opamp_circuits:2595` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-666 | `detect_opamp_circuits:2601` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-667 | `detect_opamp_circuits:2918` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-668 | `detect_opamp_circuits:2920` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-669 | `detect_opamp_circuits:2933` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-670 | `detect_transistor_circuits:3116` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-671 | `detect_transistor_circuits:3119` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-672 | `detect_transistor_circuits:3122` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-673 | `detect_transistor_circuits:3126` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-246 | `snubber_data` | keyword_classification | 4 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-152 | `source_sense` | keyword_classification | 3 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-247 | `_jfet_kw` | keyword_classification | 20 | verified | 0.4 | 0.0 | **low** (0.0) |
| CONST-674 | `postfilter_vd_and_dedup:3407` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-675 | `detect_design_observations:3653` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-175 | `obs` | keyword_classification | 10 | verified | 0.3 | 0.0 | **low** (0.0) |
| CONST-676 | `detect_design_observations:3826` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-769 | `SHORTABLE` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-770 | `MASS_SHORT_THRESHOLD` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-771 | `_MODULE_INTERNAL_RAIL_PATTERNS` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-458 | `MAX_HOPS` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |

## skills/kicad/scripts/summarize_findings.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-772 | `_SEV_RANK` | datasheet_lookup | 6 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-773 | `payload` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-774 | `severity_totals` | datasheet_lookup | 3 | verified | 0.7 | 0.0 | **low** (0.0) |

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
| CONST-677 | `validate_pullups:307` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-783 | `_VOLTAGE_THRESHOLDS` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-784 | `_EN_PIN_PATTERNS` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-678 | `validate_voltage_levels:597` | keyword_classification | 18 | unverified | 0.4 | 0.2 | **medium** (0.4) |
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
| CONST-679 | `_PS_PG_PIN_NAMES` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
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
| CONST-822 | `mult` | datasheet_lookup | 4 | verified | 0.7 | 0.0 | **low** (0.0) |
| CONST-823 | `mult` | datasheet_lookup | 3 | verified | 0.7 | 0.0 | **low** (0.0) |

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

