# Findings: reza-huss/Pin_Tester / Pin_Test

## FND-00001114: Component count and types correct: 61 components (26 LEDs, 26 resistors, 9 connectors); False positive differential pair M0+/M0- on J8 connector; Single-pin nets correctly flagged: 10 nets with iso...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Pin_Test.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- BOM extraction accurate. Missing MPN flag correct — all parts lack MPN fields. No complex circuits detected (correct — design is only LEDs+resistors+connectors).
- Nets C4, C6, C8, C10, C12, C14, C16, C18, C20, VM+ each have only one schematic pin. The LED cathodes connect to the test connector (J8/J1) physically but the schematic net routing leaves some stubs. Correctly reported.
- VCC is supplied by J2 (battery connector) and no PWR_FLAG symbol placed; ERC would flag this. Correct observation.

### Incorrect
- Analyzer detects {'type':'differential','positive':'M0+','negative':'M0-','shared_ics':['J8']} but M0+/M0- are test connector pin labels on a pin tester, not an active differential signal pair. J8 is a passive connector with LED cathodes. The +/- naming convention in the detector fires on arbitrary net names.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001115: PCB stats correct: 61 footprints (54 SMD + 7 THT), 2-layer, fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: Pin_Test.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- footprint_count=61 matches schematic, smd_count=54 (LEDs and resistors in 0603), tht_count=7 (connectors), routing_complete=True, 12 vias. All accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
