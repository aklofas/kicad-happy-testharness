# Findings: cansat-ptl/cubesat-boards / ykts-geigerboard

## FND-00000283: CubeSat Geiger counter board (102 components). LM2733YMF boost converter output rail same as input (doesn't trace past rectifier diode). L2+C18 AVR AVCC filter misclassified as RF matching. Unitless pF capacitor values parsed as Farads producing absurd time constants. Gate_driver_ics inflated via +3V3 power net traversal.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ykts-geigerboard_ykts-geigerboard.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- AD8606ARZ dual opamp detected as comparator_or_open_loop — correct, no feedback network
- 2 crystal circuits (Y1/Y2 8MHz) with 22pF load caps correct
- Voltage divider R6(100)/R4(12K) for Geiger pulse comparator input correct
- LC filter L3+C25/C26 (10uH+2.3uF) at 33kHz for boost output correct

### Incorrect
- LM2733YMF (U9) output_rail=__unnamed_18 (same as input) — true HV output is __unnamed_15 after rectifier diode D4 MBR0520LT, not traced past diode
  (signal_analysis.power_regulators)
- 9 capacitors with unitless pF values (220, 470, 510, 1000, 2200) parsed as Farads — time constants up to 4.84 billion seconds, LC resonant frequencies of 0.00Hz
  (signal_analysis.rc_filters)
- Q1/Q2 gate_driver_ics lists 9 ICs via +3V3 power net traversal — gates are statically biased, not driven by any IC
  (signal_analysis.transistor_circuits)

### Missed
(none)

### Suggestions
- Boost converter output: trace through catch/rectifier diode to find true output rail
- RF matching: exclude detections where target is connected via AVCC/VCC power pin
- Capacitor parser: treat bare numbers without unit suffix as pF when in realistic range
- Skip power nets when collecting gate_driver_ics

---
