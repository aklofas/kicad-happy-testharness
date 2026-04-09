# Findings: Wren6991/RISCBoy / board_riscboy_reva0_fpgaboy

## FND-00002591: RISCBoy Rev A0 (fpgaboy) is the earlier revision with iCE40-HX4K FPGA, GS74116 SRAM, NCP1532 dual switching regulator, BQ21040 charger, CP2102N USB-UART, and W25Q16 SPI flash. Analyzer produced good results on regulators and protection but missed memory interfaces and had many single-pin net false positives.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: board_riscboy_reva0_fpgaboy.sch.json

### Correct
- NCP1532 (U5) correctly detected as switching regulator with input_rail=PWR_EN
- Voltage divider R17/R18 (450k/100k) at ratio 0.182 correctly detected as feedback divider for NCP1532 SW2 output (3.3V rail)
- Voltage divider R19/R20 (100k/100k) at ratio 0.5 correctly detected as feedback divider for NCP1532 SW1 output (1.2V rail)
- Audio voltage divider R15/R14 (680/220) at ratio 0.244 on AUDIO_PWM net feeding P4 headphone jack is correct
- ESD protection D3, D4 (DF2B7AFS) on USB_DP and USB_DM correctly detected, plus D5 on +5V rail
- RC-networks R8/C5 and R7/C3 at ~16 kHz on +1V2 rail correctly detected as PLL supply filters
- DSC60XX (U2) correctly identified as active oscillator
- USB data nets USB_DP/USB_DM correctly flagged with ESD protection present (D3/D4)
- Decoupling coverage across 4 rails (+BATT, +5V, +3V3, +1V2) correctly tallied

### Incorrect
- Single-pin nets reports 38 nets, but many are SRAM address/data bus signals (SRAM_A13, SRAM_~WE, etc.) which connect U1 (iCE40) to U3 (GS74116) across hierarchical sheets. These are legitimate multi-pin nets that appear single-pin due to cross-sheet connectivity parsing issues
  (signal_analysis.design_observations)
- NCP1532 regulator detected with input_rail=PWR_EN, but PWR_EN is actually the enable control signal, not the power input. The actual input is +BATT
  (signal_analysis.power_regulators)
- Decoupling observations repeatedly flag U8 (74LVC2G04) as missing caps on PWR_EN rail. PWR_EN is a logic signal, not a power rail, so decoupling is not expected
  (signal_analysis.design_observations)

### Missed
- BQ21040 (U4) is a LiPo battery charger IC not detected in bms_systems
  (signal_analysis.bms_systems)
- W25Q16 (U6) SPI flash connected to iCE40 FPGA (U1) not detected in memory_interfaces
  (signal_analysis.memory_interfaces)
- GS74116 (U3) 4Mbit SRAM connected to iCE40 FPGA (U1) via parallel address/data bus not detected in memory_interfaces
  (signal_analysis.memory_interfaces)
- CP2102N (U7) USB-UART bridge not classified or noted in design_observations
  (signal_analysis.design_observations)

### Suggestions
- Fix single-pin net detection to properly handle cross-sheet hierarchical connections in KiCad 5 legacy format
- NCP1532 pin mapping: distinguish VIN/PVIN power inputs from EN enable inputs
- Add BQ21040 to bms_systems/charger detection

---

## FND-00002532: RISCBoy is an iCE40 FPGA-based handheld game console with a dual-channel NCP1532 buck converter, BQ21040 battery charger, GS74116 SRAM, W25Q16 QSPI flash, CP2102N USB-UART bridge, ILI9341 LCD, and 74LVC2G04-based soft-latching power switch. The analyzer correctly identified most voltage dividers, RC filters, protection devices, transistor circuits, decoupling analysis, and SPI bus. However, it has significant issues: the NCP1532 regulator detection is incomplete (only one entry instead of two channels, wrong input_rail as PWR_EN instead of +BATT), the BQ21040 battery charger is entirely missed, the SRAM memory interface is not detected, the display interface is not detected, the crystal oscillator output net is wrong (+3V3 instead of CLK_OSC), the clock distribution consumers list includes ICs that only share the +3V3 power rail, the USB differential pair has_esd contradicts the esd_coverage_audit, and the LCD SPI interface is falsely detected as I2C.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: board_riscboy_reva0_fpgaboy.sch.json
- **Created**: 2026-04-09

