# kicad-happy Test Harness

Test harness for validating [kicad-happy](https://github.com/aklofas/kicad-happy) analyzers against a corpus of 1,100+ real-world open-source KiCad projects.

## Quick start

```bash
# 1. Clone the kicad-happy repo alongside this one (or set KICAD_HAPPY_DIR)
git clone <kicad-happy-url> ../kicad-happy

# 2. Clone test repos
python3 checkout.py

# 3. Discover KiCad files
python3 discover.py

# 4. Run analyzers (use --jobs for parallelism, --repo to target one repo)
python3 run/run_schematic.py --jobs 4
python3 run/run_pcb.py --jobs 4
python3 run/run_gerbers.py --jobs 4

# 5. Snapshot and compare baselines
python3 regression/snapshot.py --repo {repo}
python3 regression/compare.py --repo {repo}

# 6. Run assertions
python3 regression/run_checks.py --repo {repo}

# 7. Validate outputs
python3 validate/validate_outputs.py --repo {repo}

# 8. Promote improvements
python3 regression/promote.py --repo {repo} --apply
```

### Requirements

- **Python 3.8+** (stdlib only -- no external dependencies for core scripts)
- **Git** (for cloning test repos)

### Finding kicad-happy

All scripts resolve the kicad-happy analyzer location in this order:

1. `KICAD_HAPPY_DIR` environment variable
2. `../kicad-happy` (sibling directory)

```bash
export KICAD_HAPPY_DIR=/path/to/kicad-happy   # if not at ../kicad-happy
```

## Analyzers under test

| Analyzer | Input | Description |
|----------|-------|-------------|
| `analyze_schematic.py` | `.kicad_sch`, `.sch` | Components, nets, signal paths, BOM, design analysis |
| `analyze_pcb.py` | `.kicad_pcb` | Footprints, tracks, vias, zones, DFM analysis |
| `analyze_gerbers.py` | Gerber directories | Layer completeness, drill alignment |

All analyzers are pure Python 3.8+ stdlib. They produce JSON output and support KiCad versions 5 through 9.

**Note on `.sch` files**: `discover.py` filters legacy `.sch` files by checking the header for "EESchema" (KiCad 5 signature) to exclude Eagle XML/binary `.sch` files.

## Regression testing (3-layer approach)

All operations are per-repo. Data is organized by `reference/{repo}/{project}/` where project is the subpath to the KiCad project directory with `/` encoded as `_`.

### Layer 1: Baselines

Compact snapshots of analyzer outputs, checked into git. Any machine can diff against them.

```bash
python3 regression/snapshot.py --repo {repo}
python3 regression/compare.py --repo {repo}
python3 regression/compare.py --all --only-changes
```

### Layer 2: Assertions

Machine-checkable facts about what an analyzer should find in a specific file. Stored in `reference/{repo}/{project}/assertions/`. Operators include `range`, `min_count`, `equals`, `exists`, `contains_match`, etc.

```bash
python3 regression/run_checks.py --repo {repo}
python3 regression/seed.py --repo {repo}
```

### Layer 3: LLM review

Review packets pair source files with analyzer output summaries for independent quality verification by Claude.

```bash
python3 regression/packet.py --strategy random --count 5
python3 regression/packet.py --strategy changed --repo {repo}

python3 regression/findings.py list
python3 regression/findings.py stats
python3 regression/findings.py render
python3 regression/findings.py promote FND-00000001
```

### How the layers connect

```
findings --> (promote) --> assertions --> (run_checks) --> regression caught
    ^                                                           |
    +---------- drift.py <-- (re-check against outputs) --------+
```

- **Baselines** catch broad structural changes (new/removed sections, count shifts)
- **Assertions** catch specific regressions (a known-good detection disappearing)
- **Findings** capture context that can't be automated (why something is wrong, what's missing)

`drift.py` closes the loop by re-checking findings against current outputs, surfacing regressions and improvements without manual re-review.

```bash
python3 regression/drift.py --repo {repo}
```

