# Findings: ONLYA/AR488-Bluetooth-Mega-2560 / AR488-Bluetooth

## FND-00000344: Boost regulator U4 (XC9141B50CMR-G) missing input_rail in power_regulators entry; U3 (Level_Shifter) not detected as a level-shifter interface — only classified as generic IC; U5 (MCP65R41T-1202E c...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: AR488-Bluetooth.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- design_analysis.power_domains.ic_power_rails.U5.power_rails includes 'IN-', but 'IN-' is a signal net carrying the MCP65R41T's internal 1.2V Vref output (pin 5) shorted to the inverting input (-IN, pin 4). The net_classification correctly identifies 'IN-' as 'signal'. The power_domains entry incorrectly promotes it to power_rail status because the analyzer sees a power-typed output pin (Vref) on the net, but the net is not a power supply domain.

### Incorrect
(none)

### Missed
- U4 pin 3 is named 'BAT' and connects to the '+BATT' net, which is clearly the input supply. The design_observations.switching_regulator observation records input_rail as null, and the power_regulators entry lacks the field entirely. The analyzer correctly detects the inductor (L1) and output_rail (+5V) but fails to resolve the input rail from the BAT-named power_in pin.
  (signal_analysis)
- U3 uses the AR488:Level_Shifter custom symbol, which has explicit LV/HV/LGND/HGND pin structure (classic BSS138 bidirectional MOSFET level shifter). It bridges the +3.3V domain (LV=+3.3V) to the +5V domain (HV=+5V), translating UART TX/RX and CE/STATE signals for the HC-05 Bluetooth module. The signal_analysis.level_shifters list is empty and no level-shifter detection fires. U3 appears only as a generic IC with function=''. The pin names are an unambiguous marker for level-shifter topology.
  (signal_analysis)
- U1 (SN75160BN) and U2 (SN75161BN) are TI octal GPIB bus transceivers — the core interface ICs in this design. Their source symbol definitions carry ki_keywords 'gpib bidirectional bus transceiver', but in ic_pin_analysis both show keywords as null and function as empty string. Neither appears in any bus-interface section of signal_analysis (no gpib_interfaces or bus_transceivers key exists). The GPIB bus topology is correctly identified in bus_topology.detected_bus_signals, but the ICs driving the GPIB lines are not linked to that topology.
  (statistics)

### Suggestions
(none)

---
