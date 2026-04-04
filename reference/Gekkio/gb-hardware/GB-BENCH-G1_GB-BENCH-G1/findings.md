# Findings: gb-hardware / GB-BENCH-G1_GB-BENCH-G1

## ?: Game Boy test bench with DMG CPU, dual CPLDs, dual SRAM, 3 LDOs; good component/net/bus extraction, but missed JTAG chain, memory interfaces, fuse protection, and incorrectly flags regulator input caps as missing

- **Status**: new
- **Analyzer**: schematic
- **Source**: GB-BENCH-G1_GB-BENCH-G1.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All 98 real components correctly counted and categorized (38 caps, 16 resistors, 11 LEDs, 12 connectors, 8 ICs, 9 test points, 1 fuse, 1 switch, 1 jumper, 1 oscillator)
- Three LDO regulators correctly identified: U2 MCP1703A-1802 (1.8V), U3 MCP1703A-3302 (3.3V), U4 MCP1703A-5002 (5V) with correct input rail VDC and output rails
- Active oscillator X1 (XO32) correctly identified as active_oscillator with output on SYS_CLK net feeding both CPLDs (U1, U5)
- Power rails correctly identified: +1V8, +3V3, +5V, GND, VIN, VDC (PWR_FLAG also listed)
- Bus topology detected 13 bus signal groups including A[0:15] (16-bit address), D[0:7] (8-bit data), MA[0:12] (VRAM address), MD[0:7] (VRAM data), SYS_A[0:7], SYS_D[0:7], SYS_C[0:4]
- GameBoy CPU U8 correctly has all 80 pins mapped with proper net assignments (A0-A15, D0-D7, MD0-MD7, MA0-MA12, control signals)
- Decoupling analysis correctly identified 8 caps on +5V (15.03uF), 16 caps on +3V3 (14.95uF), 11 caps on +1V8 (14.54uF) with proper bypass cap identification
- 9 test points correctly mapped to their nets: TP1=VDC, TP2=1.8V, TP3=3.3V, TP4=5.0V, TP5=XO, TP6=T1, TP7=T2, TP8=CLK, TP9=SYS_CLK
- Dual CPLD (U1, U5 LC4256ZE) power domains correctly identified as having both +1V8 (core) and +3V3 (I/O) rails
- 23 no-connect markers correctly counted matching the schematic

### Incorrect
- Design observations incorrectly flag U2, U3, U4 as having missing input caps on VDC rail. In reality, C10, C11, C12 (all 4.7uF) are directly on the VDC net serving as shared input capacitors for all three regulators. The analyzer fails to recognize shared bulk input caps when multiple regulators share an input rail.
  (signal_analysis.design_observations)
- ERC warning 'no_driver' on VDC net is incorrect. VDC is driven through the power path: J1 barrel jack -> JP1 jumper -> SW1 switch -> F1 fuse -> VDC. The fuse output drives VDC. The analyzer does not recognize passive component chains as valid power paths.
  (design_analysis.erc_warnings)
- ERC warning 'no_driver' on CLK net is debatable. CLK connects U1.P6 (CPLD output, typed 'passive' due to custom library) to U8.XI (input) and TP8. The CPLD drives CLK, but the generic pin type from the custom Lattice library causes a false positive.
  (design_analysis.erc_warnings)
- ERC warning 'no_driver' on TDO1 net is incorrect. TDO1 connects U1.TDO (output) to U5.TDI (input) forming a JTAG daisy chain. The Lattice CPLD library marks TDO as passive type, causing false no-driver detection.
  (design_analysis.erc_warnings)
- Cross-domain analysis flags 102 signals as needing level shifters, which is overly aggressive. The LC4256ZE CPLD has configurable I/O voltage banks (1.8V/3.3V/5V tolerant). The CPLD intentionally bridges between the 5V Game Boy domain and 3.3V system bus without external level shifters - this is its primary function in the design.
  (design_analysis.cross_domain_signals)

### Missed
- JTAG daisy chain not detected: J7 (10-pin JTAG header) -> U1 (CPLD Alpha, TDI/TCK/TMS/TDO) -> U5 (CPLD Beta, TDI/TCK/TMS/TDO) -> J7. TDO1 connects U1.TDO to U5.TDI, TDO2 connects U5.TDO to J7. TCK and TMS are shared. Pull-up/down resistors R4 (TDI), R5 (TCK to GND), R6 (TMS) present.
  (signal_analysis)
- Fuse F1 not detected as a protection device. F1 is in the power input path: J1 barrel jack -> JP1 -> SW1 -> F1 -> VDC, providing overcurrent protection for the entire board.
  (signal_analysis.protection_devices)
