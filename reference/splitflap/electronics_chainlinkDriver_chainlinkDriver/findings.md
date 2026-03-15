# Findings: splitflap / electronics_chainlinkDriver_chainlinkDriver

## FND-00000078: Legacy KiCad 5 schematic for split-flap motor driver board. 65 components, 184 nets correctly extracted. 0 signals detected due to KH-016. Design centers on 4x 74HC595 shift registers driving 4x TPL7407L open-drain arrays for motor control, plus 74HC165 parallel-in shift register for sensor input and 74HC125 buffer. This is a well-structured SPI-like daisy-chain topology.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/splitflap/electronics/chainlinkDriver/chainlinkDriver.sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- All 65 components extracted with correct references and values
- Component types correct: 10 ICs (4x 74HC595, 4x TPL7407L, 74HC165, 74HC125), 12 caps, 17 connectors, 13 resistors, 6 LEDs
- Power rails +12V, +3.3V, GND correctly identified
- 184 nets with proper associations
- BOM correctly consolidated: 4x 74HC595, 4x TPL7407L as grouped entries
- 10 subcircuits identified around each IC

### Incorrect
- TPL7407L components use lib_id Transistor_Array:ULN2003A - the value says TPL7407L but lib symbol is ULN2003A. Analyzer correctly reports what is in the schematic, but could note the value/lib mismatch as a design observation
  (components)

### Missed
- No signal analysis detected (0 signals) - SPI-like shift register chain (CLOCK, LATCH, DATA signals), motor drive outputs, and sensor input path should all be detectable
  (signal_analysis)
- No SPI bus detection for the 74HC595/74HC165 daisy chain despite CLOCK, LATCH, DATA net names being present
  (design_analysis.bus_analysis)

### Suggestions
- Resolving KH-016 would enable SPI/shift-register chain detection
- Consider detecting shift register daisy-chain topologies as a signal pattern

---
