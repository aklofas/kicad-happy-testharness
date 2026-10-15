# Budget records

A budget is the **evaluable** list of output changes a product round is allowed to make.
`regression/field_compare.evaluate_budget` classifies every strict-mode delta against the
budget's classes; a delta no class claims is a **residual**, and a residual means the
round is not clean. One allowed class on a board never excuses an unrelated delta on the
same board.

File: `regression/budgets/<budget_id>.json` (tracked). Shape: `budget.schema.json`.
Per class: `id`, `path_glob` (RFC 6901 pointer with `*` = one segment, `**` = rest),
optional `analyzer`, `op` (subset of the comparator ops: added/removed/changed/type_changed/
key_order/bytes/lexical_numeric), `where` (`rule_id`/`detector` lists resolved from the
finding at that index on either side; only valid under `/findings/*` and `/assessments/*`),
`direction` (`any|up|down|none`, severity changes only), `value_relation` (`any|equal`),
`unit_bound` (`{"max_units": N}`), `predicate` (`"module:function"` — `module` is a bare name imported as
`regression.budgets.<module>`, the function takes `(delta, a_doc, b_doc)`; the module lives in
this directory and is tracked), `evidence`.

The historical walkers under `results/*/walker_*.py` were ad hoc predicates; a predicate
that matters now lives here, versioned with the budget that uses it.
