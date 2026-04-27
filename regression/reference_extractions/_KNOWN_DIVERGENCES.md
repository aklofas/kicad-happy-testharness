# Known divergences in v1.4 gold set

Narrative context for INFO-class currency-check findings. Each entry maps to a
schema or convention awkwardness flagged during Phase 3b that didn't gate
acceptance but is candidate for v1.5 cleanup. When `check_gold_currency.py`
reports a minor schema bump or convention shift, look here first to understand
what the bump means and whether it should drive a re-curation now.

## `mcu.core_speed_max` bare-scalar shape

**Symptom:** `mcu.core_speed_max` ships as a bare scalar int (e.g. `72000000`)
rather than a SpecValue dict like `{"max": 72e6, "unit": "Hz"}`. Awkward
because the field name carries `_max` semantics but the value has no unit
attached.

**Currency-check signal:** if `mcu` schema reshapes this to a SpecValue,
currency check reports INFO. Re-curation recommended at that point — the new
shape will lift the unit explicitly.

**Source:** Phase 3b session 9, STM32F103C8T6 vector realignment (LOG #62).

## opamp/mcu cross-category TOPR-vs-T_A divergence

**Symptom:** opamp schema places operating-temp range `TOPR` in
`absolute_max`; mcu schema places it as `T_A` in `recommended_operating`.
Both are operating-temp range fields; cross-category convention divergence
makes uniform consumer-API access awkward.

**Currency-check signal:** if either schema realigns to share a
`recommended_operating.TOPR` (or `absolute_max.TOPR`) convention, currency
check reports INFO. Re-curation recommended.

**Source:** Phase 3b session 9, LM358 vector realignment (LOG #62).

## `body_mm` shape — already canonical

**Symptom:** Originally proposed as scalar `body_mm`; revised in Phase 3b
session 9 to nested `{length_mm, width_mm, height_mm}` (option A — main-repo
LOG #59). Already canonical across all 5 Phase 3b categories.

**Currency-check signal:** none active. Listed for completeness; if a future
shape variant emerges (e.g., per-orientation dimensions, BGA pitch separate
from body), bump entry to active divergence.

**Source:** Phase 3b session 9, ABM8G crystal vector (LOG #59, #60).

## `datasheet_lookup.sanitize_mpn` dot-stripping (consumer-API bug)

**Symptom:** v1.3 consumer-API `datasheet_lookup.sanitize_mpn` still uses
dot-replacing regex; cache files for crystal-style MPNs preserve dots
(e.g. `ABM8G-106-12.000MHZ-T`). Detector code calling `lookup()` won't find
the cache file.

**Currency-check signal:** none — this is a detector-side path-realignment
bug, NOT a cache-shape change. Listed here so reviewers don't conflate the
fix with a schema bump.

**Resolution:** v1.5 consumer-API hardening item — align
`datasheet_lookup.sanitize_mpn` with the verify flag-mode regex (or remove
sanitization entirely since `merge_results.py` writes literal MPN).

**Source:** Phase 3b session 9, ABM8G crystal gate run (LOG #62).
