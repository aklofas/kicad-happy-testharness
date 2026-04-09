# Findings: Jana-Marie/transpOtterNG / kicad_TranspOtterNG

## FND-00002559: ESP8266+RFM69HCW transponder board: good power/SPI/filter detection, but misses RF chain, DC-DC regulator, Zener protection, WS2812, and misclassifies antenna/LED driver

- **Status**: new
- **Analyzer**: schematic
- **Source**: kicad_TranspOtterNG.sch.json
- **Created**: 2026-03-23

### Correct
- AMS1117 (U1) correctly identified as LDO regulator with +5V input and VCC output
- R27/R28 voltage divider (10k/10k, ratio 0.5) for LCD contrast on VO net correctly detected
- SPI bus detected with SCK/MOSI/MISO connecting ESP-12E (U4) and RFM69HCW (U3)
- I2C SCL line (TX0_SCL) with R2 3k3 pull-up to VCC correctly detected
- RC low-pass filters on UART/I2C inputs (R4-R7 with C5-C8, ~15.9 kHz cutoff) correctly detected
- Q2 PMOS high-side switch correctly detected with gate resistors R17/R15 (100k)
- Q1 NMOS gate driver with R15/R16 gate resistors correctly identified
- 5 DNP parts correctly identified (R8, R9, R21, R22, R23)
- 63 total components correctly counted
- Decoupling analysis identifies +5V rail with C2, C12, C10 (20.2 uF total)
- Power rails +15V, +5V, GND, VCC all correctly identified
- PCF8574 (U5) I2C I/O expander correctly identified with address resistors R18-R23 as neighbors

### Incorrect
- AE1 (Antenna component, Device:Antenna) classified as type 'ic' in BOM - should be 'antenna' or 'connector'
  (bom)
- Q1 NMOS falsely associated with LED D3/R1 as an led_driver. D3+R1 is a simple VCC-to-GND power indicator (VCC -> D3 -> R1 -> GND at schematic positions 6550,1000-1750), not driven by Q1 (at position 8500,1750). They are in separate schematic sections with no electrical connection.
  (signal_analysis.transistor_circuits)
- I2C SDA line (RX0_SDA) with R3 3k3 pull-up to VCC not detected in bus_analysis.i2c. Only TX0_SCL pull-up (R2) is found; the structurally identical R3 pull-up on SDA is missed.
  (design_analysis.bus_analysis.i2c)

### Missed
- RFM69HCW (U3) not detected as an RF transceiver in rf_chains despite being a 433/868/915 MHz radio module with SPI interface and antenna output
  (signal_analysis.rf_chains)
- Antenna matching circuit (C14 series cap + AE1 antenna on ANT net) not detected in rf_matching
  (signal_analysis.rf_matching)
- URB4805YMD-6WR3 (U2) is a 48V-to-5V isolated DC-DC converter not detected in power_regulators. It converts +15V input (from XT30 via PMOS switch) to +5V rail. Pins are named VIN/VOUT/GND.
  (signal_analysis.power_regulators)
- D1 (12V Zener diode, D_SOD-323) not detected as a voltage protection/clamping device on the PMOS gate of the power input switch
  (signal_analysis.protection_devices)
- WS2812 addressable LED output not detected. ESP GPIO2 drives WS2812 label to connector J3 for external LED strip.
  (signal_analysis.addressable_led_chains)
- ESP-12E (U4) power domain shows __unnamed_26 instead of VCC - the ESP's VCC pin connection is not properly resolved to the VCC power rail
  (design_analysis.power_domains)

### Suggestions
- RF module detection should recognize RFM69HCW (lib_id RF_AM_FM:RFM69HCW) as an RF transceiver and flag the antenna circuit (AE1 + C14 matching cap on ANT net)
- DC-DC converters from custom libraries should be detectable via pin names (VIN/VOUT/GND) even when not in a known regulator library
- Antenna components (Device:Antenna) should be classified as 'antenna' type, not 'ic'
- The LED driver false association with Q1 suggests the spatial/connectivity heuristic is too loose - D3/R1 are in a separate schematic section with direct VCC/GND connections
- I2C SDA pull-up detection should match the same pattern as SCL pull-up detection - R3 on RX0_SDA is structurally identical to R2 on TX0_SCL
- WS2812 net name pattern should trigger addressable LED chain detection, especially when connected to a known GPIO-capable MCU

---
