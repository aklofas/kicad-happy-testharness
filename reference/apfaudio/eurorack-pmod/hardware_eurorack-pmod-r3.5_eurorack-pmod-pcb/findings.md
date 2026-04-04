# Findings: eurorack-pmod / hardware_eurorack-pmod-r3.5_eurorack-pmod-pcb

## FND-00000261: Eurorack FPGA audio PMOD interface r3.5 (153 components). MMBFJ111 JFETs misclassified as MOSFET. 14/15 RC filters are opamp feedback pairs, not standalone filters. Voltage dividers are actually opamp feedback networks.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_eurorack-pmod-r3.5_eurorack-pmod-pcb.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- AK4619VN audio codec correctly classified as IC
- TL074/TL072 opamp compensator configurations correctly identified
- Power regulators correctly detected

### Incorrect
- Q2-Q5 MMBFJ111 JFETs classified as 'mosfet' — signal_detectors.py hardcodes type='mosfet' for all FETs with no JFET distinction
  (signal_analysis.transistor_circuits)
- 14 of 15 RC filters are opamp feedback R+C pairs (output-to-inverting-input), not standalone filters — only R35+C32 is genuine
  (signal_analysis.rc_filters)
- R27/R28 and R19/R20 voltage dividers are actually opamp feedback networks (R27 is feedback from U2 output to inverting input)
  (signal_analysis.voltage_dividers)

### Missed
- U11 LTV-357T optocoupler not detected as isolation component — only one ground net (GNDD) and 'Isolator' in lib_id doesn't match keyword 'isolated'
  (signal_analysis.isolation_barriers)

### Suggestions
- Add JFET vs MOSFET distinction in transistor classification
- RC filter detector should exclude R+C pairs already identified as opamp feedback components
- Voltage divider detector should exclude resistor pairs forming opamp feedback/gain-setting networks
- Add 'isolator' as keyword for isolation barrier detection

---

## FND-00000262: Eurorack FPGA PMOD r3.1 (116 components). Same RC filter false positive pattern as r3.5. Resistor network in opamp feedback path not detected.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_eurorack-pmod-r3.1_eurorack-pmod-pcb.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- TL074/TL072 opamp configurations correctly identified

### Incorrect
- 14 of 15 RC filters are opamp feedback pairs, only R33+C27 (VREF filter) is genuine
  (signal_analysis.rc_filters)
- U9 unit 2 TL072 classified as 'comparator_or_open_loop' — feedback through RN7 (resistor_network type) missed because 2-hop detection only looks for 'resistor' type, not 'resistor_network'
  (signal_analysis.opamp_circuits)

### Missed
(none)

### Suggestions
- Opamp feedback path detection should include 'resistor_network' component type in 2-hop search

---
