# Findings: SparkFun_u-blox_NEO-F10N / Hardware_Production_SparkFun_NEO-F10N_panelized

## FND-00001562: total_no_connects reported as 0 despite 17 explicit no-connect markers in the schematic; PWR_FLAG warnings for GND, 5V, VBUS, 3.3V_A, 3.3V_P, VCC are over-flagged for a connector-powered design; an...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_NEO-F10N.kicad_sch
- **Created**: 2026-03-24

### Correct
- U2 (AP2112K-3.3) is correctly identified as a linear regulator. VIN (VCC) has C1 (0.1uF) as decoupling, and VOUT (3.3V) has C8 (1.0uF) and C2 (0.1uF) as decoupling capacitors. The subcircuit grouping also correctly associates L2 (30Ohm ferrite bead) on the 3.3V rail output side.
- R1 (5.1k) on CC2 and R2 (5.1k) on CC1 of J1 (USB-C receptacle) are correctly detected and the cc1_pulldown_5k1 and cc2_pulldown_5k1 checks both pass. The USB ESD IC (U1, DT1042-04SO) is also correctly recognized.
- U3 (NEO-F10N) subcircuit correctly includes BT1 (backup battery), C16 and C3 (decoupling), C7 (47pF RF bypass), D5 (Schottky for V_BCKP), JP2/JP3 (configuration jumpers), L2 (power ferrite), R12 (reset pull-up), R15/R16/R29/R30/R31/R34 (33-ohm series resistors on signal lines), and R7 (1k battery protection resistor). Component count and types are accurate.
- The LC filter detector correctly identifies L1 (33nH) forming resonant circuits with C4+C6 (parallel, ~100pF) at 2.77 MHz and with C7 (47pF) at 127.8 MHz. These are the RF matching/filtering elements on the antenna path between J5 (SMA) and U3 RF_IN. The analysis is structurally correct.
- The main schematic output at _sheet=0 contains 51 components from the root sheet, and _sheet=1 contains 12 components from the Connectors sub-sheet (C4, C6, C7, D2, D3, D6, J2, J4, J5, JP8, L1, R3). Both sheets are listed in the 'sheets' array. The total of 63 components in statistics.total_components correctly combines both sheets.
- U8 (CH340C) is correctly classified as ic, function='USB-UART bridge', with total_pins=16, unconnected_pins=0. The subcircuit includes C13 (decoupling), J1 (USB-C connector), JP1/JP4 (RXD/TXD routing jumpers), and U1 (ESD protection). The 3.3V_P power rail for V3 pin is correctly identified.

### Incorrect
- The schematic source file contains 17 'no_connect' elements (grep-confirmed). These include RESERVED pins on U3 (NEO-F10N), NC pins on U8 (CH340C), NC on U2, and NC pins on J1 (USB-C). The statistics field reports total_no_connects=0 and the no_connects array is empty. The net data does correctly reflect pin_type='no_connect' on these pins, but the summary counter and dedicated array are not populated.
  (statistics)
- Six power rails are flagged as missing PWR_FLAG or power_out driver. This is a SparkFun design where power comes from USB (J1). The VBUS rail is driven by the USB connector (passive pin type is correct for a receptacle), and 5V/VCC/3.3V_A/3.3V_P are derived rails. The analyzer flags these as ERC warnings but for connector-powered designs this is a common intentional pattern where PWR_FLAGs are omitted. The GND warning is particularly over-aggressive. However 5V, VBUS, 3.3V_A, 3.3V_P, and VCC warnings may warrant review.
  (pwr_flag_warnings)
- The annotation_issues.missing_value list flags JP1, JP2, JP3, JP4, JP6, JP7, JP8 (all solder jumpers) and U7 (SparkFun-Aesthetic:Ordering_Instructions graphic). In SparkFun's design convention, solder jumpers use value '~' intentionally as a placeholder and U7 is a PCB graphic symbol with no functional value. These are not genuine missing-value issues.
  (annotation_issues)
