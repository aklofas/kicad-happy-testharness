# Findings: keypad / KP08Hub_keypad_KP08Hub_keypad

## FND-00000244: USB hub (23 components). Incorrect regulator topology: U3 (CY7C65642 USB hub IC) VREG pin classified as LDO output but it is actually a reference input pin.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KP08Hub_keypad.kicad_sch.json
- **Created**: 2026-03-16

### Correct
(none)

### Incorrect
- U3 CY7C65642 USB hub IC VREG pin classified as LDO regulator output, but VREG is actually a voltage reference input pin
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- Do not classify IC pins named VREG as regulator outputs without verifying the IC is actually a regulator

---
