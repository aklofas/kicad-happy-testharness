# Findings: hkzlab/PS1_DatelCheatCart_Clone / PowerReplay

## FND-00001061: T1 (L78L05 linear regulator) classified as 'transformer' instead of 'ic' or 'regulator'; bus_topology 'width' field reports bus-entry-count not signal-count; Component count, BOM, nets, and power r...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PowerReplay.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 14 total components, 78 nets, power rails +7.5V/GND/VCC all correctly identified. No-connects (24) and decoupling caps identified correctly on the right rails.
- 25 multi-driver nets detected: U2 and U7 are two GAL16V8s with shared tri-state outputs (IO1-IO8) on the same nets. This is valid detection — the shared outputs are by design (SW1 selects between configurations), but the analyzer correctly identifies the electrical ambiguity.

### Incorrect
- T1 uses lib_id 'Regulator_Linear:L78L05_TO92' and has description 'Positive 100mA 30V Linear Regulator, Fixed Output 5V, TO-92', but type and category are both set to 'transformer'. This is a reference prefix misclassification — 'T' prefix is being assumed to mean transformer. The regulator is also absent from signal_analysis.power_regulators despite being clearly identifiable from the lib_id.
  (signal_analysis)
- The A bus is reported as width=68 with range A0..A20 (21 actual signals). The D bus is width=42 with range D0..D7 (8 signals). XCVR_B is width=26 with range XCVR_B0..XCVR_B7 (8 signals). The 'width' field is being populated with a count of bus entry elements rather than the number of unique signals in the bus, making it meaningless and misleading.
  (signal_analysis)

### Missed
- T1 is an L78L05 5V linear regulator with a +7.5V input rail and VCC output rail plus decoupling caps (C3 on +7.5V, C1/C2 on VCC). The power_regulators list is empty. This is partly caused by the wrong 'transformer' type classification, but also indicates the detector doesn't recognise this regulator circuit.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001062: Board outline parser misses gr_poly edge and reports only 4 corner circles; Routing completeness, layer stack, footprint counts, and net count correctly reported; Courtyard overlap detection correc...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PowerReplay.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 14 footprints (13 front/1 back), 2 copper layers, 1335 track segments, 54 vias, 4 zones, 76 nets, routing_complete=true with 0 unrouted nets all match expected values for this design.
- 9 courtyard overlaps reported including J2/SW1 (88.6mm2), U4/U2 (38.2mm2), and others. These are artifacts of the schematic coordinates being used — the PCB layout is separate and the overlap detection appears to work from schematic placement coordinates, not PCB. The PCB footprint overlaps reflect actual PCB placement data from courtyard fields in the PCB file.
- GND zone on both B.Cu and F.Cu (2918mm2, 2 stitching vias) and VCC zone on B.Cu (203.4mm2, 3 vias) correctly identified in thermal_analysis.
- min_track_width=0.2mm, min_spacing~0.22mm, min_drill=0.3mm — all within standard DFM tolerances. Correctly assigned dfm_tier='standard'.

### Incorrect
- The PCB board outline contains one gr_poly (a 13-point polygon defining the actual PS1 cartridge shape with notch) and 4 gr_circle (mounting/corner holes). The analyzer reports edge_count=4 with all edges as 'circle', completely missing the gr_poly. The bounding box dimensions (52.1x58.9mm) happen to be correct because they are derived from the component/via extent rather than outline geometry, but the board shape is not captured.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
