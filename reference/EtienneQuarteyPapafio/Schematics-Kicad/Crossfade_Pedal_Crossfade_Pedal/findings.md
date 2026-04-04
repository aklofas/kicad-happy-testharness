# Findings: Schematics-Kicad / Crossfade_Pedal_Crossfade_Pedal

## FND-00001347: Component count of 19 with correct type breakdown is accurate; Transistor circuits Q1 and Q2 correctly identified as NPN BJT relay drivers; Relay flyback diodes D1 and D4 (1N4148) not detected as p...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Crossfade_Pedal.kicad_sch
- **Created**: 2026-03-24

### Correct
- The BOM lists 19 components: 1 IC (Arduino UNO A2), 2 relays (K2/K3 G5V-2), 2 transistors (Q1/Q2 BC107), 2 diodes (D1/D4 1N4148), 2 LEDs (D2/D3), 2 connectors (J1/J2 TRS), 3 switches (SW1/SW2/SW3), and 5 resistors (R1/R2/R3/R4/R6). All counts match the component list in the file.
- The signal_analysis.transistor_circuits section correctly identifies Q1 (BC107, collector_net to relay K3 coil, emitter to GND) and Q2 (BC107, collector_net to relay K2 coil, emitter to GND) with base resistors R3 and R4 respectively. The emitter_is_ground flag is correctly true for both.
- The ic_pin_analysis for A2 correctly identifies R1, R2, and R6 (all 10K) as pull-down resistors on Arduino pins A0, A1, and A2 respectively, each going to GND. The switches SW1, SW2, SW3 connect from 3V3 (Arduino pin 4) through the switch to these pins, making these pull-downs correct for switch-to-power circuits (the other side is at 3V3, so they would actually be pull-downs when switches are open).

### Incorrect
- The bus_analysis.i2c section reports four I2C lines on nets __unnamed_19, __unnamed_20, __unnamed_38, __unnamed_39 — all attached only to the Arduino UNO itself with no secondary devices and no pull-up resistors. These are unconnected Arduino pins (each has point_count 1 in the nets section, meaning no external connections). The SDA/A4 and SCL/A5 pins appear twice because the Arduino UNO R3 symbol exposes them on two connectors, but no I2C bus is present in this design.
  (design_analysis)

### Missed
- D1 and D4 are 1N4148 diodes placed across relay coils (D4 cathode on K2 pin 16 / anode on collector Q2; D1 cathode on K3 pin 1 / anode on collector Q1). These are classic flyback/freewheeling protection diodes. The signal_analysis.protection_devices list is empty, so these are missed. The relay coil topology is clear from the net data.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001348: Component count of 19 with correct type breakdown is accurate; Decoupling capacitors C1/C2 correctly attributed to Daisy Seed VIN rail; Relay flyback diode D4 (1N4007) across IM04 relay coil K1 not...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TapTempo_TapTempo.kicad_sch
- **Created**: 2026-03-24

### Correct
- The BOM correctly lists 19 components: 1 IC (Daisy Seed A1), 2 caps (C1 100uF, C2 100nF), 4 diodes/LEDs (D1 1N5817, D2/D3 LEDs, D4 1N4007), 4 connectors (J1/J2/J5/J6 AudioJack2), 1 relay (K1 IM04), 5 resistors (R1/R2 1K, R3 1R, R4/R5 10K), and 2 switches (SW2_NC, SW_NC). The unique_parts count of 12 is also correct.
- The ic_pin_analysis for A1 shows decoupling_caps_by_rail with C1 (100uF) and C2 (100nF) on the VIN net (__unnamed_0). Both capacitors share a net with A1 pin 39 (VIN), which is correct. This is good decoupling analysis — bulk cap plus bypass cap properly identified.

### Incorrect
- The power_domains.ic_power_rails for A1 lists '__unnamed_0' as its power rail. The __unnamed_0 net is the VIN node (A1 pin 39) connecting C1, C2, and R3, which is downstream of the reverse-protection diode D1 (1N5817). The actual supply is +9V (which appears only on D1 pin A). The analyzer should trace through the protection diode to identify +9V as the primary supply domain. As reported, the power domain group is '__unnamed_0' rather than '+9V', making it harder to understand the power architecture.
  (design_analysis)

### Missed
- D4 (1N4007) has its cathode (pin K) on net __unnamed_6 with K1 pin 1 and Daisy ADC_0, and its anode (pin A) on net __unnamed_13 with K1 pin 8. This is a standard flyback diode across the relay coil. The signal_analysis.protection_devices list is empty. This is the same miss as in the Crossfade Pedal — the analyzer does not correlate diodes placed across relay coil pins as protection devices.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001349: Empty PCB file (no footprints, no routing) correctly parsed with all-zero statistics; Silkscreen documentation warnings correctly issued for board missing name and revision

- **Status**: new
- **Analyzer**: pcb
- **Source**: Crossfade_Pedal.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The Crossfade Pedal .kicad_pcb file is a KiCad 8.0 template with no footprints placed and no routing. The analyzer correctly reports footprint_count=0, track_segments=0, via_count=0, board_width_mm=null, and routing_complete=true (vacuously true with no nets). The copper_presence warning about unfilled zones is appropriate.
- The empty PCB generates missing_board_name (suggestion) and missing_revision (warning) in the documentation_warnings array. This is appropriate behavior — the board is a blank template with no silkscreen text. Both warning types and severities are correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001350: TapTempo empty PCB file correctly parsed with all-zero statistics identical to Crossfade PCB; routing_complete reported as true for empty PCB is vacuously correct but potentially misleading

- **Status**: new
- **Analyzer**: pcb
- **Source**: TapTempo_TapTempo.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The TapTempo .kicad_pcb file is also a KiCad 8.0 empty template. The analyzer correctly reports all zeros, null board dimensions, empty layers list, and the same unfilled-zones copper_presence warning. The output structure is consistent with the Crossfade PCB output.
- Both PCB files report routing_complete=true and unrouted_net_count=0. For empty PCBs with no nets defined, this is technically accurate. However, it could be confused with a fully-routed board. A reader could misinterpret this as meaning the schematic's nets have been routed. The dfm_tier of 'standard' with no metrics is also reasonable for an empty board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
