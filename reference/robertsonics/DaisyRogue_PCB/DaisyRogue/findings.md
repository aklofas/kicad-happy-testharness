# Findings: robertsonics/DaisyRogue_PCB / DaisyRogue

## FND-00000465: Component inventory (40 parts, 11 unique) and BOM correctly extracted; PCM1681TPWPQ1 (U3) pin-to-net mapping is fully and correctly resolved; I2C bus detection correct for U3 SCL/SDA with 2.2K pull...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Audio.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies all 40 components: 25 capacitors (3300pF ×8, 22uF ×8, 1.0uF ×4, 2.2uF ×2, 10uF ×2, 10nF ×1), 10 resistors (all 2.2K), 2 ferrite beads (600R), 1 connector (J2 Conn_02x13_Odd_Even), 2 ICs (U3 PCM1681TPWPQ1, U4 LP2985-5.0). Values, footprints, and lib_ids all match the source. The 5 power rails (+3V3, +5VA, GND, GNDA, VIN) are correctly identified.
- All 29 pins of U3 (including the EPAD pin 29) are correctly mapped to their nets. Key verified mappings: pin 9 VDD → +3V3, pin 10 DGND → GND, pin 17 VCC1 → +5VA, pin 18 AGND1 → GNDA, pin 23 VCC2 → +5VA, pin 24 AGND2 → GNDA, pin 25 VCOM → VCOM, pins 15–22 VOUT1–VOUT8 → OUT1–OUT8 nets with the correct coupling capacitors (22uF each). Pins 2, 11–14 tied to GND (correct — mode select strapping). Pins 5–8 (SCK/DATA1/BCK/LRCK) correctly mapped to TDM_MCLK/TDM_DO/TDM_BCLK/TDM_FS.
- The analyzer correctly detects SCL (U3 pin 3 MC/SCL/DEMP) and SDA (U3 pin 4 MD/SDA/MUTE) as I2C lines, each with a 2.2K pull-up resistor to +3V3 (R4 on SCL, R3 on SDA). Pull-up direction ('pull-up', to_rail '+3V3') is correct.
- U4 LP2985-5.0 is correctly classified as an LDO regulator. Its output (pin 5 VOUT) correctly maps to the +5VA net. The bypass cap C24 (10nF) on pin 4 (BP) is correctly associated. The inrush analysis correctly attributes C25 (2.2uF), C21 (1.0uF), C20 (1.0uF), C22 (10uF) as output caps totaling 14.2uF.
- The analyzer correctly identifies two separate ground domains: GND (digital, connected to U3 DGND pin 10 and FB2 pin 2) and GNDA (analog, connected to U3 AGND1 pin 18, AGND2 pin 24, and all the analog bypass caps C11–C18, C19–C25). FB2 (600R ferrite bead) correctly bridges GND to GNDA, and FB1 bridges VIN to the U4 input node. This analog/digital ground separation is correctly captured.
- Each of the 8 DAC outputs has a 22uF coupling capacitor correctly traced: VOUT8 (pin 15) → C3, VOUT7 (pin 16) → C7, VOUT6 (pin 19) → C4, VOUT5 (pin 20) → C8, VOUT4 (pin 21) → C5, VOUT3 (pin 22) → C9, VOUT2 (pin 26) → C6, VOUT1 (pin 27) → C10. Each has a downstream RC filter (Rxx + Cxx 3300pF) and connector output correctly traced through the 8-resistor and 8-capacitor RC filter stage.
- The VCOM net correctly connects U3 pin 25 (VCOM power_in), C19 pin 1 (2.2uF bypass), and J2 pin 25. The ERC warning about VCOM having no output driver is appropriate since VCOM is an output of the PCM1681 that the schematic expects to come in from the connector J2 (it is driven by the chip itself but the symbol shows power_in).

