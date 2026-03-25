# Findings: PY32F002_ESSOP10_minimal_board / PY32F002_ESSOP10_minimal_board

## FND-00001099: Component counts, BOM, and net extraction are accurate; Decoupling analysis correctly detects C1 (10u) and C2 (100n) on VCC rail; SWD connector J3 (4-pin) correctly identified with VCC/GND/SWDIO/SW...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PY32F002_ESSOP10_minimal_board.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 10 total components (1R, 2C, 1LED, 1IC, 3 connectors, 1 jumper, 1 graphic), 12 nets, 2 power rails (VCC, GND) — all match expectations for this minimal board.
- signal_analysis.decoupling_analysis shows VCC rail with 10.1uF total (bulk + bypass). has_bulk and has_bypass both true; has_high_freq false is correct given only 100n and 10u caps.
- Pin 1=VCC, Pin 2=SWD/PA13, Pin 3=SWC/PB3/PA14, Pin 4=GND — exactly matches PY32F002A SWD pinout.

### Incorrect
- JP1 (SolderJumper_2_Open) has in_bom=false and exclude_from_bom=true, yet it does not appear in missing_mpn (correctly). However D1, R1, C1, C2, U1 appear in missing_mpn despite having LCSC numbers filled in (lcsc fields are populated). The missing_mpn list should arguably exclude parts that have at least one part number (LCSC) — this is a minor classification issue.
  (signal_analysis)

### Missed
- The J3 connector is clearly labeled 'SWD' and wired to U1 SWD/PA13 and SWC/PB3/PA14 pins, but bus_analysis has no SWD entry. The analyzer appears not to have a SWD protocol detector. Not a critical miss but noteworthy for debugging interfaces.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001100: Board dimensions, layer stack, footprint count, and routing completeness all accurate; DFM violation correctly flagged for annular ring 0.114mm below 0.125mm standard limit; Edge clearance of -7.61...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PY32F002_ESSOP10_minimal_board.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 11.176x16.256mm 2-layer board, 9 footprints (6 front, 3 back), 86 track segments, 7 vias, 12 nets, routing_complete=true. All match the design.
- All 7 vias have 0.5588mm outer/0.3302mm drill = 0.114mm annular ring. Standard limit is 0.125mm; advanced limit is 0.1mm. Correctly classified as 'advanced' tier requirement.
- Both 0402 decoupling capacitors have pad 1 on VCC and pad 2 on GND, correctly flagged as medium risk due to potential thermal asymmetry from ground pour.
- C2 at 5.3mm and C1 at 5.59mm from U1 — both on same side. Reasonable for a minimal board. Distances look geometrically plausible given the board is 11x16mm.

### Incorrect
- J3 (SWD header) is a through-hole 2.54mm connector placed at x=101.6, y=48.26 with the board starting at x=99.822. The courtyard min_x=92.21 extends well outside the board. This is by design — through-hole headers on the edge intentionally overhang. The -7.61mm warning is technically correct per the courtyard data but is a normal pattern for edge-mounted pin headers. The warning is not wrong per se, but could generate false-positive design concern.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
