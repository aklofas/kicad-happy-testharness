# Findings: MeterBoard32 / MeterBoard32

## FND-00000949: AMS1117-3V3 LDO, WS2812B addressable LED chain, Q1/Q2 auto-reset circuit, RC filter on EN line, and decoupling analysis all correctly detected; USB Full-Speed bus protocol not detected despite CP21...

- **Status**: new
- **Analyzer**: schematic
- **Source**: MeterBoard32.sch.json
- **Created**: 2026-03-23

### Correct
- Power rails +3.3V/VBUS/GND correctly identified. AMS1117-3V3 LDO topology correct. RC filter R7(1k)+C10(10uF) → EN at 15.92 Hz LP is correct. Q1/Q2 S8050 NPN transistors for DTR/RTS ESP32 auto-reset circuit correctly detected. WS2812B chain correctly identified.

### Incorrect
(none)

### Missed
- CP2102N (U2) is a USB-UART bridge with explicit D+/D- nets. bus_protocols returns []. The design_observations only note 'usb_data' for D+ and D- individually with no ESD protection, but no USB FS bus protocol entity is synthesized. TSS721A (U5, J1708 bus transceiver) is also undetected as a bus protocol.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000950: 2-layer board, DFM annular ring violation, thermal pads for ESP32-WROOM and CP2102N, GND zone stitching, and 38 footprints (including G1 logo) all correctly detected

- **Status**: new
- **Analyzer**: pcb
- **Source**: MeterBoard32.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- DFM correctly flags 0.1mm annular ring requiring advanced process. Thermal pads on U3 (ESP32-WROOM, 6x6mm) and U2 (CP2102N, 2.6x2.6mm) correctly identified. Both have 0 nearby thermal vias which is a real concern. GND zone on F.Cu and B.Cu with 36 stitching vias correctly analyzed.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000951: 7-layer set complete and aligned, drill classification into vias/component holes/mounting holes correct, 2-layer board correctly identified

- **Status**: new
- **Analyzer**: gerber
- **Source**: Gerber.json
- **Created**: 2026-03-23

### Correct
- Layer completeness verified via .gbrjob. 56 vias at 0.4mm drill, 2 component holes at 0.7mm, 2 mounting holes at 1.3mm correctly classified. F.SilkS extent slightly larger than Edge.Cuts (69mm vs 63mm height) indicating silkscreen extends outside board edge — not flagged as alignment issue correctly since it's just silk.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
