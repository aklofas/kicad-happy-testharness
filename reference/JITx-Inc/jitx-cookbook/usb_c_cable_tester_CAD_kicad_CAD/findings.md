# Findings: jitx-cookbook / usb_c_cable_tester_CAD_kicad_CAD

## FND-00000251: USB-C tester (57 components). 18 test pads not detected as test points (gen_testpad lib_id not recognized). UART detector misclassifies USB 3.1 SuperSpeed signals as UART.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: CAD-2.kicad_sch.json
- **Created**: 2026-03-16

### Correct
(none)

### Incorrect
- UART detector misclassifies USB 3.1 SuperSpeed signals as UART
  (signal_analysis.bus_interfaces)

### Missed
- 18 test pads not detected as test points - gen_testpad library symbol not recognized
  (signal_analysis.test_points)

### Suggestions
- Recognize gen_testpad library symbols as test points
- Do not classify USB SuperSpeed differential pairs as UART

---
