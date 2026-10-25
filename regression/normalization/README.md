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
| `rewrite` | `strip_root_prefix` (string leaf) or `strip_root_prefix_keys` (dict keys), using the root prefixes the comparator supplies (see below); a prefix strips only on a path boundary (`s == root` or `s` starts with `root + "/"`) |
| `verify_values` | `sha256_of_key`, only with `strip_root_prefix_keys`: a value whose key was actually stripped (lay under a slot root) is masked only if it matches `^[0-9a-f]{64}$` AND equals the sha256 of the file the unstripped key names, checked per side; a failure is a policy violation. Values whose keys lie outside the slot roots (repo input files) stay compared |

Changing the leaf list is a **new policy version** (`volatile-leaves-v2.json`); the name
travels in every field report and per-round record. Validate the policy with an A/A
comparison (two runs of identical code): an unlisted leaf that differs between them is a
determinism bug to investigate and file, not a mask to add silently.

## Masking semantics

A leaf is masked only when it is present on BOTH sides. Present on one side only is a
normal added/removed delta (absent != null applies). Absent on both sides is a no-op.
Some leaves exist only on some analyzer types (`/elapsed_s`: cross_analysis/emc/thermal;
`/inputs/upstream_artifacts/...`: chained analyzers), so absence is expected.

`root_prefixes` is either a list of strings or `"from_manifest"`. Despite the name, nothing
reads a manifest: `"from_manifest"` means the caller supplies the prefixes, and
`compare_trees` always passes the two slot roots it compares, each in its as-given
(absolute, symlinks kept) and resolved forms. The only path leaves that need stripping
point into the slot trees; product paths never appear in envelopes.
`Policy.root_prefixes_from_manifest` is then True, and a rewrite with no supplied prefixes
is a policy violation.

Re-evaluating a historical tree that was MOVED after the gate ran breaks prefix stripping,
`sha256_of` and `verify_values`, because the envelopes hold the old absolute paths.

## Compatibility of policy versions

`volatile-leaves-v1` gained `verify_values: sha256_of_key` on `/inputs/source_hashes`
(chained emc/thermal/cross_analysis envelopes key their upstream snaps under the slot
roots, and those values differ on every run because each upstream snap embeds its own
run id; without the mask every chained unit failed strict, A/A included). The file was
edited in place rather than bumped to v2 because no per-round record had consumed v1
yet. Once a policy is used in a recorded run, any change to its leaf list requires a new
version.

The `equals` linkage on `/capability_mode_ref/run_id` (equal to `/inputs/run_id`) holds on
all six envelope types (reviewer-verified).
