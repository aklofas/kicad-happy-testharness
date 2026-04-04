# Findings: LoRa-868-915 / HARDWARE_LoRa-Rev-A_LoRa_RevA

## FND-00000825: rf_matching detector generates 17 false-positive entries treating every matching network component as 'antenna'; SPI bus detected twice for a single bus — duplicate from pin-name detection and net-...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_LoRa-Rev-A_LoRa_RevA.sch.json
- **Created**: 2026-03-23

### Correct
- Crystal circuit detection is accurate: X1 at 32.000MHz_10ppm with two 15pF load caps (C1, C2) giving effective CL=10.5pF (typical for TCXO/crystal). Consistent across all three schematics.
- Rev-A: 33 total components (1 IC, 20 caps, 6 inductors, 3 connectors, 1 crystal, 2 test points) with correct values and footprints. 0R and n.a. values preserved faithfully. Consistent with schematic content.

### Incorrect
- Every L/C component in the SX1276 RF matching network (C36, C7, C8, L1, L2, C19, L3, C9, Cx, Lx, C11, C12, C13, L4, L5, C16) is reported as a separate rf_matching entry with 'antenna' set to that component. C36 (10nF) and C7 (47pF) are clearly decoupling/series caps, not antennas. The actual antenna port is EXT_ANT1 (U.FL connector). The detector should identify ONE matching network topology (pi/L-match) ending at the antenna connector, not enumerate every adjacent passive as a candidate antenna. Rev-B has 11 false entries, MOD-Rev-B has 10.
  (signal_analysis)
- The SX1276 SPI bus is reported as two separate entries: 'pin_U1' (derived from pin names SCK/MISO/MOSI, 0 chip selects) and bus_id '0' (derived from net labels SCK/MISO/MOSI/NSS, 1 chip select). These are the same bus. The same duplicate appears in Rev-B and MOD-Rev-B. The net-label-based detection with NSS is the more informative entry; the pin-name-based duplicate should be merged or suppressed.
  (signal_analysis)
- In the parsed nets, the net named 'DIO0' contains U1 pin 14 (VBAT_DIG, power_in) and the net 'RESET' contains U1 pin 15 (GND, power_in). Meanwhile, VAA has U1 pin 8 (DIO0) and U1 pin 19 (NSS). The KiCad 5 legacy net parser is misassigning wire junction coordinates to pins — pins are off-by-several due to coordinate proximity logic. This causes false ERC warnings ('no_driver' for DIO0 and RESET nets) and missed SPI CS detection (NSS on the VAA rail). The net label names appear correct but the associated pin assignments are wrong.
  (signal_analysis)
- C19 and C16 have value '0R' and C12 has 'NA' — they use capacitor footprints as RF jumper/DNP pads. The analyzer classifies them as 'capacitor' (by footprint/symbol type) which is technically correct for the library symbol used, but 0R values in an RF matching network are zero-ohm series links, not capacitors. This affects impedance/filter analysis accuracy.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000826: kicad_version reported as 'unknown' for file_version 20171130 (KiCad 5.0 pre-release); Board dimensions, routing completeness, zone stitching, and DFM analysis are accurate; Schematic-PCB value mis...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: HARDWARE_LoRa-Rev-A_LoRa_RevA.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Rev-A: 22.86x26.035mm, 2-layer, 322 segments, 45 vias, 36 footprints (35 SMD), routing_complete=True with 0 unrouted. Two nets (Net-(U1-Pad20) and Net-(U1-Pad27)) correctly identified as zone-only (no tracks, carried by copper pours). DFM tier=standard with no violations. Thermal pad via analysis on U1 QFN EP is present.

### Incorrect
- All three PCB files have file_version=20171130 but kicad_version='unknown'. The date 20171130 corresponds to KiCad 5.0 development/pre-release (released 2018). The analyzer does not recognize this version code and should map it to 'KiCad 5 (legacy)' or similar.
  (signal_analysis)

### Missed
- L5 value in the schematic is '8.2nH' while the PCB footprint value is '6.2nH'. This is a real design inconsistency (likely the PCB was updated but the schematic was not). The analyzer outputs this data in both files but does not cross-reference or flag the mismatch. A cross-check between schematic BOM values and PCB footprint values would catch this.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000827: Edge clearance warning correctly detected for CON1 with -2.5mm clearance (component outside board boundary)

- **Status**: new
- **Analyzer**: pcb
- **Source**: HARDWARE_MOD-LoRa-Rev-B_MOD-LoRa_RevB.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- MOD-Rev-B CON1 has edge_clearance_mm=-2.5, which means it extends beyond the board outline — correct for an edge-mount connector. Rev-A's CON2 at 0.0mm edge clearance is also a reasonable flag. These are true findings.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
