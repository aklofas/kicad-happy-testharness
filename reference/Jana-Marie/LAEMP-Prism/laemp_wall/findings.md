# Findings: Jana-Marie/LAEMP-Prism / laemp_wall

## FND-00000209: LED wall panel with 41 SK6812 addressable LEDs and per-LED 100nF decoupling capacitors, powered from VBUS via 6-pin connector. The analyzer correctly identifies all components but fails to detect the LED daisy-chain due to missing pin-net mapping in legacy .sch parsing.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: laemp_wall_laemp_wall.sch.json
- **Created**: 2026-03-15

### Correct
- All 41 SK6812 LEDs (D1-D41) correctly classified as type 'led'
- All 43 100nF capacitors (C1-C43) correctly classified as type 'capacitor'
- J1 Conn_01x06 and J2 Conn_01x02 correctly classified as connectors
- SK6812 LEDs correctly recognized as addressable LED type with single-wire WS2812 protocol
- Component count accurate: 86 total (41 LEDs + 43 caps + 2 connectors)

### Incorrect
- 41 separate single-LED chains detected instead of one 41-LED daisy chain -- the SK6812 LEDs are connected DOUT-to-DIN in series but the legacy .sch parser returns empty pin lists for all LED components, preventing chain detection
  (signal_analysis.addressable_led_chains)

### Missed
- VBUS power rail decoupling not detected because capacitors have no pin-net associations in legacy .sch parse output (pins array is empty for all components)
  (signal_analysis.decoupling_analysis)

### Suggestions
- Improve legacy .sch pin-net extraction -- the parser is not resolving wire-to-pin connections for components in KiCad 4/5 format, resulting in empty pins arrays and broken signal detection
- Consider using wire geometry and component coordinates to infer pin connections when explicit pin-net data is unavailable

---
