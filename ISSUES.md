# Issue Tracker

Tracker for kicad-happy analyzer bugs (KH-*) and test harness improvements (TH-*).
Contains enough detail to resume work with zero conversation history.

Last updated: 2026-03-13 (fixed KH-015, KH-041-046, TH-007)

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new number,
check both ISSUES.md (open) and FIXED.md (closed) for the current maximum. Next KH
number: **KH-047**. Next TH number: **TH-008**.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-012: Voltage divider false positives [OPEN]

- **Severity**: MEDIUM
- **Status**: OPEN
- **Component**: `skills/kicad/scripts/signal_detectors.py` line 86, `detect_voltage_dividers()`
- **Description**: Voltage dividers are detected on resistor pairs that share a node but
  aren't actually dividers. The topology check requires: two resistors sharing a mid-point
  net, one end at power, other at ground. But this catches pull-up/pull-down pairs and
  termination networks that happen to fit the pattern.
- **Evidence**: Multiple repos show voltage dividers on non-divider resistor pairs. Specific
  examples from Layer 3 reviews include feedback resistors on opamp circuits being double-
  counted as both feedback networks and voltage dividers.
- **Proposed fix**: Multiple complementary approaches:
  1. Skip pairs where the mid-point net has many connections (>6) — real divider outputs
     connect to 2 resistors + maybe 1-2 IC inputs.
  2. Skip if ratio is extreme (>50:1 or <1:50) — not useful dividers.
  3. The existing `postfilter_vd_and_dedup()` already removes VDs on transistor gate/base
     nets — could extend to also remove VDs where mid-point connects to opamp inverting
     input (these are feedback networks, not dividers).
- **Code location**: Lines 86-200 and 1486-1530 of signal_detectors.py
- **Related findings**: FND-00000007, FND-00000012

---

### KH-013: PWR_FLAG false warnings per sheet [OPEN]

- **Severity**: LOW
- **Status**: OPEN
- **Component**: `skills/kicad/scripts/analyze_schematic.py` line 2883, `audit_pwr_flags()`
- **Description**: The PWR_FLAG audit generates "power pin not driven" warnings on power
  nets that span multiple sheets but only have PWR_FLAG on one sheet. The audit correctly
  identifies missing PWR_FLAG but produces noise for designs where the user intentionally
  placed PWR_FLAG on only the main sheet.
- **Evidence**: Multiple repos with hierarchical designs have PWR_FLAG warnings on sub-sheet
  power rails.
- **Proposed fix**: Either (a) make PWR_FLAG audit cross-sheet aware (check if any sheet
  in the hierarchy has PWR_FLAG for that net), or (b) downgrade from warning to informational
  note with severity level. The audit function already excludes nets with PWR_FLAG
  (lines 2892-2903) but only checks PWR_FLAG placement within the current analysis scope.
- **Code location**: Line 2883-2925 of analyze_schematic.py
- **Related findings**: FND-00000006

---

### KH-016: Legacy wire-to-pin coordinate matching broken [OPEN]

- **Severity**: HIGH
- **Status**: OPEN
- **Component**: `skills/kicad/scripts/analyze_schematic.py`, `build_net_map()` legacy path
- **Description**: Legacy schematic wire-to-pin connectivity relies on coordinate matching
  (wire endpoints must be within COORD_EPSILON of pin absolute positions). In the daisho
  repo, only 4 out of 160 nets have more than one pin — meaning almost no wire-to-pin
  connections are being established. Root cause is likely coordinate precision issues:
  legacy .sch files use mils (1/1000 inch) while the parser may have rounding or
  transformation errors that push pin positions slightly off from wire endpoints.
- **Evidence**: daisho main_board.sch: 160 nets but only 4 have multi-pin connections.
  Most nets are single-pin orphans. This makes all signal detectors useless on legacy
  files even after KH-015 is fixed — detectors need multi-pin nets to find circuits.
- **Proposed fix**: (a) Increase COORD_EPSILON for legacy files (mils have lower precision
  than mm), or (b) audit the coordinate transform pipeline for legacy symbol placement
  (mirror, rotation, offset) to find where precision is lost, or (c) use a different
  connectivity approach for legacy (label-based matching like KiCad does internally).
- **Code location**: `build_net_map()` in analyze_schematic.py, `COORD_EPSILON` in kicad_utils.py
- **Related findings**: FND-00000016 (daisho)

---

### KH-017: Opamp inverting classifier doesn't verify feedback path [OPEN]

- **Severity**: LOW
- **Status**: OPEN
- **Component**: `skills/kicad/scripts/signal_detectors.py`, `detect_opamp_circuits()`
- **Description**: The opamp circuit classifier identifies inverting configurations by
  checking if a resistor connects to the inverting input (IN-). However, it doesn't verify
  that the feedback resistor actually bridges the output to IN-. This can cause
  misclassification when a resistor on IN- is a bias/offset resistor rather than feedback.
