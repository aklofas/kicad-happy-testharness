# Findings: MCLEANS/STM32-SAMPLE-KICAD-BOARD / STM32_SAMPLE

## FND-00001345: PCB component_groups shows D1-D6 (6 LEDs) but schematic has D1-D7 (7 LEDs); 2-layer board with mixed front/back placement correctly detected; Large courtyard overlap between J4 and U2 correctly det...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: STM32_SAMPLE.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Board correctly identified as 2-layer (F.Cu, B.Cu only), 30 footprints on front and 15 on back side. 37 SMD and 5 THT (including the SW_PUSH push button and 3 mounting holes + USB connector). Board dimensions 49.403×34.036mm are plausible for a compact STM32F405 breakout board.
- J4 (5-pin header, 0.5mm pitch horizontal) overlaps U2 (STM32F405 LQFP-64) courtyard by 73.334mm² — a large overlap that would indicate the 5-pin connector footprint is placed on top of the MCU. This is a legitimate layout problem correctly flagged by the analyzer.

### Incorrect
- The schematic lists 7 LEDs (D1 through D7), and the BOM confirms 7 LED references. The PCB component_groups shows only D: {count: 6, references: [D1, D2, D3, D4, D5, D6]} — D7 is missing from the PCB component list. Either D7 was not placed on the PCB (layout omission) or there is a parsing error dropping the footprint. The footprint_count=45 in statistics matches the schematic's 45 components, so this appears to be a grouping/counting error in the component_groups section rather than a missing footprint.
  (component_groups)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001346: LM1117-3.3 LDO correctly identified with +5V input and +3.3V output; No UART/SPI bus detection despite STM32F405 with likely named bus nets on connector pins; 7 LED components correctly identified ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STM32_SAMPLE.sch.json
- **Created**: 2026-03-24

### Correct
- U1 (LM1117-3.3) is correctly classified as LDO topology with input_rail=+5V and output_rail=+3.3V, estimated_vout=3.3, vref_source=fixed_suffix. The 13 decoupling caps (22µF total) on +3.3V and 1 cap on +5V are correctly attributed.
- 7 LEDs (D1-D7) are all correctly classified as 'led' type with 220-ohm current limiting resistors (R2-R7 and R11) on the +3.3V rail. Component types are correctly broken down: 2 ICs, 5 connectors, 16 caps, 11 resistors, 1 switch, 7 LEDs, 3 mounting holes.

### Incorrect
(none)

### Missed
- The STM32F405RGTx (U2) is a 64-pin MCU with multiple UART, SPI, and I2C peripherals. The design has 78 nets with many unnamed (routed through connectors J1-J5). While the schematic does not use named bus nets for these peripherals, the lack of any bus detection at all (bus_analysis.uart=[], spi=[], i2c=[]) means the analyzer has nothing to check. This is borderline acceptable since the design has no named bus nets, but the MCU's USB pins (HSE_IN, HSE_OUT named, USB implicit) should trigger at least a USB detection.
  (statistics)

### Suggestions
(none)

---
