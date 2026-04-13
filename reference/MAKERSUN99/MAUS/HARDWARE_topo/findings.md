# Findings: MAKERSUN99/MAUS / HARDWARE_topo

## FND-00000864: WS2812B addressable LED chain correctly detected; USB-A connector (J1) identified as non-Type-C, no false compliance failures; PWR_FLAG false positives for USB-powered design with no explicit PWR_F...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_topo.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Analyzer correctly identifies D1 as WS2812B single-wire protocol, chain length 1, data_in_net='RGB', estimated 60mA. Component counts (14 total, resistor/led/ic/cap/connector/diode types) are correct.
- USB compliance only reports an informational ESD check for the USB-A plug (USB1061-GF-L-A), no false CC pin failures. Correct behavior for USB-A.

### Incorrect
- The design is USB-powered via J1 (USB-A plug). The analyzer warns that GND and +5V have no PWR_FLAG/power_out. This is the known over-aggressive PWR_FLAG issue (KH-160 pattern): a connector-powered design where the power comes in through passive pins on J1. The D3/D4 zener clamping and R1 pullup architecture confirms USB signaling, not a supply-less schematic.
  (signal_analysis)

### Missed
- D3 and D4 are BZT52-C3V3 zener diodes used as USB D+/D- clamps (3.3V zeners on USB data lines, classic USB low-speed pull-up circuit with R2/R3=68 ohm). The analyzer reports empty protection_devices for this schematic. These should be classified as ESD/clamp protection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000865: Unrouted net correctly detected (routing_complete=false, unrouted_net_count=1)

- **Status**: new
- **Analyzer**: pcb
- **Source**: HARDWARE_topo.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- PCB has 1 unrouted net flagged. Small board (32.6x19.4mm), 2-layer, 16 footprints with 12 SMD. Statistics look plausible for a small ATtiny85+WS2812B USB HID board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
