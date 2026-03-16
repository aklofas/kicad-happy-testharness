# Findings: dc-power-supply / kicad_dc-power-supply

## FND-00000233: DC power supply (129 components). 2 RF matching networks falsely detected (L1 ferrite EMI filter + C12 decoupling misidentified). 5 regulators correct. 10 RC filters detected but many are feedback networks not signal filters.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: dc-power-supply.sch.json
- **Created**: 2026-03-16

### Correct
- 5 regulators correctly detected

### Incorrect
- 2 RF matching networks falsely detected - L1 ferrite bead EMI filter and C12 decoupling capacitor misidentified as RF matching
  (signal_analysis.rf_matching)
- RC filter count includes feedback networks that are not signal filters
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- Distinguish ferrite EMI filters from RF matching networks
- Distinguish feedback networks from signal RC filters

---
