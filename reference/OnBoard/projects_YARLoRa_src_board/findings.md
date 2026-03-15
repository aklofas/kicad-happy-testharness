# Findings: OnBoard / projects_YARLoRa_src_board

## FND-00000107: RP2040-based LoRa radio with RFM95W module, BLE5201 Bluetooth, W25Q128JVS flash, NCP1117 LDO, and 12MHz crystal. SPI to RFM95W detected but QSPI to flash and RF interface missed.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/YARLoRa/src/board.kicad_sch
- **Created**: 2026-03-14

### Correct
- NCP1117DT33G correctly identified as LDO regulator
- SPI bus between RP2040 (U1) and RFM95W (U4) correctly detected with MISO/MOSI/SCK signals
- Crystal Y1 (ABM8G-12.000MHZ) correctly detected with two 15pF load caps and effective CL calculated
- All 5 ICs correctly identified: RP2040, RFM95W-915S2, BLE5201, W25Q128JVS, NCP1117DT33G
- 4 power rails (+1V1, +3V3, GND, VBUS) correctly detected
- 16 capacitors and 6 resistors quantities match schematic complexity

### Incorrect
(none)

### Missed
- W25Q128JVS flash (U2) connected to RP2040 QSPI bus (QSPI_SD0/SD1/SCLK/SS) not detected as a second SPI/QSPI bus
  (design_analysis.bus_analysis)
- RFM95W-915S2 is a LoRa radio module but no RF chain or RF-related observation is generated
  (signal_analysis.rf_chains)
- BLE5201 Bluetooth module not noted as a wireless interface in design observations
  (signal_analysis.design_observations)

### Suggestions
- QSPI bus detection should recognize RP2040 QSPI pins (QSPI_SD0/SD1/SCLK/SS) connected to flash as a bus interface
- RF module detection should recognize RFM95W as a LoRa radio module and note the RF chain even without explicit antenna matching components on the schematic
- BLE modules could be flagged as wireless interfaces in design observations

---
