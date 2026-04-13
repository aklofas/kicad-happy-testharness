# Findings: zaoyun/WB23-PulseMeasure_V1.0 / WB23-PulseMeasure_V0.1

## FND-00001794: Total component count of 75 is accurate; Resistor and capacitor counts are accurate; VR1 (3296W trimmer potentiometer) misclassified as varistor; V3 (REF3025 precision voltage reference) misclassif...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: WB23-PulseMeasure_V0.1.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The schematic contains exactly 75 unique component references (R1-R32, C1-C25, U1-U4, D1-D4, J1-J2+J5-J6, JP1, V1-V3, VR1, Y1), all confirmed against the source KiCad 6 file. The analyzer count matches exactly.
- The source schematic has R1-R32 (32 resistors) and C1-C25 (25 capacitors). The analyzer reports resistor=32 and capacitor=25, both correct.
- Two LDO regulators detected: V1=AMS1117-5.0 (input +12V, output +5V) and V2=HT7533 (input +5V, output +3.3V). Both are correct based on the KiCad library IDs and value strings.
- Y1 is an 8MHz crystal with C1=20pF and C4=20pF as load capacitors, yielding an effective load of 13pF. The analyzer correctly identifies the crystal circuit, frequency, and load caps.
- The analyzer correctly identifies decoupling caps on +3.3V (6 caps, 10.5uF total), VCC (2 caps, 20uF), +5V (2 caps, 10.1uF), and +12V (2 caps, 10.1uF). All rails have bulk and bypass coverage.
- The PCB (KiCad 6 format, version 20211014) contains exactly 75 footprints, confirmed against the source file's fp_text reference entries. This matches the 75 schematic components.
- The PCB is fully routed (routing_complete=true, unrouted_net_count=0) with 91 nets matching the schematic's 91 nets. Board dimensions 53.3 x 20.3mm are as laid out.

### Incorrect
- VR1 uses lib '3296W-1-103:3296W-1-103' with value '20K', which is a Bourns 3296W series multi-turn trimmer potentiometer — a variable resistor, not a varistor (MOV). The analyzer classifies it as 'varistor' based on the 'VR' reference prefix. It also appears in protection_devices as type='varistor', which is incorrect. It should be classified as a potentiometer or resistor.
  (statistics)
- V3 uses lib 'Reference_Voltage:REF3025' with value 'REF3025', which is a precision voltage reference IC. The analyzer classifies it as type='varistor' and lists it in protection_devices as type='varistor' with clamp_net='+3.3V'. This is wrong — REF3025 is a shunt reference IC, not a varistor. It should be classified as 'ic'. This also means ic count is understated at 6 (should be 7: U1, U2, U3, U4, V1, V2, V3).
  (statistics)
- The analyzer detects 10 opamp circuit entries for U3 and U4 (TLC274 quad op-amp). Units 1-4 of each IC are real opamp sections (8 correct detections). Unit 5 is the power supply pin unit of TLC274 — it has no signal function and should not appear as an opamp circuit. The two 'unknown' configuration entries for U3 unit 5 and U4 unit 5 are false positives.
  (signal_analysis)

### Missed
- The KiCad 6 PCB file (version 20211014) stores references as '(fp_text reference "R1" ...)' syntax. The analyzer fails to extract these, leaving all footprint refs as '?'. The source file contains 75 valid unique refs (R1-R32, C1-C25, etc.) that are not surfaced in the output. This affects ref-based cross-checking and BOM generation.
  (statistics)

### Suggestions
- Fix: V3 (REF3025 precision voltage reference) misclassified as varistor

---

## FND-00001795: All component references extracted as '?' in KiCad 5 legacy format; THS7376 (video amplifier IC) classified as transformer; LM1881 (video sync separator IC) classified as inductor; Transistor circu...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Winchester.sch.json.json
- **Created**: 2026-03-24

