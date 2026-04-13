# Findings: solar-cooker-UHasselt-mirror/kicad-testing-station / testing-station

## FND-00002268: SPI bus analysis creates 6 separate bus entries instead of 2 coherent buses; 74HC4050D (IC3) level-shifting buffer not identified as a level shifter; I2C bus correctly detected on DS3231 RTC with 1...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-testing-station_testing-station.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies two I2C lines (SDA and SCL), each with a single device (IC2=DS3231) and a 10k pull-up resistor to +3.3V (R24 on SDA, R23 on SCL). The BME680 (IC1) is correctly placed on the SPI bus because its CSB pin is driven (SPI mode), not left high (I2C mode).
- The design uses 5 sub-sheets (BME680.kicad_sch, DS3231.kicad_sch, MAX31865.kicad_sch x3, microSD.kicad_sch) plus the top sheet. The analyzer correctly processes all sheets, combining 89 total components from the full hierarchy. The three MAX31865 instances (U2, U4, U6) are correctly captured as separate devices.

### Incorrect
- The design has two SPI buses: a 3.3V bus (BME680=IC1, three MAX31865=U2/U4/U6 on 3V signals) and a 5V bus (74HC4050=IC3 buffer side). The analyzer creates 6 bus_id entries: '5V', '3V', 'pin_U6', 'pin_IC1', 'pin_U2', 'pin_U4'. The per-device bus IDs are redundant, as they all share the same SDO net, and the four separate per-pin entries should be collapsed into a single 3.3V SPI bus with 4 devices and 1 chip-select-per-device pattern.
  (design_analysis)

### Missed
- The 74HC4050D (IC3) is used as a 5V-to-3.3V SPI level buffer. Its VCC is +3.3V, but its inputs (1A=SCLK_5V, 2A=SDI_5V, 3A=CS) are driven from the 5V SPI domain, making it a voltage-domain translator between the microcontroller's 5V SPI interface and the 3.3V sensor SPI signals. The signal_analysis.isolation_barriers list is empty, and the cross_domain_signals entry for SDO marks needs_level_shifter=false despite IC3 being explicitly present for this purpose. There is no level-shifter/buffer detector in the signal path.
  (signal_analysis)
- The design contains 10 x 1N4148 diodes (D3-D11, D13) which are classic signal protection/clamping diodes. The signal_analysis.protection_devices list is empty despite these components being present. The diodes are counted correctly in statistics (diode:10) but the analyzer does not classify them as protection elements or identify their circuit function.
  (signal_analysis)

### Suggestions
(none)

---
