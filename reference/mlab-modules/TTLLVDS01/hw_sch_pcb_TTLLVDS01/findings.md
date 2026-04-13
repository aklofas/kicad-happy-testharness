# Findings: mlab-modules/TTLLVDS01 / hw_sch_pcb_TTLLVDS01

## FND-00001631: All BOM component values report symbol-library names instead of instance values — analyzer fails to read the (instances) section; pwr_flag_warnings fires for GND and VCC even though both have PWR_F...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TTLLVDS01.kicad_sch
- **Created**: 2026-03-24

### Correct
- design_analysis.differential_pairs reports two pairs: '1+' / '1-' with series_resistors=['R3'], and '2+' / '2-' with series_resistors=['R4']. The SN65LVDS9638D drives two differential LVDS channels; R3 and R4 (100 Ω) are series termination resistors. Net names and resistor assignments are correct.

### Incorrect
- TTLLVDS01 uses KiCad 6 format where symbol placements have empty Value properties (property 'Value' '') and the actual instance-level overrides are stored at the end of the file in a per-project (instances) section. The instances section records: C2='100nF', D1='BZV55C-3,6V', R1=R2='33R', R3=R4='100', U1='SN65LVDS9638D'. The analyzer reads the symbol placement's Value field (empty) and falls back to the lib-symbol name, so it reports: C2='C_Small', D1='D_ZENER', R1=R2=R3=R4='R'. All footprints are also empty for the same reason — the instance footprint overrides are in the same (instances) section.
  (bom)
- The TTLLVDS01 schematic contains two PWR_FLAG symbols: one at (242.57,24.13) wired to the VCC symbol at (242.57,22.86), and one at (242.57,34.29) wired to the GND symbol at (242.57,35.56). As with other designs, the analyzer assigns both to a 'PWR_FLAG' net rather than the nets they are wired to, causing false 'no PWR_FLAG' warnings for both VCC and GND.
  (pwr_flag_warnings)
- Both detected differential pairs (1+/1- and 2+/2-) have has_esd=true and esd_protection=['U1']. U1 is the SN65LVDS9638D dual LVDS line driver — it drives the signals, not a TVS/ESD suppressor. R3 and R4 (100 Ω each, correctly identified as series_resistors) are impedance-matching resistors. The LVDS driver being shared on both nets appears to trigger the ESD-protection heuristic incorrectly.
  (design_analysis)
