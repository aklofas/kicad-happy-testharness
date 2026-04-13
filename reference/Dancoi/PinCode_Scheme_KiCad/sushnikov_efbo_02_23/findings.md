# Findings: Dancoi/PinCode_Scheme_KiCad / sushnikov_efbo_02_23

## FND-00001104: Component extraction correct: 15 parts (9R, 2 LED, 2 IC, 1 DIP switch, 1 rotary encoder); STM32F407 misidentified as 'power_regulators' with topology 'ic_with_internal_regulator'; No decoupling cap...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: sushnikov_efbo_02_23.kicad_sch
- **Created**: 2026-03-23

### Correct
- STM32F407VGTx (U1), LTC-4627JD 7-segment display (U2), 9 current-limiting resistors, 2 LEDs, SW1 (DIP), SW2 (rotary encoder). All correctly identified.

### Incorrect
- signal_analysis.power_regulators includes U1 (STM32F407VGTx) as 'ic_with_internal_regulator'. The STM32F407 does have an internal voltage regulator (LDO for core from VDD), but listing a microcontroller as a power_regulator is misleading and a false positive. This appears to be over-triggering on the internal LDO heuristic for all STM32 parts.
  (signal_analysis)
- connectivity_issues.unconnected_pins=[] but there are ~80+ single-pin nets (NRST, BOOT0, VREF+, PH0, PH1, plus many PE/PA/PB GPIO pins) in the nets section with point_count=1. These are GPIO pins left unconnected but not marked with no-connect markers — they should appear as unconnected pin warnings. The 82 no_connects in the schematic are X markers placed but only on some pins; the rest show up as single-pin nets.
  (signal_analysis)

### Missed
- The STM32F407VGTx has multiple VDD pins (11, 19, 28, 50, 75, 100), VDDA, VBAT, and VREF+, all without any decoupling caps connected. design_observations correctly notes rails_without_caps=['+3.3V'], but the schematic appears to be a partial/early-stage design with no decoupling at all. The observation is correct but the total_nets=110 with 82 no-connects and no caps is a significant design concern that should be flagged more prominently.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001105: Empty PCB correctly parsed: 0 footprints, 0 tracks, 0 nets, null board dimensions

- **Status**: new
- **Analyzer**: pcb
- **Source**: sushnikov_efbo_02_23.kicad_pcb
- **Created**: 2026-03-23

### Correct
- The .kicad_pcb file is a blank project file with no layout data. All counts are 0/null as expected. routing_complete=true is technically correct (nothing to route).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
