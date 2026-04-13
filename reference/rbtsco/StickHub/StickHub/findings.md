# Findings: rbtsco/StickHub / StickHub

## FND-00001588: Component counts and types accurate for StickHub 7-port USB hub; Crystal Y1 (12MHz) correctly detected with no external load capacitors; TVS diodes correctly detected as protection devices on all 7...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: StickHub.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- 94 total components correctly identified: 38 capacitors (10×0.1uF bypass, 8×0.1uF 100V, 15×22uF, 2×10uF, 1×1uF, 1×15nF, 1×330uF), 13 resistors, 18 diodes (16 TVS AR0521P1 + 2 D5V0H1B2LP), 7 LEDs (dual-color USB status), 2 ICs (U1 XR22417 hub + U2 SLG5NT1487V power switch), 1 crystal, 9 connectors, 1 jumper, 1 mounting hole, 4 graphic logos. PCB footprint count matches at 94.
- crystal_circuits detects Y1 (12MHz 50ppm 16-20pF) with frequency=12000000 Hz and load_caps=[]. The XR22417 USB hub IC integrates internal crystal load capacitors and does not require external load caps. The XI and XO nets only connect Y1 pins to U1 (XR22417) pins with no capacitors, confirming load_caps=[] is accurate.
- 18 protection devices correctly identified: 14 TVS diodes (AR0521P1, 0.5pF 3.3V) on U1D+/U1D- through U7D+/U7D- (7 downstream port pairs), 2 TVS on D+/D- (upstream), and 2 diodes D24/D25 (5V D5V0H1B2LP) on VIN and +5V. All 16 TVS diodes and 2 ESD diodes for power are correctly attributed.
- differential_pairs correctly identifies 8 pairs: D+/D- (upstream, shared with J1 and U1) and U1D+/U1D- through U7D+/U7D- (downstream ports, each shared with a JST connector and U1). has_esd=true for all pairs via the TVS diodes on each differential pair net. This accurately represents the 7-port hub topology.
- voltage_dividers correctly identifies the VBUS sensing network: R1 (10k top) and R2 (100k bottom) between +5V and GND, midpoint connected to U1 pin 41 (VBUS_SENSE). Ratio 0.909 is correct (10k/(10k+100k) ≈ 0.909, which actually makes the mid-point higher than a simple 5V divider midpoint — this senses the 5V VBUS rail adequately for the XR22417).

### Incorrect
- bus_analysis.i2c detects net 'LED1' as SCL and unnamed net as SDA. The XR22417 has a dual-function pin 'LED1/SCL'. In this design the pin is used as LED1 (driving a status LED), confirmed by the schematic net label 'LED1'. There is no I2C master or slave device connected. The analyzer matches '/SCL' in the pin name and triggers a false positive. The net label 'LED1' should take precedence over the pin name suffix.
  (design_analysis)

### Missed
- power_regulators=[] but the XR22417 (U1) has a '1V8_OUT' pin that generates the +1V8 rail (decoupled by C4, C11, C12, C13). The +1V8 rail powers the internal logic of the hub IC. While this is an integrated regulator (not a standalone IC), the analyzer could flag the IC pin named '1V8_OUT' as a power output. This is a missed detection for integrated power generation.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001589: PCB footprint count (94), net count (47), and routing statistics are accurate; U2 (SLG5NT1487V TDFN-8) and J9 (solder pad) misclassified as through_hole footprints

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: StickHub.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- 94 footprints matches schematic exactly. 47 nets confirmed. 1309 track segments, 87 vias, 5 zones, routing_complete=true. Board dimensions 16.5 x 40.0 mm (a narrow USB stick form factor). 2 copper layers (F.Cu, B.Cu).

### Incorrect
- tht_count=2 includes U2 (SLG5NT1487V) and J9. Inspection of the source kicad_pcb file shows U2's footprint has '(attr through_hole)' at the footprint level, but all its pads are explicitly 'smd' type (roundrect pads on B.Cu/B.Paste/B.Mask only). The TDFN-8 package is a surface-mount package. The footprint has an incorrect 'through_hole' attribute set in KiCad 5.x. The PCB analyzer faithfully reads this attribute, so smd_count=85 is understated by 2.
  (statistics)

### Missed
(none)

### Suggestions
- Fix: U2 (SLG5NT1487V TDFN-8) and J9 (solder pad) misclassified as through_hole footprints

---

## FND-00001590: Gerber layer set is complete and all layers aligned; Drill file analysis correctly reports 87 PTH holes with two drill sizes; Gerber board dimensions consistent with PCB at 16.5 x 40.0 mm (job file...

- **Status**: new
- **Analyzer**: gerber
- **Source**: CAM.json
- **Created**: 2026-03-24

### Correct
- All 9 expected layers present: B.Cu, B.Mask, B.Paste, B.SilkS, Edge.Cuts, F.Cu, F.Mask, F.Paste, F.SilkS. alignment=true with consistent extents (16.5 x 40.0 mm) across all layers. No missing or extra copper layers. The completeness check uses the gbrjob file for authoritative layer list.
- 87 total holes in PTH drill file: 81 holes at 0.3mm diameter (vias) and 6 holes at 0.4mm diameter (larger vias). No NPTH drill file (no mechanical mounting holes). Tool T3 (1.5mm) has 0 holes — it's defined but unused, which is not an error.
- Layer extents from gerber parsing are 16.5 x 40.0 mm, matching PCB statistics exactly. The gbrjob file reports 16.6 x 40.1 mm (a 0.1mm rounding in the job file metadata). The actual copper layers confirm 16.5 x 40.0 mm, which is the correct board size.
- smd_apertures=265 from F.Paste (112 flashes) + B.Paste (153 flashes) = 265 total SMD pads with paste. With 85 SMD footprints in the PCB (after the 2 misclassified THT), this gives ~3.1 pads per SMD component on average (mix of 2-pad passive and multi-pad ICs). smd_ratio=1.0 (all flash apertures are SMD).
- The StickHub PCB has no mechanical mounting holes (H1 'Strap' is listed as mounting hole in the schematic but its footprint 'MountingHole:Plain_Hole_3mm' is described as 'Not Populated'). No NPTH drill file is expected, and none is present. This is correctly reported.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
