# Findings: kicad-designs / 4drum_4drum

## FND-00002245: total_components=7 for a 31-component unannotated schematic; False positive I2C detection on TRIG1/TRIG2 connector nets

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-designs_4drum_4drum.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The schematic has 31 non-power symbol instances (RV?×4, R?×14, D?×5, J?×5, SW?×1, Q?×1, U?×1), but statistics.total_components reports 7 — the number of unique unannotated reference groups (D?, J?, Q?, R?, RV?, SW?, U?). The analyzer deduplicates by reference string, collapsing all 'R?' instances into one, making the board appear to have only 7 parts. The true count is 31. This also causes component_types to undercount: resistor:2 instead of 14, led:1 instead of 5, etc.
  (statistics)
- design_analysis.bus_analysis reports 6 I2C entries including TRIG1 (as SCL) and TRIG2 (as SDA). These are trigger signal names on connector pins J?/TRIG1-4, not I2C bus lines. The Teensy 4.1 does have I2C pins named SDA/SCL in its KiCad library, but the matching is done against net names containing the pin names rather than confirming both a controller and peripheral IC are present on the same net pair. With all refs unannotated (U?), there is no confirmed I2C topology — just coincidental pin name matches.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002246: Opamp circuit analysis correctly identifies 13 TL074/opamp unit configurations

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematic_kicad-designs_AS3363_ASVCA_ASVCA.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The design uses U1 (AS3363 VCA), U2-U4 (TL074 quad opamps) for signal conditioning in an audio VCA/VCF board. The analyzer correctly identifies 13 opamp units across U2-U4, correctly classifies most as 'buffer' (unity gain, inverting tied to output), and flags the power unit (U2 unit 5) as 'unknown' since the TL074 power pins are a special unit. Voltage divider detection also correctly identifies the R1/R3 voltage reference divider on +12V rail.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002247: Gerber alignment false positive: silkscreen extent drives misalignment report

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_kicad-designs_AS3363_ASVCA_gerber_control.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- alignment.aligned is false with 'Width varies by 7.1mm across copper/edge layers'. The discrepancy comes from comparing F.SilkS (37.698mm wide) against F.Cu (31.498mm). Silkscreen graphics and text routinely extend beyond the copper keepout region and even beyond the board edge — this is normal and expected. The analyzer should exclude paste/silkscreen layers from the copper-vs-edge alignment check, or at minimum not count zero-size layers (B.Paste: 0, B.SilkS: 0) in the variance calculation. The same false positive appears in bindec_gerber-bindec.json.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002248: Correctly reports empty PCB layout (version 20211014, no footprints placed)

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad-designs_4drum_4drum.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The 4drum.kicad_pcb file is a stub: it has the KiCad 6 format header (version 20211014) but contains only '(kicad_pcb (version 20211014) (generator pcbnew))' with no footprints, nets, or board outline. The analyzer correctly reports footprint_count=0, net_count=0, board_width/height=null, and routing_complete=true (vacuously). kicad_version is reported as 'unknown' since version 20211014 was not matched to a specific release.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002249: Correctly identifies missing +5V decoupling: no caps actually connect to +5V rail

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematic_kicad-designs_bindec_bindec.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- design_analysis reports rails_without_caps: ['+5V'] for U1 (L7805), U2 (4029), and U3 (ICM7555). Inspection of the nets confirms this: C1-C5 are all connected between GND and unnamed nets (__unnamed_1, __unnamed_3, __unnamed_9, etc.) — none actually tie to the +5V rail. C1 (22µF) connects to the L7805 input rail (__unnamed_3) and GND, which is the input cap, not the output. The +5V rail genuinely lacks bypass capacitors, making this a real finding, not a false positive.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
