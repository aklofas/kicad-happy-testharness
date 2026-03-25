# Findings: SofleChocWireless / SofleChocWireless_Case_PCBBottom_SofleKeyboardBottomPlate

## FND-00001364: Keyboard matrix correctly identified as 5x6 with 31 keys on this half; RSW1 (SW_RST reset tact switch) misclassified as type 'resistor' instead of 'switch'; Addressable LED chain (SK6812 Mini-E per...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SofleChocWireless_PCB_SofleKeyboard.kicad_sch
- **Created**: 2026-03-24

### Correct
- The kicad_sch analyzer detected the key matrix with rows=[row0..row4] and columns=[col0..col5], estimated_keys=31, switches_on_matrix=31, diodes_on_matrix=30. The SofleChocWireless is a 30-key (plus encoder) per-half design, so 31 keys (including encoder) is accurate.
- The kicad_sch output correctly identifies two I2C buses (SDA and SCL nets) and correctly notes has_pull_up=false for both. In the SofleChocWireless, the traditional I2C pull-up resistors (R1/R2 present in the legacy .sch version) were removed. The design_observations correctly flag i2c_bus without pull-ups for both lines.

### Incorrect
- The BOM entry for value='SW_RST', footprint='TACT_SWITCH_TVBP06', reference='RSW1' is assigned type='resistor'. The value prefix 'SW_' and footprint name 'TACT_SWITCH' both clearly indicate a tactile switch. This misclassification also causes the total component_types.switch count to be understated by 1 (33 instead of 34) and component_types.resistor to be overstated by 1.
  (statistics)
- Seven mounting hole components (TH1-TH7, value='HOLE') are assigned type='thermistor' in the BOM. These are mechanical mounting holes with no electrical function. The 'TH' reference prefix is being matched against thermistor heuristics, but the value 'HOLE' and footprints 'M2_HOLE_PCB'/'HOLE_M2_TH' clearly indicate mechanical holes. This inflates thermistor count to 7 and misrepresents the design.
  (statistics)

### Missed
- The SofleChocWireless has SK6812 Mini-E addressable RGB LEDs integrated into each hotswap socket (footprint names include 'SK6812MiniE'). There is a net named 'LED' and a 'LED' signal in the schematic. The signal_analysis.addressable_led_chains array is empty, meaning the WS2812/SK6812 chain detection did not fire. The design has 30 per-key LEDs chained via the LED net.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001365: Legacy .sch key matrix detected as 5x5 instead of 5x6, missing col5; I2C pull-up resistors R1 and R2 correctly identified in legacy schematic; HOLE footprints (TH1-TH7) also misclassified as 'therm...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SofleChocWireless_PCB_SofleKeyboard.sch
- **Created**: 2026-03-24

### Correct
- The legacy .sch version of the design includes R1 and R2 as I2C pull-up resistors on SDA and SCL respectively. The analyzer correctly reports has_pullup=true, pullup_resistor='R2'/'R1', pullup_rail='VCC' for both I2C lines. This version predates the wireless redesign that removed the pull-ups.

### Incorrect
- The legacy KiCad 5 schematic reports a 5x5 matrix (col_nets=[col0..col4]) with estimated_keys=54. However, the .sch file also contains col5 net labels (found at lines 9681-9690 in the .sch JSON), which means the matrix is actually 5x6. The kicad_sch version correctly reports 5x6. The legacy parser appears to miss col5 in the matrix reconstruction. The 54-key estimate is also implausible for one half of a split keyboard (should be ~31).
  (signal_analysis)
- Same misclassification as in the kicad_sch version: TH1-TH7 mounting holes (value='HOLE', footprints 'M2_HOLE_PCB' and 'HOLE_M2_TH') are typed as 'thermistor'. The legacy .sch file has 84 components but component_types shows thermistor=7 when the actual count should be 0 thermistors. RSW1 (SW_RST) is also misclassified as type='resistor', inflating the resistor count from 2 (R1, R2) to 3.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001366: All 30 key-hole footprints reported with duplicate reference 'SW2' instead of unique refs; Top plate board dimensions and copper-free routing correctly reported

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SofleChocWireless_Case_PCBTop_SofleKeyboardTopPlate.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Board dimensions 143.369x111.75mm match the main PCB and bottom plate, confirming all three boards align. copper_layers_used=0, track_segments=0, via_count=0 are all correct — a mechanical switch plate has no copper routing. The single zone (a fill pattern for the plate shape) is correctly identified.

### Incorrect
- The top plate PCB component_groups.SW shows count=30 but all 30 entries in the references array are 'SW2'. This is a reference deduplication bug in the analyzer: the PCB file has all 30 key-hole cutout footprints referencing the same 'SW2' designator (the plate cutouts share a reference, which is unusual but valid for mechanical plates). However, the analyzer should ideally report this as 30 instances of 'SW2' or note the duplicate reference anomaly rather than silently listing them as 30 distinct items with identical names.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001367: Bottom plate correctly identified as mechanical-only with 5 mounting holes and no routing; fill_ratio=1.83 for the zone is implausible (filled area exceeds outline area by 83%)

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SofleKeyboardBottomPlate.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The bottom plate has footprint_count=5 (all TH mounting holes), copper_layers_used=0, track_segments=0, via_count=0. Board area ~160cm² matches the top plate and main PCB. All 5 footprints are correctly typed as through_hole with no connected nets.

