# Findings: PlummersSoftwareLLC/PongPCB / Pong

## FND-00001118: Crystal circuit detection correct: Y1 2MHz with 30pF load caps; ERC no_driver warnings for control panel connector pins (SPEED, BATSIZE, RESET, PRACTICE, SOCCER, TENNIS) are correct; Decoupling obs...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Pong.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Correctly identifies Y1 with C1 and C2 (both 30pF) as load caps, effective CL=18pF, in typical range.
- Control panel connector J2 (14-pin Molex) drives AY-3-8500 input pins through named nets. These pins have no active driver in the schematic (connector passive pins drive IC inputs), which KiCad ERC would flag. Accurate observation.
- All three ICs draw from VCC rail with no decoupling caps placed. This is a real design gap correctly identified.

### Incorrect
- The analyzer reports Q1 collector is on GND (collector_is_power=True). PCB confirms pin 3 (C) is on GND. For a 2N3904 NPN with collector at GND, this is an unusual topology — the transistor may be driving audio output from emitter with collector grounded (common-collector but in reverse sense). The analyzer correctly reports what the schematic shows; however the load_type='connector' and emitter-to-audio-jack path suggests this may be a sound output driver. The collector-to-GND needs scrutiny to confirm it is not a symbol wiring error in the original design.
  (signal_analysis)

### Missed
- Unlike Pong-1976 which has an LM7805, PongPCB has no regulator. The design uses VCC directly from the barrel jack. The analyzer correctly outputs zero power_regulators. However, it also produces no power_budget warning about unregulated VCC driving the AY-3-8500 — that observation would be useful.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001119: PCB stats correct: 26 footprints all THT, 2-layer, 42 nets, fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: Pong.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- footprint_count=26 matches schematic, all THT (no SMD - as expected for vintage-style Pong clone), routing_complete=True, 6 vias. Net count 42 vs schematic 41 is a minor +1 from the unconnected net tracking.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001120: Layer completeness correct: all 9 expected layers present, PTH and NPTH drill files present; Alignment flagged as failed (width varies 27.9mm, height 58.4mm) — false positive; Drill tool classifica...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerbers 1.02.json
- **Created**: 2026-03-23

### Correct
- 2-layer board with complete Gerber set. 111 component holes + 6 via holes + 2 NPTH mounting holes. All layer files match gbrjob expected list. 100% complete.
- x2_attributes used for classification. Via size 0.3988mm consistent with PCB via_count=6. Component hole sizes (0.65, 0.75, 0.80, 1.00, 1.19mm) appropriate for THT through-hole parts. NPTH 1.6mm for mounting holes. All accurate.

### Incorrect
- B.Paste, F.Paste, and B.SilkS are empty (0x0 extent) because all components are THT with no SMD pads and no back silk. The alignment checker compares these 0x0 empty layers against the 142x124mm board outline, producing spurious variation. Real copper (F.Cu, B.Cu: 114x66mm) is smaller than the board outline because components are in the center of a larger PCB — this is valid layout, not misalignment. The analyzer should exclude empty layers (0x0 extent) from alignment calculations.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
