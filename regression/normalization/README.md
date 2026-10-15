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
| `rewrite` | `strip_root_prefix` (string leaf) or `strip_root_prefix_keys` (dict keys) using the root prefixes from the run manifests |

Changing the leaf list is a **new policy version** (`volatile-leaves-v2.json`); the name
travels in every field report and per-round record. The list is confirmed by an A/A run
at the arc baseline: a leaf that differs in A/A and is not listed here is a determinism
bug to file, not a mask to add silently.
