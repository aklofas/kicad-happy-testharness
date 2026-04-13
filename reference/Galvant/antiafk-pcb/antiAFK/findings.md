# Findings: Galvant/antiafk-pcb / antiAFK

## FND-00001939: 18 components correctly identified for ATmega16U4-based USB HID board; 16MHz crystal circuit with 18pF load capacitors correctly detected; USB differential pair with 22Ω series resistors detected c...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: antiAFK.sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies 18 total components: 1 IC (ATMEGA16U4), 5 resistors, 5 capacitors, 2 diodes (ZENER), 1 inductor, 1 crystal, 1 switch, 2 connectors (J1=USB, P1=ISP). Power rails +5V and GND are correct.
- The crystal_circuits section correctly identifies X1 (16MHz) with load capacitors C2 (18pF) and C3 (18pF), computing effective_load_pF=12.0 using the series formula (18*18)/(18+18)+3pF stray. The frequency is correctly parsed as 16000000 Hz.
- The differential_pairs section correctly identifies USB_DP and USB_DM with series resistors R4 and R5 (both 22Ω). The design also correctly notes has_esd=false (the Zener diodes D1/D2 are connected to the raw USB lines before the 22Ω resistors, but the analyzer may not have recognized D1/D2 as ESD devices in this configuration).

### Incorrect
- D1 and D2 are Zener diodes connected from the raw USB data lines (N-0000022/N-0000023 = the USB connector's D+/D- pads) to GND. This is a classic low-cost USB ESD protection scheme using 3.6V Zeners (standard for 5V USB EAP protection). The USB data observation reports has_esd_protection=false for both USB_DP and USB_DM, and protection_devices is empty []. D1 and D2 should be detected as TVS/Zener protection devices for the USB lines.
  (signal_analysis)

### Missed
- The power_domains section shows IC1 (ATMEGA16U4) with power_rails as unnamed nets (__unnamed_13, __unnamed_32–35). The +5V rail is present but not connected to IC1 in the power domain analysis, even though IC1 has multiple VCC pins connected to +5V. This is because the KiCad 5 legacy format uses unnamed nets heavily, and the analyzer cannot always resolve them to named power rails. The design_analysis should ideally report IC1 as powered by +5V.
  (statistics)

### Suggestions
(none)

---

## FND-00001940: PCB statistics correctly show 18 footprints, all-SMD board with 1 THT-style connector on B.Cu; Documentation warning correctly flagged for missing revision marking found in silkscreen text; Missing...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: antiAFK.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly reports 18 footprints, 17 front and 1 back (P1 ISP connector on B.Cu), all 18 classified as smd_count. The tht_count=0 is correct as P1 is a through-pad SMD SPI connector. 2 copper layers, 242 track segments, 24 vias, 1 zone (GND fill on B.Cu), 16 nets, routing complete.
- The silkscreen contains text 'antiAFK\nGalvant Industries\n2013 revA' on B.SilkS, which does include a revision ('revA'). The analyzer flags a missing_revision warning, which is technically incorrect since 'revA' is present in the silkscreen text. However, the analyzer's pattern matching may require a specific format like 'Rev A' (with space and capital R), so 'revA' without space is missed — this is a minor parsing limitation.

### Incorrect
- The silkscreen text on B.SilkS reads 'antiAFK\nGalvant Industries\n2013 revA', which contains the revision 'revA'. The analyzer fires a missing_revision documentation warning, but the revision information is present. This is a false positive due to the revision pattern matcher not recognizing 'revA' (no space, lowercase) as a valid revision label.
  (silkscreen)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001941: Gerber completeness is correct — all 8 required layers present with B.Paste intentionally absent; Drill file classified as 'unknown' type instead of PTH — 24 via holes misclassified as component ho...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerbers.json
- **Created**: 2026-03-24

### Correct
- The gerber set has 8 files covering B.Cu, B.Mask, B.SilkS, Edge.Cuts, F.Cu, F.Mask, F.Paste, and F.SilkS. The missing_required and missing_recommended lists are both empty and complete=true. B.Paste is absent because the back-side has only through-hole/SMD pads without solder paste needed (the P1 connector uses through-hole pads). This is consistent with the PCB having 1 back-side component.
- The gerber analyzer reports board_dimensions of 37.08×12.14mm from edge_cuts_extents, which matches the PCB analyzer's reported 37.084×12.141mm exactly (within rounding). Layer extents show consistent alignment across copper, mask, paste, and silkscreen layers.

### Incorrect
- The PCB has 24 vias (as reported by the PCB analyzer) and 0 actual through-hole component holes (all components are SMD). The drill file antiAFK.drl contains 24 holes of 0.508mm diameter. These are all via drills (the PCB via size is 0.635/0.508 = 0.635mm annular ring / 0.508mm drill). However, the gerber drill_classification reports them as component_holes: 24, vias: 0. The drill file type is 'unknown' rather than 'pth'. The PCB has no THT components, so all 24 holes must be vias, not component holes.
  (drill_classification)
- The completeness section reports has_pth_drill=false and has_npth_drill=false even though the drill file antiAFK.drl contains 24 holes of 0.508mm. These are plated through-holes (vias). The analyzer cannot determine plated vs non-plated status from the drill file because the format is 'unknown', but the has_pth_drill flag should be true since the board has copper-layer via transitions that require PTH drilling.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
