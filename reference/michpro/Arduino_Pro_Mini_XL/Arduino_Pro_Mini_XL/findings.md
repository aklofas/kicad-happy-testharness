# Findings: Arduino_Pro_Mini_XL / Arduino_Pro_Mini_XL

## FND-00000373: RC filter detector misidentifies DTR auto-reset network as an RC filter with DTR as ground net; Bus topology reports width=13 for 'A' prefix bus covering only nets A0-A7 (8 signals, 6 connected); Y...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Arduino_Pro_Mini_XL.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The schematic has a standard Arduino DTR auto-reset circuit: C7 (100n) couples DTR to RST, and R1 (10k) pulls RST high to VCC. The RC filter detector reports this as an RC filter with input_net='RST', output_net='VCC', ground_net='DTR'. DTR is a UART control signal, not a ground net. The actual topology is a series capacitor between DTR and RST (for edge-triggered reset from DTR toggling), not a shunt RC filter. The ground_net field is wrong and the filter classification is incorrect — this is a coupling/reset network, not a low-pass filter.
  (signal_analysis)
- The bus_topology section reports prefix='A', width=13, range='A0..A7'. A0..A7 is at most 8 signals. The reported width of 13 is inflated — it appears to be counting all net labels containing 'A' (including non-bus nets like 'A0'-'A7' plus auxiliary nets from the module). The correct width for an A0..A7 bus is 8 (or 6 if only counting connected signals, since A4 and A5 are missing per the missing list). width=13 is incorrect.
  (bus_topology)
- The pwr_flag_warnings section flags VCC and GND as having no PWR_FLAG or power_out driver. This design is the Arduino Pro Mini XL itself — power comes in through the M1 module symbol's P_VCC (bidirectional) and VCC pins which bridge the external supply to the on-board rail. The M1 symbol provides bidirectional pins that carry power, so ERC would not necessarily flag this in KiCad. The warning overstates the issue for designs where power is implicitly supplied through a module/connector symbol with bidirectional power pins.
  (pwr_flag_warnings)

### Missed
- Y1 uses lib_id 'archive:Device_Crystal_GND2_Small' and footprint 'footprints:muRata-resonator_SMD_CSTCExxM00G55-R0'. The CSTCE series are 3-pin ceramic resonators with integrated load capacitors, not discrete quartz crystals. The analyzer correctly notes no load_caps in the crystal_circuits entry, but classifies Y1 as type='crystal' throughout. A more accurate classification would be 'resonator'. The footprint filter warning already flags the mismatch. This is cosmetic but could mislead design review about whether load caps are missing.
  (signal_analysis)

### Suggestions
(none)

---
