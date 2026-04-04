# Findings: GP8B / Project_GP8B

## FND-00000568: Multi-sheet parsing: all 8 hierarchical sheets correctly discovered and parsed; LDO regulator TPS7A0518PDBZR correctly detected as 3.3V→1.8V LDO; SPI bus detected with correct signal net names; Dec...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Project_GP8B.sch.json
- **Created**: 2026-03-23

### Correct
- The top-level sheet references 7 sub-sheets (fileOperation.sch, fileNumberSelect.sch, fileRegister.sch, fileRAM.sch, fileInstruction.sch, fileSPI.sch, fileConnector.sch) and the analyzer found all 8 (including root). Total 109 components, 503 nets, 37 no-connects — plausible for this design.
- power_regulators shows U28 TPS7A0518PDBZR with topology=LDO, input_rail=+3.3V, output_rail=+1V8. This matches the schematic which has +3.3V and +1V8 power symbols present.
- SPI bus detected with SCK=SPI_SCLK, MISO=SPI_MISO, MOSI=SPI_MOSI, chip_select_count=1. The design has an SPI interface connecting the CPLD to a shift register for config, with these exact net names visible in the source.
- +5V rail has 31 caps (1.48uF total), +3.3V has 15 caps (2.85uF), +1V8 has 3 caps (1.2uF). The caps are genuinely split this way across the multi-sheet design and the totals are plausible.

### Incorrect
- The design has JTAG programming interface for the Xilinx XC2C256 CPLD with nets TCK, TDI, TDO, TMS (8 JTAG labels found) and a dedicated J1 'ALU_JTAG' 6-pin header. The bus_analysis only contains i2c, spi, uart, can keys — no jtag detection. This is a missed protocol classification.
  (signal_analysis)
- U2/U1/U5 (74AHC05), IC1 (XC2C256), U30 (SN74LVC8T245DW), U32 (SN74AVC4T245D), and others show power_rails containing '__unnamed_2', '__unnamed_5' etc. instead of 'GND'. These ICs use split power symbols (separate VCC and GND pins in the Custom: library) and the analyzer fails to resolve their GND pin nets to the 'GND' power net name.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000569: Subsheet-only analysis correctly scopes to 19 local components and 3 local power rails; single_pin_nets reports U30 DIR pin connected to NUMBER_6 as a dangling net — false positive in subsheet context

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: fileOperation.sch.json
- **Created**: 2026-03-23

### Correct
- fileOperation.sch analyzed in isolation finds only the 19 components physically in that sheet (IC1 CPLD, J1/J4/J5 connectors, U28/U30/U32 level shifters/LDO, 12 decoupling caps) and correctly identifies +3.3V, +1V8, GND as the local power rails — no +5V which belongs to other sheets.

### Incorrect
- U30's (SN74LVC8T245DW) DIR pin is connected to NUMBER_6 which is part of the 8-bit NUMBER bus that spans multiple sheets. When fileOperation.sch is analyzed in isolation, NUMBER_6 only has one local connection (U30.DIR) so it appears as a single-pin net. In reality it drives U30.DIR from the parent sheet. This is an inherent limitation of subsheet-isolated analysis, but the warning is misleading.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
