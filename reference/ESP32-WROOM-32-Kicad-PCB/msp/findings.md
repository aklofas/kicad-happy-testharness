# Findings: ESP32-WROOM-32-Kicad-PCB / msp

## FND-00000495: Transistor circuits Q1/Q2 not detected despite clear auto-reset topology; Power regulator U2 (AMS1117-3.3) topology reported as unknown with null input/output rails; Split 3.3V power rails +3V3 and...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ESP32.sch.json
- **Created**: 2026-03-23

### Correct
- The schematic has USB1 (Micro-B) D+ and D- lines going through text labels to CH340C (U3). The analyzer correctly identifies these as a differential pair. The has_esd: false is accurate — there is no explicit ESD protection device (TVS diode or similar) on these lines in the schematic.
- The source schematic contains exactly: 7 capacitors (C1–C7), 9 resistors (R1–R9), 3 ICs (U1/U2/U3), 1 USB connector (USB1), 2 NPN transistors (Q1/Q2), 1 diode (D3), 2 buttons (B1/B2), 2 LEDs (D1/D2), 2 15-pin connectors (JP1/JP2). The JSON reports 29 total_components with capacitor:7, resistor:9, ic:3, connector:1, transistor:2, diode:1, switch:2, led:2, jumper:2 — all correct.
- All 21 GPIO nets used in the schematic (IO0–IO39 plus EN) are correctly listed in the nets section with their label positions. The empty pins: [] for IO nets is expected behavior for KiCad 5 legacy format since U1 (ESP32) pin definitions come from the external library symbol, not from the .sch file itself, so the analyzer cannot resolve which pins are on which nets.

### Incorrect
- Q1 and Q2 are S8050 NPN transistors forming the standard ESP32 auto-reset circuit driven by CH340C RTS/DTR signals via R8/R9. The collector of Q1 connects to the EN net and Q2 collector connects to IO0 net through the collector network. The analyzer reports transistor_circuits: [] when it should detect these as a transistor switching circuit. The DTR and RTS labels connect to the bases via R8/R9 respectively, and the collector outputs drive EN and IO0 on the ESP32.
  (signal_analysis)
- U2 is an AMS1117-3.3 LDO linear voltage regulator with input connected to VIN (USB VBUS through diode D3) and output to +3.3V. The analyzer detects the component as a power_regulator but reports topology: unknown, input_rail: null, output_rail: null, estimated_vout: null. Given the component value 'AMS1117-3.3' clearly indicates a 3.3V fixed LDO, and the +3.3V and VIN rails are present and traceable, this should resolve to a linear regulator with input_rail VIN and output_rail +3.3V.
  (signal_analysis)
- The schematic uses two different KiCad power symbols: '#PWR03' with value '+3V3' (used near the EN pull-up R3 and ESP32 VCC area) and '#PWR016' with value '+3.3V' (output of U2 AMS1117 regulator). These appear as separate power rails in the JSON output with separate point counts (16 and 6 respectively). In power_domains, neither is associated with U2's output, and no domain unification is attempted. In practice these are the same net — the design relies on KiCad's global power net naming to connect them. The analyzer should flag this as a potential split-rail ambiguity or at minimum note the two names for the same physical voltage.
  (signal_analysis)
- The bus_analysis.uart section detects nets RXD and TXD but reports devices: [] for both. Tracing the nets: TXD connects R6 pin1 (the ESP32 TX side) and the CH340C TXD pin (via label); RXD connects R5 pin2 and CH340C RXD. The resistors R5 (1K) and R6 (1K) act as series current-limiting resistors on the UART lines between ESP32 U1 and USB-UART bridge U3. Since U1 and U3 are the expected device endpoints, they should appear in the devices list.
  (signal_analysis)
- All three ICs — U1 (ESP32), U2 (AMS1117-3.3), U3 (CH340C) — have neighbor_components: [] in the subcircuits array. U2 is clearly associated with decoupling capacitors C3 (10uF input) and C4 (10uF output) and C5 (0.1uF output). U3 has decoupling cap C6 (0.1uF on VBUS pin) and C7 (0.1uF on V3 pin). U1 has decoupling caps C2 (0.1uF) with pull-up R3 (10K) on EN. The neighbor detection is failing to associate passive components that share net segments with these ICs in this legacy .sch format.
  (signal_analysis)
- D1 and D2 are LEDs connected with current-limiting resistors R1 and R2 (both 1K) from +3V3, driven by ESP32 IO2 net. The net data shows D1 pin 2 (anode 'A') and D2 pin 2 (anode 'A') on the GND net, and D1 pin 1 (cathode 'K') and D2 pin 1 (cathode 'K') on unnamed nets that connect to R1/R2. This is a standard LED driver topology. The analyzer has no LED circuit detection output and does not flag the LED+resistor+GPIO combination. Note: the LED pin mapping appears inverted — cathode (K) on the R side connects to +3V3 via resistor, and anode (A) to GND — this is actually a reverse connection, potentially a schematic error in the original design that the analyzer should flag.
  (signal_analysis)
- D3 is a diode (value S4, SOD-123 package) placed between the USB VBUS net and VIN, with anode on USB side and cathode toward VIN. This is a standard reverse-polarity or over-voltage protection diode in the power path. The analyzer reports protection_devices: [] despite D3 being clearly a protection/steering diode in the VBUS-to-VIN power path.
  (signal_analysis)
- The decoupling_analysis field is an empty array despite clear decoupling capacitors: C2 (0.1uF) and C3/C4 (both 10uF) and C5 (0.1uF) associated with the AMS1117 regulator; C6 (0.1uF) for CH340C V3 supply; C7 (0.1uF) for CH340C. The failure to populate this analysis is likely related to the same root cause as the empty neighbor_components — the pin-to-net resolution is incomplete in the legacy .sch format when IC pins have no explicit pin entries.
  (signal_analysis)
- In the source schematic, R3 (10K) pin 2 connects to the EN net (verified by wire routing: +3V3 -> R3 pin1, R3 pin2 -> EN net via label at 3250,5300). However, the EN net in the JSON output only shows R3 pin_number 2 as the sole pin entry. The R3 pin 1 side is reported as __unnamed_0 with a single-point net. This means the pull-up topology (R3 between +3V3 and EN) is present in the data but the +3V3 pin of R3 has lost its connection to the +3V3 power net, appearing as an isolated unnamed net. This is likely a wire-to-net resolution issue for pull-up resistors to power symbols in legacy .sch format.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000496: Root sheet msp.sch correctly parsed as hierarchical sheet with ESP32.sch sub-sheet; msp.sch and ESP32.sch produce identical component/net/BOM data as expected for hierarchical design

- **Status**: new
- **Analyzer**: schematic
- **Source**: msp.sch.json
- **Created**: 2026-03-23

### Correct
- msp.sch is the top-level KiCad 5 project file (Sheet 1 of 3) containing only an index/TOC table and a sheet reference to ESP32.sch. The analyzer correctly reports sheets_parsed: 2, sheet_files including both msp.sch and ESP32.sch, and picks up all 29 components from the sub-sheet. The root sheet itself has zero schematic components, only text notes and a sheet frame.
- Since msp.sch includes ESP32.sch as its only sub-sheet with actual components, both JSON outputs report identical statistics: 29 total_components, 47 total_nets, same BOM, same power rails. This is the correct behavior — analyzing the top-level sheet should yield the full design view.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
