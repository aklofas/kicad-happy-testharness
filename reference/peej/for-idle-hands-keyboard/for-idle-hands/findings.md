# Findings: for-idle-hands-keyboard / for-idle-hands

## FND-00002069: KEYSW keyboard switches misclassified as relay type; Key matrix reports switches_on_matrix=0 due to KEYSW misclassification as relay

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_for-idle-hands-keyboard_for-idle-hands.sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The 12 key switch components (K1:1, K1:2, K2:1, K2:2, K3:1–K3:4, K4:1–K4:4) use the KiCad 5 library part 'KEYSW' with reference prefix 'K'. In kicad_utils.py, 'K' maps to 'relay' in the type_map. The relay override at line 404–410 only converts relay→switch for 'mx', 'cherry', 'kailh', 'gateron', 'alps_hybrid', and 'key_switch' substrings in lib_lower. The library name 'keysw' does not match any of these patterns. The PCB footprints confirm these are Cherry MX-compatible keyboard switch cutouts (idle-hands:MX_CUTOUT). Fix: add 'keysw' to the relay→switch override list in detect_component_type.
  (statistics)
- The key_matrix detection found a 4-row × 6-column matrix via net name heuristics (row1–row4, col1–col6) with estimated_keys=12 (from diode count) and switches_on_matrix=0. The 12 physical key switches are present (KEYSW footprints idle-hands:MX_CUTOUT) but since they are typed as 'relay' rather than 'switch', the switch counting step skips them. This is a downstream consequence of the KEYSW→relay misclassification above. If correctly typed as 'switch', switches_on_matrix would equal 12.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002070: DFM advanced-tier correctly flagged for tight annular ring (0.1 mm)

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_for-idle-hands-keyboard_for-idle-hands.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB analysis correctly detects that the minimum annular ring of 0.1 mm requires advanced fabrication process (standard tier requires ≥ 0.125 mm, advanced tier limit is 0.1 mm). The dfm_tier is set to 'advanced' with a clear violation message. Board dimensions are 76.2×76.2 mm, within standard size limits, so no size violation is raised — correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
