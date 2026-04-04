# Findings: E159-KICAD-Design-File / AVR_Controller_E159_E3

## FND-00000487: All 14 component references, values, and types extracted correctly; Net connectivity for U1 ATmega328-P is fully and correctly extracted; Crystal oscillator circuit detected with correct load capac...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: AVR_Controller_E159_E3.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All 14 components (SW1, J1, J2, J3, U1, U2, C1-C6, R1, Y1) are identified with correct reference, value, footprint, lib_id, and type classification. Component counts match: 1 switch, 3 connectors, 6 capacitors, 1 resistor, 1 crystal, 2 ICs.
- All 28 pins of U1 are traced correctly. Examples verified: pin 1 (~RESET/PC6) connects to SW1 pin 1, R1 pin 1, J1 pin 5; pins 9/10 (XTAL1/XTAL2) connect to Y1 with C3/C4; pins 2-6, 11-13 route PortD to J3; pins 17-19 route PB3/PB4/PB5 to J1; pins 7 and 20 (VCC, AVCC) on +5V; pins 8 and 22 (GND) on GND.
- Y1 (16MHz) is detected as a crystal circuit. Load caps C3 (22pF, net __unnamed_5, XTAL1 side) and C4 (22pF, net __unnamed_4, XTAL2 side) are correctly identified. Effective load capacitance computed as 14pF (series combination + stray). This matches the actual schematic wiring.
- R1 is correctly identified as a pull-up on U1 pin 1 (~RESET/PC6), with direction 'pull-up' and target net '+5V'. The net __unnamed_0 connects R1 pin 1 to U1 pin 1, SW1 pin 1, and J1 pin 5 (ISP RESET).
- U2 (LM7805_TO220) is detected as a power regulator with input rail '__unnamed_24' (the unregulated supply from J2 barrel jack) and output rail '+5V'. The decoupling cap C1 (0.33uF) on the input pin (VI, pin 1) is correctly identified.
- total_no_connects=9 matches exactly the 9 no_connect markers in the schematic source (on U1 left-side pins at x=163.83: y=54.61, 57.15, 59.69, 77.47, 80.01, 82.55, 85.09, 87.63, 90.17). These correspond to U1 PC0-PC5 (analog) and PB0-PB2.

### Incorrect
- The signal_analysis.power_regulators and design_analysis entries classify U2 (LM7805_TO220) with topology 'LDO'. The LM7805 is a classic NPN-pass linear regulator requiring Vin > Vout + ~2.5V dropout — it is not an LDO (low dropout) device. LDOs (e.g., LP2950, MCP1700) have dropout below 0.5V. This label is factually incorrect and could mislead design reviews.
  (signal_analysis)
- The pwr_flag_warnings array reports: 'Power rail GND has power_in pins but no power_out or PWR_FLAG'. However, the power_symbols list includes two PWR_FLAG instances at (96.52, 67.31) and (100.33, 62.23). Tracing the schematic wiring: PWR_FLAG at (96.52, 67.31) is connected to the GND junction at y=67.31, which connects to the GND rail. The warning is a false positive — GND does have a PWR_FLAG.
  (signal_analysis)
- The design_observations array contains an entry with category 'regulator_caps', component 'U2', and missing_caps: {input: '__unnamed_24'}. But the ic_pin_analysis for U2 already shows C1 (0.33uF) in decoupling_caps for the VI input pin, and the decoupling_caps_by_rail for U2 includes __unnamed_24: [C1]. The observation is internally inconsistent — C1 is found as a decoupling cap but then the design_observations incorrectly reports the input cap as missing.
  (signal_analysis)
- The assembly_complexity section reports smd_count=4 and tht_count=10 (total 14). However, all components in this design have explicitly THT footprints: C_Disc (THT), R_Axial (THT), DIP-28 (THT), TO-220-3_Vertical (THT), Crystal_HC49-4H_Vertical (THT), BarrelJack_Horizontal (THT), PinHeader (THT), SW_PUSH_6mm (THT). The correct smd_count should be 0, tht_count should be 14.
  (signal_analysis)

### Missed
- J1 (Conn_02x03_Odd_Even, 2x3 ISP header) connects U1 PB3/MOSI (pin 17) to J1 pin 4, PB4/MISO (pin 18) to J1 pin 1, PB5/SCK (pin 19) to J1 pin 3, RESET to J1 pin 5, +5V to J1 pin 2, and GND to J1 pin 6. This is the standard 6-pin AVR ISP SPI programming interface. The bus_analysis.spi array is empty and the connector is not identified as an ISP/SPI port.
  (signal_analysis)
- U1 pin 2 (PD0/RXD) connects to J3 pin 8 and U1 pin 3 (PD1/TXD) connects to J3 pin 7. These are the ATmega328's primary UART RX/TX pins routed to the 8-pin I/O header J3. The bus_analysis.uart array is empty. The test_coverage observation 'No debug connectors (SWD/JTAG/UART) identified' is consistent but the UART signal path itself is not analyzed.
  (signal_analysis)
- U1 AVCC (pin 20) and VCC (pin 7) are both connected directly to the +5V rail with no separate LC or ferrite bead filter for AVCC. The ATmega328 datasheet recommends an LC filter on AVCC for ADC accuracy. The decoupling analysis only reports C5 and C6 as shared between VCC and AVCC on +5V. No observation is generated about the lack of an AVCC-specific filter.
  (signal_analysis)

### Suggestions
(none)

---
