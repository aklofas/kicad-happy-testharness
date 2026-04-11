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

Last updated: 2026-04-11

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new number,
check both ISSUES.md (open) and FIXED.md (closed) for the current maximum. Next KH
number: **KH-240**. Next TH number: **TH-015**.

> 8 open issues.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-239: LED current-limit resistors double-classified as sleep_current pull-ups

**Severity:** MEDIUM
**Discovered:** 2026-04-11 during 2026-04-11 main-repo inspection brief (#7)
**Where:** `kicad-happy/skills/kicad/scripts/analyze_schematic.py:5426-5446` in `analyze_sleep_current()`
**Blast radius:** **4,123 double-classified resistors across 1,746 schematic files in 733 repos** (17% of files with `sleep_current_audit` populated). Median overstatement ~52.6% on affected rails, median absolute error ~2 mA per resistor.

**Root cause:** The pull-up detection loop at line 5426 classifies a resistor as `type: "pull_up"` whenever one pin is on a power rail and the other pin is NOT a power or ground net. It does not check whether the non-power pin goes to an LED anode. The LED-series-resistor processing on lines 5448-5492 runs AFTER, sees the same resistor connected to an LED anode, and creates a SECOND entry in `rail_currents` with `type: "led_indicator"` and `series_resistor: R_ref` pointing at the same resistor.

Result: the same resistor appears in `sleep_current_audit.rails[rail].current_paths[]` TWICE:
- once as `type == "pull_up"` (wrong — arithmetic is `V_rail / R`)
- once referenced from `type == "led_indicator"` with `series_resistor == R_ref` (correct — arithmetic is `(V_rail - 2.0) / R`)

Downstream consumers that sum sleep current per rail double-count. For a 3.3V rail with a 1 kΩ LED current-limit resistor, the pull_up entry reports 3,300 µA and the LED entry reports 1,300 µA — the rail total is over-stated by ~2 mA per LED.

**Confirmed blast radius from corpus scan:**
- 36,464 schematic files scanned
- 10,366 have `sleep_current_audit` populated (28%)
- **1,746 have at least one double-classified resistor (17% of populated)**
- **4,123 total double-classifications**
- **733 unique repos affected**
- Top offenders: `adeboni/math-camp-synth` (217), `skysedge/RUST_Hardware` (156), `DRubioG/Artix7_SOM` (106), `fm4dd/pmod-i2c24io` (96)
- Rail voltage distribution: 3.3V (45%), 5.0V (41%), 12V (5%), 3.8V (3.5%), other (5.5%)

**Detection evidence (pure set-intersection on analyzer's own output):**

```python
pull_up_refs = {e["ref"] for e in current_paths if e["type"] == "pull_up"}
led_series_refs = {e["series_resistor"] for e in current_paths
                   if e["type"] == "led_indicator" and e.get("series_resistor")}
double_classified = pull_up_refs & led_series_refs  # non-empty → bug
```

No schematic re-parsing needed — the analyzer self-evidences the misclassification in its own JSON output.

**Suggested fix:** Scan for LEDs FIRST, collect their series_resistor refs into a blacklist, THEN run the pull-up detection loop skipping any resistor in the blacklist. ~10 LOC restructure of `analyze_sleep_current()`. Alternative (simpler but less clean): after the LED loop at line 5492, walk `rail_currents` and drop any `pull_up` entries whose `ref` matches a `series_resistor` value from a sibling `led_indicator` entry.

**Test plan:** Author a synthetic schematic with a power rail → current-limit resistor → LED anode → LED cathode → GND. Assert that `sleep_current_audit.rails[+3V3].current_paths[]` contains exactly one entry for that resistor with `type == "led_indicator"`, not two entries.

**Harness-side verification after fix:** Full evidence is in the (local) 2026-04-11 inspection directory (`feedback_divider_assertions.yaml` — 4,123 entries with `repo`, `schematic_file`, `resistor_ref`, `led_ref`, `pull_up_current_uA`, `led_current_uA`). Post-fix, re-run `run/run_schematic.py` on affected repos and assert each YAML entry no longer has a `pull_up` duplicate.

---

### KH-238: Feedback divider pair-ordering drops valid R-R pairs

**Severity:** HIGH
**Discovered:** 2026-04-11 during 2026-04-11 main-repo inspection brief (#6)
**Where:** `kicad-happy/skills/kicad/scripts/signal_detectors.py:274-280` in the voltage-divider detector
**Blast radius:** **1,156 confirmed misses across 447 unique projects** (40% of regulators with `fb_net` set had 2+ resistors on the feedback net but no `feedback_divider` field). The detector is missing ~40% of valid feedback dividers that it should find.

**Root cause:** The voltage-divider detector dedups candidate resistor pairs via `pair_key = (min(r1), max(r2))` and iterates once per pair. When the pair is first encountered with `r1 = bottom_resistor, r2 = top_resistor` AND the top-of-divider net is unnamed (e.g., an unlabeled intermediate node on a post-inductor pre-ferrite filter), the classification logic fails to find the top net and the pair is skipped entirely. Symptom in the analyzer JSON: regulator has `fb_net` set but no `feedback_divider` field.

**Corpus enumeration (categorized from 2,888 raw misses with `fb_net` set but no `feedback_divider`):**

| Bucket | Count | % | Interpretation |
|---|---|---|---|
| `no_resistors_on_fb` | 1,249 | 43.2% | Fixed-voltage regulator (LM1117-3.3, LM317-3.3) — no divider expected, NOT a bug |
| **`two_or_more_resistors_on_fb`** | **1,156** | **40.0%** | **REAL pair-ordering misses** |
| `one_resistor_on_fb` | 391 | 13.5% | Ambiguous (single-R fb or divider leg off-sheet) |
| `pot_feedback` (RV-R) | 106 | 3.7% | Different topology, not touched by this bug |

**Top 10 regulator families with confirmed misses:** AP63203WU (32), LM317 (29), TPS63070 (17), AP63200WU (16), HX711 (14), MT3608 (12), TPS62140 (12), AMS1117 (12), TPS54226PWPR (12), TLV62569DRL (12).

**Detection method:** For each regulator with `fb_net` set, read `nets[fb_net].pins[]` and count resistors present. If ≥ 2 resistors on the fb net, the analyzer should have classified the pair but didn't. No schematic re-parsing needed.

**Suggested fix:** Normalize pair orientation BEFORE the `pair_key` lookup — identify which resistor is "top" (connected to Vout side) and which is "bottom" (connected to GND) by checking their non-fb pins, then iterate in canonical orientation. Current code assumes r1 is always top and r2 is always bottom, which only holds when the pair is encountered in that source order. ~5 LOC.

**Test plan:** Author a synthetic regulator with:
- Vout net (named) → R_top → unnamed intermediate net → R_bottom → GND
- FB pin tapping the unnamed intermediate net

Assert `power_regulators[]` entry gets a `feedback_divider` field populated with both R_top and R_bottom regardless of source order.

**Harness-side verification after fix:** Full assertion list is in the (local) 2026-04-11 inspection directory (`feedback_divider_assertions.yaml` — 1,156 entries with `repo`, `schematic_file`, `regulator_ref`, `regulator_value`, `fb_net`, `expected_resistors_in_divider`). Post-fix, re-run `run/run_schematic.py` on affected repos and assert each YAML entry now has a `feedback_divider` field containing both expected resistors (order-insensitive). Target: ≥ 1,100 of the 1,156 flip from miss → detected.

**Follow-up beyond this fix:** The 391 `one_resistor_on_fb` cases are probably hierarchical-sheet misses (divider leg on a different sheet than the regulator). Separate bug — would need cross-sheet net tracing. File as a new issue when this one closes if the `one_resistor_on_fb` bucket doesn't shrink naturally.

---

### KH-237: Switching frequency prefix-collision + duplicated table

**Severity:** HIGH
**Discovered:** 2026-04-11 during 2026-04-11 main-repo inspection brief (#5)
**Where:**
- `kicad-happy/skills/kicad/scripts/signal_detectors.py:29` (`_KNOWN_FREQS`, uses `str.startswith`)
- `kicad-happy/skills/emc/scripts/emc_rules.py:866` (`known_freqs` local, uses `prefix in val` — substring!)

**Blast radius:** **10 real mixed-family prefix collisions**, 1,300+ regulator instances with likely-wrong switching frequencies. Affects `signal_analysis.power_regulators[].switching_frequency_hz` in schematic.json AND downstream EMC SW-001 harmonic-band calculations in emc_findings (wrong frequency → wrong harmonics flagged, some findings appear/disappear, some severities flip at band edges).

**Confirmed landmine:** prefix `"TPS54"` maps to 570 kHz (correct for TPS54331 per datasheet). But `"TPS54302".startswith("TPS54")` is True, and TPS54302's actual center frequency is ~400 kHz (range 290-510 kHz). At least 25 TPS54302 + 18 TPS54335 + 12 TPS54226 + 12 TPS54218 + 11 TPS546Dxx = **78 corpus instances** with wrong frequency under the TPS54 prefix alone.

**All 10 real collision prefixes (sorted by instance count):**

| Prefix | Current freq | Unique MPNs | Corpus instances | Notes |
|---|---|---|---|---|
| `TPS54` | 570 kHz | 51 | 317 | Confirmed TPS54302 wrong; TPS54335/TPS54226/TPS54218/TPS546D also suspect |
| `TPS62` | 2.5 MHz | 57 | 292 | TPS62130 (2.5M) vs TPS62410 vs TPS62A01/A02 vs TPS62913 — all different. Prefix too broad. |
| `TPS61` | 1.0 MHz | 65 | 210 | TPS61020/23/30 vs TPS61040 vs TPS61090 vs TPS61200 — prefix too broad. |
| `TPS56` | 500 kHz | 38 | 145 | TPS56339 vs TPS560200 vs TPS562201 vs TPS563200/201/300 vs TPS566238 — prefix too broad. |
| `TPS63` | 2.4 MHz | 28 | 142 | TPS63020 vs TPS63001 vs TPS63070 vs TPS63802 vs TPS63900 vs TPS631000 — very different families. |
| `LM259` | 150 kHz | 16 | 107 | LM2594/LM2596 variants — probably within-family, low risk. |
| `LM257` | 52 kHz | 25 | 101 | LM2574/LM2576 variants — probably within-family, low risk. |
| `TPS629` | 2.2 MHz | 9 | 47 | TPS62912/13 vs TPS629203/206 vs TPS62933 — verify each. |
| `LTC36` | 1.0 MHz | 5 | 16 | LTC3601/3602/3631/3632/3638/3642 — all different parts. |
| `ADP2` | 700 kHz | 8 | 13 | ADP2108/2164/2302/2303/2384/2503 — different families. |

**Table drift between locations:** The two tables have **identical content** (21 prefixes, same Hz values, same comments, verified 2026-04-01). But the matchers behave differently:

- `signal_detectors.py` uses `val.startswith(prefix)` (anchored)
- `emc_rules.py` uses `prefix in val` (substring, anywhere)

Substring is looser and catches MORE MPNs on 8 prefixes (TPS62: +10, TPS56: +5, LM259: +3, TPS54: +1, MP2359: +1, ADP2: +1, XL6009: +1, MT3608: +1). The extras are MPNs where the prefix appears mid-string. Rare in practice but a latent footgun.

**Suggested fix:**
1. Extract `_KNOWN_FREQS` into a shared utility module (e.g., into `kicad_utils.py` alongside `_REGULATOR_VREF`). One source of truth for both `signal_detectors.py` and `emc_rules.py`.
2. Standardize the matcher to `startswith` everywhere. Substring matching on MPN prefixes is too permissive.
3. For real collisions: replace broad prefix entries with exact-MPN or longer-prefix entries to disambiguate. Example for TPS54:
   ```python
   'TPS5430':  570e3,  # TPS5430 family correct
   'TPS54331': 570e3,  # TPS54331 correct
   'TPS54302': 400e3,  # WRONG in current table — TPS54302 actual ~400 kHz
   'TPS54218': None,   # needs DigiKey verification
   'TPS54226': None,   # needs DigiKey verification
   'TPS546D':  None,   # needs DigiKey verification (newer family)
   ```
4. DigiKey-verify the replacement values before shipping. Stub is at (local) `inspections/2026-04-11_prefix_collisions/freq_verified.json` with 302 variants pre-populated for queries.

**Test plan:** Synthetic schematic with a TPS54302 regulator, run `analyze_schematic.py`, assert `power_regulators[0].switching_frequency_hz == 400e3` (after fix). Also run `analyze_emc.py` and assert SW-001 harmonic bands shift to 400 kHz fundamentals instead of 570 kHz.

**Deferred:** Corpus EMC re-run to quantify the SW-001 finding shift (task 2d of the brief). Requires patched freq values first, then ~500 project re-runs, then before/after diff. Hours of work, waterfall on the DigiKey verification. My qualitative prediction: ~30-50% of SW-001 findings on affected boards would shift bands.

---

### KH-236: Regulator Vref prefix-collision in _REGULATOR_VREF table

**Severity:** MEDIUM
**Discovered:** 2026-04-11 during 2026-04-11 main-repo inspection brief (#4)
**Where:** `kicad-happy/skills/kicad/scripts/kicad_utils.py:31` (`_REGULATOR_VREF` dict, used via longest-prefix-match at line 172)
**Blast radius:** **27 real mixed-family prefix collisions**, 1,600+ regulator instances with Vref values of unknown correctness until DigiKey-verified. Confirmed TPS5430 landmine: 29 regulator instances (25 TPS54302 + 2 TPS54308DDC + 2 TPS54308) currently get Vref=1.221V when the actual value for the TPS54302/TPS54308 family is 0.596V per datasheet SLVSEI7. Affects `power_regulators[].estimated_vout` for adjustable regulators (Vout = Vref × (1 + R_top/R_bottom)).

**Root cause:** `_REGULATOR_VREF` uses longest-prefix-match for Vref lookup. Works correctly when newer part families have prefixes that DON'T overlap with older families' table entries. Fails when they DO. Example:

- Table has `"TPS5430": 1.221`  (correct for TPS5430/TPS5450/TPS5410 family per datasheet)
- `"TPS54302".startswith("TPS5430")` → True → TPS54302 gets Vref=1.221V
- But TPS54302 is a newer family with Vref=0.596V

**All 27 real collision prefixes** are in the (local) 2026-04-11 inspection directory (`vref_prefix_collisions.md`). Top 10 by instance count:

| Prefix | Current Vref | Unique MPNs | Instances | Notes |
|---|---|---|---|---|
| `LM78` | 1.25V | 42 | 480 | LM78xx are FIXED-output linear regs — Vref concept doesn't apply. Table entry is inert but misleading. Remove. |
| `SY8` | 0.6V | 22 | 191 | SY8089/SY80004/SY8003/SY8120/SY8208 — multiple Silergy families. |
| `TPS7A` | 1.19V | 41 | 159 | TPS7A0318, TPS7A20, TPS7A25, TPS7A30, TPS7A4501, TPS7A4901, TPS7A49, TPS7A92 — different VFB values. Prefix too broad. |
| `TPS56` | 0.6V | 38 | 145 | TPS560/562/563/565/566 — all different families. |
| `LM259` | 1.23V | 16 | 107 | LM2594/LM2596 variants — probably same family, low risk. |
| `TPS5430` | 1.221V | 6 | 95 | **Confirmed landmine** — TPS54302 (25), TPS54308 (2), TPS54308DDC (2) all wrong. |
| `AP736` | 0.8V | 21 | 79 | AP7361/AP7365/AP7366/AP7384 — different families. |
| `MP2` | 0.8V | 22 | 66 | MP2236/2315/2338/2359/2384/2403/2459/28167 — many families. |
| `LM337` | 1.25V | 9 | 51 | LM337 vs LM3370 — LM3370 is a different family. |
| `AP73` | 0.6V | 22 | 50 | AP7333/AP7335/AP7370/AP7375/AP7381/AP7384 — too broad. |

Full list + matched-MPN detail is in `inspections/2026-04-11_prefix_collisions/vref_prefix_collisions.md` (local only) and `vref_verified.json` (local stub with 337 variants pre-populated for DigiKey verification).

**Filter rationale:** the harness scanned 3,067 unique regulator MPNs across 13,721 instances in the corpus. 42 prefixes had multiple MPN matches; I filtered to the 27 that span distinct part families (digit-after-prefix heuristic). The other 15 ambiguous prefixes are family-variants-only (fixed-voltage suffixes like AMS1117-3.3/5.0/1.8 of the same family — not actionable bugs because the internal Vref doesn't drive Vout estimation for fixed-voltage parts).

**Suggested fix:**
1. DigiKey-verify the Vref value for each of the ~337 variants across the 27 collision prefixes. Takes ~60-90 minutes of API queries.
2. Replace broad prefix entries with exact-MPN or longer-prefix entries for known-wrong variants. Example for TPS5430:
   ```python
   'TPS5430':   1.221,  # correct for base TPS5430
   'TPS5450':   1.221,  # correct
   'TPS5410':   1.221,  # correct
   'TPS54302':  0.596,  # WRONG in current table — TPS54302 actual 0.596V
   'TPS54308':  0.596,  # same new family as TPS54302
   ```
   Longest-prefix match automatically prefers TPS54302 over TPS5430 for MPN TPS54302 once both keys exist.
3. Consider restructuring: replace the longest-prefix-match lookup with an exact-MPN-prefix map to eliminate the whole class of collision bugs. Slower to maintain, immune to future drift.

**Test plan:** Author a synthetic schematic with a TPS54302 adjustable regulator, feedback divider R_top=100kΩ, R_bottom=25.5kΩ. Run `analyze_schematic.py`. Assert `power_regulators[0].estimated_vout ≈ 0.596 × (1 + 100/25.5) ≈ 2.93V` (before fix: ≈ 6.01V). Expected fix behavior: Vout estimate matches the 3.3V nominal target within ±10%.

**Deferred:** DigiKey verification (60-90 min of API queries). Until verified, do NOT patch the table from my report alone — the collision identification is structural, but the replacement values are unverified.

---

### KH-235: extract_pro_net_classes TypeError on non-string net-class names

**Severity:** MEDIUM
**Discovered:** 2026-04-11 during v1.3 #10 harness re-seed sanity check
**Where:** `kicad-happy/skills/kicad/scripts/kicad_utils.py:1209` in `extract_pro_net_classes()`
**Blast radius:** ~0.1% of PCBs (5 crashes in quick_200 of ~4,900, estimated 30-50 corpus-wide)

**Repro:** `python3 skills/kicad/scripts/analyze_pcb.py <affected_board>.kicad_pcb`
produces `TypeError: unhashable type: 'list'`. Traceback:

```
File "skills/kicad/scripts/analyze_pcb.py", line 4864, in analyze_pcb
    pro_net_classes = extract_pro_net_classes(pro)
File "skills/kicad/scripts/kicad_utils.py", line 1209, in extract_pro_net_classes
    class_nets.setdefault(nc_name, []).append(net_name)
TypeError: unhashable type: 'list'
```

**Affected corpus boards (confirmed):**
- `CIRCUITSTATE/Mitayi-Pico-D1/Mitayi-Pico-D1.kicad_pcb`
- `bluerobotics/ping-dev-kit/PingDevKit.kicad_pcb`
- 3 others from the quick_200 crash set (full list in harness logs)

**Root cause:** `extract_pro_net_classes()` iterates `netclass_assignments` from `.kicad_pro`:

```python
for net_name, nc_name in assignments.items():
    if nc_name:
        class_nets.setdefault(nc_name, []).append(net_name)
```

`nc_name` is expected to be a string, but some `.kicad_pro` files store multi-class assignments as a list (e.g. `["Default", "HighSpeed"]`). `setdefault()` then tries to hash the list → TypeError. The crash happens inside `analyze_pcb()` before `analyze_thermal_pad_vias` runs, so it masks every other analysis result for the affected boards (not just thermal).

**History:** Introduced by commit `965b4c7` ("shared detector helpers, .kicad_pro/.kicad_dru parsing") when `extract_pro_net_classes()` was first added. Latent until exercised on a multi-class `.kicad_pro` file. **NOT** a v1.3 #10 regression — the crash happens before `analyze_thermal_pad_vias` is called.

**Suggested fix:** Coerce list → iterate, so a net that belongs to multiple classes gets registered under each class. ~8 LOC:

```python
for net_name, nc_name in assignments.items():
    if not nc_name:
        continue
    if isinstance(nc_name, list):
        for n in nc_name:
            class_nets.setdefault(n, []).append(net_name)
    else:
        class_nets.setdefault(nc_name, []).append(net_name)
```

**Also audit for symmetric bug:** lines 1200-1204 in the same function read `p.get('netclass', '')` from `netclass_patterns`. If KiCad 8+ also permits multi-class pattern assignments (unverified), the same coercion is needed there. Confirm on a corpus sample with multi-class patterns before shipping the fix.

**Test plan:** Add a synthetic test case with list-valued `netclass_assignments` in a `.kicad_pro` fixture. Run `analyze_pcb.py` against `CIRCUITSTATE/Mitayi-Pico-D1/Mitayi-Pico-D1.kicad_pcb` and assert exit 0 with non-empty `thermal_pad_vias` output. A full quick_200 re-run should recover the 5 crashed boards and produce outputs instead of errors.

---

### KH-234: cross_verify thermal-via check uses wrong dict keys — silent zeros

**Severity:** MEDIUM
**Discovered:** 2026-04-10 during v1.3 #10 plan shape review (main-repo agent static inspection)
**Where:** `kicad-happy/skills/kicad/scripts/cross_verify.py:566-569` in `check_thermal_via_adequacy()`
**Blast radius:** Unknown until fix lands and harness re-verifies; estimated 50-90% of current "thermal via inadequacy" findings are false positives caused by this bug.

**Root cause:** `check_thermal_via_adequacy()` builds a `via_lookup` dict from `pcb.get("thermal_pad_vias", [])` entries using the wrong key names on both sides of the lookup:

```python
via_lookup = {}
for tv in pcb.get("thermal_pad_vias", []):
    ref = tv.get("component_ref", "")      # WRONG: actual key is "component"
    if ref:                                # always False — ref is always ""
        via_lookup[ref] = tv.get("count", 0)  # WRONG: actual key is "via_count"

# ... later:
via_count = via_lookup.get(ref, 0)         # always 0
```

The lookup dict is always empty, so every thermal-via cross-check silently returns `thermal_vias: 0` for every component. The check has been dead code in its current form since `cross_verify.py` was written — no crash, no visible output anomaly, just semantically meaningless zeros.

**Actual keys produced by `analyze_thermal_pad_vias`:** each entry in `pcb["thermal_pad_vias"]` uses:

- `"component"` (not `component_ref`) — the reference designator
- `"via_count"` (not `count`) — the strict in-pad via count

**Suggested fix:** ~5 LOC at `cross_verify.py:566-569`:

```python
via_lookup = {}
for tv in pcb.get("thermal_pad_vias", []):
    ref = tv.get("component", "")
    if ref:
        via_lookup[ref] = tv.get("via_count", 0)
```

**Test plan:** Add a regression test that seeds a synthetic `thermal_pad_vias` entry with known `component` and `via_count`, and asserts cross_verify reads it back correctly:

```python
pcb = {"thermal_pad_vias": [{"component": "U1", "via_count": 5, ...}]}
schematic = {...}
thermal = {"thermal_assessments": [{"ref": "U1", "tj_estimated_c": 95, ...}]}
results = cross_verify.check_thermal_via_adequacy(pcb, schematic, thermal)
# Pre-fix: results[0]["thermal_vias"] == 0  (bug)
# Post-fix: results[0]["thermal_vias"] == 5  (fixed)
```

**Sequencing:** Queue behind v1.3 #10 (same general area, no semantic overlap). #10 touches `analyze_pcb.py:analyze_thermal_pad_vias`; KH-234 touches `cross_verify.py:check_thermal_via_adequacy`. No merge risk.

**Harness-side impact when fixed:** Zero. Harness doesn't seed `cross_verify` report.json baselines and cross_verify output doesn't land in analyzer JSON. Fix-and-done, no coordination needed.

**Post-fix follow-up:** Once fixed, run cross_verify against the harness corpus and measure the flag delta. Expected 50-90% drop in flagged components as adequately-via'd components stop being flagged. If the delta matches, close as cleanup. If counts spike or stay flat, that's a secondary investigation.

---

### KH-233: SCHEMAS dict missing 22 detector entries

**Severity:** MEDIUM
**Discovered:** 2026-04-10 by re-enabling `tests/test_detection_schema.py` (TH-014 fix)
**Where:** `detection_schema.py` in `kicad-happy/skills/kicad/scripts/` — the top-level `SCHEMAS` registry.

**Repro:** `python3 tests/test_detection_schema.py` →
`test_schema_completeness_zebra_x` reports 22 `signal_analysis` keys
present in real analyzer outputs but absent from `SCHEMAS`:

```
addressable_led_chains, adc_circuits, audio_circuits, battery_chargers,
buzzer_speaker_circuits, clock_distribution, connector_ground_audit,
debug_interfaces, display_interfaces, hdmi_dvi_interfaces, key_matrices,
led_driver_ics, level_shifters, lvds_interfaces, motor_drivers,
rail_voltages, reset_supervisors, rtc_circuits, sensor_interfaces,
snubbers, suggested_certifications, thermocouple_rtd
```

These detectors fire and write into the analyzer JSON but have no
schema entry — meaning identity/derived field metadata, recalc
functions, and inverse solvers are unavailable for them.

**Expected fix:** add a `DetectionSchema` entry per detector to
`SCHEMAS`. Most are simple (identity fields only, no derived). A few
(rail_voltages, battery_chargers) have computable values that warrant
derived fields and inverse solvers in a follow-up.

**Impact:** downstream code that walks SCHEMAS to determine field
semantics (regression seeding, validation, packet generation) silently
skips these 22 detector classes. Coverage gap.

**How to verify the fix:** in the harness, re-run
`python3 tests/test_detection_schema.py` — `test_schema_completeness_zebra_x`
should flip from XFAIL to XPASS once all 22 keys are present. Remove the
entry from `KNOWN_FAILURES`.

---

### KH-230: Empty placed Value silently substituted with lib_symbol default

**Severity:** LOW
**Discovered:** 2026-04-10 by `validate/verify_parser.py` (P1 Parser Verification, full corpus run)
**Repro:** `hamster/SAINTCON/CHC/2022/Circuits - Series and Parallel.kicad_sch`

The file has two placed `(symbol (lib_id "Device:R") ...)` instances both
annotated as `R1` (a duplicate-annotation design issue independent of this
bug). The second instance has `(property "Value" "")` — explicitly empty —
but the analyzer reports `value: "R"` for it, which is the `Device:R`
lib_symbol's placeholder default Value.

**Expected:** `components[].value` should reflect the placed instance's
property exactly. An empty placed Value should serialize as `""`, not be
silently replaced by the lib_symbol template default. Otherwise downstream
detectors and BOM logic see a fabricated value that doesn't exist in the
source.

**Evidence:**
- sexp parse: R1 instance #2 Value = `""`
- analyzer output: R1 instance #2 value = `"R"` (= lib_symbol default)
- file: `repos/hamster/SAINTCON/CHC/2022/Circuits - Series and Parallel.kicad_sch`
- analyzer output: `results/outputs/schematic/hamster/SAINTCON/CHC_2022_Circuits - Series and Parallel.kicad_sch.json`

Likely in `analyze_schematic.py` symbol parsing path — when the placed
Value property is empty, the code is falling back to `sym_def.get("value")`
or similar instead of preserving the empty string.

Severity is LOW because it requires both a duplicate-annotation defect
AND an empty Value on one of the duplicates, and only 1/25,625 corpus
files hits it.

---



---

## Test Harness Issues

(none)



---

## Deferred

(none)

---

## Priority Queue (open issues, ordered by impact)

1. **KH-233** — MED — SCHEMAS dict missing 22 detector entries (coverage gap); deferred to dedicated plan; needs `snubbers` vs `snubber_circuits` naming clarification
2. **KH-234** — MED — `cross_verify` thermal-via check reads wrong dict keys, returns silent zeros; estimated 50-90% of current thermal-via inadequacy findings are false positives; sequenced behind v1.3 #10
3. **KH-235** — MED — `extract_pro_net_classes` TypeError on multi-class `.kicad_pro` (~30-50 corpus boards crash, hard failure masks all PCB analysis for affected boards)
4. **KH-230** — LOW — empty placed Value silently replaced with lib_symbol default (1 file in corpus)

