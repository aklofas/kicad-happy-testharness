# Constants Registry

*Auto-generated from `constants_registry.json` — do not edit manually.*

**Last scan:** 2026-03-15T21:01:59.958072+00:00

## Summary

| Metric | Count |
|--------|-------|
| Total constants | 180 |
| Verified | 0 |
| Unverified | 180 |
| Stale (changed since verification) | 0 |
| Critical risk | 6 |
| High risk | 7 |

## analyze_gerbers.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-099 | `patterns` | keyword_classification | 22 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-100 | `ext_map` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-101 | `power_keywords` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-102 | `power_keywords` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-103 | `_GERBER_EXTENSIONS` | standard | 17 | unverified | 0.1 | 0.0 | **low** (0.1) |

## analyze_pcb.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-079 | `_float_keys` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-080 | `pad_info` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-081 | `fp_entry` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-082 | `via_info` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-083 | `zone_info` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-084 | `bbox` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-085 | `analyze_ground_domains:1405` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-086 | `type_counts` | standard | 3 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-087 | `type_sizes` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-088 | `annular_ring` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-089 | `analyze_vias:1942` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-090 | `current_facts` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-091 | `extract_silkscreen:2218` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-092 | `extract_silkscreen:2267` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-093 | `extract_silkscreen:2269` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-094 | `extract_silkscreen:2277` | keyword_classification | 11 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-095 | `LIMITS_STD` | standard | 7 | unverified | 0.1 | 0.3 | **low** (0.3) |
| CONST-096 | `LIMITS_ADV` | standard | 4 | unverified | 0.1 | 0.2 | **low** (0.2) |
| CONST-097 | `risk_order` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-098 | `adequacy_order` | heuristic_threshold | 4 | unverified | 0.4 | 0.1 | **medium** (0.4) |

## analyze_schematic.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-001 | `_WIRE_GRID_SIZE` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-002 | `_LIB_PREFIX_MAP` | keyword_classification | 58 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-003 | `target_types` | keyword_classification | 4 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-004 | `pin_entry` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-005 | `analyze_ic_pinouts:1507` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-006 | `ic_result` | keyword_classification | 14 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-007 | `_LEGACY_PIN_TYPE_MAP` | standard | 11 | unverified | 0.6 | 0.0 | **high** (0.6) |
| CONST-008 | `_M` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-009 | `_STANDARD_LIB_PINS` | keyword_classification | 34 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-010 | `MIL_TO_MM` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-011 | `_MAX_SNAP_DIST` | heuristic_threshold | 1 | unverified | 0.4 | 0.1 | **medium** (0.4) |
| CONST-012 | `MIL_TO_MM` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-013 | `_parse_legacy_single_sheet:2197` | standard | 3 | unverified | 0.1 | 0.2 | **low** (0.2) |
| CONST-014 | `ps` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-015 | `output_types` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-016 | `analyze_design_rules:2722` | keyword_classification | 7 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-017 | `analyze_design_rules:2724` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-018 | `analyze_design_rules:2726` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-019 | `analyze_design_rules:2728` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-020 | `analyze_design_rules:2730` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-021 | `analyze_design_rules:2732` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-022 | `analyze_design_rules:2734` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-023 | `analyze_design_rules:2738` | keyword_classification | 9 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-024 | `_io_pin_names` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-025 | `_sense_pin_names` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-026 | `_pwr_pin_to_rail` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-027 | `level_translator_keywords` | keyword_classification | 20 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-028 | `level_translator_desc_keywords` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-029 | `buses` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-030 | `_spi_net_kw` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-031 | `_spi_canon` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-032 | `_uart_exclude` | keyword_classification | 23 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-033 | `analyze_design_rules:3109` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-034 | `_sdio_prefixes` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-035 | `analyze_design_rules:3134` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-036 | `can_keywords` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-037 | `can_transceiver_kw` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-038 | `_rs485_kw` | keyword_classification | 28 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-039 | `analyze_design_rules:3288` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-040 | `outputs` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-041 | `drivers` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-042 | `drivers` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-043 | `_STANDARD_FP_LIBS` | keyword_classification | 35 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-044 | `_GENERIC_TRANSISTOR_PREFIXES` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-045 | `_GENERIC_TYPE_LABELS` | standard | 4 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-046 | `_PIN_LETTER_NAMES` | standard | 6 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-047 | `classify_ground_domains:3972` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-048 | `classify_ground_domains:3974` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-049 | `classify_ground_domains:3976` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-050 | `classify_ground_domains:3978` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-051 | `esl_by_pkg` | datasheet_lookup | 8 | unverified | 0.8 | 0.0 | **critical** (0.8) |
| CONST-052 | `esr_base_by_pkg` | datasheet_lookup | 8 | unverified | 0.8 | 0.0 | **critical** (0.8) |
| CONST-053 | `_is_electrolytic_or_tantalum:4501` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-054 | `cap_entry` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-055 | `rail_result` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-056 | `_iq_estimates_uA` | datasheet_lookup | 16 | unverified | 0.9 | 0.0 | **critical** (0.9) |
| CONST-057 | `ic_current_estimates` | datasheet_lookup | 48 | unverified | 1.0 | 0.0 | **critical** (1.0) |
| CONST-058 | `rail_info` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-059 | `dep_entry` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-060 | `analyze_power_sequencing:5204` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-061 | `analyze_power_sequencing:5206` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-062 | `pg_entry` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-063 | `debug_keywords` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-064 | `key_net_patterns` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-065 | `easy_smd` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-066 | `hard_ic_patterns` | keyword_classification | 4 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-067 | `medium_hard_ic_patterns` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-068 | `medium_ic_patterns` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-069 | `easy_ic_patterns` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-070 | `difficulty_counts` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-071 | `_extract_package_info:5567` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-072 | `analyze_usb_compliance:5696` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-073 | `conn_checks` | heuristic_threshold | 4 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-074 | `analyze_usb_compliance:5804` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-075 | `esd_keywords` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-076 | `all_checks` | heuristic_threshold | 3 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-077 | `rail_entry` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-078 | `merged_bus` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |

