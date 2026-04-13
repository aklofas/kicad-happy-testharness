# Findings: brucemack/iso9141-interface / hw_V2_iso9141-interface

## FND-00002224: LDO regulator (NCP1117-5.0) correctly identified with input +12V and output +5V; ISO9141 / K-line single-wire bus interface not recognized as a bus protocol; pwr_flag_warnings incorrectly fire for ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_iso9141-interface_hw_V2_iso9141-interface.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identified U1 as a 5V fixed LDO taking +12V as input and producing +5V for the microcontroller interface circuitry. The voltage divider (R6=47K, R7=22K) from KLINE to RX is also correctly detected, with ratio 0.319 that level-shifts the 12V K-line bus down to approximately 3.8V for the MCU RX input.
- The analyzer correctly flags four nets (KLINE, RX, CTL, IND0) as having inconsistent label shapes across the sub-sheets. For example, KLINE is marked bidirectional on one sheet and input on another, while RX, CTL, IND0 each mix input and output shapes. TX is also flagged as an undriven input label. These are real ERC issues in the design.

### Incorrect
- The V2 project is split across three sub-sheets (connectors, interface, iso9141-interface). The main sheet and the connectors sheet both have PWR_FLAGs, but analyzing each sheet in isolation causes the analyzer to emit pwr_flag_warnings for +12V and GND in the main interface sub-sheet (hw_V2_interface.kicad_sch). Those rails are properly flagged in the connectors sub-sheet. This is a known limitation of per-sheet analysis but is a false positive in terms of reporting ERC-relevant warnings.
  (signal_analysis)

### Missed
- This design is explicitly an ISO9141 K-line automotive bus interface. The schematic uses NPN transistors (Q1, Q2) to drive the KLINE net and a voltage divider (R6/R7) to receive from it. The analyzer detects the UART-named signals TX/RX on the microcontroller side, but does not recognize the K-line topology (single-wire bidirectional, 12V logic, pull-up to +12V through resistor, open-collector NPN drivers). No bus_analysis entry or design_observation for ISO9141/K-line is emitted.
  (signal_analysis)

### Suggestions
(none)

---
