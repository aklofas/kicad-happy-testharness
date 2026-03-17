# Testing Status

Log of batch testing history and current state of testing across the corpus.
Use this file to record completed batches, corpus maintenance (purges, additions),
and aggregate metrics. Do not track individual issues here — use
[ISSUES.md](ISSUES.md) for open bugs and [FIXED.md](FIXED.md) for closed ones.

Last updated: 2026-03-17

---

## Corpus summary

| Metric | Count |
|--------|------:|
| Total repos in repos.md | 1,052 |
| Checked out in repos/ | 1,044 |
| Repos with baselines | 1,035 |
| Repos with assertions | 1,035 |
| Total assertion files | ~10,000 |
| Total assertions (schematic) | 64,066 |
| Total assertions (PCB) | 42,879 |
| Total assertions | 106,945 |
| Assertion pass rate | 100.0% |
| Layer 3 reviewed (schematic) | 158 |
| Layer 3 reviewed (PCB) | 5 |
| Total findings | 324 |

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
