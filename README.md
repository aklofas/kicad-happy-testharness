# kicad-happy Test Harness

Test harness for validating [kicad-happy](https://github.com/aklofas/kicad-happy) analyzers against a corpus of real-world open-source KiCad projects.

## Regression testing (3-layer approach)

The harness uses three complementary layers to catch regressions and discover improvements.
All operations are per-repo. Data is organized by `reference/{repo}/{project}/` where project
is the subpath to the KiCad project directory with `/` encoded as `_`.

### Layer 1: Baselines

Baseline snapshots capture a summary of all analyzer outputs at a point in time. Compact manifests are checked into git (in `reference/`) so any machine can compare against them.

```bash
python3 regression/snapshot.py --repo {repo}       # create baseline
python3 regression/compare.py --repo {repo}        # diff current vs baseline
python3 regression/compare.py --all --only-changes    # all repos, only diffs
```

### Layer 2: Assertions

Assertions are machine-checkable facts about what an analyzer should find in a specific file. They live in `reference/{repo}/{project}/assertions/` and provide permanent regression protection.

```bash
python3 regression/run_checks.py --repo {repo}     # run assertions
python3 regression/seed.py --repo {repo}           # generate seed assertions
```

Assertion files are JSON with operators like `range`, `min_count`, `equals`, `exists`, `contains_match`, etc. See `regression/checks.py` for the full list.

### Layer 3: LLM review

Review packets pair source KiCad files with analyzer output summaries, making it easy for Claude to independently verify analysis quality and discover issues that deterministic checks miss.

```bash
python3 regression/packet.py --strategy random --count 5        # random review
python3 regression/packet.py --strategy changed --repo {repo} # changed files

python3 regression/findings.py list                   # list all findings
python3 regression/findings.py stats                  # summary statistics
python3 regression/findings.py render                 # regenerate all findings.md
python3 regression/findings.py promote FND-00000001   # promote to assertion
```

### Promoting improvements

When analyzer outputs improve, promote the changes to reference data:

```bash
python3 regression/promote.py --repo {repo}         # dry run
python3 regression/promote.py --repo {repo} --apply  # promote improvements
```

### Typical workflow

1. Make changes to the kicad-happy analyzers
2. Run the analyzers: `python3 run/run_schematic.py --jobs 4`
3. Compare against baseline: `python3 regression/compare.py --repo {repo} --only-changes`
4. Run assertions: `python3 regression/run_checks.py --repo {repo}`
5. Generate review packets for changed files: `python3 regression/packet.py --strategy changed --repo {repo}`
6. Review packets with Claude, record findings
7. Promote confirmed findings to assertions
8. If satisfied, promote to reference: `python3 regression/promote.py --repo {repo} --apply`

## What gets tested

The test corpus exercises:

- **KiCad versions**: 5 through 9 (legacy `.sch` and modern `.kicad_sch`)
- **Design complexity**: From minimal breakout boards to large hierarchical designs
- **Domains**: Power, RF, digital, mixed-signal, motor control, audio, sensors
- **Edge cases**: Multi-instance sheets, unusual footprints, legacy formats

### Analyzer scripts (from kicad-happy)

| Analyzer | Input | Description |
|----------|-------|-------------|
| `analyze_schematic.py` | `.kicad_sch`, `.sch` | Components, nets, signal paths, BOM, design analysis |
| `analyze_pcb.py` | `.kicad_pcb` | Footprints, tracks, vias, zones, DFM analysis |
| `analyze_gerbers.py` | Gerber directories | Layer completeness, drill alignment |

All analyzers are pure Python 3.8+ stdlib with no dependencies. They produce JSON output.

### Supported file types

| Extension | Analyzer | KiCad Version |
|-----------|----------|---------------|
| `.kicad_sch` | analyze_schematic.py | 6, 7, 8, 9 |
| `.sch` | analyze_schematic.py | 5 (legacy, filtered for KiCad format) |
| `.kicad_pcb` | analyze_pcb.py | 5, 6, 7, 8, 9 |
| `.kicad_pro` | Direct JSON read | 6+ |
| `.gbr`, `.g*`, `.drl` | analyze_gerbers.py | N/A |

**Note on `.sch` files**: Many repos contain Eagle `.sch` files (XML/binary format) which are
not KiCad files. `discover.py` filters legacy `.sch` files by checking the file header for
"EESchema" (the KiCad 5 signature) and excludes anything else. All Adafruit repos, for
example, use Eagle format and are correctly excluded.

## Quick start

```bash
# 1. Clone this repo
git clone <this-repo-url>
cd kicad-happy-testharness

# 2. Clone the kicad-happy repo alongside this one (or set KICAD_HAPPY_DIR)
git clone <kicad-happy-url> ../kicad-happy

# 3. Configure your budget in CLAUDE.md (see "Usage budget" below)

# 4. Clone all test repos
python3 checkout.py

# 5. Discover KiCad files
python3 discover.py

# 6. Run analyzers (use --jobs for parallelism, --repo to target one repo)
python3 run/run_schematic.py --jobs 4
python3 run/run_pcb.py --jobs 4
python3 run/run_gerbers.py --jobs 4

# 7. Validate outputs
python3 validate/validate_outputs.py

# 8. Extract MPNs and download datasheets
python3 validate/extract_mpns.py
python3 validate/download_datasheets.py
```

### Requirements

- **Python 3.8+** (stdlib only for core scripts)
- **Git** (for cloning test repos)
- **requests** (optional, for manufacturer datasheet scraping)
- **DigiKey/Mouser/element14 API keys** (optional, for datasheet downloads and MPN validation)

### Finding kicad-happy

All scripts that need the kicad-happy analyzers look for them in this order:

1. `KICAD_HAPPY_DIR` environment variable
2. `../kicad-happy` (sibling directory -- the common layout)

```bash
export KICAD_HAPPY_DIR=/path/to/kicad-happy   # if not at ../kicad-happy
```

## Directory structure

```
repos.md                    # Master repo list -- human-editable markdown
ISSUES.md                   # Git-tracked issue tracker (KH-* and TH-* issues)
checkout.py                 # Clone repos + check for upstream updates
discover.py                 # Find all KiCad files, write manifests
monitor.py                  # Usage budget monitor -- tracks session costs
utils.py                    # Shared utilities (path resolution, repo naming, unified runner)

run/                        # Batch-run kicad-happy analyzers (all support --repo, --jobs)
  run_schematic.py          #   Run analyze_schematic.py on all schematics
  run_pcb.py                #   Run analyze_pcb.py on all PCBs
  run_gerbers.py            #   Run analyze_gerbers.py on all Gerber dirs

regression/                 # 3-layer regression testing system
  _differ.py                #   Semantic JSON diffing engine
  checks.py                 #   Assertion data model and evaluation engine
  snapshot.py               #   Snapshot outputs -> reference/ baselines
  compare.py                #   Diff current outputs vs baselines
  run_checks.py             #   Run assertions against outputs
  seed.py                   #   Generate seed assertions from outputs
  findings.py               #   Manage LLM review findings + render findings.md
  packet.py                 #   Generate review packets for LLM analysis
  promote.py                #   Promote improved results/ to reference/

validate/                   # Output quality checks & BOM analysis
  validate_outputs.py       #   Check structural invariants in analyzer JSON
  extract_mpns.py           #   Extract MPN + manufacturer pairs from outputs
  validate_mpns.py          #   Validate MPNs against DigiKey/Mouser APIs
  analyze_bom_mismatch.py   #   Analyze BOM qty vs component count discrepancies
  download_datasheets.py    #   Download datasheets from multiple sources

integration/                # End-to-end tests
  test_datasheets.py        #   Test datasheet downloading across distributors
  test_bom_manager.py       #   Test BOM manager pipeline

reference/                  # Tracked in git -- known-good regression data
  test_mpns.json            #   Curated set of test MPNs
  {repo}/{project}/         #   Per-repo, per-project reference data
    baselines/              #     Compact baseline manifests
    assertions/{type}/      #     Machine-checkable facts per file
    findings.json           #     Structured observations from LLM review
    findings.md             #     Human-readable view (auto-generated from JSON)

repos/                      # Git-ignored -- cloned test repos
results/                    # Git-ignored -- outputs, manifests, review packets
```

## Adding test repos

Edit `repos.md` directly. It's organized as a simple list grouped by category:

```
- https://github.com/user/repo
- https://github.com/user/large-repo (shallow)
- https://github.com/user/pinned-repo @ abc123def456
```

- Append `(shallow)` for large repos where you only need the latest snapshot
- Append `@ <commit_hash>` to pin a specific commit for reproducibility
- After adding, run `python3 checkout.py` to clone the new repo

Hashes are managed automatically -- `checkout.py` pins HEAD after cloning and verifies pinned hashes on each run. `repos.md` is the single source of truth.

```bash
python3 checkout.py --check-updates              # compare pinned hashes to remote HEAD
python3 checkout.py --check-updates --pin        # update repos.md with new hashes
```

## Validation scripts

### validate_outputs.py

Checks structural invariants on schematic analyzer output (required keys, count sanity, BOM consistency, signal analysis plausibility):

```bash
python3 validate/validate_outputs.py --repo {repo}
```

### extract_mpns.py / download_datasheets.py

Extract manufacturer part numbers from analyzer outputs, then download datasheets from multiple sources in parallel:

```bash
python3 validate/extract_mpns.py --repo {repo}
python3 validate/download_datasheets.py --project {repo} --status
```

Sources tried in order: direct URL from schematic, LCSC direct API, DigiKey, Mouser, LCSC (jlcsearch), element14, manufacturer website scraping.

### validate_mpns.py

Validates extracted MPNs against DigiKey and Mouser APIs (requires API keys):

```bash
export DIGIKEY_CLIENT_ID=... DIGIKEY_CLIENT_SECRET=...
export MOUSER_SEARCH_API_KEY=...
python3 validate/validate_mpns.py --limit 50
```

### analyze_bom_mismatch.py

Analyzes root causes of BOM quantity vs component count mismatches:

```bash
python3 validate/analyze_bom_mismatch.py --repo {repo}
```

## Integration tests

```bash
python3 integration/test_datasheets.py --only lcsc     # LCSC needs no API key
python3 integration/test_datasheets.py --mpn STM32G474CEU6
python3 integration/test_bom_manager.py --repo {repo} --stage analyze -v
```

## Usage budget

> **This test harness covers 1,100+ repos.** Running the full suite takes many Claude Code
> sessions spread across multiple weeks. A built-in budget monitor prevents burning through
> your weekly Claude Code limits in a single sitting.

Configure your budget in `CLAUDE.md` (not tracked in git):

```
WEEKLY_BUDGET_USD=5.00
BUDGET_LIMIT_PCT=20
```

- **WEEKLY_BUDGET_USD** -- Your estimated total weekly Claude Code spend (based on your plan).
- **BUDGET_LIMIT_PCT** -- Max percentage of that weekly budget to allocate to test harness work.

```bash
python3 monitor.py status              # Current week's usage vs budget
python3 monitor.py log 0.35 "ran schematic analyzer on batch 1"   # Log session cost
python3 monitor.py history             # All logged sessions
```

Session costs come from the Claude Code `/cost` command. Log at end of each session. The test corpus is too large to process in one session -- work through repos in batches, and defer when the weekly allocation is spent.