## kicad_utils.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-104 | `COORD_EPSILON` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-105 | `_MIL_MM` | physics | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-106 | `_REGULATOR_VREF` | datasheet_lookup | 92 | unverified | 1.0 | 0.0 | **critical** (1.0) |
| CONST-107 | `_LOAD_TYPE_KEYWORDS` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-108 | `multipliers` | standard | 11 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-109 | `type_map` | standard | 64 | unverified | 0.7 | 0.0 | **critical** (0.7) |
| CONST-110 | `classify_component:324` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-111 | `classify_component:340` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-112 | `classify_component:344` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-113 | `classify_component:348` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-114 | `classify_component:351` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-115 | `classify_component:390` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-116 | `classify_component:394` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-117 | `classify_component:398` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-118 | `classify_component:431` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-119 | `classify_component:435` | keyword_classification | 22 | unverified | 0.4 | 0.2 | **medium** (0.4) |
| CONST-120 | `classify_component:448` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-121 | `_ic_lib_prefixes` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-122 | `classify_component:493` | keyword_classification | 8 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-123 | `classify_component:512` | keyword_classification | 6 | unverified | 0.3 | 0.2 | **medium** (0.3) |

## signal_detectors.py

| ID | Name | Category | # | Status | Impact | Overfit | Risk |
|---|---|---|---|---|---|---|---|
| CONST-124 | `divider` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-125 | `rc_entry` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-126 | `lc_entry` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-127 | `xtal_entry` | keyword_classification | 4 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-128 | `_osc_keywords` | keyword_classification | 15 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-129 | `_osc_exclude` | keyword_classification | 16 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-130 | `_xtal_pin_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-131 | `_SENSE_PIN_PREFIXES` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-132 | `_SENSE_IC_KEYWORDS` | keyword_classification | 31 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-133 | `_integrated_csa_pins` | keyword_classification | 20 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-134 | `_non_reg_exclude` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-135 | `reg_lib_keywords` | keyword_classification | 45 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-136 | `detect_power_regulators:1022` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-137 | `_rf_exclude` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-138 | `_power_mux_exclude` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-139 | `reg_info` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-140 | `_switching_kw` | keyword_classification | 12 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-141 | `inverting_kw` | keyword_classification | 5 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-142 | `detect_power_regulators:1203` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-143 | `_ldo_pin_names` | keyword_classification | 14 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-144 | `protection_types` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-145 | `tvs_keywords` | keyword_classification | 15 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-146 | `esd_ic_keywords` | keyword_classification | 11 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-147 | `opamp_lib_keywords` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-148 | `opamp_value_keywords` | keyword_classification | 25 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-149 | `detect_opamp_circuits:1438` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-150 | `detect_transistor_circuits:1768` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-151 | `detect_transistor_circuits:1773` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-152 | `source_sense` | keyword_classification | 3 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-153 | `postfilter_vd_and_dedup:1985` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-154 | `iso_keywords` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-155 | `detect_isolation_barriers:2278` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-156 | `eth_phy_keywords` | keyword_classification | 21 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-157 | `magnetics_keywords` | keyword_classification | 9 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-158 | `detect_ethernet_interfaces:2329` | keyword_classification | 10 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-159 | `_eth_tx_rx_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-160 | `_eth_net_re` | standard | 1 | unverified | 0.1 | 0.0 | **low** (0.1) |
| CONST-161 | `_bridge_kw` | keyword_classification | 22 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-162 | `_hdmi_conn_kw` | keyword_classification | 3 | unverified | 0.3 | 0.1 | **medium** (0.3) |
| CONST-163 | `memory_keywords` | keyword_classification | 30 | unverified | 0.5 | 0.0 | **high** (0.5) |
| CONST-164 | `processor_keywords` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-165 | `rf_switch_keywords` | keyword_classification | 14 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-166 | `rf_mixer_keywords` | keyword_classification | 8 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-167 | `rf_amp_keywords` | keyword_classification | 17 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-168 | `rf_transceiver_keywords` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-169 | `rf_filter_keywords` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-170 | `detect_rf_chains:2646` | keyword_classification | 4 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-171 | `_ant_keywords` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-172 | `_ant_lib_keywords` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-173 | `bms_ic_keywords` | keyword_classification | 19 | unverified | 0.4 | 0.0 | **medium** (0.4) |
| CONST-174 | `power_path_keywords` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-175 | `obs` | keyword_classification | 10 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-176 | `detect_design_observations:3198` | keyword_classification | 5 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-177 | `addr_keywords` | keyword_classification | 13 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-178 | `_get_protocol:3276` | keyword_classification | 3 | unverified | 0.3 | 0.2 | **medium** (0.3) |
| CONST-179 | `din_names` | keyword_classification | 7 | unverified | 0.3 | 0.0 | **medium** (0.3) |
| CONST-180 | `dout_names` | keyword_classification | 6 | unverified | 0.3 | 0.0 | **medium** (0.3) |

