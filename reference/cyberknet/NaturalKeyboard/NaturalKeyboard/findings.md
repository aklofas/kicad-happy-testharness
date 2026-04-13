# Findings: cyberknet/NaturalKeyboard / NaturalKeyboard

## FND-00000986: ATmega32U4 keyboard correctly detected with crystal, RC filters, decoupling, and key matrix; Key matrix detects 95 switches on matrix but design has 109 keyboard switches

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: NaturalKeyboard.sch.json
- **Created**: 2026-03-23

### Correct
- Crystal circuit (Y1, 16MHz, C2/C4 22pF load caps) correctly detected with 14pF effective load. USB D- RC filter (R7 22R + C3 1uF, 7.23kHz) and reset RC filter (R1 10k + C1 100nF, 159Hz) correctly identified. Decoupling analysis shows 5 caps on +5V rail (10.4uF total). Key matrix 10x11 with 95 keys on matrix detected.

### Incorrect
- 109 keyboard switches (SW1-SW108 plus SWP1 push button) are present. The key matrix reports switches_on_matrix=95, missing 14 switches. Row nets are all __unnamed, suggesting that in this KiCad 5 design some rows connect switches via local wires without named nets, and the topology detector cannot resolve them all into the matrix. This is a real undercounting, though likely a KiCad 5 detection limitation.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000987: All 50 courtyard overlaps are SW+D pairs — intentional under-switch diode placement; Thermal pad via count correctly flagged as insufficient for ATmega32U4 QFN thermal pad; Board size DFM violation...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: NaturalKeyboard.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- U1 ATmega32U4-MU (QFN-44) has 6 standalone vias on its 5.2x5.2mm thermal pad, but analysis recommends 13 minimum and 21 ideal. Adequacy rated 'insufficient'. This is an accurate and actionable finding for thermal management.
- Large keyboard board correctly identified as exceeding JLCPCB standard 100x100mm threshold.

### Incorrect
- Every courtyard overlap is between SWxx and Dxx with matching numbers (e.g. SW99/D99), all with overlap_mm2=10.81 on B.Cu. This is the standard keyboard PCB design pattern where the 1N4148W diode is placed directly under/beside its corresponding switch in the same footprint courtyard. All 50 should be suppressed for keyboard designs.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
