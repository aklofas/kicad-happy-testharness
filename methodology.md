# Methodology

How we validate a suite of KiCad analyzers against 1,050+ real-world open-source hardware designs, and why the system is built the way it is.

---

## The problem

kicad-happy includes three deterministic Python analyzers that parse KiCad schematics, PCB layouts, and Gerber files. They extract components, nets, and signal paths, then run 21+ signal detectors (voltage dividers, regulators, filters, bus protocols, opamp circuits, etc.) to produce structured JSON output.

These analyzers contain 180+ hardcoded constants: voltage reference tables sourced from datasheets, component classification keyword lists, regex patterns for net name matching, and numeric thresholds for detection heuristics. A single wrong entry — a hallucinated Vref value, an overly broad regex, a misclassified component prefix — can silently produce incorrect results across hundreds of projects.

The problem is: **how do you know the analyzers are correct?**

Manual review doesn't scale. There are 6,800+ schematic files across the corpus, each producing hundreds of structured observations. A human reviewer can check a few dozen files per session. Without automation, regressions accumulate faster than they can be caught.

---

## Design constraints

Several constraints shaped the architecture:

1. **No ground truth exists.** There is no authoritative database of "correct" signal analysis results for arbitrary KiCad projects. The analyzers are producing novel observations — voltage divider ratios, regulator configurations, filter topologies — that no prior tool has computed.

2. **The corpus is too large for a single session.** 1,050+ repos with 6,800+ schematics. Any workflow must support incremental, per-repo processing across many sessions.

3. **Analyzer changes are frequent.** Bug fixes, new detectors, and constant table updates happen regularly. Each change can affect outputs across the entire corpus. Regression detection must be fast and precise enough to distinguish intentional improvements from unintended breakage.

4. **False positives are the primary failure mode.** A voltage divider detector that fires on every pair of series resistors is useless. A regulator detector that classifies op-amp feedback networks as power supplies is actively misleading. The system must catch these, not just missing detections.

5. **LLM review is expensive.** Generating findings requires reading source schematics, cross-referencing with analyzer output, and understanding circuit intent. This is the highest-quality validation layer but also the slowest. Insights from LLM review must be preserved permanently, not lost between sessions.

6. **Pure Python, no dependencies.** The analyzers and test harness use only Python 3.8+ stdlib. No numpy, no testing frameworks, no external tools beyond git.

---

## The 3-layer approach

We use three complementary regression layers, each catching different classes of problems at different cost/precision tradeoffs.

### Layer 1: Baselines — broad structural change detection

**What it catches:** New or removed output sections, large count shifts, structural changes to analyzer output format.

**How it works:** `snapshot.py` extracts a compact manifest from each analyzer output: component counts by type, signal detection counts, net statistics, and a list of output sections present. These manifests are checked into git under `reference/{repo}/{project}/baselines/`. When the analyzer changes, `compare.py` diffs current outputs against baselines to flag structural shifts.

**Why compact manifests, not full outputs?** Full analyzer JSON for a single schematic can be 100KB+. Across 6,800 files, that's ~680MB of git-tracked data. Baselines compress this to ~1KB per file by storing only counts and section names. The full outputs live in git-ignored `results/` and are regenerated on demand.

**Limitations:** Baselines detect *that* something changed, not *whether* the change is correct. A baseline that says "voltage_dividers: 5 -> 3" doesn't tell you if the two removed detections were false positives (improvement) or true detections that regressed (bug). That's what Layer 2 is for.

### Layer 2: Assertions — precise regression detection

**What it catches:** Specific known-good detections disappearing, specific known-bad detections returning, exact component classifications changing.

**How it works:** Assertions are machine-checkable JSON facts about what an analyzer should find in a specific file. Each assertion has a `check` object with a JSON path, an operator, and expected values. `run_checks.py` evaluates all assertions against current outputs and reports pass/fail.

