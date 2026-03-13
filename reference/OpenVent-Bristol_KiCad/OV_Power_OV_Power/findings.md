# Findings: OpenVent-Bristol_KiCad / OV_Power_OV_Power

## FND-00000023: Legacy parse_legacy_schematic() does not call analyze_signal_paths() — 8+ circuit categories missed including LT1936 buck, LT3796 charger, LT6106 current sense, 5 voltage dividers, VNH5019 H-bridge, LTC4416 power path controller

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: OV_Power.sch
- **Created**: 2026-03-13

### Correct
- 101 components correctly extracted across 3 hierarchical sheets
- 9 subcircuits detected, but neighbor_components inconsistent

### Incorrect
(none)

### Missed
- signal_analysis key entirely absent from legacy output. parse_legacy_schematic() returns at line 1960 without calling analyze_signal_paths() or any Tier 1-3 analysis.
  (signal_analysis)

### Suggestions
- Add analyze_signal_paths() and downstream analysis calls to parse_legacy_schematic() before the return dict — all required inputs (components, nets, lib_symbols, pin_net) are already available

---

## FND-00000027: 20 #GND power symbols classified as type "other" and included in components/BOM. Legacy parser checks for #PWR and #FLG prefixes but not #GND.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: OV_Power_OV_Power.sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- #GND symbols (20 of them) should be power_symbol type, not "other". Inflates component count from 81 to 101.
  (components)

### Missed
(none)

### Suggestions
- Add #GND to the legacy power symbol prefix list alongside #PWR and #FLG

---
