# Findings: ThumbsUp / a44key-pcb

## FND-00001546: GND net lists U1 VCC-named pins; VCC net lists U1 GND-named pins; Crystal circuit detector incorrectly includes C11 (0.1uF bypass cap) as a crystal load capacitor; Key matrix estimated_keys reporte...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: a44key-pcb.sch.json
- **Created**: 2026-03-24

### Correct
- The schematic source contains exactly these component counts and the analyzer statistics match: ic=1 (U1 ATmega32U4-AU), resistor=5 (R1-R5), capacitor=10 (C1-C9, C11), switch=23 (MX1-MX22 + SW1 reset button), connector=5 (J1 audio jack + J2/J3/J4 pin headers + USB1), diode=22 (D1-D22), fuse=1 (F1 polyfuse), crystal=1 (Y1 16MHz), jumper=1 (Right-Left1/JP1). All match the source schematic.
- The differential_pairs section correctly identifies D+ and D- as a USB differential pair with USB1 as the shared IC and R1/R2 as the series resistors. This matches the schematic where R1 (22 ohm) is on D- and R2 (22 ohm) is on D+, both between the ATmega32U4 USB pins and the Molex USB connector.
- The protection_devices section reports F1 (Polyfuse) protecting the +5V rail with clamp_net=VCC, which matches the schematic where F1 sits between the +5V rail (from USB VBUS) and the VCC rail that powers the ATmega32U4.
- The three power rails in the schematic are +5V (USB input power), GND (ground), and VCC (regulated supply to MCU), all correctly identified in statistics.power_rails.

### Incorrect
- In the nets section, the GND net contains U1 pin 14 (pin_name='VCC'), pin 34 (pin_name='VCC'), and pin 2 (pin_name='UVCC'). The VCC net contains U1 pin 15 (pin_name='GND'), pin 23 (pin_name='GND'), pin 35 (pin_name='GND'), and pin 43 (pin_name='GND'). This is a KiCad 5 legacy parser artifact: the ATmega32U4-AU symbol has GND and VCC pins that are listed in multiple groups; the parser appears to map pin_names from the symbol library data but assigns them to the net name the pin is actually connected to via wire routing. The result is that GND net entries show VCC pin names and vice versa for U1's power pins, which would confuse any downstream analysis reading pin_name fields from the nets section.
  (nets)
- The crystal_circuits entry for Y1 (16MHz) lists three load capacitors: C3 (22pF), C11 (0.1uF on net '__unnamed_30'), and C2 (22pF). C11 is a 0.1uF decoupling capacitor connected to U1 pin 42 (AREF) and GND, not a crystal load cap. C11 and C3 share the same unnamed net number in this output (__unnamed_30), but in the schematic C11 is actually on the AREF bypass net while C2 and C3 are the actual crystal load caps on XTAL1/XTAL2 nets. The effective_load_pF calculation of 25pF is also wrong as a result — true effective load is approximately (22pF series 22pF) / 2 + stray ~14pF, not involving C11.
  (signal_analysis)
- The key_matrices detector reports estimated_keys=25 and switches_on_matrix=25 for a 4-row x 6-column matrix. However, the schematic has exactly 22 MX switches (MX1-MX22). The discrepancy arises because the detector is using row_count x col_count (4x6=24) as an estimate and then adding 1, rather than counting actual switch instances. Furthermore, MX4 and MX8 are thumb keys that connect to TH35/TH34 nets rather than the standard ROW nets, making the actual matrix 22 keys with 2 using special connectors.
  (signal_analysis)
- The bus_analysis.i2c section reports an I2C bus on the SCL net with only U1 connected and no SDA net present. In the schematic, 'SCL' is used as a net label on the ATmega32U4's PC0/SCL pin and appears on an audio jack connector (J1 pin area), not as an actual I2C bus. A single net named 'SCL' without a corresponding 'SDA' net and without any I2C peripheral devices attached does not constitute an active I2C bus. The design_observations section also flags this i2c_bus as having no pull-up, reinforcing that it is not a real I2C bus.
  (design_analysis)
- The analyzer processed '_autosave-a44key-pcb.sch', a KiCad internal autosave file. This file is not a real design file and duplicates the content of a44key-pcb.sch with minor differences (total_nets shows 28 vs 88 for the real file, and 12 no-connects vs 11). Autosave files should be excluded from analysis the same way .sch-bak files are excluded, as they produce redundant and potentially incorrect outputs that pollute the results.
  (file)