**Example:** "In `hackrf/marzipan.kicad_sch`, the `signal_analysis.crystal_circuits` section should contain an item where `reference` matches `^Y1$`." This assertion survives analyzer refactoring, constant table changes, and output format evolution — as long as the analyzer still correctly identifies Y1 as a crystal circuit.

**Operators:** The assertion engine supports 12 operators chosen to cover the kinds of facts we need to express:

| Operator | Purpose | Example |
|----------|---------|---------|
| `range` | Count within tolerance band | Component count 207-255 |
| `min_count` | At least N items | At least 1 power regulator |
| `max_count` | At most N items | Zero false RF matching detections |
| `equals` | Exact value or count | Exactly 4 crystal circuits |
| `exists` / `not_exists` | Section present or absent | Signal analysis section exists |
| `greater_than` / `less_than` | Numeric comparison | More than 10 nets |
| `field_equals` | Find item by field, assert another field | CR9's type is "diode" |
| `contains_match` | Regex match on item field | R15 appears in voltage_dividers |
| `not_contains_match` | Negative regex match | C5 does NOT appear in rc_filters |
| `count_matches` | Count items matching regex | Exactly 3 resistors in dividers |

The `not_contains_match` and `count_matches` operators were added specifically to express false-positive assertions — "this component should NOT appear in this detector" — which are critical for catching the dominant failure mode.

### Layer 3: LLM review — semantic quality assessment

**What it catches:** Misclassifications that can only be identified by understanding circuit intent, missing detections that require domain knowledge, false positives that look structurally valid but are semantically wrong.

**How it works:** `packet.py` generates review packets that pair KiCad source files with analyzer output summaries. Claude reviews these packets and produces findings — structured observations about what the analyzer got right (correct), wrong (incorrect), or missed (missed). Findings are stored in `reference/{repo}/{project}/findings.json` and rendered to human-readable markdown.

**Why this layer exists:** Some errors can't be caught by assertions alone. Consider an opamp feedback network with two resistors: the voltage divider detector will correctly identify the resistor ratio, but it's semantically wrong — it's gain-setting feedback, not a voltage divider for signal conditioning. Catching this requires understanding the surrounding circuit context, which is exactly what LLM review provides.

---

## Assertion categories

Not all assertions serve the same purpose. We maintain four categories, each generated differently and serving a distinct role in the regression pipeline.

### SEED assertions (~64K)

**Generated by:** `seed.py`

**Purpose:** Broad statistical coverage. Every schematic file with analyzer output gets a set of SEED assertions that verify component counts, net counts, and signal detection section sizes within tolerance bands.

**How they're generated:** From current analyzer output, extract `statistics.total_components`, component type counts, net count, and signal analysis section sizes. Apply a configurable tolerance (default 10%) to produce `range` assertions. For a file with 47 components, the assertion is `range(42, 52)`.

**Design choice — why tolerance bands?** Early versions used exact counts (`equals`), but these broke constantly. Adding a single component to a KiCad project's standard library resolution would shift counts by 1-2, causing false failures. Tolerance bands absorb minor fluctuations while still catching major regressions (e.g., a detector that stops finding anything).

**Limitations:** SEED assertions are coarse. They verify that a section has "roughly the right number of items" but not that the *right* items are present. A detector that replaces 5 correct voltage dividers with 5 false positives would pass all SEED assertions.

### STRUCT assertions (~44K)

**Generated by:** `seed_structural.py`

**Purpose:** Per-detection structural verification. For each signal detection, assert the exact count AND the presence of specific component references.

**How they're generated:** For each signal analysis section, extract every unique component reference mentioned in the detection results. Generate a `contains_match` assertion for each reference (e.g., "R15 appears in voltage_dividers") and an `equals` assertion for the total count. Uses `refextract.py` to navigate the different field paths where references appear across detector types (voltage dividers store refs in `r_top.ref`/`r_bottom.ref`, crystal circuits in `reference`, opamp circuits in `reference`, etc.).

