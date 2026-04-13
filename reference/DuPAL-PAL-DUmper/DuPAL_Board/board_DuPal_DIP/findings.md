# Findings: DuPAL-PAL-DUmper/DuPAL_Board / board_DuPal_DIP

## FND-00000478: Component counts, BOM, and power rails correctly identified; Crystal Y1 (8 MHz) with 22 pF load capacitors C1/C2 correctly detected; L7805 linear regulator correctly identified with input rail RECT...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: board_DuPal_DIP_DuPal_DIP.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies 55 components (9 ICs: U1 ATmega8A-PU, U2/U3/U9 74HC595, U5 PAL16L8, U6 MAX232, U7 L7805, U8 74HC166, U10 24-pin PAL), 14 resistors, 17 capacitors, 4 LEDs (D1/D2/D4/D5), 1 diode (D3 1N4001), 1 crystal (Y1 8MHz), 3 connectors (J1 AVR-ISP-6, J2 RS232, J3 barrel jack), 2 switches (SW1 reset, SW2 power), and 4 mounting holes. Power rails ['+12V', 'GND', 'VCC'] are correct.
- crystal_circuits detects Y1 (8MHz), load_caps C1 (22pF on XTAL1) and C2 (22pF on XTAL2), effective_load_pF=14.0 (series combination + 3 pF stray), matched to ATmega8A U1 pin PB6/XTAL1 and PB7/XTAL2.
- signal_analysis.power_regulators correctly finds U7 (L7805, Regulator_Linear:L7805) with input_rail='RECT_V12' and output_rail='VCC'. The RECT_V12 rail is the rectified 12V from J3 barrel jack through D3 (1N4001) and D2 (POWER_LED). This is a full and accurate topology identification.
- bus_analysis.uart finds 4 entries: net TTL-RX (devices U1, U6), TTL-TX (devices U1, U6), RS232-RX (devices U6), RS232-TX (devices U6). This matches the schematic: U1 ATmega8A UART pins connect to U6 MAX232 TTL side, and U6 RS232 side connects to J2 DE9 connector (J2 connector passive pins do not appear in devices list, which is correct).
- connectivity_issues.multi_driver_nets correctly identifies nets P20_12 through P20_16 as having two tri-state drivers each: U5 (PAL16L8, IO pins 12–16) and U10 (24-pin PAL, IO pins 17–22). These nets represent the shared data bus between the two PAL sockets on the DuPAL board, where only one socket is populated at a time. The tri_state pin type is appropriate and the detection is accurate.
- signal_analysis.decoupling_analysis correctly enumerates C8, C9, C10, C11, C12, C14, C13, C16, C17 (all 100nF) on VCC, and separately C4, C5, C6, C7 (1.0uF) as bulk capacitors. The design_observations notes the regulator U7 is missing input-side bypass on RECT_V12 rail, which is accurate (C15 is the only capacitor on RECT_V12, a 220nF electrolytic).

### Incorrect
- The L7805 is a standard fixed-voltage linear regulator with ~2V dropout, not a low-dropout (LDO) regulator. The 'LDO' label is incorrect and misleading. The correct topology string should be 'linear' (fixed positive linear). The same incorrect 'LDO' label appears for the negative regulators LM7905 and LM7909 in pod_1702A_2708, which are negative linear regulators with no LDO characteristic.
  (signal_analysis)
- design_analysis.bus_analysis.spi reports two SPI buses with identical signals (MOSI/MISO/SCK, devices=['U1'], cs_count=0): bus_id='0' (from generic net-name detection) and bus_id='pin_J1' (from J1 AVR-ISP-6 connector pin names). Both describe the same AVR ISP programming interface on the shared MOSI/MISO/SCK nets. The duplication inflates the SPI bus count to 2 when there is logically 1 interface. Additionally, these signals serve in-system programming (ISP), not a peripheral SPI device, so cs_count=0 is correct but the classification as 'SPI bus' is imprecise.
  (signal_analysis)
- signal_analysis.rc_filters reports: input_net='~{RESET}', output_net='VCC', ground_net='__unnamed_9'. In the actual circuit, R15 (10K) has pin1 on VCC and pin2 on the ~{RESET} net; C3 (100nF) has pin1 on ~{RESET} and pin2 on GND. The power source is VCC (via R15 pull-up), the filtered output is ~{RESET}, and the reference is GND. The labeling has input and output swapped: the driving/source end (VCC) is labeled 'output_net' and the filtered node (~{RESET}) is labeled 'input_net'. This RC forms a power-on reset circuit, not a generic signal filter.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000479: Legacy .sch parser fails to resolve component-to-net pin connections for 37 of 63 nets (59%); L7805 regulator topology is 'unknown' with null rails in legacy .sch vs correctly identified in .kicad_...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: board_DuPal_DIP_DuPal_DIP.sch.json
- **Created**: 2026-03-23

