# Testing Philosophy

Why the test harness works the way it does. Read [methodology.md](methodology.md) for
the 3-layer architecture; this document explains the reasoning behind it.

---

## Consistency vs correctness

The test harness primarily tests **consistency**, not **correctness**.

**Consistency testing** asks: "Did the output change?" If a voltage divider was detected
last time and isn't detected now, an assertion fails. But this doesn't tell you whether
the voltage divider *should* have been detected — maybe the old result was a false
positive, and the new result is correct.

**Correctness testing** asks: "Is the output right?" This requires ground truth — a
human-verified answer for what the analyzer should find. Ground truth is expensive to
create and doesn't exist for 5,822 open-source KiCad projects.

The layers map to this distinction. "Correctness" in this table does not mean "fully verified" — it means the layer tests against a source of truth independent of the analyzer's own prior output. Each correctness layer has narrow scope and specific limitations; see [methodology.md](methodology.md) § "Toward correctness" for the full accounting.

| Layer | Type | Scope | What it catches |
|-------|------|-------|-----------------|
| Layer 1 (baselines) | Consistency | Full corpus | Structural changes, count shifts |
| Layer 2 SEED-* / STRUCT-* | Consistency | Full corpus | Dropped detections, count drift |
| Layer 2 BUGFIX-* | Narrow correctness | ~67 fixed bugs | Known-right answers from verified bug fixes |
| Layer 2 NEG-* | Narrow correctness | Reviewed false positives | Known false positives stay out |
| Layer 3 LLM review + FND-* | Narrow correctness | ~1,045 reviewed repos | Semantic errors, false positives, missed circuits (reviewer-limited) |
| **v1.3: Parser verification** | Narrow correctness | Full corpus (extraction only) | Extraction mismatches — NOT interpretation bugs |
| **v1.3: Synthetic fixtures** | Narrow correctness | ~30-60 hand-built cases | Detector semantics on deterministic inputs — NOT real-world edge cases |
| **v1.3: Metamorphic tests** | Narrow correctness | Synthetic fixtures only | Causal sensitivity on controlled variants — NOT real-corpus variation |
| **v1.3: Gold-standard tier** | Narrow correctness | ~10 curated real cases | Drift from reviewed claims — limited coverage, reviewer-limited |
| **v1.3: Property invariants** | Narrow correctness | Full corpus (shape only) | Structural invariants (ratio bounds, existence) — NOT content errors |

**Implication:** A 100% assertion pass rate does NOT mean the analyzers are correct.
It means the outputs haven't changed since we last seeded assertions. A passing test
suite with stale assertions is worse than a failing one that caught a regression.

The v1.3 layers add evidence that is independent of the analyzer under test, but each layer has narrow coverage and specific blind spots. Of the 5,822 repos in the corpus, ~99.8% will still have no direct correctness evidence after v1.3 ships — their assertions remain consistency-only. See [methodology.md](methodology.md) § "Toward correctness" for the explicit limitations of each layer and what v1.3 does NOT achieve.

---

## Why 100% pass rate is artificial

When assertions are freshly seeded from current outputs, they pass by definition —
the assertions describe what the output already produces. The pass rate only becomes
meaningful after the analyzer changes:

- **100% after a code change** = the change didn't break anything we were testing
- **99% after a code change** = something we were testing broke — investigate
- **100% with stale assertions** = we haven't tested recently, the pass rate is meaningless

The staleness detector (`regression/check_staleness.py`) exists specifically to flag
this. If outputs are newer than assertions, the pass rate is unreliable.

**What actually matters:**
- Assertion count trending upward (more coverage)
- Mutation catch rate >95% (assertions are effective)
- Cross-validation agreement rates stable
- Zero new failures after code changes (regressions caught)

---

## The re-seed vs investigate decision

When an assertion fails, the question is: did the analyzer regress, or did it improve?

**Re-seed** (the assertion is stale):
- The analyzer code changed intentionally
- The new output looks correct (you verified it)
- The old assertion encoded an outdated expectation

**Investigate** (the analyzer regressed):
- No intentional code change, but output shifted
- The new output is missing a detection that should be there
- A BUGFIX assertion failed (the fixed bug returned)

**Decision tree** (from RUNBOOK Checklist 12):
1. Was the analyzer recently changed? → Check if new output is correct
2. Is it a SEED assertion? → Count may have shifted within old tolerance
3. Is it a STRUCT assertion? → Check if the ref still exists in output
4. Is it a BUGFIX assertion? → Always a regression — the fixed bug returned

**Key principle:** Re-seed ONLY after confirming the new output is correct. Never
re-seed to silence a failure you don't understand.

---

