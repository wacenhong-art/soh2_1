# Decision Record — Supervised Performance Recovery v1

> 本记录在任何本轮数据加载、训练或 validation 访问前冻结。已阅读
> `RESEARCH_GUARDRAILS.md`；locked test 始终禁止读取。

## 基本信息

- **Experiment name：** `SUPERVISED_PERFORMANCE_RECOVERY_v1`
- **Date / author：** 2026-08-19 / repository maintainer
- **Proposal category：** baseline / engineering performance recovery
- **Problem being solved：** 在现有合法的 target first-20% SOH 标签条件下，直接
  HF-to-SOH Ridge 对 B0007 的 validation RMSE 为 5.988、R² 为 -6.126，说明尚未
  确认失败究竟来自输入信息不足、简单时间上下文不足，还是模型拟合本身。
- **Supporting previous evidence：** Phase 6 的 `direct_soh_control.csv`：B0007 的
  HF-only Ridge 为 RMSE 5.988 / R² -6.126；B0018 为 RMSE 1.564 / R² 0.255。Phase 6
  同时观察到 HF–SOH relationship shift，且 train-to-validation feature range overlap
  有限。Phase 4–5 已排除 component/fusion 复杂度作为主要的通用修复路径。
- **Literature/theoretical basis：** 监督回归的输入消融是识别 information versus
  model-capacity bottleneck 的标准诊断。当前 HF、其严格过去变化、严格 trailing
  statistics 和已发生 cycle index 均在预测时可观测；本轮只比较线性、树与极小神经网络，
  不提出新方法或新机理。

## 冻结实验设计

- **Frozen hypothesis：** 对至少一个 target，F1（HF + 因果时间特征）或预定义的
  简单非线性模型可在不读取 test 的前提下，相比历史 HF-only Ridge 改善 validation
  RMSE；若不能，则其失败将作为输入/非平稳映射瓶颈的证据，而非继续堆叠特征的理由。
- **Independent variable：** 特征集 `F0` / `F1`，以及已冻结的六类简单模型与其小配置。
- **Fixed variables：** B0007/B0018；仅读取 index `< ValidationEnd`；target first-20%
  作为可标注训练前缀、next-20% 仅作外部 validation；HF1/HF2/HF3；相同 chronological
  rows；seeds `[42, 123, 2024, 3407, 7777]`；没有 source data、GAN、STL/component
  forecast、attention、transfer、domain adaptation 或 test labels。F1 只使用当前及过去
  HF/cycle，且所有 scalers 只在拟合区 fit。
- **Baselines：** `TARGET_ONLY` = F0 Ridge；`BEST_SIMPLE_BASELINE` = Phase 6 HF-only
  Ridge (B0007 5.988, B0018 1.564)。本实验不涉及 transfer，`ALL_SOURCE` 不适用。
- **Validation data：** next-20% chronological validation segment。候选配置仅以训练前缀
  内部 chronological validation 选择，随后在完整 first-20% 重拟合一次并评估 next-20%。
- **Test access：** `FORBIDDEN`。数据加载限定 `nrows=ValidationEnd`；所有输出写
  `TestLoaded=False`。
- **Success criterion：** `STRONG_BASELINE_RECOVERED` 需同一预定义 model family 在
  两 target 的训练前缀内部选择后满足：(i) B0007 的五种子 mean RMSE ≤ 5.389（历史
  Ridge 5.988 的至少 10% 改善）；(ii) B0018 five-seed mean RMSE ≤ 1.642（不高于历史
  Ridge 的 105%）；(iii) 两 target mean R² > 0；(iv) no catastrophic prediction
  (`SOH < 50%` 或 `SOH > 110%`)；(v) 无 seed-only claim。
- **Failure criterion：** 若没有一个 family 同时满足上述条件，则不称 strong recovery。
  若仅 B0007 达到 10% 改善且 B0018 不明显恶化，结论为 `PARTIAL_RECOVERY`；其余为
  `SUPERVISED_PERFORMANCE_NOT_RECOVERED`。
- **Stop criterion：** 完成本冻结表中的所有模型/配置/seed 后停止；F1 若没有跨 target
  一致改善，不得继续围绕 cycle/context 添加 feature。不得因结果更换模型、扩大网格、
  增加标签、访问 test 或启动 SSL/DG/transfer。
- **Generalization plan：** B0007/B0018 只提供 development evidence。即使 strong
  recovery，也只允许随后按新的 Gate 决定是否存在外部验证条件；本轮不作泛化 claim，
  不访问 CALCE。

## G1–G7 审查表

| Gate | PASS / FAIL | Evidence / rationale | Reviewer decision |
|---|---|---|---|
| G1 PROBLEM | PASS | Phase 6 发现 target-only HF Ridge 在 B0007 失败；F0/F1 与简单模型比较直接定位信息、时间上下文或拟合瓶颈。 | 直接诊断，不是新创新。 |
| G2 PRIOR | PASS | 因果 lag/delta/trailing summary 是监督时间序列的基础可观测输入；线性/树/小网络是预先固定诊断基线。 | 不引入流行复杂模型。 |
| G3 LEAKAGE | PASS | 特征定义、配置集、阈值、seeds、选择规则和停止规则均在 validation 前冻结；不用 validation/test SOH 生成任何 feature，scaler fit 仅训练行。 | test 禁止读取。 |
| G4 BASELINES | PASS | TARGET_ONLY F0 Ridge 与 Phase 6 best simple baseline 均保留；transfer 不适用。 | 必须完整报告。 |
| G5 GENERALIZATION | PASS | B0007/B0018 明确限为 development evidence；无外部泛化声明。 | 不授权 CALCE。 |
| G6 FALSIFIABILITY | PASS | 定量 success/failure/stop criterion 已冻结。 | 不允许 follow-up tuning。 |
| G7 COMPLEXITY | PASS | 仅六类简单模型，用于判断 simple model 是否已足够；不增加 fusion/Transformer/GAN。 | 参数规模受限。 |

## 授权结论

- **Authorization status：** `AUTHORIZED_FOR_ONE_FROZEN_RUN`
- **Authorized scope only：** 执行 `PERFORMANCE_RECOVERY_PROTOCOL.md` 规定的 F0/F1、
  六类简单模型、预定义配置与五 seeds，并生成规定报告。
- **Explicitly prohibited follow-ups：** 新 feature、再调配置、扩大标签前缀、source
  selection、transfer、SSL、DG、CALCE、locked test 读取。
- **Required artifact paths：** `SUPERVISED_FEATURE_AUDIT.md`,
  `PERFORMANCE_RECOVERY_PROTOCOL.md`, `output/supervised_performance_recovery_v1/`
  下的 metrics、feature ablation、report、config、manifest 与 training history。