- **Evidence**: Found during Layer 3 review of education_tools opamp experimenter board.
- **Proposed fix**: After finding a resistor on IN-, trace its other net. If the other net
  is the opamp output net, confirm it's an inverting feedback configuration. If the other
  net is a signal source, it's an input resistor (which is correct for inverting but the
  feedback path should also be verified).
- **Related findings**: FND-00000019

---

### KH-018: Differential pair detector matches power rails [OPEN]

- **Severity**: LOW
- **Status**: OPEN
- **Component**: `skills/kicad/scripts/signal_detectors.py`
- **Description**: The differential pair detector matches net name pairs like V+/V- and
  IN+/IN- on opamp circuits. These are not differential signal pairs — they are power
  supply rails (V+/V-) or opamp input designations. Real differential pairs are things
  like USB_D+/USB_D-, ETH_TX+/ETH_TX-.
- **Evidence**: Found during Layer 3 review of education_tools.
- **Proposed fix**: Exclude pairs where either net name matches known power rail patterns
  (V+, V-, VCC, VDD, VEE, VSS) or opamp input pin names (IN+, IN-, INP, INN).
- **Related findings**: FND-00000020
- **Additional evidence**: moteus SXX_P/SXX_N current sense Kelvin nets falsely matched as
  differential pair (they are single-ended analog sense lines for DRV8323 CSA inputs).

---

### KH-019: RC filter false pairs from shared-node components [OPEN]

- **Severity**: LOW
- **Status**: OPEN
- **Component**: `skills/kicad/scripts/signal_detectors.py` line 203, `detect_rc_filters()`
- **Description**: The RC filter detector matches any resistor-capacitor pair sharing a
  net. This creates false positives when components share a node but aren't actually
  forming a filter — e.g., a pull-up resistor and a bypass capacitor both connected to
  the same power rail (which is excluded), but also on signal nets with multiple
  components.
- **Evidence**: Found during Layer 3 reviews. Specific instances: bitaxe R4 (PGOOD pull-up)
  + C35/C44 (3V3 decoupling) detected as 7.96 Hz filter; icebreaker R3 (LDO enable delay)
  + C39 detected as filter instead of soft-start circuit.
- **Proposed fix**: Add a check that the R-C pair forms a meaningful filter topology:
  the resistor's other pin should be a signal source, and the capacitor's other pin
  should be ground. If the capacitor's other pin is another signal net, it's likely
  coupling/DC blocking, not filtering.
- **Related findings**: FND-00000021

---

### KH-020: Capacitive feedback not recognized [OPEN]

- **Severity**: LOW
- **Status**: OPEN
- **Component**: `skills/kicad/scripts/signal_detectors.py`, `detect_opamp_circuits()`
- **Description**: The opamp circuit detector only recognizes resistive feedback networks.
  Capacitive feedback (integrator/differentiator topologies) and mixed RC feedback
  (lead-lag compensators) are not detected.
- **Evidence**: Found during Layer 3 review of education_tools Wien bridge oscillator.
- **Proposed fix**: Extend feedback detection to check for capacitors and R-C combinations
  between opamp output and inverting input. Classify as integrator (C feedback only),
  differentiator (C input + R feedback), or compensator (R+C feedback).
- **Related findings**: FND-00000023

---

### KH-021: BSS138 level shifter topology not detected [OPEN]

- **Severity**: LOW
- **Status**: OPEN
- **Component**: `skills/kicad/scripts/signal_detectors.py`, `detect_transistor_circuits()`
- **Description**: BSS138-based bidirectional level shifters (common I2C level shifting
  circuit: NMOS with pull-ups on both sides) are not recognized as a distinct topology.
  They appear as generic MOSFET switches. The pattern: NMOS gate to low-voltage rail,
  source to low-side with pull-up, drain to high-side with pull-up.
- **Evidence**: Found during Layer 3 review of Glasgow hardware (io_buffer sheet uses
  multiple BSS138-style level shifters).
- **Proposed fix**: In `detect_transistor_circuits()`, after identifying a MOSFET, check
  if: (a) gate connects to a power rail, (b) both source and drain have pull-up resistors
  to different power rails. If so, classify as "level_shifter" topology.
- **Related findings**: FND-00000025

---

### KH-022: UART false positives on PCIe Rx/Tx net names [OPEN]

- **Severity**: LOW
- **Status**: OPEN
- **Component**: `skills/kicad/scripts/signal_detectors.py`
- **Description**: The bus protocol / UART detector matches net names containing "Rx" and
  "Tx" as UART signals. In OpenCAPI hardware, PCIe lane nets are named with Rx/Tx
  suffixes (e.g., "PCIE_Rx0", "PCIE_Tx0") and are falsely flagged as UART interfaces.
