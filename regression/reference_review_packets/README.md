# Reference Review Packets

Curated input packets for `run/run_review_metrics.py` (B9). Each packet
exercises one scenario from spec §15.1 and supports v1.4 measurement-only
Layer 2 reviewer-quality metrics. v1.5 calibrates target gates.

## Packet shape

Each packet is a directory `packet_NN_<scenario>/` containing 6 files:

| File | Purpose |
|---|---|
| `findings.json` | Layer 1 findings input (envelope per `finding_schema.py`) |
| `design_context.json` | Layer 2 design context (per `design_context.schema.json`) |
| `extraction_facts.json` | `{MPN: DatasheetFacts}` map for relevant parts |
| `review_annotations.json` | Recorded reviewer output (per `review_annotations.schema.json`) |
| `expected_annotations.json` | Curator's ground truth (suppressions/confirmations/escalations/correlations) |
| `notes.md` | Free-form curator notes — what scenario, why, what to look for |

Validated against `packet_schema.json` at runtime.

## Scenarios (per spec §15.1)

| # | Scenario | Status |
|---|---|---|
| 1 | suppress-true-FP | shipped (harness exemplar) |
| 2 | escalate-via-suggested_severity | main-repo contribution |
| 3 | confirm | main-repo contribution |
| 4 | cross-finding-correlation | main-repo contribution |
| 5 | trap / false-suppression-guard | main-repo contribution |
| 6 | novel-observation | v1.5 (E activation) |

## Adding a packet

1. Create `packet_NN_<scenario>/` with all 6 files.
2. Run `python3 run/run_review_metrics.py --packet packet_NN_<scenario>` to
   verify it loads and metrics compute.
3. Pre-push gate (`make smoke`) will exercise it automatically.

## Running

```bash
python3 run/run_review_metrics.py                              # all packets
python3 run/run_review_metrics.py --packet packet_01_suppress_true_fp
python3 run/run_review_metrics.py --json                       # stdout-only
```

Output: `results/review_metrics/<timestamp>/{per_packet.json, aggregate.json, report.md}` (gitignored).
