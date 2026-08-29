# Thesis Detailed Outline（写作前冻结版）

## 结构选择

采用“**扩展 IMRaD + failure-attribution audit**”结构。它保留工程论文的可复现实验主线，
但将结果按科学问题组织，不按 Phase 编号流水账组织。建议正文约 18,000–22,000 字；
参考文献、附录和图表说明不计入该范围。

## 1 Introduction（约 1,800–2,100 字）

**目的：** 将问题界定为小样本跨电池 SOH 的可复现性、稳健性与 negative-transfer risk，
而不是提出新 SOTA。

- 1.1 Background：SOH estimation 的工程意义与 cross-battery 数据受限背景。
- 1.2 Problem Statement：复杂 pipeline 的报告性能不等于在严格 target-prefix protocol 下
  的可靠性；需要 test-lock 与 baseline 对照。
- 1.3 Research Questions：逐字采用 RQ1–RQ4。
- 1.4 Contributions：只采用 `FINAL_CONTRIBUTION_WORDING.md` 的三条主贡献。

**证据/图表：** 无结果表；仅引用原论文与后续文献。说明本研究的 NASA-only 边界。
**过渡：** 从“为何需要审计”过渡至“审计的原始框架与协议”。

## 2 Related Work（约 2,400–2,800 字）

**目的：** 建立文献语境，但不以文献替代本研究证据。

- 2.1 SOH estimation：特征驱动与深度时序模型。
- 2.2 Small-sample learning：小样本、跨工况与稳健性评价。
- 2.3 STL/decomposition-based SOH：分解、component forecasting 与 fusion。
- 2.4 Cross-battery transfer and negative transfer：source choice、domain similarity 与
  calibrated/few-shot 和 zero-shot 的概念边界。

**证据/图表：** `LITERATURE_GAPS.md` 的检索清单；不报告本项目数值。
**过渡：** 现有方法动机合理，但需要在声明清楚的复现协议下检验。

## 3 Reproduction Framework and Experimental Protocol（约 3,000–3,400 字）

**目的：** 使所有后续结论可审计，先写清楚论文定义、复现定义和未验证项。

- 3.1 Original G-MTC framework：STL components、component predictors、GAN 与 fusion 的
  角色；不得把 `L_weight` 的实现猜测写成论文原式。
- 3.2 NASA dataset and HF extraction：sources B0005/B0006 与 targets B0007/B0018 的角色。
- 3.3 Reproduction ambiguities：60/20/20 与 first-20% 描述冲突，标为 `PAPER_AMBIGUOUS`。
- 3.4 Small-sample protocol：chronological target-prefix development/validation，component
  window 与 multi-seed 配置。
- 3.5 Baselines and metrics：Mean、persistence、STL/additive、paper fusion；RMSE、MAE、
  MAPE、R2 与 catastrophic definition。
- 3.6 Test-lock and multi-seed evaluation：明确 `LOCKED_TEST_REMAINS_UNOPENED`。

**证据/表：** 表 A（baseline contract）；`REPRO_AUDIT.md`；protocol manifests。
**过渡：** 协议固定后，先检验 paper-style pipeline 是否在 development/validation 中稳定。

## 4 Reproduction Results and Failure Isolation（约 3,400–3,900 字）

**目的：** 回答 RQ1，并定位由 fusion 到 component forecasting 的失效层。

- 4.1 Paper-style baseline：报告多 seed 与 simple baseline，不以单一 best seed 排名。
- 4.2 Fusion failure：展示 paper-style fusion catastrophic output 与 qualification failure。
- 4.3 Residual safety guard：说明 bounded residual 的安全作用和准确性边界。
- 4.4 Sequence/capacity ablations：用紧凑负控制总结，避免重复网格细节。
- 4.5 Component attribution：以 oracle reconstruction 与 predicted-component reconstruction
  说明 error 已在 fusion 前出现。

**证据/表图：** 表 A、B、C、E；图 1、图 2、图 3（见 `FIGURE_TABLE_MAP.md`）。
**核心结论：** 安全 guard 不等于 generalization repair；单独 fusion tuning 不是主要解决路径。
**过渡：** 若 component forecast 已失效，需要检查 representation 与 predictability 压力。

## 5 Representation and Predictability Analysis（约 2,900–3,300 字）

**目的：** 回答 RQ2–RQ3 的上游部分，区分已观察 shift 与不可声称的因果机制。

