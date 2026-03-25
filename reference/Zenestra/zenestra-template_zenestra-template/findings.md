# Findings: Zenestra / zenestra-template_zenestra-template

## FND-00001825: All 10 mounting holes correctly identified with zero nets; assembly_complexity misclassifies all 10 mounting holes as SMD

- **Status**: new
- **Analyzer**: schematic
- **Source**: zenestra-template.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The schematic contains only MountingHole symbols (H1–H10) with no wire connections. The analyzer correctly reports total_components=10, total_nets=0, total_wires=0, and classifies all components as mounting_hole type. The BOM and component list are accurate.

### Incorrect
- The analyzer reports smd_count=10, tht_count=0 in assembly_complexity, placing mounting holes in 'other_SMD'. MountingHole_3.2mm_M3_DIN965_Pad footprints are mechanical through-hole pads, not SMD. The PCB analyzer correctly reports smd_count=0 and tht_count=0 (neither SMD nor standard THT in the pick-and-place sense). The schematic assembly_complexity should not classify mechanical mounting holes as SMD.
  (assembly_complexity)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001826: PCB board dimensions, footprint count, and routing status are accurate; ENIG copper finish and 1.6mm board thickness correctly extracted; DFM violation correctly flagged: board exceeds 100x100mm JL...

- **Status**: new
- **Analyzer**: pcb
- **Source**: zenestra-template.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly reports footprint_count=10 (H1–H10), board_width_mm=150.0, board_height_mm=100.0 matching the Edge.Cuts bounding box. The design has no tracks, no vias, routing_complete=true (no nets to route). The board outline has 4 lines and 4 arcs (rounded rectangle) totaling 8 edges, all correct.
- The setup section correctly reports copper_finish='ENIG' and board_thickness_mm=1.6, matching the stackup defined in the file.
- The 150x100mm board correctly triggers a board_size DFM violation noting it exceeds the 100x100mm standard pricing tier at JLCPCB. violation_count=1 is accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001827: kicad_version correctly parsed as 8.0 from generator_version field; TLV1117-33 LDO regulator correctly detected with +5V input, +3.3V output; Three TVS diode protection devices correctly detected o...

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_external_antenna_ZBSmartMeter.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The file contains (generator_version "8.0") which the analyzer correctly extracts and reports as kicad_version='8.0'. The 37 components, 3 power rails (+3.3V, +5V, GND), and component type breakdown are all accurate.
- U2 TLV1117-33 is correctly identified as an LDO from +5V to +3.3V with estimated_vout=3.3 derived from the '-33' suffix. The topology and rail assignments match the schematic.
- Three CPDQ5V0-HF TVS diodes (D4, D5, D6) are correctly identified as protection devices on USB_D+, USB_D-, and an additional net. The USB ESD protection is also noted in design_observations with has_esd_protection=True for both USB data lines.
- Two UART buses detected: UART1 between U1 (NCN5150DG) and U3 (ESP32-C6-MINI), and UART0 programming RX/TX lines on U3. All four UART nets (UART1_TX, UART1_RX, UART0_PROG_RX, UART0_PROG_TX) have correct device associations.
- The 6 additional nets (versus onboard_antenna's 52) correspond to: 4 unconnected pins on J1 (RJ12 6-pin connector), 1 extra GPIO on U3 (ESP32-C6-MINI has an additional exposed pad vs WROOM), and 1 LED/resistor net. This correctly reflects the external antenna variant using a smaller ESP32-C6-MINI-1 module instead of the WROOM-1.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001828: kicad_version correctly reported as unknown for file lacking generator_version field; U3 correctly identified as ESP32-C6-WROOM-1 in onboard_antenna variant

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_onboard_antenna_ZBSmartMeter.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The onboard_antenna schematic uses file_version 20230121 which does not include the generator_version field (added in KiCad 8). The analyzer correctly falls back to 'unknown' rather than guessing. All 37 components and 52 nets are correctly parsed.
- The onboard_antenna uses ESP32-C6-WROOM-1 (Espressif:ESP32-C6-WROOM-1) while the external_antenna uses ESP32-C6-MINI-1/U. Both are correctly parsed from their respective lib_id fields.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001829: 28 components correctly counted across two STM32 Blackpill breakout modules and peripherals; Two SPI buses correctly detected for left and right halves of split keyboard adapter; assembly_complexit...

- **Status**: new
- **Analyzer**: schematic
- **Source**: adapter_adapter.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The schematic contains two STM32F401/F411 Blackpill breakout ICs (U1, U2), 8 resistors (5.1k), 12 connectors, 4 mounting holes, and 2 push switches totaling 28 components. The component_types breakdown is accurate.
- SPI bus L (on U2) and SPI bus R (on U1) are correctly detected via mosi/miso/sck net naming. U2 (left) has 4 chip selects (trackball, eeprom, user, plus shared) and U1 (right) has 6 chip selects. The bus_mode=full_duplex is correct.
- scl_r, sda_r, cs_eeprom_r on U1 and scl_l, sda_l, cs_eeprom_l on U2 are routed to no other component in the schematic (these are broken-out signals for future expansion). The single_pin_nets list correctly captures all 6.

### Incorrect
- The schematic assembly_complexity reports smd_count=28, tht_count=0 with all non-standard-prefix footprints classified as other_SMD. However, 12 connectors (Library:6_PinHeader, Library:5_PinHeader, etc.) are through-hole headers, and the PCB analysis correctly reports 10 SMD (resistors), 14 THT. The custom library prefix 'Library:' does not map to any SMD pattern, causing incorrect SMD classification.
  (assembly_complexity)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001830: PCB correctly reports 10 SMD, 14 THT footprints matching the connector-heavy board design; 73 nets in PCB matching the schematic net count after resolving unconnected pads

- **Status**: new
- **Analyzer**: pcb
- **Source**: adapter_adapter.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB shows 10 SMD (resistors in 1206 package) and 14 THT (pin headers and 3.5mm jack connectors). The total 32 footprints includes 4 ghost G*** entries from board groups. The 45 vias, 318 track segments, and 2-layer board are all accurate.
- The PCB netlist shows 73 nets (net IDs 1-73) which matches the schematic's 85 named nets minus power/unnamed nets that collapse. The routing is complete (unrouted_count=0). The HAL lead-free copper finish is correctly extracted.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001831: 9 gerber layers complete with both PTH and NPTH drill files, alignment verified; 2-layer board with 191 total holes and two trace widths correctly analyzed; run_gerbers.py summary function uses wro...

- **Status**: new
- **Analyzer**: gerber
- **Source**: adapter_gerbers.json
- **Created**: 2026-03-24

### Correct
- The gerber set contains F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, and Edge.Cuts — all required layers present. Both PTH (187 holes) and NPTH (4 holes) drill files present. Alignment check passes. Board dimensions from Edge.Cuts: 88.94x67.38mm.
- layer_count=2 (F.Cu + B.Cu). Total holes = 4 NPTH + 45 via + 10 small component + 128 standard component + 4 large component = 191. Two trace widths: 0.2032mm and 0.4064mm. 24 SMD apertures on back copper for SMD resistors. All correct.

### Incorrect
- The _summarize function in run_gerbers.py uses data['layers'] and data['drill_files'] which do not exist in the output JSON. The actual keys are data['gerbers'] (list of 11 gerber files) and data['drills'] (list of 2 drill files). This causes the run summary to display 'layers=0 drills=0' even though the analysis is correct. The fix is to update _summarize to use len(data.get('gerbers', [])) and len(data.get('drills', [])).
  (layer_count)

### Missed
(none)

### Suggestions
(none)

---
