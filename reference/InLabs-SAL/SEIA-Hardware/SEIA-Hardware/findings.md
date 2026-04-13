# Findings: InLabs-SAL/SEIA-Hardware / SEIA-Hardware

## FND-00001186: TLV70433DBVR LDO regulator (PS1) classified as 'connector' type instead of 'regulator' or 'power'; power_regulators[] is empty despite TLV70433DBVR being correctly identified as 'linear regulator' ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SEIA-Hardware.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies IC4 as an Ethernet PHY and notes that there are no transformer magnetics or RJ45 connector in the schematic — accurate for this schematic-only design at this stage.
- XRCGB32M768F2N10R0 is a 32.768 kHz crystal (readable from MPN) but the value field contains the MPN rather than the frequency string. The analyzer correctly returns null for frequency since it cannot parse the MPN as a frequency value.

### Incorrect
- In both the BOM and the component's 'type' field, PS1 (TLV70433DBVR, an LDO described as '24V Input Voltage, 150mA LDO Regulator') is classified as type: 'connector'. This causes it to not appear in power_regulators[] in signal_analysis despite having function: 'linear regulator' set in the detailed component section. The BOM type classification is incorrect.
  (signal_analysis)
- The schematic has 263 total_nets with the vast majority being __unnamed_N. This is extremely high for a 22-component design and suggests the design uses net labels heavily for a BGA MCU (MIMXRT1062, 196-pin BGA) where individual ball signals are not labeled. While technically correct, the net_classification section becomes dominated by unnamed signals, making design_analysis less meaningful. This is a reporting quality issue rather than an analyzer bug.
  (signal_analysis)

### Missed
- The component-level analysis for PS1 correctly sets function: 'linear regulator', but signal_analysis.power_regulators is still []. The regulator-to-signal_analysis pipeline is broken — a detected regulator is not being promoted into the power_regulators list.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001187: Empty PCB file correctly handled — all statistics zero, no false positives

- **Status**: new
- **Analyzer**: pcb
- **Source**: SEIA-Hardware.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The SEIA-Hardware PCB file contains no footprints, tracks, or board outline (schematic-only design state). The analyzer returns all-zero statistics, null board dimensions, and generates appropriate documentation warnings without crashing or producing false detections.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
