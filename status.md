# Testing Status

Log of batch testing history and current state of testing across the corpus.
Use this file to record completed batches, corpus maintenance (purges, additions),
and aggregate metrics. Do not track individual issues here — use
[ISSUES.md](ISSUES.md) for open bugs and [FIXED.md](FIXED.md) for closed ones.

Last updated: 2026-03-22

---

## Corpus summary

| Metric | Count |
|--------|------:|
| Total repos in repos.md | 1,052 |
| Checked out in repos/ | 1,044 |
| Repos with baselines | 1,035 |
| Repos with assertions | 1,035 |
| Total assertion files | 18,060 |
| SEED assertions (schematic) | 64,089 |
| SEED assertions (PCB) | 42,947 |
| SEED assertions (gerber) | 8,965 |
| STRUCT assertions (schematic) | 45,833 |
| STRUCT assertions (PCB) | 40,831 |
| FND assertions (required) | 443 |
| FND assertions (aspirational) | 211 |
| BUGFIX assertions | 67 |
| **Total assertions** | **203,179** |
| Assertion pass rate | 100.0% |
| Bugfix registry entries | 58 |
| Layer 3 reviewed repos | 155 |
| Total findings | 295 |
| Open KH-* issues | 9 (3 MEDIUM, 6 LOW) |
| Closed KH-* issues | 177 |

---

## Completed batches

### Batch 1 — Well-known hardware projects (10 repos)

All tested with reference data, assertions, and/or findings:
hackrf, splitflap, ubertooth, bitaxe, moteus, Voron-Hardware, OnBoard,
HadesFCS, icebreaker, OtterCastAudioV2

### Batch 2 — High-quality designs (6 of 10 tested)

Tested: ESP32-POE, OSHW-reCamera-Series, tomu-hardware, Otter-Iron-PRO,
greatfet-hardware, analog-toolkit

Not yet tested: acorn-robot-electronics

### Batch 3 — Broad corpus (96 repos, 2026-03-15)

96 repos from `0x42` through `Capitulo118` processed with Layer 1-3 testing.
2,449 assertions seeded, 0 errors.

### Batch 4 — Priority top 50 (2026-03-15)

50 repos from priority.md top 50 processed with Layer 1-2 testing:
tb303_vcf_kicad_project_gerbers, modular-psu, KiDiff, slab-pcb,
NUS-CPU-03-Nintendo-64-Motherboard, Duplicanator-Scart-Duplicator,
SparkFun_XRP_Controller, hw_projects, commodorelcd, Neo6502pc,
Castor_and_Pollux, ESP32-SBC-FabGL, KICAD, OtterCam-s3,
ESP32-S3-DevKit-LiPo, keyboard, PCB-Design, iMX8MP-SOM-EVB,
Cosmos-Keyboard-PCBs, SparkFun_IoT_RedBoard-RP2350, kuro65,
TPA3255_ClassD_PBTL, explorer, LAEMP-Prism, HandAssemble_Pmod,
pcb, Sichergo, kicad, geiger-counter, PCB-Modular-Multi-Protocol-Hub,
bms-c1, ms60, Gas-sens_Rs-485, Ventilator, STAN, DATALOGGER02,
KevinbotV3-KiCAD, DIN_41612_Backplane, ESP32-PRO, dib-mio-afe3,
FunBox, robocup-pcb, SparkFun_IoT_Node_LoRaWAN, fidget,
Mechanical-Keyboard-PCBs, RISCBoy, SparkFun_GNSS_Flex_Breakout,
psylink, DIY-LAPTOP, + 15 more SparkFun/misc repos.
Layer 3 reviews in progress on 19 repos (27 files).

### Batch 5 — Priority top 19 completion (2026-03-16)

