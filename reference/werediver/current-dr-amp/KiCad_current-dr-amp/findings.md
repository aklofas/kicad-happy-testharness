# Findings: werediver/current-dr-amp / KiCad_current-dr-amp

## FND-00002322: Vee and Vee_hi negative supply rails misclassified as 'signal' instead of 'power'; All three op-amps (OPA1641/OPA1611) detected with configuration 'unknown'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_current-dr-amp_KiCad_current-dr-amp_current-dr-amp.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The amp schematic uses global labels Vee and Vee_hi as negative supply rails (symmetric with Vcc and Vcc_hi). The power_rails list only shows ['GND', 'PWR_FLAG', 'Vcc', 'Vcc_hi'], omitting Vee and Vee_hi entirely. In design_analysis.net_classification, both Vee and Vee_hi are classified as 'signal' rather than 'power'. Since these are KiCad 5 global_label (not power: symbols), the analyzer fails to infer their power role from naming convention. The decoupling_analysis also only covers Vcc and Vcc_hi, missing the negative supply rails entirely.
  (statistics)
- The three op-amp ICs (U1 OPA1641, U2/U3 OPA1611) are all reported with configuration='unknown' in opamp_circuits. This is a classic audio current-drive amplifier circuit — the op-amps are surrounded by resistors forming feedback networks. The voltage_dividers detector did find R7/R10 and R8/R10 dividers adjacent to these op-amps, but no feedback_networks were detected and the op-amp configuration analyzer didn't resolve inverting or non-inverting configurations. This limits the useful signal-path description of the design.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002323: Bridge rectifier (D1-D4 Schottky diodes) not detected despite clear 4-diode bridge topology; TL431/TS432 shunt voltage references not detected as power regulators; TL072 dual op-amps generate 3 sub...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_current-dr-amp_KiCad_current-dr-psu_current-dr-psu.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- U5 and U7 are TL072 dual op-amps (2 functional units). In KiCad 5 legacy format, TL072 has unit 3 as the power supply/GND unit. The subcircuits list contains 3 entries each for U5 and U7 (units 1, 2, 3), inflating the subcircuit count from 6 unique ICs to 10 total entries. Unit 3 is not a functional op-amp circuit and should be excluded from the subcircuits and opamp_circuits lists. The same inflation appears in opamp_circuits which also shows 3 entries per TL072 instance.
  (subcircuits)

### Missed
- The PSU schematic contains D1-D4 (all STPS2L40U Schottky diodes, Device:D_Schottky lib_id) connected in a full-wave bridge rectifier configuration after transformer TR1, feeding 10000uF filter capacitors C1 and C2. The bridge_circuits detector returned an empty list. This is a significant miss for a mains-powered linear PSU — the bridge rectifier is the primary power conversion element.
  (signal_analysis)
- U6 and U8 are TS432 (TL431 clone, lib_id=Reference_Voltage:TL431DBZ), used as shunt voltage references in the linear regulator feedback loops. The power_regulators list is empty. The TL431 is one of the most common discrete voltage regulation components; its presence alongside pass transistors (Q3-Q6) and error amplifiers (U5/U7 TL072) constitutes a complete discrete linear regulator that was entirely missed by the power regulator detector.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002324: Board size DFM violation correctly flagged for 100x155mm PSU board

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_current-dr-amp_KiCad_current-dr-psu_current-dr-psu.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PSU PCB is 100x155mm. The DFM analysis correctly flags this as exceeding the 100x100mm standard tier, requiring a higher fabrication pricing tier at JLCPCB. The violation message and parameters are accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
