# Findings: UnsignedArduino/Stock-Ticker-Hardware / Stock-Ticker-Hardware

## FND-00001591: Capacitor value parsing: µF values are not converted to Farads correctly; RC filter cutoff frequency reported as 0.00 Hz due to capacitor parsing bug; SPI bus not detected despite CLK, CS, DOUT sig...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_Stock-Ticker-Hardware_Stock-Ticker-Hardware.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The schematic correctly identifies 19 unique components: 1 IC (74AHCT125, classified as ic), 1 module (RaspberryPi_Pico_W), 4 capacitors, 2 resistors, 6 connectors, 4 mounting holes, 1 switch. Power rails (+3.3V, +5V, GND) and 41 nets are correct. The 23 component instances vs 19 unique reflect the 5-unit representation of U1 in the schematic.

### Incorrect
- C3 ('10 μF') is parsed as farads=1e-11 (should be 1e-5 F). C1, C2, C4 ('0.1 μF') are parsed as farads=0.1 (should be 1e-7 F). The Unicode µ prefix is not handled, treating '0.1 μF' as 0.1 F (100,000 µF) and '10 μF' as something around 10 pF. This cascades to decoupling analysis (total_capacitance_uF reports 200000.0 µF instead of ~10.2 µF) and RC filter time constants (RC = 100s instead of ~100µs for R=1kΩ, C=0.1µF).
  (signal_analysis)
- Two RC filter instances are detected (R2+C4 and R1+C4), both reporting cutoff_hz=0.0 and enormous time constants (100s and 1000s respectively). The correct cutoff for R2(1kΩ)+C4(0.1µF) is ~1592 Hz and for R1(10kΩ)+C4(0.1µF) is ~159 Hz. The root cause is the µF→F conversion bug. Additionally, R1 (10kΩ pull-up) and C4 do not actually form a standalone RC filter — C4 is the SW1 debounce capacitor connected between the switch output and GND, not between R1 and GND, making one of the two detections a false positive.
  (signal_analysis)
- The assembly_complexity section reports smd_count=11 and tht_count=12, with package_breakdown showing other_SMD:11. However, only A1 (RaspberryPi_Pico_W_SMD_HandSolder) has an SMD footprint; all other components (U1 DIP-14, C1-C4 THT caps, R1-R2 axial THT, SW1 push button THT, J1-J6 connectors THT, H1-H4 mounting holes) are through-hole. The PCB analyzer correctly reports smd_count=1 and tht_count=14. The schematic assembly analyzer overcounts SMD by treating the 5 repeated units of U1 plus connectors as SMD.
  (assembly_complexity)

### Missed
- The schematic has nets named CLK, CS, and DOUT routed through a 74AHCT125 quad bus buffer to connector J1 (JST 5-pin, likely for a display module such as MAX7219 or similar). These three nets constitute a 3-wire SPI-like bus (write-only / half-duplex). The analyzer reports spi: [] in bus_analysis despite the presence of these named signals.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001592: PCB footprint count, layer stack, routing and board dimensions are accurate; Courtyard overlap reported for C1+C3 with overlap_mm2=0.0

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: repos_Stock-Ticker-Hardware_Stock-Ticker-Hardware.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- PCB correctly reports: 19 footprints (all front side), 1 SMD (A1 Pico_W module), 14 THT, 4 mounting holes excluded from pos. 2-layer board (F.Cu, B.Cu), 145 track segments, 6 vias, 1 GND zone, board 60×50 mm, routing complete (0 unrouted), 41 nets. These match the schematic exactly.