19 repos from priority top 20 (excluding KiCadLogicalSchemeSimulator —
simulation test fixtures, not hardware) confirmed with Layer 1-3 testing.
Re-ran analyzers to check for improvements from recent KH-* fixes: 0 baseline
changes detected. Filled assertion gaps for 6 repos with incomplete Layer 2
(KiDiff, SparkFun_XRP_Controller, Castor_and_Pollux, KICAD, ESP32-S3-DevKit-LiPo,
Cosmos-Keyboard-PCBs). All 19 moved to "Tested" in priority.md.

### Batch 14 — Complete priority queue verified (2026-03-16)

All 603 remaining repos from priority.md's "To test" queue verified at once.
599 valid repos confirmed with Layer 1-2 testing (all had baselines and
assertions from earlier batches). 4 purged repos removed (Kicad-Design-Library,
kicad-blocks, designGuardDesktopApp, kicad_schemes). Total: 16,934 assertions
checked across 695 repos (96+48+599+52 from earlier batches), all at 100% pass.
Priority queue is now empty — all 1,035 repos with baselines have been tested.

### Batch 15 — Layer 3 signal-rich batch (20 repos, 2026-03-16)

20 repos selected by weighted signal richness for Layer 3 LLM review.
38 findings added (FND-00000255 through FND-00000292). Key recurring issues:
RC filter false positives from opamp feedback, JFET typed as mosfet,
LED driver false positives, duplicate design_observations per multi-unit IC,
integrator misclassified as compensator, RF matching false positives on
non-RF circuits, VC-prefix trimmer cap as varistor, solar cell array as
key matrix, unitless pF values parsed as Farads.

Repos: Modular-Synth-Hardware, eurorack-kicad, eurorack-pmod, QFHMIX01,
zx-sizif-512, 3458A-A3-66533-2021-KS-RoHS-SMD-KiCad, 3458A-A3-Schematic-KiCad,
moco, acorn-robot-electronics, KiwiSDR_PCB, Neptune, tokay-lite-pcb,
Amiga-2000-EATX, cubesat-boards, coco_motherboards, su-pcb,
FHNW-Pro4E-FS19T8-3DPrinterBoard-STM32, Zynq-SoM, dib-mio168, PolyKybd.

### Batch 16 — Full corpus regression after Batch 14 fixes (2026-03-17)

Full corpus re-run of schematic analyzer (6,827 schematics) after fixing all
13 KH-141 through KH-153 bugs in kicad-happy. 6,827/6,827 pass, 0 failures.
3,359 baselines refreshed. Assertions reseeded for 127 repos that had stale
expectations from pre-fix output (rf_matching, rc_filter, opamp, key_matrix
counts changed; net counts changed from improved legacy lib resolution).
Final: 64,066 assertions at 100.0% pass rate.

Drift check before regression: 64 possibly_fixed, 90 now_detected findings
(improvements from fixes), 41 stale-path regressions (non-existent output
keys, not real issues), 102 no_output.

### Batch 17 — PCB Layer 2-3 bootstrap (2026-03-17)

PCB assertion seeding: 42,879 SEED-* assertions generated across 2,941 PCB files
using `seed.py --all --type pcb`. PCB review packet support added to `packet.py`.

First PCB Layer 3 reviews: 5 repos reviewed (hackrf, moteus, ESP32-P4-PC,
Neo6502pc, RP2350pc). 5 PCB findings filed (FND-00000293 through FND-00000297).
6 new KH-* issues discovered (KH-154 through KH-159), all in analyze_pcb.py:
copper_layers_used includes non-copper layers, misses zone-only layers,
paste-only stencil pads as thermal pads, connector pads as thermal pads,
thermal via adequacy ignores drill size, zone stitching per-polygon areas.

### Batch 18 — PCB fixes KH-154–KH-159 and full re-seed (2026-03-17)

All 6 PCB issues fixed in analyze_pcb.py. Full corpus re-run: 3,491/3,493 pass
(2 pre-existing parse failures). PCB assertions re-seeded: 42,786 at 100%.
Gerber assertions verified: 9,088 at 100%. Total: 115,940 assertions at 100%.

