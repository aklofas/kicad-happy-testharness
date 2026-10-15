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

Counts may only **shrink**. A count that grows fails the check. A shrink must be
committed together with the product change that removed the sites.

## Legacy untagged sites

89 of 108 emit sites at `6a91aaa` carry no `schema_era`. They are recorded in the
coverage baseline and tolerated; a **new** emit site without `schema_era` is reported
and must be either tagged or added to the changed-detector registry review.

## Coverage baseline

`reference/scan_coverage_baseline.json` records, at a product SHA, every file
scanned, every (detector, rule_id) emit-site count, every `EQ-nnn` id and every
constant `(file, scope, name)`. `check` fails when any covered set shrinks (a lost
file, site, equation or constant) unless the run is re-baselined with
`--accept-baseline`, whose diff is the review artifact.

## What is frozen regardless of policy

Emitted `detector` strings (including `emc_<category>`), rule IDs, script paths.
Changing how a detector string is *derived* is allowed only if the emitted value is
byte-identical.