- The key_matrices detector shows 4 rows (ROW0–ROW3) and 6 columns (COL0–COL5). ROW3 in the schematic has only D4 and D8 anodes, which are the two thumb keys (MX4/MX8) connecting via TH35/TH34 to external connectors J2/J3/J4, not traditional matrix rows. Counting ROW3 as a full matrix row inflates the estimated key count. The true orthogonal matrix is 3 rows x 6 columns = 18 keys plus 4 additional keys in rows 0–2 columns 5 (D17/D20/D4-like) and the two thumb keys using non-standard routing.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001547: PCB statistics correctly parsed: 69 footprints, 2-layer board, 44 vias, fully routed; ATmega32U4 correctly identified on B.Cu (back copper) as SMD; MX keyboard switch footprints correctly identifie...

- **Status**: new
- **Analyzer**: pcb
- **Source**: a44key-pcb.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB has 69 footprints matching the schematic component count, is a 2-layer design (B.Cu + F.Cu), has 44 vias, 816 track segments, and routing_complete=true with 0 unrouted nets. Board dimensions 116.713 x 103.886mm are consistent across all PCB files for the main board.
- U1 (ATmega32U4-AU, TQFP-44) is correctly placed on B.Cu layer as an SMD component with 44 pads, matching the physical design where the MCU is on the back of the keyboard PCB.
- The MX-Alps-Choc hybrid switch footprints have 15 pads each (3 for Alps, 3 for MX, 3 for Choc, plus stabilizer holes and mounting pins) and are correctly classified as through_hole type on F.Cu. This matches the MX_Alps_Hybrid:MX-Alps-Choc-X-1U-NoLED footprint.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001548: Bottom plate PCB correctly parsed as empty board with no footprints or copper

- **Status**: new
- **Analyzer**: pcb
- **Source**: a44key-pcb-bottom-plate.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The bottom plate file contains only an Edge.Cuts outline with no components or copper routing, which is correct for a keyboard bottom plate PCB. footprint_count=0, track_segments=0, via_count=0, net_count=0 are all accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001549: Left-hand PCB correctly has same component count (69) and board dimensions as right-hand version

- **Status**: new
- **Analyzer**: pcb
- **Source**: a44key-pcb-left-hand.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The left-hand PCB variant has 69 footprints and the same 116.713 x 103.886mm board dimensions as the right-hand version, consistent with it being a mirrored version of the same design with 49 vias vs 44 in the right-hand version (slightly different routing).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001550: Gerber alignment 'misalignment' flagged for keyboard PCBs is a false positive

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerbers_RightHand.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The RightHand, LeftHand, and ThumbKeys gerber sets are all flagged as aligned=false with issues like 'Width varies by 7.1mm across copper/edge layers'. For keyboard PCBs with mounting holes and irregular shapes, it is expected that copper/component extents are smaller than the board outline, since mounting holes at edges and the irregular thumb cutouts push the Edge.Cuts boundary beyond where any copper lands. The NPTH drill extents being 95.25mm vs 116.7mm Edge.Cuts width is a clear example of mounting holes spanning the full board width. This is a systematic false positive for keyboard-style boards.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001551: Back panel gerbers correctly identified as incomplete (no PTH drill file, only NPTH with 0 holes)

- **Status**: new
- **Analyzer**: gerber
- **Source**: Gerbers_BackPanel.json
- **Created**: 2026-03-24

### Correct
- The BackPanel gerber set is for a mechanical bottom plate with no components. complete=false because has_pth_drill=false, which is accurate — the BackPanel has only mounting holes (NPTH) and no component placement, so no PTH drill file exists. The NPTH file has 0 holes because the actual mount holes are already part of the main board outline.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001552: ThumbKeys gerber correctly identified as a separate smaller PCB (39.1 x 19.3mm)

- **Status**: new
- **Analyzer**: gerber
- **Source**: Gerbers_ThumbKeys.json
- **Created**: 2026-03-24

