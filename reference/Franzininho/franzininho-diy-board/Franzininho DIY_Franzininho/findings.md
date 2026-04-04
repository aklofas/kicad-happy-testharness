# Findings: franzininho-diy-board / Franzininho DIY_Franzininho

## FND-00002182: False positive: L78L05 regulator reports missing output caps (5V rail) even though C1 and C2 are present on it

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_franzininho-diy-board_Franzininho DIY_Franzininho.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The design_observation 'regulator_caps' reports missing_caps for both input (__unnamed_29) and output (5V) rails of U1 (L78L05_TO92). In reality, C1 (0.1uF) and C2 (10uF) are both connected between 5V and GND as proper output decoupling capacitors. The false positive arises because the Franzininho schematic was converted from Eagle and uses '#U$' prefixed power symbols (e.g., '#U$01') instead of the standard '#PWR' prefix. AnalysisContext.__post_init__ only searches for '#PWR' and '#FLG' to populate known_power_rails, so '5V' is never added. Without '5V' in known_power_rails, is_power_net_name('5V', set()) returns False (the bare '5V' name matches no hardcoded patterns), so detect_decoupling() skips the 5V rail entirely and decoupled_rails stays empty. This causes the regulator observation to incorrectly report missing output caps. The input rail __unnamed_29 genuinely lacks a capacitor.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002183: front_side=0, back_side=0, copper_layers_used=0 for a fully-routed KiCad 5 PCB using 'Top'/'Bottom' layer names

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_franzininho-diy-board_Franzininho DIY_Franzininho.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The Franzininho PCB is KiCad version 20171130 (KiCad 5.1) and uses 'Top' and 'Bottom' as copper layer names (layer numbers 0 and 31) instead of the post-standardization 'F.Cu'/'B.Cu'. compute_statistics() hardcodes front_copper='F.Cu' and back_copper='B.Cu' for front_side and back_side counts, so all 30 footprints (which use layer='Top') are reported as 'unknown' side and both counts are 0. copper_layers_used=0 and copper_layer_names=[] similarly. The PCB is fully routed with 157 track segments on 2 copper layers. This is a gap in the KH-043+044 fix: that fix used layer numbers for copper_layer_names but did not extend front_side/back_side to resolve 'Top'→0 and 'Bottom'→31 via the layers declaration map.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002184: Layer alignment flagged as misaligned due to silk/mask being smaller than copper — expected, not an error

- **Status**: confirmed
- **Analyzer**: gerber
- **Source**: gerber_franzininho-diy-board_Franzininho DIY_Gerber.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The gerber alignment check reports 'Width varies by 5.4mm across copper/edge layers' because B.Cu (50.3x29.2mm) and F.SilkS (50.7x29.3mm) differ from F.Cu (45.7x25.5mm) and B.Mask (45.7x25.5mm). The Edge.Cuts boundary is 51.1x30.0mm. Different layers having different extents is standard: F.Cu only contains component-side pads while B.Cu fills more of the board with ground pour. The alignment check is treating normal extent variation between layers as a potential alignment problem. This is not a genuine misalignment issue.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
