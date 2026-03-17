# Findings: 3458A-A3-66533-2021-KS-RoHS-SMD-KiCad / 3458A A3 66533 2021 KS SMD

## FND-00000267: HP 3458A A3 precision DMM analog board (399 components). All 10 rf_matching detections are false positives (ferrite beads for clock distribution and precision ADC guard networks). Three LT1001 integrators misclassified as comparator_or_open_loop. AD817A integrator misclassified as compensator. AD817A non-inverting amp misclassified as transimpedance_or_buffer. Duplicate design_observations per multi-unit IC.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: 3458A A3 66533 2021 KS SMD.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- U402 OP07C open-loop servo correctly classified as comparator_or_open_loop
- U404 LT1122 unity-gain buffer correctly classified
- U170 LM358 units correctly classified as buffer and inverting amplifier
- All 8 power regulators correct: 79L05/78L05 pairs for isolated ±5V rails, +3.3V and +1.8V LDOs
- U230 20MHz active oscillator correctly identified

### Incorrect
- U151/U160/U165 (LT1001) classified as comparator_or_open_loop — each has capacitor-only feedback (C151/C160/C165) from output to inverting input, making them integrators in the voltage reference regulation loops
  (signal_analysis.opamp_circuits)
- U111 (AD817A) classified as compensator with R118 as feedback_resistor — R118 connects two different opamps' inverting inputs (inter-stage coupling), not U111's output; C118 is the sole feedback element (integrator)
  (signal_analysis.opamp_circuits)
- U140 (AD817A) classified as transimpedance_or_buffer — has R140=1k to ground and R141=18.7k feedback, making it a non-inverting amplifier at gain 19.7x
  (signal_analysis.opamp_circuits)
- Duplicate design_observations: multi-unit ICs (U302 7x, U303 7x, U353 7x, U150 7x, U8 7x, U213 5x, U403 5x) generate per-unit entries instead of per-IC
  (signal_analysis.design_observations)

### Missed
- Precision input attenuator resistor ladder (R401-R406, 453k to 14k) with paired jumpers forms the ADC voltage ranging divider — 0 voltage_dividers detected
  (signal_analysis.voltage_dividers)

### Suggestions
- RF matching should exclude ferrite beads (description/keywords containing 'ferrite', 'EMI', 'bead')
- Integrator classification: capacitor-only feedback (output to inverting input) should be labeled 'integrator' not 'comparator_or_open_loop'
- Feedback resistor identification must verify one end connects to the opamp's output net
- Non-inverting amp detection: grounding resistor at inverting input + feedback resistor from output = non-inverting, not transimpedance
- Deduplicate design_observations by component reference

---
