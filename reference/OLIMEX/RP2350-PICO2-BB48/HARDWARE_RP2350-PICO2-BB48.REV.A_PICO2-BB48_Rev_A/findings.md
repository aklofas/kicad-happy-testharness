# Findings: OLIMEX/RP2350-PICO2-BB48 / HARDWARE_RP2350-PICO2-BB48.REV.A_PICO2-BB48_Rev_A

## FND-00001235: All three memory ICs (U1 W25Q16, U4 W25Q128, U5 APS6404L) missed by memory_interfaces detector; 4 pwr_flag_warnings fired despite 8 PWR_FLAG symbols present in the design; Crystal Q1 (12MHz ABM8), ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PICO2-BB48_Rev_A.kicad_sch
- **Created**: 2026-03-24

### Correct
- Crystal frequency parsed as 12MHz from value string, load caps C20/C21 at 27pF with CL_eff=16.5pF noted. Power sequencing found TPS62A02 with EN pin on 3V3_EN net with pull-up. USB-C CC1/CC2 pulldowns correctly pass. Voltage derating checked 19 caps with no issues.

### Incorrect
- All three memory chips use lib_id 'OLIMEX_IC:W25Q16BV' — a custom library that doesn't contain standard 'Memory_Flash' or 'Memory_PSRAM' path substrings. The analyzer fails to detect them as memory interfaces. Zero memory interfaces and zero SPI interfaces reported despite a 3-flash/PSRAM design connected to RP2350B.
  (signal_analysis)
- The schematic contains 8 PWR_FLAG power symbols but they are all on a separate 'PWR_FLAG' net (listed as its own entry in power_rails). The analyzer correctly fires warnings for VBUS, +3.3V, VSYS, and GND because those specific nets have no power_out driver. However, in KiCad's ERC, PWR_FLAG placed adjacent to a net junction resolves ERC for that net — the analyzer may or may not be correct depending on exact wiring. The GND warning is suspicious since GND always has return drivers.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001236: 4-layer 18.3x69mm board, RP2350B heatsink pad via adequacy correctly assessed as 'good' (8 vias); USB-C1 edge clearance -1.0mm reported as warning — false positive for intentional edge-mount connector

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PICO2-BB48_Rev_A.kicad_pcb
- **Created**: 2026-03-24

### Correct
- RP2350B U3 thermal pad shows 8 vias (good adequacy). MICRO_SD1 mechanical pad correctly flagged as having 0-1 vias (none/insufficient). 85 footprints matches gerber count. USB-C1 negative edge clearance (-1.0mm) is a false positive — this is an edge-mount USB-C connector intentionally overlapping the board edge.

### Incorrect
- USB-C1 is an edge-mount USB-C connector deliberately placed at the board edge with negative clearance. The PCB placement_analysis reports this as an edge_clearance_warning with -1.0mm. The analyzer has no way to distinguish intentional edge-mount from a real placement error, so this produces a false positive that cannot be suppressed.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001237: 4-layer gerber set complete, aligned, correct drill classification with X2 attributes; drill_tools merges NPTH and PTH 0.6mm holes, reporting 26 total with type NPTH

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerbers
- **Created**: 2026-03-24

### Correct
- All 11 gerber layers present (F.Cu, B.Cu, In1.Cu, In2.Cu, masks, paste, silks, Edge.Cuts). No missing required or recommended layers. 126 vias + 64 component holes correctly separated by X2 aperture function. Min trace 0.127mm consistent with PCB output. Board dimensions 18.3x69mm consistent across all three analyzers.

### Incorrect
- The drill_tools summary shows 0.6mm with count=26 and type=NPTH, but the drills section shows 2 NPTH holes (0.6mm) and 4 PTH holes (0.6mm) separately — total 6, not 26. The 26 count appears to conflate the 0.6mm ViaDrill (count=20 in PTH file) + 4 ComponentDrill + 2 NPTH into a merged entry. The drill_tools summary key-conflicts on same diameter across files.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
