# Findings: OnBoard / projects_TremorWatch_src_TremorWatch

## FND-00000103: Accelerometer wearable with MPU-6050, XIAO ESP32C3, microSD card, and resistor pack pull-ups. I2C detected but SPI for SD card missed.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/TremorWatch/src/TremorWatch.kicad_sch
- **Created**: 2026-03-14

### Correct
- MPU-6050 correctly identified as motion sensor IC
- XIAO-ESP32C3 module correctly identified as IC
- I2C bus between MPU-6050 and ESP32C3 correctly detected on SDA/SCL nets
- R_Pack04 resistor networks (4.7k) correctly classified as resistor_network type
- Battery correctly classified, +3V3 and GND power rails detected

### Incorrect
- I2C pull-ups reported as has_pull_up: false, but RN1/RN2 resistor packs have pins connected to +3V3 rail. The 4.7k pull-ups are present but not connected to the I2C SDA/SCL nets directly - they pull up the SD card signals instead.
  (design_analysis.bus_analysis)

### Missed
- MicroSD card (X1, Adafruit SDIO microSD symbol) uses SPI mode with CS, SCLK, DI (MOSI), DO (MISO) through RN1 series resistors to ESP32C3 but no SPI bus detected
  (design_analysis.bus_analysis)
- RN1 provides series protection resistors on SD card SPI lines (CS, DI, SCLK via pins 7,6,5) with pull-ups to +3V3 (pins 1-4). This level-shifting/protection topology is not noted.
  (signal_analysis.design_observations)

### Suggestions
- SPI bus detection should recognize microSD card SPI signals even when routed through resistor networks
- The microSD connector typed as connector is reasonable but could note SD card interface as a design observation

---
