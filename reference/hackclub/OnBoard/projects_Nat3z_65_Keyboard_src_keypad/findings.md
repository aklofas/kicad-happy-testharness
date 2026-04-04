# Findings: OnBoard / projects_Nat3z_65_Keyboard_src_keypad

## FND-00000099: ATmega32U4 65-key keyboard with USB-C, crystal, and fuse protection. Good matrix and signal detection but IC refs missing.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/Nat3z_65_Keyboard/src/keypad.kicad_sch
- **Created**: 2026-03-14

### Correct
- Correctly detected 65-key matrix with 4 rows (ROW0-ROW3) and COL5 column net, 65 switches and 65 diodes
- Correctly identified 16MHz crystal with 22pF load caps and calculated effective CL of 14pF
- Correctly detected 500mA fuse on USB power
- Correctly identified USB D+/D- lines lacking ESD protection
- Correctly detected +5V decoupling with 0.1uF + 10uF totaling 10.3uF

### Incorrect
- Key matrix reports only 1 column (COL5) but there should be ~16 columns for a 65-key 4-row matrix - likely only detected one column net while others use different naming
  (signal_analysis.key_matrices)
- IC pin analysis shows ref=? for ATmega32U4-A, crystal, and USB connector - reference designators not populated
  (ic_pin_analysis)
- IC function not identified for ATmega32U4-A - should be AVR 8-bit microcontroller with USB
  (ic_pin_analysis)

### Missed
- Crystal frequency 16MHz detected in value but frequency field is None - should parse numeric frequency from value string
  (signal_analysis.crystal_circuits)
- USB series resistors R2/R3 on D+/D- not analyzed for value correctness (22 ohm typical for USB)
  (signal_analysis)

### Suggestions
- Key matrix column detection should find all column nets, not just one
- Crystal frequency should be parsed from value string when possible
- IC function lookup for ATmega32U4 should identify it as AVR MCU with USB

---
