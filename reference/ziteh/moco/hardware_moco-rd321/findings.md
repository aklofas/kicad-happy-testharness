# Findings: moco / hardware_moco-rd321_moco-rd321

## FND-00000269: BLDC motor controller rd321 (STSPIN32F0A, 95 components). 7 duplicate power_regulator entries and 13 duplicate design_observations from 7-unit IC. Three-phase half-bridge (SiZ250DT dual MOSFETs), current sense shunts, and internal opamps all missed.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_moco-rd321_moco-rd321.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- STSPIN32F0A correctly identified as switching regulator with bootstrap and +3.3V output
- SPI bus detected with STSPIN32F0A and MA702 rotary sensor
- VBUS voltage divider (R2=100k/R5=10k) correctly detected
- 3x SiZ250DT MOSFETs detected with gate resistors and 20mohm source sense resistors

### Incorrect
- 7 duplicate power_regulator entries for U1 STSPIN32F0A — one per schematic unit instead of one per IC
  (signal_analysis.power_regulators)
- 7 identical reset_pin and 6 identical switching_regulator observations in design_observations — same multi-unit duplication
  (signal_analysis.design_observations)

### Missed
- bridge_circuits empty — 3x SiZ250DT dual N-ch MOSFETs (Q1/Q2/Q3) form three-phase half-bridge with pin names G1/D1/S1D2/G2/S2 not matched by bridge detector
  (signal_analysis.bridge_circuits)
- current_sense empty — three 20mohm/3W shunt resistors (R14/R16/R30) in phase paths with differential outputs to STSPIN32F0A internal opamps
  (signal_analysis.current_sense)
- opamp_circuits empty — STSPIN32F0A internal opamps (OP1-OP3) wired for current sensing not detected
  (signal_analysis.opamp_circuits)

### Suggestions
- Deduplicate multi-unit IC entries by (ref, topology, output_rail)
- Add bridge detection for dual-FET packages (SiZ250DT pin naming G1/D1/S1D2/G2/S2)
- Detect low-value shunt resistors with differential signals to opamp inputs as current_sense

---

## FND-00000270: BLDC motor controller rd501 (DRV8301 + STM32, 131 components). Three-phase bridge correctly detected but driver_ics link to DRV8301 missing. DRV8301 current sense shunts (0.5mohm) not detected.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_moco-rd501_moco-rd501.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- Three-phase bridge (Q1-Q6 CSD18540Q5B) correctly detected in bridge_circuits
- DRV8301 correctly identified as ic_with_internal_regulator providing +5V
- XC6220B331MR LDO producing 3.3V correctly identified
- MCP25625 CAN bus device correctly detected
- Two crystals (8MHz, 16MHz) with load cap analysis correct
- SPI bus with DRV8301, MCU, MCP25625, AS5147 correctly detected

### Incorrect
- bridge_circuits.driver_ics empty — DRV8301 (U2) is the gate driver for all 6 FETs but link not established
  (signal_analysis.bridge_circuits)

### Missed
- current_sense empty — two 0.5mohm shunt resistors (R32/R27) in low-side current paths with DRV8301 SO1/SO2 sense outputs (CUR_SENSE_1/CUR_SENSE_2)
  (signal_analysis.current_sense)

### Suggestions
- Trace bridge gate drive lines back to driver ICs to populate driver_ics
- For DRV8301/8305 with SO/CSO pins, detect associated shunt resistors as current_sense

---

## FND-00000271: BLDC motor controller sc1 (STSPIN32G4, 99 components). Wrong output_rail for internal buck (unnamed net instead of +3.3V). 5 duplicate power_regulator entries. Three-phase bridge (CSD88584Q5DC), current sense, and internal opamps all missed.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_moco-sc1_moco-sc1.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- STSPIN32G4 identified as switching regulator with bootstrap
- TCAN337 CAN transceiver correctly detected
- MA702 rotary sensor on SPI correctly detected
- 16MHz crystal with 6.8pF load caps correctly detected

### Incorrect
- power_regulators output_rail='__unnamed_41' for STSPIN32G4 — should be '+3.3V' (REG3V3/VDD pin connects to +3.3V net)
  (signal_analysis.power_regulators)
- 5 duplicate power_regulator entries for U1 — one per schematic unit
  (signal_analysis.power_regulators)
- 5 duplicate decoupling + 4 duplicate switching_regulator observations for U1
  (signal_analysis.design_observations)

### Missed
- bridge_circuits empty — 3x CSD88584Q5DC dual MOSFETs (Q1/Q2/Q3) with GH/SH/GL/VSW/VIN/PGND pins not detected
  (signal_analysis.bridge_circuits)
- current_sense empty — three 2.2R/125mW shunts (R18/R27/R9) with differential outputs to STSPIN32G4 opamp inputs
  (signal_analysis.current_sense)
- opamp_circuits empty — STSPIN32G4 internal opamps not detected
  (signal_analysis.opamp_circuits)

### Suggestions
- Trace buck output from REG3V3/VDD pin instead of SW node
- Deduplicate multi-unit entries
- Detect CSD88584Q5DC pin names (GH/SH/GL/VSW) as half-bridge

---
