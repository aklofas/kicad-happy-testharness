# Findings: Modular-Synth-Hardware / VCF_VCF

## FND-00000257: Analog VCF module with transistor ladder (133 components). Four phantom unit=null op-amp entries from TL072 power units. Integrator misclassified as compensator. GND-base transistors with false driver lists. Transistor load_type='connector' via GND traversal.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: VCF_VCF.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 10-transistor ladder (Q101-Q110) correctly typed as BJT transistors
- Voltage dividers for CV input networks accurately detected

### Incorrect
- Four phantom opamp entries with unit=null generated from TL072 power unit (unit 3) placements — U101, U104, U105, U106 each get a spurious entry with cross-contaminated nets from different units
  (signal_analysis.opamp_circuits)
- U106 unit 2 misclassified as 'compensator' — R201 (4.7M) connects from +12V to inverting input as bias, not feedback; C201 (1n) is the sole feedback element (integrator)
  (signal_analysis.opamp_circuits)
- Q302, Q402, Q201 (NPN, base=GND) each accumulate 22 false base_resistors and 5 false base_driver_ics from GND net traversal
  (signal_analysis.transistor_circuits)
- Q303, Q403 load_type='connector' — GND-collector traversal finds J101 power connector as load instead of emitter-side resistors
  (signal_analysis.transistor_circuits)
- False parallel capacitor grouping: C301+C401 reported as 20uF parallel but they connect to different exponential converter branches (different pin2 nodes)
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- Filter out power-unit-only symbol placements (units with only VCC/GND pins) from opamp_circuits detection
- Skip power/ground nets when determining transistor load_type and base drivers

---
