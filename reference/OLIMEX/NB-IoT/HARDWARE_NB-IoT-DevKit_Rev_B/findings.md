# Findings: NB-IoT / HARDWARE_NB-IoT-DevKit_Rev_B_NB-IoT-DevKit_Rev_B

## FND-00001008: SIM card holder SIM1 classified as 'switch' instead of 'connector'; IT1185AU2 tact switches (PWR_KEY1, RST_KEY1) classified as 'connector' instead of 'switch'; Jumper components (SJ footprints) cla...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: NB-IoT-DevKit_Rev_B.sch
- **Created**: 2026-03-23

### Correct
- AP1231-1.8V has VOUT (pin 5) connected to GND and VIN (pin 1) connected to VDD_1.8V — a backwards connection. The analyzer faithfully reports output_rail=GND which matches the netlist, accurately exposing a schematic/library symbol error.
- Q1 12MHz crystal with C8/C11 (27pF each) correctly identified as a crystal circuit. Effective load capacitance 16.5pF is a reasonable series calculation. Detected consistently across all revisions.
- I2C0_SCL(EINT) and I2C0_SDA(EINT) correctly detected with 1.5k pull-ups to +1.8V via R19/R20 connecting U4 (PCA9306) and U6 (BC66). Bus analysis is accurate.
- USB_D+ and USB_D- correctly identified as USB differential pair on USB-UART1. The design_observations correctly note has_esd_protection=false for the USB data lines, which is accurate (no TVS/ESD diode present).
- C2 (22uF/6.3V X5R) on the +5V rail has <50% voltage derating margin. The warning is valid — best practice requires 2x derating for electrolytic/ceramic caps. Consistent across all revisions.
- D1 (1N5819 Schottky) on +5V_EXT→+5V is correctly identified as reverse polarity protection. D2-D5 are also Schottky diodes in other circuit contexts (flyback protection, etc.) and are not flagged as primary protection devices — this appears contextually correct.

### Incorrect
- SIM-SMT-6P (NASCT-W0012X-06-LF) is a nano SIM card connector/holder. The analyzer classifies it as 'switch' (type: switch in BOM). This is wrong — it is a connector. Reproduced in Rev B, Rev C, and Rev D.
  (signal_analysis)
- IT1185AU2 is a tactile push-button switch. The analyzer classifies both PWR_KEY1 and RST_KEY1 as 'connector' type in the BOM. Should be 'switch'. Reproduced in Rev B, C, and D.
  (signal_analysis)
- 3.3V/VCCB1, 3.3V_E1, Start_E1 are solder jumpers. In Rev B they appear as type 'other' (3 items) while Rev C correctly classifies them as type 'jumper'. The divergence is inconsistent and likely depends on lib_id substring matching changing between revisions.
  (signal_analysis)
- The analyzer correctly reads pin 4 (IN) of U1 SY8089AAAC as connected to GND net. This is a schematic/library error (custom lib symbol has incorrect pin mapping). The analyzer faithfully reports input_rail=null rather than the expected +5V or VBAT — this is an accurate reflection of a schematic anomaly, not an analyzer bug.
  (signal_analysis)

### Missed
- rf_chains=[] and rf_matching=[] for a design with a Quectel BC66 NB-IoT module (U6) connected to an ANT1 U.FL connector through L3 (0R jumper) and optional capacitors C13/C14 (NA). Even a minimal pass-through antenna path should trigger rf_chains detection. Reproduced across all three main revisions.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001009: Extension board (7 connectors, no power except GND) correctly parsed with all components flagged as missing MPN and footprint

- **Status**: new
- **Analyzer**: schematic
- **Source**: HARDWARE_NB-IoT-DevKit_Rev_C_Extensions_Extension_Rev_B_Extension_Rev_B.sch
- **Created**: 2026-03-23

### Correct
- Extension_Rev_B.sch is a breakout schematic with unnamed connector values and no footprints assigned. The analyzer correctly reports all 7 components as missing_mpn and missing_footprint, and identifies only the GND power rail.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001010: 4-layer board (F.Cu/In1.Cu/In2.Cu/B.Cu) with 116 footprints, 203 vias, fully routed, correctly detected; DFM tier correctly classified as 'advanced' for 0.127mm min track spacing

- **Status**: new
- **Analyzer**: pcb
- **Source**: NB-IoT-DevKit_Rev_B.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Board stats are accurate: 25.4x40.64mm, 4 copper layers with inner planes, routing_complete=true, smd_count=115 vs tht_count=0 consistent with an all-SMD design. Board metadata (title, rev, company) correctly extracted.
- Min track width 0.127mm is at the boundary of advanced fabrication. The DFM tier='advanced' classification is accurate and appropriate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001011: Placeholder/stub PCB file (51-byte dummy) correctly parsed as zero-footprint board without crashing

- **Status**: new
- **Analyzer**: pcb
- **Source**: HARDWARE_NB-IoT-DevKit_Rev_C_Extensions_Extension_Rev_B_Extension_Rev_B.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Extension_Rev_B.kicad_pcb is a KiCad 'dummy file' placeholder (version 4, host=dummy). The analyzer gracefully returns all-zero statistics rather than crashing. This is correct behavior for a stub file.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001012: Gerber set is complete (11 layers + 2 drill files) with all required layers present; Gerber alignment false positive: F.Cu extent reported as 71.12mm wide but raw coordinates span 179mm; alignment ...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerbers
- **Created**: 2026-03-23

### Correct
- All 4 copper layers (F.Cu, B.Cu, In1.Cu, In2.Cu), all mask/paste/silk layers, edge cuts, and both PTH/NPTH drill files are present. completeness.complete=true is accurate.
- 203 vias at 0.399mm diameter, 29 PTH component holes at 1.001mm, 8 NPTH holes correctly identified. The PCB output also reports 203 vias confirming consistency across analyzers.

### Incorrect
- The F.Cu gerber genuinely contains data outside the board outline (the board is 25.4mm wide but F.Cu raw X coordinates span 0–179mm, including Quectel module courtyard regions). The aligned=false flag is correct. However, the reported F.Cu width of 71.12mm is inconsistent with the actual 179mm raw coordinate span — the analyzer appears to compute extents from flash positions only, missing draw commands, leading to an underestimated but still-outside-bounds width. The F.Mask has raw span 0–155mm vs reported 22.878mm, confirming the same undercount pattern. The alignment decision is correct but the extent values are inaccurate.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001013: Rev C gerbers correctly detected as 4-layer complete set with same board dimensions as Rev B

- **Status**: new
- **Analyzer**: gerber
- **Source**: HARDWARE_NB-IoT-DevKit_Rev_C_Gerbers
- **Created**: 2026-03-23

### Correct
- Rev C Gerbers: 11 gerber files + 2 drill files, 4 copper layers, 25.4x40.64mm board, all required layers present. Alignment false positive is identical to Rev B (F.Cu over-extends), consistent across revisions.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001014: Rev D gerbers generated by KiCad 5.1.6 correctly parsed; generator version difference captured

- **Status**: new
- **Analyzer**: gerber
- **Source**: HARDWARE_NB-IoT-DevKit_Rev_D_Gerbers
- **Created**: 2026-03-23

### Correct
- Rev D gerbers come from KiCad 5.1.6 while Rev B/C use KiCad 6.0.0-unknown. The generator field is correctly captured. The board dimensions and layer structure are identical to previous revisions. Total hole count (237 vs 242 in Rev B) is a real difference correctly captured.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
