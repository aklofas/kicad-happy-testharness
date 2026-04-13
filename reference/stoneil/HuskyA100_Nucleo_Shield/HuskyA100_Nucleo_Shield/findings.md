# Findings: stoneil/HuskyA100_Nucleo_Shield / HuskyA100_Nucleo_Shield

## FND-00000605: Component count, connector types, and BOM accurate for a connector-heavy Nucleo shield; Decoupling analysis empty — C1–C8 on 3.3V rail not detected because 3.3V uses global labels, not power symbol...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HuskyA100_Nucleo_Shield.sch.json
- **Created**: 2026-03-23

### Correct
- All 18 components correctly identified: 8 connectors (CN7–CN10, J1–J4), 8 capacitors (C1–C8), 1 LED, 1 resistor. The 106 nets are plausible given the four large Nucleo headers (CN7–CN10 total 100 pins). No false positives in component classification.

### Incorrect
(none)

### Missed
- The 3.3V net (from global_label text) has C1–C8 capacitors (4× 10 nF + 4× 100 nF) connected between it and GND, but decoupling_analysis returns []. The analyzer only identifies power rails from KiCad power symbols (PWR_FLAG, +3V3 etc.), not from global labels named '3.3V' or '5V'. Similarly, power_rails only lists 'GND' (from a power symbol), not '3.3V' or '5V'. This is a systematic gap for label-based power distribution (common in KiCad 5 legacy designs).
  (signal_analysis)
- D1 (LED, 5V-powered via global label) has R1 (66.5 Ω) as a series current-limiting resistor to GND. This is a textbook LED circuit that should appear in design_observations. Instead, subcircuits is empty and design_observations is empty. The absence of power_symbols (no PWR_FLAG, no power ICs) prevents the analysis engine from anchoring the topology.
  (signal_analysis)

### Suggestions
(none)

---