### Correct
- Despite pin-resolution failures, the legacy parser correctly extracts all 55 components, 27 unique parts, the same BOM (all values and footprints match the .kicad_sch output), and the same power rails ['+12V', 'GND', 'VCC']. Net name discovery via labels is complete: 63 nets resolved vs 83 in modern (difference explained by unnamed junction nets and net-name normalization between formats).

### Incorrect
- In the legacy .sch output, 37 out of 63 nets have empty 'pins' lists, including all named signal nets: TTL-RX, TTL-TX, MOSI, MISO, SCK, SIPO_SER, SIPO_CLK, all P20_* and P24_* PAL bus nets, all SIPO_O_* nets, etc. The modern .kicad_sch output has 0 empty nets. As a direct consequence: (1) all subcircuits show empty neighbor_components lists, (2) SPI bus detection finds 0 buses (modern finds 1/2), (3) UART buses are found by net name only and show devices=[] and pin_count=0, (4) any net-topology analysis is incomplete or wrong for this file.
  (signal_analysis)
- In the legacy .sch output, U7 (L7805) shows topology='unknown', input_rail=null, output_rail=null. The modern .kicad_sch correctly resolves these as topology='LDO', input_rail='RECT_V12', output_rail='VCC'. This degradation is a direct consequence of the net pin resolution failure: without resolved net-to-component pin mappings, the regulator topology detector cannot trace the input and output rails.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000480: V3 component inventory correctly identifies Pico, 5× 74HCT595, 5× 74HCT166, relay, transistor, fuse, diode, and 41-pair 10K/470K bias resistors; U7 (74HCT02 quad NOR gate, 5 KiCad units) causes 4 f...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: board_DuPal_V3_DuPal_V3.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies: U1 Raspberry Pi Pico (MCU_RaspberryPi_and_Boards:Pico, 43 pins, classified ic), U2–U6 74HCT595 SIPO shift registers (×5), U8–U12 74HCT166 PISO shift registers (×5), U7 74HCT02 quad NOR gate, U13 SN74LV1T125DBV level-translating buffer, K1 G6K-2 DPDT relay, Q1 2N3904 NPN transistor, F1 500mA fuse, D1 1N5818 Schottky diode, D2–D4 status LEDs, and 41 pairs of 10K pull-up + 470K pull-down resistors for ZIF socket biasing. Total unique refs = 128, total_components = 132 (includes 4 in_bom=False mounting holes H1–H4).
- Each ZIF socket signal pin uses a 10K pull-up (to an unnamed floating rail) and a 470K pull-down to GND, giving a ratio of 0.979 (470K/480K). The analyzer correctly identifies 19 such R_top/R_bottom voltage divider pairs (e.g., R18/R62 on ZIF_17, R35/R79 on ZIF_35, R15/R59 on ZIF_14). The mid_point_connections correctly show the ZIF connector pins (J1, J4) and the PISO/SIPO shift register IC inputs connected at the midpoint.
- signal_analysis.transistor_circuits correctly identifies Q1 (2N3904, BJT NPN) with base_net=__unnamed_11, collector_net=__unnamed_12, emitter_net=GND, emitter_is_ground=true, load_type='other', and base_resistors=[{R1, 2.2K}]. The collector drives the K1 relay coil. The detection is accurate including the emitter-to-GND topology.

### Incorrect
- U7 (74HCT02) uses 6 inverter units + 1 power unit = 7 KiCad symbol instances, but only 5 are placed in the schematic. This causes: (1) U7 appears 5 times in the components list (136 total items vs 132 unique refs), (2) the nets dictionary contains duplicate pin entries for U7 output pins (e.g., U7/pin10 appears twice on net __unnamed_1), and (3) connectivity_issues.multi_driver_nets reports 4 false positives — nets __unnamed_1, __unnamed_18, __unnamed_19, __unnamed_64 each showing U7 at the same pin number driving the same net twice. These are all false positives from the multi-unit deduplication failing in net connectivity analysis.
  (signal_analysis)

