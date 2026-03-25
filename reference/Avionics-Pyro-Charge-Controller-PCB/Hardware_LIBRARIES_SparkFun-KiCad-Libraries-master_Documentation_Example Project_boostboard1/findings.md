# Findings: Avionics-Pyro-Charge-Controller-PCB / Hardware_LIBRARIES_SparkFun-KiCad-Libraries-master_Documentation_Example Project_boostboard1

## ?: STM32L562VE MCU sub-sheet with crystal, reset, I2C pullups, decoupling, and status LEDs -- mostly correct analysis with false I2C bus entries and false USB ESD claim

- **Status**: new
- **Analyzer**: schematic
- **Source**: Hardware_COMPONENT_SHEETS_MCU_L562VE.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- STM32L562VET6Q (U2) correctly identified as IC with LQFP-100 footprint
- 35 total components correctly counted (1 IC, 1 crystal, 1 jumper, 15 capacitors, 5 LEDs, 11 resistors, 1 switch)
- Crystal Y1 correctly identified as 32MHz with two 30pF load caps (C6, C7) and effective load 18pF
- Crystal load cap calculation correct: CL_eff = (30pF * 30pF)/(30pF + 30pF) + 3pF stray = 18pF
- I2C1 bus correctly detected with R22 (4.7k) pullup on SCL and R23 (4.7k) pullup on SDA to +3.3V
- I2C2 bus correctly detected with R24 (4.7k) pullup on SCL and R25 (4.7k) pullup on SDA to +3.3V
- Reset circuit correctly detected: R33 (4.7k) pullup, C8 (100nF) filter cap, SW1 push button
- RC filter on NRST correctly identified: R33 4.7k + C8 100nF = 338.63 Hz low-pass
- Decoupling analysis correctly finds 12 caps on +3.3V rail (9x 100nF + 3x 1uF = 3.9uF total)
- SPI3 bus correctly detected with SCK, MISO, MOSI signals in full-duplex mode
- USB differential pair correctly identified (USB_D+ / USB_D-)
- Power rails correctly identified as +3.3V and GND only
- 47 no-connect markers correctly counted
- 5 LEDs correctly identified (D1-D5) with correct colors: D1,D3,D5=Red, D2,D4=Green
- All hierarchical labels correctly extracted (Fire_A-D, Sense_A-D, ABORT_1-2, Buzzer, SPI3, I2C1/2, USB, SWD, NRST)
- SWDIO and SWCLK nets correctly classified as debug and clock respectively
- Single-pin nets correctly reported for inter-sheet signals (Fire_A-D, Sense_A-D, Buzzer, ABORT_1/2, etc.) -- these are hierarchical label connections to other sheets
- Multi-driver warning correctly identifies V15SMPS_1 and V15SMPS_2 pins both driving +3.3V (this is the internal SMPS output of the STM32L5)

### Incorrect
- I2C2_EN falsely detected as I2C bus signal (line 'SCL'). I2C2_EN is an enable/control signal for the I2C2 bus power gating, not an I2C clock line. It has no pullup, which is correct for an enable signal but makes no sense for SCL.
  (design_analysis.bus_analysis.i2c)
- I2C1_EN falsely detected as I2C bus signal (line 'SCL'). I2C1_EN is an enable/control signal for the I2C1 bus, not an I2C clock line. Same false pattern as I2C2_EN.
  (design_analysis.bus_analysis.i2c)
- USB differential pair has_esd incorrectly reported as true with esd_protection listing U2 (the MCU itself). U2 is the MCU, not an ESD protection device. There is no dedicated USB ESD protection component on this sheet.
  (design_analysis.differential_pairs)
- ERC no_driver warning for NRST net is a false positive. NRST is driven through R33 (pullup to +3.3V) which provides a valid high-level driver. The passive pull-up network is the intended driver for this reset line.
  (design_analysis.erc_warnings)

### Missed
- 5 LED indicator circuits (D1-D5 with 820 ohm series resistors R17-R21) not detected as LED indicator patterns. Each LED is driven from an MCU GPIO pin through a current-limiting resistor to GND. At 3.3V with ~2V LED drop, current is approximately (3.3-2)/820 = 1.6mA per LED.
  (signal_analysis)
- PVD_IN label (Power Voltage Dropout monitoring) not recognized in design observations. This is a specific STM32 feature for brownout detection, connected to a dedicated pin via decoupling capacitor C17.
  (signal_analysis.design_observations)
- Debug jumper JP1 (3-pin jumper connecting +3.3V, common, and GND) not analyzed as a debug/configuration feature. This jumper selects BOOT0 mode or similar debug configuration for the STM32, with R32 (4.7k) in the circuit.
  (signal_analysis.design_observations)
- Duplicate I2C2_SCL hierarchical label (at two locations: 195.58,116.84 and 123.19,109.22) not flagged as a noteworthy connectivity pattern. Similarly I2C2_SDA appears at two locations (123.19,111.76 and 195.58,124.46) and I2C1_SCL/SDA are at both the MCU pins and the pullup resistor section.
  (labels)

### Suggestions
- I2C bus detection should filter out nets containing '_EN' suffix to avoid misclassifying enable signals as bus lines
- USB ESD detection should not list the main IC (MCU) as an ESD protection device -- only dedicated TVS/ESD suppressor components should qualify
- Consider adding LED indicator circuit detection: LED + series resistor from GPIO to GND/VCC is a very common pattern
- The ERC no_driver warning for NRST could be suppressed when a pull-up resistor to a power rail is present, as this is the standard reset circuit topology for STM32
- BOM grouping may use inconsistent LCSC codes when components with same value/footprint have different LCSC numbers (C23 has LCSC C14663 in schematic but BOM shows C15849 from the first match C9)

---
