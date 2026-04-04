# Findings: ISM02 / hw_sch_pcb_ISM02

## FND-00000648: SPI bus detected twice for a single-bus design (U1 SX1262 only); RF chain correctly detects SX1262 transceiver and PE4259 RF switch; Power regulator U2 (MIC5504-3.3YM5 LDO) correctly detected +5V t...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_ISM02.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- rf_chains contains one chain with U1 (SX1262) as transceiver and U3 (PE4259) as switch. rf_matching correctly identifies the pi-match network (L7, C22, C17, C19) around antenna J12.
- power_regulators lists U2 with topology LDO, input_rail +5V, output_rail +3V3, estimated_vout 3.3 from fixed_suffix. Correct.
- rc_filters correctly computes the R=100R, C=1nF low-pass filter with cutoff ~1.59 MHz on the DIO2 net going to the SX1262 DIO2 pin. Value calculation is correct.

### Incorrect
- bus_analysis.spi contains two entries: bus_id '0' and bus_id 'pin_U1', both describing the same MISO/MOSI/SCK nets connected only to U1. The second entry adds no new information; the deduplication between net-based and pin-name-based SPI detection is failing for single-device buses.
  (signal_analysis)

### Missed
- crystal_circuits reports Y1 with load_caps=[] but the schematic has small-value caps (C11 '-' value, C12 '-' value) near the crystal. C11/C12 have value '-' which may cause the cap-association logic to skip them. This is a data quality issue (unspecified cap values) but worth checking whether the crystal oscillator connection is being traced.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000649: PCB metrics correct: 55 footprints, 325 tracks, 194 vias, fully routed 2-layer board; Tombstoning risk correctly flagged on L4 (0402) due to thermal asymmetry with zone

- **Status**: new
- **Analyzer**: pcb
- **Source**: hw_sch_pcb_ISM02.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Statistics match the schematic component count (55). Board dimensions 50.3x30.0mm correctly extracted. All 29 nets fully routed.
- L4 (47nH, 0402) has pad1 connected to a zone net and pad2 on signal-only — thermal asymmetry correctly identified as medium tombstoning risk.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