### Missed
- D1 (1N5818 Schottky, 30V/1A) has its anode on net __unnamed_12 (shared with Q1 collector and K1 relay coil) and cathode on VCC. This is a classic flyback/freewheeling diode protecting Q1 from the inductive kick of K1's coil when deenergized. The analyzer detects only F1 (fuse) under protection_devices and does not identify D1 as a flyback/freewheeling diode protection device. The 1N5818 is correctly classified as a diode, but its function in the relay driver circuit is not captured.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000481: LM7905 and LM7909 negative linear regulators labeled 'LDO' topology; RD-0512D isolated DC-DC converter (U1) not detected as a power regulator; Power rails ['+12V', '-12V', '-5V', '-9V', 'GND', 'VCC...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: board_dupico_pods_pod_1702A_2708_pod_1702A_2708.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The six power rails for this pod board (which generates multiple voltages for legacy 1702A and 2708 EPROM programming) are all correctly detected. The decoupling analysis correctly identifies bypass capacitors on each rail: 100nF on VCC and +12V, 10uF+100nF on -5V and -9V, 47uF+100nF on -12V.

### Incorrect
- U2 (LM7905_TO220, Regulator_Linear:LM7905_TO220) and U3 (LM7909_TO220, Regulator_Linear:LM7909_TO220) are both reported with topology='LDO'. The LM790x series are standard negative linear regulators with ~2V dropout, not low-dropout devices. Both input_rail='-12V' and output_rail='-5V'/'-9V' are correctly identified, confirming the analyzer correctly traces the rail connectivity but applies the wrong topology label.
  (signal_analysis)

### Missed
- U1 (RD-0512D, Custom_Power:RD-0512D) is a 5V-in, ±12V-out isolated DC-DC converter with 5 pins: +Vin (VCC), GND, +Vout (+12V), -Vout (-12V), and 0V. It is the primary power source for the ±12V rails in this pod schematic. The analyzer classifies it as a generic 'ic' type and does not detect it under power_regulators or as a switching converter. Only the downstream LM7905/LM7909 linear regulators are detected.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000482: Seven PNP MMBT3906 transistors (Q1–Q7) correctly identified as high-side switch circuits; U2 (74ACT138 3-to-8 address decoder) correctly classified with enable pins and decoder outputs

- **Status**: new
- **Analyzer**: schematic
- **Source**: board_dupico_pods_pod_eprom_01_eprom_01.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- signal_analysis.transistor_circuits correctly detects all 7 MMBT3906 PNP transistors with emitter_net=VCC (high-side switch configuration), collector_net pointing to ZIF_* nets (EPROM programming voltage application), emitter_is_ground=false (correct for PNP high-side), load_type='connector' (correct — the ZIF socket is the load), and each with a 1K base resistor (R1–R7) from a 74ACT138 decoder output.
- U2 (74ACT138, lib_id=74xx:74LS138) is correctly classified as ic type. Its pin connectivity is correctly resolved: address inputs A0/A1/A2 on nets ZIF_22/ZIF_23/ZIF_24, active-low enables E1/E2 on GND, active-high enable E3 on VCC, and outputs ~{PWR_0}–~{PWR_6} plus __unnamed_1 (O7). The ~{PWR_*} naming does not cause false power-rail classification; power_rails correctly remains ['GND', 'VCC'].

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000483: Q1 (2N3906 PNP) and U1 (74ACT04 hex inverter) correctly detected with 5 no-connect marks; Value/lib_id mismatch for U1: value is '74ACT04' but lib_id is '74xx:74HCT04'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: board_dupico_pods_pod_pal_pod_pal.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Q1 (2N3906, BJT PNP) detected as transistor_circuit with emitter_net=VCC, collector_net=ZIF_40, base_resistors=[{R1, 1k}], emitter_is_ground=false, load_type='connector' — all correct for a PNP high-side switch applying VCC to a GAL device pin. U1 (74ACT04 hex inverter, lib_id=74xx:74HCT04) appears 7 times in the components list (6 gate units + 1 power unit, correct for a multi-unit KiCad symbol). total_no_connects=5 correctly captures the 5 unused gate output no-connect markers on U1's unused inverter outputs.

### Incorrect
- The schematic instantiates U1 with value='74ACT04' but uses the KiCad library symbol '74xx:74HCT04'. The analyzer faithfully reports both (value='74ACT04', lib_id='74xx:74HCT04', description='Hex Inverter'), which is correct transcription. This is a design-level inconsistency (ACT vs HCT parts have different input thresholds), not an analyzer error. No assertion is needed since the analyzer correctly reports what is in the schematic.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
