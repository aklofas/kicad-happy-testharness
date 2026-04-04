# Findings: Adafruit-KB2040-PCB / Adafruit KB2040_Adafruit KB2040

## FND-00000345: Crystal load caps C19 and C20 not detected in crystal_circuits; CONN1 (STEMMA I2C connector) misclassified as type 'capacitor'; Fiducial markers U$34 and U$35 misclassified as type 'ic'; design_obs...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Adafruit KB2040_Adafruit KB2040.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- CONN1 (value STEMMA_I2C_QTSKINNY, footprint JST_SH4_SKINNY) is a 4-pin JST I2C connector. The analyzer assigns it type 'capacitor' in both the BOM entry and component list. The lib_id symbol name does not contain typical capacitor keywords — this is a misclassification. The symbol's reference prefix in lib_symbols is 'CONN', which should result in 'connector' type. The statistics section counts it under 'connector' (count 1), but the per-component and BOM type fields say 'capacitor'.
- U$34 and U$35 are FIDUCIAL_1MM parts (PCB fiducial markers with no electrical function). Both are classified as type 'ic' in the component list and BOM. The lib_symbols entry for FIDUCIAL_1MM has reference prefix 'FID', not 'U'. These should be classified as 'other' or a mechanical/fiducial type, not IC. This inflates the ic count in component_types.
- The signal_analysis.design_observations section contains two i2c_bus entries (for SDA and SCL) with 'has_pullup: false' and 'pullup_resistor: null'. However, design_analysis.bus_analysis.i2c correctly identifies R10 (5.1K to 3.3V) on SDA and R12 (5.1K to 3.3V) on SCL with 'has_pull_up: true'. The two code paths disagree about the same schematic topology. The design_observations path is the one generating the false negative — it apparently fails to find the pull-ups where bus_analysis succeeds.
- In test_coverage.uncovered_key_nets, the net 'SCLK' is assigned category 'i2c'. SCLK is the SPI clock for the user-facing SPI bus (connected to IC2 GPIO18/SPI0_SCK and exposed on JP1). The net_classification correctly assigns it type 'clock', and it appears in bus_analysis.spi. The test coverage categorization logic incorrectly bucket-classifies it as i2c rather than spi, leading to the observation summary claiming '3 i2c' uncovered key nets instead of '2 i2c + 1 spi' additional.

### Incorrect
- The design_observations entry for U2 (category: 'regulator_caps') reports missing_caps for both input ('RAW') and output ('3.3V') rails. However, the schematic clearly has C8 (10µF) and multiple 0.1µF caps (C9, C11, C13, C14, C16, C17) on the 3.3V rail confirmed by inrush_analysis, and C6 (10µF) on the VBUS/RAW side. The inrush_analysis section lists C8, C13, C14, C15, C16 as output caps for U2. The decoupling cap detection in design_observations uses a different (apparently broken) lookup path than inrush_analysis.
  (signal_analysis)

### Missed
- Y1 (12 MHz crystal) has two 22pF load caps: C19 connected to crystal pin 3 (XIN side, net __unnamed_3) and C20 connected to crystal pin 1 (XOUT side, net __unnamed_20). Both caps have their other end on __unnamed_19 (shared node between C19 pin 1 and C20 pin 1), which connects to XIN/XOUT via R6 and IC2. The signal_analysis.crystal_circuits entry shows 'load_caps: []' — the load cap detection logic fails to associate C19 and C20 with Y1 because the crystal pins connect to them through an intermediate net rather than directly, or because the topology check is too strict.
  (signal_analysis)

### Suggestions
(none)

---
