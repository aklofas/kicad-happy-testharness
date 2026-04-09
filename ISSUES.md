# Issue Tracker

Tracker for kicad-happy analyzer bugs (KH-*) and test harness improvements (TH-*).
Contains enough detail to resume work with zero conversation history.

> **Protocol**: When fixing issues, remove them from this file and add to FIXED.md in the
> same session. See README.md "Issue tracking protocol" for full details. Closed issues
> with root cause and verification details are in [FIXED.md](FIXED.md).

Last updated: 2026-04-09

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new number,
check both ISSUES.md (open) and FIXED.md (closed) for the current maximum. Next KH
number: **KH-218**. Next TH number: **TH-009**.

> 11 open issues from Layer 3 batch reviews (2026-04-09).

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-207 — Mirrored component pin-to-net mapping wrong in KiCad 5 legacy (HIGH)

**Symptom:** Components placed with mirrored transforms (e.g., -1 X scale) have their
pin-to-net assignments scrambled. GND pins get mapped to signal nets and vice versa.
Affects all mirrored ICs, connectors, and multi-pin components in KiCad 5 `.sch` files.

**Root cause:** The legacy `.sch` parser uses coordinate-based wire-to-pin matching but
does not apply the component's transform matrix before resolving pin positions. When a
component is mirrored, pin coordinates are flipped but the matcher uses unflipped positions.

**Impact:** Propagates into ERC warnings, net classification, power domain analysis,
bus analysis, and signal detectors. Any downstream analysis referencing pin-net assignments
on mirrored components will be wrong.

**File:** `skills/kicad/scripts/analyze_schematic.py`, legacy `.sch` pin-to-net resolution.

**Repro:** `koron/yuiop` — `yuiop60pi/main2/main2.sch` — U1 (PGA2040) placed with
mirror (-1, 0, 0, -1). Pins 11/12 (GND) mapped to COL4/COL5, GPIO pins mapped to GND.
Also affects J1 (USB_B_Micro) and J2 (USB_MON) pin assignments in same file.

**Discovered:** 2026-04-08 via Layer 3 subagent review.

### KH-208 — Component type classification ignores lib_id, over-relies on ref prefix (HIGH)

**Symptom:** Components with non-standard reference prefixes get systematically
misclassified. Examples from corpus reviews:
- `T1`/`T2` (DS18B20, lib_id `Sensor_Temperature:DS18B20`) → transformer (T prefix)
- `CB1`-`CB6` (circuit breakers, lib_id `Device:CircuitBreaker`) → capacitor (C prefix)
- `COMPR` (AC motor, lib_id `Motor:Motor_AC`) → capacitor (C prefix)
- `VR1` (potentiometer, lib_id `Potentiometer_Bourns:3296W`) → varistor (VR prefix)
- `TR7` (MOSFET, lib_id `DuetWifi:BSH105`) → transformer (custom lib)
- `LED1_W+` (connector, lib_id `Connector:Conn_01x01_Pin`) → LED (LED prefix)

**Root cause:** The type classifier prioritizes reference prefix over lib_id. When lib_id
contains unambiguous type info (`Connector:*`, `Sensor_Temperature:*`, `Motor:*`,
`Device:CircuitBreaker`), it should override the prefix heuristic.

**Impact:** Corrupts component_types counts, triggers false ESD audit entries, and
prevents downstream detectors from finding components of the correct type.

**File:** `skills/kicad/scripts/analyze_schematic.py`, component type classification.

**Repro:** `borzeman/PzbElectronics`, `Duet3D/Duet-2-Hardware`, `GoodEarthWeather/myKicadProjects`

**Discovered:** 2026-04-09 via Layer 3 batch review (8 repos, 4 affected).

---

### KH-209 — Power rails with voltage-pattern names classified as signal (MEDIUM)

