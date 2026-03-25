# Findings: giant-board-design-files / 4LayerV0.9.2_ATSAMA5D27-1G

## FND-00002096: ACT8945A PMIC and MIC5247 LDO not detected as power regulators; USB differential pairs USBA_P/M and USBB_P/M not detected; I2C buses detected with correct missing pull-up flag

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_giant-board-design-files_4LayerV0.9.2_ATSAMA5D27-1G.sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer detected 5 I2C bus entries from the I2C_TWD0/TWCK0 and I2C_TWD1/TWCK1 nets. All are correctly flagged has_pull_up=false. The pull-up resistors are not present on this board (the schematic has no resistors connected to these I2C nets) — the design relies on external pull-ups from connected modules. The SPI bus (SPI0_MISO/MOSI/SCK) and UART (UART1_TX/RX) are also correctly detected.

### Incorrect
(none)

### Missed
- The design has U2=ACT8945AQJ305-T (a multi-rail PMIC with 3 DC-DC converters and 4 LDOs) and U3=MIC5247-2.0 (an LDO). Both appear in subcircuits, but power_regulators is empty in signal_analysis. The same miss occurs in the V1 file. The ACT8945A uses a custom lib_id (ACT8945AQJ305-T:ACT8945AQJ305-T) and the MIC5247 uses symbols:MIC5247-2.0 — neither matches whatever pattern the power regulator detector uses for LDO/DCDC recognition. The design also has 3 inductors (L1-L3, NR3015T2R2M) forming the switching converter output filters for the PMIC, which would confirm its DC-DC topology.
  (signal_analysis)
- The design (ATSAMA5D27 SoC) has two full-speed USB ports with signals USBA_P, USBA_M, USBB_P, USBB_M all present as nets. No differential pair detection occurs: design_analysis.differential_pairs is empty, and bus_analysis has no USB entry. There is also no usb_compliance section (unlike KiCad 6+ schematics). This is a KiCad 5 legacy schematic, so usb_compliance is not expected, but the differential pair grouping from naming conventions should still be possible. The PCB shows the USB nets are properly matched in length (USBA: 27.0/27.0mm, USBB: 32.283/32.226mm).
  (design_analysis)

### Suggestions
(none)

---

## FND-00002097: 4-layer BGA board correctly classified as advanced DFM tier

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_giant-board-design-files_4LayerV0.9.2_ATSAMA5D27-1G.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The ATSAMA5D27 design is a 22.86×50.8mm 4-layer board (F.Cu, In1.Cu power, In2.Cu power, B.Cu). The analyzer correctly identifies three DFM violations requiring advanced process: track width 0.1143mm (below standard 0.127mm limit), track spacing 0.1162mm, and annular ring 0.102mm. Footprint count matches schematic (172 on both sides). The ACT8945A PMIC (U2) thermal pad has only 1 via vs recommended 5-9 minimum, correctly flagged as insufficient.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
