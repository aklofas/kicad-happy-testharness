# Findings: fanpico / boards_fanpico-0804D_kicad_fanpico

## FND-00000129: FanPico 0804D is an 8-channel PWM fan controller with RP2040 (Pico module), 74HC4051 analog mux for tachometer reading, SN74AHCT126 buffers for PWM signal routing, LM4040 voltage reference, and SPX1117 adjustable LDO. The analyzer correctly identifies 4 MOSFET transistor circuits (2N7002K open-drain tachometer outputs), 41 protection devices (TVS diodes on all I/O), and the SPX1117 power regulator. However, all 214 components have category=None, and the ERC warnings reveal genuine design insights.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/fanpico/boards/fanpico-0804D/kicad/fanpico.kicad_sch
- **Related**: KH-047
- **Created**: 2026-03-14

### Correct
- Four 2N7002K MOSFET transistor circuits correctly identified as open-drain switches with 1k gate resistors, driving TACHO_OUT from RP2040 GPIOs - these are tachometer signal level shifters
- 41 protection devices correctly identified including TVS diodes on signal lines (3.3V TVS on SPI/UART, 12V TVS on auxiliary power input)
- SPX1117-ADJ power regulator correctly identified as adjustable LDO
- LM4040DBZ-3 correctly placed in subcircuit analysis as 3.000V precision voltage reference for ADC
- ERC warning correctly flags PWM_GEN net with 8 output drivers - this is the fan PWM bus where all 8 channels share a common PWM output (valid design but worth noting)
- ERC warning correctly identifies ADC_REF net has no output driver - the LM4040 shunt reference cathode is passive-typed
- Power domains correctly identified with 9 rails including PWR_IN, PWR_OUT separation for external fan power

### Incorrect
- All 214 components have category=None despite component_types correctly counting 59 resistors, 57 diodes, 28 capacitors, 21 connectors, 17 LEDs, etc.
  (components[*].category)
- Voltage divider count is only 2, but the SPX1117-ADJ feedback network (which sets output voltage) should be detected as a voltage divider with a purpose annotation
  (signal_analysis.voltage_dividers)

### Missed
- PWM fan control topology not identified. The core function of this board (RP2040 generating PWM signals routed through SN74AHCT126 buffers to fan headers) is not captured in any signal analysis section.
  (signal_analysis)
- 74HC4051 analog multiplexer function not identified. This mux routes 8 tachometer inputs to a single ADC channel on the RP2040 - a key design pattern for reducing GPIO usage.
  (subcircuits)
- SN74AHCT126 buffer function not identified. Two quad buffers route PWM signals to fan headers with level shifting (3.3V to 5V tolerant).
  (subcircuits)
- No I2C detection for the OLED display connector, despite having I2C signal names on the connector pins
  (design_analysis.bus_analysis)

### Suggestions
- PWM signal detection could identify timer/counter output pins driving loads through buffers
- Analog multiplexer detection would be valuable for understanding sensor multiplexing topologies
- Buffer IC detection (74HC/74AHC series) could identify level shifting and signal conditioning

---
