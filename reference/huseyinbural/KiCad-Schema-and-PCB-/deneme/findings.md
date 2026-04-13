# Findings: huseyinbural/KiCad-Schema-and-PCB- / deneme

## FND-00000696: Empty subsheet correctly yields zero components/nets

- **Status**: new
- **Analyzer**: schematic
- **Source**: actuators.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- actuators.kicad_sch is a stub sheet with only empty lib_symbols. Analyzer correctly returns 0 components, 0 nets, 0 wires.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000697: Empty subsheet correctly yields zero components/nets

- **Status**: new
- **Analyzer**: schematic
- **Source**: sensors.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- sensors.kicad_sch is a stub sheet with only empty lib_symbols. Analyzer correctly returns 0 components, 0 nets, 0 wires.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000698: Supply subsheet with only wires/labels/no-connects correctly parsed

- **Status**: new
- **Analyzer**: schematic
- **Source**: supply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- supply.kicad_sch has no components (lib_symbols empty) but has 20 wires, 11 no-connects, and 2 hierarchical labels (PV_1, PV_2). Analyzer correctly captures all of these with zero components in BOM.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000699: Component counts correct: 47 total, 9C/13R/4H/19J/2IC; I2C bus detection correct: SCL/SDA with 2.2K pull-ups on +3V3; UART bus detection correct: RX_GPS/TX_GPS identified as UART; LM358 opamp detec...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: microcontrollers.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Analyzer found 47 components matching PCB footprint count. Component type breakdown (capacitor=9, resistor=13, mounting_hole=4, connector=19, ic=2) matches manual inspection of the schematic.
- Analyzer correctly identified I2C_SCL and I2C_SDA nets, detected R16 (2.2K) and R17 (2.2K) pull-ups to +3V3, and associated U8 (ESP32) as the I2C master device.
- Analyzer correctly identified RX_GPS and TX_GPS nets as UART lines driven by U8 (ESP32 IO17/IO16). These connect to J3 (GPS connector).
- U1 unit 1 has output feeding back to input via RV1/R1 divider (wiper-to-inverting) with R2 to GND — this is a comparator topology with hysteresis. Configuration classification as 'comparator_or_open_loop' is accurate.

### Incorrect
- The analyzer reports an RC low-pass filter (R15=10k, C3=0.1u, 159Hz) with input_net='+3V3'. R15 actually connects +3V3 to the EN pin of U8 (ESP32 enable), and C3 decouples EN to GND. This is a power-on reset/enable RC circuit, not a signal filter on +3V3. The 'input_net' should not be labeled as +3V3 since +3V3 is a power rail, not a signal source for the filter.
  (signal_analysis)

### Missed
- The design has 4 LDR sensor circuits: each LDR (at Jx connector) pairs with a 10k resistor (R21-R24) forming a voltage divider to ground, with the midpoint going to ESP32 ADC pins. These are standard resistive dividers for LDR sensing. The analyzer reports voltage_dividers=[] but should detect these R/LDR pairs as voltage dividers (or sensor conditioning networks).
  (signal_analysis)
- The design_observations notes U1 (LM358) has +12V rail without decoupling caps, but no ERC warning is raised about this. erc_warnings=[] despite this being a real issue. The observation exists but could be promoted to an ERC/passive warning.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000700: Board dimensions, layer count, footprint count, routing status all correct; Ground domain fragmentation correctly detected for ESP32 unconnected GND pins; 12 courtyard overlaps correctly detected i...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: deneme.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Analyzer correctly identified 47 footprints (front only), 2-layer board (F.Cu/B.Cu), 71.8x104.7mm board, 49 nets, routing_complete=true, 251 track segments, 1 via, 2 zones. All match the PCB file contents.
- The ESP32 DevKit (U8) has 3 GND pins marked unconnected (GND_J2_14, GND_J3_1, GND_J3_7) — each becomes its own isolated ground domain. Analyzer correctly reports 4 ground domains and flags U8 as a multi-domain component. This is a real PCB design concern.
- The analyzer identified courtyard overlaps for components placed too close together or overlapping. The J14/J2 overlap of 110.9mm² and negative edge clearances (J14 at -3.81mm) indicate the board has real placement violations. This is accurate.
- The board height of 104.7mm exceeds the 100mm standard tier at JLCPCB, triggering higher pricing. Analyzer correctly identifies this as a DFM violation in the 'board_size' parameter.

### Incorrect
- PCB has 47 footprints total: statistics shows front_side=47, tht_count=43. The 4 mounting holes (H1-H4) are excluded from tht_count because they are 'exclude_from_pos_files'. However, they are through-hole pads and physically THT. The classification as separate from tht_count is a design choice, but it means tht_count+excluded != total, which could confuse users. Minor classification issue.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
