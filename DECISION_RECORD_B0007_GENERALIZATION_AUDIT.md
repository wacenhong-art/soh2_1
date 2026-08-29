# Decision Record — B0007 Generalization Bottleneck Audit v1

> 本记录在本轮数据加载、diagnostic fit 与 validation 访问前冻结。已阅读
> `RESEARCH_GUARDRAILS.md`；本轮不产生可部署方法，locked test 禁止读取。

## 基本信息

- **Experiment name：** `B0007_GENERALIZATION_AUDIT_v1`
- **Date / author：** 2026-08-19 / repository maintainer
- **Proposal category：** diagnostic / reproducibility validation
- **Problem being solved：** Phase Performance Recovery I 中同一 F0 Ridge 在 B0018
  得到 RMSE 1.189 / R² 0.569、在 B0007 得到 RMSE 3.341 / R² -1.219。需区分早期标签量、
  early-to-late mapping shift、HF 信息限制与模型拟合限制，不能继续加特征或模型。
- **Supporting previous evidence：**
  `output/supervised_performance_recovery_v1/performance_recovery_metrics.csv`、
  `SUPERVISED_FEATURE_AUDIT.md` 与 `PERFORMANCE_RECOVERY_REPORT.md`。B0007 的 HF2/HF3
  train/validation SOH Pearson sign/level 变化已是描述性漂移证据，但尚未完成 prefix
  internal 与 validation internal 的可预测性对照。
- **Literature/theoretical basis：** rolling-origin evaluation、train/evaluation
  distribution and coefficient comparison、以及 label-budget sensitivity 是时间序列监督
  泛化诊断的基础分析；本轮不引入任何新模型或新损失。

## 冻结实验设计

- **Frozen hypothesis：** 若 B0007 的 fixed Ridge 在 early prefix 内 rolling origins 可
  预测、而 prefix-to-validation 失败，且 validation 内部仍可预测并存在预定义 drift，
  则最支持 `EARLY_TO_LATE_MAPPING_SHIFT`。反之由冻结的多证据规则决定，不做追随性实验。
- **Independent variable：** 仅诊断切分：early-prefix rolling origins、train-vs-validation
  descriptive comparison、validation-internal diagnostic split、以及 10/15/20% label budget。
- **Fixed variables：** B0007/B0018；F0 current HF1/HF2/HF3；B0007 Ridge alpha=10、
  B0018 Ridge alpha=1；输入和 target scaler 只 fit 本次每个 training subset；B0007/B0018
  train/validation boundaries `[0,33)/[33,67)` 和 `[0,25)/[25,51)`；MLP 仅为 validation
  internal diagnostic，hidden=32, one ReLU layer, AdamW lr=0.001, weight_decay=1e-5,
  max epochs=300, patience=50, seeds `[42,123,2024,3407,7777]`。
- **Baselines：** `TARGET_ONLY` F0 Ridge；`BEST_SIMPLE_BASELINE` 为已提交的 Performance
  Recovery I F0 Ridge。无需 `ALL_SOURCE`（本轮不涉及 transfer）。
- **Validation data：** next-20% 仅用于 diagnostic comparison；不得用于 hyperparameter
  selection、模型选择或正式性能提升主张。
- **Test access：** `FORBIDDEN`。所有 raw loading 限制为 `nrows=ValidationEnd`，所有
  rows 标记 `TestLoaded=False`。
- **Success criterion：** 所有指定诊断及指标文件生成；独立重算的 F0 Ridge RMSE/R² 与
  已提交结果在 `1e-6` 内一致；并由预注册归因规则给出一个 primary 与最多一个 secondary。
- **Failure criterion：** 基线无法复现时 `BASELINE_REPRODUCTION_FAILED`；诊断证据彼此
  不满足任何单一规则时 `BOTTLENECK_INCONCLUSIVE`。
- **Stop criterion：** 完成一次冻结诊断后停止；不增加特征、比例、模型、source、数据集，
  不读取 test，且不把 diagnostic fit 作为正式 predictor。
- **Generalization plan：** B0007/B0018 仅为 development evidence；本轮不作跨电池或
  外部泛化 claim，也不启动 CALCE。

## 冻结的归因规则

`EARLY_TO_LATE_MAPPING_SHIFT`：B0007 Ridge 的至少 3/4 rolling origins 为 R²>0，
且 prefix-to-validation R²<0，同时满足下列之一：validation-internal Ridge R²>0；或
validation-internal MLP 的五-seed mean R²>0 且至少 4/5 seeds R²>0；并且至少两项
HF feature 的 train-vs-validation Pearson change ≥0.50 或 Ridge standardized coefficient
发生符号翻转。

`TRAIN_PREFIX_TOO_SMALL`：label budget 10→15→20 的 B0007 outer diagnostic RMSE 严格
单调下降，且 10→20 相对下降≥15%，但不满足 mapping-shift 规则。

`HF_INFORMATION_LIMITATION`：B0007 rolling origins 至少 3/4 为 R²≤0，且 validation
internal Ridge R²≤0、MLP mean R²≤0，且不满足 mapping-shift 规则。

`MODEL_FIT_LIMITATION`：B0007 validation-internal MLP mean RMSE 比 Ridge 低≥20%、至少
4/5 MLP seeds 的 R²>0，但 Ridge validation-internal R²≤0，且不满足 mapping-shift 规则。

否则 `BOTTLENECK_INCONCLUSIVE`。若 primary 为 mapping shift，secondary 为
`TRAIN_PREFIX_TOO_SMALL` 仅当其 label rule 同时满足；其他情形 secondary=`NONE`。

## G1–G7 审查表

| Gate | PASS / FAIL | Evidence / rationale | Reviewer decision |
|---|---|---|---|
| G1 PROBLEM | PASS | Recovery I 直接显示 B0007/B0018 的同框架差异；四个候选瓶颈均由该 failure 导出。 | 仅归因诊断。 |
| G2 PRIOR | PASS | rolling-origin、coefficient/drift 与 label-budget sensitivity 均为基础监督泛化诊断。 | 无新算法。 |
| G3 LEAKAGE | PASS | validation SOH 只用于标为 DIAGNOSTIC_ONLY 的已冻结统计，绝不回流到模型/参数选择；test 未读。 | 无正式性能主张。 |
| G4 BASELINES | PASS | 保留 TARGET_ONLY 与已提交 BEST_SIMPLE_BASELINE；transfer 不适用。 | 全部重算。 |
| G5 GENERALIZATION | PASS | B0007/B0018 只作为 development evidence；无外部或普适 claim。 | 禁止 CALCE。 |
| G6 FALSIFIABILITY | PASS | 基线复现、归因阈值与停止条件在运行前冻结。 | 不允许 follow-up 调参。 |
| G7 COMPLEXITY | PASS | Ridge 为正式诊断；MLP 仅复用已运行的极小配置进行 validation 可拟合性检查。 | 不新增容量。 |

## 授权结论

- **Authorization status：** `AUTHORIZED_FOR_ONE_FROZEN_RUN`
- **Authorized scope only：** 本记录和 `B0007_GENERALIZATION_AUDIT_PROTOCOL.md` 中的
  frozen diagnostics。
- **Explicitly prohibited follow-ups：** feature engineering、Transformer/TimesNet/GAN/
  attention、transfer/source selection/SSL/DG/CALCE、任何 grid、locked test。
