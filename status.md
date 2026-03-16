# Testing Status

Log of batch testing history and current state of testing across the corpus.
Use this file to record completed batches, corpus maintenance (purges, additions),
and aggregate metrics. Do not track individual issues here — use
[ISSUES.md](ISSUES.md) for open bugs and [FIXED.md](FIXED.md) for closed ones.

Last updated: 2026-03-16

---

## Corpus summary

| Metric | Count |
|--------|------:|
| Total repos in repos.md | 1,052 |
| Checked out in repos/ | 1,044 |
| Repos with baselines | 1,035 |
| Repos with assertions | 952 |
| Total assertion files | 7,026 |
| Total assertions | 63,876 |
| Assertion pass rate | 100.0% |
| Layer 3 reviewed | 60+ |

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
