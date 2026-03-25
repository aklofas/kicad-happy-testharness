# Findings: keezyboost40 / pcb_keezyboost40_keezyboost40

## FND-00002232: ST7735 SPI display misclassified as I2C bus; Key matrix correctly detected as 4×10 with 40 switches and 40 diodes; KiCad version reported as 'unknown' for a valid KiCad 6 format file

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_keezyboost40_pcb_keezyboost40_keezyboost40.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identified a 4-row × 10-column key matrix (40 estimated keys) using topology detection, matching the 40 SW_SPST switches and 40 1N4148 diodes in the BOM. Row nets (r1–r4) and column nets (c1–c10) are correctly identified.

### Incorrect
- The design connects a ST7735_1.8inch display to the Raspberry Pi Pico via signals SCK, SDA (MOSI), CS, DC, and RESET — a standard 4-wire SPI interface. The analyzer detected an I2C bus on the 'sda' net (because the net name contains 'sda') and reported it in bus_analysis.i2c, with no SPI detection. The 'sda' net is actually SPI MOSI misnamed by the designer. The analyzer should look for corroborating SCK/CS/DC signals before concluding I2C.
  (signal_analysis)
- The file has file_version '20211123', which is a KiCad 6 date-stamped format version. The analyzer reports kicad_version as 'unknown' instead of inferring 'KiCad 6' from the file_version integer. This is a missed version classification for the new KiCad 6+ format.
  (kicad_version)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002233: False positive gerber alignment warning: F.Cu extent is legitimately smaller than Edge.Cuts for this keyboard

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_keezyboost40_temp_keezyboost40.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The analyzer flags alignment=false with 'Width varies by 36.9mm across copper/edge layers'. F.Cu width is 180.725mm vs Edge.Cuts 217.586mm. For this keyboard PCB, Kailh hotswap sockets are placed on the back side (B.Cu=212.375mm, much closer to edge). The front copper legitimately does not extend to the full board width since the MCU and display connections are concentrated in one region. B.Cu is only 5.2mm narrower than Edge.Cuts (well within normal variance), so the board is not truly misaligned.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
