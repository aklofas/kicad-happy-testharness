# Findings: 16x16-led-matrix / 16x16matrix

## FND-00000310: SPI bus not detected for MAX7219 interface; MAX7219 LED driver not detected as addressable_led_chain or LED driver subcircuit; PWR_FLAG warnings incorrectly fire despite PWR_FLAG symbols being pres...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: OneMatrix.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The schematic title_block.title is '8x8 LED matrix' which the analyzer correctly reports. The repo is named '16x16-led-matrix' and the design appears to be one tile of a 16x16 arrangement (connectors allow daisy-chaining multiple MAX7219 units). This is not an analyzer error — the title is correct for one tile. No action needed; documenting for awareness.

### Incorrect
- The pwr_flag_warnings section reports that +5V and GND have no PWR_FLAG. However, two power:PWR_FLAG symbols are placed in the schematic: one at (74.295, 107.315) wired to the GND rail, and one at (74.295, 86.995) wired to the +5V rail. The analyzer records them in power_symbols with net_name 'PWR_FLAG' (their Value property) rather than resolving the actual connected net. This causes the warning to fire incorrectly. The power_rails list even includes 'PWR_FLAG' as a third rail, showing the net resolution failure.
  (pwr_flag_warnings)
- Nets R0-R7 each have 2 'output' type pins flagged as driver conflicts: one from MAX7219 DIG_x pins (output) and one from the 8x8 LED matrix D4 row pins (also typed 'output' in the KiCad symbol). In reality, the LED matrix row pins are not active drivers — they are passive anode/cathode connections. The 'output' pin type on D4 is a library symbol choice, not an actual conflicting driver. All 8 ERC output_conflict warnings (R0-R7) are false positives arising from the LED matrix symbol using 'output' pin type for its cathode/anode connections.
  (design_analysis)
- R4 (9.53k) connects from +5V to the MAX7219 ISET pin (pin 18). The analyzer classifies it as a 'pull-up' resistor with direction 'pull-up' to_net '+5V'. Topologically this is correct (resistor between supply and signal pin), but functionally R4 is the LED current-setting resistor — a dedicated function of the MAX7219 ISET pin, not a pull-up. The classification doesn't cause wrong behavior but could mislead anyone reading the output. A resistor connected to a pin named 'ISET' should be recognized as a current-set resistor.
  (ic_pin_analysis)

### Missed
- The MAX7219 (U4) uses a 3-wire SPI interface. Nets CLK, DIN, and CS (LOAD pin) are all present and connected to connectors J7/J8 for daisy-chaining. The bus_analysis.spi array is empty. The DIN, CLK, and CS net names on an IC with lib_id 'Driver_LED:MAX7219' are clear SPI indicators that should be detected.
  (signal_analysis)
- The circuit is a MAX7219 8x8 LED matrix driver — a classic LED driver topology. The signal_analysis.addressable_led_chains array is empty. While the MAX7219 drives a passive LED matrix (not individually addressable WS2812-style LEDs), it should still be detected as an LED driver circuit. The subcircuit section does identify U4 as 'LED driver' function, but no LED-specific signal analysis entry is generated.
  (signal_analysis)

### Suggestions
- Fix: R4 ISET resistor misclassified as pull-up on ISET pin

---
