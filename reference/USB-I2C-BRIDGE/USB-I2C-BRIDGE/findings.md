# Findings: USB-I2C-BRIDGE / USB-I2C-BRIDGE

## FND-00001642: Component count: 17 total, 10 unique parts correctly parsed; USBLC6-4 correctly detected as ESD protection device for USB lines; USB D+/D- differential pair detected with ESD protection; Differenti...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: USB-I2C-BRIDGE.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly parsed all 17 components from the KiCad 6 schematic: 2 ICs (CP2112, USBLC6-4), 3 connectors, 4 resistors, 6 capacitors, 1 LED, 1 switch.
- The analyzer correctly classified U1 (USBLC6-4) as an ESD IC protecting D+, D-, and two unnamed nets (IO2, IO3 pins). The esd_ic type and protected_nets are accurate per the schematic.
- The differential pair D+/D- is correctly identified with has_esd: true, referencing both the USBLC6-4 (U1) and the CP2112 (U2). The pair connects J1, U1, and U2.
- The CP2112 exposes SDA and SCL which route to external connectors J2 and J3. The analyzer correctly identifies the I2C bus and reports has_pullup: false since no pull-up resistors are present on this board — pull-ups are expected on the connected I2C target device.
- The analyzer found: VBUS: C2 (4.7µF bulk), VDD: C3 (4.7µF bulk) + C4 (100nF bypass), VIO: C5 (100nF bypass). C1 decouples the VPP pin (internal). The 3-rail coverage matches the schematic.

### Incorrect
- The differential pair D+/D- is clearly USB 2.0 data lines (named D+ and D-, connected to USB-C receptacle J1 and CP2112 USB bridge), but the type field shows 'differential' rather than 'USB'. The USB-LED-Otter schematic correctly labels an equivalent pair as type 'USB'.
  (design_analysis)

### Missed
- R1 and R2 are 5.1kΩ resistors connected between J1's CC1/CC2 pins and GND. These are the standard USB-C CC pull-down resistors for a USB device (5.1kΩ to GND = UFP/sink). The analyzer does not flag them as USB-C CC termination resistors. This is a missed detection that would be valuable for USB-C design review.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001643: PCB footprint count matches schematic: 17 footprints all on front side; 2-layer board with complete routing correctly identified

- **Status**: new
- **Analyzer**: pcb
- **Source**: USB-I2C-BRIDGE.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB has 17 footprints (14 SMD + 3 THT), all on the front side. This matches the schematic's 17 components. Routing is complete with 0 unrouted nets.
- The PCB uses F.Cu and B.Cu (2 copper layers) with 151 track segments, 41 vias, and routing_complete: true with 0 unrouted nets.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001644: Gerber set complete with all required layers present; Layer count correctly reported as 2 copper layers; Board dimensions from gerber match PCB: 12×15mm

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber.json.json
- **Created**: 2026-03-24

### Correct
- All 9 gerber layers are present (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts) plus PTH and NPTH drill files. completeness.complete is true with no missing required or recommended layers.
- The gerber set has F.Cu (L1,Top) and B.Cu (L2,Bot) matching the PCB's 2-layer design.
- The gerber Edge.Cuts layer gives board_dimensions of 12×15mm matching the PCB analyzer output exactly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001645: Component count: 31 total across all component types correctly parsed; LQ1 (optical encoder element) misclassified as inductor; No decoupling analysis performed despite VCC rail with bypass capacit...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Mouse.sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly extracted 31 components: 3 switches (SW1-SW3), 1 connector (J1), 11 resistors, 8 capacitors, 1 inductor/LQ, 2 LEDs (LD1, LD2), 1 IC (U1), 4 jumpers (JP1-JP4). Total matches the schematic.
- The 4 jumper components (JP1-JP4) use Device:R symbol with JP_Axial footprints and are correctly typed as 'jumper' rather than 'resistor', using 4 as the count in component_types.

### Incorrect
- LQ1 uses lib symbol 'Optical_Mouse:LQ' with value 'EL' and footprint 'Mouse:LQ1'. The 'LQ' designation and context (optical mouse schematic, adjacent to LED components LD1/LD2) indicates this is a light sensor or optical encoder element, not an electrical inductor. The analyzer classified it as 'inductor' due to the 'L' prefix in the reference designator.
  (statistics)

