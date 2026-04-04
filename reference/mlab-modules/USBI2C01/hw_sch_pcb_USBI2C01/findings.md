# Findings: USBI2C01 / hw_sch_pcb_USBI2C01

## FND-00001755: CP2112 USB-to-I2C bridge IC (X1) misclassified as 'connector' instead of 'ic'; I2C bus not detected despite CP2112 having SDA/SCL pins connected; SV1-SV7 connector/header components misclassified a...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: USBI2C01.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly finds X2 (USB_B connector) and notes that no USB ESD IC is identified (info-level only). The CP2112 integrates USB 2.0 full-speed phy internally, so no external ESD IC is expected. The result of 1 info-level check with 0 pass/fail is reasonable.
- Two decoupling entries: +3.3V with C2 (10uF) + C3 (100nF) = 10.1uF total (bulk + bypass), and +5V with C1 (1uF). These match the schematic. C4 (4u7) connects to +3.3V line going to CP2112 VIO pin and is also correct.

### Incorrect
- X1 is the Silicon Labs CP2112 USB-to-I2C bridge IC, the central active device in this design. Its lib_id is 'untitled-eagle-import:CP2112' (imported from Eagle). The analyzer classifies it as type='connector' because the library name lacks standard IC classification heuristics. This causes the design to show 0 ICs in the component_types breakdown, omits it from IC pin analysis, and prevents USB compliance checking from recognizing it as an active USB device.
  (statistics)
- Seven pin header connectors (SV1=MA02-1, SV2/SV5=MA05-2, SV3=MA03-1, SV4/SV6=MA03-2, SV7=MA01-1) are classified as type='switch' in component_types. These are standard male pin headers (MA series from MLAB/Eagle library), not switches. The misclassification arises because their lib_ids from 'MLAB_HEADER:HEADER_*' are mapped to the 'switch' category. The component_types breakdown shows switch=7, connector=7 when the true count should be connector=14 (7 SV headers + 7 others).
  (statistics)

### Missed
- The CP2112 (X1) has its SDA pin on net '__unnamed_11' and SCL pin on net '__unnamed_12'. Because these nets are unnamed (no net labels in the schematic — they use pin names only), the I2C bus detector cannot identify them by name pattern. The bus_analysis.i2c array is empty and design_observations contains no i2c_bus entries. This is a missed detection for a design whose primary purpose is USB-to-I2C conversion.
  (design_analysis)

### Suggestions
- Fix: CP2112 USB-to-I2C bridge IC (X1) misclassified as 'connector' instead of 'ic'
- Fix: SV1-SV7 connector/header components misclassified as 'switch' type

---

## FND-00001756: PCB footprint count, via count, and routing completeness correct; SMD/THT component split correctly identified: 14 SMD (back) and 12 THT (front)

- **Status**: new
- **Analyzer**: pcb
- **Source**: USBI2C01.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- 26 footprints, 2-layer board, 193 track segments, 11 vias, routing_complete=true, 0 unrouted nets. Board is 29.97 x 40.13 mm (portrait orientation). All match the source KiCad PCB file.
- All 14 SMD components (C1-C4, D1-D4, P1, R1/R3/R4/R5, X1) are on B.Cu. All 12 THT components (SV1-SV7, X2-X6) are on F.Cu. PCB statistics correctly shows smd_count=14, tht_count=12, front_side=12, back_side=14.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
