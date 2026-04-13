# Findings: alexlargacha/BreadBoard_power_supply_KiCad / Breadboard_power_supply

## FND-00000388: Bridge rectifier formed by D1/D2/D3/D4 not detected; R1/C1 falsely detected as RC filter; R1 is the LED current-limiter for D5; design_observations incorrectly reports U1 input (Vin) and output (Vo...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Breadboard_power_supply.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The analyzer reports an RC filter with R1 (560R) and C1 (47uF) at 6.05 Hz. R1 and C1 share the Vout1 net but are not in series in an RC filter topology. R1 connects Vout1 to the cathode of LED D5 (net __unnamed_2), making it an LED current-limiting resistor. C1 is the output bulk capacitor across Vout1/V-. The node shared between R1 pin 1 and D5 cathode (__unnamed_2) does not connect to any capacitor, so no RC low-pass filter exists. Similarly for R2 and D6 on the Vout2 rail.
  (signal_analysis)
- The decoupling observation flags 'rails_without_caps: ["Vin"]' and the regulator_caps observation lists missing_caps for both input (Vin) and output (Vout1). In the actual schematic, C2 (470uF) is connected directly across the Vin rail and V-, and C1 (47uF) is connected across Vout1 and V-. Both input and output caps are present. The analyzer fails to recognise C2 as an input bulk/decoupling cap and C1 as an output bulk/decoupling cap for U1.
  (signal_analysis)
- The nets output shows __unnamed_1 containing only U1 pin 2 (GND), with point_count 1. In the schematic, a wire runs from U1's GND pin (4950, 2550) all the way down to y=4400, which is the same horizontal bus as the V- net label. The wire segment '4950 2550 → 4950 4400' connects directly to the V- bus at y=4400. The analyzer fails to trace this wire and leaves U1 GND disconnected from V-, producing a spurious isolated net and missing the ground connection for the regulator.
  (nets)
- The net_classification entry for 'V-' is 'signal'. V- is the circuit's negative/return power rail: it connects to capacitor negatives (C1, C2), diode cathodes (D2, D4), LED anodes (D5, D6), and the GND pins of both output connectors (J2 pins 3,4 and J3 pins 3,4). It carries ground-return current for the entire regulated output. It should be classified as 'power' or 'ground', not 'signal'.
  (design_analysis)
- Vout1 is the regulated 5V output of U1 (LM7805) driving output connectors J2/J3. Vout2 is the unregulated bypass output also driving J2/J3. Both serve as power supply output rails feeding the breadboard. Classifying them as 'signal' rather than 'power' understates their role in the design.
  (design_analysis)

### Missed
- D1, D2, D3, D4 (all 1N4007) are wired as a full-wave bridge rectifier: bj_pin1 feeds D2 anode and D1 cathode; bj_pin2 feeds D4 anode and D3 cathode; the Vin rail collects D1 and D3 anodes; V- collects D2 and D4 cathodes. This is a canonical bridge rectifier topology. The analyzer leaves bridge_circuits as an empty array and does not note the rectifier structure anywhere in signal_analysis.
  (signal_analysis)

### Suggestions
- Fix: V- net classified as 'signal' instead of 'power' or 'ground'
- Fix: Vout1 and Vout2 nets classified as 'signal' instead of 'power'

---
