# Findings: USB-Mouse / Mouse

## FND-00001927: Component count, BOM groupings, and component types all correct; LQ1 (Optical_Mouse:LQ, value='EL') misclassified as 'inductor'; USB differential pair D+/D- not detected; D+ net missing from nets d...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_USB-Mouse_Mouse.sch.json
- **Created**: 2026-03-24

### Correct
- 31 components correctly parsed matching PCB footprint count exactly. Component types: 3 switches (SW1/SW2/SW3), 1 connector (J1), 11 resistors, 8 capacitors, 1 inductor, 2 LEDs (LD1/LD2), 1 IC (U1), 4 jumpers (JP1-JP4). All 31 references accounted for in BOM groups.

### Incorrect
- LQ1 from lib 'Optical_Mouse:LQ' with value 'EL' is classified as type='inductor'. The 'LQ' prefix triggered the inductor heuristic (L prefix). However, from context it is a custom optical encoder/sensor component in a custom library specific to this mouse design — not an inductor. The value 'EL' (electroluminescent?) and lib name 'Optical_Mouse:LQ' both indicate it is a sensor/emitter element, not an inductor. It should be classified as 'ic' or left as unknown rather than inductor.
  (components)

### Missed
- The schematic has two global labels for 'D+' and two for 'D-', representing USB data lines. D- appears correctly in the nets dict (connected to R7 and C8). However, 'D+' does not appear in the nets dict at all despite appearing in the labels array. Because D+ is absent from nets, the differential pair detector cannot match D+ and D- and reports differential_pairs=[]. The D+ net is effectively lost in the legacy KiCad5 net resolution. The net classification also has no entry for D+ (returns None). The design has classic USB low-speed/full-speed signaling with 270Ω pull-down resistors (R7, R8).
  (design_analysis)
- The design has multiple decoupling capacitors on the VCC supply rail used by the optical sensor IC (U1). C14 (4.7uF) and C15 (0.1uF) are bulk/bypass on VCC, C8 and C9 (0.01uF each) are high-frequency bypass. However signal_analysis.decoupling_analysis=[] and design_observations=[] — no decoupling coverage analysis was generated. This is likely because VCC is a global label in the design (not a power symbol), and the decoupling analyzer does not connect the caps to the VCC rail.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001928: PCB stats, single-layer routing, footprint count, and dimensions all correct

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_USB-Mouse_Mouse.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- 31 footprints matching schematic exactly. Single copper layer (F.Cu only) with 212 track segments. Board dimensions 39×78mm. 18 SMD + 13 THT footprints (mix including THT axial components for the through-hole design). Routing complete, 0 unrouted. 2 copper fill zones. DFM tier=standard, min track 0.2mm, no violations.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
