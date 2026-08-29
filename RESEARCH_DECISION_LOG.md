# SOH 研究决策日志

本日志记录已冻结的研究决策。它不是实验结果重写区；任何新条目必须引用对应的
Decision Record、冻结配置和 Git commit。

## 2026-08-18 — 无监督 compatibility score：已关闭

- **Method hypothesis：** source-to-target pure-HF nearest-neighbor distance 能预测
  transfer utility。
- **Formal result：** `COMPATIBILITY_AWARE_SELECTION_NOT_SUPPORTED`。
- **Evidence：** B0007/B0018 均自动选择 B0006；selected-source 在 zero-shot 与
  calibrated 的四个正式对照中都差于 all-source。
- **Decision：** `CLOSED_UNSUPPORTED`，`LOCKED_TEST_DECISION=DO_NOT_PROCEED`。
- **Permanent constraint：** 禁止在 B0007/B0018 上借 Wasserstein、MMD、DTW、
  correlation 或距离组合继续寻找能选中 B0005 的公式。

## 2026-08-18 — Prefix-supervised source screening：部分关闭

- **Method hypothesis：** 用 source-only Ridge 在 target first-20% prefix 上的 RMSE
  筛查 calibrated transfer 的 source。
- **Formal result：** `PREFIX_SUPERVISED_SOURCE_SCREENING_PARTIALLY_SUPPORTED`。
- **Evidence：** B0018 选中 B0005，与 oracle 一致，C2 RMSE 1.377 优于 all-source
  1.565；B0007 选中 B0006，但 oracle 为 B0005，C2 RMSE 2.654 差于 all-source 0.589。
- **Decision：** `CLOSED_PARTIAL`，`LOCKED_TEST_DECISION=DO_NOT_PROCEED`。
- **Permanent constraint：** 禁止在 B0007/B0018 修改 score 或设计第三种 score。
  仅允许将完全不变的冻结协议带到独立新 target/外部数据作一次预注册 confirmation；
  该动作必须有新的完整 Decision Record，且不得用外部数据调参。

## 2026-08-18 — Locked test 与论文定位

- **Test state：** `LOCKED_TEST_REMAINS_UNOPENED`；当前没有通过 validation 资格门的
  冻结主方法，因此不授权读取 test。
- **Thesis positioning：** NASA-only reproduction failure attribution 与 cross-battery
  negative-transfer audit。
- **Reproduction status：** implementation reproduction 较完整；
  paper-reported performance reproduction 未成功复现。
- **Dataset Gate：** 成功的 NASA 预注册方法才可常规进入 CALCE external validation。
  被拒绝的 NASA 方法不得去 CALCE 寻找正结果；本次 partial frozen protocol 的独立确认
  是唯一例外，且不是调参或第三种 source-selection hypothesis。

## 当前授权清单

```text
NO_NEW_MODEL_EXPERIMENT_AUTHORIZED
NO_NEW_GRID_AUTHORIZED
NO_NEW_SOURCE_SELECTION_SCORE_AUTHORIZED
NO_LOCKED_TEST_ACCESS_AUTHORIZED
```

任何新提案必须从 `EXPERIMENT_DECISION_TEMPLATE.md` 开始，并经
`RESEARCH_GUARDRAILS.md` 的 G1–G7 审查。

## 2026-08-19 — Supervised performance recovery：单次冻结基线诊断

- **Decision Record：** `DECISION_RECORD_SUPERVISED_PERFORMANCE_RECOVERY.md`。
- **Authorization：** `AUTHORIZED_FOR_ONE_FROZEN_RUN`，仅限 F0/F1、六类预定义简单
  模型、小配置表与固定五 seeds；不是新创新或 source-selection 路线。
- **Boundary：** B0007/B0018 的 first-20% target labels 训练，next-20% validation；
  `LOCKED_TEST_REMAINS_UNOPENED`。先在训练前缀内做 chronological selection，再以完整
  前缀重拟合；外部 validation 不能改变模型、特征或超参数。
- **Stop rule：** 全表一次执行后只报告 `STRONG_BASELINE_RECOVERED`、`PARTIAL_RECOVERY`
  或 `SUPERVISED_PERFORMANCE_NOT_RECOVERED`，禁止 follow-up feature/model search。

## 2026-08-19 — Supervised performance recovery：部分恢复后停止

- **Decision Record：** `DECISION_RECORD_SUPERVISED_PERFORMANCE_RECOVERY.md`；结果位于
  `output/supervised_performance_recovery_v1/`。
- **Formal result：** `PARTIAL_RECOVERY`。F0 Ridge 在 B0007 将历史 RMSE 5.988 降至
  3.341，但 R² 仍为 -1.219；B0018 从 1.564 改善至 1.189，R² 为 0.569。没有任何
  configuration 在两个 target 上同时达到 `R² > 0`。
- **F1 conclusion：** 因果 temporal context 未形成跨 target 的一致改善；相对 F0 Ridge，
  B0007 的 RMSE 为 3.556，B0018 为 1.755。不得据此继续添加 context feature。