**Why REF_FIELD_MAP exists:** Each signal detector stores component references in different fields. Voltage dividers have `r_top.ref` and `r_bottom.ref`. Crystal circuits have `reference`. Opamp circuits have `reference`. The `REF_FIELD_MAP` in `refextract.py` maps detector names to their reference field paths, allowing `seed_structural.py` and `generate_finding_checks.py` to write correct assertions without hardcoding detector-specific logic everywhere.

**Design choice — strict vs tolerant mode:** `--tolerant` mode uses `min_count` instead of `equals` for detection counts, allowing new detections to appear without breaking assertions. Strict mode (default) uses `equals` to catch both additions and removals.

### FND assertions (~664, of which ~216 aspirational)

**Generated by:** `findings.py promote`

**Purpose:** Preserve LLM review insights as permanent, machine-checkable regression tests.

**How they're generated:** When a finding is promoted, each item in `correct`, `incorrect`, and `missed` is converted to an assertion:

- **Correct items** become positive assertions ("this should keep working"). If the item has a `check` field, that check is used directly. Otherwise, a `min_count >= 1` assertion is generated for the analyzer section.
- **Incorrect items** become **aspirational** negative assertions ("this bug should eventually be fixed"). Typically `not_contains_match` assertions that verify a false positive has been removed.
- **Missed items** become **aspirational** positive assertions ("this should eventually be detected"). Typically `min_count >= 1` or `contains_match` assertions for the expected detection.

**Aspirational assertions:** Assertions marked `"aspirational": true` are expected to fail. They represent the desired future state — what the analyzer *should* do once a bug is fixed. They are tracked separately from regular assertions (excluded from the pass rate) but included in drift detection. When an aspirational assertion starts passing, drift.py reports it as `now_detected` or `possibly_fixed`, signaling that the bug may have been fixed and the assertion can be upgraded to a regular one.

**Why aspirational assertions matter:** Without them, knowledge from LLM review is lost. A reviewer identifies that "C5 is falsely detected as an RC filter because it's actually part of an opamp feedback network." If we only track this as a text finding, we have to re-review the file manually to check if it's been fixed. With an aspirational assertion (`not_contains_match` for C5 in rc_filters), drift.py automatically detects when the fix lands.

### BUGFIX assertions (~34)

**Generated by:** `generate_bugfix_assertions.py` from `bugfix_registry.json`

**Purpose:** Prevent specific fixed bugs from returning. Each assertion is tied to a KH-* issue number.

**How they're generated:** The bugfix registry is a hand-curated JSON file mapping issue numbers to specific check objects. Each entry records:
- The issue number (e.g., KH-091)
- The fix type (classification_fix, false_positive_fix, count_change_fix, detection_fix)
- The repo, project, and source file where the bug was observed
- A check that would fail if the bug returned

**Example:** KH-091 was "CR-prefixed diodes misclassified as capacitors." The bugfix assertion uses `field_equals` to verify that `CR9` in the `components` list has `type: "diode"`, not `type: "capacitor"`. If a future analyzer change re-introduces the CR-prefix misclassification, this assertion fails immediately.

**Design choice — why a separate registry?** Bugfix assertions need different metadata than seed or finding assertions. They track issue numbers, fix types, and the specific behavioral guarantee. A separate registry makes it easy to audit coverage ("which KH-* issues have regression tests?") and generate assertions in batch.

**Current coverage:** 29 of 153 closed KH-* issues have bugfix assertions. The registry is expanded as new bugs are fixed.

---

## The findings pipeline

Findings are the bridge between expensive LLM review and cheap automated regression testing. The pipeline has five stages:

### Stage 1: Review packet generation

`packet.py` selects files for review using configurable strategies:
- **random** — uniform random sample across the corpus
- **changed** — files that changed since last baseline snapshot
- **signal-rich** — files with the most signal analysis detections (weighted by detector diversity)

