# Findings: OnBoard / projects_clock_src_ESP32Clock

## FND-00000104: ESP32 clock display with 87 WS2812D-F8 addressable LEDs and AZ1117H-3.3 LDO. Regulator detected but LED chain and decoupling issues noted.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/clock/src/ESP32Clock.kicad_sch
- **Created**: 2026-03-14

### Correct
- Correctly identified AZ1117H-3.3TRG1 as LDO regulator with +5V input and +3.3V output
- Correctly flagged missing decoupling capacitors on ESP32 and regulator rails
- Correctly identified 87 LEDs and component counts
- Correctly identified ESP32-MINI-1-N4 module and USB-C connector

### Incorrect
- IC function not identified for any of the 3 ICs (ESP32, USB-C, AZ1117H) - all show func=?
  (ic_pin_analysis)
- IC ref fields are ? for all components
  (ic_pin_analysis)
- Regulator output noted as missing caps but 10 capacitors on the board may include regulator output caps - needs net-level analysis
  (signal_analysis.design_observations)

### Missed
- WS2812D-F8 LEDs are addressable RGB LEDs in a daisy-chain topology - should detect LED chain/strip pattern with DIN/DOUT connections
  (signal_analysis)
- No analysis of 10 generic capacitors (value=C) - likely decoupling caps that could resolve the missing decoupling warnings if values were parsed
  (signal_analysis.decoupling_analysis)
- USB-C connector type not identified (TYPE-C 16PIN 2MD(073) is an EasyEDA part)
  (ic_pin_analysis)
- ESP32 WiFi/BT capability not noted in any analysis section
  (ic_pin_analysis)

### Suggestions
- Detect WS2812/SK6812 LED chain topology (DIN->DOUT daisy chain)
- Parse capacitor values from footprint or other fields when value field is generic
- Identify ESP32 modules and their wireless capabilities
- IC function lookup should work for common regulator and MCU module part numbers

---