- **Audit boundary：** 76 条 metrics 和 2,160 条 predictions 均为 `TestLoaded=False`；
  所有 17 个候选配置已按固定 seeds/内部时间选择完成。
- **Decision：** 本轮停止。最强诊断为 `NONSTATIONARY_MAPPING`，次级为
  `TEMPORAL_CONTEXT_INSUFFICIENT`；不得称 successful estimator，不自动授权新的
  feature/model/grid/transfer/SSL/DG/CALCE 实验。任何最小性能修复仍须新的完整 Gate 与
  人工确认。

## 2026-08-19 — B0007 generalization bottleneck：冻结诊断后停止

- **Decision Record：** `DECISION_RECORD_B0007_GENERALIZATION_AUDIT.md`；结果位于
  `output/b0007_generalization_audit_v1/`。
- **Baseline reproduction：** B0007 Ridge(alpha=10) 与 B0018 Ridge(alpha=1) 的 RMSE/R²
  均在 `1e-6` 内复现；所有输出为 `TestLoaded=False`。
- **Formal conclusion：** `PRIMARY_BOTTLENECK=BOTTLENECK_INCONCLUSIVE`；
  `SECONDARY_BOTTLENECK=NONE`；`NEXT_STAGE=STOP_AND_REASSESS`。
- **Reason:** B0007 有显著的 feature/coefficient drift 与 prefix-to-validation bias，
  但 early-prefix rolling 仅 2/4 正 R²，validation 内部时间预测及固定 MLP 仍失败，且
  10→15→20% label budget 不单调改善。因此不得将任一单一机制写成已证实原因。
- **Decision：** 不授权 stage repair、feature enrichment、label-efficient repair 或
  model-fit repair；不得继续在 B0007/B0018 上做 follow-up 诊断/调参，等待人工审查。

## 2026-08-19 — Feature adequacy reassessment：raw health information 有效

- **Decision Record：** `DECISION_RECORD_FEATURE_ADEQUACY_REASSESSMENT.md`；结果位于
  `output/feature_adequacy_reassessment_v1/`。
- **Formal result：** `FEATURE_ENRICHMENT_EFFECTIVE`，但仅 F1 是无全序列平滑的
  leakage-safe feature set。F1 Ridge 将 B0007 从 RMSE 3.341 / R² -1.219 改善至
  2.034 / 0.177，将 B0018 从 1.189 / 0.569 改善至 0.375 / 0.957；所有结果
  `TestLoaded=False`。
- **Critical scope:** F1 使用当前同一放电 cycle 完成后的 duration/energy/voltage/
  temperature descriptors，属于 end-of-cycle health estimation，且与容量标签邻近；
  不得声称提前预测、独立机制或泛化。F0/F2 含 legacy centered smoothing，永久标为
  `LEGACY_REFERENCE_NOT_STRICTLY_CAUSAL`，F2 的较高结果不得作为正式方法依据。
- **Decision：** `NEXT_STAGE=SUPERVISED_PERFORMANCE_RECOVERY` 仅为人工审查后的 gate，
  不自动授权新的 feature/model 实验；不得继续扩展手工特征或访问 test。

## 2026-08-21 — Strong baseline & raw-feature contribution isolation：任务有效性重审

- **Decision Record：** `DECISION_RECORD_STRONG_BASELINE_RAW_ABLATION.md`；唯一冻结运行的
  结果位于 `output/strong_baseline_raw_ablation_v1/`。
- **Formal result：** `STRONG_SUPERVISED_BASELINE_RECOVERED`。内层训练前缀选择的
  A0 Ridge 在 B0007 达到 RMSE 0.416 / R² 0.966，B0018 为 0.204 / 0.987；两者无
  catastrophic output。Experiment-B 按冻结规则选择 ElasticNet，A0 为 B0007 0.796 /
  0.874、B0018 0.200 / 0.988；该 family selection 完全来自内层前缀而非 outer validation。
- **Feature-dependence result：** `CAPACITY_PROXY_DOMINATED`。移除 duration 与 energy 的
  A3 后，B0007 RMSE 0.796→2.713、R² 0.874→-0.463；B0018 RMSE 0.200→1.300、R²
  0.988→0.485。两块电池均满足预注册的 proxy-dominance 门槛。
- **Scope and integrity：** 48 条 inner-selection、16 条 A0 和 8 条 A0–A3 结果均为
  `TestLoaded=False`；随机 MLP 运行固定 5 seeds。duration/energy 是当前完成放电 cycle
  的合法 label-adjacent 输入，不是 SOH/future-label leakage，但该任务不能声称提前预测、
  RUL、跨数据集泛化或算法创新。
- **Decision：** `NEXT_STAGE=TASK_VALIDITY_REASSESSMENT`。本路线按停止条件关闭；不得基于
  这些 validation 结果增加特征、改 ablation、再调 Ridge/ElasticNet/MLP 或启动后续模型实验。
