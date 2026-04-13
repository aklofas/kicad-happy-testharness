# Findings: hackclub/OnBoard / projects_Hugo's Keyboard_src_keyboar!

## FND-00000096: Hugo keyboard with KB2040 MCU, 76-key matrix using GPIO naming (A0-A3, D0-D13 etc). Matrix not detected, IC/connector refs missing, KiCad version unknown.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/Hugo's Keyboard/src/keyboar!.kicad_sch
- **Created**: 2026-03-14

### Correct
- Correctly identified 76 switches and 76 diodes in a keyboard layout
- Correctly identified USB-C receptacle, JST SH, and 2.54mm connectors
- Correctly identified 5.1K CC resistors for USB-C
- Correctly flagged missing decoupling caps on +3V3 and VBUS rails
- Correctly flagged RST pin lacking pullup resistor

### Incorrect
- IC pin analysis shows ref=? for all components - reference designators not populated
  (ic_pin_analysis)
- IC function field is ? for KB2040 - should be identified as RP2040-based dev board/microcontroller
  (ic_pin_analysis)
- KiCad version reported as unknown despite file_version 20211123 indicating KiCad 6.x
  (kicad_version)

### Missed
- Key matrix not detected despite 76 switches with diodes connected to GPIO nets (A0-A3 rows, D0-D13+MISO+MOSI+SCK columns) - net names use Arduino-style GPIO names instead of ROW/COL
  (signal_analysis.key_matrices)
- USB data lines D+/D- not flagged for ESD protection analysis
  (signal_analysis.design_observations)
- KB2040 is an Adafruit RP2040 dev board - could provide more context about the module
  (ic_pin_analysis)

### Suggestions
- Key matrix detector should handle arbitrary GPIO net names, not just ROW/COL patterns
- IC pin analysis should populate ref fields from component data
- File version 20211123 should map to KiCad 6.x

---
