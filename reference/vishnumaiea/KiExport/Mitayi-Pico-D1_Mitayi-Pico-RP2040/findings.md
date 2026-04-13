# Findings: vishnumaiea/KiExport / Mitayi-Pico-D1_Mitayi-Pico-RP2040

## FND-00000741: Component counts and BOM extraction correct for RP2040 design; LDO regulator (MIC5219-3.3YM5) correctly detected with input/output rails; Regulator missing-cap warning is a false positive: C13 (10u...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Mitayi-Pico-D1_Mitayi-Pico-RP2040.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 57 components, 31 unique parts, 2 DNP correctly identified. All BOM entries with MPNs correctly extracted. J6 (USB_B_Micro) correctly flagged dnp:true.
- power_regulators section correctly identifies U2 as LDO with VSYS input and 3.3V estimated output. topology='LDO' correct.
- memory_interfaces correctly identifies U1 as flash, U3 as processor, with 6 shared signal nets (QSPI_SCLK, QSPI_SS, QSPI_SD0-SD3).
- USB_D+ and USB_D- are correctly classified as 'high_speed' in net_classification. USB series resistors R5/R6 (27R) are correctly associated.
- statistics.power_rails is ['VSYS'] — correctly identified from net labels. The design uses local net labels for power (no explicit PWR_FLAG), so this is a reasonable detection.

### Incorrect
- design_observations reports 'regulator_caps' missing for U2 VSYS input and unnamed_34 output. But C13 is connected to VSYS (confirmed in nets section) and C14 is on the output rail (__unnamed_34). The analyzer fails to associate these caps with the regulator, likely because the output net is unnamed. This is a false-positive warning.
  (signal_analysis)
- crystal_circuits shows Y1 with load_caps: []. The schematic has R10+C18 on XOUT and matching caps on XIN, forming the crystal oscillator load network. The RC filter detector incorrectly captures R10+C18 as an RC filter (5.31 MHz) instead of recognizing the crystal load cap topology.
  (signal_analysis)
- R3 and R4 are 5.1k resistors on CC1/CC2 nets of the USB-C connector, forming classic USB-C CC pull-down dividers. The signal_analysis voltage_dividers list is empty, missing this detection.
  (signal_analysis)
- detected_bus_signals shows prefix='GPIO', width=68, range='GPIO0..GPIO29'. The range says GPIO0..GPIO29 (30 signals) but the width claims 68. This is an internal counting error — likely counting label occurrences rather than unique signal names.
  (signal_analysis)

### Missed
- test_coverage observations says 'No debug connectors (SWD/JTAG/UART) identified'. J5 is explicitly named 'SWD' and connects to SWCLK/SWDIO on U3 (RP2040). The SWD connector should be detected.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000742: PCB component count (72), layer count (2), net count (63) all plausible for RP2040 board

- **Status**: new
- **Analyzer**: pcb
- **Source**: Mitayi-Pico-D1_Mitayi-Pico-RP2040.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Gerber component_analysis shows 72 unique components. The schematic has 57 in-BOM components but PCB also has kibuzzard graphic elements which inflate the count. Net count of 63 in gerber matches 63 in gerber net_analysis.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000743: Gerber layer completeness check correct — all 9 expected layers present, no missing layers; Via drill classification correct: 107x 0.2mm + 4x 0.254mm via tools correctly identified as vias; B.Paste...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Mitayi-Pico-D1_Jobsets_Jobset-1_R0.6_2025-04-23_Gerber.json
- **Created**: 2026-03-23

### Correct
- found_layers matches expected_layers exactly, complete=true. Board dimensions 51.1x21.1mm match a typical Pico-form-factor board. X2 attributes confirm KiCad 9.99 generation.
- drill_classification correctly separates via drills (111 total) from component holes (113 total) using X2 ViaDrill attribute. NPTH mounting holes (1.5mm x4) correctly classified.

### Incorrect
- pad_summary smd_ratio=0.6 (60% SMD). B.Paste is empty because back-side components are THT (no paste needed). This is correct behavior, not an error. The ratio itself is a valid metric.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
