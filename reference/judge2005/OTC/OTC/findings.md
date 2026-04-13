# Findings: judge2005/OTC / OTC

## FND-00000964: Board height reported as 0.0mm due to circular outline mishandling; Courtyard overlaps correctly detected for densely packed components; Two ground domains (GND and GNDPWR) correctly identified wit...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: OTC.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Multiple courtyard overlaps reported (J1/R26, Rf1/Rsen1, C14/Rsen1, R26/R27, Cc1/Rsen1, R31/R32), consistent with a compact 70mm circular nixie clock board with high component density.
- GND domain (39 components) and GNDPWR domain correctly separated, with GND having copper zones on both layers. This reflects the deliberate HV/LV ground separation in a nixie tube power supply design.

### Incorrect
- The board has a circular Edge.Cuts outline (center 130,110; end 165,110; radius=35mm). The bounding box is computed with min_y=max_y=110 giving height=0.0mm and board_height_mm=0.0. The actual board is circular with diameter ~70mm. The DFM metrics also show board_height_mm=0.0. The analyzer needs to account for circular outlines when computing bounding boxes.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000965: K1 (MICROSWITCH lib_id, B3U-1100P footprint) misclassified as 'relay' instead of 'other' or 'switch'; Current sense resistor Rsen1 (0.04Ω, R_2010) not detected by current_sense detector; AO4294 (du...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: OTC.sch.json
- **Created**: 2026-03-23

### Correct
- The schematic parses all 4 sheets correctly: OTC.sch, ESP8285.sch, USB-UART.sch, HVPS_SMD.sch. Component counts, BOM grouping, and power rails (+3V3, +5V, GND, HT, VBus, VCC, etc.) all look accurate.
- Y1 (26MHz) crystal with C2 and C3 (12pF each) load capacitors is correctly detected. Effective load capacitance computed as 9pF which is reasonable.
- D1 (D_Schottky_Small) identified as reverse_polarity protection on VBus. U5 (ESD SOT143) identified as ESD protection on USB D+/D- lines. Both are accurate.

### Incorrect
- K1 has lib_id='MICROSWITCH', value='RST', and footprint 'nixiemisc-B3U-1100P(M)' which is an Omron tactile microswitch. The analyzer typed it as 'relay', which is wrong. It should be classified as 'other' or a dedicated 'switch' type. This causes the 'relay' count in statistics to be 1 instead of 0.
  (signal_analysis)
- The AO4294 is a complementary dual MOSFET (one N-channel + one P-channel in SO8). The analyzer reports is_pchannel=false, missing the P-channel half. Additionally gate_net and source_net appear to be the same net, suggesting the pin-to-role mapping may be off for this dual-FET package.
  (signal_analysis)
- U8 (LM3478SOIC8) is a boost (step-up) controller IC. The power_regulators entry lists topology='unknown'. The LM3478 is a well-known boost controller and should be detectable as such from its lib_id or value string.
  (signal_analysis)

### Missed
- Rsen1 is a 40mΩ shunt resistor in an R_2010 package, used in the LM3478-based high-voltage boost supply. The current_sense detector returned an empty list. This is a real current sensing element that should be detected.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000966: Gerber outputs do not exist for OTC repo — three gerber files referenced in review prompt are missing

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: OTC-gerbers.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- OTC-gerbers.json, OTC-gerbers_v2.json, and OTC-gerbers_v3.json were listed for review but no gerber output directory exists at results/outputs/gerber/OTC/. Either the gerbers were never generated or the repo has no gerber files.
  (signal_analysis)

### Suggestions
(none)

---
