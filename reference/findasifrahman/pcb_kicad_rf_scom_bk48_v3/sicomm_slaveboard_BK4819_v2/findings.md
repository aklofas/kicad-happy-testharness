# Findings: findasifrahman/pcb_kicad_rf_scom_bk48_v3 / sicomm_slaveboard_BK4819_v2

## FND-00000219: BK4819 RF board power sub-sheet (11 components). False negative: TPLP5907MFX-3.3 linear regulator (U19) not detected as power regulator despite clear LDO topology with input/output decoupling. IC pin analysis correctly identified all 5 pins and decoupling caps. Design observation incorrectly lists VBAT as rail_without_caps despite C1(10uF)+C163(100nF) being present.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_sicomm_bk4819.kicad_sch.json
- **Related**: KH-118
- **Created**: 2026-03-16

### Correct
- All 11 components correctly identified with proper values (U19 TPLP5907MFX-3.3, R26/R27/R28 100ohm, C1 10uF, C160/C161/C163 100nF)
- U19 IC pin analysis correct: VIN/GND/EN/NC/VOUT pins properly mapped, decoupling caps identified per rail

### Incorrect
- Design observation reports VBAT in rails_without_caps despite C1(10uF) and C163(100nF) present on that rail. Contradicts IC pin analysis which correctly identifies decoupling.
  (signal_analysis.design_observations)

### Missed
(none)

### Suggestions
- Add TPLP pattern to regulator part number recognition (TECH PUBLIC linear regulators)
- Fix design_observations decoupling logic to use IC pin analysis data correctly
- Consider topology-based regulator detection as fallback when part number matching fails

---

## FND-00000222: BK4819 RF transceiver board main schematic (123 components). LC filter overcounting: 23 reported but most are L-C net pairs in RF matching, not discrete filters. RF chain detection misses BK4819 transceiver and CMX994E1 analog front-end. X2 26MHz crystal not detected. RF matching networks (2) correctly identified. ERC warnings (16) are expected for test/interface board with jumper connectors.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: sicomm_slaveboard_BK4819_v2.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 2 RF matching networks correctly identified: LNA_IN1 (antenna to CMX994E1) and ANT1 (antenna to RF switch), topologies and components verified
- 123 total components, 58 unique parts correctly counted. BOM values verified across 72 caps, 22 resistors, 14 inductors, 7 ICs
- Hierarchical schematic properly analyzed across 3 sheets (Amplifier, SCT3811, PCB_sicomm_bk4819)

### Incorrect
- 23 LC filters overcounted — analyzer pairs every inductor-capacitor sharing a net. In RF designs these are impedance matching components, not discrete LC filters. L7 alone generates 4 pairs.
  (signal_analysis.lc_filters)

### Missed
- X2 26MHz crystal in SCT3811.kicad_sch not detected as crystal circuit. Primary clock source for RF design.
  (signal_analysis.crystal_circuits)

### Suggestions
- Refine LC filter detection to identify actual filter topologies rather than any L-C net pairing
- Extend RF chain detection to recognize transceiver ICs (BK4819) and mixed-signal RF front-ends (CMX994E1)
- Check crystal detection for components in hierarchical sub-sheets

---
