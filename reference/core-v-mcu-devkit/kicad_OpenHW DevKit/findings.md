# Findings: core-v-mcu-devkit / kicad_OpenHW DevKit

## FND-00000132: RISC-V dev kit with CORE-V MCU: strong bus protocol and power regulation detection, voltage sense dividers correctly found for power monitoring

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/core-v-mcu-devkit/kicad/OpenHW DevKit.kicad_sch
- **Created**: 2026-03-14

### Correct
- Four-rail LDO cascade correctly identified: AMS1117-3.3 (VDC->3.3V), AP2127K-1.8 (3.3V->1.8V), AP2127K-ADJ (3.3V->0.8V), AP2127K-2.8 (3.3V->2.8V)
- I2C buses detected at two voltage levels: 3.3V domain (sda/scl with 4.7k pull-ups) and 1.8V domain (i2c_sda/i2c_scl with 4.7k pull-ups)
- SPI bus correctly identified connecting SOC to flash (MISO0_SOC, MOSI0_SOC, SCLK0_SOC) and MikroBUS click socket
- Voltage sense dividers for power monitoring detected: 1.8V sense (R36/R37), 3.3V sense (R34/R35), 0.8V sense (R38/R39) feeding SENSE pins
- Two crystal circuits found: 12MHz main oscillator and 32.768kHz RTC crystal with 12.5pF load caps, plus 10MHz active oscillator (ECS-2520MVLC)
- Differential pair d+/d- detected with ESD protection via U2
- JTAG debug interface signals detected on UART nets

### Incorrect
- Differential pair typed as generic "differential" rather than "USB" despite d+/d- naming convention matching USB data lines
  (design_analysis.differential_pairs)

### Missed
- JTAG/debug interface (jtag signals visible in nets) not identified as a debug bus protocol
  (design_analysis.bus_analysis)
- MikroBUS click socket interface not identified - standardized expansion bus with SPI, I2C, UART, and GPIO
  (design_analysis.bus_analysis)
- Camera interface connector not detected as a parallel camera bus (MIPI CSI or parallel)
  (design_analysis.bus_analysis)
- AWS ExpressLink module interface not identified as a cloud connectivity subsystem
  (signal_analysis)

### Suggestions
- Detect JTAG interfaces (TCK, TMS, TDI, TDO, nRST) as a debug bus protocol
- Identify MikroBUS socket pinouts as standardized expansion interfaces
- Recognize d+/d- net naming as USB differential pairs

---
