# Findings: jgrip/commodorelcd / commodorelcd

## FND-00000169: Commodore LCD replica/interface board. CR-prefixed diodes misclassified as capacitors, speaker and DC-DC converter misclassified, no regulators detected.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: commodorelcd.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- All ICs correctly identified and classified
- 44 ferrite beads correctly identified
- LM324 and LM358 opamps correctly identified

### Incorrect
- 12 CR-prefixed diodes misclassified as capacitor (CR is a standard diode reference designator per IEEE 315)
  (components)
- CNP1 speaker classified as capacitor instead of speaker/transducer
  (components)
- CN2 DB37 connector classified as mounting_hole instead of connector
  (components)
- DC1 DCDC converter classified as diode instead of power converter
  (components)

### Missed
- No power regulators detected despite DC-DC converter and voltage regulation on board
  (signal_analysis.power_regulators)

### Suggestions
- Recognize CR prefix as diode (IEEE 315 standard reference designator for diodes)
- Classify Speaker_Crystal and similar speaker library symbols as transducer not capacitor
- Classify DB-series connectors (DB9, DB25, DB37) as connector not mounting_hole
- Classify DC-prefix and DCDC-Conv library parts as power converter
- Detect DC-DC converters as power regulators from component type and net connections

---

## FND-00000175: Commodore LCD computer (231 components). Correct: all ICs, 44 ferrite beads, crystals, UART, opamps, bus topology. Incorrect: 12 CR-prefixed diodes misclassified as capacitor (CR is standard diode prefix), Speaker CNP1 as capacitor, DB37 connector CN2 as mounting_hole, DC1 DCDC-Conv as diode. Missed: no power_regulators detected, 4N28 optocoupler not in isolation_barriers.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: commodorelcd.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- 44 FB-prefixed components correctly classified as ferrite_bead
- Crystal circuits Y1 4MHz and Y3 3.579545MHz correctly detected
- LM324/LM358 opamp circuits correctly analyzed

### Incorrect
- 12 CR-prefixed components misclassified as capacitor instead of diode (CR1 1N4728 zener, CR15 LM385-2.5 voltage reference, etc)
  (statistics.component_types)

### Missed
- No power_regulators detected despite DC1 DCDC-Conv generating -12V/-5V
  (signal_analysis.power_regulators)

### Suggestions
- Add CR as standard diode reference prefix
- Classify Speaker_Crystal as speaker/piezo
- Recognize DB*_MountingHoles as connector
- Add DCDC/DC-DC value patterns to ic classification

---
