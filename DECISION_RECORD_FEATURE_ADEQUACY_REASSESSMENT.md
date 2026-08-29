# Decision Record — Feature Adequacy Reassessment v1

> 本记录在任何新特征提取、模型拟合或 validation 访问前冻结。已阅读
> `RESEARCH_GUARDRAILS.md`；本轮是工程/信息充分性审计，不是创新或新方法。

## 基本信息

- **Experiment name：** `FEATURE_ADEQUACY_REASSESSMENT_v1`
- **Date / author：** 2026-08-19 / repository maintainer
- **Proposal category：** feature adequacy diagnostic / supervised baseline comparison
- **Problem being solved：** Recovery I 的 F0 Ridge 在 B0007 为 RMSE 3.341 / R² -1.219，
  在 B0018 为 RMSE 1.189 / R² 0.569；B0007 Generalization Audit 又不能把失败归于单一
  模型或标签量因素。因此检验当前 charge-only HF1/HF2/HF3 是否缺少稳定的当 cycle
  health information。
- **Supporting previous evidence：** `CURRENT_HF_AUDIT.md` 将审计既有定义；
  `SUPERVISED_BOTTLENECK_REPORT.md` 为 `BOTTLENECK_INCONCLUSIVE`；
  `PERFORMANCE_RECOVERY_REPORT.md` 显示 F1 temporal context 未恢复 B0007。
- **Literature/theoretical basis：** 放电时间、固定电压区间时间、温度/电压统计与
  电压-电流能量积分是常见且物理可解释的 battery health indicators。它们只来自当前
  cycle 已完成的原始 charge/discharge waveform，不依赖寿命终点或未来 cycle。

## 冻结特征与协议

- **F0：** 现有 `HF1/HF2/HF3` CSV；不修改原定义或将新特征重命名为旧 HF。代码审计已
  发现其全序列居中 Hampel 平滑与双向插值，因此 F0 是 `LEGACY_REFERENCE_NOT_STRICTLY_CAUSAL`。
- **F1：** 7 个预定义的 raw discharge health features：
  1. total discharge duration；2. first-downcrossing `4.0 V → 3.6 V` duration；
  3. discharge voltage mean；4. discharge voltage standard deviation；
  5. discharge temperature mean；6. discharge temperature standard deviation；
  7. trapezoidal discharge energy integral in Wh。
- **F2：** F0 + F1，共 10 dimensions。固定电压窗口只有一个 `4.0→3.6 V`，并且在
  运行前冻结；不扫描或调节窗口。
- **Causality and scope：** 每行仅使用关联 charge 和其紧随的 current discharge 的
  Voltage/Current/Temperature/Time。SOH label 的 Capacity 字段不进入 feature formula。
  这些是 *end-of-cycle* 特征；它们不能用于 discharge 结束之前的预测主张。MAT 容器的
  loader 必须在产生 `ValidationEnd` 个有效 rows 后停止遍历，绝不访问后续 raw cycle。
- **Missing/outlier rule：** 不做全序列平滑、居中滤波或双向插值。训练缺失值用该特征
  training subset median 填补，validation 只 transform；缺失率原样报告。
- **Models：** M0 = fixed target-specific Ridge（B0007 alpha=10, B0018 alpha=1）；
  M1 = 已冻结 one-layer MLP (`hidden=32`, ReLU, AdamW lr=0.001, wd=1e-5,
  300 epochs, patience=50, seeds `[42,123,2024,3407,7777]`）。无其他模型。
- **Data boundary：** B0007 `[0,33)` train / `[33,67)` validation；B0018 `[0,25)` /
  `[25,51)`。`TestLoaded=False`；test 禁止读取。

## 预注册判定

`FEATURE_ENRICHMENT_EFFECTIVE`：**仅 F1** 的同一简单 model 在 B0007 relative to
its F0 counterpart 将 RMSE 至少降低 15%（≤2.840），R²>0；B0018 的 corresponding RMSE
不高于 F0 的 105%；M1 满足时取五 seeds mean 且至少 4/5 seeds 的 B0007 R²>0；无
missing-data leakage 或 validation 后验 feature selection。

F2 必须完整报告以显示 legacy-HF combination 的行为，但因 F0 的预处理 provenance，
F2 永远不得作为无泄漏有效性结论或后续方法依据。

`FEATURE_ENRICHMENT_PARTIAL`：F1 在 B0007 RMSE 至少降低 15%，但 R²仍≤0，
或 B0007 R²>0 但未同时满足 B0018 non-degradation / stability 条件。

`CURRENT_RAW_FEATURES_INSUFFICIENT`：F1 未在 B0007 达到 15% RMSE 降低且 R²>0 的
门槛。该结论不授权继续堆叠手工特征。

- **Stop criterion：** 所有 3 feature sets × 2 fixed models × 2 batteries 一次完成后
  停止；不得添加窗口、特征、模型、标签、source、dataset 或访问 test。
- **Generalization plan：** B0007/B0018 仅是 development evidence；即使有效，也只可
  得出 `CURRENT_HF_SET_WAS_INADEQUATE`，不能声称新 feature 的泛化或创新。

## G1–G7 审查表

| Gate | PASS / FAIL | Evidence / rationale | Reviewer decision |
|---|---|---|---|
| G1 PROBLEM | PASS | Phase Recovery I 和 B0007 audit 均表明 current HF 的可预测性可能不足。 | 直接检验输入信息。 |
| G2 PRIOR | PASS | 所有七项是成熟 waveform health descriptors，固定窗口有明确电化学/工作区间含义。 | 不引入新结构。 |
| G3 LEAKAGE | CONDITIONAL PASS | F1 的特征/窗口/模型/阈值均先冻结，MAT traversal 在 prefix 截止；F0/F2 的中心平滑 provenance 已显式降级为 legacy reference，不能用于有效性 claim。 | 仅 F1 可通过无泄漏 Gate。 |
| G4 BASELINES | PASS | 包含 TARGET_ONLY F0 和已提交 BEST_SIMPLE_BASELINE；无 transfer。 | 相同 boundary。 |
| G5 GENERALIZATION | PASS | B0007/B0018 只为 development evidence。 | 无 CALCE。 |
| G6 FALSIFIABILITY | PASS | 三种互斥结论、15%门槛与停止规则已冻结。 | 不 follow-up。 |
| G7 COMPLEXITY | PASS | 仅 7 个预定义成熟 descriptors、两个既有简单模型、总维度≤10。 | 不自动筛选。 |

## 授权结论

- **Authorization status：** `AUTHORIZED_FOR_ONE_FROZEN_RUN`
- **Explicitly prohibited follow-ups：** window sweep、新 feature、PCA/自动选择、更多
  模型、Transformer/GAN/attention、transfer/SSL/DG/CALCE、locked test。