### Correct
- The ThumbKeys gerber set covers a separate small thumb cluster PCB of 39.12 x 19.3mm, which is correct for the a44key-pcb-thumbs PCB containing only a few thumb switches. The 20 total holes and 7 gerber files are consistent with a small 2-layer board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001902: Component count and BOM extraction correct; Power rails correctly identified; Protection device F1 (polyfuse) correctly detected on +5V rail; USB differential pair detected with series resistors; K...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_ThumbsUp_a44key-pcb.sch.json
- **Created**: 2026-03-24

### Correct
- Correctly identifies 69 real components (excluding 23 power symbols from 92 total $Comp entries): 1 ATmega32U4-AU IC, 22 MX-NoLED switches, 22 D_Small diodes, 10 capacitors, 5 resistors, 5 connectors, 1 crystal, 1 fuse, 1 jumper, 1 push-switch. All values, footprints, and lib_ids match the source. Wire count 136 and no-connect count 11 are both exact.
- Correctly identifies three power rails: +5V, GND, VCC. The +5V comes from USB through polyfuse F1, VCC is the regulated MCU supply, GND is the common ground. All three appear in the source schematic power symbols.
- F1 (Polyfuse, Fuse:Fuse_1206_3216Metric) is correctly identified as a protection device with protected_net='+5V' and clamp_net='VCC'. The fuse protects the USB 5V supply before it reaches the MCU VCC rail.
- Correctly identifies D+/D- as a USB differential pair with series resistors R1 (22Ω on D-) and R2 (22Ω on D+), no ESD protection. The Molex-0548190589 USB connector (USB1) is the shared IC. This matches the schematic: both 22Ω resistors are present between the MCU and USB connector.
- Correctly identifies a key matrix using net-name detection with 4 row nets (ROW0-ROW3) and 6 column nets (COL0-COL5). diodes_on_matrix=22 is accurate (D1-D22 all connect via their Anode to a ROW net). The detection method 'net_name' is appropriate for this design.

### Incorrect
- The analyzer reports switches_on_matrix=25 and estimated_keys=25, but there are exactly 22 MX-NoLED switches in the schematic (MX1-MX22). The overcounting arises because the code counts MX pin occurrences on COL nets (25 total pin instances) rather than unique MX component references. Three MX switches (MX1, MX17, MX20) have both their pin1 and pin2 on the same COL net, adding 3 extra pin counts: COL5 has 5 MX pin instances (MX1 both pins + MX2/3/4 pin1), COL1 has 4 (MX17 both pins + MX18/19 pin1), COL0 has 4 (MX20 both pins + MX21/22 pin1). True matrix size is 4×6 with 22 populated positions (ROW3 only has 4 keys: COL3-COL5 not present in row 3).
  (signal_analysis)
- The analyzer assigns C11 (0.1uF) to net __unnamed_30, the same unnamed net as crystal pin Y1:pin1 and load cap C3 (22pF). In the actual schematic, C11 pin2 connects via wire to the +5V power symbol, making it a +5V decoupling cap, not a crystal load capacitor. The net tracer in the KiCad 5 legacy parser fails to follow the wire from C11 pin2 (at schematic coords ~3000,3050) to the +5V symbol (at 2350,3000). As a result: (a) the effective_load_pF is reported as 25.0pF instead of the correct ~13.7pF (C2 and C3 only in series, ignoring C11); (b) the note incorrectly states 'CL_eff = (22pF * 0.1uF) / (22pF + 0.1uF) + ~3pF stray'.
  (signal_analysis)
- Because C11 pin2 is assigned to __unnamed_30 (the XTAL1 net) instead of +5V, C11 (0.1uF) does not appear in the +5V decoupling_analysis rail. The +5V rail shows only C7 (10uF) and C9 (1uF) for 2 caps / 11.0uF total. The correct count should be 3 caps / 11.1uF. This also causes the design_observation for +5V decoupling to report has_bypass=true based on C7/C9 (both >=1uF, not actually bypass range), when C11 at 0.1uF is the real bypass capacitor. Additionally, U1 UCAP pin (pin 6) is on isolated net __unnamed_23 not connected to C6, though C6 should decouple UCAP.
  (signal_analysis)
- The analyzer detects an I2C bus because a net named 'SCL' exists, connecting U1 pin 26 (PD6) to J1 pin 3 (audio jack ring contact). However, PD6 on the ATmega32U4 is a general GPIO (not the I2C/TWI clock pin — that is PD0). The designer used 'SCL' as a net label for the audio jack split signal, not for an I2C bus. The analyzer correctly notes has_pullup=false and pullup_resistor=null, but the bus classification itself is incorrect. There is no I2C bus in this design.
  (design_analysis)