Each packet pairs the original KiCad source file content with a summary of the analyzer output, formatted for LLM consumption.

### Stage 2: LLM review

Claude reviews the packet and produces a finding with the tripartite structure:
- **correct[]** — items the analyzer got right, with specific component references and section paths
- **incorrect[]** — classification errors, false positives, misidentifications
- **missed[]** — expected detections that didn't happen

Each item gets an `analyzer_section` field (e.g., `signal_analysis.voltage_dividers`) that anchors it to a specific part of the output.

### Stage 3: Check field generation

`generate_finding_checks.py` enriches finding items with machine-checkable `check` fields:

1. Parse the `description` text to extract component references using `refextract.py` (handles patterns like "R15/R16", "Q13-Q16", and "U4A" unit suffixes)
2. Look up the reference field path for the detector using `REF_FIELD_MAP`
3. Generate appropriate check:
   - Correct item with refs → `contains_match` (verify ref IS in the section)
   - Incorrect item with refs → `not_contains_match` (verify ref is NOT there)
   - Missed item with refs → `contains_match` (verify ref IS now detected)
   - Items without extractable refs → section-level `exists`/`min_count`

This step is critical because it converts free-text LLM observations into deterministic checks that drift.py can evaluate automatically.

### Stage 4: Drift detection

`drift.py` re-evaluates all findings against current outputs:
- Correct item + check passes → **ok** (still working)
- Correct item + check fails → **regression** (something broke)
- Incorrect item + check passes → **possibly_fixed** (bug might be resolved)
- Incorrect item + check fails → **ok** (bug still present, expected)
- Missed item + check passes → **now_detected** (new detection appeared)
- Missed item + check fails → **ok** (still missing, expected)

For findings without check fields, drift.py falls back to section-level counting: if the analyzer_section exists and has items, the correct item is considered present; if it's empty or missing, it's a regression.

`cleanup_drift.py` handles stale items — findings that reference output paths that no longer exist (e.g., after a detector rename or output restructure).

### Stage 5: Promotion

`findings.py promote` converts findings to permanent assertions. The promoted assertions go in `{file}_finding.json` alongside the other assertion files. Aspirational assertions are included but marked, so they can be tracked without affecting the pass rate.

---

## The constants audit

Hardcoded constants are the biggest source of silent errors. The `audit_constants.py` system addresses this with three mechanisms:

### AST scanning

Python's `ast` module walks the analyzer source code to find all constant definitions: module-level dicts, function-level lookup tables, keyword lists, regex patterns, and numeric thresholds. Each constant gets a stable ID (CONST-NNN), content hash for drift detection, and automatic categorization:

| Category | Example | Verification source |
|----------|---------|---------------------|
| `physics` | Unit conversions, coordinate tolerances | Textbook, auto-verified |
| `standard` | KiCad format codes, IPC designators | KiCad docs, IPC standards |
| `datasheet_lookup` | Regulator Vref values, quiescent currents | Manufacturer datasheets |
| `heuristic_threshold` | Scoring cutoffs, detection thresholds | Engineering judgment + corpus tuning |
| `keyword_classification` | Part families, net name patterns | KiCad stdlib + domain knowledge |

### Two-dimensional risk scoring

Each constant is scored on two axes:

- **Impact** (0.0-1.0) — How bad is it if this constant is wrong? A hallucinated Vref value silently produces incorrect voltage calculations for every board using that regulator. A wrong keyword in an obscure detector might affect one file.
- **Overfit** (0.0-1.0) — Does this constant generalize across the corpus, or was it added to fix one project? Starts with structural heuristics (inline vs module-level, table size), then `corpus` analysis fills in real hit data.

Risk score = `max(impact * (1 - verified_fraction), overfit)`. Verification drives risk down. High overfit stays risky regardless.

### Corpus cross-reference

