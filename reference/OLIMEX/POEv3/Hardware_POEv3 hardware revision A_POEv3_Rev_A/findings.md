# Findings: POEv3 / Hardware_POEv3 hardware revision A_POEv3_Rev_A

## FND-00002002: Component count and type breakdown are accurate; L1 (33uH power inductor) misclassified as ferrite_bead; Cable-PoE1 (IDC cable) misclassified as type capacitor in BOM; TX4138 switching regulator co...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_POEv3_Hardware_POEv3 hardware revision A_POEv3_Rev_A.kicad_sch
- **Created**: 2026-03-24

### Correct
- Analyzer reports 37 total_components with correct breakdown: 7 capacitors, 11 resistors, 2 diodes, 2 ICs, 8 fiducials, 4 mounting holes, 1 connector, 1 jumper, 1 ferrite_bead (L1). Verified against source: 37 unique placed references match exactly. The 10 unnumbered library template definitions (P, D, U, SJ, etc.) in the file are correctly excluded.
- U2 (TX4138) detected as topology=switching with input_rail=Spare1 (PoE bus), feedback divider R11(30.1k)/R10(5.23k). Vout estimate 4.053V uses heuristic Vref=0.6V; actual TX4138 Vref is ~0.795V which gives ~5.37V, but vref_source=heuristic correctly flags the uncertainty. Feedback network correctly attributed.
- Two current sense circuits detected: R6 and R7 (both 0.03R/R1206) as shunts with U2 (TX4138) as sense IC. max_current_50mV_A=1.667A and max_current_100mV_A=3.333A accurately calculated from 0.03R values.
- The +5VP net contains only passive-type components and power_in power symbols (#PWR03, #PWR012), but no power_out driver or PWR_FLAG. The three placed PWR_FLAG instances (#FLG01-03) are on GND and Spare1 nets, not +5VP. The warning is a genuine ERC concern.

### Incorrect
- L1 has lib_id "OLIMEX_RCL:L" (plain inductor symbol) and value "33uH/2.1A/DCR=0.1R/20%/DBS135" — this is a high-current power inductor used in the TX4138 switching regulator output stage, not a ferrite bead. statistics.component_types shows "ferrite_bead: 1" which should be "inductor: 1". The BOM entry also has type="ferrite_bead" instead of "inductor".
  (statistics)
- Cable-PoE1 has lib_id "OLIMEX_OTHER:Cable-IDC" and value "CABLE-PH2-4-60-R" — it is a cable/connector. The BOM entry records type="capacitor" instead of "connector". This is a library name parsing error where an unknown lib_id falls through to an incorrect default type. The statistics.component_types.connector count of 1 (POE_PWR1) is correct, but Cable-PoE1 should add a second connector.
  (statistics)

### Missed
- The TX4138 (U2) output stage uses L1 (33uH) as a series filter inductor with C6 (470uF) to GND on the +5VP rail. lc_filters is empty. This LC forms the standard output filter of the switching regulator and should be reported.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002003: PCB footprint count of 44 correctly accounts for 7 PCB-only decorative footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_POEv3_Hardware_POEv3 hardware revision A_POEv3_Rev_A.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Schematic has 37 components; PCB has 44 footprints. Delta of 7: Logo_OLIMEX_SMALL_TB, Logo_OLIMEX_TB, Sign_Antistatic_150, Sign_CE, Sign_OSHW_7.3x6.0mm, Sign_PB-Free, Sign_RecycleBin_1. 4-layer, 30x30mm, fully routed.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002004: Gerber layer set is complete for a 4-layer board

- **Status**: new
- **Analyzer**: gerber
- **Source**: repos_POEv3_Hardware_POEv3 hardware revision A_Gerbers
- **Created**: 2026-03-24

### Correct
- All 11 layers present (F.Cu, B.Cu, In1.Cu, In2.Cu, F/B Mask, Paste, SilkS, Edge.Cuts). Both PTH and NPTH drill files present. completeness.complete=true. 30x30mm matches PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
