# Findings: RP2040_minimal / RP2040_minimal_r2_RP2040_minimal_r2

## FND-00001233: LDO regulator (U1 NCP1117), RP2040 (U3), W25Q128 flash (U2) all correctly identified; Crystal Y1 (ABM8-272-T3) frequency not parsed — returns null instead of 12MHz; QSPI_SCLK net categorized as 'i2...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RP2040_minimal_r2.kicad_sch
- **Created**: 2026-03-24

### Correct
- Power regulators, memory interface, crystal circuit, USB compliance (ESD fail), and decoupling analysis all produced correct results. No false pwr_flag warnings. Cross-domain QSPI signals correctly detected with needs_level_shifter=False.

### Incorrect
- ABM8-272-T3 is a 12MHz crystal from Abracon. The value string does not contain a parseable frequency (no 'MHz' substring), so frequency=null. The analyzer should handle part numbers where frequency is only in the datasheet/MPN, but as a fallback should at least note inability to parse rather than silently returning null.
  (signal_analysis)
- test_coverage.uncovered_key_nets lists QSPI_SCLK with category='i2c'. QSPI_SCLK is clearly a QSPI/SPI clock net, not I2C. This is a net-category misclassification in the test coverage detector.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001234: 2-layer 52x51mm board, 34 footprints, routing complete, DFM standard tier correctly assessed

- **Status**: new
- **Analyzer**: pcb
- **Source**: RP2040_minimal_r2.kicad_pcb
- **Created**: 2026-03-24

### Correct
- PCB stats are consistent with schematic: 34 footprints (34 schematic components), 52 nets, routing_complete=true, DFM standard tier with min track 0.15mm. Edge clearance warnings for J1/J4/J3 at 0-0.07mm are marginal but plausible for edge connectors. Decoupling placement correctly identifies 2 caps near U1 LDO and 13 near U3 RP2040.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
