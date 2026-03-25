# Findings: RP2040-designguide / PCB_RP2040-Guide

## FND-00001179: RP2040 crystal circuit correctly detected: 12MHz Y1, 22pF load caps C2/C3, CL_eff=14pF; USB-C compliance checks pass for CC1/CC2 5.1k pulldowns and USBLC6 ESD protection; pwr_flag_warnings fires fo...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RP2040-Guide.kicad_sch
- **Created**: 2026-03-23

### Correct
- Crystal circuit parsed correctly. 22pF series combo + 3pF stray = 14pF effective load, appropriate for 12MHz RP2040 oscillator.
- J1 USB-C connector has R3 and R4 (5.1k) on CC1/CC2 correctly detected as pulldown resistors. U2 USBLC6-2SC6 is correctly identified as USB ESD protection IC. cc1/cc2_pulldown_5k1 checks pass.

### Incorrect
- The +3V3 rail is the RP2040 internal 3.3V output (driven by the internal LDO of the RP2040 plus the external XC6206 LDO U4 on +3.3V). The warning that '+3V3 has power_in pins but no power_out or PWR_FLAG' fires because the KiCad 6 schematic has no explicit PWR_FLAG symbol on those rails. This is a real ERC advisory in KiCad, correctly detected, but may appear excessive if the connector J1 (USB-C) implicitly provides power.
  (signal_analysis)
- SW1 has in_bom=false (it is excluded from BOM via the KiCad property), yet it does not appear in missing_mpn — actually checking confirms SW1 is absent from missing_mpn, which is correct. However, the sourcing_audit still lists 31 missing MPN including components with LCSC numbers populated (C1, C2, etc.), because mpn field is empty even though lcsc is present. The MPN coverage reported as 0/31 is misleading since most passives have LCSC part numbers.
  (signal_analysis)

### Missed
- The sourcing_audit reports mpn_percent=0.0 and lists all 31 components as missing_mpn. However, most components have lcsc fields populated (C1=C1525, U3=C2040, U4=C5446, etc.). The MPN coverage metric should consider lcsc as an equivalent sourcing identifier. As-is, the audit overstates sourcing gaps for this well-populated design guide.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001180: 2-layer board 45.2x93.4mm, 36 components (31 back-side SMD, 5 front THT), fully routed; DFM tier 'standard': min track 0.2mm, min drill 0.3mm, min annular ring 0.125mm — no violations

- **Status**: new
- **Analyzer**: pcb
- **Source**: RP2040-Guide.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Component placement with majority on back side (31) and 5 THT on front is unusual but correctly detected. 433 track segments, 32 vias, 3 zones, net count 58, routing complete — all plausible for an RP2040 reference design.
- These are tight but achievable tolerances consistent with a 4-layer-class design at standard PCB fabs. Zero DFM violations reported, consistent with a clean reference design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
