# Findings: SIPM02 / hw_sch_pcb_SIPM02

## FND-00001246: Component counts, net extraction, and BOM correct; R8 typed as resistor but has value '100nF'; C10 typed as capacitor but has value '0R' — BOM grouping is mixed; RC filter chain on SiPM bias supply...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SIPM02.kicad_sch
- **Created**: 2026-03-24

### Correct
- 39 components, 16 nets, 10 connectors, 12 resistors, 10 capacitors, 2 ICs, 1 diode all correctly parsed. Power rails +28V, +3.3V, +3V6, GND correctly identified.
- Three-stage low-pass RC filter on the +28V → SiPM bias path (R1/C1+C2 at 964 Hz, R2/C5 at 159 kHz, R4/C9+C6 at 144 kHz) correctly detected and characterized.
- U2 OPA836IDB correctly classified as transimpedance_or_buffer configuration with 12k feedback resistor R10 between output and inverting input. This is accurate for a SiPM readout transimpedance amplifier.
- Nets driven externally through connectors (J7=DIRECT_OUT, J10=#PD, J8=OUT) correctly flagged as having no output driver within the schematic. These are legitimate ERC warnings for a module with external signal entry points.

### Incorrect
- In the BOM, R8 (value='100nF') is grouped with capacitors (type='capacitor'), and C10 (value='0R') is grouped with resistors in the 100nF cap group. The analyzer correctly uses the schematic symbol type, not value string. However, the BOM entry at line ~183 groups R8 in the 100nF capacitor group with references [C5, C6, R8, C8], which is a cross-type grouping error — a resistor ref is in a capacitor BOM line.
  (signal_analysis)
- The fourth RC filter entry has R4 with input_net='__unnamed_4' and output_net='__unnamed_6', which is the reverse of the correct signal flow. The correct filter has R4 driving from __unnamed_6 to __unnamed_4. This creates a duplicate/reversed entry that is a false positive.
  (signal_analysis)

### Missed
- +3.3V → R3(100R) → D1 → +3V6 forms a reverse-biased diode clamp (limiting +3V6 to 3.3V - Vf). The voltage_dividers list is empty and no power regulator or protection device was detected for this path. This is a noteworthy signal path missed by all detectors.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001247: PCB statistics accurate: 39 footprints, 2-layer, 56 vias, 2 zones, routing complete; Decoupling placement for U2 (OPA836) correctly identifies C8/C7 on same side at 3.95/5.67mm; DFM tier standard, ...

- **Status**: new
- **Analyzer**: pcb
- **Source**: SIPM02.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Footprint count, layer count, via count, zone count, and board dimensions all consistent with the gerber set. Routing reported complete with 0 unrouted nets.
- C8 (100nF) and C7 (10uF) are both on B.Cu same side as U2 and within recommended distance, correctly flagged as adequate decoupling. U1 (SiPM) caps are on opposite side which is also noted.
- Min track width 0.4mm, min drill 0.4mm (via size), approx min spacing 0.2mm all consistent with the gerber trace widths (0.4, 0.5, 0.8mm).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001248: hw/CAM_PROFI gerbers are from a different project (AIRDOSC01A_PCB01C), not SIPM02; Project ID mismatch between gerbers and expected project not flagged

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hw_CAM_PROFI
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- Every gerber file in this directory contains X2 attributes showing ProjectId='AIRDOSC01A_PCB01C,41495244-4f53-4433-9031-415f50434230,rev?' and CreationDate 2021-07-20. These are leftover files from a different project. The analyzer correctly parses what it finds but does not detect the project mismatch. The pad_summary shows smd_ratio=0.0 and smd_apertures=0 because this older gerber set lacks X2 aperture function attributes for SMD pads.
  (signal_analysis)

### Missed
- The analyzer could detect when all gerbers in a directory share a ProjectId (from X2 attributes) that does not match the directory/repository name. AIRDOSC01A_PCB01C vs SIPM02 is a clear mismatch that indicates stale/wrong gerbers. Adding a project_id_mismatch check would improve gerber QA.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001249: hw/cam_profi/gbr is the correct SIPM02C gerber set, complete with 9 layers; SMD ratio 0.68 and pad counts consistent with PCB (24 SMD back-side, 15 THT front-side)

- **Status**: new
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr
- **Created**: 2026-03-24

### Correct
- ProjectId='SIPM02,...', 9 layers found matching gbrjob expected layers, complete=true, 80 total holes (56 vias at 0.4mm + 20 component at 0.889mm + 4 mounting at 3.0mm), all consistent with PCB file.
- 52 SMD flashes on B.Cu, 56 via pads, 24 THT holes match the PCB statistics of 24 SMD and 15 THT footprints. The smd_ratio of 0.68 (52 SMD / 77 total non-via pads) is plausible.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
