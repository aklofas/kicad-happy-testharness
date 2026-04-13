# Findings: Kernow-Robotics/kicad-ref-schematics / kicad-ref-schematics

## FND-00002260: Crystal X1 (X322512MSB4SI) classified as 'connector' type, not 'crystal'; Crystal feedback resistor R1/C2 on XOUT net misclassified as an RC low-pass filter; SPI flash W25Q128 connected to RP2040 n...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-ref-schematics_kicad-ref-schematics.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The RP2040 12 MHz crystal X1 uses a lib_id from the easyeda2kicad library ('easyeda2kicad:X322512MSB4SI') with a footprint 'CRYSTAL-SMD_4P-L3.2-W2.5-BL'. The analyzer assigns it type 'connector' and category 'connector' rather than recognizing it as a crystal oscillator. As a result, crystal_circuits is empty even though X1 is connected to RP2040 pins XIN/XOUT with appropriate load capacitors (C1, C2) and a feedback resistor (R1). The crystal is also counted in the BOM under connectors, not crystals.
  (signal_analysis)
- R1 (1k) and C2 (30p) on the XOUT net form the crystal oscillator feedback/damping network, not an independent RC filter. The analyzer reports this as a 5.31 MHz low-pass filter in rc_filters. Since X1 is not recognized as a crystal, the analyzer cannot suppress this spurious RC filter detection. This is a secondary consequence of the crystal misclassification.
  (signal_analysis)

### Missed
- U2 (W25Q128JVSIQTR) is correctly identified as a memory_interfaces item (connected to U1 RP2040 with 6 shared signal nets), but the bus_analysis.spi array is empty. The SPI bus between RP2040 and the flash chip is not detected, likely because the net names do not include 'SPI' or MISO/MOSI keywords. The bus should be reconstructable from the shared nets.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002261: Hierarchical sub-sheet analyzed independently with identical component counts and power rails

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematic_kicad-ref-schematics_schematics_rp2040.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The repo uses KiCad hierarchical sheets: the root file kicad-ref-schematics.kicad_sch includes schematics/rp2040.kicad_sch as a sub-sheet. Both are analyzed, and the sub-sheet correctly reports the same 27 components and 4 power rails (+1V1, +3.3V, +5V, GND). The main sheet adds sheet-path-qualified net names for the 30 GPIO nets. This dual analysis is expected behavior for hierarchical designs.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
