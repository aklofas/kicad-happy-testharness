# Findings: Voron-Hardware / V0_Display_RP2040_KiCad_V0_Display_RP2040

## FND-00000077: V0 Display RP2040 - well-analyzed KiCad 6+ schematic with good coverage of RP2040 support circuitry

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/Voron-Hardware/V0_Display_RP2040/KiCad/V0_Display_RP2040.kicad_sch
- **Created**: 2026-03-14

### Correct
- AP2127K-3.3 LDO correctly detected with VBUS input and +3V3 output rail
- Crystal circuit (12MHz) properly analyzed with 2x 30pF load caps giving 18pF effective load - calculation correct
- USBLC6-2P6 USB ESD protection correctly detected on both D+ and D- lines (4 entries for upstream/downstream)
- W25Q16JVUXIQ SPI flash memory interface detected with 6 shared signal nets to RP2040
- I2C bus (SCL/SDA) correctly flagged as missing pullup resistors - important design observation for RP2040
- Decoupling analysis: +3V3 has 10 caps (6.5uF total) with both bulk and bypass - good for RP2040
- RC filter on RUN pin (10K + 100nF, fc=159Hz) correctly identified as power-on reset delay
- 22 no-connect markers properly counted

### Incorrect
- AVDD rail flagged as missing decoupling for RP2040 (U5) but AVDD typically has dedicated filtering via inductor - may be present but on a different net name
  (signal_analysis.design_observations)
- RC filter on OSC_OUT (1K + 30pF, fc=5.3MHz) is actually part of the crystal circuit load capacitor network, not a separate filter
  (signal_analysis.rc_filters)

### Missed
- No encoder/rotary switch detection - board has 4 switches including encoder with A/B/switch signals
  (signal_analysis)
- OLED/display interface not characterized despite being the primary function of this board
  (signal_analysis)
- RP2040 boot mode configuration (USB boot vs flash boot) not analyzed
  (signal_analysis)

### Suggestions
- Avoid double-counting crystal load caps as RC filters
- Add rotary encoder detection (A/B/switch pattern)
- Add I2C/SPI display interface detection (OLED, LCD modules)

---
