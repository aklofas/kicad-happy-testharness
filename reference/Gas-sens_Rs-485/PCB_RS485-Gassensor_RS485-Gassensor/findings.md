# Findings: Gas-sens_Rs-485 / PCB_RS485-Gassensor_RS485-Gassensor

## FND-00000202: RS485 gas sensor board with dual STM32G031K8 MCUs (U1 LQFP-32 active, U2 QFN-32 DNP), MCP6002 and AD8676 op-amps for gas sensor signal conditioning, OKI-78SR DC-DC converter, AP2127N LDO, RS485 transceiver (LT1785), and 4 sub-sheets. Thorough opamp detection and good voltage divider identification for sensor reference biasing.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: PCB_RS485-Gassensor_RS485-Gassensor.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- 6 opamp circuits correctly identified: U3 units 1-2 (MCP6002) for CO gas sensing, U6 units 1-2 (MCP6002) for NO gas sensing, U9 units 1-2 (AD8676) for output buffering
- U3 unit 2 correctly identified as transimpedance/buffer for CO output with R8 feedback (10R)
- U6 unit 1 correctly identified as comparator (no feedback) generating Counter_NO digital output
- U9 units 1-2 (AD8676) correctly identified as transimpedance/buffer with R16/R19 (2.2k) feedback for U_Out_CO and U_Out_NO outputs
- Voltage divider R14/R9 (2.2k/1k, ratio=0.31) correctly detected generating reference for U3 non-inverting input
- Voltage divider R27/R28 (1k/1k, ratio=0.5) correctly detected generating mid-rail reference for U6 comparator
- RC low-pass filters R17/C8 and R15/C4 (1k/470nF, fc=338.6Hz) correctly detected for PWM-to-analog conversion on gas sensor heater drives
- U4 (OKI-78SR-5) correctly identified as switching DC-DC converter from +24V to +5V
- U5 (AP2127N-3.3) correctly identified as LDO from +5V to +3.3V
- Dual MCU design correctly parsed: U1 (STM32G031K8Tx, in_bom=yes) and U2 (STM32G031K8Ux, dnp=yes) with matching pin counts
- 4 mounting holes (H1-H4) and 2 fiducials (FID1-FID2) correctly classified
- Power cascade +24V -> +5V -> +3.3V correctly reflected in regulator chain U4->U5

### Incorrect
- Current sense detection claims R12 (R220=0.22 ohm) is a shunt resistor with U7 (LT1785xS8) as sense IC on RS485-A/RS485-B nets. However, U7 is an RS485 transceiver, not a current sense amplifier. R12 is likely a termination or bias resistor, not a current shunt.
  (signal_analysis.current_sense)
- U4 (OKI-78SR-5_1.5-W36-C) estimated_vout=1.5V is wrong; it outputs 5V. The '1.5' in the part name refers to the 1.5A current rating, not the output voltage. The output rail is correctly labeled +5V.
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- Do not classify RS485 transceivers (LT1785, MAX485, etc.) as current sense ICs when they are adjacent to low-value resistors - these are typically bus termination/bias resistors
- Parse OKI-78SR part numbers correctly: the format is OKI-78SR-{Vout}_{Imax}-W{Vin_max}-C where the first number after the dash is the output voltage
- Investigate why capacitors on named power rails (+3.3V, +5V, +24V) are not being found in decoupling analysis - possible issue with hierarchical sheet net resolution

---
