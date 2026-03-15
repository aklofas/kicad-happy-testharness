# Findings: Voron-Hardware / Taco_Raven_KiCad_Voron_Klipper_Board

## FND-00000074: Taco Raven 3D printer controller board - good signal detection on legacy schematic with 358 components

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/Voron-Hardware/Taco_Raven/KiCad/Voron_Klipper_Board.sch
- **Created**: 2026-03-14

### Correct
- Correctly identified 8x TMC2130 stepper drivers grouped as single BOM entry
- Power regulators found: 2x A4403 switching buck and 1x AP2112-3.3 LDO with correct topologies
- 3 fuses (3557-2) properly detected as protection devices with correct net associations
- Memory interface detected: SPI flash (SPIFLASH_SOIC8) connected to ATSAMD51 with 4 shared signal nets
- Voltage dividers correctly identified: 10.5K/750 on +12V (ratio 0.067) and 3.48K/681 on +5V (ratio 0.164) - likely feedback dividers for regulators
- 23 RC filters detected across the design
- 3 LC filters found - appropriate for switching regulator output filtering
- Decoupling analysis comprehensive: 9 rails analyzed, VMOT_FUSED has 800.9uF total
- I2C bus (EXP_I2C_SDA) correctly shows pullup resistor R98 to +3.3V

### Incorrect
- Single-pin nets reported on TMC2130 GNDP1 pins (SPI_CS_X/Y/E0/E1/Z2/Z3) - these are likely valid chip-select nets connected via hierarchical sheets, flagged as single-pin because sub-sheet connections are not followed
  (signal_analysis.design_observations)
- Regulator caps flagged as missing for A4403 and AP2112 input/output - likely present but on unnamed nets the analyzer cannot trace back to the regulator
  (signal_analysis.design_observations)
- MOSFET transistor circuits not detected despite board having high-current heater and fan outputs (expected for a Voron printer controller)
  (signal_analysis.transistor_circuits)
- USB D+ flagged as missing ESD protection, but USB may not be a primary interface on this board
  (signal_analysis.design_observations)

### Missed
- No crystal circuit detected - ATSAMD51 typically uses an external crystal/oscillator, likely present but not identified
  (signal_analysis.crystal_circuits)
- TMC2130 SPI bus topology not characterized - 8 stepper drivers sharing SPI with individual chip selects is a key design pattern
  (signal_analysis)
- No current sense detection despite TMC2130 drivers having sense resistors for motor current setting
  (signal_analysis.current_sense)

### Suggestions
- Improve hierarchical sheet traversal to resolve single-pin net false positives
- Add stepper driver IC recognition (TMC2xxx family) with SPI/UART configuration detection
- Detect crystal/oscillator circuits on MCU pins even when custom library symbols are used

---
