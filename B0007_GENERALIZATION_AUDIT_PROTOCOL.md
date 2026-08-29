# B0007 Generalization Bottleneck Audit Protocol v1

`DIAGNOSTIC_ONLY / NOT_AVAILABLE_FOR_MODEL_SELECTION`。本协议不产生新 SOH 方法。

## Fixed baseline and boundary

| Battery | formal fixed model | input | train prefix | diagnostic validation | locked test |
|---|---|---|---:|---:|---|
| B0007 | Ridge(alpha=10) | F0 current HF1/HF2/HF3 | `[0,33)` | `[33,67)` | `[67,end)` unread |
| B0018 | Ridge(alpha=1) | F0 current HF1/HF2/HF3 | `[0,25)` | `[25,51)` | `[51,end)` unread |

F0 is the prior protocol's current-HF-only feature set. For every diagnostic
fit, input and target standardization fit only on that fit's chronological train
rows. Raw CSV loading is limited to `nrows=ValidationEnd`.

## Frozen diagnostics

1. **Baseline reproduction.** Recompute the two fixed F0 Ridge results and compare
   RMSE/R² against Recovery I with absolute tolerance `1e-6`.
2. **Prefix rolling origin.** For each battery, fit at 50/60/70/80% of its frozen
   first-20% prefix, and evaluate the remaining early-prefix rows. Record RMSE,
   MAE, R² and prediction bias.
3. **Mapping drift.** Compare prefix and validation-only diagnostic data: each HF
   feature's Pearson/Spearman, mean/std/min/max, SOH slope, standardized Ridge
   coefficient and intercept. Also record residual bias/std for in-split Ridge
   fits and for prefix Ridge applied to validation. This comparison is diagnostic
   only; validation fit never becomes a formal predictor.
4. **Validation internal predictability.** Split validation chronologically 50/50.
   Fit the fixed Ridge and the fixed one-layer MLP (`hidden=32`) on its first half
   and evaluate its second half. MLP runs five frozen seeds. Label output
   `DIAGNOSTIC_ORACLE_LIKE_FIT` and `NOT_AVAILABLE_FOR_MODEL_SELECTION`.
5. **Label budget.** Train fixed Ridge with the first 10%, 15% and 20% of the
   already authorized target prefix: B0007 = 16/24/33 rows; B0018 = 12/18/25
   rows. Evaluate the unchanged diagnostic validation. This is
   `LABEL_BUDGET_DIAGNOSTIC`, not an authorized increase in formal labels.

## Required files

`B0007_GENERALIZATION_AUDIT.md` and `SUPERVISED_BOTTLENECK_REPORT.md` at the
repository root; the four CSV files under `output/b0007_generalization_audit_v1/`.
Each result row has `TestLoaded=False`.

After the single run, apply only the Decision Record's frozen attribution rules
and stop pending human confirmation.
