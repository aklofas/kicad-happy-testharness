# Findings: Siegmundshof93/kicadPCBs / amurNutzlast

## FND-00002271: LT3030 regulator estimated_vout=0.601V incorrect; analyzer selects current-sense resistors (0.1Ω/100Ω) instead of ADJ pin feedback divider (357kΩ/210kΩ); Correct detection of FPGA design with I2C/S...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicadPCBs_amurNutzlast_amurNutzlast.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- For the ICE40HX1K-TQ144 FPGA design, the analyzer correctly identifies: 1 I2C bus, 2 SPI buses, 4 UART buses; a crystal circuit for Y1 with proper load cap identification (C38, C37 at 18pF each); decoupling capacitor groupings per power rail (+3.3V, +1V8, etc.); the W25Q128JVS flash memory interface connected to the ICE40 with 4 shared signal nets; and 3 power regulators (LT3030, LD1117S33TR, FT2232HL internal LDO). The design_observations correctly flag U4 (FT2232HL) as missing decoupling on the '+' rail.

### Incorrect
- U2 (LT3030 dual LDO) has two feedback paths. The analyzer selects the voltage divider formed by R10 (0.1Ω, top_net='+1V2') and R11 (100Ω, bottom_net='GND') and calculates estimated_vout = 0.6 * (100/100.1) = 0.601V. However R10/R11 are current sense resistors placed in the output current path, not the ADJ feedback divider. The actual feedback divider for OUT1 is R12 (357kΩ, top) and R13 (210kΩ, bottom) connecting to the ADJ1 pin. Using the correct formula Vout = Vref*(1 + R_top/R_bot) = 0.6*(1 + 357k/210k) = 1.62V. The analyzer incorrectly identifies any voltage divider whose midpoint connects to a regulator pin, without distinguishing sense resistors from feedback resistors by value.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