### Correct
- Voltage divider R17 (450k) / R18 (100k) correctly identified as feedback for NCP1532 CH1 (+3V3 output), ratio 0.1818 is correct
- Voltage divider R19 (100k) / R20 (100k) correctly identified as feedback for NCP1532 CH2 (+1V2 output), ratio 0.5 is correct
- Voltage divider R15 (680) / R14 (220) correctly identified as audio output attenuator with parallel_count=2, connected to P4 speaker connector
- Voltage divider R12 (100k) / R21 (100k) correctly identified as reset divider for CP2102N U7 pin ~RST, ratio 0.5, from +5V to GND
- RC filter R23 (100k) / C31 (1u) at 1.59 Hz correctly identified as part of soft-latching power switch debounce circuit
- RC filter R24 (100k) / C32 (0.1u) at 15.92 Hz correctly identified as PWR_EN debounce filter
- RC filter R22 (10k) / C21+C19 parallel at 1.58 Hz correctly identified as USB controller VDD filter for CP2102N REGIN pin
- RC-network R8 (10) / C5 (1u) and R7 (10) / C3 (1u) correctly identified as FPGA 1V2 PLL power filters
- Protection devices D3/D4/D5 (DF2B7AFS TVS diodes) correctly identified protecting USB_DP, USB_DM, and +5V
- Q1 (BSS816NW) NMOS correctly identified as LED/backlight driver, gate driven by LCD_PWM with R1 10k pulldown, gate driver U1 FPGA
- LED D1 correctly identified as indicator LED with R6 (680 ohm) series resistor driven by U4
- SPI bus FLASH correctly identified with FLASH_SCK, FLASH_MOSI, FLASH_MISO connecting to U6 (W25Q16), full_duplex mode
- USB differential pair USB_DP/USB_DM correctly identified
- ESD coverage audit correctly identifies P3 USB connector as fully protected by D3/D4
- Decoupling analysis correctly identifies 4 rails (+BATT 2uF, +5V 12.1uF, +3V3 13.7uF, +1V2 11.4uF) with accurate cap counts
- Power domains correctly map all 8 ICs (U1-U8) to their respective power rails
- Component counts are accurate: 93 total components, 8 ICs, 32 capacitors, 26 resistors, 2 LEDs, 9 test points
- Power rails correctly identified: +1V2 (1.2V), +3V3 (3.3V), +5V (5.0V), +BATT, GND, GNDPWR, PWR_EN
- U5 NCP1532 correctly identified as switching regulator topology
- U2 (DSC60XX 12MHz MEMS oscillator) correctly identified as active oscillator

### Incorrect
- NCP1532 (U5) input_rail reported as 'PWR_EN' but the actual power input (VIN, pin 3) connects to +BATT. PWR_EN is the enable signal, not the power input rail
  (signal_analysis.power_regulators)
- Only one power_regulator entry for U5 NCP1532, but it is a dual-channel buck converter producing both +3V3 (CH1 via L1, R17/R18 feedback) and +1V2 (CH2 via L2, R19/R20 feedback)
  (signal_analysis.power_regulators)
- Crystal circuit U2 (DSC60XX) output_net is '+3V3' which is the power supply net, not the clock output. The actual output net is 'CLK_OSC'
  (signal_analysis.crystal_circuits)
- Clock distribution U2 output_net also incorrectly '+3V3' instead of 'CLK_OSC'. The consumers list [U3, U1, U6, U8] is wrong — CLK_OSC only connects to U1 FPGA
  (signal_analysis.clock_distribution)
- USB differential pair has_esd is false despite D3/D4 (DF2B7AFS) being correctly identified in protection_devices and esd_coverage_audit
  (signal_analysis.differential_pairs)
- Q1 transistor circuit has_flyback_diode is true with flyback_diode='D5', but D5 is a TVS on USB +5V, completely unrelated to Q1 backlight circuit
  (signal_analysis.transistor_circuits)
