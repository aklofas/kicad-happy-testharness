# Findings: eez-open/modular-psu / aux-ps_EDA files_KiCad_EEZ DIB AUX-PS

## FND-00000304: Gerber review: Eagle vs KiCad across 16 sets. Three HIGH Eagle bugs: .TXT drill, .G2L inner layers, inch units

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: aux-ps/EDA files/
- **Related**: KH-178, KH-179, KH-180, KH-186
- **Created**: 2026-03-18

### Correct
- KiCad gerber sets (aux-ps, bp3c) produce comprehensive correct analysis: X2 attributes, gbrjob, correct mm units, trace widths
- Standard 7 Eagle layers (.GTL/.GBL/.GTS/.GBS/.GTO/.GBO/.GKO) correctly identified via Protel extension map

### Incorrect
- Eagle .TXT Excellon drill files not recognized -- only globs *.drl. All 12 Eagle sets show drill_files=0, total_holes=0
  (drill_classification)
- Eagle board dimensions in inches mislabeled as mm. aux-ps Eagle: 9.07x2.36 'mm' should be 230.6x60.1mm
  (board_dimensions)
- Eagle .G2L/.G3L inner copper layers not discovered -- file glob misses 3-char Protel extensions. DCP405/MCU 4-layer boards reported as 2-layer
  (layer_count)
- KiCad aux-ps: 3.0/3.2mm NPTH mounting holes classified as component_holes via X2 ComponentDrill
  (drill_classification.mounting_holes)

### Missed
(none)

### Suggestions
- Add .TXT to drill glob
- Add .G2L/.G3L to layer glob
- Convert inches to mm

---