`audit_constants.py corpus` scans all analyzer outputs to measure which constants actually fire. For the `_REGULATOR_VREF` table (92 entries mapping regulator part prefixes to reference voltages), it traces `vref_source: "lookup"` in power_regulator detections to identify which table entries match real parts. Entries with zero corpus hits get flagged as potential dead weight, increasing the overfit score.

---

## Issue tracking and the feedback loop

Issues are discovered opportunistically during any phase of testing:

1. **During batch runs** — analyzer crashes, unexpected output structure
2. **During assertion checking** — known-good detections disappearing
3. **During LLM review** — false positives, misclassifications, missing detections
4. **During drift checks** — regressions in previously-correct findings

Each issue gets a globally unique ID (KH-* for analyzer bugs, TH-* for harness issues) and lives in ISSUES.md until fixed. On fix, it moves to FIXED.md with root cause and verification details.

The bugfix registry closes the loop: when a KH-* issue is fixed, a regression entry is added to `bugfix_registry.json`, and `generate_bugfix_assertions.py` creates permanent assertions that prevent the bug from returning.

```
LLM review discovers bug → KH-NNN filed in ISSUES.md
    → Fix lands in analyzer
    → Issue moved to FIXED.md
    → Bugfix entry added to registry
    → BUGFIX-* assertion generated
    → Aspirational FND-* assertion upgraded to regular assertion
    → drift.py confirms fix via possibly_fixed/now_detected
```

---

## Repo management

### Selection criteria

The corpus of 1,052 repos was curated from publicly available GitHub repositories containing KiCad project files. 87 repos were purged after audit:
- 18 Eagle-only repos misidentified as KiCad
- 14 tool/library repos with example PCBs but no real designs
- 22 PCB-only repos with no schematics
- 33 repos with fewer than 3 components (templates, art pieces, rulers)

### Reproducibility

Every repo in `repos.md` is pinned to a specific commit hash. `checkout.py --check-updates` compares pinned hashes to remote HEAD, and `--pin` updates the hashes. This ensures that re-running the test harness on any machine produces identical results, regardless of upstream changes.

### Priority ranking

`priority.md` ranks repos by schematic complexity (total file size) as a proxy for signal detector coverage value. Complex designs with many signal paths exercise more detectors and are more likely to expose edge cases. The priority queue guided batch testing order: high-priority repos were tested first to maximize early coverage.

---

## Data organization

All persistent data follows the same per-repo, per-project hierarchy:

```
reference/{repo}/{project}/
    baselines/          # Layer 1: compact output snapshots
    assertions/{type}/  # Layer 2: machine-checkable facts
    findings.json       # Layer 3: LLM review observations
    findings.md         # Auto-rendered from findings.json
```

**Project naming:** The project name is derived from the path to the KiCad project directory within the repo, with `/` encoded as `_`. Root-level projects use the `.kicad_pro` filename stem. This encoding is invertible via `metadata.json` which stores the original `project_path`.

**Working data** lives in git-ignored `results/`:

```
results/
    manifests/{repo}/   # Discovered file lists
    outputs/{type}/{repo}/  # Current analyzer JSON outputs
```

This separation means the git repository tracks only curated regression data (~7MB for the full corpus), not raw analyzer outputs (~680MB+).

---

## Current state

As of 2026-03-17:

| Metric | Value |
|--------|-------|
| Repos in corpus | 1,052 |
| Repos with baselines + assertions | 1,035 |
| Total schematic files | 6,827 |
| Total assertions | 110,175 |
| Assertion pass rate | 100.0% |
| Aspirational assertions | 216 |
| KH-* issues filed/closed | 153/153 |
| Layer 3 reviewed repos | 158 of 1,035 |
| Total findings | 319 |
| Finding items with check fields | 1,304 |

The priority queue is empty — all repos have been tested at Layer 1-2. Layer 3 coverage continues to expand.

---

## Weaknesses and limitations

