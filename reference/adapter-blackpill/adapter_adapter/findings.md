# Findings: adapter-blackpill / adapter_adapter

## FND-00001975: Component count correct: 28 total, correct type breakdown; SPI bus correctly detected on both left and right sides; I2C bus correctly detected on both sides (scl_l/sda_l and scl_r/sda_r); I2C repor...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: adapter.kicad_sch
- **Created**: 2026-03-24

### Correct
- Analyzer reports 28 total_components with connector:12, resistor:8, ic:2, mounting_hole:4, switch:2. This matches the actual schematic (STM32 Blackpill adapter with 12 connectors including J1-J12, R1-R8 5.1k resistors, U1/U2 Blackpill breakouts, H1-H4 mounting holes, SW1/SW2 buttons).
- The analyzer correctly identifies two SPI buses: bus_id 'L' (mosi_l/sck_l/miso_l on U2, chip_select_count:4) and bus_id 'R' (mosi_r/sck_r/miso_r on U1, chip_select_count:6). The schematic net names confirm these SPI signals, and the trackball+EEPROM CS nets are present on both sides.
- Analyzer correctly finds four I2C net entries: scl_r (U1), sda_r (U1), scl_l (U2), sda_l (U2). These are real I2C signals present in the schematic for the Charybdis keyboard's per-side I2C buses.
- Analyzer identifies three power rails matching the schematic. The +5V rail powers all connectors and both STM32 modules; +3.3V is used for pull-up resistors R1-R3/R6/R7 on signal lines.

### Incorrect
- The analyzer correctly reports has_pull_up:false for all I2C nets. This is a correct observation, not a false positive: the Charybdis Blackpill holder is an adapter PCB; pull-ups for I2C are expected to be on the peripheral boards themselves. The finding is accurate.
  (design_analysis)
- signal_analysis section reports rc_filters:[] and all other signal detectors empty. The schematic has R1-R8 (5.1k resistors) on the serial lines, but these are current-limiting/protection resistors in series with connector signals, not true RC filters. The empty result is correct for RC filters specifically.
  (signal_analysis)
- The signal_analysis.decoupling_analysis array is empty. The design_observations correctly notes that U1 and U2 have rails_without_caps ['+3.3V', '+5V']. This is accurate: the Blackpill breakout modules have their own decoupling capacitors built in, so the adapter board intentionally has no decoupling caps. The finding is correct behavior.
  (signal_analysis)

### Missed
- The nets serial_l and serial_r are clearly named for UART serial communication (connected to STM32 PA9/PA10 UART1 TX/RX via 5.1k resistors). The analyzer places them under design_analysis.net_classification as 'signal' but bus_analysis.uart is empty []. These should be detected as UART bus signals.
  (design_analysis)
- Nets rgb_l and rgb_r appear in net_classification as 'signal', and connectors J3/J4 are labeled 'RGB'. signal_analysis.addressable_led_chains is empty []. The analyzer should detect these as potential WS2812/addressable LED data lines.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001976: Layer set complete: all 9 expected layers present for 2-layer board; F.Paste empty (no front SMD paste) correctly detected; Drill classification correctly identifies vias at 0.305mm and PTH compone...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerbers
- **Created**: 2026-03-24

### Correct
- Gerber reports completeness.complete:true with 9 found layers (B.Cu, B.Mask, B.Paste, B.SilkS, Edge.Cuts, F.Cu, F.Mask, F.Paste, F.SilkS) and missing_required:[]. This is correct for a 2-layer THT+connector board.
- The board has no front-side SMD pads (all SMD pads are on the back for the through-hole connectors' SMD footprints). F.Paste layer_extents show width:0/height:0, consistent with an empty paste layer. The pad_summary shows smd_ratio:0.14 with SMD pads on back only.
- 45 vias at 0.305mm, 10×0.6mm PTH, 128×1.0mm PTH, 4×4.0mm PTH (mounting holes), and 4×1.5mm NPTH (panel holes). The 4.0mm PTH holes correspond to the 4 M4 mounting holes in the schematic.
- Gerber reports board_dimensions width_mm:88.94, height_mm:67.38 from Edge.Cuts. This is consistent with a compact split keyboard adapter board housing two 40-pin Blackpill breakout modules side by side.

### Incorrect
(none)

### Missed
- The alignment section shows B.SilkS width:0/height:0 yet there are 24 SMD pads on the back side. A real back silkscreen is expected for component identification. This may indicate the back silkscreen Gerber file is empty or the analyzer is not detecting the back silkscreen content.
  (alignment)

### Suggestions
(none)

---
