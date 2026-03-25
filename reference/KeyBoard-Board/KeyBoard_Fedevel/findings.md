# Findings: KeyBoard-Board / KeyBoard_Fedevel

## FND-00000674: RP2040 MCU, W25Q128 flash, crystal circuit, and USB Type-C compliance checks all detected correctly; Key matrix detector reports 3 rows in top-level schematic but design has 4 rows (ROW0–ROW3); USB...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KeyBoard_Fedevel.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- U1 RP2040 detected with correct power rails (+3V3, +1V1, +3V3_A). W25Q128 QSPI memory interface detected with 6 shared signal nets. Crystal Y1 (ABM8 12MHz) with 15pF load caps → 10.5pF effective load, in range. USB-C J101 CC1/CC2 pulldowns pass. Reset RC filter R11+C20 at 58.95 kHz cutoff correct (27R × 100nF).

### Incorrect
- The top-level schematic has nets /dd7bb189.../ROW0 through /dd7bb189.../ROW3 all with the same UUID prefix, each carrying 3 diodes. The detector found only ROW0–ROW2 (3 rows × 3 cols = 9 estimated keys, but reported 13) and missed ROW3 which holds the encoder click switches D16/D17/D18. The Switch sub-sheet correctly detects 4×3 = 12 keys. The top-level schematic should also report 4 rows.
  (signal_analysis)
- usb_esd_ic check correctly passes (U4 USBLC6-2P6 detected), but vbus_esd_protection fails. The USBLC6-2P6 has pin 5 (VBUS) connected to the VBUS net — this chip explicitly provides VBUS ESD clamping. The two checks are contradictory; the VBUS protection check appears to look for a separate discrete TVS/zener rather than recognising VBUS protection via the USBLC6 IC itself.
  (signal_analysis)
- The design_observation says missing_caps: {output: '__unnamed_2'}, but C35 (10uF) and C16 (100nF) are both on __unnamed_2 (the LDO output net). The caps exist and are correctly wired; the checker failed to find them. Separately, the decoupling_analysis section omits __unnamed_2 entirely — only named power rails appear there. Both the cap-detection and the decoupling analysis drop caps on unnamed nets.
  (signal_analysis)
- The PCB silkscreen documentation_warnings lists S1–S18, SW3–SW7 as switches lacking function labels. For a keyboard PCB, switch function is defined entirely by key position and keycaps; asking for ON/OFF/RESET/BOOT labels on every key switch is inappropriate. This check should be suppressed when a key_matrix is detected.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000675: Switch sub-sheet correctly detects 4×3 key matrix with 12 keys and 12 diodes

- **Status**: new
- **Analyzer**: schematic
- **Source**: Switch.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Switch sheet key_matrix: rows=4 (ROW0–ROW3), columns=3 (COL0–COL2), 12 switches, 12 diodes, detection_method=net_name. Matches the physical layout of S1–S18 keys (some unpopulated) plus 3 encoder click switches.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000676: 4-layer stackup, 124 footprints, fully routed, RP2040 thermal pad with 5 vias, and GND planes on In1/In2 all correctly detected; J101 USB-C connector edge clearance of 0.05mm correctly flagged as a...

- **Status**: new
- **Analyzer**: pcb
- **Source**: KeyBoard_Fedevel.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- copper_layers_used=4 (F.Cu, In1.Cu/GND_1, In2.Cu/GND_2, B.Cu). footprint_count=124 matches schematic. routing_complete=true, unrouted=0. RP2040 U1 thermal pad (pad 57, 3.2×3.2mm, 10.24mm²) with 5 nearby thermal vias correctly reported.
- J101 is 0.05mm from the board edge on B.Cu — extremely close and likely intentional for a flush-mount USB port, but the analyzer correctly identifies this as worth noting. This is a real finding.
- Single DFM violation: board_size 73.144×111.862mm exceeds the 100×100mm threshold. This is accurate — the board needs the larger panel pricing tier at JLCPCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
