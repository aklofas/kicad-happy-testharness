# Findings: Sudhamsu98/AD4858_Breakout_Board / AD4858_breakout

## FND-00000350: LT1761-SD adjustable LDO output voltage estimates use wrong Vref heuristic (0.6V instead of 1.22V)

- **Status**: new
- **Analyzer**: schematic
- **Source**: AD4858_breakout_powerSupply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The LT1761-SD has an internal reference of 1.22V. For U7 (target +2V5 rail): R1=1.05K/R2=1K gives Vout=1.22*(1+1050/1000)=2.50V, but analyzer estimates 1.23V using 0.6V heuristic and flags a 50.8% vout_net_mismatch. For U6 (target +1V8 rail): R3=475/R4=1K gives Vout=1.22*(1+475/1000)=1.80V, but analyzer estimates 0.885V and again flags a mismatch. Both regulators are actually set correctly for their target rails; the mismatch observations are false positives caused by the wrong Vref assumption. The LT1761-SD datasheet specifies Vref=1.22V.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000351: SPI/serial configuration interface of AD4858BBCZ not detected despite CS, CSCK, CSDIO, CSD0 nets

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: AD4858_breakout_ad4858.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The AD4858 ADC uses a serial peripheral interface for configuration and readback with nets named CS (chip select), CSCK (serial clock), CSDIO (bidirectional data I/O), and CSD0 (data output). These nets are present in the schematic and connected to U1 (AD4858BBCZ), but bus_analysis.spi=[] and no SPI interface is detected. The signal names use the AD4858-specific naming convention rather than generic MOSI/MISO/SCLK/SS names, which causes the SPI detector to miss this interface. Additionally, the bus_topology.detected_bus_signals only picks up the SDO0..SDO7 parallel output bus prefix, not the actual config interface.
  (design_analysis)

### Suggestions
(none)

---

## FND-00000352: U1 (AD4858BBCZ) appears twice in the components list, causing a mismatch between statistics and actual list length

- **Status**: new
- **Analyzer**: schematic
- **Source**: AD4858_breakout_AD4858_breakout.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The full-project output has 183 entries in the components array but statistics.total_components=182 and statistics.component_types.ic=5. Inspection shows U1 (AD4858BBCZ) appears at two different UUIDs (1ff72a26 and af850a67) both on sheet=2 (the ad4858.kicad_sch sub-sheet). The BOM correctly deduplicates to qty=1 for AD4858BBCZ, but the components list carries the duplicate. This likely arises because the ad4858.kicad_sch sub-sheet defines U1 across two symbol instances (the chip symbol is split into two units in the KiCad library definition with different pin groups), and the parser adds both units as separate component entries without deduplicating by reference.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