### No independent ground truth

The most fundamental limitation: there is no external oracle for what a KiCad signal analyzer should produce. Every assertion in the system was either derived from the analyzer's own output (SEED, STRUCT) or from LLM review of that output (FND). This creates a circularity at every layer:

- **SEED and STRUCT assertions** encode the current behavior as correct. If the analyzer has a systematic false positive that appears in every file (e.g., misclassifying a common circuit topology), these assertions lock that wrong behavior in as the expected result. Worse, they resist fixing it — a correct fix that removes false positives will break thousands of assertions, making it look like a regression.
- **LLM findings** are the only layer that reasons independently about correctness, but the reviewer (Claude) can misread a schematic, misidentify a component's role, or miss context. There is no second reviewer. Findings will inevitably contain errors, and those errors propagate into FND assertions and bugfix entries.
- **Bugfix assertions** verify the fix at the point where we believe it's correct. If the original diagnosis was wrong — if what looked like a false positive was actually correct — the bugfix assertion encodes the wrong expectation permanently.

The system mitigates this through corpus diversity (many different repos exercise the same detectors in different contexts, making systematic errors more visible) and the constants audit (cross-referencing hardcoded values against datasheets). But it cannot prove correctness — only consistency with prior judgments.

### The reviewer is fallible

Layer 3 review is performed by Claude, which introduces several categories of error:

- **Circuit misinterpretation.** An LLM reading a schematic can misidentify component roles. A feedback resistor pair around an opamp may be called a "false positive voltage divider" when it actually is a deliberate voltage divider used for biasing. Or the reverse: a reviewer may accept a detection as correct when it's actually a coincidental resistor pair with no voltage-dividing function.
- **Missing cross-sheet context.** The reviewer sees one schematic file at a time. In hierarchical designs, the function of a subcircuit depends on how it's connected in the parent sheet. Without that context, findings will sometimes be wrong.
- **Inconsistent severity.** Whether something is classified as "incorrect" vs "correct but imprecise" depends on the reviewer's judgment in the moment. The same edge case may be flagged in one review and accepted in another.
- **Error accumulation.** As findings are promoted to assertions, reviewer errors become permanent fixtures of the regression suite. A wrong finding becomes a wrong assertion, which then resists correct analyzer changes. The drift system detects when assertions break, but it can't distinguish "assertion was wrong all along" from "analyzer regressed."

There is no systematic mechanism to re-review existing findings for accuracy. The assumption is that errors are sparse enough that corpus diversity compensates, but this has not been validated.

### Behavioral regression is not correctness testing

This system is fundamentally a **behavioral regression suite**. It answers "did the analyzer's output change?" and "did known-correct things stop working?" It cannot answer "is this output correct for a design nobody has reviewed?"

This means the suite's confidence is bounded by its review coverage. For unreviewed repos, the assertions only guarantee structural consistency with a prior run — not that the prior run was correct. A detector that produces plausible-looking but wrong results will pass all SEED and STRUCT assertions indefinitely, until someone reviews the output and files a finding.

### Tolerance bands create a detection blind spot

SEED assertions use 10% tolerance bands to avoid brittleness. A file with 50 components gets `range(45, 55)`. If a bug causes the count to drop from 50 to 46, the assertion still passes. STRUCT assertions partially compensate (they check specific component references in signal analysis sections), but the basic component parsing pipeline has no per-component assertions — only aggregate counts with tolerance.

This is a deliberate tradeoff. Tighter tolerances cause frequent false failures when KiCad library resolution changes component counts by 1-2, which happens often. But it means small regressions accumulate undetected until they exceed the tolerance threshold. A series of small bugs, each removing one or two components from detection, could collectively drop accuracy significantly while never tripping an assertion.

### Aspirational assertions can't be validated until they pass

