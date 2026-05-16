# packet_01_suppress_true_fp

Synthetic scaffolding packet authored by harness for B9 v1.4. Shape exemplar
locking the on-disk schema for main-repo's scenario contributions (02–05).

**Scenario:** suppress-true-FP. The PU-001 detector fires on I2C SDA to
STM32F103C8T6 PB7 because the pin has no external pull-up; the reviewer
should suppress this because the MCU has an internal weak pull-up adequate
for low-speed I2C. All other findings are decoy — no expected annotation.

**Expected metrics on this packet:**
- suppression_precision = 1.0 (1 suppression matches 1 expected)
- false_suppression_miss_rate = null (no expected_confirmations)
- All other status-based metrics = null (no other expected annotations)
- confidence_calibration = {"high": insufficient_data, "medium": ..., "low": ...} (n<5)
- cost_delta = null (no cost ledger at v1.4)
