# Findings: wntrblm/Micronova / hardware_board

## FND-00000916: U1 (VX7805-500) and U2 (P78E12-1000) both classified as topology=LDO instead of DC-DC switching converter; U3 (P78E12-1000, -12V output) completely absent from signal_analysis.power_regulators; LCF...

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_board_board.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- LC filter at 15.92 kHz detected correctly. Decoupling analysis correctly identifies caps on -12V, +5V, +15V, +12V rails. Fuse F1 and varistor TH1 detected as protection devices with correct net assignments.
- Statistics match the schematic structure. Missing MPN list (C2-C9, JP1) is accurate — these generic passives lack MPNs in the schematic properties.
- The design has PWR_FLAG symbols on only a subset of rails (connected to standalone PWR_FLAG net). The +15V, +VDC, and -12V rails genuinely lack PWR_FLAG coverage, so these warnings are accurate.

### Incorrect
- VX7805-500 and P78E12-1000 are CUI switching DC-DC converters, not LDOs. The regulator detector identifies them as LDO based on library name heuristics, which is wrong. These are buck/inverting switchers that accept a wide input range and generate regulated outputs.
  (signal_analysis)

### Missed
- U3 is a -12V DC-DC converter (P78E12-1000) visible in design_analysis.power_domains.ic_power_rails with rails [-12V, GND, __unnamed_5], but it is not listed in signal_analysis.power_regulators at all. The regulator detector likely only found U1 and U2 because U3 is the inverting negative-rail variant. This is a missed detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000917: pwr_flag_warnings falsely flags all 4 power rails on the bus board (a passive distribution board with no active components); Bus board component counts (11 total: 7 connectors + 4 mounting holes), ...

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_bus_board_bus_board.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Statistics accurately reflect the simple bus board design. All 7 Eurorack Power connectors and 4 mounting holes identified. Missing MPN list is empty (correct — all components have MPNs).

### Incorrect
- The bus board is purely a passive power distribution/splitter — it receives power from the main board and distributes it via connectors. There is no source of power on this board, so requiring PWR_FLAGs is an over-aggressive false positive. The GND warning is especially dubious since GND is inherently the reference.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000918: Board dimensions (100x30mm), 2-layer stackup, 55 footprints, routing complete, GND zones on both layers all correct; connectivity reports routed_nets=15 vs total_nets_with_pads=17, implying 2 unrou...

- **Status**: new
- **Analyzer**: pcb
- **Source**: hardware_board_board.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- All core PCB statistics are accurate. The 100x30mm Eurorack format board with rounded corners is properly captured. GND zone stitching with 160 vias on both F.Cu and B.Cu is correctly analyzed.
- The 0.51mm courtyard-to-edge clearance for Eurorack IDC connectors is expected design practice for tight Eurorack format PCBs where connectors extend to the board edge. These warnings are accurate observations, not false positives.

### Incorrect
- Nets 'unconnected-(J1-Pad3)' and 'unconnected-(J5-Pad3)' are intentionally unrouted barrel jack pin 3 (no-connect) pads. The analyzer counts them as unrouted but correctly sets routing_complete=true and unrouted_count=0, which is contradictory. The stat 'routed_nets=15' should not count these single-pad no-connect nets as unrouted.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000919: Bus board PCB (100x30mm, 14 footprints, GND zones on both layers, 49 stitching vias) all correctly analyzed

- **Status**: new
- **Analyzer**: pcb
- **Source**: hardware_bus_board_bus_board.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The 7 Eurorack power connectors, 4 mounting holes, GND copper pours on both layers, and via stitching are accurately captured. Power net routing for +12V and +5V with 1.5mm tracks is correctly reported.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000920: board_outline shows 0 edges and null bounding box for a faceplate PCB that clearly has defined dimensions (128.5mm x 20mm per dimension annotations); refs_visible_on_silk=9 is misleading — all 9 fo...

- **Status**: new
- **Analyzer**: pcb
- **Source**: hardware_front-entry-faceplate_faceplate.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The faceplate is a mechanical-only PCB. copper_layers_used=0, net_count=0, all 9 footprints flagged board_only=true are all accurate observations.

### Incorrect
- The faceplate has dimension annotations explicitly showing 128.5mm and 20mm, but the Edge.Cuts outline was not parsed (edge_count=0, bounding_box=null). This is a real missed Edge.Cuts detection — the board outline exists (confirmed by dimension text) but the parser failed to extract it.
  (signal_analysis)
- All footprints on the faceplate are pure graphics/mechanical holes with no reference designators (empty string). Reporting refs_visible_on_silk=9 implies 9 reference labels are visible on silkscreen, but these are actually just footprints with no reference text. This inflates the ref count metric.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
