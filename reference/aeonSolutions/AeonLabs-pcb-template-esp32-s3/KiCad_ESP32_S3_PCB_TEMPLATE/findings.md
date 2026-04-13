# Findings: aeonSolutions/AeonLabs-pcb-template-esp32-s3 / KiCad_ESP32_S3_PCB_TEMPLATE

## FND-00000374: LR1 (Device:R, 330R resistor) misclassified as inductor; EL1 (Device:L, 1.8nH inductor) misclassified as other instead of inductor; Crystal circuits ECY1 (32.768MHz) and ECY2 (40MHz) not detected i...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KiCad_ESP32_S3_PCB_TEMPLATE.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- LR1 has lib_id=Device:R and value=330R (a resistor), but the analyzer assigns type=inductor and category=inductor. The reference prefix LR appears to confuse the type classifier into treating it as an inductor. It should be classified as other (resistor).
- EL1 has lib_id=Device:L and value=1.8nH 5% (a genuine inductor), but the analyzer assigns type=other and category=other. The reference prefix EL is not being recognized as an inductor prefix. It should be classified as inductor.

### Incorrect
(none)

### Missed
- The schematic has two crystal oscillator circuits: ECY1 (32.768MHz, Device:Crystal_GND24_Small) with load caps EC12/EC15 (22pF) connected to ESP32-S3 GPIO15/GPIO16 XTAL_32K pins, and ECY2 (40MHz, Device:Crystal_GND24_Small) with load caps EC14/EC17 (22pF) connected to ESP32-S3 XTAL_P/XTAL_N pins. The signal_analysis.crystal_circuits array is empty. Both ECY1 and ECY2 are also mistyped as other instead of crystal.
  (signal_analysis)
- The schematic has a classic ESP32-S3 RF front-end: EL1 (1.8nH series inductor) and EC6/EC9 (2.7pF shunt capacitors) form a pi/L matching network between the ESP32-S3 LNA_IN/RF pin (pin 1) and the antenna path (J3 U.FL connector and ANT1 PCB antenna). Both rf_matching and rf_chains arrays are empty. This is a standard single-chip RF matching topology.
  (signal_analysis)

### Suggestions
(none)

---
