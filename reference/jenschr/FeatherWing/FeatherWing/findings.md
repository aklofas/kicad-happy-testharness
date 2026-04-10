# Findings: FeatherWing / FeatherWing_FeatherWing

## FND-00000551: Component count, types, and BOM correctly identified; Named nets bat/sck/mo/mi/rx/tx/rst show empty pins[] despite being wired to connectors; Net 'en' mapped to J1 pin 1 but 'bat' (the actual pin-1...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: FeatherWing_FeatherWing.sch.json
- **Created**: 2026-03-23

### Correct
- 6 components (4 mounting holes, 2 connectors), 3 unique parts, 15 no-connects, power rails +3V3/GND/PWR_FLAG all correct.
- Both PWR_FLAG instances (#FLG0101 on +3V3 and #FLG0102 on GND) are captured in power_symbols with correct net names and coordinates.

### Incorrect
- Labels bat, sck, mo, mi, rx, tx, rst are connected via wires to J1/J2 pins in the schematic, but all appear with pins:[] in the nets section. The analyzer failed to trace these label-to-pin connections, likely due to legacy KiCad 5 wire endpoint matching on these particular nets.
  (signal_analysis)
- Wire at (4200,3500)-(4000,3500) connects label 'bat' to J1 pin 1. Wire at (4200,3600)-(4000,3600) connects 'en' to J1 pin 2. But output shows en→pin1, usb→pin2, and bat with empty pins. The pin-to-net assignment is shifted/wrong for this connector.
  (signal_analysis)
- The schematic has 28 connector pins total minus the named/connected ones. Many __unnamed_N nets (0–21) correspond to NoConn pins that should arguably not be separate nets. The count of 35 nets includes many single-point unnamed nets for no-connect pins, which inflates the total.
  (signal_analysis)

### Missed
- Labels 'scl' and 'sda' are present and connected to J1. The bus_analysis.i2c array is empty. The SPI bus (sck/mo/mi) is also not detected. Only UART (tx/rx) was detected, though those nets also have empty pins.
  (signal_analysis)

### Suggestions
(none)

---
