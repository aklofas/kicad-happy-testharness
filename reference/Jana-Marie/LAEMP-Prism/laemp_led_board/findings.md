# Findings: Jana-Marie/LAEMP-Prism / laemp_led_board

## FND-00000210: LED board with 44 SK6812 addressable LEDs in a daisy chain with per-LED 100nF decoupling capacitors, dual 4-pin connectors for power and data. Analyzer correctly detects the full 44-LED chain and VBUS decoupling.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: laemp_led_board_laemp_led_board.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- 44-LED SK6812 daisy chain correctly detected from D1 through D44 with DIN input net and single-wire WS2812 protocol
- Estimated current of 2640mA (44 LEDs x 60mA) correctly calculated
- All 44 SK6812 LEDs correctly classified as type 'led'
- All 44 100nF capacitors correctly classified as type 'capacitor'
- J1 Conn_01x04 and J2 Conn_01x04 correctly classified as connectors
- VBUS decoupling rail correctly detected with 44 bypass caps totaling 4.4uF
- Design observation correctly notes VBUS rail has bypass but no bulk capacitor
- Component count accurate: 90 total (44 LEDs + 44 caps + 2 connectors)

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
