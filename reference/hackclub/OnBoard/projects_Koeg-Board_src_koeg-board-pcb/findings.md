# Findings: hackclub/OnBoard / projects_Koeg-Board_src_koeg-board-pcb

## FND-00000086: Keyboard PCB with nRF52-based BLE. Key matrix (5x5, 42 keys) correctly detected. RF matching networks identified for dual chip antennas. BOM sum (260) does not match total_components (290) — gap of 30 partially explained by 26 non-BOM types.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/Koeg-Board/src/koeg-board-pcb.kicad_sch
- **Created**: 2026-03-14

### Correct
- Key matrix correctly detected: 5 rows x 5 cols, 42 switches, 42 diodes
- RF matching networks identified for two chip antennas (AE65, AE66) with pi_match topology
- 4 crystal circuits detected including 32MHz and 32.768kHz
- USB differential pair detected with ESD protection
- Transistor circuits correctly identified: Q7 (2N7002) NMOS, Q5 (AO3401A) PMOS power switch
- Battery voltage divider R2(806k)/R3(2M) correctly detected for battery monitoring
- 6 LC filters detected in GHz range consistent with RF matching components

### Incorrect
- BOM quantity sum (260) does not match total_components (290) — 30 missing, only 26 accounted for by mounting_hole(13)+fiducial(3)+graphic(2)+test_point(8)
  (statistics)

### Missed
- No power regulators detected despite board needing voltage regulation for nRF52 from battery/USB
  (signal_analysis.power_regulators)
- No BLE/wireless bus protocol detected for nRF52-based design
  (design_analysis.bus_analysis)

### Suggestions
- Investigate the 4-component BOM gap (30 missing vs 26 non-BOM types)
- Consider detecting wireless/BLE interfaces for nRF52 designs

---
