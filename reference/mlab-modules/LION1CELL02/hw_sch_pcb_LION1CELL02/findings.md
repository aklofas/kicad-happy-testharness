# Findings: mlab-modules/LION1CELL02 / hw_sch_pcb_LION1CELL02

## FND-00000805: Unrouted PCB correctly detected: 0 track segments, 69/77 nets unrouted, board_outline empty

- **Status**: new
- **Analyzer**: pcb
- **Source**: hw_sch_pcb_LION1CELL02.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The PCB file contains component placement only with no routing. The analyzer correctly reports routing_complete=false, unrouted_net_count=69, copper_layers_used=0, board_width_mm=null, and edge_count=0. This matches the actual PCB file which has no (segment) entries.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000806: BMS system not detected despite BQ34Z100 fuel gauge + BQ25628E charger + BQ29700DSER protection IC; USB-C compliance check for J1 correctly identifies missing VBUS ESD protection; Switching regulat...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_LION1CELL02.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- USB-C connector J1 (USB4105-GF-A) has CC1/CC2 5.1k pulldowns (pass), VBUS decoupling (pass), but no VBUS ESD protection (fail). The analyzer correctly identifies this gap with 1 fail, 3 pass, 3 info.
- U3 detected as switching topology with L2 inductor, +VSW input, +3.3V output, feedback via R8/R9 voltage divider (511k/91k). Estimated Vout=3.308V from Vref=0.5V lookup. This is accurate for the TPS631000.

### Incorrect
- P1/P2 cross +BATT to +3.3V domains. BQ34Z100 has open-drain IO pins that are tolerant of 3.3V pull-ups even when running from higher BATT voltage (typical Li-ion 3.7-4.2V). The level-shifter flag fires because the power domain voltages differ, but the open-drain topology makes this safe without a dedicated level shifter.
  (signal_analysis)

### Missed
- The design is explicitly a Li-ion BMS (title: 'Single cell Li-ion battery management with USB-C charger'). U1=BQ34Z100 (fuel gauge), U2=BQ25628E (charger), U5=BQ29700DSER (cell protection). bms_systems=[] in signal_analysis. The BMS detector apparently does not recognize these TI BQ-series parts.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000807: board_dimensions is empty dict {} because Edge.Cuts gerber has 0 draws and no gbrjob board size

- **Status**: new
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The LION1CELL02 Edge.Cuts gerber file contains 0 apertures and 0 draws — the board outline is genuinely absent from the gerber set. The gbrjob file has board_width_mm=0.0, board_height_mm=0.0. The board dimensions are therefore not determinable, which is correctly indicated by board_dimensions={}. However, the gerber analyzer reports complete=true (from gbrjob) while the board is clearly incomplete/placeholder, which is misleading.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
