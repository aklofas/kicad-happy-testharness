# Findings: Jana-Marie/ligra / ligra_back

## FND-00002382: NCP1117-12 output voltage estimated as 1.2V instead of 12V due to suffix parsing bug; Power regulator topology correctly identified: AL8843 switching regulator + two NCP1117 LDOs detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_ligra_ligra_back_ligra_back.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The design powers a 12V LED strip (via AL8843 boost/LED driver from VBUS), provides +12V via NCP1117-12 LDO, and +3V3 via NCP1117-3.3 LDO. All three regulators are correctly detected with their topologies (switching vs LDO), inductor association (L1 with U2), input rail (VBUS), and output rails. The STM32F030F4Px microcontroller (U7) and DRV8231 motor driver (U8) are also identified.

### Incorrect
- U4 is an NCP1117-12_SOT223, a fixed 12V LDO regulator. The analyzer extracts '12' from the part name suffix and interprets it as 1.2 (decimal) rather than 12V. This triggers a spurious vout_net_mismatch observation reporting 90% error between estimated 1.2V and the net name '+12V' (correctly identified as 12V). The NCP1117-3.3 (U5) is parsed correctly at 3.3V, so the bug is specific to multi-digit integer suffixes like '12' that are not decimal fractions.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002383: Thermal pad via stitching correctly detected for U2 (AL8843) and U8 (DRV8231) exposed pads

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_ligra_ligra_back_ligra_back.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Both U2 and U8 are power ICs with large exposed thermal pads (~9mm2). The analyzer correctly identifies nearby thermal vias (15 for U2, 19 for U8) connected to GND, consistent with standard thermal relief practice. The GND zone stitching shows 212 vias with 1.6 via/cm2 density across the board, which is appropriate for a motor/LED driver design handling non-trivial currents.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002384: Mechanical mounting plate PCB (no routing) correctly parsed without errors

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_ligra_ligra_front_ligra_front.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- ligra_front is a mechanical/mounting plate PCB containing only 4 connector footprints (J1-J4), 2 logos (G***), no tracks, no vias, and no copper zones. The analyzer correctly reports copper_layers_used=0, track_segments=0, via_count=0, routing_complete=true, and unrouted_net_count=0. This is valid for a board-only mechanical part that uses only the Edge.Cuts outline and has no electrical connections beyond GND.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
