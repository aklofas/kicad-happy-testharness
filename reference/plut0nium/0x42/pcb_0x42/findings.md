# Findings: plut0nium/0x42 / pcb_0x42

## FND-00000326: ESD protection PRTR5V0U2X not detected; key matrix switch count likely overcounted due to dual-unit Key_Switch_LED symbols

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pcb_0x42.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Key matrix switch count likely overcounted due to Key_Switch_LED dual-unit symbols (switch + LED counted separately)
  (signal_analysis)

### Missed
- ESD1 (PRTR5V0U2X, lib: Power_Protection:PRTR5V0U2X) on USB data lines not detected as protection_device
  (signal_analysis)

### Suggestions
- Recognize Power_Protection library symbols as protection devices

---

## FND-00000327: ESD1 (PRTR5V0U2X) missing from protection_devices, causing has_esd_protection=false on USB data lines; Key matrix reports 162 switches/keys instead of actual 70 (overcounts multi-unit Key_Switch_LE...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pcb_0x42.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The schematic uses a 2-unit Key_Switch_LED symbol (unit 1 = switch contacts, unit 2 = LED). The key matrix is 5 rows x 14 columns = 70 physical key positions, confirmed by 70 unique diode refs (D000-D413). However, the topology-based detection counts each unit of each multi-unit symbol as a separate switch, giving 162 (= 70 K-symbols × 2 units + 11 Kb-symbols × 2 units). The correct answer for estimated_keys is 70. The matrix dimensions (rows:5, columns:14) are correct.
  (signal_analysis)

### Missed
- ESD1 is a PRTR5V0U2X USB ESD protection IC (Nexperia, Power_Protection:PRTR5V0U2X library) directly connected to D+ and D- nets. It is absent from signal_analysis.protection_devices because the component is classified as type='other' (not 'ic' or 'diode'), causing it to fall through both the diode-based and IC-based code paths in detect_protection_devices. As a result, the design_observations for net 'D+' and 'D-' both report has_esd_protection: false even though ESD1 is clearly present on both nets.
  (signal_analysis)
- R5 (1k resistor) sits between RP2040 U1 XOUT pin (net __unnamed_14) and Y1 crystal pin 3 / C14 load cap (net __unnamed_12). This is the standard RP2040 crystal feedback series resistor recommended in the RP2040 hardware design guide for oscillation stability. The crystal_circuits detection reports C14 as a direct load capacitor on that crystal pin, but C14 is actually in series with R5 — the analyzer does not report R5 as a series_resistor in the crystal circuit entry for Y1.
  (signal_analysis)

### Suggestions
(none)

---
