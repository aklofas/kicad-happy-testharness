# Findings: kicad-make / tests_reference-outputs_globlib_test_project

## FND-00002252: HDMI connector and 8 differential pairs correctly detected in hierarchical schematic; Power symbols in hierarchical schematic all return None reference and None net; HDMI bus alias member resolutio...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-make_tests_test_project_test_project.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies J1 as an HDMI_A connector, and detects all 8 differential pairs: 4 TMDS pairs (ADV7611_D0/D1/D2/CK) and 4 HDMI-labeled pairs (hdmi_in.D0/D1/D2/CK). ESD protection is correctly noted on the ADV7611 TMDS pairs.

### Incorrect
- The power_symbols array contains 59 entries but every item has null reference and null net fields (while a flat schematic like kicad-keyboards correctly returns net_name, x, y, lib_id). This means pwr_flag_warnings fire on DVDDIO, GND, +5V, DVDD, and +3V3 even though PWR_FLAG appears in the statistics power_rails list (the symbol exists in a sub-sheet). This is a parsing bug for power symbols in hierarchical/multi-sheet schematics.
  (power_symbols)

### Missed
- The HDMI bus alias defines 12 members (D2+, D2-, D1+, D1-, D0+, D0-, CK+, CK-, HPD, SDA, SCL, CEC). The analyzer reports present_labels=0 and resolved_nets=0 for all 12, listing them all as unresolved. However, the actual nets use dot-notation: hdmi_in.D2+, hdmi_in.D1+, hdmi_in.CK+, etc., which are present in the nets dict. The analyzer matches bare member names ('D2+') but not 'busname.member' form — a systematic miss for bus alias resolution when bus signals are labeled with the 'busname.signal' convention.
  (bus_topology)
- U6 is an RT9742AGJ5F, a 500mA LDO regulator from Richtek in the Power_Management library. Only U4 (AP2112K-1.8) is detected in signal_analysis.power_regulators. U6 appears only in power_budget.rails.+3V3.ics. The RT9742AGJ5F is not in the analyzer's known-regulator list, causing a false negative for regulator detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002253: 8-layer PCB with DFM violation correctly analyzed: via drill 0.1mm below standard

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad-make_tests_test_project_test_project.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies the 8 copper layers (F.Cu, B.Cu, In1–In6), 91 footprints, 706 tracks, 102 vias, and fully routed design. DFM correctly flags a 0.1mm via drill as below the advanced process minimum (0.15mm), classifying the board as 'challenging' tier.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002254: kibuzzard-converted variant correctly shows 2 fewer footprints (89 vs 91)

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad-make_tests_reference-outputs_kibuzzard-to-graphic_test_project.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The kibuzzard-to-graphic variant of the PCB has 89 footprints vs 91 in the standard test_project. The two missing references are 'kibuzzard-67891646' and 'kibuzzard-67891633' — KiBuzzard-generated graphical objects that were converted to plain graphics and removed as footprints. The analyzer correctly captures this difference without error.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
