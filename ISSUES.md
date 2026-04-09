# Issue Tracker

Tracker for kicad-happy analyzer bugs (KH-*) and test harness improvements (TH-*).
Contains enough detail to resume work with zero conversation history.

> **Protocol**: When fixing issues, remove them from this file and add to FIXED.md in the
> same session. See README.md "Issue tracking protocol" for full details. Closed issues
> with root cause and verification details are in [FIXED.md](FIXED.md).

> **Reporting guidelines for Level 3 subagents**: Root cause descriptions must cite
> specific function names and line numbers, not just file names. When claiming code
> "doesn't check X", trace the actual code path for the repro input and show which line
> returns the wrong result — don't infer from the symptom what the code must be doing.
> Common pitfalls:
> - Code checks the right field but matches the wrong strings (KH-213: checked keywords
>   for `p-channel` but actual keywords contain `PMOS`)
> - Code has the right pattern but wrong format (KH-209: matched `Vnn` but not `nnVn`)
> - Fix exists but callers bypass it (KH-212: KH-153 fix requires `component_type` param
>   that callers don't pass)
> - Transforms are applied but decomposed wrong (KH-207: `compute_pin_positions` runs but
>   matrix→angle extraction is mathematically incorrect)
>
> Include in every report: (1) the function name and line number that produces the wrong
> result, (2) the actual input values from the repro file, (3) what the code returns vs
> what it should return.

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

### KH-207 — Legacy 2x2 matrix decomposition produces wrong pin positions (HIGH)

**Symptom:** Components placed with certain rotation/mirror transforms in KiCad 5 `.sch`
files have their pin-to-net assignments scrambled. GND pins get mapped to signal nets and
vice versa. Affects components using non-trivial 2x2 orientation matrices.

**Root cause:** The legacy matrix decomposition at `analyze_schematic.py:2468-2481` is
mathematically incomplete. The code does apply transforms via `compute_pin_positions()`
before wire matching, but the decomposition of the 2x2 matrix `(a, b, c, d)` into
rotation angle + mirror flags is wrong for several matrix values. Specifically:
- Matrix `(0, 1, -1, 0)` (90° CCW): code extracts angle=90 no-mirror, producing pin
  offset `(-5, 10)` instead of correct `(5, -10)`.
- `mirror_y` is **never set** for legacy components (only `mirror_x` via determinant check).
- Angle extraction uses only `(a, b)` pair without fully accounting for mirror correction.

**Impact:** Propagates into ERC warnings, net classification, power domain analysis,
bus analysis, and signal detectors. Any downstream analysis referencing pin-net assignments
on affected components will be wrong.

**File:** `analyze_schematic.py:2468-2481` (matrix decomposition), `:326-337`
(`compute_pin_positions` transform application).

**Repro:** `koron/yuiop` — `yuiop60pi/main2/main2.sch` — F1 (Fuse) at line 550 with
matrix `(0, 1, -1, 0)`. Matrix appears in 40+ files across koron/yuiop (yuiop47, yuiop54,
yuiop60hh). Also affects U1 (PGA2040) with matrix `(-1, 0, 0, -1)`.

**Discovered:** 2026-04-08 via Layer 3 subagent review. Root cause corrected 2026-04-09.

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

### KH-209 — Power rails with `nnVn` naming pattern classified as signal (MEDIUM)

**Symptom:** Nets named `12V0`, `3V3`, `5V0`, `1V5`, `1V8`, `6v`, `Neg6v`, `VDD5`,
`VDD12`, `5V_INT` etc. are classified as `signal` or `interrupt` in net_classification
instead of `power`. These are clearly power rails feeding multiple ICs.

**Root cause:** `is_power_net_name()` at `kicad_utils.py:800-840` does check voltage
patterns, but only the `Vnn` format (V3V3, V5V0, V12P0 — V-first). The industry-standard
`nnVn` format (3V3, 5V0, 12V0 — digit-first) is completely unmatched. The Vnn check at
lines 826-828 requires `nu[0] == "V"` and `nu[1].isdigit()`, so digit-first names fail
immediately. Also misses `VDD5`/`VDD12` (no underscore separator, so the underscore-prefix
check at lines 832-839 doesn't trigger). `5V_INT` has underscore but first segment `5V`
is not in the valid prefix list.

**File:** `kicad_utils.py:826-839` (pattern matching), `analyze_schematic.py:2977`
(classification call site).

**Repro:** `azonenberg/starshipraider` (12V0, 3V3, 5V0 etc.), `Duet3D/Duet-2-Hardware`
(5V_INT as 'interrupt'), `GoodEarthWeather/myKicadProjects` (VDD12/VDD5/VDD3.3 missing),
`jonathan-tooley/903` (6v/Neg6v as signal).

**Discovered:** 2026-04-09 via Layer 3 batch review (4 repos affected). Root cause
corrected 2026-04-09.

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

### KH-212 — Bare capacitor values < 1.0 parsed as Farads (MEDIUM)

**Symptom:** Capacitors with unitless value `0.1` in 0603/0805 packages are parsed as
0.1 Farads (100,000 µF) instead of 0.1 µF (100 nF). This causes absurd RC filter
calculations (0 Hz cutoff) and wildly inflated decoupling totals (100,047 µF).

**Root cause:** Two-part failure in `parse_value()` at `kicad_utils.py:276-281`:
1. The KH-153 fix (bare integers → picofarads) only applies when `result >= 1.0`. Values
   < 1.0 (like 0.1, 0.47, 0.22, 0.01) fall through and are returned as Farads.
2. Key callers bypass even the KH-153 fix: `analyze_bom_optimization()` at line 6278 and
   `analyze_schematic()` at line 7595 call `parse_value(val_str)` WITHOUT the
   `component_type` parameter, so the capacitor-specific pF conversion never triggers.
   Meanwhile `AnalysisContext.__post_init__()` at `kicad_types.py:81` correctly passes
   `component_type=c.get("type")`, creating inconsistent parsed values in memory.

**File:** `kicad_utils.py:276-281` (parse_value fallthrough), `analyze_schematic.py:6278`
and `:7595` (callers missing component_type).

**Repro:** `eddyem/stm32samples` — C16/C15 value="0.1", C19/C17/C18 value="0.47" in
`F1:F103/BISS_C_encoders/kicad/isolated_232.kicad_sch`.

**Discovered:** 2026-04-09 via Layer 3 batch review. Root cause corrected 2026-04-09.

---

### KH-213 — P-MOSFET detection misses PMOS/P-MOS/P-MOSFET keyword variants (LOW)

**Symptom:** IRF9310 classified as N-channel MOSFET despite lib_symbol description
saying `P-MOSFET transistor` and keywords containing `PMOS P-MOS P-MOSFET`.

**Root cause:** Channel detection at `signal_detectors.py:2457-2467` does check keywords,
but only matches `p-channel` and `pchannel` (lines 2463-2464). The actual KiCad library
keywords for this part are `"transistor PMOS P-MOS P-MOSFET"` — none of which contain the
substring `p-channel` or `pchannel`. The lib_id check (lines 2461-2462) looks for `pmos`
but the lib_id is `elements:IRF9310` which doesn't contain it. The value check (lines
2465-2467) also fails since `irf9310` doesn't contain `pmos`. The `description` field
(`"P-MOSFET transistor..."`) is never checked at all.

**File:** `signal_detectors.py:2461-2467` (P-channel detection logic).

**Repro:** `eddyem/stm32samples` — Q2 IRF9310 (lib_id=`elements:IRF9310`,
keywords=`transistor PMOS P-MOS P-MOSFET`).

**Discovered:** 2026-04-09 via Layer 3 batch review. Root cause corrected 2026-04-09.

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
2. KH-207 — Legacy 2x2 matrix decomposition produces wrong pin positions (HIGH)
3. KH-209 — Power rails with `nnVn` naming pattern classified as signal (MEDIUM)
4. KH-210 — SPI chip select detection too narrow (MEDIUM)
5. KH-211 — LED chain fragmentation across hierarchical sheets (MEDIUM)
6. KH-212 — Bare capacitor values < 1.0 parsed as Farads (MEDIUM)
7. KH-214 — INA2xx power monitors as opamp circuits (LOW)
8. KH-215 — LM2576/LM2596 switching bucks as LDO (LOW)
9. KH-213 — P-MOSFET detection misses PMOS/P-MOS/P-MOSFET keyword variants (LOW)
10. KH-216 — Multi-unit IC pin_nets shows wrong unit's pins (LOW)
11. KH-217 — Crystal frequency parsing case-sensitive (LOW)
