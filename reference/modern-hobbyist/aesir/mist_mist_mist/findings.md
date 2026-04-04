# Findings: aesir / mist_mist_mist

## ?: Custom mechanical keyboard (7x18 matrix, 103 keys) with STM32G474, 103 SK6812 addressable LEDs, ILI9341 LCD display, USB-C. Component counts and most signal detections are accurate; key issues are duplicated SPI bus, wrong IC function classification for regulator, and inconsistent ESD reporting for D-.

- **Status**: new
- **Analyzer**: schematic
- **Source**: mist_mist_mist.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Total component count of 456 exactly matches the schematic (37 main + 213 matrix + 206 rgb sheet)
- Key matrix correctly detected as 7 rows x 18 columns with 103 switches and 103 diodes
- Key matrix column count of 18 correctly identified (col0-col17)
- 103 estimated keys in matrix correctly counted
- Addressable LED chain of 103 SK6812MINI-E LEDs correctly detected as single-wire WS2812 protocol
- XC6206 LDO correctly identified as power regulator with +5V input and +3V3 output
- PRTR5V0U2X correctly identified as ESD protection IC protecting D+ and D- nets
- 500mA polyfuse correctly identified as protection device on VBUS-to-+5V path
- Two RC low-pass filters on BOOT0 correctly detected (R7/120ohm charge path at 6.63kHz, R8/68k discharge path at 11.7Hz)
- PNP transistor Q3 (MMUN2133LT1G BRT) correctly detected with base driven by STM32 via BOOT0_CHRG net
- SPI bus correctly identified between STM32 (U5) and LCD display (U4) with MOSI/MISO/SCK signals
- USB D+/D- differential pair correctly detected with ESD protection
- Cross-domain signal RGB3.3 correctly flagged as needing level shifting between 3.3V and 5V domains
- All 4 power rails correctly identified: +3V3, +5V, GND, VBUS
- 106 decoupling caps on +5V rail correct (103 per-LED caps + 3 power regulation caps)
- 3 hierarchical sheets correctly enumerated (main, matrix, rgb)
- 16 no-connect markers correctly counted (15 main + 1 rgb)
- CC1 and CC2 5.1k pulldown resistors correctly identified for USB-C UFP mode
- STM32G474RETx correctly classified as microcontroller with 64 pins, 0 unconnected

### Incorrect
- U3 (XC6206 linear regulator by Torex) misclassified as 'FPGA (Xilinx)' due to XC prefix matching. Should be 'voltage regulator' or 'LDO'
  (ic_pin_analysis)
- SPI bus detected twice (once as 'LCD' from net prefix, once as 'pin_U4' from display pin names) — these are the same bus with identical MOSI/MISO/SCK nets and devices
  (design_analysis.bus_analysis.spi)
- D- net reported as has_esd_protection=false in design_observations, but PRTR5V0U2X (U2) protects both D+ and D- (correctly noted in protection_devices.protected_nets)
  (signal_analysis.design_observations)

### Missed
- STM32 NRST reset circuit not detected as a design observation (NRST has RESET1 push button, R9/68k, C130/100nF, plus D41 diode), despite U4's LCD_RST being detected
  (signal_analysis.design_observations)
- U6 (SN74AHCT1G125DBVR) functions as a 3.3V-to-5V level shifter for the RGB LED chain data line, but is classified only as 'logic IC'. The schematic has a text annotation 'Level Shifter' confirming this purpose
  (ic_pin_analysis)
- SWD debug interface on J2 (GND, SWCLK, SWD, NRST, +3V3) not detected as a debug/programming port
  (design_analysis.bus_analysis)
- LED chain current (6180 mA estimated) not factored into +5V power budget (shows only 30 mA from ICs). With 500mA fuse, full LED brightness is physically impossible
  (power_budget)

### Suggestions
- IC function classifier should not match 'XC6206' as Xilinx FPGA — check lib_id or description for 'Regulator' keyword before falling back to value-based prefix matching
- SPI bus deduplication: when two detected SPI buses share identical nets and devices, merge them into one entry
- Reset pin detection should also check the MCU's own NRST/reset pin, not just peripheral IC reset pins
- Level shifter detection could use the SN74AHCT1G125 part number or the cross_domain_signals analysis to identify buffer ICs used for level translation
- Power budget should cross-reference addressable_led_chains estimated_current_mA and add it to the relevant rail's load estimate

---
