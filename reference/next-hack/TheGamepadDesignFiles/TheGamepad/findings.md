# Findings: next-hack/TheGamepadDesignFiles / TheGamepad

## FND-00001634: DISP1 (Adafruit4311 display) misclassified as 'diode' type; key_matrices detector fires a false positive on this shift-register gamepad; bus_topology 'width' field reports total pin-connection coun...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TheGamepad.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- DISP1 uses lib_id=DoomWSTK:Adafruit4311 which is a custom symbol for an Adafruit ST7789 display module. The analyzer classifies it as type='diode', inflating the diode count to 4 (D1, D2, D4, DISP1). The actual diode count is 3 (D1=BAT43, D2=1N5817, D4=BAT43). DISP1 should be classified as 'ic' or 'other' not 'diode'.
  (statistics)
- The detector reports a 2-row × 17-column key matrix with row_nets=['BL', '__unnamed_28'] and diodes_on_matrix=17. In reality this is a gamepad using two 74HC165 parallel-in shift registers to read 17 buttons; there is no matrix. BL is the display backlight control signal; __unnamed_28 is the 5 V supply rail via BAT43 protection diodes D1 and D4. Only 3 physical diodes exist in the design (D1, D2, D4), none of which form a matrix. The estimated_keys=17 and diodes_on_matrix=17 are both wrong.
  (signal_analysis)
- The 'width' field in detected_bus_signals equals the total number of pad connections across all nets with that prefix, not the number of distinct signal lines. K_C (K_C0..K_C3) reports width=12 (4 nets × 3 pins each) but the bus is only 4 bits wide. MISO_, MOSI_, SCK_ each report width=4 (2 nets × 2 pins) but are each 2-bit groups. The 'range' field (e.g. 'K_C0..K_C3') is correct; 'width' is not.
  (bus_topology)
- Every entry in the 'components' list has ref=None, even though the BOM and subcircuits correctly populate refs (A1, C1, D1, etc.). The analyzer extracts refs from the (instances ...) block for BOM construction and subcircuit detection but fails to populate the ref field in the flat components list. This is a KiCad 8 format parsing issue. Affected: TheGamepad.kicad_sch (140 components, all ref=None).
  (components)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001635: smd_count reports 14 instead of 12; two no-attr graphical footprints counted as SMD; All footprint refs are None in the footprints list for this KiCad 8 PCB

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: TheGamepad.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The PCB has 12 footprints with attr=smd and 2 footprints (REF** / SPEAKER_SYMBOL_4x4) with no attr at all. The analyzer defaults footprints with no attr to SMD, producing smd_count=14 instead of the correct 12. The two SPEAKER_SYMBOL_4x4 footprints are graphical-only (no pads, no copper function) and should not be counted as SMD components.
  (statistics)
- Every entry in the 'footprints' list has ref=None despite the PCB file containing (property "Reference" "X") entries for all 88 footprints. The component_groups, courtyard_overlaps, decoupling_placement and other sections correctly use refs (A1, U2, R10, etc.), confirming refs are parsed elsewhere but not propagated to the footprints list.
  (footprints)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001884: DISP1 (Adafruit 4311 OLED display) misclassified as type 'diode'; Key matrix detected (18 switches across button nets), speaker circuits, transistor, and decoupling all correctly identified

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TheGamepadDesignFiles_TheGamepad.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- key_matrices correctly detects the button matrix structure. buzzer_speaker_circuits correctly identifies LS1 and LS2 (Speaker). transistor_circuits correctly identifies Q1 as a PMOS power switch (TSM480P06CH) with gate resistor R4. has_transistor_driver=false for speakers is correct because Q1 is a battery switch on the drain net, not a speaker driver. decoupling_analysis correctly identifies multiple 100nF caps on +3V3. Component counts (18 switches, 16 caps, 24 resistors, 5 ICs) are accurate.

### Incorrect
- The symbol DoomWSTK:Adafruit4311 has its default Reference property set to 'D' in the embedded symbol definition, causing the analyzer to infer type='diode'. The Adafruit 4311 is a 128x64 OLED display (SSD1306 controller), not a diode. The BOM also groups it under type='diode'. The correct type should be 'ic' or 'display'.
  (components)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001885: smd_count over-reports by 2: reports 14 SMD but source has 12 footprints with (attr smd); Board dimensions, layer counts, routing completeness, and front/back placement are accurate

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: TheGamepadDesignFiles_TheGamepad.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- 88 footprints confirmed (all 88 found in source), front=27 on F.Cu and back=61 on B.Cu both verified by counting footprint layer attributes in source. Board 128.528mm x 66.763mm, 2-layer, 855 track segments, 290 vias, 1 zone, 63 nets, routing_complete=true, 0 unrouted. All match the PCB source file.

### Incorrect
- The PCB source has exactly 12 footprints with '(attr smd)': SW16, SW3, SW17, LS2, SW4, LS1, RP1, SW12, RP2, SW2, SW15, SW5. The analyzer reports smd_count=14, including two graphical symbol footprints (DoomWSTK:SPEAKER_SYMBOL_4x4, reference REF**) that have no attr tag and no pads. These are silkscreen-only artwork footprints that should not be counted as SMD components. Total footprint count (88) and THT count (61) are correct.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
