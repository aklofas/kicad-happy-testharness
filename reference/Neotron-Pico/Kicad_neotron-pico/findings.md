# Findings: Neotron-Pico / Kicad_neotron-pico

## FND-00001015: I2S bus not detected for TLV320AIC23 CODEC despite clear I2S signals; RC filters R801-R804 / C804-C809 classified as high-pass filters but are DC-blocking coupling caps with load resistors; PWR_FLA...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: audio.kicad_sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Four RC combinations are flagged as high-pass filters with cutoffs of 1.59 Hz and 0.02 Hz. R801-R804 are 100k load/volume-pot resistors; C804/C805 are 1uF and C808/C809 are 100uF AC coupling/blocking capacitors. The topology is a series capacitor (AC coupling) with a shunt resistor to ground, which the analyzer inverts: it labels input_net as the audio signal net and output_net as GND. These are AC coupling stages, not intentional filter circuits. The sub-Hz cutoffs confirm this — no audio filter operates at 1.59 Hz intentionally.
  (signal_analysis)
- Every sub-sheet (audio, bmc, io_exp, rtc, sdcard, video12, raspberry_pico, expansion_slots) generates pwr_flag_warnings saying power rails like +3V3 and GND have no PWR_FLAG. In a hierarchical KiCad design, power is injected into sub-sheets via hierarchical labels from the top level — sub-sheets do not independently require PWR_FLAGs. The audio.kicad_sch does contain a PWR_FLAG symbol, but warnings still fire for +3V3 and GND. This produces 2-4 spurious warnings per sub-sheet (totaling ~25 warnings across the design).
  (signal_analysis)

### Missed
- The audio CODEC (U801, TLV320AIC23BPW) has I2S signals BCLK, LRCIN, LRCOUT, DIN, DOUT connected via hierarchical labels AUDIO_BIT_CLK, AUDIO_DAC_LR, AUDIO_ADC_LR, AUDIO_DAC_DAT, AUDIO_ADC_DATA. These are reported as 'single_pin_nets' in design_observations rather than being identified as an I2S bus. The I2C interface (SDIN/SCLK) is detected as an i2c_bus, but the I2S interface is missed entirely.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001016: Crystal Y1201 '32,768 Hz' frequency parsed as None due to comma in number

- **Status**: new
- **Analyzer**: schematic
- **Source**: rtc.kicad_sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Y1201 value is '32,768 Hz' (comma-formatted). The crystal parser returns frequency: null instead of 32768.0 Hz. Also load_caps is empty, which may be because the RTC uses built-in oscillator capacitors. The frequency parsing failure means crystal_circuits reports an incomplete entry. This also affects the main neotron-pico.kicad_sch which aggregates all sheets.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001017: SPI bus not detected for MCP23S17 IO expander (SPI-interface chip)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: io_exp.kicad_sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- U301 is an MCP23S17_SO, an SPI-interface GPIO expander. Its SPI pins (SCK -> SPI_CLK, SI -> SPI_COPI, ~CS -> ~{SPI_CS}) are listed in single_pin_nets but no spi_buses entry is generated. The SPI bus signals are clearly named but the SPI detector does not trigger on MCP23S17 pin names.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001018: THS7316 triple video buffer classified as 'comparator_or_open_loop' opamp; TPD7S019 ESD protection IC correctly identified protecting 11 VGA/DDC signal nets

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: video12.kicad_sch
- **Created**: 2026-03-23

### Correct
- U402 (TPD7S019) is correctly classified as an esd_ic protecting DDC_SCL, DDC_SDA, HSYNC, VSYNC, VGA_RED, VGA_GRN, VGA_BLU, and related buffered signals. The protected_nets list is accurate for a VGA ESD protection IC.

### Incorrect
- U401 (THS7316) is a triple 3-channel SD/HD video buffer IC, not an opamp comparator. The lib_id references 'TPF133A' (an alternative symbol) and the analyzer assigns configuration 'comparator_or_open_loop'. The THS7316 operates as a unity-gain buffer for video signals and should not be classified as a comparator. The misclassification affects the design_observations output.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001019: R-2R DAC ladder resistor network detected as voltage dividers

- **Status**: new
- **Analyzer**: schematic
- **Source**: dac4.kicad_sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The dac4 schematic is a 4-bit R-2R resistor ladder DAC (only 2k and 1k resistors + GND power symbol, no ICs). The analyzer reports 3 voltage dividers, which are actually sub-sections of the R-2R ladder network. This is a structural misclassification — an R-2R DAC is a well-known pattern that should be identified as a DAC rather than individual voltage dividers. The same pattern appears in video12.kicad_sch (3 instances of dac4 are used for RGB VGA output).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001020: Power supply correctly identifies 3 regulators: switching DC-DC (K78L05), LDO AMS1117-3.3, and LDO HT75xx

- **Status**: new
- **Analyzer**: schematic
- **Source**: powersupply.kicad_sch
- **Created**: 2026-03-23

### Correct
- U1301 (switching +5V from VDC), U1302 (LDO 3.3V from 5V), U1303 (LDO 3.3VP from VDC) are all correctly detected with proper topology and rail assignments. The design has both a switching pre-regulator and linear post-regulators, which is correctly captured.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001021: Unrouted net reporting is misleading: pad_count=2 but both pads are the same reference (e.g. U201.36 twice); Edge clearance warnings report negative values for intentional board-edge connectors; DF...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: neotron-pico.kicad_pcb
- **Created**: 2026-03-23

### Correct
- The DFM tier=advanced is accurate: minimum track width 0.1143mm is below JLCPCB standard 0.127mm threshold. The board size warning (243.84x171.45mm) is also correct — this is a large ATX-form-factor board that would incur premium pricing. Both violations are genuine and actionable.
- The PCB statistics are accurate: this is a single-sided component placement board (242 front, 0 back) with 4 copper layers, consistent with the Neotron Pico design which uses a standard ATX board with all components on the top layer.

### Incorrect
- The 6 'unrouted' nets for U201 pads 35-43 each show pad_count=2 with identical pads (e.g. ['U201.36', 'U201.36']). This is because the RPi_Pico_SMD_TH footprint uses dual-pad construction (one thru_hole + one SMD pad per pin number). These pads share the same net ('unconnected-(U201-3V3-Pad36)') which means they are intentionally no-connect — they appear unrouted because the net has no external connections, not because routing is missing. Reporting routing_complete=False due to these is misleading.
  (signal_analysis)
- J401 (edge_clearance_mm: -6.22), U1301 (-1.9), U802 (-1.14), J1101 (-0.37), J1301 (-0.28) all have negative edge clearance. These are intentional: edge-mount connectors (VGA, DC barrel jack, audio jacks) are designed to overhang the PCB edge. Negative clearance is expected and correct for these connector types. Flagging them as warnings creates false positives for a standard board design.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001022: No gerber files present in repository — gerber analysis not applicable

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: 
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The Neotron-Pico repository contains no Gerber or drill files. It uses KiBot configuration (.kibot/gerbers_jlcpcb.kibot.yml) to generate gerbers on demand. No gerber output directory exists at results/outputs/gerber/Neotron-Pico/. The requested output files (neotron_pico-gerbers.json, neotron_pico-gerbers_v0.5.0.json) do not exist and were never generated.
  (signal_analysis)

### Suggestions
(none)

---