## Assertion type roles

Each assertion type serves a different purpose in the testing pyramid:

### SEED-* (safety net)

Generated by `seed.py`. Broad, count-based assertions with tolerance bands.
Example: "Component count 42-52" for a file with 47 components.

**Purpose:** Catch large structural changes. If component count drops from 47 to 12,
something is very wrong.

**Limitation:** Coarse. A tolerance of ±10% means up to 4 components can disappear
undetected. For large counts (>200), tolerance is tightened to ±3%.

**When they fail:** Usually means the analyzer's output structure changed (new section
added, count shifted). Almost always a re-seed situation after verification.

### STRUCT-* (precision)

Generated by `seed_structural.py`. Per-ref assertions for specific component
references in specific detectors.

**Purpose:** Catch individual detection drops. If R15 was in voltage_dividers and now
it isn't, STRUCT catches it even if the count is still within SEED tolerance.

**When they fail:** Either the component was reclassified to a different detector
(review needed) or the detection was legitimately dropped (regression).

### FND-* (semantic)

Promoted from Layer 3 findings via `findings.py promote`. Encode domain knowledge
from LLM review.

**Purpose:** Preserve insights that can't be auto-generated. "This opamp is in
inverting configuration with gain=-10" is knowledge from reading the schematic,
not from counting components.

**When they fail:** The analyzer lost a capability it previously had. Investigate.

### BUGFIX-* (regression guard)

Generated from `bugfix_registry.json` via `generate_bugfix_assertions.py`. Each is
tied to a specific KH-* issue.

**Purpose:** Prevent fixed bugs from returning. If KH-015 fixed legacy .sch parsing,
the BUGFIX assertion ensures signal_analysis still exists on that file.

**When they fail:** Always investigate. The bug returned. File a new KH-* issue
referencing the original.

### NEG-* (false-positive prevention)

Generated by `seed_negative.py` from Layer 3 "incorrect" findings.