**Symptom:** Nets named `12V0`, `3V3`, `5V0`, `1V5`, `1V8`, `6v`, `Neg6v`, `VDD5`,
`VDD12`, `5V_INT` etc. are classified as `signal` or `interrupt` in net_classification
instead of `power`. These are clearly power rails feeding multiple ICs.

**Root cause:** Net classification uses label type (power symbol vs global label) rather
than also checking if the net name matches common voltage patterns.

**File:** `skills/kicad/scripts/analyze_schematic.py`, net classification.

**Repro:** `azonenberg/starshipraider` (12V0, 3V3, 5V0 etc.), `Duet3D/Duet-2-Hardware`
(5V_INT as 'interrupt'), `GoodEarthWeather/myKicadProjects` (VDD12/VDD5/VDD3.3 missing),
`jonathan-tooley/903` (6v/Neg6v as signal).

**Discovered:** 2026-04-09 via Layer 3 batch review (4 repos affected).

---

### KH-210 — SPI chip select detection too narrow (MEDIUM)

**Symptom:** SPI protocol compliance reports 0 CS lines when chip selects use non-standard
naming: `_EN` suffix (TMC2660), `CSN` pin name (AW20216S), `Lx_CS` pattern.

**Root cause:** CS detection only matches `_CS` / `_SS` naming patterns. Does not check
IC pin names like `~{CS}` or `CSN`, or `_EN` nets connected to SPI peripheral CS pins.

**File:** `skills/kicad/scripts/analyze_schematic.py`, SPI protocol compliance.

**Repro:** `Duet3D/Duet-2-Hardware` (TMC2660 _EN pins), `itsmevjnk/MelbourneTrainTracker`
(AW20216S CSN/Lx_CS).

**Discovered:** 2026-04-09 via Layer 3 batch review (2 repos).

---

### KH-211 — Addressable LED chain fragmentation across hierarchical sheets (MEDIUM)

**Symptom:** WS2812/SK6812 LED chains spanning hierarchical sub-sheets are fragmented into
many single-LED "chains" instead of one continuous chain. Chain tracing fails to follow
DOUT→DIN connections across sheet boundaries.

**Root cause:** LED chain tracer does not resolve hierarchical pin connections when tracing
DOUT to DIN between consecutive LEDs in different sheets.

**File:** `skills/kicad/scripts/analyze_schematic.py`, addressable LED chain detection.

**Repro:** `koron/yuiop` (56 WS2812 → 55+ fragments), `itsmevjnk/MelbourneTrainTracker`
(chain detection issues).

**Discovered:** 2026-04-09 via Layer 3 batch review (2 repos).

---

### KH-212 — Bare capacitor values parsed as Farads instead of microfarads (MEDIUM)

**Symptom:** Capacitors with unitless value `0.1` in 0603/0805 packages are parsed as
0.1 Farads (100,000 µF) instead of 0.1 µF (100 nF). This causes absurd RC filter
calculations (0 Hz cutoff) and wildly inflated decoupling totals (100,047 µF).

**Root cause:** Value parser treats bare numeric values without units as base SI units
(Farads). In practice, unitless cap values in small SMD packages are always µF.

**File:** `skills/kicad/scripts/analyze_schematic.py`, capacitor value parsing.

**Repro:** `eddyem/stm32samples` — 12 caps with value `0.1` in 0603 packages.

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

### KH-213 — P-MOSFET channel detection ignores lib description/keywords (LOW)

**Symptom:** IRF9310 classified as N-channel MOSFET despite lib_symbol description
saying `P-MOSFET transistor` and keywords containing `PMOS P-MOS P-MOSFET`.

**Root cause:** Channel type detection only checks lib_id pattern, not description or
keywords fields from the component's library symbol definition.

**File:** `skills/kicad/scripts/analyze_schematic.py`, MOSFET classification.

**Repro:** `eddyem/stm32samples` — Q2 IRF9310.

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

### KH-214 — INA2xx power monitors misclassified as opamp circuits (LOW)

