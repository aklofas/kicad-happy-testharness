# Findings: piotr-binkowski/kintex-pcie-board / kintex-pcie

## FND-00002614: Kintex-7 FPGA PCIe x8 board with DDR2, SPI flash, LVDS B2B links, quad PMIC, and 125MHz oscillators; good differential pair detection but missed DDR2 memory interface, quad regulator outputs, SPI bus, and oscillators

- **Status**: new
- **Analyzer**: schematic
- **Source**: kintex-pcie.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- PCIe x8 differential pairs correctly identified (24 PCIe-typed pairs covering TX0-TX7 and RX0-RX7 both pre- and post-AC-coupling)
- Total component count of 166 matches schematic (90 caps, 33 resistors, 12 LEDs, 9 ICs, 6 connectors, 8 net ties, 3 transistors, 2 ferrite beads, 2 mounting holes, 1 jumper)
- Kintex-7 FPGA U1 (XC7K160T-FFG676) correctly parsed as 8-unit multi-unit symbol with 676 total pins
- W25Q128JVS SPI flash (U3) correctly detected as memory interface connected to FPGA with 6 shared signal nets
- TPD4E02B04DQAR ESD protection ICs (U6, U7) correctly detected protecting B2B differential pairs
- Power sequencing correctly detects U8 EN driven by 1V_PG (power good from U9), establishing U9->U8 sequence
- BSS138 MOSFET LED drivers (Q1, Q2, Q3) correctly detected with gate pulldown resistors and LED load identification
- Voltage divider R15/R16 (15K/3K from +12V) correctly detected feeding U9 EN pin via 1V_EN net
- VREF voltage divider R18/R19 (2K/2K from +1V8) correctly detected generating 0.9V reference for DDR2 SDRAM U2
- GND and GNDA dual ground domains correctly identified with GNDA as analog ground for FPGA VDDA supply
- 7 power rails correctly identified (+12V, +1V0, +1V8, +3V3, GND, GNDA, VDDA)
- DDR bus signals correctly detected in bus topology (DDR_A0-13, DDR_BA0-1, DDR_DQ0-7)
- DDR differential clock (DDR_CK_P/N) and data strobe (DDR_DQS_P/N) pairs correctly identified
- Decoupling analysis correctly identifies 5 power rails with cap counts: +1V0 (17 caps, 486.9uF), +3V3 (9 caps), +1V8 (23 caps), +12V (5 caps), VDDA (2 caps)

### Incorrect
- MPM54304GMN-0000 (U8) identified as producing only MGTAVTT with topology 'ic_with_internal_regulator'. It is actually a quad PMIC producing 4 rails: +1V8 (VOUT1), +3V3 (VOUT2), MGTAVCC (VOUT3), MGTAVTT (VOUT4). The analyzer should detect all 4 output rails.
  (signal_analysis.power_regulators)
- 16 LVDS/differential signals (B2B_TXC_*, B2B_TXD_*, B2B_RXC_*, B2B_RXD_*, GTX_125_*) misclassified as UART bus signals in bus_analysis. These are differential data/clock pairs for the board-to-board LVDS link and GTX reference clock, not UART.
  (design_analysis.bus_analysis.uart)
- RC filter detection found R12+C2 as an 'RC-network' with ground_net='VSENSE_P'. This is actually a compensation/snubber capacitor in the MPM3683 differential remote sense feedback network (FB/VSENSE_P/VSENSE_N), not a signal-path RC filter. The ground_net should be recognized as part of the differential sense pair, not a ground reference.
  (signal_analysis.rc_filters)
- Power budget shows +1V8 and +3V3 rails with no regulator assigned, despite both being outputs of U8 (MPM54304). MGTAVCC rail is entirely missing from the power budget. Only MGTAVTT is attributed to U8.
  (power_budget)
- U4 and U5 (OB3225125MLDB6SI-00 125MHz LVDS oscillators) categorized as generic 'ic' type. They should be recognized as oscillator/clock sources, which would feed into crystal_circuits or a dedicated clock source detector. The part number clearly indicates 125MHz oscillator.
  (statistics.component_types)

### Missed
- DDR2 SDRAM interface: MT47H64M8SH (U2) is a 60-pin DDR2 memory IC with 28+ signal connections to FPGA U1 (DDR_A0-13, DDR_BA0-1, DDR_DQ0-7, DDR_DM, DDR_DQS_P/N, DDR_CK_P/N, DDR_CAS, DDR_RAS, DDR_WE, DDR_CKE, DDR_ODT). This is the most signal-rich interface on the board and was not detected in memory_interfaces.
  (signal_analysis.memory_interfaces)
- SPI bus between FPGA U1 and Flash U3 via nets SPI_CLK, SPI_CS, SPI_D0-D3 (Quad SPI) not detected in bus_analysis.spi despite 6 signal nets and proper SPI naming convention.
  (design_analysis.bus_analysis.spi)
- PCIe x8 interface not detected as a high-speed bus protocol. The design has a PCI Express x8 edge connector (J1) with 8 TX and 8 RX differential lanes, REFCLK+/-, PERST#, WAKE#, SMCLK/SMDAT, and JTAG signals. While differential pairs are detected, no PCIe bus-level detection exists.
  (signal_analysis)
- Two 125MHz LVDS oscillators (U4, U5) providing GTX reference clock and DDR reference clock not detected as clock sources. U4 outputs GTX_125_C_P/N feeding FPGA MGT refclk, U5 outputs DDR_125_P/N feeding FPGA bank for DDR2 clocking.
  (signal_analysis.crystal_circuits)
- MGTAVCC power rail (1.0V for FPGA MGT analog) missing from decoupling_analysis despite having C12 (22uF) and C21 (4.7uF) on the rail with 10 pin connections.
  (signal_analysis.decoupling_analysis)
- MGTAVTT power rail (1.2V for FPGA MGT termination) missing from decoupling_analysis despite having C15 (22uF) and C25 (4.7uF) on the rail with 14 pin connections.
  (signal_analysis.decoupling_analysis)
- I2C bus (MPM_SDA, MPM_SCK) between FPGA U1 and PMIC U8 detected in bus_analysis but missing pull-up resistors flagged as a design concern. The I2C bus has no pull-ups which is notable for a bus that requires them.
  (design_analysis.bus_analysis.i2c)

### Suggestions
- Quad PMIC detection should trace all VOUT pins to identify multiple output rails per IC, not just pick the first power_out net encountered
- LVDS differential pairs (B2B_*) should not be classified as UART - the TX/RX naming pattern with paired _P/_N suffixes is a clear indicator of differential signaling, not asynchronous serial
- MEMS/packaged oscillators (non-crystal) should be detected by footprint pattern (OSC-SMD*) or part number keywords (e.g., OB3225* is a well-known oscillator family) and reported in crystal_circuits or a dedicated clock_sources section
- DDR2/DDR3 SDRAM detection should recognize Micron MT47H* and similar memory ICs via lib_id patterns (contains 'Memory' or common DDR part prefixes) and confirm by checking for characteristic DDR signals (DQ, DQS, CK, RAS, CAS, WE, CKE, ODT)
- SPI bus detection should match signal name patterns like SPI_CLK, SPI_CS, SPI_D0-D3 in addition to looking at IC pin names

---
