# Findings: kicad_rf_detector / v1_rev-_kicad_rf_detector

## FND-00002369: RV1 potentiometer (Device:R_POT_US) classified as 'resistor' component type; RF detector signal chain not detected — Schottky diode envelope detector with RF input and LC filter; RC filter detected...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad_rf_detector_v1_rev-_kicad_rf_detector.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- RV1 is a Bourns 3314G 10k SMD trimmer potentiometer with lib_id 'Device:R_POT_US' and footprint 'Potentiometer_SMD:Potentiometer_Bourns_3314G_Vertical'. The analyzer classifies it as type 'resistor' in both the BOM and component_types. It should be a distinct type like 'potentiometer' or 'variable_resistor'. This also means the RC filter detection uses the potentiometer as a fixed 10k resistor with a calculated cutoff of 15.92 kHz, which is misleading since the resistance is variable.
  (statistics)
- The detected RC low-pass filter reports input_net='__unnamed_6' (RV1 wiper/pin 2) and output_net='__unnamed_3' (L1/C4 junction, before the wiper). In the actual circuit, RF power flows from J1 through D1 and L1 into net __unnamed_3 (the detected DC voltage node), then through the RV1 pot to the wiper output. The RC filter topology and cutoff calculation (15.92 kHz) may be structurally questionable since RV1 is a variable resistor and the signal direction is from __unnamed_3 toward __unnamed_6, not the reverse.
  (signal_analysis)

### Missed
- This is a classic RF envelope detector: SMA input J1 → input coupling capacitor C1 (5pF) → Schottky diode D1 (SMS7630-005LF, a zero-bias Schottky for RF detection) with C2/C3 bypass caps → inductor L1 (100nH) RF choke → C4 output filter → RV1 trimmer output. The rf_chains and rf_matching arrays are both empty. The analyzer should detect at minimum the Schottky diode in an RF context (no forward bias DC source, connected to RF input connector) and the LC network as RF-frequency filtering (~15 MHz resonance). The design_observations list is also empty.
  (signal_analysis)

### Suggestions
(none)

---
