# Findings: ronaldsieber/ESP32SmartBoard_PCB / ESP32SmartBoard_PCB

## FND-00000498: U1 VIN and 3V3 pins incorrectly placed in GND net; U1 GND pin incorrectly placed in VIN rail net; U2 MH-Z19B RXD (pin 2) and TXD (pin 3) appear as isolated single-pin nets despite being wired; UART...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ESP32SmartBoard_PCB_ESP32SmartBoard_PCB.sch.json
- **Created**: 2026-03-23

### Correct
- All 32 components are correctly identified: U1 (ESP32_DevKit), U2 (MH-Z19B), U3 (DHT22), D1 (1N4001), D200-D208 (9 LEDs), R1/R2/R100/R101 (4.7kΩ), R200-R208 (470Ω), C1 (100µF), C2 (47µF), J1 (Vin screw terminal), SW1/SW100/SW101 (push switches). Component types, values, footprints, and datasheets match the source. The BOM grouping is correct: 9×470Ω, 4×4.7kΩ, 9×LEDs individually listed. No spurious or missing components.
- The source has exactly 16 NoConn (~) markers (lines 190-194, 291-292, 315-317, and on U1 at lines 629-634 = 6 more = 16 total). The statistics.total_no_connects = 16 matches. The no_connects array in the output contains 16 coordinate entries.

### Incorrect
- In the nets output, U1 pin 15 (VIN) and pin 16 (3V3) appear inside the 'GND' net (lines 2386-2396 of JSON). Simultaneously, U1 pin 14 (GND, power_in) appears in '__unnamed_5' alongside U2's Vin. The schematic connects U1's VIN pin (at schematic coord 3900,2650) via wire to the 5V supply rail at y=1350, and U1 GND connects to the GND rail. This is a net-resolution error: the analyzer has swapped U1's power pins between the VIN rail net and the GND net. The power_domains section also reflects this error, listing only GND as U1's power rail.
  (signal_analysis)
- Nets '__unnamed_1' (U2 RXD) and '__unnamed_2' (U2 TXD) each contain only one pin, implying those pins are unconnected floating nets. However, the schematic has wires at the positions of U2's right-side pins (pins at 2400,3300 and related coordinates) that connect through long wire runs to U1 GPIO pins. The analyzer appears to have misidentified which pin connects to which wire segment, likely due to coordinate resolution issues under the component's mirror transform (-1 0 0 -1).
  (signal_analysis)
- The design_analysis.cross_domain_signals section flags nets __unnamed_3, __unnamed_4, and __unnamed_5 with 'needs_level_shifter: true' for signals between U1 (ESP32) and U2 (MH-Z19B). However, both devices operate at 3.3V logic — the MH-Z19B specifies 3.3V UART levels and the ESP32 is a 3.3V device. The root cause is that the power domain analysis incorrectly identifies U2's power rails (misidentifying '__unnamed_0' as a rail, which is the Vout/analog output pin of the MH-Z19B, not a supply), leading to phantom domain mismatches. Additionally, __unnamed_5 being flagged as a cross-domain signal is incorrect since it is the shared VIN supply rail itself.
  (signal_analysis)

### Missed
- The MH-Z19B (U2) is a CO2 sensor with UART TXD/RXD pins connected to the ESP32 (U1). The bus_analysis.uart section is empty. The connection uses U2 TXD/RXD mapped to U1 GPIO pins. Even if the net-tracing errors above prevented proper net resolution, the analyzer should detect potential UART signals from pin names like TXD, RXD on U2 and GPIO pins on U1 that serve as UART2 (IO16/IO17 are typical ESP32 UART2 pins, and IO4 is connected to U2's HD pin).
  (signal_analysis)
- The schematic contains 9 identical resistor-LED series circuits (R200/D200 through R208/D208), each driven from a dedicated ESP32 GPIO pin (IO25, IO26, IO23, IO32, IO27, IO18, IO17, IO16, IO15 respectively). All 9 LED cathodes connect to GND and anodes through 470-ohm current limiting resistors to the GPIO pins. The signal_analysis section contains no LED driver detection, no reference to this pattern in design_observations, and the transistor_circuits and buzzer_speaker_circuits sections are empty. This is a clear, structured LED bank that warrants detection.
  (signal_analysis)
- D1 (1N4001) is placed in series with the positive power input rail between J1 (screw terminal Vin) and the rest of the circuit, serving as a reverse-polarity protection diode. C1 (100µF electrolytic) and C2 (47µF electrolytic) are bulk bypass capacitors on the power rails. The signal_analysis.protection_devices and signal_analysis.decoupling_analysis sections are both empty. These are structurally clear: D1 is in the main power path with an anode at the connector and cathode at the supply rail, and both capacitors are across the supply rails.
  (signal_analysis)
- R2 (4.7kΩ) connects between the supply rail and the DHT22 (U3) DATA pin — a standard single-wire protocol pull-up. R1 (4.7kΩ) connects between the supply rail and SW1 (BLE_CFG button) with the other switch terminal to GND, forming a pull-up for a digital input. R100 and R101 similarly pull up the KEY0 and KEY1 button inputs. The signal_analysis.feedback_networks and decoupling_analysis sections are empty, and there is no mention of pull-up topology. These pull-up patterns are significant for signal integrity and are directly verifiable from net connectivity.
  (signal_analysis)
- U3 is a DHT22 temperature+humidity sensor that uses a single-wire proprietary protocol on its DATA pin (pin 2), which connects to ESP32 IO14. The analyzer classifies U3 as a generic 'ic' type without any sensor classification or single-wire protocol note. The DHT22 is a well-known sensor and the pattern (single data pin + pull-up resistor R2 to supply) is structurally detectable. No entry appears in signal_analysis for this interface.
  (signal_analysis)

### Suggestions
(none)

---
