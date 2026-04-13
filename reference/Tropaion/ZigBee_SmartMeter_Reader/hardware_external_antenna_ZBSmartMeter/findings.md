# Findings: Tropaion/ZigBee_SmartMeter_Reader / hardware_external_antenna_ZBSmartMeter

## FND-00001973: TLV1117-33 LDO regulator correctly identified with estimated 3.3V output; USB-C differential pair correctly identified with ESD protection; UART interfaces correctly detected for NCN5150 and ESP32-...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ZBSmartMeter.kicad_sch
- **Created**: 2026-03-24

### Correct
- U2 (TLV1117-33) is correctly identified as an LDO regulator with input from +5V and output to +3.3V. The estimated_vout=3.3 is derived from the fixed_suffix of the part name, which is correct.
- The USB_D+ and USB_D- differential pair is correctly detected with shared_ics including J6 (USB-C connector) and U3 (ESP32-C6). ESD protection is correctly flagged as present via CPDQ5V0-HF diodes (D4, D5, D6). The three protection diodes are all correctly classified.
- Four UART nets detected: UART1_TX/RX (between NCN5150DG U1 and ESP32-C6 U3) and UART0_PROG_RX/TX (programming interface on U3). All four are correctly identified with the relevant device references.

### Incorrect
(none)

### Missed
- U3 (ESP32-C6-MINI-1/U) is a ZigBee and WiFi SoC with an external antenna configuration. The project name ('external_antenna') and the PCB design indicate an RF signal path. The signal_analysis.rf_chains list is empty. The analyzer likely does not recognize ESP32-C6-MINI as an RF device, and without explicit antenna net names (e.g., ANT, RF_OUT), the RF chain detector does not fire.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001974: ESP32-C6 thermal pad (pad 49) duplicated 8 times in thermal_pads list; Zone count of 121 correctly reflects dense copper pour design; 14 courtyard overlaps correctly detected on a densely populated...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: ZBSmartMeter.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The ZBSmartMeter PCB uses a KiCad 8 format (version 20240108) with 121 copper zones — a mix of +3.3V and GND pours covering both layers. This is verified against the source file (121 zone definitions). The zone_stitching section correctly summarizes the 9 major nets with copper pours.
- The board is 43.3×37.6 mm with 37 footprints including THT connectors (RJ12, USB-C) with large courtyard footprints. The 14 overlaps include large violations like J1 vs U1 (61.4 mm²) and C3 vs J5 (37.2 mm²), which are plausible given how tightly components are placed around the THT connectors.

### Incorrect
- The ESP32-C6-MINI-1/U footprint defines pad '49' (the exposed ground thermal pad) as one custom-shaped pad plus 8 rectangular sub-pads — a total of 9 pad definitions in the source file. The analyzer reports 8 identical entries in thermal_analysis.thermal_pads, all for (U3, pad '49'). These should be deduplicated into a single thermal pad entry. All 8 entries show 0 nearby_thermal_vias, which may also be inaccurate given the dense copper pour on the board.
  (thermal_analysis)

### Missed
(none)

### Suggestions
(none)

---