Key fixes: copper layer filter changed from type-based to name-based ("Cu" in name),
paste-only/no-net pads excluded from thermal detection, drill-weighted via adequacy,
per-net zone stitching aggregation. 0 open KH-* issues remain.

### Batch 19 — 5 MEDIUM fixes + re-seed (KH-160, KH-163–165, KH-174) (2026-03-17)

5 MEDIUM issues fixed across analyze_schematic.py (1) and analyze_pcb.py (4):
- KH-160: Removed over-aggressive PWR_FLAG name-based skip for connector-powered designs
- KH-164: Broadened IC regex `^U\d` → `^(U|IC)\d` in decoupling analysis
- KH-165: Lowered thermal pad thresholds + area-ratio EP detection for small DFN/QFN
- KH-163: Expanded thermal pad via containment margin from 1.1x to 1.5x
- KH-174: Added raw_adequacy field and small_via_note for small-drill thermal vias

Full corpus re-run and re-seed. 5 aspirational assertions promoted to required.
PCB structural assertions bootstrapped: 40,831 STRUCT-* assertions across 2,178 files.
Bugfix registry expanded from 29 to 58 entries (67 assertions).
Total: 203,300 assertions at 100% pass rate.

### Batch 20 — Documentation refresh (2026-03-17)

Updated CLAUDE.md, status.md, and memory files to reflect current state (203K assertions,
18K assertion files, 155 reviewed repos, 287 findings, 58 bugfix entries, 5 LOW issues).

### Batch 21 — First Gerber Layer 3 reviews (2026-03-17)

5 repos reviewed for gerber analysis quality: bitaxe, HadesFCS (4 boards), glasgow
(6 revisions), modular-psu (16 gerber sets), SparkFun_XRP_Controller (beta + production).
8 gerber findings filed (FND-00000298 through FND-00000305). 10 new KH-* issues discovered
(KH-177 through KH-186), all in analyze_gerbers.py:

- 6 HIGH: smd_apertures always zero, .TXT drill not recognized, .G2L/.G3L inner layers
  not discovered, inch-to-mm unit conversion, GKO misclassification from X2 conflict,
  %TD*% attribute clearing incomplete
- 3 MEDIUM: drill extent units, combined drill has_pth/npth, front/back component counts
- 1 LOW: large NPTH mounting hole misclassification

Key theme: analyzer works well for modern KiCad X2 gerbers but has significant gaps with
Eagle/Protel format gerbers and X2 attribute edge cases.

### Batch 22 — 6 HIGH gerber fixes (KH-177–KH-182) (2026-03-22)

All 6 HIGH gerber issues fixed in analyze_gerbers.py:
- KH-177: Paste layer flash fallback for smd_apertures when no X2 data
- KH-178: .TXT drill file discovery with M48 header validation
- KH-179: .G2L/.G3L inner layer glob + regex fix
- KH-180: Inch-to-mm conversion for Edge.Cuts board dimensions
- KH-181: .gko filename override when X2 FileFunction says copper
- KH-182: %TD*% clears current_component and current_net per X2 spec

Full corpus re-run: 1048/1048 pass. Gerber assertions re-seeded: 8,965 SEED-*.
Total: 203,179 assertions at 100% pass rate. 9 open issues remain (3 MEDIUM, 6 LOW).

---

## Purge log

### 2026-03-15 — Removed 87 repos

Repos removed from repos.md and all local data after audit:

- **18 Eagle-only** — Adafruit, SparkFun, and others in Eagle XML format
  misidentified as KiCad (discover.py filters these via header check)
- **14 Tools/libraries** — KiCad parsers, generators, plugins with example
  PCBs but no real designs (CopperForge, KiParse, PcbDraw, etc.)
- **22 PCB-only** — Repos with `.kicad_pcb` but no schematics
  (keyboard plates, templates, footprint-only repos)
- **33 Tiny** — Schematics with <3 components (templates, art pieces,
  rulers, test patterns)