- The schematic analyzer reports 88 total nets, but the KiCad PCB netlist (a44key-pcb.kicad_pcb) contains exactly 72 named nets (73 including net 0/unnamed). Of the 88 schematic nets, 53 are single-pin unnamed nets (__unnamed_0 through __unnamed_69), meaning the KiCad 5 legacy wire-tracing logic fails to merge connected wire segments into unified nets for over half of all net endpoints. The 16-net discrepancy (88 − 72 = 16) reflects un-merged wire junction points in the legacy .sch parser.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001903: Autosave schematic net count severely understated (28 vs 88) due to displaced power symbols

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_ThumbsUp__autosave-a44key-pcb.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The autosave differs from the main schematic only in the position of two power symbols (#PWR0103 GND and #PWR0116 GND), which are displaced to coordinates where they no longer connect to adjacent wires. This breaks net continuity and causes the net tracer to produce only 28 nets (vs 88 in the main file) even though all 69 components are present. As a secondary effect, key_matrices and crystal_circuits both report as empty because the matrix and crystal nets are not properly formed. The autosave also has 12 no-connects vs 11 in the main file (one extra NoConn marker at 5450 2550). This is a fundamental limitation: autosave files may be mid-edit states not suitable for analysis.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001904: Footprint count, board dimensions, and layer stack correct; DFM board-size violation correctly detected; Decoupling placement analysis correctly locates bypass caps near U1; Edge clearance warnings...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: repos_ThumbsUp_a44key-pcb.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Correctly reports 69 footprints matching the schematic component count. Board dimensions 116.713×103.886mm match the Edge.Cuts bounding box. Two copper layers (F.Cu, B.Cu) are correct. Net count 72 matches PCB source (73 net definitions minus net 0). routing_complete=true is correct (0 unrouted nets). The 'Power' net class with 0.5mm trace width for +5V/GND/VCC is correctly extracted.
- Correctly identifies that the 116.713×103.886mm board exceeds the JLCPCB 100×100mm standard-tier threshold. The violation message is accurate. min_track_width_mm=0.254 matches the net class default trace width. min_drill_mm=0.4 matches via_drill in the net class setup.
- Correctly identifies U1 (ATmega32U4-AU) on B.Cu and lists C11, C8, C1, C5, C6, C9 as nearby caps within 10mm. All shared-net pairings (GND, VCC) are correct. The closest cap at 8.18mm (C11) is physically accurate for a 0805 cap near a TQFP-44.
- USB1 (Molex-0548190589) at x=117.762 has edge_clearance_mm=-1.18, meaning the footprint courtyard extends 1.18mm beyond the nearest board edge. J4 (pin header) at x=86.614, y=139.192 shows -0.87mm. Both are intentional design choices (edge-mount USB and side connector), but the analyzer correctly surfaces them as placement warnings. J1 at 0.73mm positive clearance is also correctly not flagged as a violation.

### Incorrect
- The PCB file declares '(kicad_pcb (version 20171130) (host pcbnew "(5.1.4)-1"))'. The analyzer looks for a 'generator_version' token (used in KiCad 6+) which does not exist in KiCad 5 format. It should fall back to parsing the 'host' token to extract '5.1.4' or infer 'KiCad 5' from file_version=20171130. The schematic analyzer correctly reports '5 (legacy)' for the same project. All four PCB files in this repo are affected (both main boards, thumbs, and bottom plate).
  (kicad_version)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001905: Bottom plate PCB correctly reports zero footprints and tracks

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_ThumbsUp_a44key-pcb-bottom-plate.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The bottom plate PCB file explicitly states '(modules 0) (tracks 0) (nets 1)' in its general section. It is a pure mechanical boundary PCB used as a physical back panel/switch plate. The analyzer correctly reports footprint_count=0, track_segments=0, routing_complete=true. The board outline (116.713×103.886mm with 41 edge segments including 6 mounting-hole circles) is correctly parsed.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001906: Thumbs PCB correctly identified as a small 5-component board (39×19mm)

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_ThumbsUp_a44key-pcb-thumbs.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Correctly reports 5 footprints: MX8, MX4 (the two thumb keys), J2, J3, J4 (header connectors to main board). Board dimensions 39.116×19.304mm match the Edge.Cuts extent. routing_complete=true and unrouted_count=0 are correct. The small size explains why the gerber alignment checker sees large extents variation (mounting holes in NPTH span only 19.5mm width vs 39mm board width).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001907: Gerber layer set correctly identified as complete 2-layer board; Drill classification correctly counts vias, component holes, and mounting holes; Gerber alignment flagged as false positive for mech...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: repos_ThumbsUp_Gerbers_RightHand.json
- **Created**: 2026-03-24

### Correct
- Correctly identifies all 7 required gerber files (F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, Edge.Cuts) plus PTH and NPTH drill files. missing_required=[] is correct. F.Paste is correctly listed as only missing_recommended (no SMD paste stencil is needed since SMD components use reflow separately). Generator correctly extracted as 'KiCad,Pcbnew,(5.1.4)-1'.
- Via count=44 matches the PCB analyzer's via_count=44 for a44key-pcb.kicad_pcb. Component holes: 84 (12×1.0mm for 3-pin MX footprint stabilizer pins, 26×1.1mm for MX/Alps standard pins, 44×1.2mm for switch plate holes, 2×1.1mm NPTH). Mounting holes: 22×3.988mm NPTH, matching the keyboard case mounting pattern. Classification method 'diameter_heuristic' is appropriate.

### Incorrect
- The analyzer reports aligned=false with 'Width varies by 7.1mm across copper/edge layers' and 'Height varies by 7.1mm'. This occurs because copper features (THT key switch pads, SMD components) do not extend to the full board edge — the board outline includes a margin around the key grid. For a mechanical keyboard PCB where all components are interior to the board outline, copper layer extents will always be smaller than Edge.Cuts extents. The Gerbers are correctly aligned (all files use TF.SameCoordinates=Original); the variance is inherent to the design type, not a fabrication defect.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001908: Left-hand gerber via count matches left-hand PCB (49 vias)

- **Status**: new
- **Analyzer**: gerber
- **Source**: repos_ThumbsUp_Gerbers_LeftHand.json
- **Created**: 2026-03-24

### Correct
- Left-hand gerber reports drill_classification.vias.count=49, matching the PCB analyzer's via_count=49 for a44key-pcb-left-hand.kicad_pcb. The right-hand board has 44 vias vs left-hand 49 vias — the routing difference is expected since the boards are independent KiCad PCB files with different track layouts despite identical schematic.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001909: Back panel gerber correctly shows empty copper layers and no component holes; Back panel completeness=false is a false negative for a pure mechanical board; Back panel alignment correctly reported ...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: repos_ThumbsUp_Gerbers_BackPanel.json
- **Created**: 2026-03-24

### Correct
- The back panel is a mechanical plate with no components: the F.Cu and B.Cu gerber files contain only a header (14 lines each, no draw commands). The analyzer correctly reports total_flashes=0, total_draws=41 (all in Edge.Cuts), and drill_classification with all zero counts. The NPTH drill file is also empty (no holes defined — the mounting circles are only on Edge.Cuts, not drilled through a footprint).
- Unlike the populated boards, the back panel reports aligned=true with no issues. This is correct: all copper layers have zero extent (no features), so there is no variation to measure. The Edge.Cuts layer at 116.713×103.886mm is the only layer with content.

### Incorrect
- The analyzer marks complete=false because has_pth_drill=false (no PTH drill file exists). For a back panel PCB with zero components and zero footprints, the absence of a PTH drill file is expected and correct. The completeness check should recognize that boards with no footprints do not require PTH drill files. The board is actually complete for its purpose.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001910: ThumbKeys gerber alignment false positive — same mechanical keyboard pattern

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: repos_ThumbsUp_Gerbers_ThumbKeys.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- ThumbKeys gerber reports aligned=false with 'Width varies by 3.1mm' and 'Height varies by 6.9mm'. The Edge.Cuts is 39.116×19.304mm but copper features span only ~36×13mm because the MX key switch pads and connector pads are all interior to the board edge. The NPTH drill extent (19.5mm wide, 0.03mm tall) shows mounting holes on a single horizontal axis. This is a false positive for the same reason as RightHand and LeftHand: inherent to THT-dominant mechanical keyboard PCBs.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
