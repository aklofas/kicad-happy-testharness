# Findings: JAMMA_2player_xbox360 / KiCAD_Jamma_rgbuntu_xbox360

## FND-00000652: SPK+/SPK- flagged as differential pair requiring ESD — false positive; USB_SHIELD flagged as cross-domain signal needing level shifter — false positive; USB D+/D- differential pairs correctly detec...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KiCAD_Jamma_rgbuntu_xbox360.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- PICO1_D+/PICO1_D- and PICO2_D+/PICO2_D- are correctly identified as differential pairs with ESD protection attributed to the Pi Pico (U1, U2) internal protection.
- The board is a purely passive passthrough adapter. Zero bus protocols detected is correct. 17 components + 56 no-connects reflect the heavily unconnected nature of the design.

### Incorrect
- differential_pairs includes SPK+ and SPK- as a 'differential' pair with 'has_esd: false', connecting JAMMA audio connector J8 and JAMMA edge connector J9. These are mono speaker connections on separate connectors, not a differential signal pair. The name matching on +/- suffix is over-broad.
  (signal_analysis)
- cross_domain_signals flags USB_SHIELD (shared between J1/U1 in USB_PICO1_VCC domain and J2/U2 in USB_PICO2_VCC domain) as needing a level shifter. USB_SHIELD is chassis ground/shield, not a logic signal — no level shifter is needed or appropriate.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000653: DFM correctly flags board size 125.7x77.0mm exceeding JLCPCB 100x100mm standard tier; PCB metrics correct: 23 footprints, 754 tracks, 28 vias, fully routed, 111 nets

- **Status**: new
- **Analyzer**: pcb
- **Source**: KiCAD_Jamma_rgbuntu_xbox360.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The board at 125.73x77.036mm correctly triggers the board_size DFM violation requiring a higher pricing tier. This is valid for a JAMMA edge connector board which must be a certain size.
- Net count (111) matches the schematic (111 total_nets). 22 front/1 back placement, 1 SMD/17 THT is plausible for a connector-heavy JAMMA board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
