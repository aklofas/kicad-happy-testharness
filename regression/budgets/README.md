# Budget records

A budget is the **evaluable** list of output changes a product round is allowed to make.
`regression/field_compare.evaluate_budget` classifies every strict-mode delta against the
budget's classes; a delta no class claims is a **residual**. The round is clean only when
the residuals do not exceed `unexplained_deltas_allowed`, the units missing from one side
do not exceed `unexplained_missing_units_allowed`, and no class is over budget. Set both
allowances to 0 for a round that must explain every delta (every tracked budget does);
only the product handoff can authorize a nonzero allowance, never as a way to silence an
unexplained change. One allowed class on a board never excuses an unrelated delta on the
same board.

File: `regression/budgets/<budget_id>.json` (tracked). Shape: `budget.schema.json`. The
loader requires these top-level keys (non-negative integers for the two allowances); the
optional `baseline_sha` / `candidate_sha` / `normalization_policy` are checked against the
run when present:

```json
{
  "budget_id": "example",
  "classes": [],
  "unexplained_deltas_allowed": 0,
  "unexplained_missing_units_allowed": 0,
  "relock": false
}
```

Per class, only `id` and `path_glob` are required (RFC 6901 pointer with `*` = one
segment, `**` = rest); the rest are optional selectors: `analyzer`, `op` (subset of the comparator ops: added/removed/changed/type_changed/
key_order/bytes/lexical_numeric), `where` (`rule_id`/`detector` lists resolved from the
finding at that index on either side; only valid under `/findings/*` and `/assessments/*`),
`direction` (`any|up|down|none`, severity changes only), `value_relation` (`any|equal`),
`unit_bound` (`{"max_units": N}`), `predicate` (`"module:function"` — `module` is a bare name imported as
`regression.budgets.<module>`, the function takes `(delta, a_doc, b_doc)`; the module lives in
this directory and is tracked), `evidence`, `expected_magnitude` (non-negative int: the
number of deltas the product expects the class to claim).

`direction` + `expected_magnitude` are stated by the product handoff; a class claiming more
than 2× its `expected_magnitude` is `over_budget` and fails the round until re-budgeted.

The historical walkers under `results/*/walker_*.py` were ad hoc predicates; a predicate
that matters now lives here, versioned with the budget that uses it.
