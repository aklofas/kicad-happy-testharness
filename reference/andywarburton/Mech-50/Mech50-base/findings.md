# Findings: andywarburton/Mech-50 / Mech50-base

## FND-00000892: Mechanical-only schematic with 9 mounting holes correctly parsed

- **Status**: new
- **Analyzer**: schematic
- **Source**: Mech50-base_Mech50-base.sch.json
- **Created**: 2026-03-23

### Correct
- 9 MountingHole components, zero nets, zero signal analysis — all expected for a base plate schematic.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000893: 5x13 key matrix, 62 SK6812MINI addressable LEDs, Elite-C MCU all correctly detected; power_rails empty list is acceptable for KiCad 5 legacy keyboard schematic

- **Status**: new
- **Analyzer**: schematic
- **Source**: Mech50-keyboard_Mech50-keyboard.sch.json
- **Created**: 2026-03-23

### Correct
- 196 total components (62 switches, 62 diodes, 62 LEDs, 1 IC, 9 mounting holes), key_matrices entry with rows=5 cols=13 is accurate, addressable_led_chains detected for 62-LED SK6812MINI chain.
- The keyboard uses unnamed nets for power (no explicit PWR_FLAG/VCC symbols), so empty power_rails is correct behavior for this KiCad 5 format.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000894: Plate project reuses keyboard schematic — analyzer correctly parses the shared .sch file

- **Status**: new
- **Analyzer**: schematic
- **Source**: mech50-plate_Mech50-plate.sch.json
- **Created**: 2026-03-23

### Correct
- The mech50-plate project folder uses the same keyboard schematic (196 components). This is expected project structure; analyzer output is identical to keyboard schematic output, which is correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000895: Base PCB correctly analyzed as mechanical-only board with no copper routing

- **Status**: new
- **Analyzer**: pcb
- **Source**: Mech50-base_Mech50-base.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 10 footprints (9 mounting holes + 1 logo), 0 track segments, 0 vias, copper_layers_used=0, board size 256x96mm correctly extracted.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000896: missing_revision false positive: silkscreen text 'MECH / 50+3 / V 0.3' contains version 'V 0.3' but warning still fires; missing_switch_labels false positive: keyboard matrix switches don't need ON...

- **Status**: new
- **Analyzer**: pcb
- **Source**: Mech50-keyboard_Mech50-keyboard.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- PCB has 150 nets with 9 unrouted, correctly flagged as incomplete routing.

### Incorrect
- The board text 'MECH / 50+3 / V 0.3' clearly contains a version marker ('V 0.3'). The revision detector should recognize 'V 0.3' as a valid revision string but failed to match it.
  (signal_analysis)
- All 62 MX keyboard switches flagged as missing function labels. The 'missing_switch_labels' warning is intended for discrete push-buttons (reset, boot, power switches), not for keyboard matrix key switches. Firing for all 62 keys is pure noise for keyboard PCBs.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000897: Plate PCB correctly analyzed: 4 switch-cutout footprints, no routing, no copper

- **Status**: new
- **Analyzer**: pcb
- **Source**: mech50-plate_Mech50-plate.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 4 MX_Switch_Cutout footprints (all sharing ref S-A1 — duplicate refs in plate file), 0 tracks, 0 vias, copper_layers_used=0. Board outline via circles is correctly parsed.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000898: Base gerbers complete: 9 mounting holes in drill, 2-layer set, no copper content

- **Status**: new
- **Analyzer**: gerber
- **Source**: Mech50-base_mech50-base-gerbers.json
- **Created**: 2026-03-23

### Correct
- All expected layers present, 9 drill holes at 3.2004mm (M3 mounting), F.Cu and B.Cu are empty (correct for mechanical board), layer completeness=true.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000899: Alignment warning 'Height varies by 5.9mm' is a false positive for a fully-populated keyboard PCB; Keyboard gerbers: 1131 holes, 3611 flashes, 2-layer set complete

- **Status**: new
- **Analyzer**: gerber
- **Source**: Mech50-keyboard_mech50-keyboard-gerbers.json
- **Created**: 2026-03-23

### Correct
- All expected layers found, has_pth_drill=true, layer completeness=true. Drill count consistent with 62 THT switches + diodes + mounting holes.

### Incorrect
- The height difference between copper/paste extents and edge cuts extents is expected on a keyboard: SMD paste only covers LED pads (smaller area) while edge cuts span the full board. This is not a real alignment defect — the layers are correctly positioned, just have different content extents.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000900: Plate gerbers: no drill holes (correct for SMD switch-cutout footprints), layer set complete

- **Status**: new
- **Analyzer**: gerber
- **Source**: mech50-plate_mech50-plate-gerbers.json
- **Created**: 2026-03-23

### Correct
- All expected layers present, total_holes=0 is correct since MX_Switch_Cutout uses mask/copper flashes not drilled holes. Layer completeness=true.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