### Promoting improvements

```bash
python3 regression/promote.py --repo {repo}          # dry run
python3 regression/promote.py --repo {repo} --apply   # promote
```

## Constants audit

The analyzer scripts contain 180+ hardcoded constants: lookup tables, keyword lists, numeric thresholds, and regex patterns. `audit_constants.py` scans analyzer source using Python AST, builds a registry of all constants, and tracks verification status.

```bash
python3 validate/audit_constants.py scan                # scan scripts, update registry
python3 validate/audit_constants.py scan --diff          # show what changed since last scan

python3 validate/audit_constants.py list                 # all constants
python3 validate/audit_constants.py list --unverified    # unverified only
python3 validate/audit_constants.py list --risk critical  # critical risk constants
python3 validate/audit_constants.py list --risk high      # high+ risk constants
python3 validate/audit_constants.py list --category datasheet_lookup
python3 validate/audit_constants.py show CONST-001       # detail view

python3 validate/audit_constants.py verify CONST-001 --source "LM317 datasheet SNVS774Q"
python3 validate/audit_constants.py verify CONST-001 --entry TPS5430 --source "datasheet SLVS632L"

python3 validate/audit_constants.py corpus              # cross-reference against outputs
python3 validate/audit_constants.py stats                # summary breakdown
python3 validate/audit_constants.py report               # full text report
python3 validate/audit_constants.py render               # generate constants_registry.md
```

### Two-dimensional risk scoring

Each constant is scored on two independent axes:

- **Impact** (0.0-1.0) -- How bad is it if this constant is wrong. A hallucinated Vref value silently produces incorrect voltage calculations; a wrong keyword list causes misclassification.
- **Overfit** (0.0-1.0) -- Whether this constant pulls its weight across the corpus, or was added to fix one project and doesn't generalize. Starts with structural heuristics (inline definitions, small local lists), then `corpus` fills in real data from analyzer outputs.

These combine into a **risk score**: `max(impact * (1 - verified_fraction), overfit)`. Verification drives risk down -- a fully-verified high-impact constant drops to low risk. High overfit stays risky regardless.

| Risk level | Score | Example |
|---|---|---|
| critical | >= 0.7 | `_REGULATOR_VREF` (92 unverified Vref values from datasheets) |
| high | >= 0.5 | `type_map` (64-entry component classifier) |
| medium | >= 0.3 | Keyword lists for IC family matching |
| low | < 0.3 | Format codes, unit conversions, verified tables |

### Corpus analysis

`corpus` scans all analyzer outputs to measure which constants actually fire across the test corpus. For each constant, it records how many repos exercise it:

- **`_REGULATOR_VREF`** -- traces `vref_source: "lookup"` in power_regulators to identify which prefix keys match real parts. Per-entry hit counts show which entries are exercised vs dead weight.
- **`type_map`** -- counts which reference designator prefixes appear across all components.
- **Signal detector keywords** -- maps keyword lists to their signal_analysis sections and counts repos with non-empty results.

Entries with zero corpus hits get flagged (`corpus_unused_entries`) and increase the overfit score. This surfaces constants that were potentially added for one project and never exercised again.

### Categories

Each constant is auto-classified into a category that determines what kind of verification it needs:

| Category | Description | Verification source |
|---|---|---|
| `physics` | Unit conversions, coordinate tolerances | Textbook / auto-verified |
| `standard` | KiCad format codes, IPC designators, SI prefixes | KiCad docs, IPC standards |
| `datasheet_lookup` | Part-specific values (Vref, quiescent current) | Manufacturer datasheets |
| `heuristic_threshold` | Empirical cutoffs and scoring tables | Engineering justification + corpus tuning |
| `keyword_classification` | Part families, net name patterns, pin names | KiCad stdlib + domain knowledge |

The registry (`reference/constants_registry.json`) tracks stable IDs, content hashes for drift detection, per-entry verification for lookup tables, corpus hit data, and both risk dimensions.

