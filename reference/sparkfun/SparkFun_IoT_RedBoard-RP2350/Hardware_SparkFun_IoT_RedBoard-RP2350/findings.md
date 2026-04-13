# Findings: sparkfun/SparkFun_IoT_RedBoard-RP2350 / Hardware_SparkFun_IoT_RedBoard-RP2350

## FND-00000204: RP2350B-based development board with USB-C, LiPo charging, WiFi/BLE (RM2 module), PSRAM, flash, microSD, and HSTX display connector. Analyzer does well overall but misclassifies the LM66200 ideal diode OR controller as an LDO regulator.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_IoT_RedBoard-RP2350.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- AP63357DV-7 (U5) correctly identified as switching regulator with L3 inductor, bootstrap cap, and feedback divider R19=220k/R20=41.2k producing 3.804V on VDD rail
- RT9080-3.3 (U10, U11) correctly identified as fixed 3.3V LDO regulators via value suffix parsing
- Y1 12MHz crystal with C9=15pF and C7=15pF load caps correctly detected, effective load 10.5pF calculated
- R28=41.2k/R29=10k voltage divider from VRAW to VIN_MEAS correctly detected as ADC measurement input to U1 pin 57 (RP2350B)
- D2 DT1042-04SO correctly identified as USB ESD protection on USBC+/USBC- lines
- F1 and F2 correctly identified as fuses protecting VRAW and VUSB rails
- WS2812B (D4) addressable LED chain correctly detected with single-wire protocol
- R35=10k/C36=0.1uF low-pass RC filter on ~{USER_BTN} at 159Hz correctly detected as button debounce
- R7=200/C3=4.7uF and R8=33/C5=4.7uF RC filters on 3.3V correctly detected as power filtering for RP2350B analog domains
- Q1 RE1C001ZPTL correctly identified as P-channel MOSFET with gate control from BATT_PWR net and R21=10k gate resistor
- MCP73831 (U9) LiPo charger and MAX17048 (U8) fuel gauge correctly classified as ICs
- 8 decoupling rails correctly analyzed including 3.3V (13 caps), VDD (2 caps, 44uF), 1.1V (4 caps)
- R24=10k/R25=1M voltage divider feeding U10 EN pin (PERI_POW) correctly detected as GPIO-controlled enable

### Incorrect
- U6 LM66200 classified as LDO regulator with topology 'LDO' -- it is actually an ideal diode OR controller that selects between VUSB and VDD power sources. It has no regulation function.
  (signal_analysis.power_regulators)
- R10=1k/C9=15pF detected as 10.6MHz low-pass RC filter, but these are actually the crystal Y1 load circuit (R10 is a feedback resistor in the crystal oscillator, not a standalone filter)
  (signal_analysis.rc_filters)

### Missed
- MCP73831 (U9) LiPo battery charger not detected as a charger IC or BMS component -- it manages single-cell LiPo charging from VUSB with R23=4.7k programming resistor
  (signal_analysis.bms_systems)
- MAX17048 (U8) fuel gauge IC with I2C interface on SDA/SCL not detected as part of battery management system
  (signal_analysis.bms_systems)
- I2C bus on SDA/SCL nets connecting U1 (RP2350B) and U8 (MAX17048) with I2C pull-up jumper JP3 not detected
  (signal_analysis.bus_interfaces)
- QSPI flash (U3 W25Q128JVPIM) and QSPI PSRAM (U4 APS6404L-3SQR-ZR) memory interfaces not detected
  (signal_analysis.memory_interfaces)
- USB data pairs on USB_D+/USB_D- and USBC+/USBC- not detected as USB bus interfaces despite ESD protection and series resistors R3=27/R4=27
  (signal_analysis.bus_interfaces)

### Suggestions
- Add LM66200 to an ideal-diode/OR-controller recognition list so it is not misclassified as LDO
- Filter out RC pairs that are part of crystal oscillator circuits from the rc_filters detector
- Add MCP73831 to a battery charger IC list for bms_systems detection
- Detect QSPI interfaces when 4+ data lines plus CLK/CS connect to flash/PSRAM ICs

---
