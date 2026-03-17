# Findings: rp2040-motor-controller / RP2040_base_RP2040_base

## FND-00000123: Motor controller base board: good power regulation and CAN bus detection, but missing current sense on base board and isolation components not identified

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/rp2040-motor-controller/RP2040_base/RP2040_base.kicad_sch
- **Created**: 2026-03-14

### Correct
- Power regulation chain correctly identified: MT2492 switching 12V->5V with feedback divider (R15/R16, estimated 5.0V), TLV1117 LDOs for 3.3V and 3.3VA, TX4139 switching from VMOT
- CAN bus differential pairs detected for CAN0 (CAN0_P/CAN0_N) and CAN1 (CAN1_P/CAN1_N) with ESD protection noted
- USB differential pairs found for both RP2040 CPUs (USB_D+/- and USB_D_2+/-) with USBLC6 ESD protection
- I2C buses correctly detected with pull-ups: SDA1/SCL1 with 10k to +3V3, and ADC_DATA I2C line found (missing pull-up flagged)
- Dual RP2040 architecture detected with supporting flash memory (W25Q128JVSIQ), crystals (12MHz with 20pF load caps)
- P-channel MOSFET Q3 (NCE40P05Y) correctly identified as high-side power switch on 12V rail with gate resistor
- Isolation barrier detected between GND and GND_ISO domains with isolated power rails (+5V_ISO, +5V_ISO_FILT)
- MCP2515 CAN controller and CA-IS3052G isolated CAN transceiver identified in IC analysis

### Incorrect
- TX4139 regulator feedback divider shows input as +12V but R96/R97 ratio gives 8.97V output - the input should be VMOT not +12V for the voltage divider top_net
  (signal_analysis.voltage_dividers)
- Isolation barrier lists no isolation_components despite SFH617A optocoupler and LTV-208 dual optocouplers being present in the design
  (signal_analysis.isolation_barriers)

### Missed
- E-stop circuit with optocoupler-based safety interlock (Q7 NMOS on GND_ISO, SFH617A optocoupler crossing isolation barrier) not identified as a safety/interlock circuit
  (signal_analysis)
- No SPI bus detected despite ADC081S021 and ADS7822 ADCs communicating via SPI (MISO/MOSI/SCLK lines)
  (design_analysis.bus_analysis)
- Level shifters TXS0101DCKR not identified in the signal path between isolated and non-isolated domains
  (signal_analysis.isolation_barriers)
- Dual CAN bus architecture (MCP2515+CA-IS3052G for CAN0, separate path for CAN1) not described as a redundant/dual CAN topology
  (design_analysis.bus_analysis)

### Suggestions
- Detect optocouplers (SFH617A, LTV-827S) as isolation_components in isolation barrier analysis
- Identify SPI buses from ADC data lines (MISO/MOSI/SCLK naming patterns)
- Recognize e-stop/safety interlock circuits as a distinct signal type
- Link level shifters to isolation barrier analysis

---