### Missed
- The schematic has a VCC power rail (via global labels) with capacitors C14 (4.7µF), C15 (0.1µF), C8 (0.01µF), C9 (0.01µF), C12 (0.1µF) as bypass/bulk capacitors. The signal_analysis.decoupling_analysis array is empty. This is likely because VCC is a global label rather than a proper KiCad power symbol, so the analyzer does not associate the capacitors with the rail.
  (signal_analysis)

### Suggestions
- Fix: LQ1 (optical encoder element) misclassified as inductor

---

## FND-00001646: PCB footprint count 31 matches schematic component count; Single copper layer used for routing correctly identified; Board dimensions 39×78mm correctly extracted

- **Status**: new
- **Analyzer**: pcb
- **Source**: Mouse.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB has 31 footprints: 18 front side (SMD) and 13 back side (THT), matching the schematic's 31 components. Routing is complete on F.Cu only.
- Although B.Cu is defined in the layer table and some footprints are placed on the back side, all tracks are on F.Cu only (no B.Cu tracks, 0 vias). The copper_layers_used: 1 is accurate for routing purposes.
- The PCB reports board_width_mm: 39.0 and board_height_mm: 78.0, consistent with a USB mouse PCB outline.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001922: Component count, types, USB-C compliance (CC pull-downs), and USB ESD detection mostly accurate; D- USB data line incorrectly reported as lacking ESD protection despite U1 (USBLC6-4) being connecte...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: USB-I2C-BRIDGE_USB-I2C-BRIDGE.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- 17 components correct. Power rails [GND, VBUS, VDD, VIO] correct. 4 no-connects matches source exactly. U2=CP2112 correctly identified as IC. U1=USBLC6-4 correctly identified as ESD protection IC. USB compliance: cc1_pulldown_5k1=pass and cc2_pulldown_5k1=pass are correct (R1/R2 are 5.1kΩ pull-downs on CC1/CC2). vbus_decoupling=pass correct (C2 4.7uF on VBUS). is_type_c=True correct for J1 (Connector:USB_C_Receptacle_USB2.0 lib_id).
- The CP2112 I2C master outputs (SDA/SCL) connect only to J2 and J3 headers with no pull-up resistors on the board. The analyzer correctly reports has_pull_up=False for both SDA and SCL in bus_analysis.i2c. R1/R2 are CC1/CC2 pull-downs, R3 is the LED current limiter, and R4 connects to the VIO switching circuit — none are I2C pull-ups. External pull-ups are required on the connected I2C bus.

### Incorrect
- design_observations shows usb_data for D- with has_esd_protection=False, yet D- net analysis shows U1 pin 1 (IO1) is directly on the D- net. The protection_devices section correctly lists U1 as protecting ['D+', 'D-', '__unnamed_4', '__unnamed_5']. The ESD detection for D+ (has_esd_protection=True) correctly finds U1, but the same logic fails for D-. This is an asymmetric bug in the ESD detection path for the design_observations section — both D+ and D- are symmetrically connected to the USBLC6-4.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001923: PCB statistics correct: 17 footprints, 31 nets, 151 tracks, 41 vias, 2 copper layers, fully routed; Placement issues correctly detected: courtyard overlap between J2/J3, SW1 and J3 violating edge c...

- **Status**: new
- **Analyzer**: pcb
- **Source**: USB-I2C-BRIDGE_USB-I2C-BRIDGE.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Source confirms: 17 footprints, 31 non-zero nets (source has 32 including net 0), 151 segments, 41 vias, F.Cu + B.Cu present. routing_complete=True, unrouted=0 correct. DFM correctly flags annular ring=0.1mm requiring advanced process tier (below standard 0.125mm threshold). Thermal pad analysis for U2 CP2112 QFN correctly identifies 4 vias as insufficient (recommended minimum 5).
- J2 at (129.3, 100) and J3 at (135.45, 100) are 6.15mm apart with a 5.2mm² courtyard overlap — valid DFM concern for connectors with large courtyard extents. SW1 edge_clearance=-0.5mm (extends 0.5mm beyond board edge) and J3 edge_clearance=-0.14mm are both negative, indicating footprint courtyard/silkscreen extends beyond the board outline.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
