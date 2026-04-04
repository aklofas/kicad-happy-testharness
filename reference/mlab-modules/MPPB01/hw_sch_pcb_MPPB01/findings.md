# Findings: MPPB01 / hw_sch_pcb_MPPB01

## FND-00000927: 64 Epiphany e-link signals misclassified as UART; I2C bus (I2C_SCL/I2C_SDA) not detected in bus_analysis; assembly_complexity total (29) is higher than statistics total_components (27); Differentia...

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_MPPB01.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 17 differential pairs detected including VADC_P/N, all Epiphany RXI/TXO LCLK, FRAME, and WAIT signal pairs. Pattern matching on _P/_N suffixes is working correctly for these LVDS-style nets.
- The 112 single-pin nets correspond to the many individual GPIO and Epiphany link signals on the SAS Mini connector P5/P6 that are exposed on only one side of the hierarchical design. This is correct — these are nets defined on sub-sheets that only have one connection point visible at the top level.
- GND has power_in pins but no PWR_FLAG in this hierarchical design — the pwr_flag_warnings entry is correct. The design distributes power via connectors rather than regulators.

### Incorrect
- The bus_analysis.uart list contains 66 signals, of which 64 are Epiphany high-speed serial link signals (RXI_DATA_*, TXO_DATA_*, RXI_LCLK, RXI_FRAME, TXI/TXO_WAIT lines). Only UART_RX and UART_TX are genuine UART. The analyzer is matching 'RX'/'TX' substrings in net names to the UART detector, producing massive false positives. These are actually LVDS differential pairs for the Adapteva Epiphany interface.
  (signal_analysis)
- statistics.total_components = 27, assembly_complexity.total_components = 29 (smd=28, tht=1). The BOM also totals 26 entries. This inconsistency is likely caused by the duplicate sheet entry: paracard-elink.kicad_sch appears twice in the sheets list (indices 3 and 5). P4 (a 60-pin Samtec connector) on sheet index 5 is counted again in assembly, even though it is the same physical component. This inflates the assembly complexity count by 2.
  (signal_analysis)

### Missed
- The design has nets I2C_SCL and I2C_SDA (both connected to P3 and P11). The bus_analysis.i2c list is empty in the top-level schematic output, even though these nets exist. The test_coverage section does note '2 i2c' nets, so the nets are found but not promoted to bus_analysis. In the paracard-power sub-schematic output, i2c is also empty despite the nets being present.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000928: MH1 connected to SYS_5P0V net reported as single-pin net — plausible but misleading

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_paracard-mtg.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- MH1 (a mounting standoff) connects to SYS_5P0V via a hierarchical label. The connectivity_issues.single_pin_nets reports this as a single-pin net, which is technically correct within this sub-sheet. However, in the context of the full design SYS_5P0V connects to the power supply. This is a known limitation of per-sheet analysis rather than a bug.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000929: Power schematic components and nets correctly extracted

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_paracard-power.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 4 components (P3, P7, P11, R3), 43 nets, 1 no-connect correctly reported. Power rails VDD_ADJ, VDD_DSP, VDD_GPIO correctly identified. R3 (10k pull-up on UART_RX) and connectors correctly categorized.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000930: PCB statistics correctly reported: 2-layer, 101x101mm, 197 nets, 27 footprints, fully routed; DFM violation correctly flagged: board size exceeds 100x100mm JLCPCB threshold; No differential pair le...

- **Status**: new
- **Analyzer**: pcb
- **Source**: hw_sch_pcb_MPPB01.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- All key metrics correct: footprint_count=27, 2 copper layers (F.Cu, B.Cu), 6038 track segments, 249 vias, 7 zones, board 101.092x101.092mm, routing_complete=true. Component side distribution (5 front, 22 back) correctly identifies this as a predominantly back-side populated board.
- Board is 101.092x101.092mm, slightly over the 100x100mm standard JLCPCB pricing threshold. The DFM check correctly identifies this as a board_size violation requiring a higher pricing tier.

### Incorrect
(none)

### Missed
- The PCB carries 64 Epiphany e-link LVDS differential pairs. The net_lengths list only covers 76 of 197 nets and appears focused on high-length nets. There is no pairing of differential signals to check for intra-pair skew or length matching. This is a missed analysis opportunity for a design where LVDS signal integrity is critical.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000931: Gerber completeness and alignment correctly verified; Component count and side distribution consistent between gerber and PCB outputs

- **Status**: new
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr.json
- **Created**: 2026-03-23

### Correct
- All 9 expected layers present (F/B Cu, Mask, Paste, Silkscreen, Edge.Cuts) plus PTH and NPTH drill files. All layers aligned. Layer extents are consistent. Drill classification correctly identifies 249 vias and 91 component holes.
- Gerber component_analysis shows 27 unique components matching PCB statistics. However, gerber reports front_side=19, back_side=8, while PCB reports front_side=5, back_side=22. This discrepancy is because gerber uses X2 aperture function data (19 pads on F.Cu apertures, 8 on B.Cu) while PCB analyzer counts footprint placement layers. The mounting holes and through-hole parts inflate the gerber front count. This is an expected difference in counting methodology, not a bug.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
