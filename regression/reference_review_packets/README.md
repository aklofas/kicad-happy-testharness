# Reference Review Packets

Curated inputs for replaying recorded reviewer output with
`run/run_review_metrics.py`. Each packet exercises one scenario. The runner
measures Layer 2 reviewer quality; it does not enforce target metrics.

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

The runner validates packets against `packet_schema.json` when `jsonschema` is
installed; otherwise that validation is skipped. Install it before curating
packets: `python3 -m pip install jsonschema`. A packet that fails to load or
validate is reported as `skipped`, not as an error.

## Scenarios

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
3. Run `python3 run/run_review_metrics.py --json` over all packets and inspect
   `packets_run` and `packets_skipped`: the new packet must be included and
   nothing may be skipped unexpectedly. The exit code is 0 even when packets
   were skipped, so it is not proof that every packet validated.

## Running

```bash
python3 run/run_review_metrics.py                              # all packets
python3 run/run_review_metrics.py --packet packet_01_suppress_true_fp
python3 run/run_review_metrics.py --json                       # stdout-only
```

Output: `results/review_metrics/<timestamp>/{per_packet.json, aggregate.json, report.md}` (gitignored).