- Q1 LED driver led_ref is D2 (charge status LED) not the LCD backlight. Actual backlight load is R2-R5 parallel 220-ohm to P1 connector
  (signal_analysis.transistor_circuits)
- I2C bus detection for LCD_SCL is a false positive. The LCD uses SPI not I2C: LCD_SCL=clock, LCD_SDA=MOSI, LCD_SDO=MISO, LCD_CS=chip select, LCD_D~C~=data/command
  (signal_analysis.bus_analysis.i2c)
- UART detection shows empty devices lists for FPGA_UART_RX and FPGA_UART_TX. U7 (CP2102N) and U1 (FPGA) should be listed as endpoints
  (signal_analysis.bus_analysis.uart)
- Voltage divider R17/R18 mid_point connects to U5 pin 7 'SW2' but should connect to FB1 (pin 1). Pin mapping error
  (signal_analysis.voltage_dividers)
- Voltage divider R19/R20 mid_point connects to U5 pin 4 'SW1' but should connect to FB2 (pin 10). Same pin mapping confusion
  (signal_analysis.voltage_dividers)
- Design observation reports U5 and U8 rails_without_caps for 'PWR_EN', but PWR_EN is a logic enable signal, not a power rail needing decoupling
  (signal_analysis.design_observations)

### Missed
- BQ21040 (U4) battery charger completely missed. U4 is a linear Li-ion charger: +5V USB input, +BATT output, R9 (10k) timer, R10 (680) ISET charge current resistor (~147mA), D2/R11 charge status LED
  (signal_analysis.battery_chargers)
- SRAM memory interface completely missed. U3 (GS74116AGP) is a 16Mbit parallel SRAM with 18 address lines, 16 data lines, and control signals, all connected to U1 FPGA
  (signal_analysis.memory_interfaces)
- Display interface completely missed. P1 (ILI9341) is an 18-pin FFC connector for TFT LCD with SPI interface, backlight PWM control through Q1
  (signal_analysis.display_interfaces)
- Soft-latching power switch circuit not detected. U8 (74LVC2G04 dual inverter) forms a bistable latch with SW1 pushbutton, producing PWR_EN to enable U5 regulator
  (signal_analysis.power_path)
- Audio low-pass filter not detected. R15/R13 (680 ohm parallel) + R14 (220) + C30 (0.1u) form RC low-pass on AUDIO_PWM for analog audio output to P4
  (signal_analysis.audio_circuits)
- QSPI Flash quad-SPI capability not detected. U6 (W25Q16) has FLASH_IO2/IO3 via RN1 10k pull-ups indicating quad-SPI mode
  (signal_analysis.bus_analysis.spi)
- USB-to-UART bridge U7 (CP2102N) not detected as USB interface. Bridges USB D+/D- to FPGA UART with R25/R26 (220) series termination
  (signal_analysis.usb_interfaces)
- Reset circuit missed. U5 NCP1532 ~POR output drives FPGA_~RST with RN2 10k pull-ups on FPGA_CFG_DONE and FPGA_~RST
  (signal_analysis.reset_supervisors)
- Second LCD SPI bus not detected. LCD interface (LCD_CS, LCD_SCL, LCD_SDA, LCD_SDO) is separate SPI bus from FLASH SPI bus
  (signal_analysis.bus_analysis.spi)

### Suggestions
- NCP1532 dual-channel buck: create separate entries per channel with own output rail, feedback divider, and inductor
- Add BQ21040 and similar TI charger ICs to battery charger detection
- Detect parallel bus patterns (sequential numeric suffixes) for SRAM memory interfaces
- Detect ILI9341 and similar LCD controllers or FFC connectors with SPI-like signal groups
- LCD SPI should NOT be detected as I2C — DC pin and chip select are strong SPI indicators
- Crystal oscillator output_net returning VDD net instead of clock output — trace the output pin not the power pin
- differential_pairs.has_esd should cross-reference protection_devices to avoid contradicting esd_coverage_audit
- Soft-latching power switch pattern (dual inverter + pushbutton + RC debounce) is common and could be a new detector

---
