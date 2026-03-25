# Findings: Kicad-Hardware-SMD / HARDWARE_GitHub2

## FND-00000788: Triple-rail power supply (L7805/L7812/L7912) with 22 components correctly parsed; C4 (capacitor) appears on both pin 1 and pin 2 of the same net (__unnamed_3) — shorted cap not flagged; power_rails...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_GitHub2.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Three linear regulator subcircuits detected. Component counts correct: 3 ICs (U1=L7805, U2=L7812, U3=L7912), 12 caps, 4 diodes (1N4007 in D_SMA footprint), 3 connectors. All SMD footprints despite 1N4007 (THT in description) — footprint correctly overridden to D_SMA.

### Incorrect
- In net __unnamed_3, C4 pin_number '1' and pin_number '2' are both listed on the same net, meaning C4 is shorted. This is a real design bug — both terminals of C4 connected to the same net. The analyzer correctly extracted the net data but does not flag this as a short-circuit or anomaly.
  (signal_analysis)
- The schematic uses an unnamed GND net (not connected to a named GND power symbol), so GND does not appear in power_rails. The actual GND net (__unnamed_3) includes U1 IN and GND pins on the same net, which is suspicious. The L7912 negative regulator's ground topology is complex and the unnamed-net handling obscures it.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000789: All-SMD board with 22 components, 2-layer routing, 16 vias correctly analyzed; net_analysis in gerber shows 9 nets but PCB shows 8 — one-net discrepancy unexplained

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: HARDWARE_GitHub2.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- smd_count=22, tht_count=0. copper_layers_used=2 (F.Cu+B.Cu). 16 vias all 0.3mm drill (matching gerber). net_count=8 matches schematic's 8 nets. Routing complete.

### Incorrect
- PCB output reports net_count=8, but gerber net_analysis shows total_unique=9. The gerber sees the 'N/C' net as a signal net in addition to the 8 design nets. This is consistent (N/C is likely a no-connect marker net), but the discrepancy between the two analyzers is not flagged anywhere.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000790: Alignment flagged false (8.4mm width variance) — false positive for SMD board with components not filling full board area; All-SMD board correctly detected: smd_ratio=1.0, 16 via-only PTH holes, 0 ...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: GERBER.json
- **Created**: 2026-03-23

### Correct
- pad_summary shows smd_apertures=55, tht_holes=0, smd_ratio=1.0. The 16 PTH drills are all 0.3mm ViaDrill, correctly classified as vias not component holes. Complete 9-layer gerber set present.

### Incorrect
- Similar to Kicad-Hardware-Design: copper extent is smaller than board outline because components cluster in one area. B.Cu (25.1x26mm) and F.Cu (27.6x25.8mm) vs Edge.Cuts (33.5x30mm). The board outline is larger than the populated area — this is a normal design choice, not a Gerber misalignment.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
