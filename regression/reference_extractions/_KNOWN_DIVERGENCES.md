# Known divergences in v1.4 gold set

Narrative context for INFO-class currency-check findings. Each entry maps to a
schema or convention awkwardness found while curating the gold set that did not
gate acceptance but is a candidate for cleanup. When `check_gold_currency.py`
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

**Source:** STM32F103C8T6 sanity-vector realignment.

## opamp/mcu cross-category TOPR-vs-T_A divergence

**Symptom:** opamp schema places operating-temp range `TOPR` in
`absolute_max`; mcu schema places it as `T_A` in `recommended_operating`.
Both are operating-temp range fields; cross-category convention divergence
makes uniform consumer-API access awkward.

**Currency-check signal:** if either schema realigns to share a
`recommended_operating.TOPR` (or `absolute_max.TOPR`) convention, currency
check reports INFO. Re-curation recommended.

**Source:** LM358 sanity-vector realignment.

## `body_mm` shape — already canonical

**Canonical shape:** `body_mm` is a nested object with `length`, `width` and
`height`, each in millimeters (originally proposed as a scalar). The base, opamp
and mcu schemas reject additional keys such as `length_mm`.

**Currency-check signal:** none active. Listed for completeness; if a future
shape variant emerges (e.g., per-orientation dimensions, BGA pitch separate
from body), bump entry to active divergence.

**Source:** ABM8G crystal sanity vector.

## `datasheet_lookup.sanitize_mpn` dot-stripping (consumer-API bug)

**Symptom (historical):** the old consumer-API `sanitize_mpn` replaced dots,
while cache files for crystal-style MPNs preserve them (e.g.
`ABM8G-106-12.000MHZ-T`), so a detector lookup missed the cache file.

**Currency-check signal:** none — this was a filename-resolution bug, NOT a
cache-shape change. Listed here so reviewers don't conflate it with a schema
bump.

**Resolution:** resolved. The consumer now lives in
`skills/datasheets/datasheet_types/cache_reader.py`, whose `sanitize_mpn`
preserves dots and hyphens, so `ABM8G-106-12.000MHZ-T` resolves to a cache
filename containing the same MPN. If that lookup fails, inspect cache presence
and validity rather than applying the former dot-stripping workaround.

**Source:** ABM8G crystal gate run.
