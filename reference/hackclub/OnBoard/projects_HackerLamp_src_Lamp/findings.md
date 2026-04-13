# Findings: hackclub/OnBoard / projects_HackerLamp_src_Lamp

## FND-00000106: HackerLamp with 100 SK6812 addressable LEDs driven by XIAO-RP2040. Very minimal analysis - only decoupling warning produced.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/HackerLamp/src/Lamp.kicad_sch
- **Created**: 2026-03-14

### Correct
- Correctly identified 100 LEDs and 1 IC (XIAO-RP2040-DIP)
- Correctly flagged missing decoupling on VCC rail for XIAO-RP2040

### Incorrect
- IC function not identified for XIAO-RP2040-DIP - should be identified as Seeed XIAO RP2040 dev board
  (ic_pin_analysis)

### Missed
- SK6812 addressable LED chain topology not detected - 100 LEDs in a daisy-chain DIN/DOUT pattern is a significant signal path
  (signal_analysis)
- No power analysis despite 100 addressable LEDs drawing significant current (up to 6A at full white)
  (signal_analysis.power_regulators)
- No connector analysis - XIAO-RP2040 has USB-C on-board for programming
  (statistics.component_types)
- XIAO-RP2040-DIP is a dev board module containing RP2040, USB-C, and power regulation - this context is missing
  (ic_pin_analysis)
- Only 2 unique parts and 101 components but no subcircuit detection of the LED array
  (subcircuits)

### Suggestions
- Detect WS2812/SK6812 LED chain topology as a significant signal pattern
- Flag power budget concerns for large LED arrays (each SK6812 draws up to 60mA)
- Identify common dev board modules (XIAO, Arduino Nano, etc.) and their capabilities

---
