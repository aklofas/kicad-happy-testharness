# Findings: PDH_photodiode / KiCad_PDH_photodiode

## FND-00001035: LTC6228HS8 (U3) misclassified as power regulator instead of op-amp; V- net classified as 'signal' instead of 'power'; C10 and C11 (value='DNF') not flagged as DNP, dnp_parts=0; RC filter topology f...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PDH_photodiode.kicad_sch
- **Created**: 2026-03-23

### Correct
- U2A detected as transimpedance_or_buffer (feedback resistor R3=20k, non-inverting input to GND — correct for TIA with photodiode). U2B detected as compensator with feedback R/C. Both configurations are accurately classified.
- Two 100k/100k dividers from V+ and V- to GND setting the LT3032 output voltages are correctly identified, with mid-point connections to U1 ADJP and ADJN pins.

### Incorrect
- U3 (LTC6228HS8) appears in both power_regulators (topology: unknown) and opamp_circuits (correctly as unity-gain buffer). The power_regulators entry is a false positive — LTC6228 is a high-speed op-amp, not a regulator. The real regulator is LT3032 (U1), which is absent from power_regulators.
  (signal_analysis)
- V- is the negative supply rail (output of LT3032 dual regulator, connected to V- pins of U2 and U3 op-amps). net_classification shows 'V-': 'signal' which is wrong; it should be 'power' or 'negative_supply'. Also, power_domains only shows V+ for U1/U2/U3, missing V-.
  (signal_analysis)
- Components C10 and C11 have value 'DNF' (Do Not Fit), a common KiCad convention for unpopulated parts, but the analyzer reports dnp_parts=0 and dnp=false for both. The analyzer should detect 'DNF' as a DNP marker in the value field.
  (signal_analysis)
- The rc_filters entry shows R1(1k)+C7(10n) as 'high-pass' with cutoff 15.92 kHz. However, the same C7 also appears in the subsequent low-pass filter with R8/C8 as parallel caps. If C7 is shunted to ground after R1, the topology through R1 to C7 is low-pass (signal passes R1, C7 shunts to GND), not high-pass. Needs source inspection to confirm but the labeling is suspicious.
  (signal_analysis)

### Missed
- U1 (LT3032) is a dual ±5V linear regulator that is the main power supply IC on this board. It is absent from power_regulators. The voltage divider networks on ADJP/ADJN pins feeding U1 are correctly found, but the regulator itself is missed.
  (signal_analysis)
- The design has C2 and C6 (10u each) on the V- negative supply rail, plus C9/C14 (100n) also on V-. The decoupling_analysis only reports V+ rail coverage. This is a systematic miss for negative supply decoupling.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001036: PCB statistics, routing, and layer structure correctly extracted

- **Status**: new
- **Analyzer**: pcb
- **Source**: PDH_photodiode.kicad_pcb
- **Created**: 2026-03-23

### Correct
- 38 footprints, 2-layer, 212 segments, 27 vias, routing complete. Board has a non-rectangular outline (arcs + lines, 18 edges), correctly captured. Unconnected nets for NC pins (U1A-NC, shutdown pins) correctly listed in nets.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
