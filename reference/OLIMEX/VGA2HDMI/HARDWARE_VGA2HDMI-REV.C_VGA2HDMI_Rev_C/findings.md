# Findings: OLIMEX/VGA2HDMI / HARDWARE_VGA2HDMI-REV.C_VGA2HDMI_Rev_C

## FND-00001786: Total component count (86 unique refs) is accurate; HDMI interface detected correctly; Crystal circuit detected (Q1 = 24.576 MHz quartz crystal); VGA RGB RC high-pass filters correctly identified; ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: VGA2HDMI_Rev_C.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The schematic contains 86 unique reference designators. Multi-unit symbols (e.g., R12 × 4, CHARGING1 × 3, L4 × 2) appear multiple times in the components list but are correctly de-duplicated to 86 in statistics.total_components.
- The schematic contains HDMI_OUT1 (HDMI-SWM-19 connector) which is correctly detected as an HDMI interface.
- Q1 uses the OLIMEX_Devices:Crystal library and has value 'Q24.576MHz/20pF/20ppm/2P/5x3.2mm'. The analyzer correctly identifies it as a crystal with load capacitors C18 and C19 (33 pF each), calculating 19.5 pF effective load within typical range.
- Three identical RC high-pass networks (R=75Ω, C=47nF, fc=45.15 kHz) on RED_IN, GREEN_IN, BLUE_IN are correctly detected. These are DC-blocking/termination networks for VGA analog signals.
- VR1 LD1117AG-33 is correctly identified as a fixed 3.3V LDO with +5V_USB input and +3.3V output, voltage inferred from the '-33' suffix.
- VR2 LD1117AG-AD is an adjustable LDO. With R29=220Ω (output to ADJ) and R26=100Ω (ADJ to GND), Vout = 1.25×(1+220/100) = 4.0V, but the net is named +1.8V. The analyzer correctly flags a 122% mismatch. This appears to be a real design error or a net naming mistake in the VGA2HDMI schematic.

### Incorrect
- Three LED components (CHARGING1 × 3, UUIDs: 54065cbc, 67a1df4e, d1aea1fe) all share the reference CHARGING1 in the schematic. De-duplication by reference yields led=1 in statistics, but there are 3 distinct placed instances (confirmed by matching PCB footprints LED_VGA1, LED_PWR1, LED_HDMI1 linking to the same 3 UUIDs). This is a schematic design error (duplicate refs), but the count underreports actual LEDs.
  (statistics)
- Two inductor symbols both named L4 (UUIDs 5ce7ffe1 and b40318a9) appear in the schematic, both with unit=1 (not different units of a single multi-unit component). The PCB assigns them as L3 and L4 respectively. The statistics correctly count unique refs (inductor=1) but the schematic has duplicate reference designators for 2 physically distinct components.
  (statistics)

### Missed
- The schematic has 5 ESD protection arrays (TVS1-TVS5, OLIMEX_Diodes:GG0402052R542P). They are classified as 'diode' in component_types but are absent from signal_analysis.protection_devices. Only FUSE1 is detected. The TVS reference prefix and GG0402 library name should trigger TVS/ESD protection detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001787: 4-layer board correctly identified; PCB footprint count of 99 is accurate including decorative items

- **Status**: new
- **Analyzer**: pcb
- **Source**: VGA2HDMI_Rev_C.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB uses F.Cu, In1.Cu, In2.Cu, B.Cu — 4 copper layers. The analyzer reports copper_layers_used=4 and copper_layer_names matches the source gerbers (4-layer board confirmed by In1_Cu and In2_Cu gerber files).
- The PCB has 99 footprints: 86 from schematic components plus Sign_* (6 compliance marks), Logo_OLIMEX_TB-Bottom (1), and additional LED (LED_VGA1, LED_PWR1, LED_HDMI1) and ferrite bead (L3) footprints with remapped references vs the schematic.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001788: 4-layer gerber set complete with all required layers; Board dimensions 31 × 55 mm correctly measured from Edge.Cuts

- **Status**: new
- **Analyzer**: gerber
- **Source**: Gerbers.json
- **Created**: 2026-03-24

### Correct
- 11 gerber files cover F.Cu, In1.Cu, In2.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, and Edge.Cuts. PTH and NPTH drill files are both present. The completeness check passes with no missing required layers.
- Board outline extracted from Edge.Cuts gerber gives 31.0 × 55.0 mm, consistent with the PCB file (board_width_mm=31.0, board_height_mm=55.0).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001789: 2-layer gerber set complete with job file verification; Component analysis from X2 gerber attributes correctly lists 9 components

- **Status**: new
- **Analyzer**: gerber
- **Source**: hw_cam_profi.json
- **Created**: 2026-03-24

### Correct
- 9 gerber files cover all standard 2-layer layers (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts) plus PTH and NPTH drill files. Completeness validated against .gbrjob file with expected_layers match.
- The B.Mask gerber X2 attributes report 9 components (J1, J2, J3, J7, J9, M1, M2, M3, M4), matching the PCB and schematic component count exactly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