- All 17 components appear in missing_footprint because the analyzer reads the symbol-placement Footprint property (which is empty in TTLLVDS01's instance format) rather than the (instances) section footprint overrides. The PCB has all 17 footprints correctly populated with real library references (e.g., Package_SO:SOIC-8_3.9x4.9mm_P1.27mm for U1, Diode_SMD:D_MiniMELF for D1).
  (statistics)

### Missed
- C2 has pin 1 on VCC and pin 2 on GND; the PCB footprint confirms value '100nF'. Because the schematic analyzer reads the empty instance Value field and falls back to the symbol name 'C_Small', parsed_value is None. The decoupling detector requires a valid capacitance, so C2 is excluded and decoupling_analysis returns an empty list. The design_observations also incorrectly states U1's VCC rail has no decoupling caps at all.
  (signal_analysis)

### Suggestions
- Fix: LVDS differential pairs report U1 (SN65LVDS9638D) as has_esd=true with esd_protection=[U1] — the LVDS driver IC is misidentified as an ESD protection device

---

## FND-00001632: TTLLVDS01 PCB correctly parsed: 17 footprints, 2-layer 40×20 mm board, fully routed; C2 (100 nF) correctly found as decoupling cap for U1 (SN65LVDS9638D) in PCB decoupling_placement

- **Status**: new
- **Analyzer**: pcb
- **Source**: TTLLVDS01.kicad_pcb
- **Created**: 2026-03-24

### Correct
- statistics: footprint_count=17, smd_count=7, tht_count=10, copper_layers=2, routing_complete=true, net_count=10. Board dimensions 40.132×19.812 mm match the Edge.Cuts extents in the gerber. DFM standard tier, min track 0.3 mm, min drill 0.4 mm, no violations.
- decoupling_placement for U1 lists C2 (value='100nF') at distance 5.06 mm, sharing GND and VCC nets with U1, same-side (B.Cu). This is accurate: the PCB footprint retains the correct '100nF' value even though the schematic analyzer shows 'C_Small'.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001633: Gerber set complete: 8 signal/mask/paste/silkscreen layers plus 2 drill files, gbrjob parsed; board_dimensions reports 40.28×19.96 mm from gbrjob while PCB Edge.Cuts gives 40.132×19.812 mm — gbrjob...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hw_cam_profi
- **Created**: 2026-03-24

### Correct
- completeness reports found_layers=[B.Cu, B.Mask, B.Paste, B.SilkS, Edge.Cuts, F.Cu, F.Mask, F.SilkS], missing=[], complete=true using gbrjob as source. Both PTH and NPTH drill files present. F.Paste is absent (no front-side SMD paste needed as all SMD is on B.Cu), which is consistent with the layout.

### Incorrect
- The gbrjob GeneralSpecs.Size is X=40.282, Y=19.962 mm — a ~0.15 mm discrepancy versus the PCB analyzer's computed Edge.Cuts extents of 40.132×19.812 mm. The gbrjob file was generated from KiCad 6.0.4 and the Size field appears to be rounded or includes tooling allowance. The gerber Edge.Cuts layer itself reports 40.132×19.812 mm (confirmed by the layer_extents field). The discrepancy is in the gbrjob metadata, not the actual copper/outline data.
  (board_dimensions)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001881: missing_footprint list incorrectly includes all 17 components; Design observation falsely reports U1 VCC rail has no decoupling capacitors; PWR_FLAG warnings fire for VCC and GND despite both havin...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TTLLVDS01_hw_sch_pcb_TTLLVDS01.kicad_sch
- **Created**: 2026-03-24

### Correct
- 17 total components (4 other/mounting holes, 1 capacitor, 6 connectors, 1 diode, 1 IC, 4 resistors), 10 nets (VCC, GND, 1A, 2A, 1+, 1-, 2+, 2-, Net-R1-Pad1, Net-R2-Pad1), power rails [GND, PWR_FLAG, VCC] — all confirmed correct against the source schematic. The SN65LVDS9638D IC and its net connections are accurately extracted.

### Incorrect
- The schematic's symbol_instances section contains fully-populated footprint strings for all real components (e.g., C2='Resistor_SMD:R_0805_2012Metric', D1='Diode_SMD:D_MiniMELF', J1='Mlab_Pin_Headers:Straight_2x03', J2–J5='Mlab_Pin_Headers:Straight_2x01', J6='Mlab_CON:SATA-7_THT_VERT_2', M1–M4='Mlab_Mechanical:MountingHole_3mm', R1–R4='Resistor_SMD:R_0805_2012Metric', U1='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'). The analyzer reads footprints from the embedded symbol library definitions (which have empty footprint fields) rather than from the symbol_instances block where the actual instance-level footprint assignments live. All 17 components should have non-empty footprints.
  (statistics)
- signal_analysis.design_observations contains {category: 'decoupling', component: 'U1', rails_without_caps: ['VCC'], rails_with_caps: []}. The nets section clearly shows C2 pin 1 is on VCC and C2 pin 2 is on GND, meaning C2 (100nF) is a decoupling capacitor bridging VCC to GND. The VCC rail is properly decoupled. The decoupling_analysis section is also empty when it should contain C2. The observation is a false positive.
  (signal_analysis)
- pwr_flag_warnings reports that both 'GND' and 'VCC' have power_in pins but no power_out or PWR_FLAG. The schematic contains two PWR_FLAG instances: #FLG0101 at (242.57, 24.13) co-located with the VCC power symbol at (242.57, 22.86), and #FLG0102 at (242.57, 34.29) co-located with the GND symbol at (242.57, 35.56). Both power rails have proper PWR_FLAG coverage. These warnings are false positives.
  (pwr_flag_warnings)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001882: Footprint count, track segments, via count, net count, and board dimensions are all accurate; C2 footprint library correctly reported as Resistor_SMD despite being a capacitor

- **Status**: new
- **Analyzer**: pcb
- **Source**: TTLLVDS01_hw_sch_pcb_TTLLVDS01.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 17 footprints confirmed (grep for module patterns), 62 track segments all on B.Cu confirmed by parsing the .kicad_pcb file, 9 vias, 10 nets, board 40.132mm x 19.812mm, 2-layer (F.Cu + B.Cu). Zones (2 GND fills on F.Cu and B.Cu), connectivity complete with 0 unrouted nets. All verified against source.
- C2 (100nF capacitor) uses the footprint 'Resistor_SMD:R_0805_2012Metric' — the PCB file confirms this. The analyzer correctly reports the library name from the source without misclassifying it. This is a design quirk (resistor footprint used for a capacitor), not an analyzer error.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001883: Gerber layer completeness, drill classification, and board dimensions are accurate

- **Status**: new
- **Analyzer**: gerber
- **Source**: TTLLVDS01_hw_cam_profi
- **Created**: 2026-03-24

### Correct
- The gerber output (processed from cam_profi, not the non-existent sch_pcb/gerber path specified) correctly identifies 8 gerber files + 2 drill files (PTH + NPTH), all expected layers present (B.Cu, B.Mask, B.Paste, B.SilkS, Edge.Cuts, F.Cu, F.Mask, F.SilkS), complete=true, 9 vias in drill (0.4mm drill), board 40.28mm x 19.96mm from gbrjob. Note: the user-specified gerber source path (repos/TTLLVDS01/hw/sch_pcb/gerber) does not exist; the actual gerbers are in hw/cam_profi/.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
