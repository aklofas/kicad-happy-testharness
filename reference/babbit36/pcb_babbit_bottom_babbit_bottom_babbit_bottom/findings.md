# Findings: babbit36 / pcb_babbit_bottom_babbit_bottom_babbit_bottom

## FND-00001819: Empty schematic correctly parsed with zero components and nets

- **Status**: new
- **Analyzer**: schematic
- **Source**: babbit_bottom.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The babbit_bottom.kicad_sch file contains only a KiCad schematic header with no symbols, wires, or power rails. The analyzer correctly reports 0 total_components, 0 nets, 0 wires, and all empty signal analysis sections.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001820: Bottom plate PCB with 6 M2 mounting holes and board outline correctly parsed; Board dimensions correctly extracted as 173×71mm; DFM violation correctly flagged for board exceeding 100×100mm JLCPCB ...

- **Status**: new
- **Analyzer**: pcb
- **Source**: babbit_bottom.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The babbit_bottom PCB is a keyboard bottom plate with only 6 MountingHole_2.2mm_M2_ISO7380 footprints and no electrical components, no tracks, and no nets. The analyzer correctly identifies 6 footprints, 0 nets, 0 tracks, 0 vias, board dimensions 173×71mm, all excluded from BOM and pos files.
- The Edge.Cuts gerber and PCB bounding box both confirm 173×71mm board size, matching the analyzer output of board_width_mm=173.0 and board_height_mm=71.0.
- The 173×71mm board correctly triggers a DFM board_size violation noting it exceeds the 100×100mm standard tier at JLCPCB. This is accurate — the board width of 173mm exceeds the threshold.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001821: Gerber set complete with 9 layers and 2 drill files; 6 NPTH mounting holes correctly identified at 2.2mm diameter; Alignment flagged as misaligned but this is expected for a no-copper plate design

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerbers.json
- **Created**: 2026-03-24

### Correct
- The babbit_bottom gerber set is complete: 9 gerber files (F.Cu, B.Cu, F/B.Mask, F/B.Paste, F/B.SilkS, Edge.Cuts) plus PTH and NPTH drill files. All expected layers present, no missing or extra layers.
- The NPTH drill file contains exactly 6 holes at 2.2mm diameter, matching the 6 M2 mounting holes in the PCB layout. The drill classification correctly categorizes all 6 as mounting_holes.

### Incorrect
- The alignment checker reports 'aligned: false' with 'Width varies by 144.9mm across copper/edge layers' and 'Height varies by 32.5mm'. However, B.Cu has 0 draws and 0 flashes (no copper at all), and F.Cu only contains courtyard/fab outline draws for the mounting holes — neither layer spans the full board as there are no electrical components. This misalignment warning is a false positive for a purely mechanical board with no copper routing.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001822: 83 total components correctly identified: 36 diodes, 37 switches, 6 mounting holes, 2 connectors, 2 ICs; 4×10 key matrix with 36 switches and 36 diodes correctly detected; I2C bus falsely detected ...

- **Status**: new
- **Analyzer**: schematic
- **Source**: pcb_bancouver40_cfx_bancouver40_cfx.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The schematic has 36 D_Small diodes, 36 SW_Push key switches + 1 SW_SPST power switch = 37 switches, 6 MountingHoles, J1 (JST PH 2-pin) + J2 (pin header 2-pin) = 2 connectors, U1 (xiao-ble) + U2 (74HC595) = 2 ICs. Total 83 components confirmed against source schematic.
- The bancouver40_cfx is a 40% keyboard with a 4-row × 10-column matrix. The analyzer correctly detects it via net_name method: row1-row4 and col1-col10 named nets, 36 switches on matrix, 36 diodes on matrix, estimated_keys=36. The switch count slightly undershoots 37 total switches as SW41 (power switch) is not on the matrix.
- The design uses SPI to drive the 74HC595 shift register for key column scanning. The analyzer correctly identifies MOSI, SCK signals shared between U1 and U2, and io_cs as the chip select. The bus mode is half_duplex (no MISO) which is correct — the 74HC595 is write-only.
- In the schematic, all 36 D_Small diodes and 6 MountingHole components have no footprint assigned (the footprint field is empty). U1 (xiao-ble) also lacks a footprint in the schematic, though it has one assigned in the PCB file via a custom library. The analyzer correctly lists these in missing_footprint.
- Neither U1 (Seeed XIAO BLE) nor U2 (74HC595) have decoupling capacitors on the VCC rail in this design. The analyzer correctly identifies both ICs in design_observations with category 'decoupling' and rails_without_caps: ['vcc'].

