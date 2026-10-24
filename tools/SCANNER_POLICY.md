# Literal-tag scan policy (harness → product CONTRIBUTING)

Version 1 — measured at product `6a91aaa`, 2026-10-15. Owner: test harness
(`tools/source_scan.py`). The main repo copies this section into CONTRIBUTING.

## What the harness scans

Every `*.py` under `skills/*/scripts/**` and `skills/*/*/scripts/**`
(recursive; `__pycache__` skipped), identified by its **root-relative POSIX path**.
Scanners read source with `ast` only; they never import or `eval` product code.

## What counts as a finding emit site

A call is an emit site when either holds:

1. its callee's last name segment is `make_finding` or `_make_finding`, or
2. it carries all three keywords `detector=`, `rule_id=`, `schema_era=`.

## What an emit site must look like (new or migrated code)

- `detector=` **string literal** (the emitted detector string — frozen for v3)
- `rule_id=` **string literal**
- `schema_era=` **string literal** when the finding belongs to a changed-detector set

Anything else — a variable, an f-string, an attribute, a positional shape — is
*unresolved* and fails `python3 tools/source_scan.py check` unless it is one of the
grandfathered exceptions below.

## Grandfathered exceptions (`tools/scan_exceptions.json`)

| id | shape | count @6a91aaa | retire by |
|---|---|---:|---|
| emc-positional-make-finding | `_make_finding('<category>', '<sev>', '<RULE>', ...)` in `skills/emc/scripts/emc_rules.py`; detector derived as `emc_<category>` | 53 | EMC reshape round |
| det-enum-shorted-two-pin | `detector=Det.SHORTED_TWO_PIN` in `skills/kicad/scripts/signal_detectors.py`; resolved from the literal `Det` class body | 2 | first SP-001 touch |
| usb-compliance-rule-id-loop | `rule_id=_rid` loop in `skills/kicad/scripts/analyze_schematic.py` | 1 | first UC-00x touch |

Counts may only **shrink**, and the file must always state the exact count. A count
that grows fails the check; so does a ledger entry that now matches fewer sites than
its recorded count (`shrank: matched n < recorded count`) or zero sites (stale entry).
A shrink is therefore committed together with the product change that removed the
sites, in the same commit.

## Legacy untagged sites

At `6a91aaa` the walker finds 108 emit sites; 89 of them carry no `schema_era`:

- **35 resolved sites** (literal `detector` + `rule_id`, including the 2
  `Det.SHORTED_TWO_PIN` enum sites) are tracked per `detector|rule_id` in the
  baseline's `untagged_era_sites` map (`untagged_era_total` = 35).
- **54 unresolved sites** (53 positional EMC + 1 UC loop) are absorbed by the
  exception ledger above and tracked by its exact counts, not by the untagged map.

They are tolerated. A **new** untagged site under a `detector|rule_id` whose untagged
count grows fails the check (`new_untagged_era`), even when another rule's site gained
a tag in the same round; it must be tagged or go through the changed-detector
registry review.

## Coverage baseline

`reference/scan_coverage_baseline.json` (snapshot_version 2) records, at a product
SHA, every file scanned, every (detector, rule_id) emit-site count, the per-key
untagged-era counts, every `EQ-nnn` id and every constant `(file, scope, name)`.
`check` fails when any covered set shrinks (a lost file, site, equation or constant),
an untagged count grows, unless the run is
re-baselined with `--accept-baseline`, whose diff is the review artifact.

**Ratchet on growth.** When coverage grows (new files, site keys, EQ ids or
constants, or an untagged count drops), `check` stays CLEAN but prints
`coverage grew: …`. Run `check --accept-baseline` and commit the rewritten baseline
in the same round, so the next round cannot silently drop what this one added.

**Constants and EQ ids come from the same walk as `files`.** `validate/audit_constants.py`
and `validate/audit_equations.py` consume `source_scan.iter_product_sources`, so a
constant or `EQ-nnn` tag anywhere under `skills/**/scripts/**` (kicad, kicad/review,
spice, emc, datasheets, bom and the distributor skills) enters both registries and the
baseline (TH-066; before it the audit tools walked three roots, 58 of 90 files).

## What is frozen regardless of policy

Emitted `detector` strings (including `emc_<category>`), rule IDs, script paths.
Changing how a detector string is *derived* is allowed only if the emitted value is
byte-identical.
