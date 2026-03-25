# Findings: Jeden-board / Jeden-Board

## FND-00000654: Component count (29), net count (53), BOM, power rails, and protection device (D2=TVS on VCC) correctly detected; UART between FT232RL (U2) and ATmega328-P (U1) not detected; crystal_circuits corre...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Jeden-Board.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- ATmega328-P and FT232RL classified as 'ic', Y2 (XO57CRECNA16M) classified as 'crystal', J7 (USB4235) detected as USB connector, D2 (PTVS5V0Z1USKP) correctly identified as TVS protection on VCC. Missing MPN correctly flagged for parts where the MPN field is blank (value field used as part reference only).
- Y2 is a 4-pin TCXO/oscillator module (GND/VDD/OUTPUT/TRI-STATE), not a 2-pin bare crystal. Oscillator modules do not need load caps, so the crystal_circuits detector correctly produces no result. PWR_FLAG warnings for VCC/GND are legitimate ERC findings.

### Incorrect
(none)

### Missed
- U2.TXD connects to U1.PD0 and U2.RXD to U1.PD1 via unnamed wired nets. The bus_analysis UART detector requires net labels (TX/RX name patterns) to trigger; unnamed nets with matching pin names on the connected IC are not detected. bus_analysis.uart is empty.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000655: Edge clearance for U1 (ATmega328-P) reported as -27.81mm but U1 is inside board bounds when accounting for 90-degree rotation; Courtyard overlaps between U1/D4 (9.7mm2) and U1/R6 (5.3mm2) correctly...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Jeden-Board.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- U1 (DIP-28 rotated 90°) X-extent [110.2, 117.8] intersects D4 (DO-35 at 120.31, 83.5) courtyard and R6 (0805 at 117.0, 87.0) courtyard. Overlap areas reported are plausible. These are real design issues.
- 0.1mm via drills are below both standard (0.2mm) and advanced (0.15mm) process limits. Violations correctly flagged. board 62.5x61.5mm, 2-layer, 29 footprints all accurately reported.

### Incorrect
- U1 is placed at (113.99, 80.305) with 90-degree rotation. At that rotation the DIP-28 long axis runs along Y [63.8, 96.8] and short axis along X [110.2, 117.8] — both within board bounds [107.25–169.75, 36.25–97.75]. The reported -27.81mm edge clearance treats the footprint as unrotated. This is a bug in the edge clearance calculation (rotation not applied before measuring pad/courtyard extents).
  (signal_analysis)
- The decoupling_placement for U2 reports C10 as the closest cap at 10.0mm sharing net 'Net-(U2-DTR)', which is a signal pin, not a VCC or GND net. Decoupling cap proximity should be measured via shared power/ground nets, not arbitrary shared nets.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
