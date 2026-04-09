# Findings: hsetlik/PolySynth / SplitBoard8Voice_SplitBoard8Voice

## FND-00002523: 8-voice polyphonic synthesizer (581 components, 10 sheets, STM32F411, TPS56528 + L7805/L7905, TL074 opamp arrays, 65 SK6812 LEDs, MIDI, ILI9341 LCD). Strong analysis. Issues: rotary encoders as resistors (RE prefix), TCA9548A I2C mux as level shifter, 24 voice signals as power rails, crystal '32.768kHZ' frequency not parsed (case-sensitive).

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: SplitBoard8Voice_SplitBoard8Voice.kicad_sch.json
- **Created**: 2026-04-09

### Correct
- U201 TL074 quad opamp correctly decomposed into 4 units with correct gain/config
- TPS56528 switching + L7805/L7905 LDOs correctly identified
- Y401 16MHz crystal correctly parsed with 6pF load caps
- Two SK6812 LED chains (50+15) correctly detected
- 22 encoder debounce RC filters correctly detected at 338.63Hz
- ~70 buffer opamps for CV distribution correctly detected

### Incorrect
- RE601-RE609 (9 rotary encoders, lib_id Device:RotaryEncoder) classified as 'resistor' due to RE prefix
  (components)
- U701 TCA9548A I2C mux classified as level_shifter_ic — it's an 8-channel I2C switch
  (signal_analysis.level_shifters)
- 24 voice signals (V1_CLK1..V8_OUT) listed as power_rails — they're digital clock/audio outputs
  (statistics.power_rails)
- Y402 '32.768kHZ' frequency=null — capital HZ not recognized
  (signal_analysis.crystal_circuits)
- TPS56528 output_rail is '__unnamed_28' instead of +3.3V (Schottky OR-ing diode not traced)
  (signal_analysis.power_regulators)

### Missed
- MIDI interface (3 DIN connectors, 6N138 optocoupler, MIDI_RX/TX) not detected
  (signal_analysis)
- U301 DAC7578 8-channel I2C DAC not identified as DAC
  (signal_analysis.adc_circuits)
- Audio output circuit (TL074 mixing to stereo jack) not in audio_circuits
  (signal_analysis.audio_circuits)

### Suggestions
- Case-insensitive frequency unit parsing for crystals
- Detect rotary encoders via lib_id Device:RotaryEncoder, not RE prefix
- Distinguish I2C mux (TCA9548) from level shifter
- Filter global_labels with 'output' shape from power_rails
- Trace through Schottky diodes for regulator output rail mapping

---