### Incorrect
- The bus_analysis.i2c section reports col1 as SDA and col2 as SCL connected to U1 (xiao-ble). In reality, col1 and col2 are keyboard matrix column signals routed to the Seeed XIAO BLE pins that happen to have SDA/SCL alternate function names (A8_SDA/0.04_H and A9_SCL/0.05_H). These pins are used as GPIO for scanning keyboard columns, not as I2C communication. There is no I2C bus, no I2C pull-up resistors, and no I2C peripheral on the design. The analyzer is misclassifying GPIO usage of I2C-capable pins.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001823: PCB correctly identified with 83 footprints, 2-layer, 422 tracks, 85 vias, 67 nets; Component split correctly reported: 42 front (switches + mounting holes), 41 back (diodes, MCU, shift register, m...

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_bancouver40_cfx_bancouver40_cfx.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The bancouver40_cfx PCB has 83 footprints (36 SW Kailh sockets, 36 diodes, 6 mounting holes, 2 connectors, U1 XIAO BLE, U2 74HC595, SW41 power switch), 2 copper layers, 422 track segments, 85 vias, and 67 nets. All values match the source .kicad_pcb file.
- The 36 key switch sockets (Kailh PG1350) plus 6 mounting holes are on F.Cu = 42 front. The 36 diodes (D_MiniMELF_Handsoldering), U1 (xiao-ble-smd), U2 (SOIC-16), J2 (pin header), and SW41 (SPDT) are on B.Cu = 41 back. This is an unusual split-layer keyboard design where sockets are on top and diodes on bottom.
- SMD count of 75 covers 36 Kailh sockets (SMD) + 36 diodes (SMD) + U1 (SMD) + U2 (SMD) + SW41 (SMD) = 75. THT count of 2 covers J1 (JST PH horizontal) and J2 (pin header) which are through-hole. The 6 mounting holes are excluded from SMD/THT counts as they have no electrical pads.
- The PCB has routing_complete=true and unrouted_net_count=0, which is confirmed by the source file having all nets connected and no ratsnest. Track length of 2707mm across 422 segments and 85 vias is plausible for a 170×68mm keyboard PCB.
- The 170×68mm PCB: height 68mm is under 100mm but width 170mm exceeds 100mm. The analyzer assigns dfm_tier='standard' and does not flag a size violation. Depending on the fabricator this may be acceptable at standard pricing, and the output does not add unnecessary warnings here.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001824: Gerber set complete with 9 layers, 2 drill files, 321 total holes; Key switch stabilizer and plate cutout NPTH holes misclassified as mounting holes; 0.9mm and 0.991mm NPTH holes misclassified as c...

- **Status**: new
- **Analyzer**: gerber
- **Source**: pcb_bancouver40_cfx_gerbers.json
- **Created**: 2026-03-24

### Correct
- The bancouver40_cfx gerber set includes all 9 expected layers (F/B.Cu, F/B.Mask, F/B.Paste, F/B.SilkS, Edge.Cuts), PTH drill (97 holes: 85 vias + 2 JST + 2 J2 headers + 8 SW41 non-standard) and NPTH drill (224 holes: switch plate cutouts and mounting holes). Completeness check passes.
- The PTH drill file has 85 holes at 0.4mm which are vias, matching the PCB analyzer's via_count=85. The gerber drill_classification correctly identifies 85 vias at 0.4mm diameter.
- The B.Mask gerber x2_component_count=83 matches the total footprint count in the PCB. The gerber component_analysis.total_unique=83 is correct.
- The bancouver40_cfx PCB uses a single trace width of 0.25mm throughout, which matches the design rules in the .gbrjob file (MinLineWidth: 0.25) and the gerber conductor aperture analysis reporting a single width of 0.25mm.

### Incorrect
- The drill classification reports 114 'mounting_holes' including 72 holes at 3.0mm NPTH, 36 holes at 3.429mm NPTH (likely PCB-mount stabilizer holes or switch plate fixings), and 6 holes at 4.0mm NPTH (true M4 mounting holes). The 36+72=108 holes at 3.0mm and 3.429mm are Kailh socket or stabilizer/PCM12 related NPTH features, not board mounting holes. Only the 6 holes at 4.0mm are true M4 mounting holes. The diameter_heuristic misclassifies these because 3.0mm and 3.429mm exceed the via threshold but aren't board mounting hardware.
  (drill_classification)
- The drill classification reports 122 'component_holes' which includes 2 holes at 0.9mm NPTH, 36 holes at 0.991mm NPTH, and 72 holes at 1.702mm NPTH. The 0.991mm and 1.702mm NPTH holes are the Kailh PG1350 socket mounting pin holes (non-plated retention posts), not component holes in the traditional sense. The 0.75mm and 1.016mm PTH holes (connector and through-hole pads) are correctly in component_holes but lumped with the NPTH switch socket retention holes.
  (drill_classification)

### Missed
(none)

### Suggestions
- Fix: Key switch stabilizer and plate cutout NPTH holes misclassified as mounting holes
- Fix: 0.9mm and 0.991mm NPTH holes misclassified as component holes

---