**Purpose:** Assert that known false positives don't reappear. If R30 was incorrectly
detected as a voltage divider (it's actually current sense), the NEG assertion
ensures it stays out.

**When they fail:** The false positive returned. The fix was undone or bypassed.

### v1.3 correctness layers

These are new evidence types being added in v1.3. Unlike SEED/STRUCT assertions, they test against sources of truth that are independent of the analyzer's own prior output. Each has narrow scope and specific limitations — none of them verify correctness of the full 5,822-repo corpus, and the gaps matter.

See [methodology.md](methodology.md) § "Toward correctness" for the framing and the explicit list of what v1.3 does NOT achieve.

#### Parser verification

Generated by `validate/verify_parser.py` (v1.3+). An independent S-expression reader walks the raw `.kicad_sch`/`.kicad_pcb` source and extracts component references, nets, labels, and power symbols. Those are compared exactly against the analyzer's output.

**What it catches:** Extraction bugs — if the analyzer reports 142 components but the independent reader finds 143, the analyzer is missing one.

**What it does NOT catch:** Interpretation bugs. If the parser correctly extracts R15 but the voltage-divider detector misclassifies its role, parser verification passes and the semantic error continues downstream.

**When it fails:** Always investigate. The parser is a foundation layer; parser bugs corrupt every downstream detection.

#### Synthetic fixtures (tests/fixtures/detectors/)

Hand-built `.kicad_sch` files with circuits whose correct answer is known by construction. Organized by detector family × bucket: `voltage_divider/{positive,negative,near_miss,regressions}/`, same for `rc_filter`, `power_regulator`, `protection_device`, `crystal_circuit`. Initial target: ~30-60 fixtures across 5 detector families.

**What it catches:** Detector semantic bugs on deterministic inputs. A positive case asserts "this IS a voltage divider with ratio 0.5". A negative case asserts "this is NOT a voltage divider — it's a pull-up". A near-miss asserts the detector degrades gracefully on ambiguous input.

**What it does NOT catch:** Real-world edge cases that don't appear in hand-built fixtures. Messy library substitutions, hierarchical cross-sheet references, unusual naming conventions — a detector can pass every synthetic fixture and still fail on the first real project in an unfamiliar domain.

**When it fails:** The detector is wrong on a known-answer case. Investigate before any re-seed of corpus assertions.

#### Metamorphic tests

Variants of each synthetic fixture with controlled transformations. Invariance transforms (reorder symbol blocks, rename unused nets, add floating components) should produce identical output. Covariance transforms (change R2 from 10k to 20k, swap opamp inputs) should produce specific output deltas.

**What it catches:** Detectors that pattern-match on cosmetic features instead of reading the circuit. A detector that "works" on every corpus file can still be causally disconnected from its input — metamorphic tests reveal that.

**What it does NOT catch:** Bugs that only manifest on real-world structural complexity. v1.3 metamorphic tests run on synthetic fixtures, not on real corpus files. A detector can pass every metamorphic test on synthetic inputs and still be insensitive on real layouts. (Full metamorphic testing on real corpus files is a v1.4 candidate — it requires a safe KiCad file rewriter that does not exist yet.)

**When it fails:** The detector is sensitive to something it shouldn't be (invariance failure) or insensitive to something it should be (covariance failure). Both are bugs.

#### Gold-standard tier (reference_gold/)

Ten initial hand-reviewed real designs with structured claim files. Each claim has explicit `subject_refs`, `expected_relation`, and `evidence` citations (datasheet pages, schematic inspection notes). Reviewer and review date are recorded. Target growth: 1-3 new cases per month.

**What it catches:** Drift from specific reviewed-correct claims on specific real designs. The only v1.3 layer that tests against external truth on real (non-synthetic) files.

**What it does NOT catch:** Anything outside the ~10 curated cases. At a growth rate of 1-3/month, meaningful corpus coverage is years away. The gold tier anchors *specific* claims, not general correctness — and every claim inherits the fallibility of the reviewer who wrote it. There is no second reviewer.

**When it fails:** Either the analyzer drifted from a reviewed-correct state (regression) or the reviewer's original judgment was wrong. Investigate carefully; don't re-seed automatically.

#### Property invariants

Universal structural rules that should hold for every analyzer output, not per-file seeded values. Generated by `validate/invariants.py` (v1.3+). Examples: `voltage_dividers[].ratio ∈ (0, 1)`, `rc_filters[].cutoff_hz > 0` when R > 0 and C > 0, no duplicate refs in `components[]`.

**What it catches:** Structural shape violations that SEED/STRUCT assertions miss because SEED/STRUCT encode current behavior, including wrong current behavior.

**What it does NOT catch:** Content errors within valid shape. A detector that reports a consistent but wrong `ratio = 0.5` for every divider passes every invariant — the shape is fine, the value is just wrong.

**When they fail:** Always a bug. Invariants are universal — if one fails, something is fundamentally wrong with the output shape.

### Evidence provenance

A transverse v1.3 addition: every assertion, finding, and bugfix entry carries an `evidence_source` field: one of `human_review`, `datasheet`, `spice`, `cross_analyzer`, `corpus_heuristic`, `auto_seeded`. Reports and trust-weighting use this to distinguish strong claims (human-reviewed gold fact) from weak claims (auto-seeded count assertion).

A 100% pass rate with 99% auto-seeded evidence is a weaker signal than 95% pass rate with 80% human-reviewed evidence. Provenance tracking makes that visible in aggregate metrics, but it does not change what any individual check verifies — a wrong claim with `evidence_source: human_review` is still wrong, just tagged as such.

---

## The false positive problem

False positives are the dominant failure mode for circuit analysis. The analyzer
looks at a resistor network and guesses its function — but:

- A voltage divider in an opamp feedback path isn't a standalone voltage divider
- An RC filter that's actually decoupling for an IC isn't a signal filter
- Two resistors near a connector might be termination, not a divider
- A current sense resistor shares topology with a voltage divider

False positives are worse than missed detections because they actively mislead the
designer. A missed RC filter is a gap in the report; a false RC filter at 1.2MHz
sends the designer chasing a phantom problem.

**Defenses:**
1. `not_contains_match` assertions (NEG-*) encode known false positive patterns
2. Layer 3 "incorrect" findings document specific false positives per repo
3. The `seed_negative.py` generator scans findings for false positive keywords
4. Mutation testing (`mutation_test.py`) verifies assertions catch injected errors

---

## Constants and equations as hallucination vectors

The analyzers contain 335 hardcoded constants and 86 engineering equations. These are
the highest-risk area for LLM hallucination.

**Why constants are dangerous:** An LLM adding a Vref value of 0.6V for the TPS5430
(actual: 1.221V) will silently produce wrong voltage calculations for every design
using that part. The error propagates invisibly because the output format is correct —
only the number is wrong.

**The verification hierarchy:**

| Source | Reliability | Example |
|--------|-------------|---------|
| Manufacturer datasheet | Highest | "TI TPS5430 datasheet SLVS632L, Table 7.5" |
| Distributor parametric data | High | "DigiKey parametric data for TPS5430" |
| Industry standard | High | "IPC-2221B Table 6-1" |
| Textbook | High | "Ott, EMC Engineering (Wiley 2009) Eq. 6.4" |
| Application note | Medium | "Murata MLCC app note, Table 3" |
| Self-evident physics | Auto-verified | "Ohm's law: V = IR" |
| Engineering heuristic | Low | "Empirical threshold from corpus tuning" |

**Never accept:** LLM training data, "common knowledge", values without citation,
round numbers that look plausible but have no source.

**The audit pipeline:**
1. `audit_constants.py scan` — AST-scan all analyzer scripts for constants
2. `audit_constants.py corpus` — cross-reference against 5,822 repos
3. `verify_constants_online.py` — spot-check against DigiKey parametric data
4. `audit_equations.py scan` — verify EQ-NNN tags and function body hashes

**Rule:** If a constant cannot be verified from an authoritative source, remove it
and use a conservative default. Better to not estimate than to estimate wrong.

---

## The corpus as statistical authority

5,822 repos provide empirical validation that no manual test suite can match:

- A constant exercised by 500 repos is highly trustworthy (if verified)
- A constant exercised by 3 repos may be overfitted
- A detector with 1,895 corpus hits (rc_filter) has broad validation
- A detector with 10 corpus hits (bms_systems) has narrow validation

The coverage map (`coverage_detector_map.py`) shows this distribution. Detectors
with high corpus hits but low assertion counts are under-tested. Detectors with
low corpus hits but verified constants are high-quality but narrow.

**Corpus-derived insights:**
- 91.9% cross-analyzer agreement (schematic ↔ PCB ↔ EMC ↔ SPICE) across 97,012 checks
- 100% SPICE cross-validation agreement on 145,758 simulations
- 84.8% SPICE pass rate, 12.1% warn, 0.06% fail
- 99.6% tolerance parsing coverage
- 100% mutation catch rate on tested repos

These metrics are the real quality indicators — not the assertion pass rate.

---

## When to add new assertions

Add assertions when:
1. A bug is fixed → BUGFIX-* assertion to prevent regression + minimal reproducer fixture in `tests/fixtures/regressions/`
2. A Layer 3 review identifies something correct → FND-* assertion (use structured fields where possible, not free-text)
3. A Layer 3 review identifies a false positive → NEG-* assertion
4. A new analyzer feature is added → SEED + STRUCT for new output sections, plus synthetic fixtures if it's a new detector family
5. Schema drift detects new fields → DRIFT-* assertions via `auto-seed`
6. A structural invariant can be stated universally (bounds, existence) → property invariant in `validate/invariants.py`
7. A new detector family is added → synthetic fixtures under `tests/fixtures/detectors/{family}/` with positive/negative/near_miss/regressions buckets
8. A hand-reviewed real design matches analyzer output on an important claim → gold-standard entry in `reference_gold/`

Don't add assertions:
- For things that are already covered (check `coverage_detector_map.py` first)
- For exact values that are likely to change (use tolerance ranges)
- For aspirational goals that aren't implemented yet (use `aspirational: true`)
- By copying from one repo to another (assertions are per-project, not universal)
- For property invariants: per-file — invariants are universal, they go in `validate/invariants.py`

---

## Summary: what the numbers mean

None of these metrics individually prove the analyzer is correct. They measure specific aspects of output stability and, for the v1.3+ rows, specific kinds of independent evidence on narrow curated slices of the corpus. Read them together, not as standalone verdicts.

| Metric | Good | Bad | Action |
|--------|------|-----|--------|
| Assertion pass rate (consistency) | 100% after fresh seed | <99% after code change | Investigate failures; consistency not correctness |
| Mutation catch rate | >95% | <80% | Add structural assertions |
| Cross-validation agreement | >90% | <85% | Investigate mismatches |
| Constants unverified | 0 critical-risk | Any critical-risk | Verify or remove |
| Staleness | 0 stale files | >100 stale | Re-seed affected types |
| Finding drift | <10% items drifted | >50% items drifted | Refresh findings |
| Parser verification (v1.3+, extraction only) | 100% exact match on full corpus | Any mismatches | Investigate as KH-* parser bug; does not cover interpretation |
| Gold benchmark pass rate (v1.3+, ~10 curated cases) | 100% on current curated set | Any failures | Investigate — narrow coverage, reviewer-limited |
| Metamorphic test suite (v1.3+, synthetic only) | All invariance/covariance pass on fixtures | Any failure | Detector lacks causal sensitivity on synthetic inputs — real-corpus behavior untested |
| Property invariants (v1.3+, shape only) | 100% across full corpus | Any failure | Output shape violation — does not verify content correctness |

The v1.3+ metrics give independent evidence on specific slices, not corpus-wide correctness. See [methodology.md](methodology.md) § "Toward correctness" for the explicit limitations of each layer.
