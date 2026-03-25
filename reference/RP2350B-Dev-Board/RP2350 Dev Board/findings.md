# Findings: RP2350B-Dev-Board / RP2350 Dev Board

## FND-00001238: X1 crystal (ABRACON X252012MMB4SI-24, 24MHz) misclassified as type='connector'; VREG_LX (RP2350B switching inductor node) treated as a power domain, generating 6 spurious cross_domain_signals; W25Q...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RP2350 Dev Board.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- U3 (ME6217C33M5G, lib_id EasyEDA:ME6217C33M5G) correctly identified as LDO with VSYS input and 3V3 output. Power sequencing finds CE pin on 3V3_EN net with pull-up via J2/R11. USB-C USB compliance checks (CC1/CC2 pass, VBUS ESD/decoupling fail) are correct for this design.

### Incorrect
- X1 has lib_id 'ProPrj_RP2-easyedapro:X252012MMB4SI-24' — an EasyEDA/LCSC project library. The analyzer classifies it as 'connector' because neither the lib_id nor value string matches crystal detection heuristics. No crystal_circuits entry is generated, so crystal load capacitor analysis and frequency verification are skipped entirely.
  (signal_analysis)
- U1 (RP2350B) has VREG_LX as one of its pin-connected power nets (the inductor pad for the internal SMPS). The analyzer includes VREG_LX in the IC's power domain set, then reports all 6 QSPI unnamed nets as crossing three domains (1V1, 3V3, VREG_LX). VREG_LX is a switching node — not an IO power rail — so these cross-domain warnings are false positives. The real cross-domain issue (1V1 core vs 3V3 IO) is valid but obscured by the VREG_LX noise.
  (signal_analysis)
- U4 uses a JLCPCB-specific library path. Despite the value being 'W25Q128' and the description clearly saying '128Mbit NOR FLASH', the memory_interfaces detector produces an empty list. Memory detection relies on lib_id pattern matching (e.g. 'Memory_Flash:') and misses JLCPCB/EasyEDA custom library paths. No SPI interfaces detected either.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001239: 108 PCB footprints vs 50 schematic components — large discrepancy not flagged; GPIO castellated pads generate false edge_clearance_warnings at -1.03mm; DFM advanced tier correctly identified with t...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: RP2350 Dev Board.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The 4-layer board uses 0.1mm-class track spacing, correctly flagged as requiring advanced process (tier='advanced'). Single DFM violation for track_spacing=0.1011mm vs 0.127mm standard limit is accurate. VREG_LX switching node appears in power_net_routing, which is slightly odd but not harmful.

### Incorrect
- The PCB has 108 footprints while the schematic has 50 components. This 2x discrepancy is not flagged anywhere in the analysis. Many of the extra PCB footprints are test pads (GPIO0–GPIO47 castellated pads used as breakout points) that are valid, but the analyzer has no cross-reference check between schematic and PCB BOM counts.
  (signal_analysis)
- GPIO0 through GPIO47 are castellated half-holes on the board edge (intentional edge-mount pads). The placement_analysis reports all of them as edge_clearance_warnings with -1.03mm. These are intentional and not errors. The analyzer cannot distinguish castellated pads from misplaced components.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
