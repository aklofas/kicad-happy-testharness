# Findings: TU-Darmstadt-APQ/DIN_41612_Backplane / backplane

## FND-00002588: 19-inch DIN 41612 backplane with dual +/-15V rails, input protection using ADM1270 hot-swap controller with P-channel MOSFETs (SQM120P06), SMBJ40CA TVS diodes, and per-slot bulk/bypass capacitors. Analyzer provides thorough analysis of this power distribution design.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: backplane.kicad_sch.json

### Correct
- Voltage divider R8/R9 (30.1k/10k) correctly detected feeding U1 (ADM1270) OV pin with ratio 0.249, used for overvoltage threshold setting
- Feedback network R6/R7 (1.65k/10k) correctly identified as feeding U1 (ADM1270) FB_PG pin, marked as is_feedback=true
- Four low-pass RC filters (R20/C31, R12/C18, R10/C15, R1/C1 all 22R/1u) at 7.23 kHz correctly detected as input filtering on the MOSFET source/drain paths
- Protection devices D2 and D3 (SMBJ40CA bidirectional TVS) correctly detected on the Vin rail
- Q1, Q2 (SQM120P06 P-channel MOSFET) correctly detected as MOSFET transistor circuits with U1 (ADM1270) as gate driver for Q1
- Q3, Q4 (SQJQ160E) correctly detected as MOSFET transistor circuits
- U1 (ADM1270) and U2 (LM5067) correctly classified as ICs
- Extensive decoupling analysis: +15V rail with 9x 220uF + 100nF (1980.1uF total), -15V rail with similar bulk capacitance, Earth rail with 2x 10nF safety caps
- 146 components including 52 mounting holes (DIN 41612 connector mounting), 15 connectors, 31 capacitors correctly counted
- FB1, FB2 (12R @ 100 MHz) correctly classified as ferrite_bead type
- D5 (BZT52H-B15) zener diode and D4 (3.5 mA current source diode) correctly classified

### Incorrect
(none)

### Missed
(none)

### Suggestions
- The ADM1270 hot-swap controller could be specifically identified in power_regulators or protection_devices as a hot-swap/inrush controller, since its primary purpose is power path management.

---

## FND-00002589: Positive rail input protection sub-sheet with ADM1270 hot-swap controller, dual SQM120P06 P-channel MOSFETs, TVS protection (SMBJ40CA), and RC input filtering. Analyzer correctly captures this focused protection circuit.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: input_protection_positive_sch.kicad_sch.json

### Correct
- Voltage divider R8/R9 (30.1k/10k) correctly detected feeding U1 OV pin for overvoltage threshold at ratio 0.249
- Feedback divider R6/R7 (1.65k/10k) correctly identified as feedback to U1 FB_PG pin with is_feedback=true
- RC low-pass filters R10/C15 and R1/C1 (both 22R/1u at 7.23 kHz) correctly detected
- D2 (SMBJ40CA) correctly detected as protection device on Vin rail clamping to GND
- Q1 (SQM120P06) correctly identified as P-channel MOSFET with U1 (ADM1270) as gate driver IC
- Q2 (SQM120P06) correctly identified as P-channel MOSFET
- R3 (3m ohm sense resistor) correctly classified as resistor; it serves as current sense for the ADM1270
- 25 components correctly counted: 10 resistors, 6 capacitors, 1 diode, 1 LED, 1 ferrite bead, 1 test point, 2 net ties, 2 transistors, 1 IC
- Vout rail decoupling with C2 (100nF) correctly identified with design observation about single cap, no bulk

### Incorrect
(none)

### Missed
- R3 (3m ohm) is a current sense resistor for the ADM1270 hot-swap controller (connected to its SENSE pin) but was not detected as a current_sense element.
  (signal_analysis.current_sense)

### Suggestions
- Very low value resistors (milliohm range like R3=3m) connected to hot-swap controller sense pins should be identified as current sense resistors.

---
