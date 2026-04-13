# Findings: CIRCUITSTATE/Mitayi-Pico-D1 / Mitayi-Pico-D1

## FND-00000130: RP2040 dev board with good analysis quality. Crystal circuit, SPI flash, LDO, USB, decoupling all detected. Power domains correctly map RP2040 dual-rail (+1V1/+3V3). Minor issues with crystal frequency not parsed from value string and all subcircuit neighbors being identical.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/Mitayi-Pico-D1/Mitayi-Pico-D1.kicad_sch
- **Created**: 2026-03-14

### Correct
- RP2040 dual power domains (+1V1, +3V3) correctly identified
- W25Q32JVSSIQ SPI flash detected with 6 shared signal nets to RP2040 (memory_interfaces)
- MIC5219-3.3 LDO correctly identified with VSYS input and +3V3 output
- Crystal Y1 with 30pF load caps correctly detected, effective CL=18pF calculated
- USB data lines detected with series resistors R5/R6 (27R)
- Decoupling analysis shows good coverage: +1V1 has 3 caps/1.2uF, +3V3 has 11 caps/14uF
- RC filter on RUN pin (R9 10K + C19 1uF, fc=15.92Hz) correctly detected
- ERC warnings for V_EN, AREF, RUN nets are legitimate observations
- 2 DNP parts correctly tracked

### Incorrect
- Crystal frequency field is null despite value string containing frequency info (YIC-12M20P2 is likely 12MHz)
  (signal_analysis.crystal_circuits)
- Subcircuit neighbors are identical for all 3 ICs (U1, U2, U3) - listing same 5 caps for each regardless of actual connectivity
  (subcircuits)
- RC filter on XOUT (R10 1K + C18 30pF, fc=5.3MHz) is not actually an RC filter - C18 is a crystal load cap
  (signal_analysis.rc_filters)

### Missed
- SPI bus between RP2040 and W25Q32 flash not detected in bus_analysis.spi
  (design_analysis.bus_analysis.spi)
- USB-C connector CC resistors (R3/R4 5.1K) not identified
  (signal_analysis.design_observations)
- BS5817WS Schottky diode (D1) function not identified - likely VSYS power OR-ing
  (signal_analysis.protection_devices)

### Suggestions
- Parse crystal frequency from MPN/value string (12MHz from YIC-12M20P2)
- Fix subcircuit neighbor detection
- Exclude crystal load caps from RC filter detection (caps connected to crystal XIN/XOUT pins)
- Detect SPI flash bus connections in bus_analysis

---
