# Supervised Performance Recovery Protocol v1

## Purpose and status

`ENGINEERING / BASELINE IMPROVEMENT ONLY`。本协议不声称 novel method、innovation
或 SOTA。它仅定位在合法 target-prefix supervision 下，简单 predictor 是否可以恢复。

`TestLoaded=False` 是硬约束：对每个 battery 只读取 `nrows=ValidationEnd`。

## Data boundary

| Target | labeled training prefix | external validation | locked test |
|---|---:|---:|---:|
| B0007 | rows `[0, 33)` | rows `[33, 67)` | rows `[67, end)` — unread |
| B0018 | rows `[0, 25)` | rows `[25, 51)` | rows `[51, end)` — unread |

Within each usable training prefix, the first 60% of chronological rows is the
inner fit segment and the final 40% is the inner selection segment. Candidate
selection uses only this inner selection segment. The winning pre-defined
configuration is then refit on every usable row in `[0, TrainEnd)` and evaluated
once on `[TrainEnd, ValidationEnd)`. No outer-validation result chooses a model,
feature or hyperparameter.

## Frozen feature sets

- `F0_HF_CURRENT`: current `HF1`, `HF2`, `HF3` only.
- `F1_HF_CAUSAL_TEMPORAL`: F0 plus, per HF, current-minus-previous value,
  trailing-4 mean, trailing-4 standard deviation, and trailing-4 least-squares
  slope; plus `cycle_index / TrainEnd`. Row `t` uses only rows `<= t`; the first
  eligible F1 row is `t=3`. The denominator is the known labelled-prefix end,
  never total lifetime.

Past true SOH is intentionally excluded: its validation-time recursive use would
introduce a separate forecasting-state decision and obscure the HF-to-SOH mapping
audit. No feature uses final lifetime, validation SOH, validation future HF, or
test data.

For every fit, input and target normalization parameters are calculated only from
that fit's training rows. Tree models receive the same input features but do not
require scaling; this implementation still uses train-fitted scaling for a single
auditable feature contract.

## Frozen model/configuration table

| ID | Model | configurations | stochastic evaluation |
|---|---|---|---|
| M0 | Ridge | alpha = 0.1, 1.0, 10.0 | deterministic |
| M1 | ElasticNet | alpha = 0.001, 0.01, 0.1; l1_ratio = 0.5 | deterministic |
| M2 | RandomForestRegressor | max_depth = 2, 3, 4; n_estimators = 200, min_samples_leaf = 2 | five seeds |
| M3 | HistGradientBoostingRegressor | max_leaf_nodes = 3, 5, 7; l2_regularization = 1.0 | deterministic |
| M4 | small MLP | hidden = 8, 16, 32; one hidden layer, ReLU, AdamW lr=0.001, weight_decay=1e-5, max_epochs=300, patience=50 | five seeds |
| M5 | small GRU | hidden = 8, 16; 1 layer, trailing-4 HF sequence, AdamW lr=0.001, weight_decay=1e-5, max_epochs=300, patience=50 | five seeds |

Stochastic models use exactly `[42, 123, 2024, 3407, 7777]`. The inner-selection
score is mean RMSE across these seeds (or the deterministic RMSE). Ties are broken
only by the listed configuration order. Each selected stochastic configuration is
refit/evaluated for all five seeds. No configuration is added after results appear.

## Metrics and frozen classification

Every external-validation run records RMSE, MAE, MAPE, R², prediction mean/std, maximum
absolute error, catastrophic count, `TestLoaded`, feature/model/configuration,
seed, fit sample count and best epoch (when applicable). Catastrophic means
prediction `< 50%` or `> 110%`; it is a monitoring threshold, not a physical SOH
claim.

Primary F0-vs-F1 and model-family summaries report mean/std/worst across applicable
seeds. The decision rule is exactly the one in
`DECISION_RECORD_SUPERVISED_PERFORMANCE_RECOVERY.md`; an outer validation result
cannot alter the protocol.

## Stop rule

After every table entry is run once, classify only `STRONG_BASELINE_RECOVERED`,
`PARTIAL_RECOVERY`, or `SUPERVISED_PERFORMANCE_NOT_RECOVERED`, write the failure
attribution, and stop. No test, CALCE, transfer, source-selection, SSL/DG,
component/fusion, attention/Transformer, large grid or follow-up feature search
is authorized.