- Memory interface not detected: U6 (GameBoy_SRAM_64K) connected to CPU U8 via MA0-MA12 (address), MD0-MD7 (data), ~{MCS}, ~{MRD}, ~{MWR} (control). This is a classic parallel SRAM interface with active-low chip enable, output enable, and write enable.
  (signal_analysis.memory_interfaces)
- Second memory interface not detected: U7 (GameBoy_SRAM_64K) connected to CPU U8 via A0-A14 (address, remapped through cartridge slot J13), D0-D7 (data), ~{CS}, ~{RD}, ~{WR} (control). This is the external cartridge SRAM.
  (signal_analysis.memory_interfaces)
- GameBoy serial link interface not identified: SCLK, SIN, SOUT connecting CPU U8 to CPLD U1 and external connector J14. This is a synchronous serial protocol used for Game Boy link cable communication.
  (design_analysis.bus_analysis)
- GameBoy LCD interface not identified as a display bus: LD0-LD1 (2-bit pixel data), CP, CPG, CPL (clock signals), FR (frame), HSYNC, VSYNC connecting U8 to CPLD U5 and connector J9. This is the Game Boy's proprietary LCD timing interface.
  (signal_analysis)
- Pull-up resistor R1 (10K) on ~{RES} to +5V not identified. This is a standard active-low reset pull-up keeping the CPU out of reset during normal operation.
  (signal_analysis)
- LED activity indicators on bus control signals not identified: D2-D7 with R7-R12 (2.2K) showing ~{MRD}, ~{MWR}, ~{MCS}, ~{RD}, ~{CS}, ~{WR} activity. D8-D11 with R13-R16 (1K) for CPLD user LEDs. D1 with R2 (560R) as power indicator on VDC.
  (signal_analysis)

### Suggestions
- Add JTAG chain detection: look for TDI/TDO/TCK/TMS signal patterns and daisy-chained TDO->TDI connections between ICs
- Improve parallel SRAM interface detection: match patterns of address bus (A/MA), data bus (D/MD), and active-low control signals (~CE, ~OE, ~WE) connecting between ICs
- Recognize shared input capacitors for regulators: when multiple regulators share an input rail, caps on that rail serve all regulators
- Add fuse detection to protection_devices: fuses in series with power input paths are key protection elements
- Reduce false positives for cross-domain level shifter warnings when CPLDs or FPGAs are present, since they typically have configurable I/O voltage banks
- Detect LED activity indicators: LEDs connected through current-limiting resistors to active-low control signals serve as bus activity monitors

---

## ?: Game Boy DMG test bench with CPU, dual CPLDs, dual SRAM, 3 LDOs; good component/net/bus extraction but missed JTAG chain, memory interfaces, fuse protection, and incorrectly flags shared regulator input caps as missing

- **Status**: new
- **Analyzer**: schematic
- **Source**: GB-BENCH-G1_GB-BENCH-G1.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All 98 real components correctly counted and categorized (38 caps, 16 resistors, 11 LEDs, 12 connectors, 8 ICs, 9 test points, 1 fuse, 1 switch, 1 jumper, 1 oscillator)
- Three LDO regulators correctly identified: U2 MCP1703A-1802 (1.8V), U3 MCP1703A-3302 (3.3V), U4 MCP1703A-5002 (5V) with correct input rail VDC and output rails
- Active oscillator X1 (XO32) correctly identified as active_oscillator with output on SYS_CLK net feeding both CPLDs U1 and U5
- Power rails correctly identified: +1V8, +3V3, +5V, GND, VIN, VDC
- Bus topology detected 13 bus signal groups including A[0:15], D[0:7], MA[0:12], MD[0:7], SYS_A[0:7], SYS_D[0:7], SYS_C[0:4]
- Decoupling analysis correctly identified 8 caps on +5V (15.03uF), 16 caps on +3V3 (14.95uF), 11 caps on +1V8 (14.54uF) across three rails
- 9 test points correctly mapped: TP1=VDC, TP2=1.8V, TP3=3.3V, TP4=5.0V, TP5=XO, TP6=T1, TP7=T2, TP8=CLK, TP9=SYS_CLK
- Dual CPLD power domains correctly identified as having both +1V8 (core) and +3V3 (I/O) rails
- 23 no-connect markers correctly counted matching the schematic
- 8 subcircuits correctly identified centered on U8, U7, U6, U1, U5, U2, U3, U4 with appropriate neighbor components

