# Findings: cheyao/icepi-sbc / hardware_cm0

## FND-00002217: Ethernet PHY differential nets EPHY_RX+/- and EPHY_TX+/- falsely reported as UART signals in bus_analysis.uart; eMMC 8-bit bus correctly detected in cpu schematic with all 10 signals (CLK, CMD, D0-...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_icepi-sbc_hardware_cpu.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The SDIO detector correctly identifies the eMMC bus connected to the Allwinner H3 SoC (U1) with bus_width=8, bus_id='EMMC', and all 10 signals (eMMC_CLK, eMMC_CMD, eMMC_D0 through eMMC_D7). This is a non-trivial detection on a complex multi-sheet SoC schematic.
- Both EPHY_RX+/EPHY_RX- and EPHY_TX+/EPHY_TX- are correctly classified as differential pairs under design_analysis.differential_pairs, each showing has_esd=true. The DDR3 strobe pairs DQS0+/- and DQS1+/- and four HDMI/GPDI differential pairs are also correctly detected.

### Incorrect
- The UART detector fires on EPHY_RX+ and EPHY_RX- (and EPHY_TX+ / EPHY_TX-) because their net names contain substrings matching TX/RX patterns. However, these are Ethernet PHY differential pair signals on the Allwinner H3 SoC (U1), correctly identified as differential pairs elsewhere in the same output under differential_pairs. The four EPHY nets appear in the uart list with pin_count=1 each, which is a false positive.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002218: Six switching buck regulators (U3-U8 with inductors L1-L6) not identified as voltage regulators — only their feedback dividers are detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_icepi-sbc_hardware_power.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The power schematic contains 6 switching regulators generating +3V3_WIFI, +3V3_IO, +3V3_RTC, +1V5, +1V2_SYSTEM, and +1V1_CPUX rails from a +5V input, each with an inductor and multiple output capacitors. The analyzer correctly finds their feedback voltage dividers (is_feedback=true) but does not report any regulator topology, switcher type, or inductor-based power stage. There is no 'regulators' or 'switching_regulators' section in the output, leaving the core power architecture undescribed.
  (signal_analysis)

### Suggestions
(none)

---
