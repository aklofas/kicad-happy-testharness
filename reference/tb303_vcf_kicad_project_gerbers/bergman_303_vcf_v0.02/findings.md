# Findings: tb303_vcf_kicad_project_gerbers / bergman_303_vcf_v0.02

## FND-00000170: TB-303 VCF clone analog filter circuit. L7805 regulator classified as IC, trimmers as resistors, no analog filter detection.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: bergman_303_vcf_v0.02.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- 18 transistors correctly identified in the analog filter topology
- Component values correctly extracted

### Incorrect
- L7805 voltage regulator classified as IC instead of power regulator
  (signal_analysis.power_regulators)
- RV1 and RV2 trimmer potentiometers classified as resistor instead of potentiometer
  (components)

### Missed
- Analog filter topology not detected despite being the core function of the board (TB-303 VCF)
  (signal_analysis.filters)

### Suggestions
- Recognize L78xx and L79xx series as voltage regulators regardless of library symbol category
- Classify RV-prefixed components and trimmer symbols as potentiometer not resistor
- Add analog filter detection for transistor ladder / OTA filter topologies common in audio circuits

---

## FND-00000176: TB-303 VCF clone (69 components). Correct: all 18 transistors, power rails, L7805 in power_budget, resistor values. Incorrect: L7805 classified as IC instead of regulator, sleep current dominated by misclassified R4 path. Missed: no analog filter detection for 4-pole transistor ladder VCF, no voltage divider detection, trimmers RV1/RV2 classified as resistor instead of potentiometer.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: bergman_303_vcf_v0.02.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- All 18 transistors (16x 2SC945 NPN, 2x 2SA733 PNP) correctly enumerated
- L7805 correctly in power_budget producing +5V from +12V

### Incorrect
(none)

### Missed
- Trimmers RV1/RV2 classified as resistor instead of potentiometer
  (bom.type)

### Suggestions
- Add Regulator_Linear/Regulator_* lib_id patterns to regulator classification
- Classify R_Potentiometer_Trim as potentiometer

---
