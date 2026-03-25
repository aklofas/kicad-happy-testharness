# Findings: STM32-Bluetooth / stm32withBlueto0th

## FND-00001340: Component count and type breakdown accurate for STM32WB55 BLE board; LDO regulator correctly identified with VBUS→+3.3V topology; 32kHz LSE crystal load capacitors correctly detected and effective ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: stm32withBlueto0th.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- 48 total components identified, including 19 capacitors, 3 inductors, 2 ICs (MIC5365-3.3 LDO + STM32WB55CEU6), 2 crystals (32MHz HSE + 32kHz LSE), 4 connectors, 7 resistors. All counts match the BOM entries and references listed. The STM32WB55CEU6 MCU is correctly classified as 'ic' and the MIC5365-3.3YD5 as an LDO power regulator.
- MIC5365-3.3YD5 is correctly detected as LDO with input_rail=VBUS and output_rail=+3.3V, estimated_vout=3.3, vref_source=fixed_suffix. This is accurate — the MIC5365-3.3 is a fixed 3.3V LDO powered from USB VBUS.
- X2 (32kHz LSE) crystal correctly identifies load caps C19 and C16 (both 10pF), computes effective_load_pF=8.0 using the series formula (10p*10p)/(10p+10p)+3pF stray. This is correct and in typical range for a 32.768kHz watch crystal.
- D2 (USBLC6-2SC6) is correctly detected as esd_ic type protecting USB_D+, USB_D-, USBC_D+, USBC_D- nets. The USBLC6-2SC6 is a dual-data-line USB ESD suppressor in SOT-23-6, and its identification as esd_ic with 4 protected nets is accurate.

### Incorrect
- The analyzer reports an LC filter with L2(10uH)+C14(4u7) sharing net 'SMPSFB'. In reality SMPSFB is the STM32WB55's internal SMPS feedback pin net, not a shared LC filter net. The inductor L2 and capacitor C14 form the buck converter output stage — the inductor connects SMPSLX to the output and C14 is the output bulk cap. Calling this an LC filter (resonant at 23.2kHz) is a misclassification; they share different nodes of the switching stage.
  (signal_analysis)

### Missed
- The design has named nets I2C1_SCL and I2C1_SDA connected to the STM32WB55. The design_observations section correctly records these as i2c_bus category items with pullup resistors (R2 on SDA, R5 on SCL), but bus_analysis.i2c is an empty array. The I2C detection in design_observations is correct, but the bus_analysis section should also populate i2c entries for completeness and assertion coverage.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001341: 4-layer board dimensions and stackup accurately parsed for STM32WB board; Thermal pad on STM32WB55 QFN correctly identified with adequate via stitching; Courtyard overlaps and negative edge clearan...

- **Status**: new
- **Analyzer**: pcb
- **Source**: stm32withBlueto0th.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Board correctly identified as 4-layer (F.Cu, In1.Cu, In2.Cu, B.Cu) with dimensions 49.0×27.3mm, 48 footprints all on front side (SMD RF design), 142 vias, 290 track segments. The stackup details (1.58mm total, 0.035mm copper, prepreg/core thicknesses) are correctly extracted from the KiCad 9 file.
- U3 (STM32WB55CEU6, QFN-48) thermal pad (pad 49, 5.6×5.6mm, 31.36mm²) on GND net is correctly detected with 24 nearby thermal vias. This is accurate — the QFN-48 exposed pad requires via stitching to the GND plane for thermal management.
- J1 (USB-C connector) shows edge_clearance_mm=-1.33, meaning its courtyard extends 1.33mm beyond the board edge. This is expected for an edge-mount USB-C connector where the connector body intentionally overhangs the board edge. Three courtyard overlaps are also detected (J1/J3, R1/J3, U2/J3) which are likely due to the compact layout of this small (49×27mm) board.
- Min track 0.19mm, min spacing ~0.151mm, min drill 0.25mm, min annular ring 0.2mm — all within standard PCB fab capabilities. dfm_tier='standard' and violation_count=0 are correct. The 0.19mm tracks on a 4-layer BLE RF board is reasonable.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
