# 本科论文 Master Writing Plan（证据冻结版）

## 0. 写作授权与边界

本计划仅重组既有的 NASA development/validation 证据，不引入新算法、训练、CALCE
运行或 locked-test 访问。其上位约束为 `RESEARCH_GUARDRAILS.md`；最终实验状态为
`EXPERIMENTAL_WORK_COMPLETE` 与 `LOCKED_TEST_REMAINS_UNOPENED`。

**论文定位：** `FINAL_THESIS_POSITIONING = C`，即“NASA 小样本条件下 G-MTC
复现失效归因与跨电池负迁移审计”。论文不是一个已验证成功的新 SOH estimator，更不
是 SOTA 或跨数据集 generalization 论文。

## 1. 中心论题与四个固定 Research Questions

**中心论题：** 在明确的 NASA 小目标前缀协议下，G-MTC 式 STL-component-fusion
pipeline 未形成稳定的跨电池 SOH estimator；逐层审计表明，受限残差只能改善输出安全性，
而 component forecasting、HF generalization 与 source-specific transfer risk 仍限制
泛化，且两种简单 source-screening 规则均不足以可靠预测 transfer utility。

| RQ | 冻结问题 | 回答范围 | 主要证据 |
|---|---|---|---|
| RQ1 | 论文式 G-MTC 在 NASA 极小样本条件下能否稳定复现？ | 仅本地声明的 target-prefix 开发/验证协议；不推及原论文所有设置。 | Phase 0、Phase 1、`FINAL_EVIDENCE_LEDGER.csv` |
| RQ2 | 性能失败主要发生在哪一层：fusion、component forecasting、representation 还是 domain shift？ | 给出分层失效链与证据强度，不宣称单一物理因果。 | Phases 1、4A、6、7 |
| RQ3 | 序列缩短、容量缩小、去 GAN、因果分解等直觉改进是否解决主要问题？ | 判断它们在固定诊断中是否为主要 remedy，而不是否定所有未来版本。 | Phases 2、3A、3B、4B、5、7 |
| RQ4 | 为什么 cross-battery transfer 出现 source-specific negative transfer，简单 compatibility screening 能否可靠避免？ | 仅 B0005/B0006 source bank 与 B0007/B0018 targets；screening 结论不泛化。 | Phases 8、9、两轮冻结 selection validation |

## 2. 主叙事链与证据强度

| 叙事步骤 | 证据状态 | 可写入正文的结论 | 证据锚点 |
|---|---|---|---|
| 原论文复现 | INFERENCE | 本地 implementation reproduction 较完整，但 paper-reported performance 未成功复现，且协议仍有 `PAPER_AMBIGUOUS` 边界。 | `REPRO_AUDIT.md`；Final Evidence Ledger |
| Paper-style fusion instability | CONFIRMED | 在审计的极小样本协议中，paper-style fusion 出现 predefined catastrophic validation outputs。 | Phase 1；Ledger |
| Bounded residual safety guard | CONFIRMED | 受限残差将观测 catastrophic count 从 25 降至 0，但未恢复可靠泛化。 | Phases 1–2；Ledger |
| Component forecasts fail before fusion | CONFIRMED | Oracle STL reconstruction 准确，而 predicted-component reconstruction 在 fusion 前已失效。 | Phase 4A；Ledger |
| GAN / Trend / capacity 不是统一主因 | CONFIRMED / REJECTED | 这些固定对照没有建立稳健 remedy；Trend 重要但非唯一瓶颈。 | Phases 2–5；Ledger |
| STL prefix instability | SUPPORTED / REJECTED | prefix instability 存在，但 causal prefix-stable alternatives 未恢复固定预测器表现。 | Phases 6–7；Ledger |
| HF train-to-validation shift | SUPPORTED | 协变量与关系 shift 是 plausible upstream stressor，不能写成 electrochemical causality。 | Phase 6；Ledger |
| Transfer is battery-specific | CONFIRMED | transfer benefit 随 source-target pair 改变，校准结果不称 zero-shot。 | Phase 8；Ledger |
| B0006 negative-transfer risk | CONFIRMED | 在审计 source bank 与两个 targets 中，B0006 产生 source-specific negative-transfer risk。 | Phase 9；Ledger |
| Unsupervised screening | REJECTED | pure-HF nearest-neighbor rule 未预测 transfer utility。 | Final Method Validation |
| Prefix-supervised screening | PARTIALLY_SUPPORTED | 它在 B0018 有效、B0007 失效，不能构成 cross-target algorithm claim。 | Prefix-supervised Validation |
| 综合结论 | INFERENCE | 小样本跨电池 SOH transfer 不能简单依赖更多 source 或表面 HF 相似度。 | 全部冻结证据；`CLAIM_BOUNDARIES.md` |

## 3. 论证骨架

1. **复现审计不是算法宣传。** 先声明本地协议、test lock、multi-seed 和 simple baseline，
   再报告 performance reproduction 未成功，避免把不可比协议中的高分作为参照。
2. **安全性与准确性必须拆开。** bounded residual 的价值是消除失控输出，不是修复 generalization。
3. **失效链由下游回溯到上游。** component forecast 在 fusion 前失败，故仅调整 fusion
   sequence 或 capacity 不构成主要解释；GAN、Trend、STL 的固定负控制进一步排除直觉性归因。
4. **transfer 不是无条件增益。** B0005/B0006 的结果提示 source identity 会改变结果；
   两种预注册 screening 的失败/partial 结果限定了 compatibility claim。
5. **结论保持 NASA-only。** 支持的是方法学审计和风险证据，而非物理机制、通用 source
   ranking 或 cross-dataset generalization。

## 4. 正文写作顺序

按科学问题而非 Phase 编号叙述：第 3–4 章建立可审计复现与失效证据，第 5 章解释
representation/predictability 压力，第 6 章转入 transfer risk，第 7 章综合但不升级因果。
Phase 编号只在表注、方法附录与结果溯源中出现。

## 5. 写作停止条件

- 不为获得正结果重新设计 source-selection score、模型或 loss。
- 不读取 locked test，也不将 CALCE 当作 NASA 失败后的补救。
- 任一段若需要跨数据集、物理机制、universal source 或 effective new algorithm 表述，
  必须删除或降级为 future work / INCONCLUSIVE。
- 本计划完成后等待人工确认；不自动开始 Chapter 1 正文。
