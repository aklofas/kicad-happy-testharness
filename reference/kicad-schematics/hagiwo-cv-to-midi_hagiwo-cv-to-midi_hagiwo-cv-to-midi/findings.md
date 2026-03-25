# Findings: kicad-schematics / hagiwo-cv-to-midi_hagiwo-cv-to-midi_hagiwo-cv-to-midi

## FND-00002348: Correctly detects dual RC high-pass and low-pass filters in SSI2131 VCO circuit; LM4040DBZ-2.5 shunt voltage reference (U2) not detected as a voltage reference or regulator

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-schematics_ssi2131_ssi2131.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer found 2 RC filters in the SSI2131 eurorack VCO schematic (R4/C1 high-pass at 1591 Hz, and another RC pair), along with decoupling analysis for the +5V and -12V rails. The design uses split power rails (+5V, -12V, +2V5) and the analyzer correctly reports all three power domains.

### Incorrect
(none)

### Missed
- U2 is an LM4040DBZ-2.5 precision shunt voltage reference providing a +2V5 reference rail to the SSI2131 VCO. The analyzer classifies it generically as 'ic' and finds no power_regulators. The +2V5 power rail exists in the design but no voltage reference or regulator is reported for U2. The analyzer should recognize LM4040 as a shunt reference device.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002349: False positive I2C bus detection: SDA/A4 pin used as analog CV input, not I2C

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-schematics_hagiwo-mozzi-2osc_mozzi2osc_mozzi2osc.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The analyzer detects an I2C bus on net 'CV' because Arduino Nano Every pin 23 is named 'SDA/A4' and the net name happens to match. However, the net named 'CV' (control voltage) is used as an analog audio input with a voltage divider (R6 1k series, R4 100k pull-down) and Schottky diode clamps — clearly an analog signal path, not a digital I2C bus. The paired SCL/A5 pin (pin 24) is on an unnamed net with no connected devices, confirming this is not an active I2C bus. The I2C detection is driven by pin naming heuristics rather than actual bus topology.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002350: Empty schematic (shell file with no components) handled gracefully with zero counts

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematic_kicad-schematics_thomas-henry-555_thomas-henry-555_thomas-henry-555.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The thomas-henry-555 schematic file is a skeleton with only the header (kicad_sch version 20211123) and empty lib_symbols/symbol_instances sections — no actual components, wires, or nets. The analyzer correctly produces all-zero statistics (total_components=0, total_nets=0, total_wires=0) with no crashes or spurious detections, and the .err file shows a clean write message.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002351: Empty schematic shell handled gracefully — sequential-switch-4-1 is also a stub file

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematic_kicad-schematics_sequential-switch-4-1_sequential-switch-4-1_sequential-switch-4-1.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Like thomas-henry-555, the sequential-switch-4-1 schematic is a KiCad 6 stub file with no symbols or wires. The analyzer produces zero counts with no errors. Both stub schematics coexist in the kicad-schematics repo alongside fully-populated schematics (hagiwo-mozzi, ssi2131), confirming the analyzer handles mixed-completion repos without issue.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