### Incorrect
- Design observations incorrectly flag U2, U3, U4 as having missing input caps on VDC rail. C10, C11, C12 (all 4.7uF) are directly on the VDC net serving as shared input capacitors for all three regulators. The analyzer fails to recognize shared bulk input caps when multiple regulators share an input rail.
  (signal_analysis.design_observations)
- ERC warning 'no_driver' on VDC net is incorrect. VDC is driven through the power path: J1 barrel jack -> JP1 jumper -> SW1 switch -> F1 fuse -> VDC. The analyzer does not recognize passive component chains as valid power driver paths.
  (design_analysis.erc_warnings)
- ERC warning 'no_driver' on TDO1 net is incorrect. TDO1 connects U1.TDO (output) to U5.TDI (input) forming a JTAG daisy chain. The custom Lattice CPLD library marks TDO as passive type, causing false no-driver detection.
  (design_analysis.erc_warnings)
- ERC warning 'no_driver' on CLK net is incorrect. CLK is driven by CPLD U1 pin P6 to CPU U8 pin XI. The CPLD generates the clock from SYS_CLK, but the generic passive pin type from the custom Lattice library causes a false positive.
  (design_analysis.erc_warnings)
- Cross-domain analysis flags 102 signals as needing level shifters, which is overly aggressive. The LC4256ZE CPLDs have configurable I/O voltage banks and intentionally bridge the 5V Game Boy domain and 3.3V system bus without external level shifters -- this is their primary function in the design.
  (design_analysis.cross_domain_signals)

### Missed
- JTAG daisy chain not detected: J7 (10-pin header) -> U1 (CPLD Alpha TDI/TCK/TMS/TDO) -> U5 (CPLD Beta TDI/TCK/TMS/TDO) -> J7. TDO1 connects U1.TDO to U5.TDI, TDO2 connects U5.TDO to J7. Pull resistors R4 (TDI to +1V8), R5 (TCK to GND), R6 (TMS to +1V8) present.
  (signal_analysis)
- Fuse F1 not detected as a protection device. F1 is in the power input path: J1 barrel jack -> JP1 -> SW1 -> F1 -> VDC, providing overcurrent protection for the entire board.
  (signal_analysis.protection_devices)
- VRAM memory interface not detected: U6 (GameBoy_SRAM_64K) connected to CPU U8 via MA0-MA12 (13-bit address), MD0-MD7 (8-bit data), ~{MCS} (chip enable), ~{MRD} (output enable), ~{MWR} (write enable). Classic parallel SRAM interface.
  (signal_analysis.memory_interfaces)
- Cartridge SRAM interface not detected: U7 (GameBoy_SRAM_64K) connected to CPU U8 via A0-A14 (address through cartridge slot J13), D0-D7 (data), ~{CS}, ~{RD}, ~{WR} (control). External cartridge SRAM with active-low control.
  (signal_analysis.memory_interfaces)
- Game Boy serial link interface not identified: SCLK, SIN, SOUT connecting CPU U8 to CPLD U1 and external connector J14 (5-pin). This is the Game Boy link cable synchronous serial protocol.
  (design_analysis.bus_analysis)
- Game Boy LCD interface not identified as a display bus: LD0-LD1 (2-bit pixel data), CP/CPG/CPL (clock phases), FR (frame), HSYNC, VSYNC connecting CPU U8 to CPLD U5 and connector J9 (8-pin). Proprietary LCD timing interface.
  (signal_analysis)
- Pull-up resistor R1 (10K) on ~{RES} to +5V not identified as a reset pull-up. Standard active-low reset pull-up keeping the CPU out of reset during normal operation.
  (signal_analysis)
- LED activity indicators on bus control signals not identified: D2-D4 with R7-R9 (2.2K) on ~{MRD}/~{MWR}/~{MCS}, D5-D7 with R10-R12 (2.2K) on ~{RD}/~{CS}/~{WR}, D8-D11 with R13-R16 (1K) for CPLD user LEDs, D1 with R2 (560R) as VDC power indicator.
  (signal_analysis)

### Suggestions
- Add JTAG chain detection: look for TDI/TDO/TCK/TMS signal patterns and daisy-chained TDO->TDI connections between ICs
- Improve parallel SRAM interface detection: match patterns of address bus, data bus, and active-low control signals (~CE, ~OE, ~WE) connecting between ICs
- Recognize shared input capacitors for regulators: when multiple regulators share an input rail, caps on that rail serve all regulators and should not be flagged as missing
- Add fuse detection to protection_devices: fuses in series with power input paths are key protection elements
- Reduce false positives for cross-domain level shifter warnings when CPLDs or FPGAs with configurable I/O banks are present
- Detect LED activity indicators: LEDs connected through current-limiting resistors to active-low control signals serve as bus activity monitors

---
