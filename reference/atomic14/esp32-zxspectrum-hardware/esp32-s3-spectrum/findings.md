# Findings: atomic14/esp32-zxspectrum-hardware / esp32-s3-spectrum

## FND-00000146: ZX Spectrum emulator with ESP32-S3: good USB and power detection, but touch pad keyboard matrix misclassified as relays, missing SD card and HDMI/display interface detection

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/esp32-zxspectrum-hardware/esp32-s3-spectrum.kicad_sch
- **Created**: 2026-03-14

### Correct
- NCP167BMX330TBG LDO identified for PWR to 3.3V regulation
- USB differential pairs (USB_D+/-, USB_D_IN+/-) detected with USBLC6-2P6 ESD protection
- SPI bus detected for TFT display (TFT_SCLK, TFT_MOSI)
- TPS2117DRLR power mux IC identified for switching between USB and battery power
- TP4057 battery charger IC identified
- MOSFET Q2 (TPNTA4153NT1G) correctly identified driving speaker with 100-ohm gate resistor
- UART TX/RX detected for serial interface
- Five 74HC4051 analog mux ICs identified

### Incorrect
- Touch pad matrix components (K0-K10) classified as relay type - these are PCB touch pads for a virtual ZX Spectrum keyboard, not electromechanical relays
  (statistics.component_types)
- Touch pad matrix components A1, V1, T1 classified as ic/varistor/transformer respectively - all are touch pad matrix elements
  (statistics.component_types)
- Component count shows 11 relays, 1 varistor, 1 transformer - all are actually touch pad keyboard matrix elements
  (statistics.component_types)

### Missed
- ZX Spectrum keyboard matrix using touch pads (K0-K10) with 74HC4051 multiplexers not identified as a key matrix
  (signal_analysis.key_matrices)
- SD card interface (SD-01A connector Card1) not detected as a memory card interface
  (signal_analysis.memory_interfaces)
- TFT display interface only partially detected (SPI signals found) - CS, DC, RST, and backlight control lines not grouped
  (design_analysis.bus_analysis)
- Battery management subsystem (TP4057 charger + TPS2117 power mux + battery connector) not identified as a complete power path
  (signal_analysis)
- QWIIC/I2C connectors (SM04B-SRSS-TB) not detected as I2C expansion ports
  (design_analysis.bus_analysis)

### Suggestions
- Use lib_id to distinguish touch pad matrix symbols from actual relay/transformer/varistor symbols
- Detect key matrices when multiplexer ICs (74HC4051, 74HC138) connect to arrays of switches or touch pads
- Identify SD card connectors and their SPI/SDIO data lines as memory interfaces
- Recognize QWIIC connector footprints as I2C expansion ports
- Detect battery charger + power mux combinations as battery management subsystems

---
