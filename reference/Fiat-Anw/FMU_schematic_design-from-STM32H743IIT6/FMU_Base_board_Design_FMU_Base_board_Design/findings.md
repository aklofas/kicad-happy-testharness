# Findings: Fiat-Anw/FMU_schematic_design-from-STM32H743IIT6 / FMU_Base_board_Design_FMU_Base_board_Design

## FND-00000306: PX4-style FMU flight controller based on STM32H743IIT6 with 3-source power management (LTC4417+SIS903DN MOSFETs), 3x MIC5330 dual LDOs, 2x CAN (TJA1051T), 4x TXS0108 level shifters, IMU (ICM-20649), barometer (BMP388), magnetometer (BMM150), FRAM (FM25V05-G), microSD with EMIF06 filter, USB-C with ESD protection. Analyzer correctly identifies most subsystems but misses voltage dividers, only finds 1 of 2 CAN buses, and has incomplete regulator output mapping for dual-output LDOs.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: FMU_Base_board_Design_FMU_Base_board_Design.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- STM32H743IITx MCU correctly identified with internal regulator topology
- 3 I2C buses (I2C1-I2C3) correctly detected with pull-up resistors (1.5k to MCU_3V3)
- SPI bus for IMU (ICM-20649) on SPI1 correctly detected with SCK/MOSI/MISO
- SPI bus for FRAM (FM25V05-G) on SPI5 correctly detected
- SDMMC2 4-bit SD card bus correctly detected with EMIF06 filter IC
- USBLC6-2 ESD protection on USB data lines correctly detected
- USB Type-C connector (USB4105-GF-A) CC pull-down check passes
- RC filter on NRST pin (R7=10k, C8=100nF, fc=159 Hz) correctly detected
- Reset pin analysis identifies pullup, filter cap, switch, debug connector
- 153 components across 26 hierarchical sheets correctly counted
- FM25V05-G FRAM correctly detected in memory_interfaces with SPI to STM32
- USB differential pairs detected for both internal and external USB paths
- FMU_PWM bus signal group correctly identified (PWM1..PWM8)
- 37 UART nets detected covering USART1-3, UART4-5, UART7, USART8
- 9 decoupling rail analyses covering all major power rails

### Incorrect
- I2C1_BMP388_DRDY net incorrectly classified as I2C SCL -- it is a data-ready interrupt from BMP388 to STM32, not an I2C clock
  (design_analysis.bus_analysis.i2c)
- Only 1 CAN bus detected (U13/CAN2) but 2 exist -- U12/CAN1 with TJA1051T, CAN1_H/CAN1_L nets, and 120 ohm termination R27 completely missed
  (design_analysis.bus_analysis.can)
- SIS903DN-T1-GE3 (U18/U19/U20) classified as 'ic' but are dual P-channel MOSFETs for power switching, lib_id contains 'MOSFET'
  (statistics.component_types)
- U14 (MIC5330) output_rail is __unnamed_9 (BYP pin) instead of MCU_3V3 (VOUT1 pin 8, the primary output)
  (signal_analysis.power_regulators)
- U16 (MIC5330) output_rail is __unnamed_27 (VOUT2) instead of VDD_3V3_PWM (VOUT1 pin 8)
  (signal_analysis.power_regulators)
- U15 (MIC5330) only reports SD_3V3 output but misses second output SENSOR_3V3 -- dual-output LDO
  (signal_analysis.power_regulators)
- SPI bus for BMP388 (U8) and BMM150 (U10) misidentifies GND net as MOSI signal
  (design_analysis.bus_analysis.spi)

### Missed
- 6 voltage dividers for LTC4417 UV/OV thresholds: R21(453k)/R22(56k), R23(105k)/R22, R34(453k)/R35(56k), R36(105k)/R35, R37(453k)/R38(56k), R39(105k)/R38
  (signal_analysis.voltage_dividers)
- LTC4417CUF power path priority controller not classified as power management IC -- selects from 3 input sources to VDD_5V_IN
  (signal_analysis.power_regulators)
- CAN bus termination resistors not reported: R27=120 ohm on CAN1, R28=120 ohm on CAN2
  (design_analysis.bus_analysis.can)
- 4x TXS0108ERGYR level shifter/buffer ICs not detected as level translation despite lib_id 'Level-Shifting:TXS0108ERGYR'
  (signal_analysis.isolation_barriers)
- EMIF06-MSD02N16 (U11) SD card EMI filter + ESD protection not flagged in protection_devices
  (signal_analysis.protection_devices)
- Power path switch topology (LTC4417 + 3x SIS903DN P-FETs) not recognized as prioritized power selection circuit
  (signal_analysis.transistor_circuits)

### Suggestions
- Voltage divider detector should examine resistor pairs connected to IC threshold/feedback pins
- Dual-output LDO detection should report both VOUT1 and VOUT2 rails, prioritizing named rails
- CAN bus detector should find all TJA1051T transceivers, not just one
- I2C net classification should not flag DRDY/interrupt nets that happen to contain 'I2C' in the name
- Components with 'MOSFET' in lib_id should be classified as transistor not IC
- Level shifter ICs with 'Level-Shifting' in lib_id should be reported in an appropriate category
- Power path controllers like LTC4417 should be distinctly classified from LDO regulators

---

## FND-00002551: STM32H743 flight controller: good IC/SPI/I2C/UART detection, but misses 6 voltage dividers (UV/OV monitoring), misclassifies I2C1_BMP388_DRDY interrupt as I2C SCL, CAN termination not detected, USBLC6-2 called varistor instead of ESD protection

- **Status**: new
- **Analyzer**: schematic
- **Source**: FMU_Base_board_Design_FMU_Base_board_Design.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 153 total components correctly counted
- Multiple power regulators detected including LDOs and buck converters
- SPI buses correctly detected with MOSI/MISO/SCK signals
- I2C buses detected with pull-ups
- USBLC6-2 detected as protection device
- RC filters on UART/sensor inputs correctly detected

### Incorrect
- I2C1_BMP388_DRDY net (data-ready interrupt from BMP388) misclassified as I2C SCL because net name contains 'I2C1'
  (design_analysis.bus_analysis.i2c)
- USBLC6-2 (USB_ESD_Protection library) classified as varistor instead of ESD protection IC
  (signal_analysis.protection_devices)

### Missed
- 6 voltage dividers for UV/OV monitoring (R21/R22, R23/R22, R34/R35, R36/R35, R37/R38, R39/R38 feeding UV1/OV1/UV2/OV2/UV3/OV3 pins) not detected
  (signal_analysis.voltage_dividers)
- CAN bus termination resistors (R27 120ohm CAN1_H-CAN1_L, R28 120ohm CAN2_H-CAN2_L) not detected
  (design_analysis.bus_analysis.can)
- EMIF06-MSD02N16 SD card EMI/ESD filter not detected as protection device
  (signal_analysis.protection_devices)

### Suggestions
- Net name heuristic for I2C should not classify _DRDY/_IRQ/_INT suffix nets as I2C even if they contain I2C in the name
- Voltage divider detection should find dividers feeding UV/OV monitoring pins of power management ICs
- CAN bus termination detection: 120ohm between CANH and CANL nets
- ESD protection ICs from USB_ESD_Protection library should be classified as esd_protection, not varistor

---