### Incorrect
- In power_domains.ic_power_rails, U4 is listed with power_rails=['+5VA', '__unnamed_3']. The '__unnamed_3' net is the node between FB1 pin 1 and U4 pins 1 (VIN) and 3 (ON/OFF). The actual supply net connecting FB1 pin 2 to the VIN hierarchical label is named 'VIN'. The issue is that FB1 creates an intermediate unlabeled node between the VIN hierarchical label and U4's VIN pin, so the analyzer sees an unnamed net rather than 'VIN' as U4's supply. The domain_groups for U4 incorrectly lists '__unnamed_3' instead of VIN. This is a net-naming propagation issue through a ferrite bead.
  (signal_analysis)

### Missed
- U3 (PCM1681TPWPQ1) is an 8-channel DAC with a TDM/I2S serial audio interface. Its four TDM signals (TDM_MCLK → SCK pin 5, TDM_DO → DATA1 pin 6, TDM_BCLK → BCK pin 7, TDM_FS → LRCK pin 8) are present in the nets and flagged as single-pin nets (correctly noting they're sub-sheet hierarchical connections), but no I2S/TDM bus group is detected in bus_analysis. The analyzer detects I2C correctly but does not detect this audio serial bus.
  (signal_analysis)
- Each of the 8 DAC output channels has an RC low-pass filter formed by one 2.2K resistor and one 3300pF capacitor (e.g. R7+C15 for OUT7/J2 pin 18, R9+C12 for OUT1/J2 pin 12, etc.). These 8 RC filter pairs are clearly present in the netlist but are not identified as low-pass filters in any signal_paths or filter detector output. The analyzer does not have a 'signal_paths' or 'filter_detectors' section in its output at all for this file.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000466: Component inventory correctly extracted: 20 components including Daisy Seed (A1), LM1117 (U5), AT25DF256 (U6); SPI bus to AT25DF256 flash (U6) correctly detected with bus_id 'MEM'; SD card bus (SDI...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Daisy.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies all 20 components: A1 (Device_Audio_Electrosmith_Daisy_Seed_Rev4), U5 (LM1117-5.0 LDO in SOT-223), U6 (AT25DF256-SSHN-T SPI Flash in SOIC), J3 (Conn_01x02), J4 (PJ-059A barrel jack), J5 (connector), 9 resistors, 5 capacitors. Power rails +3V3, +5V, AGND, GND, VIN are all correct. The 1 DNP part (R14 with value='DNP') is correctly detected via value-field inspection.
- The SPI bus connecting A1 (Daisy Seed) to U6 (AT25DF256 SPI flash) is correctly detected as bus_id 'MEM' with signals MEM_MISO, MEM_MOSI, MEM_SCK. Both devices A1 and U6 are correctly listed. chip_select_count=1, bus_mode='full_duplex' are correct. MEM_WP (write-protect) is also identified as a cross-domain signal.
- The SDIO bus is correctly detected with bus_width=4, signals SD_D0–SD_D3, SD_CMD, SD_CLK, and device A1 (Daisy Seed). has_pullups=true with pullup_signals correctly listing CMD, D0, D1, D2, D3.
- The Daisy.kicad_sch sheet shows A1 pins I2C1_SCL and I2C1_SDA connected to nets SCL and SDA which are hierarchical labels going to the Audio sheet. The analyzer correctly detects the I2C bus with has_pull_up=false in this sub-sheet's context (the pull-ups R3 and R4 are in the Audio.kicad_sch sheet, not visible here). This is accurate per-sheet analysis.
- U5 (LM1117-5.0 in SOT-223 package) is correctly classified as an LDO regulator with output_voltage=5.0V, topology='LDO', output_rail='+5V'. The output capacitor C27 (10uF, 0805) is correctly identified in inrush_analysis. VIN and +5V as power rails for U5 are correct.

### Incorrect
- The cross_domain_signals section flags MEM_MISO, MEM_MOSI, MEM_WP, MEM_CS, MEM_SCK as crossing between '+3V3' (U6's domain) and 'VIN' (A1's domain), with needs_level_shifter=false. However, A1 (Daisy Seed) is a 3.3V microcontroller module that internally regulates from VIN; its I/O signals are 3.3V. U6 is also 3.3V. The cross-domain analysis is technically correct in noting VIN is A1's VCC pin, but this likely overstates the concern since A1 is a complete module with internal regulation, not a bare microcontroller whose I/O voltage follows VIN directly. The needs_level_shifter=false conclusion is correct, but the cross-domain flagging could be misleading.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000467: Component inventory correctly extracted: 10 components including H11L1STA optocoupler (U2), USBLC6-2SC6 (U1), STMPS2151STR USB power switch (U7); USB differential pair (DP/DM) with ESD protection (...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Interfaces.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies all 10 components: U1 (USBLC6-2SC6 USB ESD protection SOT-23-6), U2 (H11L1STA optocoupler 6-pin), U7 (STMPS2151STR USB power switch SOT-23-5), D1 (D_Schottky SOD-323), J1 (Conn_02x13_Odd_Even), P1 (connector), R1 (2.2K), R2 (unknown), R22 (10K), R23 (unknown). Power rails +3V3, +5V, GND correctly identified.
- The differential_pairs section correctly identifies DP and DM as a USB differential pair, lists shared_ics=[U1], has_esd=true, and esd_protection=[U1]. The USBLC6-2SC6 is correctly recognized as providing ESD protection for the USB lines.
- TX and RX are detected in the UART bus_analysis with pin_count=1 each (TX connects to J1 pin 18, RX to J1 pin 20 in this sheet). In the Daisy sheet, TX connects to A1 USART1_TX and RX to A1 with pin_count=2. The per-sheet analysis is accurate for both.

### Incorrect
(none)

### Missed
- U2 (H11L1STA) is a 6-pin high-speed logic output optocoupler used in MIDI receive circuits. The MIDI_IN hierarchical label connects through R1 (2.2K current-limiting resistor) to the optocoupler LED input. The output connects back to the Daisy sheet via the MIDI_IN signal. The analyzer correctly identifies U2 as an IC with +3V3 power domain, but does not identify it as a MIDI input isolator or flag the characteristic optocoupler MIDI receive topology. No MIDI-related signal category is present.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000468: Top-level hierarchical schematic correctly flattened: 74 total components from 3 sub-sheets; Power rail '/ae936f30-33f3-410a-847a-0a2e1cfd0bc7/VIN' appears as a distinct power rail due to scoped ne...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: DaisyRogue.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The DaisyRogue.kicad_sch is the hierarchical top-level sheet containing 3 sub-sheets (Daisy.kicad_sch, Interfaces.kicad_sch, Audio.kicad_sch). The analyzer correctly flattens and combines all sub-sheet components: 74 total (40 Audio + 20 Daisy + 10 Interfaces + 4 mounting holes at top level = 74). The component_types breakdown (mounting_hole: 4, resistor: 23, capacitor: 30, ic: 8, connector: 6, diode: 1, ferrite_bead: 2) matches the union of all sub-sheets. The sheets list at the end correctly enumerates all 4 processed files.
- The top-level DaisyRogue JSON correctly aggregates bus detections from all sub-sheets: I2C SCL/SDA (A1 + pull-ups R3/R4), SPI bus MEM (A1 ↔ U6 AT25DF256), SDIO bus SD 4-bit (A1 with pull-ups), UART TX/RX (A1). USB differential pair DP/DM with ESD (U1) is also present. This comprehensive bus detection is correct.
- R14 in Daisy.kicad_sch uses the old-style value='DNP' marker (not the KiCad 7+ (dnp yes) attribute). The analyzer correctly detects this as DNP through value-field inspection. Both the Daisy.kicad_sch and DaisyRogue.kicad_sch outputs show dnp_parts=1, correctly identifying R14.

### Incorrect
- The power_rails list in statistics includes both 'VIN' and '/ae936f30-33f3-410a-847a-0a2e1cfd0bc7/VIN'. The UUID-prefixed name is a scoped internal net path from the hierarchical sheet traversal, representing the same VIN rail within a sub-sheet context. These are the same physical net but appear as two separate power rails in the flattened output. This is a net naming artifact from hierarchical sheet UUID scoping. It is not a real second power rail.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