Aspirational assertions represent known bugs. They encode the *desired* behavior: "C5 should NOT appear in rc_filters" or "power_regulators should have at least 1 entry." But until the bug is fixed and the assertion starts passing, there's no way to verify that the assertion itself is correctly specified. A badly-written check might pass for the wrong reason when the fix eventually lands — matching the right component for the wrong detector, or passing because a section was emptied rather than because the specific false positive was removed.

### Corpus bias toward hobbyist designs

The test corpus is drawn from public GitHub repositories, which biases it toward:
- **ESP32 dev boards** and **mechanical keyboards** (the dominant categories in open-source KiCad)
- **Simple power supplies** — linear regulators and basic buck converters
- **Through-hole and standard SMD** packaging
- **KiCad 7-9** file formats (KiCad 5 legacy is thinner)

Underrepresented domains include high-frequency RF, precision analog, power electronics with complex topologies (interleaved converters, PFC stages), mixed-signal designs, and anything with exotic packaging. The analyzers may perform well on the corpus while failing on the first professional design in an unfamiliar domain.

This bias also affects the constants audit: corpus cross-referencing can only validate constants against the designs that exist in the corpus. A regulator Vref entry for a part that no open-source project uses will show zero corpus hits and be flagged as potential dead weight — but it might be perfectly correct and essential for a user's specific design.

### Single-file analysis limits what assertions can express

The schematic analyzer processes each `.kicad_sch` file independently. In hierarchical designs, a power regulator on one sheet drives decoupling capacitors on another, but the analyzer can't associate them across files. This is a limitation of the analyzer, not the test harness — but the test harness inherits it, because assertions can only check what the per-file analyzer produces.

This means certain classes of correctness can never be asserted: "the 3.3V regulator on the power sheet correctly associates with the 47uF output cap on the MCU sheet" is not expressible. Findings can note this as a missed detection, but the resulting aspirational assertion can only check whether the section exists on the individual sheet, not whether the cross-sheet association is correct.

### Check field generation is fragile

The `generate_finding_checks.py` script converts free-text finding descriptions into machine-checkable assertions by extracting component references with regex. This works well for descriptions like "R15 falsely detected as voltage divider" but fails on:

- Descriptions that reference component values instead of designators ("100k feedback resistor")
- Ambiguous references that match false-positive patterns ("S1" could be a sheet reference or a switch)
- Descriptions with unusual formatting or references embedded in longer words
- Detectors where the reference field path doesn't match REF_FIELD_MAP (new or renamed detectors)

Items without extractable refs fall back to section-level `min_count` or `exists` checks, which are much coarser. A finding that says "RC filter false positives from opamp feedback network" with no specific refs becomes a blunt "rc_filters section exists" check that can't distinguish between the false positive being fixed and the section being emptied entirely.

### The 100% pass rate is a constructed artifact

The assertion pass rate is maintained at 100% by design: when analyzer behavior changes, assertions are regenerated to match. This is necessary for the system to function (you can't run a regression suite with thousands of known failures), but it means the pass rate measures *consistency with the last accepted state*, not *correctness*. The number is meaningful for catching unintentional regressions between accepted states, but it says nothing about the quality of the accepted state itself.

### Constant verification doesn't scale

The constants audit identifies which hardcoded values exist and measures their corpus impact, but verifying them requires manual cross-reference with manufacturer datasheets. This is fundamentally an O(n) human effort problem. The `_REGULATOR_VREF` table has 92 entries; each one is a Vref value claimed to come from a specific regulator family's datasheet. Verifying all of them means opening 92 datasheets and checking 92 values. The audit system can prioritize (high-impact, high-corpus-hit entries first) but cannot automate the verification itself.

More subtly, the corpus analysis can detect constants that are *unused* (zero hits) but not constants that are *wrong*. A Vref value that fires on 50 repos will show high corpus coverage, but if the value is 1.25V when the datasheet says 1.235V, the corpus analysis can't detect that. Only manual verification or a failed real-world design review would surface the error.
