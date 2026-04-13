# Findings: whatnick/IotaWatt_Kicad / IotaWatt3.2

## FND-00000650: 62 resistors present but zero voltage dividers detected — AC current transformer divider networks missed; Spurious SPI entries with MISO mapped to GND net — false positive pin-name matching in lega...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: IotaWatt3.2.sch.json
- **Created**: 2026-03-23

### Correct
- bus_analysis.i2c correctly identifies SCL and SDA nets connecting U$16 (NODEMCU) and U$17 (PCF8523_RTC). Missing pull-up detection (has_pull_up=false) is worth verifying against the schematic.

### Incorrect
- bus_analysis.spi has two phantom entries (bus_id 'pin_U$16', 'pin_U$19') where MISO resolves to the GND net and contains 7 devices. This is a false positive from legacy .sch pin-name matching conflating unrelated GND-connected pins with SPI MISO. The third bus entry (bus_id '0') appears correct.
  (signal_analysis)
- statistics.power_rails lists only 'GND'. The board uses '3V3' as a local net label throughout but without a KiCad power symbol, so the analyzer misses it as a power rail. This is expected behavior but means decoupling_analysis is empty and LDO output rail is untracked.
  (signal_analysis)

### Missed
- IotaWatt is a current/voltage monitoring board with many resistive divider networks for scaling AC signals from current transformers to ADC range. The analyzer detects no voltage_dividers despite 62 resistors. This is a significant false negative, likely because the KiCad 5 legacy net naming (N$x) prevents net-topology tracing that the divider detector relies on.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000651: Correctly handles KiCad v4 placeholder PCB with 0 footprints and 0 tracks

- **Status**: new
- **Analyzer**: pcb
- **Source**: IotaWatt3.2.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The file is an Eagle import stub with explicit 'DUMMY SAVE FILE' warning text. The analyzer returns 0 footprints/tracks and surfaces the silkscreen warning text. Appropriate handling of this degenerate case.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
