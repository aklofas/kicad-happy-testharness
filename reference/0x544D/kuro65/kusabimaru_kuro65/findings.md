# Findings: kuro65 / kusabimaru_kuro65

## FND-00000223: Kuro65 keyboard switches sheet (276 components). Key matrix 5x16 correctly detected with 69 keys. Critical: 69 SK6812MINI-E addressable LEDs misclassified as generic diodes, 0 addressable_led_chains detected. BOM shows 138 diodes but 69 are actually RGB LED ICs.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: kusabimaru_switches.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- Key matrix correctly detected: 5 rows x 16 columns, 69 switch-diode pairs, matrix structure valid
- 69 bypass capacitors (100nF each) correctly detected as decoupling, totaling 6.9uF

### Incorrect
- 69 SK6812MINI-E addressable RGB LED components (D74-D141) misclassified as generic diodes instead of addressable_led. BOM reports 138 diodes but only 69 are 1N4148 switch protection diodes.
  (statistics.component_types)

### Missed
(none)

### Suggestions
- Add SK6812/WS2812 addressable LED detection by library name pattern matching
- Build addressable_led_chains detection that identifies DIN->DOUT chaining topology
- Separate addressable LED components from generic diode classification

---
