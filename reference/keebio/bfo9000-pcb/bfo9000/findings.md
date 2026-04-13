# Findings: keebio/bfo9000-pcb / bfo9000

## FND-00001954: 6x9 keyboard matrix with 54 switches and 54 diodes correctly detected; I2C pullup resistors R1 (SCL) and R2 (SDA) correctly identified with VCC rail; USB connectors (USB1, USB2) correctly typed as ...

- **Status**: new
- **Analyzer**: schematic
- **Source**: bfo9000.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The bfo9000 is a 54-key keyboard (6 rows A-F, 9 columns 1-9). The key_matrices detector correctly identifies rows RowA-RowF, columns Col1-Col9, 54 switches (SW_Push), and 54 diodes using topology detection. The estimated_keys=54 matches exactly the actual component count.
- Two I2C bus observations are reported: SDA net pulled up to VCC via R2, and SCL net pulled up to VCC via R1. The sole I2C device is U1 (ProMicro). This matches the source schematic where R1 and R2 are 4.7k pull-ups for I2C to the OLED display.
- USB1 and USB2 (HRO-TYPE-C-31-M-12 USB-C receptacles) are typed as 'connector' in the BOM output. This is correct — they are mechanical connectors, not ICs. The type field reflects the component category accurately.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001955: PCB statistics correctly reflect 286 footprints, 6x9 keyboard layout, fully routed; missing_switch_labels warning incorrectly flags all 54 keyboard switches plus reset switch; DFM correctly identif...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: bfo9000.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- 286 footprints are detected (280 front, 6 back), 2 copper layers, 84 nets, 1013 track segments, 46 vias, 2 zones, and 0 unrouted nets. The 54 key switches, 54 diodes, 4 mounting holes, test points, USB-C connectors, and ProMicro footprint all account for the total correctly.
- The PCB has vias with 0.4mm drill diameter. The analyzer computes 0.1mm annular ring (below the standard 0.125mm threshold) and correctly flags this as requiring an advanced fabrication process. The board size violation for 171.45 x 116.979mm exceeding 100x100mm is also correctly reported as a pricing tier factor.

### Incorrect
- The silkscreen documentation_warnings include 'missing_switch_labels' for all 54 keyboard switches (SW_A1 through SW_F9) and SW_RESET1. The keyboard switches have no need for individual silkscreen function labels. SW_RESET1 is a legitimate candidate for a warning but the keyboard key switches are false positives. This is the same over-broad switch-label heuristic seen in beyblock20.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001956: Gerber set correctly identified as complete despite missing F.Paste layer; Drill hole counts and tool sizes correctly parsed for large through-hole keyboard PCB

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerbers_pcb.json
- **Created**: 2026-03-24

### Correct
- The bfo9000 has no F.Paste gerber (all switches/THT components don't need solder paste). The analyzer reports it in missing_recommended rather than missing_required, and still marks complete=true. This is correct — paste layers are not required for all-THT/keyswitch boards.
- 981 total holes are detected: 29 vias (0.4mm), 882 component holes across multiple tool sizes (0.3mm SMD pad holes, 1.5mm, 2.0mm, 3.0mm, 3.5mm for MX switch mounts and connector holes), and NPTH holes. The large number of component holes (148 at 0.3mm) corresponds to the SMD USB-C pads and diodes.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
