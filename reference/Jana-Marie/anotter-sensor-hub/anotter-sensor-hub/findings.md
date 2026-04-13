# Findings: Jana-Marie/anotter-sensor-hub / anotter-sensor-hub

## FND-00001937: Component count of 29 correctly captured including ESP32-WROOM-32, AMS1117, connectors, jumpers, and mounting holes; I2C bus with pull-ups correctly detected; SPI and UART buses on ESP32 correctly ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: anotter-sensor-hub.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies 29 total components (5 resistors, 12 connectors, 3 capacitors, 4 mounting holes, 2 ICs, 3 jumpers) and the three power rails (+5V, GND, VCC). The AMS1117-3.3 LDO is correctly detected with topology=LDO, input=+5V, output=VCC, estimated_vout=3.3.
- The bus_analysis correctly identifies I2C on SCL/SDA nets with R2 and R3 (5.1kΩ) pull-ups to VCC. SPI bus is detected on COPI/CIPO/SCK with 4 chip selects (full_duplex mode). UART on RXD/TXD is also detected. All buses connect through the ESP32-WROOM-32 (U1).
- The power_regulators section correctly identifies U2 as AMS1117-3.3, topology=LDO, input_rail=+5V, output_rail=VCC, estimated_vout=3.3. The VCC output naming is correct as confirmed by the schematic nets.

### Incorrect
- Four mounting holes (H1-H4 with value 'M3') are included in total_components=29 and also in the missing_mpn list, which is correct behavior. However, missing_mpn lists 25 refs but excludes H1, H2, H3, H4 (mounting holes). Looking at the output more carefully, the missing_mpn list has 25 entries which does not include H1-H4. Mounting holes with no MPN should appear in missing_mpn, but they do not. This is a minor inconsistency — mounting holes are mechanically necessary parts without MPNs, so either they should all be excluded or all included.
  (statistics)

### Missed
- The schematic includes J5 with value 'USB Power' and footprint 'otter:USB-C 16Pin', which is a USB-C power connector. The design_observations section has no usb_data entry for this connector, and differential_pairs is empty []. For a USB-C connector, the analyzer should at minimum detect the USB power role (even if only VBUS/GND are connected). The 5k1 pull-down resistors R1-R5 on CC pins (USB-C configuration channel) are not detected as USB-C CC resistors either.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001938: PCB footprint count (29) matches schematic component count, 2-layer board with 3 copper zones

- **Status**: new
- **Analyzer**: pcb
- **Source**: anotter-sensor-hub.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer correctly identifies 29 footprints (27 front, 2 back), 19 SMD + 5 THT + 5 mounting holes, 2 copper layers, 307 track segments, 143 vias, 3 zones, 51 nets (matching schematic), and routing_complete=true. Board is 52.3×43.3mm.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
