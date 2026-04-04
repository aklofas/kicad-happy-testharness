# Findings: Kicad-PCB / IDA_demoprojekt_IDA_demoprojekt

## FND-00000794: BOM collapses all U? refs into one entry, omitting nRF24L01P, USBLC6-2SC6, and AP2112K-3.3; Crystal circuit detected correctly for Y? (ASA-16.000MHZ-L-T); AP2112K-3.3 LDO regulator not detected in ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: IDA_demoprojekt_IDA_demoprojekt.sch.json
- **Created**: 2026-03-23

### Correct
- Crystal detected in signal_analysis.crystal_circuits. ESD protection (USBLC6-2SC6), linear regulator (AP2112K-3.3), and RF IC (nRF24L01P) context correctly captured in IC context analysis.

### Incorrect
- There are 4 distinct U? components (STM32L072KZTx, nRF24L01P, USBLC6-2SC6, AP2112K-3.3) but the BOM shows only 6 entries with a single U? row for the STM32. The deduplication logic groups all same-prefix unassigned references together, losing 3 unique ICs. The signal_analysis correctly detects AP2112K-3.3 as a regulator and USBLC6-2SC6 as a protection device, but the BOM/statistics are wrong.
  (signal_analysis)

### Missed
- signal_analysis.power_regulators is empty even though AP2112K-3.3 (Regulator_Linear:AP2112K-3.3) is present. The design_observations section flags a decoupling issue for it, indicating the analyzer found it but failed to classify it as a power regulator.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000795: Empty PCB file correctly handled — all stats zero, 4-layer stackup parsed

- **Status**: new
- **Analyzer**: pcb
- **Source**: IDA_demoprojekt_IDA_demoprojekt.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The PCB is an empty template board (footprint_count=0, track_segments=0). The analyzer correctly reports all zeros and extracts the declared 4-layer stackup (F.Cu, In1.Cu, In2.Cu, B.Cu). The copper_presence warning about unfilled zones is appropriate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
