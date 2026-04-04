# Findings: kicad-projects / projects_led-controller-esp32_led-controller-esp32

## FND-00002257: EIA capacitor code '104' parsed as 104 pF instead of 100 nF

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-projects_projects_motion-nightlight_motion-nightlight.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- Capacitors C1 and C2 have value '104', which is standard EIA capacitor code for 100 nF (10 × 10^4 pF). The analyzer parses this as 1.04e-10 F (104 pF), yielding a calculated self-resonant frequency of ~494 MHz — more than 30x too high. This causes the decoupling analysis for V_CONTROL rail to show total_capacitance_uF=0.0 (essentially zero) and 'has_bypass: false', which is incorrect. The actual capacitance is 0.2 uF (200 nF) across the two caps.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002258: Buck converter module U2 not detected as a power regulator

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-projects_projects_led-controller-esp32_led-controller-esp32.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- U2 is the MP1584 'Mini360' buck converter module with pin names '+Vin', '+Vout', '-Vin', '-Vout' and a description explicitly stating '6.5-24V input, 5V 1.8A output'. The signal_analysis.power_regulators list is empty. The analyzer only flagged a decoupling warning noting '+Vin' lacks capacitors but missed detecting the converter topology entirely. Given the pin names and description, this should be detectable as a switching regulator converting +Vin to +5V.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002259: 74LVC2G14 Schmitt trigger IC correctly identified and component types parsed accurately

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematic_kicad-projects_projects_motionhold_AM312_motionhold_AM312.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identified U1 as a 74LVC2G14 dual Schmitt-triggered inverter, correctly parsed it as type 'ic', and correctly enumerated all 7 components (2 capacitors, 2 connectors, 1 IC, 1 diode, 1 trim potentiometer). The potentiometer RV1 is correctly typed as 'resistor' per the library description, and the diode D1 (1N4148) is correctly identified with full datasheet URL from the KiCad library.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
