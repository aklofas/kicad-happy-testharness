# Findings: kicad-keyboards / kicad-keyboards

## FND-00002250: Key matrix correctly detected: 4×9, 37 keys, 37 diodes, via net-name method; USB Full Speed interface not detected despite ATmega32U4 and D+/D- nets; Crystal circuit correctly detected with Y1 16MH...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-keyboards_kicad-keyboards.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identified the keyboard matrix structure: 4 row nets (Row 0–3), 9 column nets (Col 0–9), 37 MX switches, and 37 SOD-123 diodes matched on matrix. Detection method 'net_name' is accurate for this design.
- Y1 (16MHz crystal) is found with both load capacitors C6 and C7 (22pF each), yielding effective load of 14pF. The circuit is consistent with ATmega32U4 USB FS requirements (16MHz with 22pF load caps is a standard and correct combination).

### Incorrect
(none)

### Missed
- The schematic uses an ATmega32U4 MCU (U1) which has a built-in USB FS transceiver. The D+ and D- nets are present (connected via 22Ω series resistors R2/R3 to USB connector USB1). However, there is no 'usb_interfaces' key in signal_analysis at all — USB FS detection is entirely absent from the analyzer. The design clearly implements USB HID.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002251: Empty/stub PCB file correctly reported as having 0 footprints and 0 tracks

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad-keyboards_kicad-keyboards.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The source kicad_pcb file is a minimal 78-byte stub containing only the version header with no footprints, tracks, or board outline. The analyzer correctly returns all-zero statistics rather than crashing. This is a schematic-only project where PCB layout has not been started.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
