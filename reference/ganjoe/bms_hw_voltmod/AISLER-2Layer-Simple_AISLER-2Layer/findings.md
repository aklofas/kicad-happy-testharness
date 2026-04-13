# Findings: ganjoe/bms_hw_voltmod / AISLER-2Layer-Simple_AISLER-2Layer

## FND-00002288: RS485 interface not detected despite ISO3082DW RS485 isolated transceiver being present

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_bms_hw_voltmod_RS485iso.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The RS485iso.kicad_sch contains U11 (ISO3082DW, lib_id Interface_UART:ISO3082DW), which is an isolated RS485 transceiver. The bus_analysis reports can=[], i2c=[], spi=[], uart=[] — no RS485 interface is detected. The design_observations only flags 4 single-pin nets (POCI, REN, DEN, PICO — which are the RS485 DE/RE control and data pins) but does not synthesize them into an RS485 bus detection. The analyzer should recognize the ISO3082DW lib_id or the A/B differential pair as RS485.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002289: Op-amp circuits correctly identified: 8 inverting TL074 stages with gain=-1.0 and 2 power units; Unannotated components and duplicate references correctly flagged in annotation_issues; kicad_versio...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_bms_hw_voltmod_hw_voltmod.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The hw_voltmod schematic uses two TL074 quad op-amps (U3, U4) to buffer and invert 8 cell voltage measurements. All 8 functional units are correctly identified as inverting configuration with gain=-1.0 (Rf=Rin from equal-value 56k or 100k resistor pairs). The two power supply units (unit 5 on each IC) are correctly reported as config=unknown since they have no analog signal connections. Total opamp_circuits=10 matches 8 functional + 2 power units.
- The hw_voltmod schematic is a work-in-progress with many unannotated components (D?, J?, JP?, R?, U?). The analyzer correctly reports annotation_issues with unannotated=['D?','J?','JP?','R?','U?'] and duplicate_references=['D?','R?']. This accurately reflects the design state. The isolation barrier (ADuM6000, ADuM5411, ISO7331C) in the RS485iso sub-sheet is also correctly detected.

### Incorrect
- The hw_voltmod.kicad_sch file_version is 20230121, which corresponds to KiCad 7.0. The analyzer outputs kicad_version='unknown' instead of the expected '7'. The version mapping for date-stamped KiCad 6+ file versions appears to be missing the 20230121 entry (KiCad 7 shipped in February 2023 with file_version 20230121). This affects display and any version-conditional analysis paths.
  (kicad_version)

### Missed
(none)

### Suggestions
(none)

---