- The RC filter detector finds R7 (1k) and C3 (1.0uF) forming a 159 Hz low-pass structure on the V_BCKP rail. In reality, R7 is a protection/isolation resistor between D5 (Schottky diode that trickle-charges from 3.3V_A) and C3 (bulk decoupling for the NEO-F10N V_BCKP backup pin). This is a power supply protection circuit, not a signal filter. The cutoff frequency label is misleading in context.
  (signal_analysis)

### Missed
(none)

### Suggestions
- Fix: R7+C3 detected as an RC low-pass filter (159 Hz) but is actually a backup battery isolation network

---

## FND-00001563: GKO (board outline) file misclassified as B.Mask layer, causing false Edge.Cuts missing alert; GKO file's X2 FileFunction attribute is contradicted by its aperture content — analyzer trusts wrong a...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: SparkFun_NEO-F10N_panelized.GKO
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The GKO file has X2 attributes claiming 'Soldermask,Bot' (FileFunction), but its aperture_analysis shows a 'Profile' aperture function — confirming it is the board outline (Edge.Cuts). The analyzer classifies it as layer_type='B.Mask' based on the X2 FileFunction attribute instead of the aperture content, resulting in 'Edge.Cuts' appearing in missing_required and complete=false. The file should be classified as Edge.Cuts and the completeness check should pass.
  (completeness)
- The GKO gerber file has FileFunction='Soldermask,Bot' in its X2 header but contains only Profile-function apertures. The .GKO extension is a standard KiCad convention for the board outline (Edge.Cuts). The analyzer should prioritize the aperture_analysis Profile function or the .GKO extension over the misleading X2 FileFunction header to correctly classify this layer.
  (gerbers)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001564: board_outline reports edge_count=0 and null bounding_box despite the PCB having a defined Edge.Cuts outline; smd_count=50 undercounts actual SMD components: 7 solder jumpers classified as 'allow_so...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_NEO-F10N.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The PCB is correctly identified as a 2-layer board (F.Cu/B.Cu). The GND copper zone spanning both layers (F&B.Cu) with 58 thermal via stitching vias at 3.0 vias/cm² is correctly captured in thermal_analysis.zone_stitching. DFM metrics (min track 0.1524mm, min drill 0.3mm) match the actual design rules.

### Incorrect
- The main PCB file (SparkFun_NEO-F10N.kicad_pcb) shows board_outline.edge_count=0 and bounding_box=null, yet the PCB clearly has a board outline — dimension annotations on Dwgs.User reference dimensions like 50.8mm and 38.1mm. The panelized board output correctly extracts a board size (174.72x90.4mm). The Edge.Cuts layer is present in the layer table but its geometry is not being extracted.
  (board_outline)
- Seven jumper footprints (JP1, JP2, JP3, JP4, JP5, JP7, JP8) have type='allow_soldermask_bridges' in the output rather than 'smd'. These are genuine SMD pad footprints on B.Cu and should contribute to smd_count. The reported smd_count=50 misses these 7 components, resulting in an undercount. Total non-board-only components are 61 (50 smd + 3 tht + 7 allow_soldermask_bridges + 1 exclude_from_bom) but smd_count only reflects 50.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001565: Panelized PCB reported as routing_complete=false with 31 unrouted nets, but all are intentional no-connect nets duplicated across 6 panels

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_NEO-F10N_panelized.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The panelized PCB shows unrouted_count=31 and routing_complete=false. All 31 unrouted nets have names starting with 'unconnected-' (e.g., unconnected-D2-K1-Pad1, unconnected-J1-NC-PadA8) which correspond to intentional no-connect pins. In a 6-unit panel, each single-board no-connect net appears 6 times with pad_count=6, forming nets across panel copies that have no ratsnest connections but appear unrouted. The main single board correctly reports routing_complete=true.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
