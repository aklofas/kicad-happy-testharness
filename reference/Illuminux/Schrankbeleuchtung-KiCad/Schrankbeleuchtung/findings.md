# Findings: Schrankbeleuchtung-KiCad / Schrankbeleuchtung

## FND-00001398: Component counts and types are accurate for all 33 components; Switching regulator (TPS560430) detected with correct topology and voltage mismatch correctly flagged; Voltage divider and LC filter c...

- **Status**: new
- **Analyzer**: schematic
- **Source**: Schrankbeleuchtung.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- statistics reports 33 total components: 9 connectors, 10 resistors, 2 ICs, 3 capacitors, 4 transistors, 4 mounting holes, 1 inductor. Manual BOM cross-check confirms: C1-C3 (3 caps), J1-J9 (9 connectors), L1 (1 inductor), Q1-Q4 (4 N-ch MOSFETs), R1-R10 (10 resistors), A1 (Pico 2 module), U1 (TPS560430), H1-H4 (4 mounting holes) = 33. All counts match the listed components array exactly.
- U1 TPS560430XDBVT is identified as a switching regulator with L1 (10uH inductor), +12V input, +5V output rail, and FB divider R9/R10. The estimated Vout of 2.499V (Vref=0.6V, R9=10k top, R10=3.16k bottom: 0.6*(1+10000/3160)=2.499V) is mathematically correct. The vout_net_mismatch observation correctly flags the 50% discrepancy between calculated Vout (~2.5V) and the +5V net name — a genuine design anomaly the analyzer correctly surfaces.
- R9/R10 voltage divider (10k/3.16k, ratio 0.240) is detected as both a voltage_divider and feedback_network feeding U1's FB pin — accurate. LC filter (L1 10uH + C3 0.1uF, resonant at 159.15 kHz) is detected for the switching converter output filter — correct topology for a TPS560430 design. Four N-channel MOSFETs (Q1-Q4 IRLML0030TRPBF) are correctly detected as transistor_circuits with gate resistors R1-R4 (187R each) driving LED channel outputs.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001399: PCB dimensions, layer count, and routing completeness are accurate

- **Status**: new
- **Analyzer**: pcb
- **Source**: Schrankbeleuchtung.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Board dimensions 55.0x45.0mm match the gbrjob file (55.05x45.05mm — minor gbrjob rounding difference is expected). 2-layer design (F.Cu + B.Cu), fully routed (unrouted_net_count=0), 33 footprints all on front side, 12 vias, 82 zones (mostly GND pour). DFM tier standard with zero violations. Connector J1 edge clearance of -4.0mm correctly flagged (barrel jack overhangs the board edge by design for panel mount).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001400: Gerber alignment check reports false negative due to including non-copper layers in extent comparison

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Schrankbeleuchtung-GBR.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- aligned=false is triggered because B.Mask (50.5mm) and F.Mask (50.5mm) are narrower than Edge.Cuts (55.0mm), and B.Paste/B.SilkS have zero extent (empty layers — correct for a board with no back SMD or back silk). Solder mask and paste layers legitimately have smaller extents than the board outline since they only cover component pad areas, not the full board perimeter. F.Cu (50.5mm) vs B.Cu (53.999mm) difference is ~3.5mm which reflects different copper pour extents on each layer — also normal. The alignment flag creates noise but no actual issue exists; layer completeness is correctly reported as complete=true.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---
