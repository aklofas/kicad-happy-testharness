# Findings: winneymj/kicad-mem_disp_adaptor / epoch

## FND-00002196: False positive I2C bus: crystal oscillator feedback path (U1 SCL pin + R1 1M + U2 inverter) misidentified as I2C SCL line; Decoupling capacitor C1 not credited to U1 or U2 in decoupling_analysis de...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-mem_disp_adaptor_epoch.sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- Net __unnamed_5 connects MCP7940N U1 pin 6 (SCL output) to 74HC1G14GW U2 pin 2 (A input) with R1 (1M ohm) as a feedback resistor. This is a classic Pierce/inverter crystal oscillator configuration: the inverter (U2) and 1M feedback resistor form the oscillator circuit driving the RTC crystal. The analyzer reports this as a third I2C SCL bus with pullup R1 at 1000000 ohms — but a 1M ohm value is far outside any valid I2C pullup range (typically 1-10k), and U2 is a logic inverter, not an I2C device. The real I2C buses (SCL and SDA nets going to the external connector P2) are correctly detected. Only the __unnamed_5 entry is spurious.
  (design_analysis)
- C1 (0.1uF) connects directly between (+3.3) and (GND), the same power rails used by U1 (MCP7940N) and U2 (74HC1G14GW). The design_observations section correctly reports both ICs have rails_without_caps, and the PCB decoupling_placement section correctly finds C1 nearby. However, signal_analysis.decoupling_analysis is completely empty — it should list C1 as a decoupling cap associated with the power rail, even if the spatial proximity cannot be confirmed from schematic coordinates alone. The observations section shows the right data but is nested under design_observations rather than the dedicated decoupling_analysis list.
  (signal_analysis)

### Missed
- The design has three nets with canonical SPI names (SPI_CLK, SPI_CS, SPI_SI) routing between P1 (FFC display connector) and P2 (pin header). While no IC is on the SPI bus (the board is a passive adapter), the net_classification correctly labels SPI_CLK as 'clock' and SPI_CS as 'chip_select'. The bus_analysis.spi is empty — the analyzer could at minimum report the SPI signal group passing through even without an identified controller.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002197: Crystal Y1 with 4-pad footprint correctly parsed; via-in-pad correctly flagged on P1 pad 12

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad-mem_disp_adaptor_epoch.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies Y1 (Crystal_SMD_Citizen_CM200C) with pad_count=4 (two signal pads plus two NC mechanical pads), and the via_in_pad analysis correctly flags a via at (163.576, 89.154) near P1 pad 12 with same_net=false. The board outline (23.37 x 26.67 mm) and 2-layer stackup with copper fills on F.Cu (+3.3) and B.Cu (GND) are all accurately reported.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
