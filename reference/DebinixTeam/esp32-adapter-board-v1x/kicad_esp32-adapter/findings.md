# Findings: DebinixTeam/esp32-adapter-board-v1x / kicad_esp32-adapter

## FND-00002044: GND net falsely detected as an I2C SDA line; SPI bus false positives: SCK mapped to GND and +3V3 rails

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_esp32-adapter-board-v1x_kicad_esp32-adapter_esp32-adapter.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The bus_analysis.i2c array contains an entry with net='GND' classified as an SDA line with 14 devices attached. GND is the ground net, not a data bus. This happens because pin-name matching on the ILI9341 TFT LCD module (U10) has a pin whose internal unnamed net ultimately resolves to GND through the schematic topology. The analyzer should exclude power/ground nets from bus detection.
  (design_analysis)
- Two SPI bus entries in bus_analysis.spi are clearly wrong. 'pin_U1' has SCK->net 'DC' (the ILI9341 data/command control pin, not a clock) and MOSI->net 'GND'. 'pin_U10' has SCK->net '+3V3' (a power rail) and MISO/MOSI swapped. These arise because the SPI detector matches pin names on the ILI9341 TFT module and then follows net connectivity incorrectly to power and ground rails. Only the bus_id='0' entry with SCK->net 'SCK' is a legitimate SPI bus.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002045: 2-layer gerber set correctly validated as complete with good alignment

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber_esp32-adapter-board-v1x_fabrication_gerbers.json
- **Created**: 2026-03-24

### Correct
- The gerber analyzer correctly identifies all 9 gerber layers (F.Cu, B.Cu, F/B.Mask, F/B.Paste, F/B.SilkS, Edge.Cuts) plus two drill files (PTH and NPTH). completeness.complete=true with no missing required or recommended layers. alignment.aligned=true. Board dimensions 137.16 x 167.64 mm match the PCB analysis. 210 component holes and 8 NPTH mounting holes are correctly classified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
