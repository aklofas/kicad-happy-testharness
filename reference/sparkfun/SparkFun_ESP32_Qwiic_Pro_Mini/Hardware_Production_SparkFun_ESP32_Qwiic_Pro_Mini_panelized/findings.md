# Findings: sparkfun/SparkFun_ESP32_Qwiic_Pro_Mini / Hardware_Production_SparkFun_ESP32_Qwiic_Pro_Mini_panelized

## FND-00001395: Component count of 26 and BOM breakdown are accurate; LDO regulator (U2 AP2112K-3.3) correctly detected with VCC→+3.3V path; I2C bus not detected despite Qwiic connector and 2.2k pull-up resistors ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_ESP32_Qwiic_Pro_Mini.kicad_sch
- **Created**: 2026-03-24

### Correct
- The schematic reports 26 total_components with correct type distribution: 4C, 2D (LED), 2FID, 4 connectors, 1 jumper, 5R, 2SW, 3 ICs (U1=ESP32, U2=LDO, U3=aesthetic), 2 logo graphics (G1, G3). The BOM de-duplicates correctly into 19 unique parts. All refs match what is visible in the design.
- power_regulators correctly identifies U2 as an LDO topology with input_rail=VCC, output_rail=+3.3V, estimated_vout=3.3V via fixed_suffix detection. The power budget also correctly assigns U1 (ESP32) load to the +3.3V rail at 240mA, which is within the AP2112K-3.3's 600mA rating.
- bus_analysis.uart contains two entries for ESP_1{slash}TX and ESP_3{slash}RX, each connected to U1 (ESP32). The debug connector J1 (6-pin UART header) is also correctly identified as a UART debug connector in test_coverage.debug_connectors. Net naming conventions (slash-notation for TX/RX) are handled correctly.

### Incorrect
(none)

### Missed
- The design has a Qwiic (JST-SH 4-pin I2C) connector J5, and R3/R4 (both 2.2k) are I2C pull-up resistors on the +3.3V rail. The bus_analysis.i2c array is empty. The ESP32-PICO-V3-02 exposes I2C on IO21/IO22 (ESP_21/ESP_22 nets), which are broken out on J3. The analyzer should have detected the Qwiic connector by footprint name or description ('4 pin JST 1mm polarized connector for I2C') and the pull-up topology.
  (design_analysis)
- U1 is an ESP32-PICO-V3-02 — a module with integrated 2.4GHz WiFi and Bluetooth. The rf_chains and rf_matching arrays are both empty, and no wireless protocol is identified in the signal detectors. The component keywords field contains 'RF Radio BT ESP ESP32 Espressif onboard PCB antenna', which should be sufficient for the analyzer to flag this as a WiFi+BT capable device and surface it under a wireless or rf_module detector.
  (signal_paths)

### Suggestions
(none)

---

## FND-00001396: Board dimensions (33.02×17.78 mm) are correct for a Pro Mini form factor; PCB footprint count (82) and side distribution are plausible; Via count (63) and net count (40) are consistent with the sch...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_ESP32_Qwiic_Pro_Mini.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The board outline is a single rectangle from (129.54, 114.3) to (162.56, 132.08), giving 33.02×17.78mm (~1.3"×0.7"). This is consistent with a Pro Mini variant sized to fit an ESP32 module. Board thickness is 1.6mm FR4 with 2-layer stackup, both plausible for a production SparkFun design.
- statistics reports 82 footprints total: 43 front, 39 back. The high back count is driven by 55 kibuzzard graphic/logo items (board_only, exclude_from_bom). Actual electrical components are 24 (U1, U2, 4C, 2D, 2FID, 5R, 4J, 1JP, 2SW, G2, U3, Ref**) plus kibuzzard decorators. The split is credible given extensive artwork on this SparkFun board.
- The PCB reports 63 vias and 40 nets vs the schematic's 39 nets — the extra net is due to the PCB including unconnected stubs (e.g., unconnected-(J5-NC-PadNC1/2)) treated separately. routing_complete=true with 0 unrouted nets. The track count of 364 segments and 572.5mm total length is plausible for a compact 33×18mm 2-layer ESP32 board.

### Incorrect
- The PCB statistics report only 19 SMD and 3 THT footprints, but the actual board has ~24 electrical components (U1 at 61 pads, U2, 4C, 5R, 2D, 2SW, 2FID, plus connectors). The discrepancy is because the smd/tht counts only reflect footprints where the type is unambiguously set; the kibuzzard board_only items (55 of them) are excluded correctly, but several real SMD components may be misclassified. The counts 19+3=22 are too low relative to the 26 schematic components.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001397: Edge.Cuts (outline) reported as missing but .GKO file is present and contains outline data; Drill file hole counts are consistent and correctly classified; Layer count (9 gerber + 1 drill) and 2-la...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- The drill file contains 2604 total holes: 1484 vias at 0.3mm, 280 vias at 0.305mm, and 840 component THT holes at 1.016mm. The 840 THT holes match 28 panels × 30 holes per board (J1=6, J2=12, J3=12). The via classification via x2_attributes (Plated,PTH,ViaDrill vs ComponentDrill) is correct.
- The set contains 9 gerber files covering F.Cu, B.Cu, F.SilkS, B.SilkS, F.Paste, B.Paste, F.Mask, B.Mask, and the outline (.GKO). This is the standard 9-file set for a 2-layer PCB from KiCad. The B.Paste layer is correctly empty (0 flashes, 0 draws) — back-side THT components have no paste. The SMD ratio of 0.78 (78% SMD pads) is consistent with the mix of SMD passives and THT connectors.
- Three unique trace widths found: 0.1524mm (6mil, minimum — used for signal routing), 0.4064mm (16mil — mid-weight), 0.5588mm (22mil — power traces). The 6mil minimum is tight but acceptable for a professional PCB fab. The widths are consistent between the gerber analysis and what the PCB analyzer would report from the .kicad_pcb file.

### Incorrect
- completeness.missing_required lists 'Edge.Cuts' and complete=false. The file SparkFun_ESP32_Qwiic_Pro_Mini_panelized.GKO is present in the gerber set (1017 draw strokes, Profile aperture function) but its X2 FileFunction attribute was generated as 'Soldermask,Bot' — the same tag as the .GBS file. The analyzer uses the X2 FileFunction to classify layers, not the file extension, so it fails to recognize .GKO as the board outline and instead misclassifies it as a second soldermask layer. This is an analyzer bug: when X2 FileFunction is absent or mismatched for a .GKO/.GML file, the extension should be used as fallback.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---