- **Evidence**: OpenCAPI hardware repo: PCIe lanes flagged as UART. moteus: OUTX motor
  phase output (27 pins on DRV8323) classified as UART. moteus: CAN_RX/CAN_TX categorized
  as UART in test_coverage despite correct CAN bus detection.
- **Proposed fix**: If the net name contains "PCIe", "PCIE", "PCI_E", or similar PCIe
  indicators, exclude from UART detection. More generally, UART detection should require
  both Rx and Tx on the same interface, not just any net with Rx/Tx in the name.
- **Related findings**: FND-00000024

---

### KH-024: #GND power symbols classified as components in legacy parser [OPEN]

- **Severity**: MEDIUM
- **Status**: OPEN
- **Component**: `skills/kicad/scripts/analyze_schematic.py`, legacy component extraction
- **Description**: In the legacy (.sch) parser, power symbols like #GND, #PWR, #+3V3 are
  supposed to be classified as `type: "power_symbol"` and excluded from the component
  list. However, some variants (particularly #GND with non-standard lib references) slip
  through and appear as regular components in the output, inflating component counts and
  creating noise in BOM data.
- **Evidence**: OpenVent-Bristol_KiCad: #GND symbols appear in component list.
- **Proposed fix**: In the legacy component extraction, check if the reference starts with
  "#" — if so, classify as power_symbol regardless of lib reference. KiCad 5 convention:
  all power symbols have references starting with "#".
- **Related findings**: FND-00000027

---

### KH-025: Crystals with X prefix classified as connectors [OPEN]

- **Severity**: LOW
- **Status**: OPEN
- **Component**: `skills/kicad/scripts/kicad_utils.py`, `classify_component()`
- **Description**: The component classifier maps reference prefix "X" to connector type.
  In some symbol libraries, crystals/oscillators use "X" prefix (e.g., X1, X2) instead
  of the more common "Y" prefix. These get classified as connectors instead of crystals.
- **Evidence**: daisho hardware: crystal X1 classified as connector.
- **Proposed fix**: In `classify_component()`, check the component value/lib_id for crystal
  keywords ("crystal", "oscillator", "xtal", "MHz", "kHz") before falling back to the
  reference-prefix classification. The value/lib_id check should take priority over prefix.
- **Related findings**: FND-00000028

---

### KH-026: Hierarchical net merging bug for multi-instance sub-sheets [OPEN]

- **Severity**: HIGH
- **Status**: OPEN
- **Component**: `skills/kicad/scripts/analyze_schematic.py`, `build_net_map()`
- **Description**: When a sub-sheet is instantiated multiple times (e.g., cynthion's
  `type_c.kicad_sch` used 3 times for 3 USB-C ports), hierarchical labels from different
  instances should have per-instance net namespacing. Currently, the net merger combines
  all instances' hierarchical labels into the same nets, causing false connectivity
  between electrically independent instances.
- **Evidence**: cynthion hardware: type_c.kicad_sch instantiated 3 times. All CC1/CC2
  nets from different ports merged into the same net, which is electrically wrong.
- **Proposed fix**: When resolving hierarchical labels, prefix the label name with the
  sheet instance path (or instance UUID) to create unique nets per instance. The parent
  sheet's pin stubs should map to the instance-specific label names. This requires
  tracking which instance of a sub-sheet is being processed during hierarchical
  traversal.
- **Code location**: `build_net_map()` hierarchical label handling, and the sheet
  traversal logic in the KiCad 6+ parser entry point.
- **Related findings**: FND-00000014 (cynthion)
- **Additional evidence**: moteus h_bridge.kicad_sch instantiated 3x for three-phase bridge.
  All three half-bridges show identical nets (OUTX, GHX, GLX, SPX_Q) instead of per-instance
  names. Makes three-phase bridge analysis incorrect — all phases appear electrically identical.

---

## Priority Queue (open issues, ordered by impact)

1. **KH-026** (HIGH) -- Hierarchical net merging for multi-instance sheets. Wrong connectivity.
2. **KH-016** (HIGH) -- Legacy wire-to-pin broken. 50% orphan nets in ubertooth, 32 spurious nets in throwing-star.
3. **KH-024** (MEDIUM) -- #GND as component in legacy parser.
4. **KH-012** (MEDIUM) -- Voltage divider FPs.
5. **KH-013** (LOW) -- PWR_FLAG warnings per-sheet scope.
6. **KH-017** (LOW) -- Opamp feedback verification.
7. **KH-018** (LOW) -- Diff pair on power rails and current sense nets.
8. **KH-019** (LOW) -- RC filter shared-node FPs.
9. **KH-020** (LOW) -- Capacitive feedback recognition.
10. **KH-021** (LOW) -- BSS138 level shifter detection.
11. **KH-022** (LOW) -- UART FP on PCIe Rx/Tx, CAN, motor outputs.
12. **KH-025** (LOW) -- Crystal X-prefix classification.
