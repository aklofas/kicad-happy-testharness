# Normalization policies

A policy names the **exact leaves** of an analyzer envelope that are allowed to differ
between two runs of identical code (run ids, elapsed time, absolute path prefixes). The
strict comparator (`regression/field_compare.py`) masks only these leaves, and even then
checks each masked leaf's shape and linkage. Whole blocks (`/inputs`,
`/capability_mode_ref`) are never masked: a `pointer` that lands on a dict or list is a
policy violation.

Leaf entry keys:

| key | meaning |
|---|---|
| `pointer` | absolute RFC 6901 pointer to one leaf |
| `pointer_glob` | pointer with `*` matching exactly one path segment |
| `shape` | regex the leaf must match on both sides, or `number` / `iso8601` / `run_id` |
| `equals` | absolute pointer that must hold the same value on the same side |
| `sha256_of` | sibling key holding a file path; the leaf must equal that file's sha256 |
| `note` | free-text scope note, ignored by the comparator |
| `rewrite` | `strip_root_prefix` (string leaf) or `strip_root_prefix_keys` (dict keys) using the root prefixes from the run manifests |

Changing the leaf list is a **new policy version** (`volatile-leaves-v2.json`); the name
travels in every field report and per-round record. The list is to be confirmed (pending) by the plan-6 A/A run
at product 6a91aaa: a leaf that differs in A/A and is not listed here is a determinism
bug to file, not a mask to add silently.

## Masking semantics

A leaf is masked only when it is present on BOTH sides. Present on one side only is a
normal added/removed delta (absent != null applies). Absent on both sides is a no-op.
Some leaves exist only on some analyzer types (`/elapsed_s`: cross_analysis/emc/thermal;
`/inputs/upstream_artifacts/...`: chained analyzers), so absence is expected.

`root_prefixes` is either a list of strings or `"from_manifest"` (prefixes are read from
the run manifests; `Policy.root_prefixes_from_manifest` is then True).

The `equals` linkage on `/capability_mode_ref/run_id` (equal to `/inputs/run_id`) holds on
all six envelope types (reviewer-verified).
