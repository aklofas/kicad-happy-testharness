# Findings: cracked-machine/BigMuffs / BMP_BasicClone

## FND-00000407: Potentiometer misclassified as transformer in component_types; Resistor count inflated by 1 due to POT misclassification

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: BMP_BasicClone_BMP_BasicClone.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The schematic has 3 POT components (SUSTAIN1, TONE1, VOLUME1) with lib_id='POT'. One of these is classified as 'transformer' in component_types, which is completely incorrect for a guitar pedal. This inflates transformer count to 1 (there are no transformers in this design). The same pot that becomes 'transformer' is also causing 'switch' to read 2 instead of the expected 4 (SW_EN1 + 3 pots). This same misclassification pattern appears identically in the RussianClone output.
  (statistics)
- The schematic has exactly 23 resistors (R1–R23). The analyzer reports component_types.resistor=24. The extra count comes from one of the three POT components (SUSTAIN1, TONE1, VOLUME1) being incorrectly classified as a resistor. The BOM section correctly groups all resistors as R1–R23 totalling 23, confirming the component_types count is wrong. Same issue exists in RussianClone.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000408: Potentiometer misclassified as transformer in component_types (same as BasicClone)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: BMP_RussianClone_BMP_RussianClone.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The RussianClone has the same 3 POT components (SUSTAIN1, TONE1, VOLUME1) with lib_id='POT' as the BasicClone. One POT is misclassified as 'transformer' (component_types.transformer=1) and another as 'resistor', producing the same wrong counts: resistor=24 (should be 23), switch=2 (should be 4), transformer=1 (should be 0). There are no transformers in this guitar pedal design.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000409: NPOT potentiometer DEPTH1 misclassified as diode in BOM; Resistor count inflated by 1 due to NPOT misclassification; Key matrix falsely detected in guitar pedal schematic; GND missing from power_ra...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: BMP_SuperColliderClone_BMP_SuperColliderClone.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- DEPTH1 is a 150K potentiometer with lib_id='NPOT'. It is classified as type='diode' in the BOM output. This is completely incorrect — it is a potentiometer controlling the 'depth' of the effect. This misclassification causes component_types.diode to read 6 (there are only 5 real diodes: D1=Schottky, D2–D5=1N914), with the 6th being DEPTH1 falsely counted.
  (statistics)
- The SuperCollider schematic has 26 resistors (R1–R26). The analyzer reports component_types.resistor=27. As with the BasicClone, one of the 5 NPOT potentiometer components is being misclassified as a resistor. Additionally, one NPOT is classified as 'transformer' (component_types.transformer=1), which is wrong.
  (statistics)
- The signal_analysis.key_matrices section reports a 2x2 keyboard matrix (estimated_keys=4, switches_on_matrix=4, diodes_on_matrix=4). This is a guitar effects pedal (Big Muff clone) with no keyboard matrix. The false positive is likely triggered by the four 2-pin transistor-mod connectors (J_Q1MOD1–J_Q4MOD1), which are bypass jumper pads for transistor socket modification, combined with nearby diodes. The topology-based detection misidentified these as a matrix. BasicClone and RussianClone (which lack these connectors) do not have this false positive.
  (signal_analysis)

### Missed
- The statistics.power_rails array contains only ['+9V'] for the SuperCollider schematic, omitting GND. The source schematic contains 17 'Text Label ... ~ 12\nGND' entries — the same format used in BMP_BasicClone.sch and BMP_RussianClone.sch, where GND is correctly detected and reported in power_rails. The SuperCollider also has one additional GND text label with '~ 0' style (at position 2000 6100), but the standard '~ 12' labels are identical in format to the other two designs which do report GND. This is an inconsistency in the power rail detection for this file.
  (statistics)

### Suggestions
- Fix: NPOT potentiometer DEPTH1 misclassified as diode in BOM

---
