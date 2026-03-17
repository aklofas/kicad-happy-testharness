# Findings: 3458A-A3-Schematic-KiCad / 3458A A3 1989 ERC 2931_3458A A3 1989 ERC 2931

## FND-00000268: HP 3458A A3 analog board 1989 recreation (270 components). All 9 rf_matching entries are false positives (clock ferrite beads and precision integrator input filters). EL2018 comparator misclassified as compensator (C403 hysteresis is positive feedback). False RC filter from comparator hysteresis network. Duplicate design_observations per IC unit.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: 3458A A3 1989 ERC 2931_3458A A3 1989 ERC 2931.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- Active 20MHz oscillator U230 correctly identified
- LM6361 U140 correctly classified as transimpedance_or_buffer with R141=12.1k feedback
- LM358 U170 units correctly classified as inverting (gain=-0.412) and buffer
- LT1001 reference regulators U160/U165 for +12ref/-12ref correctly identified
- Precision RC filters for signal path correctly detected (XO_OVLD, XF/R, ACDA/DCDA)

### Incorrect
- All 9 rf_matching entries are false positives — L231/L232/L233 are clock distribution ferrite beads from 20MHz oscillator to logic ICs; L123/L127 with C128/C129/C119/C122 are precision integrator input filters on summing node
  (signal_analysis.rf_matching)
- U405 EL2018 (lib PCM_Analog_Comparator_AKL:AD8561AN, desc 'IC COMPARATOR HS') misclassified as 'compensator' — C403 22pF from output HTRIG to inverting input is positive feedback for hysteresis, not opamp compensation
  (signal_analysis.opamp_circuits)
- RC filter [7] (R407+C403, ground_net=HTRIG) is false positive — R407 is comparator input resistor, C403 is hysteresis cap; HTRIG is comparator output, not ground
  (signal_analysis.rc_filters)
- Duplicate design_observations: U213 5x, U303 7x, U302 7x, U353 7x, U150 7x, U403 5x — decoupling check iterates per unit, inflating 25 unique ICs to 66 entries
  (signal_analysis.design_observations)

### Missed
(none)

### Suggestions
- RF matching should exclude ferrite beads and require RF-context ICs (not logic gates or precision opamps)
- Opamp classifier should check lib_id/description for 'COMPARATOR' — feedback to inverting input on comparators is hysteresis, not compensation
- RC filter should exclude cases where ground_net is a driven output (not ground/power rail)
- Deduplicate design_observations by component reference

---
