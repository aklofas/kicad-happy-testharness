# Findings: OnBoard / projects_Mobile Power Station_bms_src_bms_v2

## FND-00000108: BMS v2 board with TPS2491 hot-swap controller, BQ7721605 battery protector, 8x HY2213-BB3A cell balancers, MOSFETs for power switching. Massive misclassification: 84 components as other.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/Mobile Power Station/bms/src/bms_v2.kicad_sch
- **Created**: 2026-03-14

### Correct
- Correctly identified TPS2491DGSR as IC
- Correctly identified fuse 0154010.DR for protection
- Correctly identified thermistor NTCS0603E3103JHT
- Correctly identified 7 connectors

### Incorrect
- 84 components classified as other - should include: 18 capacitors (100n), 1 capacitor (33n), 8 MOSFETs (AO3400A), 1 MOSFET (MS50N06), 1 MOSFET (NCE40P40K), 2 MOSFETs (2N7002), 24+8 resistors, 1 zener diode, 8 ICs (HY2213-BB3A cell balancers), 1 IC (BQ7721605PWR battery protector)
  (statistics.component_types)
- Only 1 IC detected but board has 10 ICs: TPS2491, BQ7721605PWR, and 8x HY2213-BB3A
  (statistics.component_types)
- IC pin analysis treats connectors and copper pads as ICs instead of actual ICs
  (ic_pin_analysis)

### Missed
- BQ7721605PWR is a battery protection/management IC for 3-7 cell lithium batteries - not detected as IC or analyzed
  (ic_pin_analysis)
- HY2213-BB3A x8 are single-cell lithium battery balancer ICs - not detected, critical for an 8S BMS design
  (ic_pin_analysis)
- MOSFET classification completely missed: AO3400A (N-ch), MS50N06 (N-ch power), NCE40P40K (P-ch power), 2N7002 (N-ch small signal)
  (statistics.component_types)
- No voltage regulator detection despite TPS2491 being a hot-swap/eFuse controller
  (signal_analysis.power_regulators)
- No current sense detection despite RF10=6mohm being a current sense resistor
  (signal_analysis.current_sense)
- 8S battery configuration not analyzed - this is a multi-cell BMS with balancing, protection, and hot-swap
  (signal_analysis)
- D_Zener 12V (DF1) not classified as protection device
  (signal_analysis.protection_devices)

### Suggestions
- Component classifier needs to handle EasyEDA-imported parts with non-standard naming (CB/CP/RB/RP/QB/QF prefixes)
- MOSFET detection should use footprint (SOT-23, TO-252) and value patterns (AO3400A, 2N7002)
- BMS-specific analysis: cell balancer detection, battery protection IC identification
- Current sense resistor detection for very low ohm values (milliohm range)
- Hot-swap controller (TPS2491) should be identified and analyzed

---
