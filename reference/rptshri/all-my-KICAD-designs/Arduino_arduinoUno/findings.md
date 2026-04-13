# Findings: rptshri/all-my-KICAD-designs / Arduino_arduinoUno

## FND-00002340: Power regulator entries have reference=null despite components having valid references; MJE2955T PNP power transistors (U12, U7, U8, U13) classified as ic instead of transistor; Current-boost topol...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_all-my-KICAD-designs_current_booster_power_supply_current_booster_power_supply.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The power_regulators array reports 4 entries (U1/U3/U4 LM317_3PinPackage, U6 AZ1117-ADJ) but each entry has reference: null rather than the actual component reference. The component list confirms these parts have valid references (U1, U3, U4, U6). The regulator detector is failing to populate the reference field when constructing the regulator record.
  (signal_analysis)
- Four MJE2955T PNP power transistors are referenced as U12, U7, U8, U13 (U-prefix used by the designer), causing the analyzer to classify them as 'ic' instead of 'transistor'. Their pin names (B, C, E) confirm they are BJTs. Because of the wrong type classification, they do not appear in transistor_circuits and the L7805 current-boost topology is missed entirely.
  (signal_analysis)

### Missed
- The design uses four MJE2955T PNP transistors as current-boost pass elements on the regulator outputs. Because the transistors are misclassified as 'ic', the analyzer cannot recognize the boosted-regulator topology. The transistor_circuits list is empty for this schematic, and no topology involving the BJT current boosters is reported.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002341: Correctly detected 99 THT footprints and 27 unrouted nets in an incomplete layout

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_all-my-KICAD-designs_current_booster_power_supply_current_booster_power_supply.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB has 99 footprints (all THT, 0 SMD), 0 tracks and 27 unrouted nets, accurately reflecting a partially laid-out design where components are placed but routing has not started. The copper_layers_used: 0 and routing_complete: false are both accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
