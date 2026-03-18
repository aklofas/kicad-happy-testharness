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
number: **KH-177**. Next TH number: **TH-008**.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-166: False positive missing_revision silkscreen warning (PCB analyzer) [LOW]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: modular-psu

The `documentation_warnings` includes `missing_revision` with severity "warning", but the `board_metadata` section correctly shows `rev: "r3B7"` and the silkscreen text includes "EEZ DIB AUX PS (12/2021 r3B7)".

**Root cause**: The silkscreen warning check does not cross-reference against board_metadata or silkscreen text content.
**Fix**: Skip the `missing_revision` warning if `board_metadata.rev` is non-empty or if silkscreen text contains a revision pattern.

---

### KH-167: ESD/TVS protection devices included in decoupling analysis (PCB analyzer) [LOW]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: cnhardware (ch32v305-radioset)

RCLAMP0502N (U3), an ESD protection device, is classified as an IC needing decoupling. Protection/TVS devices do not need bypass capacitors.

**Root cause**: Decoupling analysis includes all U-prefix components without filtering ESD/TVS/protection devices.
**Fix**: Filter out known ESD/TVS families (RCLAMP, PRTR, PESD, USBLC, etc.) or components classified as protection devices from decoupling analysis.

---

### KH-173: SMD ratio uses incommensurate units (Gerber analyzer) [LOW]

**Analyzer**: analyze_gerbers.py
**Discovered**: 2026-03-17 (Gerber Layer 3 review)
**Affected repos**: bitaxe

`smd_apertures` counts unique SMDPad aperture definitions (shapes), while `tht_holes` counts actual hole instances. A board with 45 unique SMD pad shapes but 500 pad placements gets the same count as one with 45 placements. bitaxe reports 0.44 ratio which is misleadingly low for a BGA-based design.

**Root cause**: Lines ~866-893 count unique aperture definitions for SMD but instance counts for THT.
**Fix**: Count SMD pad flash instances (from the gerber flash command count per SMDPad aperture) instead of unique aperture definitions. Or clearly label the metric as `smd_aperture_types` vs `tht_hole_instances`.

---

### KH-175: Sleep current total overestimates by including conditional pull-up paths [LOW]

**Analyzer**: analyze_schematic.py
**Discovered**: 2026-03-17 (external testing)

The `total_estimated_sleep_uA` sums all current paths including pull-up resistors at worst-case I=V/R (assuming signal driven low). Pull-ups where both ends are at the same potential during sleep draw zero current. Per-path notes already say "worst-case (signal driven low)" but the headline total doesn't distinguish always-on vs conditional paths. Reported 371µA vs actual ~35-46µA (10× overestimate).

**Root cause**: Lines ~4895-4896 sum all paths equally. Pull-up paths (lines ~4755-4775) are conditional on signal state but contribute to the total as if always-on.
**Fix**: Split the total into `always_on_uA` (dividers, LEDs, regulator Iq) and `conditional_uA` (pull-ups). Report both and use always-on as the headline figure.

---

### KH-176: DFM fab house capability thresholds not canonicalized [LOW]

**Analyzer**: report generation (references/report-generation.md)
**Discovered**: 2026-03-17 (external testing)

Different report runs cite different JLCPCB standard tier thresholds (e.g., min trace 0.127mm in one report, 0.09mm in another). `standards-compliance.md` has IPC-2221A values and the JLCPCB skill has fab-specific capabilities, but `report-generation.md` doesn't link to a canonical fab capability table.

**Root cause**: No single authoritative table of JLCPCB/PCBWay tier capabilities in the reference files. LLM report author fills in from training data, which varies.
**Fix**: Add a canonical fab house capability table (JLCPCB standard/advanced, PCBWay standard) to `standards-compliance.md` or `report-generation.md` so the LLM cites consistent thresholds.

---

## Priority Queue (open issues, ordered by impact)

1. **KH-166** [LOW] -- false positive missing_revision warning (PCB)
2. **KH-167** [LOW] -- ESD/TVS in decoupling analysis (PCB)
3. **KH-173** [LOW] -- SMD ratio incommensurate units (Gerber)
4. **KH-175** [LOW] -- sleep current total includes conditional paths (Schematic)
5. **KH-176** [LOW] -- DFM thresholds not canonicalized (Report)
