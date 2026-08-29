# Decision Record — Strong Baseline & Raw-Feature Ablation v1

> 本记录在模型拟合、validation 访问与特征消融前冻结。已阅读
> `RESEARCH_GUARDRAILS.md`；本轮不是 innovation、future prediction、RUL prediction
> 或 cross-dataset generalization。

## 基本信息

- **Experiment name：** `STRONG_BASELINE_RAW_ABLATION_v1`
- **Proposal category：** supervised baseline capacity diagnostic / feature contribution
  ablation
- **Problem being solved：** Feature Adequacy Reassessment 已用 leakage-safe F1 Ridge
  将 B0007 提升到 RMSE 2.034/R² 0.177、B0018 到 0.375/0.957，但不清楚 Ridge 是否已接近
  F1 信息上限，或性能是否主要来自同 cycle discharge duration/energy capacity proxy。
- **Supporting previous evidence：** `FEATURE_ADEQUACY_REPORT.md`、
  `FEATURE_EXTRACTION_PROTOCOL.md` 和
  `output/feature_adequacy_reassessment_v1/feature_set_performance.csv`。
- **Literature/theoretical basis：** Ridge/ElasticNet/gradient boosting/small MLP 是不同
  容量的标准监督基线；删除物理上预指定的 duration/energy descriptors 是直接的 feature
  contribution test。二者均不构成新算法。

## 冻结数据、特征和因果边界

- **Task only：** current discharge completed 后的 end-of-cycle SOH estimation。
- **Target/boundary：** B0007 `[0,33)` train / `[33,67)` validation；B0018 `[0,25)` /
  `[25,51)`。从已冻结 raw-prefix F1 artifact 载入；`TestLoaded=False`。
- **A0 full F1：**
  `DISCHARGE_DURATION_S`, `DISCHARGE_V4P0_TO_V3P6_S`,
  `DISCHARGE_VOLTAGE_MEAN_V`, `DISCHARGE_VOLTAGE_STD_V`,
  `DISCHARGE_TEMPERATURE_MEAN_C`, `DISCHARGE_TEMPERATURE_STD_C`,
  `DISCHARGE_ENERGY_WH`。
- **A1:** A0 删除 `DISCHARGE_DURATION_S`。
- **A2:** A0 删除 `DISCHARGE_ENERGY_WH`。
- **A3:** A0 同时删除 duration 与 energy。不得增加 A4/A5、修改 voltage window、加入
  rolling/context/新 health feature 或做自动特征选择。
- **Label proximity:** duration/energy 属于合法、同 cycle、post-discharge capacity-adjacent
  inputs，不是 label leakage；SOH/Capacity/future cycle/total life 均不得进入 feature。

## 冻结模型与选择

| ID | model | configurations (最多3) | seed policy |
|---|---|---|---|
| M0 | Ridge | alpha = 0.1/1/10 | deterministic |
| M1 | ElasticNet | alpha = 0.001/0.01/0.1, l1_ratio=0.5 | deterministic |
| M2 | HistGradientBoosting | max_leaf_nodes=3/5/7, min_samples_leaf=2, l2=1.0 | deterministic |
| M3 | one-hidden-layer MLP | hidden=8/16/32, ReLU, AdamW lr=0.001, wd=1e-5, 300 epochs, patience=50 | seeds 42/123/2024/3407/7777 |

Each configuration is evaluated only on the chronological 60/40 inner split of
the labelled prefix. Input/target imputation and scaling fit only on inner-fit
rows. Each model's target-specific configuration is its lowest inner mean RMSE;
ties follow configuration order. The Experiment-B family is the smallest mean
of per-target normalized inner RMSE across B0007/B0018; ties follow
M0→M1→M2→M3. The selected family and target-specific config are then refit on the
complete first-20% prefix and evaluated once on the unchanged validation. No
outer-validation score selects a family/configuration.

## Pre-registered gates

`STRONG_SUPERVISED_BASELINE_RECOVERED` requires any A0 model to meet all:
B0007 RMSE ≤1.729 (≥15% below 2.034), B0007 R²≥0.277 (≥0.10 above 0.177), B0018
RMSE≤0.394 (≤105% of 0.375), B0018 R²>0, no catastrophic predictions; M3 also
needs ≥4/5 B0007 seeds R²≥0.277. All rows must be `TestLoaded=False`.

`RIDGE_ALREADY_NEAR_FEATURE_LIMIT` requires every non-Ridge A0 model to improve
B0007 RMSE by <5% *and* R² by <0.05 versus A0 Ridge, or fail B0018 stability.
Otherwise result is `SUPERVISED_BASELINE_PARTIAL`.

Per battery, `CAPACITY_PROXY_DOMINATED` requires A3 (duration+energy removed) to
raise RMSE ≥25% and lower R²≥0.20 relative to A0. `ROBUST_MULTI_FEATURE_SIGNAL`
requires all A1/A2/A3 to retain RMSE within 10% and R² within 0.10 of A0. All
other patterns are `MIXED_FEATURE_DEPENDENCE`. The overall dependence is robust
only if both batteries are robust, proxy-dominated only if both are dominated;
otherwise it is mixed.

- **Stop criterion：** exactly one A0 capacity comparison and exactly the four
  A0–A3 ablations for the internally selected model. No follow-up tuning, no
  model expansion, no test, transfer, source selection, SSL/DG/CALCE.
- **Generalization limitation：** B0007/B0018 are development evidence only; any
  apparent high accuracy remains end-of-cycle and label-adjacent.

## G1–G7

| Gate | PASS / FAIL | Evidence / rationale | Reviewer decision |
|---|---|---|---|
| G1 PROBLEM | PASS | Feature Adequacy showed F1 recovery but unresolved capacity-versus-information contribution. | Direct isolation. |
| G2 PRIOR | PASS | Standard simple regressors and fixed ablation are established diagnostic methods. | No novel architecture. |
| G3 LEAKAGE | PASS | Feature list, ablations, configs, inner selection and gates freeze before validation; no labels as input. | Test prohibited. |
| G4 BASELINES | PASS | Includes F1 Ridge and all simple comparators; transfer not applicable. | Same target-only protocol. |
| G5 GENERALIZATION | PASS | Development-only wording; no external claim. | No CALCE. |
| G6 FALSIFIABILITY | PASS | Fixed capacity/dependence/stop rules. | No follow-up grid. |
| G7 COMPLEXITY | PASS | Four small baselines determine whether capacity adds value. | No deep temporal model. |

## Authorization

`AUTHORIZED_FOR_ONE_FROZEN_RUN` limited to this record and
`STRONG_BASELINE_PROTOCOL.md`.
