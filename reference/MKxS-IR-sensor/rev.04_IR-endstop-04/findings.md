# Findings: MKxS-IR-sensor / rev.04_IR-endstop-04

## FND-00000125: Very simple IR filament sensor (8 components) has severe connectivity parsing failure. Only 4 of 8 components have pins parsed, all nets are single-pin unnamed nets except GND. 29 wires exist but netlist is essentially empty. The EE-SX1103 photomicrosensor is misclassified as generic IC.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/MKxS-IR-sensor/rev.04/IR-endstop-04.sch
- **Created**: 2026-03-14

### Correct
- Component count correct at 8 total
- Resistor values correctly parsed (330R, 10k, 56k)
- Component types mostly correct - resistors, diode, transistor, connector
- GND power rail detected with 11 connection points

### Incorrect
- U1 (EE-SX1103 photomicrosensor) classified as generic IC type - it is an optical sensor/optocoupler
  (bom)
- 4 of 8 components have no pins parsed (U1, P1, Q1, D2) - these use non-standard KiCad 5 library symbols with pin extraction failing
  (components)
- All 8 unnamed nets are single-pin orphans - the netlist is nearly completely disconnected despite 29 wires in the schematic
  (nets)
- GND net has 0 pins associated despite 11 connection points
  (nets)

### Missed
- IR LED current limiting resistor R1 (330R) circuit not detected
  (signal_analysis)
- Phototransistor output with Q1 (2N7002K MOSFET) level shifter circuit not detected
  (signal_analysis.transistor_circuits)
- Voltage divider R2/R3/R4 network for signal conditioning not detected
  (signal_analysis.voltage_dividers)
- BAT54K Schottky diode D2 ESD/clamp protection not detected
  (signal_analysis.protection_devices)
- No power rail detected other than GND - VCC/+5V rail should exist via connector P1
  (statistics.power_rails)

### Suggestions
- Fix KiCad 5 legacy pin parsing for symbols using non-standard library formats (opto, transistors, connectors)
- Net connectivity is fundamentally broken for this file - investigate wire-to-pin matching in legacy parser
- Classify optical sensors (EE-SX1103, LTV-817 lib_id) as sensor/optocoupler type rather than generic IC

---
