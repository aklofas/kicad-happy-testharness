# Findings: SparkFun_GNSS_ZED-X20P / Hardware_Production_SparkFun_GNSS_ZED-X20P_panelized

## FND-00001430: LC filter detection is a false positive for RF matching network inductors; RF chain not detected despite clear SMA-to-GNSS-IC signal path; I2C pullup detection reports has_pullup=false despite 2.2k...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_GNSS_ZED-X20P.kicad_sch
- **Created**: 2026-03-24

### Correct
- total_components=71 (correct — includes G1 OSHW_Logo with in_bom=False, which is a schematic annotation symbol), BOM sum=70 is correct for purchasable parts. Power rails [3.3V, 5V, GND, VCC_RF, VIN, VOUT, VUSB] are all present and correct. Regulator U2 (RT9080-3.3, LDO, 5V->3.3V) is correctly detected. USB-C compliance analysis correctly identifies CC1/CC2 5.1k pulldowns as pass and vbus_esd_protection as fail (there is no separate VBUS TVS, only the ESD IC). The 7 protection devices (ESD ICs and TVS diodes) are all accounted for.
- The decoupling_analysis correctly groups: 3.3V rail has C5 (0.1uF), C8 (33pF), C2 (10uF) — total 10.1uF, 3 caps; VUSB rail has C7 (0.1uF) and C13 (1.0uF) — total 1.1uF, 2 caps; 5V rail has C1 (0.1uF), 1 cap. The design_observations correctly note that 3.3V has bulk+bypass+high_freq coverage and 5V lacks bulk capacitance. These observations are accurate.

### Incorrect
- The analyzer reports two LC filters (L1+C3 and L2+C3, resonant at 2.32 MHz). In reality, L1 and L2 are 47nH series inductors forming an RF matching network in the GNSS antenna signal path (SMA connector J5 -> L1 -> L2 -> U5.RF_IN). C3 (0.1uF) is a decoupling capacitor connected at the L1-L2 junction node via R6 to VCC_RF (the active antenna bias rail), not a filter capacitor. The 2.32 MHz resonance figure is nonsensical for a GNSS RF path operating at 1.2–1.6 GHz. This is a false positive that mischaracterizes an RF pi/L-network as low-frequency LC filters.
  (signal_analysis)
- The design_observations i2c_bus entry for SDA reports has_pullup=false and pullup_resistor=null. However R12 (2.2k) and R13 (2.2k) are physically connected to the SCL and SDA lines respectively. The other ends of R12/R13 connect to JP9 (a 3-pin solder jumper) which selects whether pullups are enabled and which rail they pull to. The detector likely fails because the pullup resistors do not connect directly to a named power rail — they go through a jumper first. This is a standard SparkFun Qwiic design pattern. The result is a false-negative: the I2C bus does have optional/configurable pullups.
  (signal_analysis)

### Missed
- signal_analysis.rf_chains is empty. This design has a well-defined RF signal path: J5 (SMA edge connector) -> JP1 (RF/trace selector jumper) -> L1 -> L2 (47nH series matching inductors) -> U5.RF_IN (ZED-X20P GNSS receiver). There is also J10 (U.FL connector) on the same path via JP1. The RF_IN net explicitly connects J5, JP1, L1, L2, and U5. An RF chain should be detected here. Separately, the VCC_RF rail (active antenna bias) with L2 and C3 forms an antenna bias injection circuit that is also not characterized.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001431: Board dimensions, layer count, net count, and DFM metrics are accurate; Edge clearance warnings report negative values for G1 component (-53.97mm) and PTH connectors

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_GNSS_ZED-X20P.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Board dimensions 43.18 x 43.18 mm (1.7" x 1.7" — standard SparkFun breakout size) are correct. 4-layer stackup with F.Cu, In1.Cu, In2.Cu, B.Cu is correct. Net count 85 matches schematic. footprint_count=143 matches component_groups sum=143. DFM tier=standard with min_track=0.1524mm (6mil), min_drill=0.3mm — all realistic for a professional board. routing_complete=true with 0 unrouted nets is correct for the single-board file.

### Incorrect
- placement_analysis.edge_clearance_warnings reports G1 with edge_clearance_mm=-53.97 — G1 is an OSHW logo silkscreen symbol that is likely placed outside the board outline coordinates, or is a schematic-only symbol with no physical location. Negative clearances of -5.08mm for J2 (PTH connector that intentionally overhangs the board edge) are expected and correct for castellation/edge-mount connectors but the magnitude for G1 is anomalous. J2, J3, J11 are 0.1" PTH edge connectors designed to overhang — their negative clearances are correct. G1 at -53.97mm suggests the logo graphic origin is at a very different coordinate than the board boundary.
  (placement_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001432: Panel PCB falsely reports routing_complete=false due to intentional NC pads duplicated across instances

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_GNSS_ZED-X20P_panelized.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The panelized board reports routing_complete=false with unrouted_count=40. Inspection of the unrouted list shows all 40 entries are 'unconnected-(XX-NC-PadNN)' nets — these are intentionally no-connected pads on J1 (USB-C NC pins), D13 (unused ESD IC outputs), and similar. Each appears 9 times in the pad list because the panel contains 9 board instances. These are not real unrouted signal paths — they are deliberate NC connections replicated across the panel. The connectivity analysis is misclassifying NC pad replicas as unrouted nets. The single-board PCB file correctly shows routing_complete=true.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001433: GKO (Edge.Cuts) file is misidentified as B.Mask, causing false 'missing Edge.Cuts' report; Layer set, pad counts, trace widths, and alignment analysis are accurate

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- The 9 Gerber files (4 copper + 4 mask/paste/silk + 1 outline) are all found and parsed. Total of 139 unique component references on the panel is consistent with 9 copies of ~15-ish unique electrical components (143 total footprints / 9 ≈ 15.9). The 5 trace widths detected (0.1524, 0.1778, 0.2616, 0.2819, 0.4064 mm) correspond to 6, 7, 10.3, 11.1, and 16 mil widths — all reasonable for a 4-layer RF design. The layer alignment check passes correctly (all layers co-registered). Back paste is correctly empty (all components are on the front side or use SMD pads without back paste).

### Incorrect
- The GKO Gerber file (SparkFun_GNSS_ZED-X20P_panelized.GKO) is assigned layer_type='B.Mask' and its x2_attributes show FileFunction='Soldermask,Bot'. However its aperture_analysis contains a 'Profile' function aperture — the standard X2 attribute for board outline (Edge.Cuts) layers — indicating this is actually the board outline file. The completeness check then reports missing_required=['Edge.Cuts'] which is incorrect since the GKO file IS the outline. This appears to be an x2 attribute parsing bug where the GKO file's FileFunction attribute is being read incorrectly (possibly confused with the adjacent GBS file's attribute). The drill_files=0 in statistics is also wrong — the zip archive contains 1 drill file that is not being parsed from the loose files directory.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---
