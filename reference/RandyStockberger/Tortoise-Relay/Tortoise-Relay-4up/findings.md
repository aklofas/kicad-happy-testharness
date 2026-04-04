# Findings: Tortoise-Relay / Tortoise-Relay-4up

## FND-00001636: EC2-12NU relays (RL1–RL4) misclassified as type='resistor'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Tortoise-Relay-4up.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The four EC2-12NU components (refs RL1, RL2, RL3, RL4) are Panasonic EC2-12NU 12 V DPDT relays. The analyzer classifies them as 'resistor', causing component_types to show {'connector': 12, 'resistor': 4} instead of {'connector': 12, 'relay': 4} (or 'other'). The RL prefix and EC2-12NU part name both unambiguously indicate a relay.
  (statistics)

### Missed
(none)

### Suggestions
- Fix: EC2-12NU relays (RL1–RL4) misclassified as type='resistor'

---

## FND-00001637: Edge.Cuts outline file (.gbr) not recognized; missing_required incorrectly lists Edge.Cuts

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerber_Tortoise-Relay-4up.gbr.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The file Tortoise-Relay-4up.gbr is the board outline (Edge.Cuts). It draws a 1.9×1.9-inch rectangle exactly matching the 48.26×48.26 mm board size. However the analyzer labels it layer_type='unknown' (non-standard extension) and reports Edge.Cuts as missing_required. The outline IS present in the gerber set.
  (completeness)

### Suggestions
(none)

---

## FND-00001638: has_pth_drill=False despite a valid PTH drill file with 60 holes being present

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerber_Tortoise-Relay-4up.drl.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The drill file contains 60 holes (T1=1.016 mm × 40, T2=1.092 mm × 16, T3=3.048 mm × 4) in standard Excellon format. The analyzer assigns type='unknown' because the file lacks a PTHONLY header and reports has_pth_drill=False. The file IS a PTH drill file; has_pth_drill should be True.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001639: Via drill size reported as 0 mm for all 8 vias in this KiCad v3 PCB

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Tortoise-Relay-4up.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- KiCad v3 .kicad_pcb format stores vias as '(via (at x y) (size 0.889) (layers F.Cu B.Cu) (net N))' without an explicit drill field. The analyzer reports all vias with drill=0 (size_distribution key '0.889/0') and omits min_drill_mm and min_annular_ring_mm from DFM metrics as a result. The actual via drill size is unspecified in the source file; the report should note this rather than silently using 0.
  (vias)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001886: EC2-12NU relay components (RL1–RL4) misclassified as type 'resistor'; Component count (16), connector count (12), net count (22), and power rails correctly extracted from KiCad 5 legacy format

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Tortoise-Relay_Tortoise-Relay-4up.sch.json
- **Created**: 2026-03-24

### Correct
- 16 total components (12 connectors: 4×PWR terminal blocks, 4×MOTOR connectors, 4×JACK connectors; 4 relays), 22 nets (GND, +12V, and 20 unnamed internal nets), power_rails=[+12V, GND, PWR_FLAG] — all confirmed against the legacy .sch source file. The KiCad 5 legacy parser correctly handles the old format.

### Incorrect
- The four relay components RL1–RL4 (EC2-12NU, a 12V DPDT PCB relay) are classified as type='resistor' because the analyzer falls back to the reference prefix 'RL' being unrecognized and misapplies the 'R'-prefix heuristic, or the KiCad 5 legacy library symbol has no keyword metadata to identify it as a relay. component_types shows 'resistor: 4' instead of a relay category. Correct classification should be 'relay' or at minimum 'other'.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001887: Component group '1PIN' incorrectly groups 4 structural mounting-hole footprints under a non-standard reference; Footprint count (20), track segments (139), via count (8), zones (8), board size (48....

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Tortoise-Relay_Tortoise-Relay-4up.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- 20 modules confirmed in the KiCad 5 .kicad_pcb source (16 electrical + 4 '1PIN' mechanical holes), board outline is 48.26mm × 48.26mm square confirmed from Edge.Cuts coordinates (25.4 to 73.66mm = 48.26mm each side), 8 GND zones (4 per copper layer for the 4-up layout), routing_complete=true with 14 nets all routed.

### Incorrect
- The KiCad 5 PCB file contains 4 instances of a library footprint called '1 pin (ou trou mecanique de percage)' with fp_text reference '1PIN'. The PCB analyzer groups them as component_groups['1PIN'] = {count:4, references:['1PIN','1PIN','1PIN','1PIN']}. All four entries have the same reference string rather than being disambiguated (e.g., 1PIN1–1PIN4). These appear to be mechanical drill holes unrelated to the schematic components. The schematic has no '1PIN' references.
  (component_groups)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001888: has_pth_drill=false is incorrect; drill file contains 60 holes including 4 classified as PTH mounting holes; Layer extents reported in raw inch units instead of millimeters; missing_required report...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Tortoise-Relay_Gerber.json
- **Created**: 2026-03-24

### Correct
- B.Cu (.gbl), B.SilkS (.gbo), B.Mask (.gbs), F.Cu (.gtl), F.SilkS (.gto), F.Mask (.gts) are all correctly identified. Drill file is correctly parsed: 60 total holes split into 56 component holes (40×1.016mm + 16×1.092mm) and 4 mounting holes (3.048mm). Flash counts (60 per copper/mask layer) are consistent with 20 through-hole footprints × 3 pads average.

### Incorrect
- completeness reports has_pth_drill=false and has_npth_drill=false, yet drill_classification correctly identifies 4 PTH mounting holes (3.048mm diameter). The Excellon drill file (Tortoise-Relay-4up.drl) exists with 60 holes but uses old-format headers (FMAT,2 / INCH,TZ) without explicit PTH/NPTH section markers, so the analyzer cannot determine drill type from file structure and defaults to false. The classification is internally contradictory: drill_classification marks 4 holes as PTH while has_pth_drill remains false.
  (completeness)
- alignment.layer_extents reports B.Cu width=1.846, height=1.846 and similar small values for other layers. The gerber files are in inches (%MOIN*%) with format 3.4. The actual B.Cu extent should be approximately 46.9mm × 46.9mm (1.846 inches × 25.4). The board from the PCB analyzer is 48.26mm × 48.26mm, consistent with 1.9 inches — matching the F.SilkS width=1.9. The analyzer reports these extents without converting from inches to millimeters, misleading downstream consumers.
  (alignment)
- completeness.missing_required=['Edge.Cuts'] and complete=false. The Gerber set (7 files) uses the .gbr extension file (Tortoise-Relay-4up.gbr) for board outline data — this file contains 6 draw segments defining a rectangular boundary. The analyzer classifies it as layer_type='unknown' rather than mapping .gbr to Edge.Cuts, so it does not count toward the required layers. The board outline is present but unrecognized.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---
