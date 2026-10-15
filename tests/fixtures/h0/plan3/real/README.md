# Real snap pairs from results/v22x_pr44_gate (harness 7abf547, product 3cf837b→788649f)

Copied 2026-10-15 from the only retained gate snap trees. `identical/` is a pair whose
only leaf differences are the two run-id leaves; `rail_flip/` is one PR #44
`is_power_net_name` unit (12V reclassified signal→power). Used by
`tests/test_field_compare_real_pr44.py` as the comparator's real-shape check. Do not edit
the snap.json files; if they ever need refreshing, copy from a fresh gate tree and update
this README and the budget's SHAs.

`pr44_rail_flip_budget.json` is a FIXTURE budget: `rail-flip-finding` claims any field of any
LB-001/RS-001 finding and `rail-flip-audience` claims all of `/audience_summary/**`. That
breadth is acceptable only because the pair holds one such finding; a real gate budget must be
narrower (per-net `where`, explicit `op`).

`chained/` (copied 2026-10-15, same gate, `v131`→`baseline`, `v14`→`candidate`, byte-identical
including the `capability_mode.json` sidecars) is one project, `0Prashant/Kicad/BAsanta_maga`,
with all five units: schematic, pcb and the three chained analyzers (emc, thermal,
cross_analysis). Its schematic and pcb pairs are strict-clean, so the whole tree is clean once
the chained `/inputs/source_hashes` values are verified and masked (C1). The chained snaps record
the original absolute gate paths; `tests/test_field_compare_real_chained.py` copies the tree to
a tmp gate and rewrites only those path strings to the tmp slot roots. Upstream bytes are never
touched, so the recorded sha256 values stay valid.
