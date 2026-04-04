# Findings: OnBoard / projects_Debate-Device_src_Debate Device

## FND-00000102: Arduino Nano-based debate timer with buzzer, OLED display, rotary encoder, addressable LEDs, and push buttons. Good detection overall.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/Debate-Device/src/Debate Device.kicad_sch
- **Created**: 2026-03-14

### Correct
- Arduino_Nano_v3.x correctly identified as IC type
- Buzzer correctly detected with direct GPIO drive from Arduino (no transistor driver)
- 5 SK6812MINI addressable LEDs correctly classified as LED type
- Rotary encoder with switch correctly classified as switch type
- Power rails +5V and GND correctly detected

### Incorrect
(none)

### Missed
- SSD1306 OLED module (Brd1) is on I2C bus (SCL/SDA pins connected to Arduino A4/A5) but I2C bus analysis only shows Arduino, not the OLED. The SSD1306 is typed as other rather than display/ic.
  (design_analysis.bus_analysis)
- SK6812MINI LEDs use a serial data protocol (single-wire NZR) but no observation about addressable LED chains is generated
  (signal_analysis.design_observations)

### Suggestions
- SSD1306 OLED modules from custom libraries should be detected as I2C display devices when they have SCL/SDA pins
- SK6812/WS2812 addressable LED chains could be noted as a design observation

---
