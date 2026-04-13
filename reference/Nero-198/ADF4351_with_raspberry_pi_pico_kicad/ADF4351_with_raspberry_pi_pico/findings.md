# Findings: Nero-198/ADF4351_with_raspberry_pi_pico_kicad / ADF4351_with_raspberry_pi_pico

## FND-00000337: I2C pull-up status contradicts between design_observations and bus_analysis; DNP pull-up resistors reported as active pull-ups in design_observations; ADF4351 3-wire SPI control interface not detec...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ADF4351_with_raspberry_pi_pico.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- design_observations reports I2C0_SDA has_pullup=true (pullup_resistor=R2, pullup_rail=+3.3V) and I2C0_SCL has_pullup=true (pullup_resistor=R1), but bus_analysis.i2c reports has_pull_up=false and pull_ups=[] for both I2C0_SDA and I2C0_SCL. The two sections contradict each other. Both R1 and R2 are DNP (do_not_place=true, value='NC'), so the pull-ups are not assembled; bus_analysis is correct that there are no effective pull-ups in circuit.
- Despite the repo being named 'ADF4351_with_raspberry_pi_pico_kicad', this schematic is the Raspberry Pi Pico controller board only. The ADF4351 RF synthesizer is an off-board module connected via the 'to PLL connector' (J6, J2). There are no RF components (inductors, capacitors, matching networks, the ADF4351 IC) in the schematic. The analyzer output correctly shows rf_chains=[] and rf_matching=[]. This is accurate but the design context should be noted: the absence of RF detections is correct for this partial design.

### Incorrect
(none)

### Missed
- R1 and R2 are both marked DNP=true with value='NC' in the schematic. The design_observations section reports the I2C lines have pull-ups via R1 and R2 (has_pullup=true, pullup_rail=+3.3V). This is misleading: the assembled board has no I2C pull-ups because these resistors are DNP. The analyzer should qualify pull-up detections by whether the resistors are DNP.
  (signal_analysis)
- The schematic has nets CLK (GPIO2/SPI0_SCK), DAT (GPIO3/SPI0_TX), CE (GPIO5), and LE (GPIO7) connecting via J6 and J2 to an external ADF4351 PLL module labeled 'to PLL connector'. These form a 3-wire SPI-like interface for the ADF4351. bus_analysis.spi is empty []. GPIO2 and GPIO3 carry SPI0_SCK and SPI0_TX alternate functions respectively per the Pico pinout, but the net names CLK/DAT do not use the SPI naming convention. No SPI bus was detected.
  (design_analysis)

### Suggestions
(none)

---
