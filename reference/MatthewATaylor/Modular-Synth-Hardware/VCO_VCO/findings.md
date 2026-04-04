# Findings: Modular-Synth-Hardware / VCO_VCO

## FND-00000256: Analog VCO module (151 components). Sawtooth integrator core misclassified as compensator. GND-base transistors in exponential converter accumulate false base_resistor/driver lists from GND net traversal.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: VCO_VCO.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- CA3080 OTA correctly identified
- Comparator/open-loop op-amp classifications appropriate for VCO core

### Incorrect
- U101 unit 2 misclassified as 'compensator' — R202 (6.8k) is the input resistor from gain pot, not feedback; C202 (1n) alone is the feedback element making this an integrator
  (signal_analysis.opamp_circuits)
- Q302 and Q201 (2N3906 PNP, base=GND) each accumulate 16 false base_resistors and 12 false base_driver_ics from traversal of global GND net (132 connections)
  (signal_analysis.transistor_circuits)

### Missed
(none)

### Suggestions
- Integrator detection: when only a capacitor is in the feedback path (output-to-inverting-input), classify as integrator even if a resistor touches the inverting input node from a different source
- Skip power/ground nets when collecting base_resistors and base_driver_ics for transistors

---