- 5.1 GAN attribution：REAL_ONLY vs REAL+GAN，报告其 battery-specific effect。
- 5.2 Component model adequacy：复杂和轻量 alternatives 都未建立稳健 remedy。
- 5.3 HF distribution shift：报告 KS 与 relationship-shift diagnostic，使用“associated with”。
- 5.4 STL prefix instability：稳定性证据与 causal alternatives 的 null result 并置。
- 5.5 Direct HF→SOH controls：作为 component pipeline 的诊断控制，不包装为最终赢家。

**证据/表图：** 表 D；表 E 的 representation 子行；图 4、图 5。
**核心结论：** GAN、Trend、capacity 和 STL instability 都不能单独解释或修复失效；
HF shift 是 plausible stressor，而非物理因果证明。
**过渡：** representation 压力之外，source identity 是否进一步改变 transfer outcome？

## 6 Cross-Battery Transfer and Negative Transfer（约 3,300–3,800 字）

**目的：** 回答 RQ4，并将 source-selection 的负结果保留为主结论的一部分。

- 6.1 Source-only and calibrated transfer：严格区分 target-only、source-only zero-shot
  与 calibrated transfer。
- 6.2 Source-specific transfer：B0005-only、B0006-only、all-source，展示 B0006 risk。
- 6.3 Multivariate support mismatch：作为关联性 diagnostic，不宣称 physical causality。
- 6.4 Unsupervised source-selection failure：冻结 nearest-neighbor protocol 的 formal rejection。
- 6.5 Prefix-supervised screening result：B0018 partial benefit 与 B0007 failure 并列；
  C3 oracle 仅 diagnostic，不是方法 winner。

**证据/表图：** 表 F、G、H；图 6、图 7。
**核心结论：** 更多 source 和表面 HF similarity 均不足以保证 transfer utility；两种规则
不支持通用 source-selection claim。
**过渡：** 将各层证据整合为方法学含义，同时明确不可跨越的推论边界。

## 7 Discussion（约 2,100–2,500 字）

**目的：** 整合失效链，回应反驳而不新造机制。

- 7.1 What actually caused failure：使用“layered evidence”，不声称单一充分原因。
- 7.2 Why intuitive fixes failed：解释这些是固定 contracts 下的 negative controls。
- 7.3 Implications for small-sample SOH：强调安全性、upstream predictability 与 source
  auditing 的优先级。
- 7.4 Methodological lessons：test lock、multi-seed、baseline、calibrated/zero-shot 命名。

**证据/图表：** 图 8 failure-chain synthesis；Final Evidence Ledger。
**核心结论：** 技术贡献是审计与风险识别，不是成功深度算法。
**过渡：** 从发现过渡至其可推广边界。

## 8 Limitations and Future Work（约 1,200–1,500 字）

**目的：** 保护所有主结论的有效范围。

- 8.1 NASA-only、两 source、两 target、development/validation-stage scope。
- 8.2 paper-protocol ambiguity、no locked-test evaluation 与其理由。
- 8.3 未识别 physical/electrochemical mechanism。
- 8.4 Future work：只有被冻结、通过 Gate 的方法才可进入 independent NASA target 与 CALCE
  external validation；`CLOSED_PARTIAL` 路线仅可做完全不变协议的预注册 confirmation。

## 9 Conclusion（约 700–900 字）

**目的：** 直接回答四个 RQ，复述贡献与边界。

结论只重申：paper-style fusion 的不稳定性、residual 的安全发现、component forecast
upstream failure、source-specific negative-transfer risk、two screening rules 的限制，以及
`LOCKED_TEST_REMAINS_UNOPENED`。不增加任何新结果或算法主张。

## 章节证据覆盖与过渡检查

| 章节 | 服务 RQ | 主要冻结来源 | 结果性质 |
|---|---|---|---|
| 1–3 | framing | Final positioning、claim boundaries、REPRO_AUDIT | scope/protocol |
| 4 | RQ1、RQ2 | Phases 1–4A | confirmed + rejected controls |
| 5 | RQ2、RQ3 | Phases 4B–7 | supported/rejected diagnostics |
| 6 | RQ4 | Phases 8–9 + two validations | confirmed/rejected/partial |
| 7–9 | synthesis | Final Evidence Ledger | bounded inference + limitation |
