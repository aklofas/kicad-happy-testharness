# Issue Tracker

Tracker for kicad-happy analyzer bugs (KH-*) and test harness improvements (TH-*).
Contains enough detail to resume work with zero conversation history.

> **Protocol**: When fixing issues, remove them from this file and add to FIXED.md in the
> same session. See README.md "Issue tracking protocol" for full details. Closed issues
> with root cause and verification details are in [FIXED.md](FIXED.md).

Last updated: 2026-03-17

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new number,
check both ISSUES.md (open) and FIXED.md (closed) for the current maximum. Next KH
number: **KH-160**. Next TH number: **TH-008**.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-154: copper_layers_used includes non-copper layers (PCB analyzer) [HIGH]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: hackrf, Neo6502pc, RP2350pc

The `statistics.copper_layers_used` count includes non-copper layers like F.SilkS and F.Mask. hackrf-one reports 5 copper layers instead of 4; Neo6502pc includes F.SilkS; RP2350pc includes F.Mask.

**Root cause**: Layer enumeration does not filter to `*.Cu` pattern.
**Fix**: Filter `copper_layers_used` and `copper_layer_names` to only include layers matching `*.Cu` or the standard copper layer names (F.Cu, B.Cu, In*.Cu).
**Findings**: FND-00000293, FND-00000296, FND-00000297

---

### KH-155: copper_layers_used misses layers with only zone fills (PCB analyzer) [MEDIUM]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: moteus

The `copper_layers_used` count does not include copper layers that have zone fills but no track segments. moteus uses In1.Cu as a ground/power plane via zone fills only, but it is not counted in `copper_layers_used`.

**Root cause**: Layer counting only considers track segments, not zone fills.
**Fix**: Also count layers that have zone fills when computing `copper_layers_used`.
**Findings**: FND-00000294

---

### KH-156: Paste-only stencil aperture pads misidentified as thermal pads (PCB analyzer) [HIGH]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: ESP32-P4-PC, Neo6502pc

Pads that exist only on paste layers (solder paste stencil apertures with no copper pad) are misidentified as thermal pads. On ESP32-P4-PC, 15 of ~19 thermal_pad_vias entries are these false positives. Same pattern on Neo6502pc.

**Root cause**: Thermal pad detection does not check for copper layer presence on the pad.
**Fix**: Require the pad to have at least one copper layer (F.Cu or B.Cu) before considering it a thermal pad.
**Findings**: FND-00000295, FND-00000296

---

### KH-157: Connector structural/shield pads misidentified as thermal pads (PCB analyzer) [MEDIUM]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: ESP32-P4-PC, RP2350pc

Mechanical mounting pads and shield pads on USB/HDMI/SD connectors (typically with no net or a shield net) are misidentified as thermal pads. These serve structural or EMI shielding purposes, not thermal relief.

**Root cause**: Thermal pad detection does not distinguish between IC exposed pads and connector structural pads.
**Fix**: Filter out pads belonging to connector footprints (J* refs) or pads with no net assignment from thermal pad analysis.
**Findings**: FND-00000295, FND-00000297

---

### KH-158: Thermal via adequacy formula ignores drill size (PCB analyzer) [LOW]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: ESP32-P4-PC

The thermal via adequacy rating does not account for via drill diameter. A 1.0mm drill via conducts ~10x more heat than a 0.3mm drill via, but both receive the same adequacy score.

**Root cause**: Adequacy formula uses only via count and pad area, not individual via dimensions.
**Fix**: Weight thermal conductivity by drill diameter (or cross-sectional area) in adequacy calculation.
**Findings**: FND-00000295

---

### KH-159: Zone stitching via density uses per-polygon areas (PCB analyzer) [LOW]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: moteus, RP2350pc

Zone stitching via density calculation uses per-polygon zone areas rather than per-net totals, inflating the density number when a net has multiple zone polygons on a layer.

**Root cause**: Zone area summed per polygon, not aggregated per net before computing via density.
**Fix**: Aggregate zone area per net across all polygons before computing stitching via density.
**Findings**: FND-00000294, FND-00000297

---

## Priority Queue (open issues, ordered by impact)

1. **KH-154** [HIGH] -- copper_layers_used includes non-copper layers (3 repos)
2. **KH-156** [HIGH] -- paste-only pads as thermal pads (2 repos, many false positives)
3. **KH-155** [MEDIUM] -- copper_layers_used misses zone-only layers (1 repo)
4. **KH-157** [MEDIUM] -- connector pads as thermal pads (2 repos)
5. **KH-158** [LOW] -- thermal via adequacy ignores drill size
6. **KH-159** [LOW] -- zone stitching per-polygon areas
