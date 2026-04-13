# Findings: UnsignedArduino/ESP32-Camera-PCB / ESP32 Camera PCB

## FND-00000494: SPI bus not detected despite two SPI peripherals (ArduCam B5 and MicroSD B3) explicitly wired to ESP32 (B2); I2C bus not detected despite RTC (B6) and ArduCam I2C (B5 SDA/SCL) connected through lev...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ESP32 Camera PCB.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The signal_analysis.voltage_dividers correctly identifies R1 (top, 100K) connected to B7/BAT net and R2 (bottom, 100K) to GND, with the midpoint (__unnamed_43) connecting to B2 pin 3 (GPIO36). The ratio 0.5 is correct. This is used for battery voltage monitoring via the ADC input.
- The +3V3 net has only power_in pins (B4/LV, B2/VIN_3.3V, B8/VDD). There is no power_out pin supplying this rail within the schematic — the ESP32 dev board internally generates 3.3V but the schematic symbol only presents a power_in. The analyzer correctly warns that ERC will flag this.
- All 17 BOM components (B1-B9, C1, R1, R2, SW1-SW5) are correctly identified with accurate lib_ids, footprints, values, and coordinates. The pin_uuids match the source. Net connections for named pins (SDA, SCL, MOSI, MISO, CS, CLK, etc.) are correctly traced. Power rails +3V3, +5V, GND are correctly enumerated. The total_nets=67 and total_wires=170 are plausible.

### Incorrect
- The rf_chains detector classified B2 (ESP32_Dev_Board_Breakout), B8 and B9 (ESP32_Camera_Multi_PCB_pins) as RF transceivers. These are general-purpose breakout modules/connectors, not RF components. The ESP32 does have WiFi/BT capability but the symbol here represents the dev board header, not an RF transceiver circuit element. This classification would be confusing at best and misleading for any RF chain analysis.
  (signal_analysis)
- Net __unnamed_1 contains B9 pin 11 (GND, power_in), B1 pin 1 (GND, power_in), plus SW3 pin 2, SW1 pin 2, SW4 pin 2 passive pins. This GND-type net has point_count=12 but is never connected to the main GND net (which is separate). B9 and B1 have floating GND power_in pins. The connectivity_issues section does not flag this, and it is not in single_pin_nets or unconnected_pins. This is a legitimate floating power island that should be flagged.
  (signal_analysis)
- Net __unnamed_18 has only one pin: B7 pin 2 (name GND, type power_out), point_count=1. Similarly __unnamed_19 (B7/LBO, output, 1 pin), __unnamed_22 (B7/USB, power_out, 1 pin), __unnamed_25/26/27/28 (B4 LV2/LV1/HV4/HV3, each 1 pin) are unconnected single-pin nets. These should appear in connectivity_issues.single_pin_nets but the list is empty.
  (signal_analysis)

### Missed
- B5 (ArduCam_OV2640_Breakout) has named pins CS/MOSI/MISO/SCK connected to B2 GPIO15/27/14/13. B3 (Adafruit_MicroSD_Card_Breakout) has named pins CS/DI/DO/CLK connected to B2 GPIO5/23/19/18. Both are canonical SPI connections. The bus_analysis.spi array is empty. These connections are textbook SPI and should be detected.
  (signal_analysis)
- B6 (RTC_Breakout) SDA/SCL pins connect to B4 (I2C_Level_Shifter_Breakout) HV2/HV1 (high-voltage side). B5 (ArduCam) SDA/SCL also connects to B4 HV2/HV1 on the same nets (__unnamed_15, __unnamed_16). B4 LV3/LV4 (low-voltage side) connect to B2 (ESP32) GPIO22/21. This is a complete I2C bus with level shifting. The bus_analysis.i2c array is empty.
  (signal_analysis)
- B4 explicitly separates +3.3V logic (LV side, connected to +3V3 and ESP32 GPIO) from +5V logic (HV side, connected to +5V rail, RTC, and ArduCam). The isolation_barriers list is empty. This is a clear 3.3V/5V level-shifting topology that should be detected, especially since the component name contains 'Level_Shifter'.
  (signal_analysis)
- power_domains.ic_power_rails and domain_groups are both empty. The schematic has B4 (I2C_Level_Shifter) separating a 3.3V domain (ESP32 + B8 connector) from a 5V domain (ArduCam B5, RTC B6). Cross-domain signals (the I2C lines through B4) are also not in cross_domain_signals. This is a missed analysis opportunity.
  (signal_analysis)

### Suggestions
(none)

---
