# Findings: samlee91/keebs / CustomKeyboard_1_CustomKeyboard

## FND-00002230: 90 keyboard key switches (keyboard_parts:KEYSW) misclassified as 'relay' in component statistics; Key matrix reports switches_on_matrix=0 due to key switches being misclassified as relays

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_keebs_CustomKeyboard_1_CustomKeyboard.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- In the legacy KiCad 5 schematic, 90 key switch components with references K_* and lib_id keyboard_parts:KEYSW are classified as type 'relay' (visible in both statistics.component_types and the per-component 'type' field). The part uses a two-pin relay symbol shape in the library, which triggers the relay classifier. These are clearly MX-socket keyboard switches, not relays. This cascades into key_matrix detection reporting switches_on_matrix=0 even though 90 switches exist.
  (statistics)
- The key_matrices detector correctly identifies the 7×18 matrix from row/col net names and finds 90 diodes on the matrix. However, switches_on_matrix=0 because the 90 K_* components have type='relay' rather than 'switch', so the key matrix scanner does not count them as switches. The matrix relies on net-name detection for its existence but cannot correlate switches to it. The estimated_keys=90 is correct but switch_count reporting is wrong.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002231: Gerber set correctly identified as complete and aligned for a large full-size keyboard PCB

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber_keebs_CustomKeyboard_1_Gerber Files.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies all 9 expected layers (F.Cu, B.Cu, F/B.Mask, F/B.Paste, F/B.SilkS, Edge.Cuts), finds both PTH and NPTH drill files, and confirms alignment is good. Board dimensions (352.5mm × 128.7mm) match the expected full-size keyboard form factor. The DFM violation for board_size (>100mm) is correctly flagged for this large board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
