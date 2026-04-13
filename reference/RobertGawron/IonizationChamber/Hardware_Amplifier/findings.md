# Findings: RobertGawron/IonizationChamber / Hardware_Amplifier

## FND-00000630: U1A (LMC6062 unit 1) misclassified as 'comparator_or_open_loop' — it is a transimpedance amplifier (TIA); V31 (Sensor:Nuclear-Radiation_Detector) classified as 'varistor' due to 'V' reference prefi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_Amplifier_Amplifier.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- R38 (100G ohm, expressed as '2*50G') connects the output net __unnamed_0 to the inverting input net __unnamed_1 of U1A, forming a classic TIA topology used for the ionization chamber detector current. The analyzer correctly identified R38 as bridging these two nets, but failed to parse the compound value '2*50G' (parsed_value is None), so no feedback_resistor was found and the unit was classified as open-loop/comparator instead of inverting with feedback. The fix should extend the resistor value parser to handle arithmetic expressions like '2*50G'.
  (signal_analysis)
- The ionization chamber sensor has reference designator V31 and lib_id 'Sensor:Nuclear-Radiation_Detector'. The analyzer assigned it type 'varistor' based on the 'V' reference prefix. The library name 'Sensor' strongly indicates this is a sensor, not a varistor. The classifier should check the lib_id library name (e.g., 'Sensor:') before falling back to the reference prefix heuristic.
  (signal_analysis)
- The statistics section correctly counts 36 components. The assembly_complexity section reports 40 total_components. This is an internal inconsistency — the assembly complexity calculator is counting a different set of items (possibly including power symbols or hierarchical sheet instances). Both numbers should reflect the same 36 real components.
  (signal_analysis)

### Missed
- C46 has value 'not mounted', and C47/C48 use resistor values in capacitor symbols ('0R resistor') — these are clearly optional/configuration parts. The KiCad DNP attribute is not set on these parts, so the analyzer correctly reports dnp=False. However, the design_observations or assembly_complexity sections could flag these as unusual values warranting attention. Not filing as high-impact.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000631: Regulator topology correctly identified: U3 (L78L05, LDO→+5V), U5 (L78L33, LDO→+3.3V), U6 (TPS60403, inverting charge pump→negative rail); pwr_flag_warnings for GND and -3V3 are false positives — s...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_DataProcessingUnit_PowerSupply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All four regulators detected with correct topologies. TPS60403 correctly flagged as inverting switched-capacitor. LDO classification for L78L05/L78L33 is accurate (they are positive-output fixed-voltage linear regulators). The PDN impedance, inrush analysis, and power_budget sections are all populated appropriately.

### Incorrect
- The PowerSupply and SignalProcessor sheets are sub-sheets of the DataProcessingUnit hierarchy. PWR_FLAG symbols exist in the parent sheet context, so these sub-sheet warnings about missing PWR_FLAGs for GND, -3V3, +3.3V, +5V are ERC-false-positives when the full hierarchy is considered. This is a known limitation of single-sheet analysis — not a critical bug but worth noting.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000632: I2C bus (SCL/SDA with 2k2 pull-ups to +5V) and UART (TX/RX on STM8) correctly detected with U54 (STM8S003F3P) and U1 (MCP3425 ADC) as I2C participants

- **Status**: new
- **Analyzer**: schematic
- **Source**: Hardware_DataProcessingUnit_SignalProcessor.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The STM8 MCU communicates with the MCP3425 delta-sigma ADC over I2C. Both SCL and SDA have 2.2k pull-ups to +5V, which is correctly identified. UART pins are also detected. Reset pin with filter cap is noted in design_observations.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000633: PCB correctly identifies 2-layer board (79.75×55mm), mostly back-side placement (33/36), routing complete, DFM standard tier

- **Status**: new
- **Analyzer**: pcb
- **Source**: Hardware_Amplifier_Amplifier.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Component placement matches the schematic (36 footprints). The board is correctly identified as 2-layer with 25 SMD and 11 through-hole parts. front_side=3 (C40, V31, C42 on F.Cu), back_side=33 are all verified accurate. Decoupling placement analysis for U1 and U2 is correctly computed.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000634: DPU PCB correctly identifies 72 footprints all on front side, 2-layer, 1 copper zone, routing complete with 26 vias

- **Status**: new
- **Analyzer**: pcb
- **Source**: Hardware_DataProcessingUnit_DataProcessingUnit.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The DataProcessingUnit PCB matches the schematic component count (72). All components on F.Cu (front_side=72, back_side=0). Net count (44) matches the schematic. DFM standard tier with no violations and standard track widths (0.254mm min).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
