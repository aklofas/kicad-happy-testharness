# Findings: audio-amp / Audio Amp

## FND-00001843: VCC1 terminal block connector misclassified as varistor and listed as protection device; TA8251AH 4-channel audio amplifier correctly identified with 13 total components and 30 nets; Audio amplifie...

- **Status**: new
- **Analyzer**: schematic
- **Source**: Audio Amp.sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies the TA8251AH (25-pin HZIP package), 4 capacitors at 0.1uF, 1 bulk 2200uF capacitor, 4 resistors at 2.2 ohm, 2 Phoenix Contact 4-pin connectors (J1 INPUT, J2 OUTPUT), and 1 VCC power input connector. Component count, BOM grouping, and footprint assignments match the source schematic.
- The TA8251AH schematic uses KiCad 'power:Earth' symbols exclusively for its ground reference. The VCC supply enters via an unnamed net (not a named power symbol), so the analyzer correctly identifies only 'Earth' as a named power rail. The power_rails list matches what is in the source file.

### Incorrect
- VCC1 is a Phoenix Contact 1935161 2-pin screw terminal block (power input connector), with lib_id 'dk_Terminal-Blocks-Wire-to-Board:1935161'. The analyzer classifies it as type 'varistor' and adds it to signal_analysis.protection_devices as a varistor clamp. The reference prefix 'VCC' or the 'V' in the lib MPN appears to trigger the varistor heuristic. The component is clearly a connector (footprint Connector_Phoenix_MC:PhoenixContact_MCV_1,5_2-G-3.5_1x02_P3.50mm_Vertical, category 'Connectors, Interconnects') with no varistor characteristics.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001844: PCB correctly identifies 4 THT and 9 SMD footprints with 4 mounting holes as virtual; PCB correctly reports 24 routed nets with complete routing; Courtyard overlaps correctly detected between C5, J...

- **Status**: new
- **Analyzer**: pcb
- **Source**: Audio Amp.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The 4 through-hole footprints are J1, J2, U1, and VCC1 — all correct. The 9 SMD footprints are C1-C5 and R1-R4. The 4 REF** mounting holes are correctly marked as virtual/board-only excluded from BOM. The large 2200uF C5 with footprint 'Capacitor_SMD:CP_Elec_18x17.5' is correctly classified as SMD since it uses an SMD land pattern.
- The schematic has 30 nets, but most of the unnamed nets in the schematic are single-pin dangling stubs on the TA8251AH pins that are not wired in this simplified design. The PCB has 24 nets which are the physically routed connections, and routing_complete is correctly reported as true with unrouted_count of 0.
- The 2200uF C5 (18x17.5mm footprint) physically overlaps with J1 (INPUT connector) with 59.4mm² overlap and J2 (OUTPUT connector) with 13.4mm². These overlaps are real — the large bulk capacitor is placed in close proximity to the connectors in the original layout. The placement_analysis.courtyard_overlaps correctly flags both.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001845: 91 components correctly parsed from KiCad 5 legacy schematic with complex multi-rail power design; SCL1, SDA1, and GND1 test pads incorrectly classified as 'switch' or 'other' instead of 'test_poin...

- **Status**: new
- **Analyzer**: schematic
- **Source**: pcb_pcb.sch.json.json
- **Created**: 2026-03-24

### Correct
- The axiom-micro-mainboard schematic (KiCad 5 format) has 91 components including 36 capacitors, 14 resistors, 16 connectors, 10 ferrite beads, 7 ICs, 3 LEDs, 2 switches, 1 test point, 2 other components. The 13 power rails (including GNDA, VDD, VAA, VDD_HISPI, etc.) for the AR0330 image sensor are correctly enumerated.
- The three WS2812B LEDs (D1, D2, D3) are detected as three individual chains of length 1. Each is correctly identified with the single-wire protocol, estimated 60mA current, and 'ws2812b' LED type. The chain topology detection does not link them into one chain (the schematic daisy-chain wiring uses net labels not visible to the detector), but the individual detection is accurate.
- All 10 ferrite beads (L1-L10, value 'FB', footprint 'parts:ferrite_bead_0402_handsoldering') are correctly identified as type 'ferrite_bead' in both the BOM and component_types statistics. This correctly distinguishes them from inductors.

### Incorrect
- The design has four test pads (SCL1, GND1, SDA1, LED1) all using the same 'device1:TEST' KiCad 5 symbol. LED1 is correctly classified as 'test_point', but SCL1 and SDA1 are classified as 'switch', and GND1 as 'other'. All four should be 'test_point'. The BOM also groups them as type 'switch' which is incorrect. This is an inconsistent classification of the same symbol type within a single schematic.
  (statistics)

### Missed
- The schematic has SDA_N, SCL_N, SDA_S, and SCL_S nets (I2C buses for north and south sensor interfaces) and SDA_N/SCL_N nets have pull-up resistors (R110/R112) connected. However, the IC components (BMX055 IMU U2, ar0330CM U9, MCP1727 regulators U7/U8, 74LVC1T45GW U1) all have empty pin lists in the KiCad 5 legacy parse. The bus_analysis.i2c list is empty because no IC pins are resolved to the SCL/SDA nets. This is a limitation of the KiCad 5 legacy format parsing when custom library symbols have no pin data extractable.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001846: PCB correctly identifies 96 footprints including 13 board-only items for a complex 4-layer design; Inner copper layers In1.Cu and In2.Cu correctly reported as 'signal' type matching source file; PC...

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_pcb.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The axiom-micro-mainboard PCB has 96 footprints versus 91 schematic components. The 5-unit difference is accounted for by board-only items: REF*** (1), unnamed items 0/1/2/3 (4), and test points. The 4-layer stackup with 2555 track segments and 310 vias is consistent with a dense camera board design.
- The axiom PCB source file defines both In1.Cu and In2.Cu as type 'signal' (not 'power'), which differs from the avdisplay-cape which explicitly sets them as 'power'. The analyzer faithfully reads the layer type from the file. In practice In1.Cu carries the GNDA net zone and In2.Cu likely carries power, but the layer type attribute in the KiCad 5 file was left as 'signal'. The reporting is accurate to the file definition.
- The axiom PCB has 151 nets while the schematic reports 106. The 45-net difference consists of auto-generated 'Net-(Component-PadN)' stub nets for IC pads that lack explicit net names (e.g., Net-(A1-Pad1), Net-(E1-Pad5)). Many of these come from the AR0330CM image sensor (U9) and the Z-Turn-Lite module (A1) which have numerous unconnected I/O pads. This is expected PCB behavior.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
