# Findings: ThunderFly-aerospace/TFRPM01 / hw_sch_pcb_TFRPM01

## FND-00001621: assembly_complexity.total_components=29 overcounts due to multi-unit IC U2 counted twice; assembly_complexity reports tht_count=0 but J1 (PinHeader_1x03_P2.54mm_Horizontal) is THT

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TFRPM01_hw_sch_pcb_TFRPM01.kicad_sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The SN74LVC1G14QDCKRQ1 (U2) is a single-gate Schmitt trigger implemented as a two-unit schematic symbol in KiCad: unit 1 (logic gate, at 127,63.5) and unit 2 (power pins, at 53.34,137.16), both with in_bom=True. The components array contains two entries for U2, causing assembly_complexity.total_components=29 instead of the correct 28. statistics.total_components correctly deduplicates to 28. The BOM correctly groups U2 as one entry. Only assembly_complexity overcounts.
  (assembly_complexity)
- assembly_complexity reports smd_count=29, tht_count=0. J1 (DS1022-1*40RDF11-B) uses footprint Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Horizontal, which is a through-hole 2.54mm pitch pin header. The PCB correctly identifies J1 as through_hole (PCB statistics: smd_count=23, tht_count=3 — where the 3 THT are J1, M2 mounting hole, and G1 logo). The schematic analyzer fails to detect the THT classification for PinHeader footprints in this case.
  (assembly_complexity)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001622: component_analysis.front_side=4 overcounts genuine front-side components; correct count is 2

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: TFRPM01_hw_cam_profi_gbr
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The gerber component_analysis reports front_side=4, back_side=24. The PCB file shows only JP1 and G1 (logo) are on F.Cu (primary layer = front), giving front_side=2, back_side=26. The gerber analyzer counts front_side by any component reference appearing in F.Cu pads, which includes J1 and M2 (both B.Cu primary-layer THT components whose pads penetrate to F.Cu). JP1 appears in F.Cu copper (it is on F.Cu) and F.SilkS, while J1 and M2 appear in F.Cu because their through-hole pads exist on both copper layers.
  (component_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001872: I2C bus detection: SDA and SCL lines with pull-up resistors identified; LDO regulator U3 MIC5504-3.3YM5 detected with correct input/output rails; RC low-pass filter detected on input signal path (R...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TFRPM01.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- bus_analysis.i2c correctly identifies SDA (R3 10k to +3V3) and SCL (R10 10k to +3V3) with PCF8583T (U1) as the device. Pull-up resistors are correctly named and their rail is correct.
- signal_analysis.power_regulators correctly identifies U3 as LDO topology with input_rail=+5V and output_rail=+3V3. Vout estimated at 3.3V via fixed_suffix method.
- signal_analysis.rc_filters correctly identifies R2 (82R) and C2 (10uF) as a low-pass filter with cutoff at 194.09 Hz. This matches the frequency conditioning circuit on the RPM sensor input.
- +5V has C4 (100nF) + C3 (10uF) = 10.1 uF total; +3V3 has C5+C6 (100nF each) + C1 (1uF) = 1.2 uF total. Both rails have bulk and bypass coverage flagged correctly.

### Incorrect
- The SN74LVC1G14 is a 5-pin SOT-23-5 Schmitt-trigger inverter (IN, OUT, GND, VCC). The analyzer reports total_pins=2 for U2 because it only counts logic signal pins (pin 1=IN and pin 2=OUT from the signal unit), while the power pins (VCC pin 5, GND pin 3) are on a separate unit of the same symbol. The ic_pin_analysis for U2 shows power_pins for GND and VCC separately. This split-unit counting underreports pin coverage and may mislead DFM checks.
  (components)

### Missed
- D1 (BZX585-B5V6.115, a 5.6V Zener) is connected anode-to-GND, cathode-to-+5V via R5 (130R) forming an overvoltage clamp. signal_analysis.protection_devices is empty []. This TVS/Zener clamp topology should be detected as a protection device.
  (signal_analysis)
- The i2c bus analysis lists devices=[U1] for both SDA and SCL, but J2 (pin 2=SCL, pin 3=SDA) and J3 (pin 2=SCL, pin 3=SDA) are physical I2C connectors exposing the bus to a host MCU. They should appear as bus participants so the I2C topology is understood as a module-with-external-host rather than a single-device bus.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001873: Board dimensions, layer count, via count and track count are accurate; Component placement split (back-heavy) correctly reported: 2 front, 26 back; F.Cu layer type classified as 'jumper' instead of...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: TFRPM01.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- PCB reports 37.5 x 19.0 mm (confirmed by edge cuts), 2 copper layers, 63 vias, 120 track segments, 28 footprints. These match the source .kicad_pcb.
- front_side=2, back_side=26 matches the design layout where nearly all SMD components are on the bottom copper layer.

### Incorrect
- The copper layer type for F.Cu is reported as 'jumper' in the layers section. F.Cu is a standard signal routing layer with regular traces and pads. The 'jumper' type is only appropriate for dedicated jumper layers. This is a misclassification that would affect any layer-type-based DFM checks. Likely caused by the layer type string in the .kicad_pcb file being parsed incorrectly or defaulting to a wrong value when not explicitly set.
  (layers)

### Missed
- The schematic contains JP1 and JP2 (SolderJumper_3_Bridged12) which allow address/configuration selection for the PCF8583T. The PCB analysis does not surface these as design-time configuration items or flag them in a jumper-configuration section, which would be useful for manufacturing notes.
  (design_observations)

### Suggestions
(none)

---

## FND-00001874: Gerber set is complete: all required copper, mask, paste, silk, and edge-cut layers present; Drill classification correctly identifies 63 vias and 4 component through-holes; Board dimensions from e...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr.json
- **Created**: 2026-03-24

### Correct
- completeness.complete=true with no missing_required or missing_recommended layers. 9 gerber files plus 2 drill files, matching the 2-layer board.
- drill_classification.vias.count=63 and component_holes.count=4, matching the PCB analysis. The 0.4mm via drill and 1.0mm component drill tools are correctly identified.
- board_dimensions.width_mm=37.65 and height_mm=19.15. The slight difference from the PCB reported 37.5x19.0 mm is expected because the gerber edge-cut extent includes the outline line width (0.15mm per side).

### Incorrect
(none)

### Missed
- The gerbers are generated from a named CAM job (hw/cam_profi/gbr/) using a .gbrjob manifest. The analyzer output does not capture the gbrjob metadata or note that this is a named CAM profile. While the gerbers themselves are correctly analyzed, the source provenance (cam profile name, gbrjob board size reference) is silently dropped.
  (source_cam_profile)

### Suggestions
(none)

---

## FND-00001875: Complete gerber set from JLCPCB CAM job: all layers present, board 55x20 mm; 131 total holes (113 vias + 18 component/mounting holes) consistent with PCB; Generator is KiCad 5.99 (dev/nightly) — no...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: jlcpcb_gerber.json
- **Created**: 2026-03-24

### Correct
- completeness.complete=true, 11 gerber files + 2 drill files. Board dimensions match the PCB (55.0 x 20.0 mm). Generator correctly identified as KiCad 5.99.
- Total drill holes = 131, matching the PCB's 113 vias plus the THT connector pins and 4 mounting holes.

### Incorrect
(none)

### Missed
- The X2 attribute GenerationSoftware shows 'KiCad,Pcbnew,5.99.0-12376-gd4dc5b7b70' which is a development snapshot, not a stable release. The analyzer reports the generator string correctly but does not flag this as a non-standard generator that could produce subtle differences vs stable release outputs.
  (generator)

### Suggestions
(none)

---

## FND-00001876: All 6 BOM components identified: U1=TS4231, D1=BPW34S, C1/C2, R1, J1; DVDD decoupling (C1=100nF on +3.3V) correctly catalogued; PWR_FLAG ERC warnings for GND and +3.3V correctly raised for connecto...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TS4231-BOB.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- bom.components lists all 6 parts. U1=TS4231 (ASIC), D1=BPW34S (photodiode), C1=100nF (DVDD decoupling), C2=1uF (AVDD local supply), R1=15k (RBIAS), J1=Conn_01x04. Component types and values are accurate.
- decoupling_analysis for +3.3V lists C1 (100nF). This matches TS4231 application note requirements for 100nF on DVDD pin.
- erc_warnings includes PWR_FLAG issues for GND and +3.3V. This is expected behavior — the board is powered via J1 connector pins and has no explicit power source symbol, so PWR_FLAGs are legitimately missing in the schematic.

### Incorrect
(none)

### Missed
- The TS4231 AVDD pin (A1) connects to an unnamed net with only C2 (1uF) as a local bypass. The analyzer classifies this net as 'power_internal' but does not report that AVDD is physically tied to DVDD (+3.3V) via a short PCB trace with a local filter cap — this is a design-significant topology (ferrite bead or RC filtering between DVDD and AVDD) that should be noted. The power_domains section omits AVDD as a separate rail.
  (design_analysis)
- R1 (15k) is connected to the RBIAS pin of the TS4231, which sets the internal current reference. It is listed in the BOM but is not annotated in any signal analysis section (not a voltage divider, not a pull-up, not a current sense). The RBIAS function is design-critical and should ideally be flagged as a bias/reference resistor.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001877: Board dimensions 12.0 x 12.9 mm, 6 footprints, 2 copper layers, 10 vias correctly reported; SMD/THT mix correctly identified: 3 SMD (U1, D1, C1/C2 are SMD) and 3 THT (J1 header + others)

- **Status**: new
- **Analyzer**: pcb
- **Source**: TS4231-BOB.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- All primary board metrics match the source .kicad_pcb: 12.0 x 12.9 mm, 6 footprints, 2 layers, 10 vias, 2 copper zones.
- smd=3 THT=3 split is consistent with: U1 (SOT-23-6 SMD), D1 (SMD photodiode), C1 (SMD 0402) on front side as SMD, and J1 (1x4 pin header THT), C2 (THT electrolytic or radial), R1 (THT) as through-hole.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001878: Complete 9-layer gerber set for 2-layer board with correct drill files; B.Paste empty (0 flashes) correctly handled — no back-side SMD pads; 14 total holes: 10 vias (0.4mm) + 4 component PTH (1.0mm...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: output_gerber.json
- **Created**: 2026-03-24

### Correct
- completeness.complete=true, all standard layers present (F.Cu, B.Cu, F/B.Mask, F/B.Paste, F/B.SilkS, Edge.Cuts), plus PTH and NPTH drill files. Board dimensions 12.0 x 12.9 mm consistent with PCB.
- B.Paste has aperture_count=0 and flash_count=0. This is correct: all SMD pads are on the front side (F.Cu), so no solder paste is needed on the back. An empty paste layer is valid and is not flagged as an error.
- drill_classification.vias.count=10 and component_holes.count=4 correctly matches the board. J1 (Conn_01x04) is the only THT component, contributing 4 x 1.0mm PTH holes.

### Incorrect
(none)

### Missed
- zip_archives[0].vs_loose_files='loose_files_newer' with age_delta_hours=9811.6. This means the gerber ZIP was not regenerated after the most recent KiCad export. The analyzer correctly detects and reports this discrepancy, but it should be surfaced as a warning in completeness.issues rather than only in the zip_archives section.
  (zip_archives)

### Suggestions
(none)

---
