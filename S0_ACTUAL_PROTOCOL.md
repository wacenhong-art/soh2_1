# S0 Actual Protocol — Recovered `dc931f7`

```text
REPOSITORY=soh2_1
RECOVERY_SOURCE=soh02@dc931f7
BASELINE=S0_RIDGE
MODEL_OR_PROTOCOL_CHANGED=False
TestLoaded=False
```

The reproduced entry `scripts/98_reproduce_s0_ridge.py` calls recovered `scripts/84_strong_baseline_raw_feature_ablation.py` functions `load`, `predict`, and `metrics` without changing S0 semantics.

| Item | Actual S0 evidence |
|---|---|
| Batteries and role | B0007 and B0018 are target-only regressions; no source battery, GAN, transfer, or synthetic sample enters S0. |
| Feature set | `DISCHARGE_DURATION_S`, `DISCHARGE_V4P0_TO_V3P6_S`, discharge voltage mean/std, discharge temperature mean/std, `DISCHARGE_ENERGY_WH`. |
| Feature timing | Each feature is derived from the current completed discharge cycle. |
| Label | Frozen table scalar `SOH` is read as target and multiplied by 100. S0 code does not recompute capacity/SOH from raw data; raw-label construction is `REPRO_DEFINED`. |
| Model | `Ridge(alpha=0.1)`, deterministic. |
| Split | B0007 `[0,33)` train / `[33,67)` validation; B0018 `[0,25)` / `[25,51)`. The feature CSV contains exactly 67/51 rows, all `TestLoaded=False`. |
| Scaling | Median imputation, feature mean/std, and target mean/std are fit only on the training prefix. |
| Train/validation separation | `load` returns only the frozen train-plus-validation prefix. `predict` receives `x[:train], y[:train]` for fit and `x[train:end]` only for outer validation prediction. The S0 reproduction freezes `alpha=0.1`; it does not select a configuration from outer validation. |
| Configuration provenance | The recovered historical ablation used chronological inner-prefix selection among candidates. The exact S0 reproduction uses the already recorded `M0_RIDGE, alpha=0.1` setting and does not re-run selection; this audit therefore treats the outer validation scores as evaluation, not a tuning signal. |
| Metrics | RMSE, MAE, MAPE and R2 on chronological validation prefix. |
| Test gate | `load` rejects a non-false `TestLoaded`; no raw MAT or test row is opened. |

S0 is end-of-current-completed-discharge estimation, not early-life or future/RUL prediction.

`TRAIN_VAL_LEAKAGE_FOUND=False`: fitted scaler statistics and Ridge coefficients are produced from the training prefix only; validation rows enter only `transform` and metric computation. This finding applies to the reproduced fixed S0 configuration, not to any unrecorded earlier exploratory work.
