# Findings: TU-Darmstadt-APQ/RedPitaya-IntStab / pcb_KiCad_RedPitaya_IntStab

## FND-00001240: 12 opamp circuits correctly identified with proper configurations; Voltage dividers and SMA connector detection correct; kicad_version reports 'unknown' for KiCad 7 files (file_version 20230121)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Input_Output_Section.kicad_sch
- **Created**: 2026-03-24

### Correct
- OPA1604 and OPA1602 opamps detected across all units. Unit 3/4 as inverting (gain=-1) and buffer configurations are correct. Unit 1 marked comparator_or_open_loop is reasonable given no direct feedback resistor visible at that hierarchical level.
- 4 voltage dividers detected with correct R values and ratios (0.5 for 1k/1k pairs). 14 SMA connectors detected as connector type. R42/R43 TIA circuits with feedback_resistor ohms=0 correctly detected as transimpedance_or_buffer configuration.

### Incorrect
- All three IntStab schematic files have file_version=20230121 which corresponds to KiCad 7.0, but kicad_version='unknown' is reported. The version should be resolved from the file_version field. Also affects the PCB file (file_version=20221018 = KiCad 6, also reports 'unknown').
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001241: LT8610 switching regulator correctly detected with feedback divider and LC filter; LT3032-12 dual ±12V linear regulator absent from power_regulators list; -12V and -15V nets classified as 'signal' ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Supply_Ref.kicad_sch
- **Created**: 2026-03-24

### Correct
- LT8610 found as topology=switching with inductor L3, bootstrap, FB divider R36/R35. Two LC filters at 33.86kHz correctly computed. SMBJ40CA TVS protection diodes correctly identified on +15V and -15V rails.
- Math is correct: Vfb=0.6V, R36=1M, R35=243k gives Vout=3.069V. The net labeled +5V disagrees with the feedback divider calculation (38.6% difference). This is a genuine discrepancy in the schematic that the analyzer correctly surfaces, regardless of root cause.

### Incorrect
- U1 (LT3032-12) is classified as 'linear regulator' in ic_pin_analysis (function field) but does not appear in signal_analysis.power_regulators. The device outputs both +12V (pin OUTP) and -12V (pin OUTN), and the -12V output is not tracked at all as a power regulator output.
  (signal_analysis)
- In design_analysis.net_classification, both '-12V' and '-15V' are labeled 'signal'. These are power output rails from the LT3032-12 dual regulator and the -15V input supply. Negative supply rails should be recognized as power nets. This also means decoupling coverage for negative rails is not analyzed.
  (signal_analysis)
- GND is flagged as missing PWR_FLAG, but this is a hierarchical sub-sheet where GND is supplied by the parent sheet. The two PWR_FLAG symbols present on this sheet connect to the PWR_FLAG net (not GND), which is correct KiCad practice. ERC passes when evaluated as part of the full hierarchy.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001242: PCB statistics, DFM, and routing correctly analyzed; kicad_version='unknown' for KiCad 6 PCB (file_version=20221018); GND copper pour stitching and thermal analysis correct

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: RedPitaya_IntStab.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 127 footprints, 2-layer 160x100mm board, routing_complete=true, 0 unrouted nets. DFM correctly flags board_size exceeding 100x100mm JLCPCB threshold. min_track_width=0.15mm, min_drill=0.3mm all correctly extracted.
- GND zone spans both F.Cu and B.Cu (31609.7 mm²) with 520 stitching vias at 1.6 vias/cm². +15V pour on F.Cu with 9 stitching vias at 19 vias/cm². Single ground domain with 70 components. These are all plausible values for a 160x100mm analog board.

### Incorrect
- The PCB file contains 'version 20221018' in its header which maps to KiCad 6.0, but the output reports kicad_version='unknown'. This is the same version-resolution failure as the schematic files.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
