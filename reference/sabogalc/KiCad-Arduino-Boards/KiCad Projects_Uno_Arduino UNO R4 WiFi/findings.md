# Findings: sabogalc/KiCad-Arduino-Boards / KiCad Projects_Uno_Arduino UNO R4 WiFi_Arduino UNO R4 WiFi

## FND-00002615: Arduino UNO R4 WiFi with R7FA4M1AB3CFM MCU, ESP32-S3-MINI WiFi module, ISL854102 buck converter, AP7361C LDO, 12x8 charlieplexed LED matrix, USB-C with analog switch mux, and TXB0108 level translation; buck converter topology missed, USB ESD detection inconsistent, LED matrix undetected

- **Status**: new
- **Analyzer**: schematic
- **Source**: KiCad Projects_Uno_Arduino UNO R4 WiFi_Arduino UNO R4 WiFi.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- AP7361C-33E (U5) correctly identified as LDO regulator with +5V input and +3.3V output at 3.3V estimated
- Q1 and Q2 (2N7002KT1G) correctly identified as MOSFET I2C level shifters between +3.3VA and +5V domains
- TXB0108DQSR (U4) correctly identified with dual power domains +3.3V and +5V and io_rails
- 4 I2C bus lines detected with pull-ups (IIC0_SCL/SDA at 5.1k and secondary SCL/SDA pair at 5.1k)
- 8 UART nets detected including ESP_TXD0/RXD0 and multiple SCI channels on RA4M1
- USB differential pair (USB_D_P/USB_D_N) correctly identified with series resistors
- D3 PRTR5V0U2X correctly identified as ESD IC protecting USB_D_N and USB_D_P
- 2 voltage dividers correctly detected: R59/R60 (100k/13.7k from +5V for ADC sensing) and R56/R57 (100k/100k from +3.3V for ESP32 ADC)
- Decoupling analysis correctly identified 7 caps on +5V (28.1uF total) and 3 caps on +3.3V (22.2uF total)
- F1 (MF-MSMF050-2-W2) correctly identified as fuse protecting +3.3VA from +3.3V
- 3 differential pairs detected: USB, RA4_P/RA4_N (MCU USB), ESP_P/ESP_N (ESP32 USB)
- 262 total components correctly counted across root and 5 hierarchical sub-sheets (Capacitors, Headers, Power, LED Matrix, ESP32-S3)

### Incorrect
- USB differential pair has_esd:false but D3 (PRTR5V0U2X) is detected as ESD IC in protection_devices — internal inconsistency between differential_pairs and protection_devices sections
  (design_analysis.differential_pairs)
- RA4_P/RA4_N differential pair has has_esd:true with esd_protection:[U1] but U1 is the R7FA4M1AB3CFM MCU, not an ESD protection device
  (design_analysis.differential_pairs)
- D1 and D2 (PMEG6020AELRX Schottky diodes) classified as reverse_polarity protection but they are power ORing diodes for input source selection (barrel jack VCC->VDD and USB VBUS->+5V)
  (signal_analysis.protection_devices)
- DL1-DL4 (Device:LED indicator LEDs) classified as type 'diode' in BOM instead of 'led', causing led count to be 96 instead of 100 and diode count inflated from 3 to 7
  (statistics.component_types)
- ISL854102FRZ-T (U3) topology classified as 'unknown' — should be 'buck' converter (has VIN, PHASE, BOOT, FB, COMP, SS pins characteristic of synchronous buck)
  (signal_analysis.power_regulators)

### Missed
- ISL854102 output rail +5V not identified — the PHASE pin connects through L3 (10uH) to the +5V rail, and feedback divider R44 (100k) / R40 (13.7k) sets output to ~5.0V
  (signal_analysis.power_regulators)
- Feedback network for ISL854102 buck converter not detected — R44 (100k) top and R40 (13.7k) bottom form FB divider from +5V output to U3 FB pin
  (signal_analysis.feedback_networks)
- SPI bus not detected despite clear SPI0 signals on RA4M1: P411_SPI0_MOSI, P410_SPI0_MISO, P102_SPI0_RSPCK, P103_SPI0_SSL all routed to Arduino headers
  (design_analysis.bus_analysis.spi)
- M1 (ESP32-S3-MINI-1-N8) missing from power_domains.ic_power_rails — should show +3.3V power domain
  (design_analysis.power_domains.ic_power_rails)
- 96-LED charlieplexed matrix (11 ROW lines driven by RA4M1 MCU) not detected in any signal analysis category
  (signal_analysis.addressable_led_chains)
- EXT_SCL/EXT_SDA I2C lines (level-shifted external side through Q1/Q2 MOSFETs) not detected in I2C bus analysis
  (design_analysis.bus_analysis.i2c)

### Suggestions
- Recognize ISL854102 as a buck converter based on pin names (VIN, PHASE, BOOT, FB, COMP, SS) — these are canonical synchronous buck controller pins
- Cross-reference differential_pairs ESD detection with protection_devices to avoid has_esd:false when an ESD IC is on the same nets
- Classify Device:LED components with DL-prefix references as 'led' type not 'diode' — the lib_id clearly indicates LED
- Detect SPI bus from net names containing SPI/MOSI/MISO/SCK/SS patterns even when no SPI-specific IC is on the bus (signals are exposed on expansion headers)
- Include WiFi/BLE modules (ESP32-S3-MINI-1-N8) in power domain analysis — the M prefix should not exclude it from IC enumeration
- Distinguish power ORing Schottky diodes (between two power rails) from reverse polarity protection (between power and ground)

---