### Incorrect
- The bottom plate zone reports outline_area_mm2=14225.71 but filled_area_mm2=26028.28, giving fill_ratio=1.83. A copper fill ratio greater than 1.0 is physically impossible — filled copper cannot exceed the zone outline. This likely reflects a bug in zone area calculation where the outline polygon area is underestimated (perhaps the concave outline is computed incorrectly) while the filled area from gerber region data is correct. The top plate zone has fill_ratio=0.758, which is plausible.
  (zones)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001368: Main PCB fully routed with correct component count, layer count, and via count; thermal_pad_vias analysis incorrectly treats hotswap socket pads as thermal pads; DFM tier 'challenging' correctly fl...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SofleChocWireless_PCB_SofleKeyboard.kicad_pcb
- **Created**: 2026-03-24

### Correct
- footprint_count=85 matches the schematic's total_components=85. copper_layers_used=2 is correct (2-layer board). via_count=418 matches the gerber's PTH via drill count of 418 (T1, 0.2997mm tool). routing_complete=true with unrouted_count=0. Board dimensions 143.37x111.75mm consistent across all outputs.
- The analyzer correctly identifies the annular ring violation: drill=0.3mm, computed annular_ring=0.05mm (below the 0.1mm advanced process minimum). Keyboard PCBs often use the smallest possible via drill to maximize routing space in the dense switch matrix, making this a genuinely tight design. The board_size violation (143x111mm > 100x100mm) is also correctly flagged.

### Incorrect
- The thermal_pad_vias section lists all SW1-SW31 hotswap socket pads (e.g., SW1 pad 6 'col5', SW10 pad 5) and flags them as having 'adequacy=none' (no thermal vias). These are electrical hotswap retention/signal pads on Kailh Choc hotswap sockets, not thermal pads requiring via stitching for heat dissipation. The SK6812 Mini-E LED pads may have larger area, but the pads flagged (2.19x3.08mm to 2.21x2.88mm) are standard hotswap electrical pads. True thermal pads (e.g., on power ICs) would require different context — a keyboard hotswap socket carries no significant heat load.
  (thermal_pad_vias)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001369: Main gerber set correctly identified: 7 layers, 731 total holes, 418 vias cross-validates with PCB; PTH drill tool T6 (1.6993mm) defined with hole_count=0 — unused tool not flagged

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerbers_SofleChocWireless
- **Created**: 2026-03-24

### Correct
- layer_count=2, 7 gerber files (F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, Edge.Cuts) plus 2 drill files. total_holes=731 (418 vias + 191 component + 122 mounting = 731). The 418 via count exactly matches the PCB analyzer. F.Paste correctly listed as missing_recommended since keyboard switches have no SMD paste requirements on the signal pads.

### Incorrect
- In the PTH drill file, tool T6 (diameter 1.6993mm) has hole_count=0. This is a defined but unused drill tool, which is unusual and may indicate a leftover from a design revision. The analyzer captures this data correctly in the raw drills section but does not surface a warning or anomaly for a tool defined with zero holes. This edge case should ideally be noted as a potential design artifact.
  (drills)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001370: Bottom plate gerbers correctly identified: minimal copper fill, 5 PTH mounting holes; Mounting holes on bottom/top plates classified as 'component_holes' instead of 'mounting_holes'

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerbers_SofleChocWirelessBottomPlate
- **Created**: 2026-03-24

### Correct
- layer_count=2, total_holes=5, all at 2.1996mm diameter (M2 holes drilled at ~2.2mm for clearance fit). The B.Cu and F.Cu layers have draw_count=1076/1075 which represents the copper fill artwork. The drill_NPTH extent is 0x0 (no NPTH holes), consistent with the PCB showing all holes as THT type. Gerber dimensions 143.38x111.75mm match the PCB.

### Incorrect
- The drill_classification shows 5 holes at 2.1996mm as component_holes with mounting_holes.count=0. Mounting holes for M2 screws (2.2mm drill) should be classified as mounting_holes, not component_holes. The X2 attribute says 'Plated,PTH,ComponentDrill' because KiCad exported the unconnected TH pads as PTH rather than NPTH. However the analyzer should detect that 2.2mm+ unconnected holes are mounting holes. The same misclassification occurs in the TopPlate gerber output.
  (drill_classification)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001371: Top plate gerbers correctly report same dimensions and hole count as bottom plate; B.SilkS and F.SilkS layers have zero draws on top/bottom plates but are included in layer set

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerbers_SofleChocWirelessTopPlate
- **Created**: 2026-03-24

### Correct
- Top plate dimensions 143.37x111.75mm, 5 holes at 2.1996mm, layer set complete with F.Paste missing. The F.Cu and B.Cu draw_counts (8868 each) are much higher than the bottom plate (1076) reflecting the key cutout geometry drawn in copper for the switch plate. Edge.Cuts has 170 draw operations vs 36 for the bottom plate, consistent with more cutouts in the top plate outline.

### Incorrect
(none)

### Missed
- For both the top and bottom plate gerbers, the B.SilkS and F.SilkS files have draw_count=0 and flash_count=5 (just pad flashes from the mounting holes). Including empty silkscreen layers inflates the gerber file count and is a minor completeness false positive — the plates are visually blank silkscreen. The analyzer marks completeness.complete=true and does not note that the silk layers contain no actual silkscreen content. A warning about blank silk layers would be useful.
  (completeness)

### Suggestions
(none)

---
