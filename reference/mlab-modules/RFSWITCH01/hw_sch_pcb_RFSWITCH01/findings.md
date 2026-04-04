# Findings: RFSWITCH01 / hw_sch_pcb_RFSWITCH01

## FND-00001144: RF chain detected PE4259 switches (U2, U4) and rf_matching networks for SMA antennas; RF chain missing SPF5189Z LNA (U3) as amplifier and FL1 SAW filter; SAW filter (FL1) detected as 'filter' compo...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RFSWITCH01.kicad_sch
- **Created**: 2026-03-23

### Correct
- Correctly identifies 2x PE4259 RF switches with matching L/C networks on RX/TX antenna ports at ~15.9 MHz. 9 LC filters found correctly. ERC no_driver warnings for SW1_CTRL/SW2_CTRL/SW1_#CTRL/SW2_#CTRL are valid — these nets are driven externally via connectors.
- FL1 SAW_AFS434S3-T is correctly categorized as type='filter', category='filter' in the BOM, and appears in statistics.component_types.filter=1.
- The board is powered externally through connectors; no PWR_FLAG symbols present. Warnings for +3V3 and GND are valid ERC findings for this design.

### Incorrect
- rf_chains shows only switches (U2, U4) with total_rf_components=2, amplifiers=[], filters=[]. U3 is an SPF5189Z Low Noise Amplifier and FL1 is a SAW bandpass filter — both are RF chain components and should be included. The chain is also missing connections between stages.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001145: PCB correctly identifies 2-layer board, 290 vias, GND zone stitching, and routing complete; PCB front_side=14 disagrees with gerber component_analysis front_side=15

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: RFSWITCH01.kicad_pcb
- **Created**: 2026-03-23

### Correct
- 45 footprints, 23 nets, routing_complete=True, zone_stitching reports 281 vias at 0.2mm drill for GND net. All matches gerber data exactly.

### Incorrect
- PCB analyzer counts 14 F.Cu footprints (all connectors J* and mounting holes M*). Gerber analyzer reports front_side=15. Likely a counting methodology difference between the two analyzers — one of M1-M4 (NPTH mounting holes) is being counted differently. Minor but represents a cross-analyzer inconsistency.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001146: Complete and correct gerber analysis for 2-layer 40.23x40.23mm RF board

- **Status**: new
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr
- **Created**: 2026-03-23

### Correct
- All 9 layers present (F/B Cu, Mask, Paste, SilkS, Edge.Cuts), drill classification correct (290 vias + 40 component holes + 1 NPTH mount hole), smd_ratio=0.65 accurate (75 SMD pads of 119 total), F.Paste correctly has 0 flashes (all SMD on back side). Min trace 0.3mm consistent with design rules.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
