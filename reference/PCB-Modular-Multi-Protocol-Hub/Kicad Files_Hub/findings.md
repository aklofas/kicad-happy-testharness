# Findings: PCB-Modular-Multi-Protocol-Hub / Kicad Files_Hub

## FND-00000225: Multi-Protocol Hub (167 components). Correct: 2 crystals, 2 transistors, 1 ethernet PHY, 2 voltage dividers, 3 regulators. False positive: MCP73871 battery charger classified as BMS (it's a charger, not BMS). RC filter overcounting: Ethernet termination network (R51-R54 50ohm + shared C58) generates 4 phantom filter detections. Protection device count conflates physical parts with protected nets (9 reported, 5 actual parts).

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Kicad Files_Hub.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- Y2 16MHz and Y3 25MHz crystals correctly identified with proper load capacitance calculations
- Q1 FDN340P PMOS and Q2 BC817 BJT correctly identified with proper pin assignments and driver ICs
- U12 LAN8720A Ethernet PHY correctly detected
- 2 voltage dividers correctly identified: R60/R59 (ratio 0.909) and R21/R22 (ratio 0.25 for U10 VPCC)
- 3 power regulators correctly detected (U3, U4, U6)

### Incorrect
- RC filter overcounting: C58 (0.1uF) shared by R51-R54 (50ohm Ethernet terminators) generates 4 separate filter detections. These are impedance matching/termination, not discrete RC filters.
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- Reclassify MCP73871 as battery_charger, not bms_system
- Deduplicate RC filters sharing a common capacitor (Ethernet termination networks)
- Report protection_devices as both physical part count and protected net count separately

---
