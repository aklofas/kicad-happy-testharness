# Findings: OrangePiR1-schematics / KiCad_OrangePiR1

## FND-00000979: D-prefix components (DR*, DC*, DU*) misclassified as diode type

- **Status**: new
- **Analyzer**: schematic
- **Source**: DDR3_16x1.sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The project uses non-standard ref prefixes: DR* = DDR resistors (value RES402), DC* = DDR caps (value CAP0402), DU1 = DDR3-FBGA96 IC. All 28 of these are typed as 'diode' based purely on the D ref prefix, inflating the diode count to 40 (only ~12 are actual diodes). The DDR3 memory chip DU1 is classified as a diode, preventing memory_interfaces detection.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000980: False-positive decoupling warnings for DCIN rail on all 6 regulators; Switching and LDO regulators correctly identified with topology and input rail

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: POWER.sch
- **Created**: 2026-03-23

### Correct
- All 6 regulators in the POWER sheet are detected: SY8008B (x3), SY8089A, SY8113B as switching; MIC5219-3.3YM5-TR as LDO with estimated_vout=3.3 from value suffix. Topology classification and input rail attribution are accurate.

### Incorrect
- design_observations reports 'rails_without_caps: [DCIN]' for U4, U7, U53, U55, U5, U6, and 'missing_caps: {input: DCIN}' for each. However, the DCIN net in the parsed data has 12+ capacitors directly connected (C38, C39, C57, C58, C50, C51, C183, C184, C307, C326, C327, C63). The decoupling checker is failing to associate these cap pins with the DCIN rail when evaluating regulator input caps.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000981: RTL8189ETV WiFi SoC not detected as rf_chain or any signal path

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: WIFI.sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The WIFI sheet contains CK-W-R189ETV-SM (RTL8189ETV WiFi module IC) with an antenna connector (ANT1). rf_chains and rf_matching both return empty. This is a WiFi SoC with RF output - it should trigger rf_chain or at minimum an ethernet/wireless interface detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000982: SPI NOR flash (U54 SPI-SST) not detected as memory_interface or SPI bus

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: NOR FLASH-TF.sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- U54 with value 'SPI-SST' is an SPI NOR flash IC. memory_interfaces returns empty and no SPI bus detection is present in signal_analysis. The bus_analysis.spi in design_analysis also appears empty. A flash chip connected to the SoC via SPI should be detectable.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000983: Top-level multi-sheet parsing and power rail enumeration is correct

- **Status**: new
- **Analyzer**: schematic
- **Source**: OrangePiR1.sch
- **Created**: 2026-03-23

### Correct
- The top-level file correctly parses all 13 sub-sheets, aggregates 316 components, 967 nets, and extracts a comprehensive set of 50+ power rails (VCC-1V2, VCC-DRAM, VDD-CPUX, etc.). Sheet traversal and statistics rollup work properly for this complex hierarchical design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