## Validation scripts

```bash
python3 validate/validate_outputs.py --repo {repo}     # structural invariants
python3 validate/extract_mpns.py --repo {repo}          # extract MPNs from outputs
python3 validate/analyze_bom_mismatch.py --repo {repo}  # BOM qty vs component count
python3 validate/download_datasheets.py --project {repo} --status   # datasheet downloads
python3 validate/validate_mpns.py --limit 50            # validate MPNs against APIs
```

## Repo management

- **repos.md** -- Master list of all repos with URLs and pinned commit hashes
- **priority.md** -- Repos ranked by testing priority (schematic complexity)
- **status.md** -- Operational log of batch testing progress

### Adding test repos

Edit `repos.md` directly:

```
- https://github.com/user/repo
- https://github.com/user/large-repo (shallow)
- https://github.com/user/pinned-repo @ abc123def456
```

```bash
python3 checkout.py                        # clone new repos
python3 checkout.py --check-updates        # compare pinned hashes to remote HEAD
python3 checkout.py --check-updates --pin  # update repos.md with new hashes
```

## Issue tracking

Issues are discovered opportunistically while running analyzers and reviewing outputs:

- **ISSUES.md** -- Open issues only. Removed when fixed.
- **FIXED.md** -- Closed issues with root cause, fix details, and verification.

Prefixes: `KH-*` for analyzer bugs, `TH-*` for harness issues. Numbers are globally unique and never reused.

## Directory structure

```
repos.md                    # Master repo list
priority.md                 # Testing priority ranking
status.md                   # Batch testing progress log
ISSUES.md                   # Open issues (KH-* analyzer, TH-* harness)
FIXED.md                    # Closed issues with fix details
checkout.py                 # Clone repos + check upstream updates
discover.py                 # Find KiCad files, write manifests
utils.py                    # Shared utilities (path resolution, unified runner)

run/                        # Batch-run analyzers (all support --repo, --jobs)
  run_schematic.py
  run_pcb.py
  run_gerbers.py

regression/                 # 3-layer regression testing
  _differ.py                #   Semantic JSON diff engine
  checks.py                 #   Assertion data model + evaluation
  snapshot.py               #   Snapshot outputs to reference/ baselines
  compare.py                #   Diff current outputs vs baselines
  run_checks.py             #   Run assertions against outputs
  seed.py                   #   Generate seed assertions from outputs
  findings.py               #   Manage LLM review findings
  drift.py                  #   Detect findings drift against outputs
  packet.py                 #   Generate review packets for LLM analysis
  promote.py                #   Promote improved results/ to reference/

validate/                   # Output quality + constants audit
  validate_outputs.py       #   Structural invariants on analyzer JSON
  extract_mpns.py           #   Extract MPN + manufacturer pairs
  validate_mpns.py          #   Validate MPNs against distributor APIs
  analyze_bom_mismatch.py   #   BOM qty vs component count analysis
  download_datasheets.py    #   Download datasheets from multiple sources
  audit_constants.py        #   AST-based constant registry + verification

integration/                # End-to-end tests
  test_datasheets.py        #   Datasheet download across distributors
  test_bom_manager.py       #   BOM manager pipeline

reference/                  # Tracked in git -- known-good regression data
  constants_registry.json   #   Constant audit registry
  constants_registry.md     #   Auto-generated constant summary
  test_mpns.json            #   Curated test MPNs
  {repo}/{project}/         #   Per-repo, per-project reference data
    baselines/              #     Compact baseline manifests
    assertions/{type}/      #     Machine-checkable facts per file
    findings.json           #     Structured findings from LLM review
    findings.md             #     Human-readable view (auto-generated)

repos/                      # Git-ignored -- cloned test repos
results/                    # Git-ignored -- outputs, manifests, review packets
```

## Usage warning

The test corpus has 1,100+ repos and cannot be processed in a single session. Work through repos in batches using `--repo` flags. Use `--jobs` for parallelism where supported.
