# Findings: hackclub/OnBoard / projects_BrainHat_src_EEG amp

## FND-00000095: EEG amplifier using AD8232 heart rate monitor IC and TS5A3159A analog switch. Opamp detection is questionable for AD8232 which is not a generic opamp.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/BrainHat/src/EEG amp.kicad_sch
- **Created**: 2026-03-14
- **Datasheets**: AD8232 datasheet (Analog Devices)

### Correct
- AD8232 correctly identified as IC type with proper description about ECG/biopotential measurement
- TS5A3159ADBVR correctly identified as IC (analog switch)
- Power rail +3.3V and GND correctly detected
- 4 LEDs and 4 connectors (Electrodes, Output, Power, Status) correctly classified
- BOM entries use MPN-style values (e.g., ARG03BTC1002 for resistors) which are correctly preserved

### Incorrect
- AD8232 detected as opamp in comparator_or_open_loop configuration with inverting input on GND and non-inverting on +3.3V. The AD8232 is an integrated signal conditioning block, not a generic opamp. Its internal opamps are not user-accessible as separate amplifier stages.
  (signal_analysis.opamp_circuits)

### Missed
- No I2C or SPI bus detected. The AD8232 outputs are analog, so this is correct. However, the OLED or other peripherals may use I2C - would need to verify the full schematic hierarchy.
  (design_analysis.bus_analysis)

### Suggestions
- The opamp detector should not flag integrated signal conditioning ICs like AD8232 as opamp circuits. The AD8232 lib_id is from a personal library (Personal:AD8232) which makes heuristic filtering harder, but the description mentions it is an integrated block.

---
