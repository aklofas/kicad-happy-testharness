# kicad-happy Test Harness

Test harness for validating [kicad-happy](https://github.com/aklofas/kicad-happy) analyzers against a corpus of real-world open-source KiCad projects.

## Important: Usage budget

> **This test harness covers 1,100+ repos.** Running the full suite takes many Claude Code
> sessions spread across multiple weeks. A built-in budget monitor prevents burning through
> your weekly Claude Code limits in a single sitting.

Before running any analyzers, validators, or batch operations, you **must** configure your
budget in `CLAUDE.md` (not tracked in git):

```
WEEKLY_BUDGET_USD=5.00
BUDGET_LIMIT_PCT=20
```

- **WEEKLY_BUDGET_USD** -- Your estimated total weekly Claude Code spend (based on your plan).
- **BUDGET_LIMIT_PCT** -- Max percentage of that weekly budget to allocate to test harness
  work. Start with 10-20%.

With the defaults above, the test harness is allowed $1.00/week of Claude Code usage.
The budget resets every Monday (ISO week).

### Checking budget

```bash
python3 monitor.py status              # Current week's usage vs budget
python3 monitor.py log 0.35 "ran schematic analyzer on batch 1"   # Log session cost
python3 monitor.py history             # All logged sessions
```

Session costs come from the Claude Code `/cost` command. Log them at the end of each
session to keep the ledger accurate. The ledger is stored in `data/usage.json` (git-ignored).

### How pacing works

The test corpus is too large to process in one session. Instead:

1. Each session, check budget with `python3 monitor.py status`
2. Work through a batch of repos (checkout, analyze, validate)
3. Log the session cost when done
4. When the weekly allocation is spent, defer remaining work to next week
5. Repeat until the full corpus is processed

Claude Code is instructed (via `CLAUDE.md`) to **prompt the user for budget values before
launching any batch operations** if they haven't been configured yet.

## Quick start

```bash
# 1. Clone this repo
git clone <this-repo-url>
cd kicad-happy-testharness

# 2. Clone the kicad-happy repo alongside this one (or set KICAD_HAPPY_DIR)
git clone <kicad-happy-url> ../kicad-happy

# 3. Configure your budget in CLAUDE.md (see "Usage budget" above)

# 4. Clone all test repos
python3 checkout.py

# 5. Discover KiCad files
python3 discover.py

# 6. Run analyzers
python3 analyzers/run_schematic.py
python3 analyzers/run_pcb.py
python3 analyzers/run_gerbers.py

# 7. Validate outputs
python3 validators/validate_outputs.py

# 8. Extract MPNs and download datasheets
python3 validators/extract_mpns.py
python3 validators/download_datasheets.py
```

## Requirements

- **Python 3.8+** (stdlib only for core scripts)
- **Git** (for cloning test repos)
- **requests** (optional, for manufacturer datasheet scraping)
- **DigiKey/Mouser/element14 API keys** (optional, for datasheet downloads and MPN validation)

## Finding kicad-happy

All scripts that need the kicad-happy analyzers look for them in this order:

1. `KICAD_HAPPY_DIR` environment variable
2. `../kicad-happy` (sibling directory -- the common layout)

Set the env var if your kicad-happy repo is elsewhere:

```bash
export KICAD_HAPPY_DIR=/path/to/kicad-happy
```

## Directory structure

```
repos.md                  # Master repo list -- human-editable markdown
checkout.py               # Clone test repos into repos/
check_updates.py          # Check if repos have upstream updates
discover.py               # Find all KiCad files, write manifests
monitor.py                # Usage budget monitor -- tracks session costs

analyzers/
  run_schematic.py        # Batch run analyze_schematic.py on all schematics
  run_pcb.py              # Batch run analyze_pcb.py on all PCBs
  run_gerbers.py          # Batch run analyze_gerbers.py on all Gerber dirs

baselines/
  snapshot.py             # Create baseline snapshots of analyzer outputs
  compare.py              # Compare current outputs against a baseline
  _differ.py              # Semantic JSON diffing engine

review/
  assertions.py           # Assertion data model and evaluation engine
  check_assertions.py     # Run assertions against current outputs
  findings.py             # Manage review findings (new/confirmed/promoted)
  packet.py               # Generate review packets for LLM analysis

validators/
  validate_outputs.py     # Check structural invariants in analyzer JSON
  extract_mpns.py         # Extract MPN + manufacturer pairs from analyzer outputs
  download_datasheets.py  # Download datasheets for extracted MPNs (parallel)
  validate_mpns.py        # Validate MPNs against DigiKey/Mouser APIs
  analyze_bom_mismatch.py # Analyze BOM qty vs component count discrepancies

integration/
  test_datasheets.py      # Test datasheet downloading across distributors
  test_bom_manager.py     # Test BOM manager pipeline

data/
  test_mpns.json          # Curated set of test MPNs (checked in)
  baselines/              # Compact baseline manifests (checked in)
  assertions/             # Curated assertions per file (checked in)
  findings/               # Review findings (checked in)

repos/                    # Git-ignored -- cloned test repos
results/                  # Git-ignored -- outputs, full baselines, review packets
```

## Adding test repos

Edit `repos.md` directly. It's organized as a simple list grouped by category. To add a repo, add a line to the appropriate section:

```
- https://github.com/user/repo
- https://github.com/user/large-repo (shallow)
- https://github.com/user/pinned-repo @ abc123def456
- https://github.com/user/pinned-shallow @ abc123def456 (shallow)
```

- Append `(shallow)` for large repos where you only need the latest snapshot
- Append `@ <commit_hash>` to pin a specific commit for reproducibility
- Prefer projects with clear open-source licenses (MIT, Apache, CERN-OHL, etc.)
- After adding, run `python3 checkout.py` to clone the new repo

Hashes are managed automatically:
- `checkout.py` pins the HEAD hash into `repos.md` after cloning new repos
- `checkout.py` verifies and restores existing repos to their pinned hash on each run
- `repos.md` is the single source of truth for commit hashes (no separate state file)

### Checking for upstream updates

```bash
python3 check_updates.py              # compare pinned hashes to remote HEAD
python3 check_updates.py --pin        # update repos.md with new remote hashes
python3 check_updates.py --fetch      # also git fetch in local clones
python3 check_updates.py --json       # machine-readable output
```

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

## Validation scripts

### validate_outputs.py

Checks structural invariants on schematic analyzer output:
- Required JSON keys present
- Component/net count sanity
- BOM consistency
- Signal analysis plausibility

```bash
python3 validators/validate_outputs.py
python3 validators/validate_outputs.py --results-dir path/to/outputs --manifests-dir path/to/manifests
```

### extract_mpns.py

Extracts manufacturer part numbers from analyzer JSON outputs:

```bash
python3 validators/extract_mpns.py
python3 validators/extract_mpns.py --results-dir path/to/outputs --output results/extracted_mpns.json
```

### download_datasheets.py

Downloads datasheets for extracted MPNs using multiple sources in parallel:

```bash
python3 validators/download_datasheets.py                    # download all
python3 validators/download_datasheets.py --limit 20         # first 20
python3 validators/download_datasheets.py --project OpenMower # one project
python3 validators/download_datasheets.py --status           # show progress
python3 validators/download_datasheets.py --retry             # retry failures
python3 validators/download_datasheets.py --workers 16        # more parallelism
```

Sources tried in order: direct URL from schematic, LCSC direct API, DigiKey, Mouser, LCSC (jlcsearch), element14, manufacturer website scraping.

### validate_mpns.py

Validates extracted MPNs against DigiKey and Mouser APIs (requires API keys):

```bash
export DIGIKEY_CLIENT_ID=... DIGIKEY_CLIENT_SECRET=...
export MOUSER_SEARCH_API_KEY=...
python3 validators/validate_mpns.py --limit 50
```

### analyze_bom_mismatch.py

Analyzes root causes of BOM quantity vs component count mismatches:

```bash
python3 validators/analyze_bom_mismatch.py
```

## Regression testing (3-layer approach)

The harness uses three complementary layers to catch regressions and discover improvements:

### Layer 1: Baselines

Baseline snapshots capture a summary of all analyzer outputs at a point in time. Compact manifests are checked into git (in `data/baselines/`) so any machine can compare against them.

```bash
# Create a baseline after running analyzers
python3 baselines/snapshot.py my-baseline

# Also save full output copies for deeper diffing (git-ignored)
python3 baselines/snapshot.py my-baseline --full

# Compare current outputs against a baseline
python3 baselines/compare.py my-baseline
python3 baselines/compare.py my-baseline --type schematic --only-changes
python3 baselines/compare.py my-baseline --json

# List / delete baselines
python3 baselines/snapshot.py --list
python3 baselines/snapshot.py --delete old-baseline
```

### Layer 2: Assertions

Assertions are machine-checkable facts about what an analyzer should find in a specific file. They live in `data/assertions/` and provide permanent regression protection.

```bash
# Run all assertions
python3 review/check_assertions.py

# Filter by type or file pattern
python3 review/check_assertions.py --type schematic
python3 review/check_assertions.py --file "hackrf*"
python3 review/check_assertions.py --json
```

Assertion files are JSON in `data/assertions/<type>/<file>.json` with operators like `range`, `min_count`, `equals`, `exists`, `contains_match`, etc. See `review/assertions.py` for the full list.

### Layer 3: LLM review

Review packets pair source KiCad files with analyzer output summaries, making it easy for Claude to independently verify analysis quality and discover issues that deterministic checks miss.

```bash
# Generate review packets for random files
python3 review/packet.py --strategy random --count 5

# Review files that changed most from baseline
python3 review/packet.py --strategy changed --baseline my-baseline --count 5

# Review a specific file
python3 review/packet.py --file "repos/hackrf/hardware/hackrf-one/hackrf-one.kicad_sch"

# Manage findings from reviews
python3 review/findings.py list
python3 review/findings.py show FND-0001
python3 review/findings.py stats

# Promote a confirmed finding to a permanent assertion
python3 review/findings.py promote FND-0001
```

### Typical workflow

1. Make changes to the kicad-happy analyzers
2. Run the analyzers: `python3 analyzers/run_schematic.py`
3. Compare against baseline: `python3 baselines/compare.py my-baseline --only-changes`
4. Run assertions: `python3 review/check_assertions.py`
5. Generate review packets for changed files: `python3 review/packet.py --strategy changed --baseline my-baseline`
6. Review packets with Claude, record findings
7. Promote confirmed findings to assertions
8. If satisfied, create a new baseline: `python3 baselines/snapshot.py new-baseline`

## Integration tests

### test_datasheets.py

Tests datasheet downloading across distributors (DigiKey, Mouser, LCSC, element14):

```bash
python3 integration/test_datasheets.py --only lcsc     # LCSC needs no API key
python3 integration/test_datasheets.py --mpn STM32G474CEU6
python3 integration/test_datasheets.py --keep -v
```

### test_bom_manager.py

Tests the BOM manager pipeline against test repos:

```bash
python3 integration/test_bom_manager.py
python3 integration/test_bom_manager.py --repo hackrf --stage analyze -v
```
