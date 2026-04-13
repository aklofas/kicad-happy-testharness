# Findings: PTALTS-LK/RKD-OLD / PCB_stand+sdvx_MicroUSB_RKD

## FND-00001141: K1–K6 keyboard switches (lib_id=Key:Key) misclassified as 'relay' instead of 'switch'; Crystal frequency not extracted from value string 'Crystal 12MHZ HC49'; AMS1117-33 LDO regulator correctly ide...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RKD.kicad_sch
- **Created**: 2026-03-23

### Correct
- U4 correctly parsed from Regulator_Linear:AP1117-33 lib_id with estimated_vout=3.3 inferred from fixed_suffix. Power domain linkage VBUS->+3V3 is accurate.
- VBUS connects only to J1 (USB connector), C5 (decoupling), and U4 (LDO input). No ESD/TVS protection device present. Fail result is accurate. Consistent across all 4 variants.
- memory_interfaces section correctly identifies W25Q32JV (U1) connected to RP2040 (U2) with 6 shared signal nets. Subcircuits correctly groups these with their local passives.
- C3 and C4 (27pF each) on XIN/XOUT nets correctly associated with Y1. CL_eff calculation of 16.5pF is accurate: (27p||27p) + 3pF stray = 13.5 + 3 = 16.5pF.

### Incorrect
- All 6 'Key' components use lib_id='Key:Key' and reference prefix 'K', which triggers the relay classifier. They are MX-style keyboard switches. The statistics section reports 6 relays and 6 switches, overcounting switches as relays. Consistent across all 4 schematic variants.
  (signal_analysis)
- Y1 has value='Crystal 12MHZ HC49' which contains the frequency '12MHZ' in plain text, but crystal_circuits reports frequency=null. The analyzer should parse MHz/kHz patterns from the value string. Affects all 4 schematic variants (all have the same crystal).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001142: USB Type-C CC1/CC2 5.1k pull-down resistors correctly detected as pass in Type-C variants

- **Status**: new
- **Analyzer**: schematic
- **Source**: PCB_stand+sdvx_Type-C_RKD.kicad_sch
- **Created**: 2026-03-23

### Correct
- Both Type-C variants report cc1_pulldown_5k1=pass and cc2_pulldown_5k1=pass, which is correct for a USB device-side Type-C implementation. MicroUSB variants correctly omit these checks.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001143: Zone count of 417 is unusual but reflects real design: per-signal copper fills across all signal nets; Many courtyard overlaps are likely real design issues from a crowded custom PCB, but some smal...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: RKD.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Zone analysis shows 49 zones on +3V3 alone, with fills across most signal nets on both F.Cu and B.Cu. This keyboard PCB uses copper pours for virtually every net rather than just power planes, which is verified from zone net distribution data.
- Min track width 0.15mm, min drill 0.3mm, min annular ring 0.2mm — all within standard fab capabilities. Consistent across all 4 PCB variants.
- All 4 PCB files show routing_complete=True with unrouted_count=0. This matches the keyboard controller design which is a finished production board.

### Incorrect
- 32 overlaps detected. Large overlaps (SW5 vs SW2 at 49.6mm2, J2 vs J14 at 27.8mm2) appear to be genuine design issues on this custom keyboard board. However, very small overlaps like C7 vs C11 (0.017mm2), C1 vs C2 (0.014mm2), R16 vs D3 (0.009mm2) are suspiciously small and may be numerical precision artifacts from courtyard polygon calculations rather than real overlaps.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