### Correct
- The ECS120 crystal (Y1) used with the FE1.1s USB hub IC is correctly detected. The analyzer correctly reports no load caps (no discrete caps near the crystal in the schematic — ECS-120 is a through-hole crystal and the design appears to rely on the IC's internal caps or board layout).
- The schematic analyzer reports 89 total components. The KiCad 5 source contains 89 placed components (excluding power symbols), confirmed by counting module blocks and cross-referencing with the PCB's 89 footprints.

### Incorrect
- THS7376 is a 4-channel video amplifier IC from Texas Instruments (WinchesterSymbols:THS7376-WinchesterSymbols). The analyzer classifies it as type='transformer', which is incorrect. It should be classified as 'ic'. This is likely a heuristic mismatch on the symbol name or pin count.
  (statistics)
- LM1881 is a video sync separator IC by National Semiconductor/TI. The analyzer classifies it as type='inductor'. This is incorrect — it is a signal processing IC. The library reference (WinchesterSymbols:LM1881) should indicate an IC.
  (statistics)
- ATX1 (WinchesterSymbols:ATX20-WinchesterSymbols) is a 20-pin ATX power connector, providing +12V, +5V, -5V, and GND rails. The analyzer classifies it as type='ic'. It should be classified as 'connector'. Similarly, KICK1 (Jamma connector, U1) is also classified as 'ic'.
  (statistics)

### Missed
- The Winchester schematic uses KiCad 5 legacy .sch format where components have 'L LibName RefDes' lines. The analyzer fails to extract reference designators, showing '?' for all 89 components. The source file contains refs like ATX1, R17, D1, Q1-Q13, BA7230LS1, THS7376, INA260-1, INA260-2, FE1.1s1, U1, U7, Y1, etc. This makes cross-referencing, BOM extraction, and signal path analysis unreliable.
  (statistics)
- The schematic contains Q1-Q13 (13 instances of MUN5230DW1T1G dual NPN digital transistor), used for RGB output switching to the JAMMA connector. The analyzer reports transistor_circuits=0. This is a false negative — the transistors should be detected as switching circuits. Likely caused by the KiCad 5 format ref parsing failure leaving the components without refs.
  (signal_analysis)

### Suggestions
- Fix: THS7376 (video amplifier IC) classified as transformer
- Fix: LM1881 (video sync separator IC) classified as inductor
- Fix: ATX20 power connector classified as IC

---

## FND-00001796: PCB footprint count of 89 is accurate; All PCB footprint refs show as '?' — KiCad 5 unquoted fp_text not parsed; GND copper pour correctly detected with accurate via count; Routing complete with no...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Winchester.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The KiCad 5 PCB (version 20171130) general section lists 89 modules, matching the schematic component count. The analyzer correctly reports footprint_count=89.
- The PCB has 2 fill zones (GND) on F.Cu and B.Cu, which the analyzer detects as zone_stitching with GND net, 215 stitching vias, and area of 23704mm². This matches the KiCad 5 source which shows 2 zone blocks.
- The PCB analyzer correctly reports routing_complete=true and unrouted_net_count=0 for this 135x86mm two-layer board with 996 track segments and 248 vias.

### Incorrect
(none)

### Missed
- KiCad 5 PCB format stores references as '(fp_text reference RefDes' without surrounding quotes, e.g. '(fp_text reference INA260'. The analyzer fails to parse this format, leaving all 89 footprint refs as '?'. The source contains valid refs: Q1-Q13, R1-R25, C1-C24, etc.
  (statistics)

### Suggestions
(none)

---

## FND-00001797: All component references show as '?' — KiCad 9 property format not parsed; Total component count of 27 is correct; I2C bus correctly detected with pullup resistors; LDO regulator XC6206P332MR corre...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_KiCad files_core-v1.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The schematic has exactly 27 placed component instances: R1-R6 (6), C1-C9 (9), D1-D4 (4), J1-J4 (4), U1-U4 (4). Analyzer reports 27 total_components, which is correct.
- The TMAG5273A1QDBVR Hall sensor (U3) and STM32G031F8Px MCU (U2) share I2C SDA and SCL nets. The analyzer correctly detects the I2C bus on both nets with pullup resistors R6 (SDA, +3.3V) and R5 (SCL, +3.3V). Both signals correctly identified.
- U1 (XC6206P332MR) is a 3.3V LDO voltage regulator taking VCC input and producing +3.3V output. The analyzer correctly classifies it as LDO topology with the correct input and output rails.
- D1 (SP0502BAHT) from Power_Protection library is correctly identified as an ESD protection IC on the TX2 net. The analyzer reports it as type='esd_ic' in protection_devices.
- The PCB (KiCad 7 format, version 20221018) has 28 footprints: 27 schematic components plus 1 mounting hole (MountingHole:MountingHole_3.2mm_M3 with REF** designator). This is expected and correctly reported.
- The 87.98 x 17.14mm board is fully routed (routing_complete=true, 281 track segments, 66 vias, 26 nets). All components are on F.Cu (front side). One GND zone on both copper layers.

### Incorrect
(none)

### Missed
- The Windnerd-Core schematic uses KiCad 9 format (version 20230121) where properties do not use '(id N)' syntax but instead use '(at X Y Z)' directly: '(property "Reference" "R1" (at ...)'. The analyzer regex matches only '(id 0)' format, leaving all 27 component refs as '?'. The source has refs R1-R6, C1-C9, D1-D4, J1-J4, U1-U4.
  (statistics)
- The Windnerd-Core PCB uses KiCad 7 format (version 20221018) with '(fp_text reference "R4" ...)' syntax. The analyzer does not extract refs from this format, leaving all 28 footprint references as '?'. Source verification confirms refs R1-R6, C1-C9, D1-D4, J1-J4, U1-U4, plus REF** for the mounting hole.
  (statistics)

### Suggestions
(none)

---
