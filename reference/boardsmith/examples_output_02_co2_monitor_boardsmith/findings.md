# Findings: boardsmith / examples_output_02_co2_monitor_boardsmith

## ?: RP2040 CO2 monitor with I2C sensors (SCD41, BME680, SSD1306), SPI flash (W25Q16), USB-C, and AMS1117 LDO. Analyzer correctly identifies major ICs, power regulator, memory interface, I2C bus observations, and crystal circuit, but misses I2C pullup detection issue, SPI bus protocol, USB interface, SWD debug, and has false decoupling warnings.

- **Status**: new
- **Analyzer**: schematic
- **Source**: examples_output_02_co2_monitor_schematic.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- AMS1117-3.3 correctly identified as LDO regulator with +5V input and +3V3 output, estimated_vout=3.3
- W25Q16JVSSIQ correctly identified as memory interface connected to RP2040 with 4 shared signal nets (MOSI, MISO, SCLK, CS)
- Crystal Y1 HC49-12MHZ detected in crystal_circuits
- I2C bus detected on SDA net with 4 devices: U1 (RP2040), U2 (SCD41), U3 (SSD1306), U4 (BME680)
- I2C bus detected on SCL net with same 4 devices
- Total component count of 37 is correct (6 ICs + 2 connectors + 1 MOSFET + 12 resistors + 15 capacitors + 1 crystal)
- Power rails correctly identified as +3V3, +5V, GND
- BSS138 correctly classified as N-channel MOSFET
- 55 no_connect markers correctly counted
- BOM correctly identifies 19 unique parts

### Incorrect
- I2C bus observations report has_pullup=false, but R1 (2.2k) is on SDA net and R2 (2.2k) is on SCL net. While both pins of each resistor are on the same net (a boardsmith generator artifact), the resistors are present on the bus and should at minimum be noted. The real issue is that this schematic has R1 and R2 with both pins on SDA/SCL respectively (not acting as pullups to VCC), so has_pullup=false is technically correct for the actual netlist, but the design_observation could note these resistors are present but non-functional.
  (signal_analysis.design_observations)
- Crystal circuit reports frequency=null despite the value being HC49-12MHZ (12 MHz is parseable from the part name). Also reports load_caps=[] but C12 and C13 (GRM1555C1H120GA01D, 12pF) are connected to NET_XIN and NET_XOUT which connect to Y1's pins -- these are classic crystal load capacitors.
  (signal_analysis.crystal_circuits)
- All 6 ICs report decoupling warnings with rails_with_caps=[] (empty), but the +3V3 rail has 11 capacitors (C1-C5 100nF, C6-C9 10uF, C10 100nF, C14) and +5V has implicit input caps. The decoupling analyzer fails to associate caps to ICs because caps connect to power rails not directly to IC pins, but the capacitors clearly exist on these rails.
  (signal_analysis.design_observations)
- Regulator U6 (AMS1117-3.3) observation reports missing input and output caps, but the +5V and +3V3 rails have multiple capacitors connected. C6-C9 (10uF, 0603) are on +3V3, and the USB connector provides +5V with input decoupling.
  (signal_analysis.design_observations)
- Q1 BSS138 transistor circuit shows all nets as unnamed (__unnamed_42/43/44) with drain_is_power=false, source_is_ground=false, load_type=other. The BSS138 has all 3 pins on single-pin nets (unconnected), so it is effectively floating/unconnected in this schematic -- this should ideally be flagged as a connectivity issue rather than analyzed as a functional circuit.
  (signal_analysis.transistor_circuits)

### Missed
- SPI bus between U1 (RP2040) and U5 (W25Q16JVSSIQ) not detected as a bus protocol. Four signals (MOSI, MISO, SCLK, CS) connect the two chips via named nets. While memory_interfaces detects U5, a dedicated SPI bus detection would be more informative.
  (signal_analysis)
- USB interface not detected. J1 (USB-C-CONN) has VBUS on +5V and GND but D+, D-, CC1, CC2 are all on single-pin unnamed nets -- not connected to U1's USB_DM/USB_DP pins. This is a major connectivity gap (USB data lines unconnected) that should be flagged.
  (connectivity_issues)
- SWD debug interface not detected. J2 (CONN-SWD-2x5) has SWDIO, SWCLK, NRST, SWO pins all on single-pin unnamed nets, not connected to U1's SWCLK/SWDIO pins. This is another major connectivity gap.
  (connectivity_issues)
- Multiple significant unconnected pins not flagged: U1.USB_DM, U1.USB_DP (USB data), U1.SWCLK, U1.SWDIO (debug), U1.VREG_VOUT (internal regulator output), J1.D+/D-/CC1/CC2 (USB data/config), J2.SWDIO/SWCLK/NRST/SWO (debug connector). All are single-pin nets suggesting incomplete wiring.
  (connectivity_issues)
- Crystal load capacitors C12 and C13 (GRM1555C1H120GA01D, 12pF) not associated with Y1 crystal circuit. They connect via NET_XIN and NET_XOUT to Y1's pins with other ends to GND -- a textbook crystal oscillator load cap topology.
  (signal_analysis.crystal_circuits)
- R5 (10k to +3V3) and R6 (10k to +5V) form a level shifter/signal conditioning network via LS_USB_C_CONN_SIG net, but neither a voltage divider nor any other signal conditioning is detected for this pair.
  (signal_analysis.voltage_dividers)

### Suggestions
- The boardsmith-generated schematic has several connectivity gaps (USB data, SWD, Q1 MOSFET all floating) -- the single_pin_nets detector should flag these as potential issues rather than silently ignoring them.
- Crystal frequency parsing should extract '12MHZ' from HC49-12MHZ part values using regex patterns like /([0-9.]+)\s*[Mm][Hh][Zz]/.
- Crystal load cap detection should trace nets from XIN/XOUT pins through named nets (NET_XIN, NET_XOUT) to find capacitors with one end on the crystal net and the other on GND.
- Decoupling analysis should consider that in many designs, caps connect to power rails (not directly to IC pins) and are shared across multiple ICs on the same rail. A rail-level cap count would be more useful.
- The I2C pullup detection is correct for this schematic (R1/R2 have both pins on the same net so they are not pullups), but it could note the presence of resistors on I2C lines even if they are not functional pullups.

---
