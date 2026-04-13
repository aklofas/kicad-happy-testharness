# Findings: rianadon/Cosmos-Keyboard-PCBs / lemon-pcb-swizzle_lemon-wired-swizzle

## FND-00000193: RP2040 keyboard PCB with dual USB-C and FSUSB42 muxes (58 components). Correct: all components classified correctly, XC6206 LDO detected, crystal 12MHz, WS2812B LED chain, USB compliance, power budget, footprint warnings. No incorrect classifications found. Missed: dual USB-C split keyboard architecture, VIK connector bus.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: lemon-pcb-swizzle_lemon-wired-swizzle.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- All 58 components correctly classified across 9 types
- XC6206P332MR-G correctly detected as LDO feeding +3V3
- WS2812B-2020 addressable LED detected
- USB-C compliance: CC pulldowns pass, VBUS ESD/decoupling fail

### Incorrect
(none)

### Missed
- Dual USB-C split keyboard USB mux pattern not recognized
  (signal_analysis)
- VIK keyboard expansion bus not recognized
  (design_analysis.bus_analysis)

### Suggestions
- Consider detecting split keyboard USB mux patterns
- Consider recognizing VIK as standardized keyboard bus

---
