# Findings: Pi-Compute-3-Lite-BLANK / Pi-Compute-3-Lite_BLANK

## FND-00001101: Legacy KiCad 5 schematic parsed correctly: 33 components, 22 nets, correct component type breakdown

- **Status**: new
- **Analyzer**: schematic
- **Source**: Page_1.sch.json
- **Created**: 2026-03-23

### Correct
- 4 ICs, 6 resistors, 18 capacitors, 2 connectors, 1 fuse, 2 inductors. Power rails show only GND — expected for a carrier board where VDD rails come from the CM3 module pins.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001102: Top-level sheet correctly includes Page_1.sch as a subsheet with identical component totals

- **Status**: new
- **Analyzer**: schematic
- **Source**: Pi-Compute-3-Lite_BLANK.sch.json
- **Created**: 2026-03-23

### Correct
- sheets_parsed=2, sheet_files includes both .sch files, same 33 components/22 nets as standalone parse of Page_1.sch — correct deduplication behavior.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001103: copper_layers_used reported as 0 despite F.Cu and B.Cu being defined, and 33 SMD footprints present; board_width_mm and board_height_mm are null despite Edge.Cuts layer being present

- **Status**: new
- **Analyzer**: pcb
- **Source**: Pi-Compute-3-Lite_BLANK.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The PCB has 33 SMD components on F.Cu and nets defined (136 nets, 23 unrouted). F.Cu and B.Cu are in the layers list but copper_layers_used=0 and copper_layer_names=[] is wrong. This is a KiCad 5 legacy PCB format parsing issue — the analyzer fails to count copper layers used when there are no tracks/zones routed yet. The board is clearly a work-in-progress with placed but unrouted components.
  (signal_analysis)
- The board has an Edge.Cuts layer defined in the layer stack, but board_outline edge_count=0 and bounding_box=null. The analyzer did not extract board outline from the legacy KiCad 5 PCB format. This is a known limitation for unfinished boards or legacy format parsing gaps.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
