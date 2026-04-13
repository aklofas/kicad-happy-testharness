# Findings: Bastardkb/TBK-Mini-PCB-plate / flex

## FND-00001595: Component count (81), key matrix detection, and addressable LED detection are accurate; Assembly complexity reports 81 SMD / 0 THT instead of ~40 SMD / 41 THT; Addressable LED chains: 3 chains repo...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_TBK-Mini-PCB-plate_flex_flex.kicad_sch
- **Created**: 2026-03-24

### Correct
- The schematic correctly identifies 81 components: 18 switches (SW_MX_reversible), 54 diodes (18 SOD-123 matrix diodes + 36 SK6812MINI-E LEDs split as 'diode:18, led:36'), 5 connectors, 2 capacitors, 2 resistors. Key matrix detected: 4 rows × 6 columns, 18 switches, 18 matrix diodes — correct for an 18-key compact keyboard PCB. Two addressable LED chains of 18 LEDs each (36 total) correctly identified as SK6812MINI WS2812-protocol LEDs.

### Incorrect
- The assembly_complexity section reports smd_count=81 (all components) and tht_count=0. In reality, the 18 key switches (custom:SW_MX_reversible) and 18 matrix diodes (custom:Diode_TH_SOD123, named with 'TH_' prefix) are through-hole, along with 5 connectors (PinHeader_2.54mm THT). Only the 36 SK6812MINI-E LEDs, 2 SMD capacitors, and 2 SMD resistors are SMD (~40 SMD). The analyzer fails to classify custom library footprints with 'TH_' prefix as THT, defaulting them to SMD. The PCB analyzer correctly reports 4 SMD and 77 THT.
  (assembly_complexity)
- The signal_analysis.addressable_led_chains reports 3 chains: two with chain_length=18 (both starting at D28 on net __unnamed_35) and one chain_length=1 starting at D3. Total LEDs across chains = 18+18+1 = 37 but the schematic has exactly 36 LEDs. The 1-LED chain for D3 appears to be the start of one of the two 18-LED chains detected via a different traversal path, not a separate chain. Two physical chains of 18 LEDs each (one per side of the reversible PCB) is the correct topology.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001596: PCB statistics, layer usage, and DFM tier are accurate for a thin flex keyboard plate; SMD and THT counts from PCB correctly reflect actual footprint types

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_TBK-Mini-PCB-plate_flex_flex.kicad_pcb
- **Created**: 2026-03-24

### Correct
- PCB correctly reports: 85 footprints (77 THT, 4 SMD, 4 board_only graphics), 2-layer board, 2004 track segments, 174 vias, 0 zones, board 126.31×90.634 mm, routing complete, 51 nets. Board thickness of 0.6 mm is consistent with a flex PCB keyboard plate. DFM tier 'advanced' due to 0.1 mm annular rings on the small vias (0.2 mm drill / 0.4 mm pad) used for switch reversibility routing.
- The PCB reports smd_count=4 and tht_count=77, which is consistent with the actual design: 4 SMD footprints (the SK6812MINI-E LEDs or SMD capacitors/resistors seen in PCB context) and 77 THT footprints (switches, matrix diodes, connectors). This is in stark contrast to the schematic assembly_complexity which wrongly says 81 SMD / 0 THT.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001915: Keyboard matrix correctly detected: 4×6 layout with 18 actual keys; Component types correctly classified: 18 diodes, 36 SK6812MINI LEDs, 18 switches; addressable_led_chains reports 3 chains (length...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TBK-Mini-PCB-plate_TBK-mini_plate_flex.kicad_sch
- **Created**: 2026-03-24

### Correct
- key_matrices detects 4 row nets (row2, row3, row4, row5) and 6 column nets (col1–col6), estimated_keys=18 matching switches_on_matrix=18 and diodes_on_matrix=18. The 4×6 = 24 positions with 18 populated keys is accurately characterized. The detection_method=net_name is appropriate for this design which uses explicit row/col net labels.
- The 18 plain diodes (value 'D', footprint custom:Diode_TH_SOD123) are correctly classified as diode=18. The 36 SK6812MINI addressable LEDs are correctly classified as led=36. The 18 MX key switches are correctly classified as switch=18. Total 81 components (2+18+18+36+5+2) matches total_components=81.
- The reverse-mounted SK6812MINI-E design has 18 nets where two LEDs share a DOUT connection (dual-chain topology with branch points). The analyzer correctly identifies these as multi_driver conflicts. Each entry correctly names the component references and pin numbers. These reflect real ERC flags in the KiCad design.

### Incorrect
- The 36 SK6812MINI LEDs form two chains of 18 each. The analyzer finds three chains: chain1 (18 LEDs, first=D28), chain2 (18 LEDs, first=D28), and chain3 (length 1, D3). Chains 1 and 2 share the same data_in_net (__unnamed_35) and start node D28, indicating a duplicate traversal from a branch point rather than two genuinely separate chains. D3 is isolated as a single-LED chain, suggesting a topology traversal error. Together the three chains cover all 36 unique LEDs (chain1 ∪ chain2 ∪ chain3 = 36 unique), so coverage is complete but the chain decomposition is wrong.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001916: PCB statistics correct: 85 footprints, 4 SMD, 77 THT, routing complete; DFM annular ring violation correctly identified; board_size DFM violation uses tier_required='standard' for an oversized board

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: TBK-Mini-PCB-plate_TBK-mini_plate_flex.kicad_pcb
- **Created**: 2026-03-24

### Correct
- footprint_count=85 matches source (77 through_hole + 4 smd + 4 board_only = 85). smd_count=4 (C1, C2, R1, R2 with SMD footprints) and tht_count=77 are correct per source attrs. The SK6812MINI LEDs use custom footprints marked (attr through_hole) in the PCB file, which the analyzer correctly reads. net_count=51, routing_complete=true, via_count=174 are correct.
- min_annular_ring=0.1 mm correctly detected. This is at the advanced tier limit (0.1 mm) and below standard (0.125 mm), so tier_required=advanced is correct. dfm_tier=advanced is correctly set.

### Incorrect
- The board is 126.31×90.634 mm, exceeding JLCPCB's 100×100 mm standard-pricing boundary. The violation message correctly says 'higher fabrication pricing tier', but tier_required='standard' is counterintuitive and misleading — it implies the board meets standard requirements, when in fact exceeding 100×100 mm triggers a pricing premium. The field should indicate 'premium' or equivalent to clearly communicate the impact.
  (dfm)

### Missed
(none)

### Suggestions
(none)

---
