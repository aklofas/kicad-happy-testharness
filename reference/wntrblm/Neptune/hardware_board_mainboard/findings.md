# Findings: wntrblm/Neptune / hardware_board_mainboard

## FND-00000276: Neptune analog synth filter mainboard (273 components, 6 TL074 ICs). Opamp circuits, RC filters, voltage dividers, BJT VCA transistors all well detected. U1 unit3 non-inverting amplifier (+8VREF generator, gain=3.2) misclassified as transimpedance_or_buffer. Duplicate design_observations: U1 decoupling warning emitted 5 times (once per TL074 unit).

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_board_mainboard.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 30 opamp circuit entries for 6 TL074 chips with accurate gain values and configurations
- TL431A correctly classified as voltage reference with REF shorted to cathode (2.5V config)
- 4 BJT VCA transistors (BCM847 NPN, MMBT3906 PNP) correctly typed with LED load detection
- 31 RC filters with correct topology categorization (low-pass, high-pass, RC-network)
- 16 voltage dividers including TL431 reference and potentiometer bias correctly detected
- Decoupling coverage for +12V/-12V (8 caps each, 20.6uF) correctly reported

### Incorrect
- U1 unit3 (+8VREF non-inverting amp, gain=3.2) misclassified as 'transimpedance_or_buffer' — has R205 (220k) feedback and R202 (100k) to GND, a standard non-inverting topology
  (signal_analysis.opamp_circuits)
- design_observations: U1 TL074 decoupling warning emitted 5 times (once per symbol unit) instead of once per IC
  (signal_analysis.design_observations)

### Missed
(none)

### Suggestions
- Non-inverting topology: if feedback resistor found from output to inv_input AND second resistor from inv_input to GND, classify as non_inverting with gain=(Rf+Rg)/Rg
- Deduplicate design_observations by (component reference, category)

---

## FND-00000277: Neptune Hubble test fixture (66 components, 14 DG449 analog switches). Correctly reports zero opamp/filter/divider detections. Decoupling warnings for 14 ICs without bypass caps are factually accurate.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_hubble-lens_hubble-lens.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- Zero opamp circuits, RC filters, voltage dividers correctly reported for switch-only board
- 14 DG449 power domains correctly identified on +/-12V rails
- 14 decoupling warnings accurately reflect no bypass caps on board

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
