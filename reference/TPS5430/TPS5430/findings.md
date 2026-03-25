# Findings: TPS5430 / TPS5430

## FND-00001625: pwr_flag_warnings fires for GND, VCC, and VDD even though all three nets have PWR_FLAG symbols placed on them; C9 and C10 (100 µF tantalum) missing from VDD decoupling analysis due to {slash} value...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TPS5430.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- signal_analysis.power_regulators reports U1 as topology=switching, inductor=L1, has_bootstrap=true, input_rail=VCC, output_rail=VDD. This accurately reflects the schematic: L1 (47 µH) is the output inductor, the BOOT cap network is present, and the design converts VCC to VDD.
- transistor_circuits reports Q1 as mosfet, is_pchannel=true, source_net=VCC, load_type=high_side_switch, with gate_pulldown R1 (100 kΩ). This matches the schematic: Q1 is a P-channel MOSFET enabling/disabling power to the regulator.
- decoupling_analysis for rail VCC reports capacitors C3, C1, C2, C4 all 10 µF/50 V, totalling 40 µF with cap_count=4. This matches the schematic: four 10 µF 1206 bulk caps on the VCC input rail.

### Incorrect
- The schematic contains three PWR_FLAG symbol instances: one wired to GND (at 74.93,52.07), one wired to VDD (at 172.72,118.11 on the L1 output rail), and one wired to VCC (at 140.97,41.91). The analyzer tracks each PWR_FLAG symbol as belonging to its own 'PWR_FLAG' net rather than resolving which power net the symbol's pin is wired to, so it never credits any of the three actual power rails with having a PWR_FLAG. All three warnings ('GND has power_in pins but no PWR_FLAG', 'VDD …', 'VCC …') are false positives.
  (pwr_flag_warnings)

### Missed
- C9 and C10 both have value '100u{slash}6.3V' — KiCad encodes the slash character as '{slash}' in the S-expression file. The value parser does not substitute {slash} back to '/', so parsed_value is null for both capacitors. As a result they are absent from the decoupling_analysis for the VDD rail, which reports only C7 (10 µF, total 10 µF) instead of C7+C9+C10 (210 µF). C5 (100n{slash}50V) and C8 (4n7{slash}50V) are similarly affected but are signal capacitors, not decoupling caps on a named rail.
  (signal_analysis)
- F1 is a Littelfuse 1206L300SLTHYR resettable polyfuse placed in series between J1 (barrel-jack input) and the Q1 P-MOSFET drain, providing overcurrent protection on the input rail. D2 is a ZMM5V6 Zener diode with its cathode on VCC and anode on the gate of Q1, clamping the gate drive voltage. Neither is reported in signal_analysis.protection_devices, which returns an empty list.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001626: Thermal pad vias for TPS5430DDA PowerPAD correctly evaluated as adequate; Board dimensions and layer completeness correctly reported for 2-layer 55×20 mm board; statistics.tht_count is 0 but actual...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: TPS5430.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- thermal_pad_vias reports U1 pad 9 (2.6×3.1 mm solder pad) with 8 footprint via-pads (thermal vias embedded in footprint), via density 0.993/mm², and adequacy='adequate'. The recommended minimum is 5 vias and ideal is 9; 8 meets the threshold. The PCB file confirms 8 thru-hole via-pads plus additional standalone vias in the vicinity.
- statistics reports board 55×20 mm, 2 copper layers, routing_complete=true (0 unrouted nets). Gerber confirms Edge.Cuts extents 55×20 mm matching PCB. DFM tier=standard with no violations, min track 0.25 mm, min drill 0.4 mm.

### Incorrect
- The schematic assembly_complexity reports smd_count=41 and tht_count=0. The PCB correctly identifies J2 (TerminalBlock_Phoenix, through-hole screw terminal) as tht_count=1, smd_count=30. The discrepancy in the schematic analyzer is because footprint technology type (THT/SMD) is stored in the footprint library, not the schematic S-expression, so the schematic analyzer cannot distinguish them and classifies everything as SMD.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001627: TPS5430 gerber set complete and aligned: 9 layer files + 2 drill files, Edge.Cuts 55×20 mm

- **Status**: new
- **Analyzer**: gerber
- **Source**: jlcpcb.json
- **Created**: 2026-03-24

### Correct
- completeness: found_layers=[B.Cu, B.Mask, B.Paste, B.SilkS, Edge.Cuts, F.Cu, F.Mask, F.Paste, F.SilkS], missing_required=[], missing_recommended=[], complete=true. alignment.aligned=true, no issues. board_dimensions.width_mm=55.0, height_mm=20.0 matches PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001879: Switching buck regulator topology correctly detected with U1=TPS5430DDA, L1, D1; Feedback voltage divider R5/R6 correctly detected on Feedback net; Q1 P-FET load switch and Q2 NPN BJT detected as t...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TPS5430.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- signal_analysis.power_regulators identifies U1 as a switching regulator. The inductor L1 (47uH) and Schottky diode D1 (SS34) are the correct components for this TPS5430 synchronous buck design.
- signal_analysis.voltage_dividers identifies R5 (5k6) and R6 (270R) on the Feedback net, consistent with the TPS5430 output voltage programming network.
- signal_analysis.transistor_circuits identifies both Q1 (AO3401A, P-channel MOSFET) and Q2 (MMBT3904, NPN BJT). Q1 functions as a high-side load switch and Q2 as the gate drive/control transistor.
- design_analysis.erc_warnings includes a no_driver warning for the net connected to U1 pin 5 (EN). The EN pin is intentionally left floating in this design variant, which is a real design concern for an active-low enable input.

### Incorrect
(none)

### Missed
- signal_analysis.decoupling_analysis for VDD rail only includes C7 (10uF). The schematic also has C9 and C10 (100uF tantalum electrolytic) on the VDD output rail, which are the primary bulk storage capacitors. The total decoupling on VDD is 210uF, not 10uF. This is likely because the capacitor value parser does not recognise the 100u or 100uF tantalum values, or the net connectivity for C9/C10 pins is not resolved to VDD.
  (signal_analysis)
- signal_analysis.protection_devices is empty. F1 is a polyfuse (resettable fuse) on the VCC input rail providing overcurrent protection. Polyfuses should be classified as protection devices alongside TVS diodes and Zener clamps.
  (signal_analysis)
- signal_analysis.snubbers is empty. The TPS5430 schematic includes an RC snubber (a resistor and capacitor) on the SW switching node to suppress ringing. This should be classified in signal_analysis.snubbers.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001880: Board dimensions 55.0 x 20.0 mm and 4-layer copper zone count accurate; 44 footprints reported including 4 mounting holes and 1 logo not in schematic BOM; SMD/THT split correct: 30 SMD pads, 1 THT ...

- **Status**: new
- **Analyzer**: pcb
- **Source**: TPS5430.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- board.dimensions.width_mm=55.0, height_mm=20.0, and 8 copper zones reported. These match the PCB source file edge cuts and zone definitions.
- schematic has 41 components; PCB has 44 footprints. The 3 extras are mounting holes H1-H4 (counted as 4-1=3 net extra) and LOGO1 mechanical — matching a typical production-ready board.
- smd=30, tht=1 reported. The single THT component matches the through-hole header/connector in the design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
