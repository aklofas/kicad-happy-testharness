# Findings: fiberaudio-108 / pcb_fiberaudio-108

## FND-00002067: LD1 LED misclassified as inductor type; USB ESD protection device SRV05-4 not detected; has_esd=false for both USB differential pairs; False positive cross-domain level-shifter warning for SPI bus ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_fiberaudio-108_pcb_fiberaudio-108.sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies the SPI bus with bus_id 'EE', full_duplex mode, one chip select, and the correct MOSI/MISO signals (EEMOSI, EEMISO). The crystal (Y1, 12MHz) load cap circuit is also detected correctly with CL_eff=13pF from 20pF+20pF caps. Decoupling coverage on +5V and +3.3V rails is correctly cataloged.

### Incorrect
- LD1 is a red LED (lib_id: Device:LED, footprint: LED_SMD:LED_0603_1608Metric) but is classified as type 'inductor' in both the BOM and components list. The root cause is in the reference prefix resolution: prefix 'LD' has no entry in the type_map, so the code falls through to the single-character fallback where 'L' maps to 'inductor'. The lib_id check ('device:led') does not fire the led-override because the led-in-lib check at line 511 requires both 'led' AND 'diode' in lib_lower. Fix: add 'LD' as a key in type_map mapping to 'led', or add an override in the single-char fallback block for result=='inductor' that checks for 'led' in lib_lower.
  (statistics)
- U3 (SRV05-4, lib_id: Power_Protection:SRV05-4) is a USB ESD suppressor that connects directly to the USBD_P and USBD_N lines. The ESD detection code at signal_detectors.py line 1728 correctly identifies it as a protection device via 'power_protection:' prefix, but then iterates over U3's pins to find protected nets. In the KiCad 5 legacy parser output, U3 has pins=[] (empty), so no protected nets are gathered and the device is not added to protection_devices. Consequently the differential pair entries for USBD_P/USBD_N and USBD_IN_P/USBD_IN_N both show has_esd=False, which is incorrect — ESD protection is present. Root cause: KiCad 5 legacy pin data not populated for this component.
  (signal_analysis)
- design_analysis.cross_domain_signals flags EECS, EESK, and EEMOSI as needing a level shifter because U1 (AT93C46D EEPROM) appears to be on power domain '__unnamed_3' (an unresolved single-pin net) while U2 (CM108AH) is on +3.3V/+5V. In reality, the PCB confirms U1 pin 8 (VCC) connects to +3V3 — both devices operate at 3.3V logic so no level shifter is needed. The KiCad 5 legacy parser fails to trace the U1 VCC connection through to the named +3.3V power rail, leaving it as an unnamed single-pin net, which causes a spurious cross-domain warning.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---
