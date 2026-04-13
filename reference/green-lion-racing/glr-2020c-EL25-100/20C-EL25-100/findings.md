# Findings: green-lion-racing/glr-2020c-EL25-100 / 20C-EL25-100

## FND-00002101: All 3 relays and connector correctly detected as extending outside the board boundary

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_glr-2020c-EL25-100_20C-EL25-100.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The board edge runs from (0,0) to (83.82,-23.5)mm. The three JSM1-12V-5 relays (RLY1-3) are placed at Y≈-3.05mm rotated 90°, and their footprint courtyard extends approximately +2.85mm above Y=0 (the board top edge). J1 (Molex Mega-Fit connector) similarly extends outside. The analyzer reports edge_clearance_mm values of -17.2mm for each relay and -11.27mm for J1. The REF** logo footprint at (76.25, 43.61)mm is also flagged (-43.61mm clearance). This is a genuine design characteristic of through-board-edge connectors/relays that overhang the PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002102: Simple relay board component classification correct; 12V net correctly not classified as power rail

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_glr-2020c-EL25-100_20C-EL25-100.sch.json.json
- **Created**: 2026-03-24

### Correct
- The 6-component relay board (3x JSM1-12V-5, 1x LED, 1x resistor, 1x connector) is correctly classified. The power_rails list contains only GND, which is accurate: the 12V and 12V_SW1 nets are local labels, not power symbols — there are 7 GND power symbols but no 12V power symbol in the schematic. The relay type detection is correct. The ERC warning about net SW having no driver is a valid observation (SW is an input label driven by external connector).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
