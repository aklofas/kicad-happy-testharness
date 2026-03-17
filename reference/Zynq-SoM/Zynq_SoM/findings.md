# Findings: Zynq-SoM / Zynq_SoM

## FND-00000290: Zynq XC7Z020 SoM (288 components). TPSM82864 voltage monitoring divider (R78/R79 to STM32 ADC) misidentified as regulator feedback divider. RTL8211F Ethernet interface not detected (custom lib_id). Duplicate reset_pin observations for eMMC (3x). has_high_freq=false on rails with 47nF 0201 caps (standard FPGA HF bypass).

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Zynq_SoM.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- MPM3834/MPM3822 switching regulators correctly identified
- TPS7A20 LDO correctly identified
- DDR3L SDRAM interface correctly detected
- STM32G431 system controller crystal correctly detected

### Incorrect
- TPSM82864 (U8) feedback divider misidentified — R78/R79 (100k/100k) are STM32 ADC voltage monitoring dividers on +1V0 rail, not regulator FB divider. TPSM82864 FB pin ties directly to +1V0, voltage set via VSET pin R25.
  (signal_analysis.power_regulators)
- Duplicate reset_pin observations for U7 (IS21ES08G eMMC) — emitted 3 times identically
  (signal_analysis.design_observations)
- has_high_freq=false on +1V35 with 11x 47nF/0201 caps (SRF ~23MHz) — 47nF in 0201 is standard FPGA HF bypass
  (signal_analysis.decoupling_analysis)
- TPSM82864 multi-VOUT pins flagged as multi_driver_net — internal connection of power module QFN pads is expected
  (connectivity_issues.multi_driver_nets)

### Missed
- RTL8211F Ethernet PHY interface not detected — custom lib_id MyLibrary:RTL8211F-CG not matched by Ethernet detector
  (signal_analysis.ethernet_interfaces)

### Suggestions
- When FB pin ties directly to output rail with no divider, don't attribute separate monitoring dividers as feedback
- Deduplicate reset_pin observations by component reference
- Raise has_high_freq threshold or make it footprint-aware (47nF/0201 is HF bypass)
- Ethernet detector: match on part value (RTL8211) not just lib_id prefix

---
