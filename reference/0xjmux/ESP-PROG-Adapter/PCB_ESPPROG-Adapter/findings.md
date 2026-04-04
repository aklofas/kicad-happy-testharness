# Findings: ESP-PROG-Adapter / PCB_ESPPROG-Adapter

## FND-00000491: All four components correctly identified with correct refs, types, and footprints; Net connectivity for JTAG signals (TMS, TCK, TDI, TDO) correctly traced between J2 and J3; Reset net (~{RST}) corr...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ESP-EZ-Debug-KicadLib_UsageExamples.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- J1 (ESP8266 SOICbite UART), J2 (SOICbite JTAG), J3 (TC2050 JTAG), J4 (ESP8266 SOICbite UART) are all correctly parsed. All have in_bom=false, which correctly yields unique_parts=0 and an empty bom array. Component types (connector) and lib_ids match the source.
- Net TMS connects J3 pin 2 and J2 pin 2. Net TCK connects J3 pin 4 and J2 pin 3. Net TDI connects J3 pin 8 and J2 pin 5. Net TDO connects J3 pin 6 and J2 pin 6. All four nets are correctly populated with the right pins from both connectors.
- The ~{RST} net includes all four connectors at the right pins, correctly cross-referencing different pin names for the same reset signal across different symbol libraries.
- Net RX connects J1 pin 5 and J4 pin 5. Net TX connects J1 pin 6 and J4 pin 6. The BOOT net connects J1 pin 2 (GPIO0) and J4 pin 2 (GPIO0). All correct.
- J3 (TC2050 JTAG) and J2 (SOICbite JTAG) are detected as interface=jtag. J1 and J4 (SOICbite-ESP8266) are detected as interface=uart. All four appear in debug_connectors with the correct connected nets.
- The +3.3V net includes J1 pin 1 (VCC), J2 pin 1 (VT_{ref}), J3 pin 1 (VTref), J4 pin 1 (VCC), plus four #PWR symbols. The Earth net correctly connects the GND pins of all four connectors.
- Both J1 and J4 SOICbite-ESP8266 connectors receive function='microcontroller (ESP)', which is contextually appropriate given the symbol name and keyword 'ESP'. J3 (TC2050) has function='' (empty) and J2 (SOICbite-JTAG) has function='', which is also correct since they are pure connectors.

### Incorrect
- The analyzer creates net entries for '{UART}' and '{JTAG}' with pins=[] and point_count=2. These are schematic text labels used as annotation only (not net labels driving connectivity). In the source schematic these are graphical labels on the drawing but not actual nets connecting to any pin. Creating empty net entries and classifying them as 'data' and 'debug' in net_classification is misleading. They also appear in uncovered_key_nets as uart nets, which is incorrect.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000492: All 12 components correctly parsed with correct references, values, lib_ids, and in_bom flags; statistics.dnp_parts reports 0 but J8 has dnp=yes in the source; JTAG net routing between J1, J3, J9 c...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_ESPPROG-Adapter.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- JP1 (ESPPROG_TX_RX_JUMP), JP2 (CH_PD EN), JP5 (TX→RX), JP6 (RX→TX), JP7 (JTAG ~{RST}), J1 (Conn ESP-Prog JTAG), J2 (Conn ESP-Prog UART), J3 (DebugHeader_Cortex-M_JTAG_10p_TagConnect), J5 (SOICBite connector UART Loopback), J7 (SOICBite IDC UART), J8 (SOICBite connector numbering order, DNP), J9 (SOICBite IDC JTAG) — all 12 components are present with correct reference, value, lib_id, footprint, and in_bom fields. J8 correctly has dnp=true.
- ESP_TMS connects J1 pin 2, J3 pin 2 (TMS), J9 pin 3. ESP_TCK connects J1 pin 4, J3 pin 4 (TCK), J9 pin 5. ESP_TDO connects J1 pin 6, J3 pin 6 (TDO), J9 pin 6. ESP_TDI connects J1 pin 8, J3 pin 8 (TDI), J9 pin 8. JTAG_VDD connects J1 pin 1, J3 pin 1 (VTREF), J9 pin 1. All correct.
- JP1 (jmux-kicadlib:ESP-Prog-Adapter-Reversible-UART) is a 2-unit component. Both unit 1 and unit 2 appear as separate component entries in the components list with distinct uuids and y-positions. The nets ESP_RXD0 and ESP_TXD0 correctly reference both units' pins (e.g., JP1 pin 1 and JP1 pin 2 from unit 1, plus JP1 pins 5 and 6 from unit 2 for the TX0 outputs).
- The ESP_EN net is shared across all three connector interfaces (UART header J2, SOICbite UART J7, SOICbite JTAG J9) plus the solder jumper JP7. This represents the ESP chip-enable signal routing. Net connectivity is fully and correctly traced.
- J1 (Conn ESP-Prog JTAG) interface=jtag, J3 (DebugHeader_Cortex-M_JTAG_10p_TagConnect) interface=jtag, J9 (SOICBite IDC JTAG) interface=jtag. J2 (Conn ESP-Prog UART) interface=uart, J5 (SOICBite connector UART Loopback) interface=uart, J7 (SOICBite IDC UART) interface=uart. All six correctly categorized.
- The schematic uses 'Earth' and 'VDD_U' power symbols (#PWR01–#PWR08 are Earth; VDD_U appears on J7/J2 VDD rails). JTAG_VDD is not a power symbol — it is a net label connecting VTREF pins — so its omission from power_rails is correct.
- The source schematic contains exactly 18 (no_connect ...) entries (lines 2543–2611). The analyzer reports total_no_connects=18, which is correct.
- J1, J2, J3, J7, J9 (connectors) and JP1 (ESPPROG_TX_RX_JUMP) are the 6 in_bom=true parts. JP2, JP5, JP6, JP7 (solder jumpers with in_bom=false), J5 (in_bom=false), and J8 (in_bom=false, DNP) are all correctly excluded from the bom array. unique_parts=6 is correct.

### Incorrect
- J8 (SOICBite connector numbering order) has (dnp yes) in the source schematic at line 5251. The analyzer correctly sets dnp=true on the J8 component record but reports statistics.dnp_parts=0. The counter is not being incremented for components flagged as DNP. The correct value should be 1.
  (signal_analysis)
- The connectivity_issues.single_pin_nets section is empty ([]) despite numerous single-pin nets in the netlist. Nets __unnamed_1 through __unnamed_8 each have exactly one pin (all on J8, point_count=1). Nets __unnamed_9 (J3 pin 7 RTCK), __unnamed_10 (J3 pin 9 ~{TRST}), __unnamed_11 (J7 pin 5), __unnamed_19 (J1 pin 10) are also effectively single-pin nets. The analyzer is not flagging these, likely because J8 is DNP and the unnamed nets from DNP components may be excluded, but __unnamed_9, __unnamed_10, __unnamed_11, and __unnamed_19 are on non-DNP components and should appear.
  (signal_analysis)

### Missed
- The bus_analysis.uart section correctly lists four UART nets (ESP_RXD0, ESPPROG_RX, ESP_TXD0, ESPPROG_TX). However, bus_analysis contains no 'jtag' section despite the presence of named nets ESP_TMS, ESP_TCK, ESP_TDI, ESP_TDO that form a complete JTAG bus. The analyzer detects JTAG connectors in test_coverage but does not synthesize a JTAG bus entry in bus_analysis. The same issue exists for UsageExamples.kicad_sch where TMS, TCK, TDI, TDO nets form a JTAG bus that goes undetected in bus_analysis.
  (signal_analysis)

### Suggestions
(none)

---