**Symptom:** INA233/INA226/INA230 power/current monitor ICs appear in opamp_circuits as
`comparator_or_open_loop`. These are digital I2C power monitors with differential current
sense inputs, not opamps.

**Root cause:** The opamp detector matches any IC with differential-looking inputs without
checking if it's a known power monitor family.

**File:** `skills/kicad/scripts/analyze_schematic.py`, opamp circuit detection.

**Repro:** `azonenberg/starshipraider` (24 INA233 entries), `Sierra-Lobo/mainboard-hardware`
(5 INA230).

**Discovered:** 2026-04-09 via Layer 3 batch review (2 repos).

---

### KH-215 — LM2576/LM2596 switching bucks classified as LDO (LOW)

**Symptom:** LM2576-5.0 classified with topology `LDO` despite being a well-known switching
buck regulator with external inductor and freewheeling diode.

**Root cause:** Regulator topology detection defaults to LDO when it can't find a direct
inductor connection on a known switch pin. The LM2576 uses a different pin naming convention
than modern integrated FET bucks.

**File:** `skills/kicad/scripts/analyze_schematic.py`, regulator topology detection.

**Repro:** `eddyem/stm32samples` — U5 LM2576-5.0 with L1 and D27.

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

### KH-216 — Multi-unit IC pin_nets shows wrong unit's pins (LOW)

**Symptom:** For multi-unit components (e.g., 6x LS_Gen ICs with 2 units each), unit 1's
component entry shows pin_nets from unit 2 (power pins 21/22/23) instead of unit 1's
signal pins (1-6, 11-13).

**Root cause:** Pin_nets merging across units assigns all discovered pin connections to
each unit entry rather than filtering by pin membership per unit.

**File:** `skills/kicad/scripts/analyze_schematic.py`, multi-unit component handling.

**Repro:** `jonathan-tooley/903` — U1-U6 (LS_Gen) unit 1 instances all show unit 2 pins.

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

### KH-217 — Crystal frequency parsing is case-sensitive (LOW)

**Symptom:** Crystal with value `32.768kHZ` has frequency parsed as null. The capital `HZ`
is not recognized. `16MHz` with standard casing parses correctly.

**Root cause:** Frequency unit suffix matching is case-sensitive (`MHz` matches but `kHZ`
does not).

**File:** `skills/kicad/scripts/analyze_schematic.py`, crystal frequency parsing.

**Repro:** `hsetlik/PolySynth` — Y402 `32.768kHZ`.

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

## Deferred

### KH-205 — D+ net lost in KiCad 5 legacy net resolution (MEDIUM)

**Status:** Unreproducible — referenced file `Mouse/Mouse.sch` not found in repo
`prashantbhandary/Meshmerize-MicroMouse-`. No `.sch` files exist in the checked-out
repo (all converted to `.kicad_sch`). Reopen if repro file is located.

**Discovered:** 2026-04-08 via v1.2 pre-release assertion suite.

---

## Priority Queue (open issues, ordered by impact)

1. KH-208 — Component type classification ignores lib_id (HIGH)
2. KH-207 — Mirrored component pin-to-net mapping wrong in KiCad 5 (HIGH)
3. KH-209 — Power rails with voltage-pattern names classified as signal (MEDIUM)
4. KH-210 — SPI chip select detection too narrow (MEDIUM)
5. KH-211 — LED chain fragmentation across hierarchical sheets (MEDIUM)
6. KH-212 — Bare capacitor values parsed as Farads (MEDIUM)
7. KH-214 — INA2xx power monitors as opamp circuits (LOW)
8. KH-215 — LM2576/LM2596 switching bucks as LDO (LOW)
9. KH-213 — P-MOSFET channel detection ignores description/keywords (LOW)
10. KH-216 — Multi-unit IC pin_nets shows wrong unit's pins (LOW)
11. KH-217 — Crystal frequency parsing case-sensitive (LOW)
