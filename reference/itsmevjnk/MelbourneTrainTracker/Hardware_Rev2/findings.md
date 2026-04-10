# Findings: itsmevjnk/MelbourneTrainTracker / Hardware_Rev2_Rev2

## FND-00002513: Melbourne train tracker: ESP32-S3 drives 11 AW20216S LED matrix controllers over SPI via 74LS125 bus buffers, with USB-C, SD card, and 3.3V LDO. Correct hierarchical parsing and power regulation, but RGB LEDs misclassified as diodes, SPI CS detection failure, LED driver ICs missed.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Hardware_Rev2_Rev2.kicad_sch.json
- **Created**: 2026-04-09

### Correct
- U17 (XC6220B331MR) correctly identified as LDO regulator with accurate cap enumeration
- U16 (USBLC6-2SC6) correctly identified as ESD protection
- USB Type-C J1 with correct CC1/CC2 5.1k pull-downs for sink role
- RC filters on RESET and BOOT lines correctly detected
- All 5 hierarchical sub-sheets flattened to 1055 components
- MISO multi-driver conflicts correctly identified
- ESD coverage gaps correctly flagged on JTAG, SD card, expansion headers

### Incorrect
- 735 XL-B1010RGBT-HF (D1-D735) classified as 'diode' but are RGB LEDs (description says 'RGBA LED', keywords include 'LED RGB'). Should be 'led' not 'diode'
  (statistics.component_types)
- SPI protocol compliance reports 0 CS lines per bus but each AW20216S has individual CS (L0_CS-L10_CS). CS detection fails on 'Lx_CS' naming pattern and 'CSN' pin name
  (protocol_compliance)
- SPI bus analysis creates 13 duplicate bus entries for 3 physical buses (A, B, C)
  (design_analysis.bus_analysis)
- Decoupling analysis has ic_ref=null for both entries, failing to attribute 78 capacitors to specific ICs
  (signal_analysis.decoupling_analysis)

### Missed
- AW20216S (U1-U11) are LED matrix driver ICs but led_driver_ics is empty
  (signal_analysis.led_driver_ics)
- 74LS125 tri-state bus buffers (U12-U14) fan out SPI to three AW20216S groups — not captured
  (signal_analysis.level_shifters)
- VCC rail voltage should be 3.3V (from XC6220B331MR) but shows voltage=null
  (statistics.power_rails)

### Suggestions
- Classify components with description/keywords containing 'LED' as 'led' regardless of D-prefix
- Recognize CSN/CS pin names on ICs as chip select signals for SPI bus membership
- Deduplicate SPI bus entries sharing same physical nets into single bus with multiple devices
- Detect LED driver ICs by matching known families (AW20216S, IS31FL*, TLC59*, PCA9685)

---