### Incorrect
- The placement_analysis reports 3 courtyard overlaps: U1+R2 (26.535 mm²), U1+R1 (15.538 mm²), and C1+C3 (0.0 mm²). The C1+C3 entry has zero area, indicating the courtyards merely touch at a point or share a single edge rather than truly overlap. This is a false positive — zero-area overlaps should not be flagged as violations.
  (placement_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001911: Component inventory correct: 19 total, correct type breakdown, 3 DNP; Net count correct: 41 nets including 26 unconnected-* Pico pins; RC filter cutoff_hz=0.0 due to capacitor unit parsing bug (µF ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Stock-Ticker-Hardware_Stock-Ticker-Hardware.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- total_components=19 matches source (A1, U1, C1-C4, R1-R2, J1-J6, SW1, H1-H4). component_types breakdown (ic=2, capacitor=4, connector=6, mounting_hole=4, resistor=2, switch=1) is accurate. dnp_parts=3 correctly captures J4, J5, J6 marked DNP. power_rails [+3.3V, +5V, GND] correct.
- total_nets=41 matches the actual net count. The Raspberry Pi Pico W (A1) has many GPIO pins that are no-connected, creating 26 unconnected-* single-pad nets. 15 real interconnection nets plus 26 unconnected-* = 41 total. This is correctly parsed.

### Incorrect
- R2 (1 kΩ) + C4 (0.1 µF) form a switch debounce RC. The analyzer stores C4 as farads=0.1 (treating the µF numeric value as Farads), producing time_constant=100 s and cutoff_hz=0.0016 Hz rounded to 0.00. Correct values: time_constant=100 µs, cutoff=1591.5 Hz. The unicode 'µ' with space prefix (e.g. '0.1 µF') is not correctly scaled to Farads. The same bug makes R1+C4 a spurious second filter entry with input_net=+3.3V (pull-up resistor misidentified as filter input). The actual circuit is a pull-up (R1) + series resistor (R2) + debounce cap (C4) for SW1.
  (signal_analysis)
- In the decoupling_analysis section: C3 (10 µF) has farads=1e-11 and self_resonant_hz=1.59e9 Hz — both are wildly wrong. C1 and C2 (0.1 µF each) have farads=0.1 — treating µF value as Farads. total_capacitance_uF=200000 (should be ~10.2 µF) is internally consistent with the bug: 0.1 F × 1e6 = 100000 µF each for C1 and C2. Correct: C3=10 µF=1e-5 F, C1=C2=0.1 µF=1e-7 F. This is a separate code path from pdn_impedance (which has different unit handling).
  (signal_analysis)
- pdn_impedance stores farads in µF-magnitude values (C3: farads=10.0, C1/C2: farads=0.1) and uses them directly in the SRF formula sqrt(ESL × C). With ESL=7.5 nH and C=10.0 (instead of 10e-6 F), SRF = 581 Hz instead of the correct 581 kHz. Same error for C1/C2: reported 5812 Hz instead of 5.81 MHz. This creates consistent SRF values that are exactly 1000× too low.
  (pdn_impedance)
- The 74AHCT125 is a 4-buffer IC with 5 schematic units (4 buffers + 1 power unit). The subcircuits section emits one entry per unit instance, producing 5 subcircuit entries for U1. Two of them include neighbor_components, three are empty. There should be one deduplicated subcircuit entry per unique reference designator.
  (subcircuits)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001912: PCB statistics correct: 19 footprints, 2-layer, 60×50 mm, routing complete; connectivity.routed_nets=15 correctly excludes 26 unconnected-* single-pad nets; DFM violation correctly identified: via ...

- **Status**: new
- **Analyzer**: pcb
- **Source**: Stock-Ticker-Hardware_Stock-Ticker-Hardware.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- footprint_count=19 matches source exactly. smd_count=1 (A1 Pico W) and tht_count=14 (11 regular + 3 DNP) are correct; 4 mounting holes counted separately. front_side=19, back_side=0 is accurate. board dimensions 60×50 mm match the Edge.Cuts rectangle. routing_complete=true, unrouted=0, via_count=6 are all correct.
- The PCB has 41 total nets (matching schematic), of which 26 are unconnected-* nets from Pico W no-connect pads. These single-pad nets require no routing. The 15 real multi-pad nets are all routed (routed_nets=15, unrouted_count=0), which is correct. The net_lengths dictionary also contains exactly 15 entries.
- The via drill size 0.1905 mm (7.5 mil) is below the standard 0.2 mm limit and above the advanced 0.15 mm limit, correctly flagged as tier_required=advanced. Overall DFM tier=advanced is correct. violation_count=1 matches one actual violation.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
