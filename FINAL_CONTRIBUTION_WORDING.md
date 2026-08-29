# Final Contribution Wording（可直接进入论文的冻结草案）

以下三条是本科论文允许使用的主贡献。措辞基于现有 NASA development/validation 证据，
不表示跨数据集 generalization，也不将 diagnostic evidence 升级为物理机制。

## Contribution 1 — 严格复现与稳健性审计

在明确的 chronological target-prefix protocol、multi-seed evaluation 与 locked-test
discipline 下，本研究对 G-MTC 式 SOH pipeline 进行实现与性能复现审计。结果表明：
在本地 NASA 极小样本开发/验证设置中，paper-style fusion 出现 predefined catastrophic
predictions，且未通过跨 target 的 qualification gate。该贡献是一个可审计的复现与
robustness finding，并不否定原论文在其他数据、协议或实现下的结果。

## Contribution 2 — 分层 failure attribution 与安全性区分

本研究将输出安全性与泛化准确性分离，并沿 fusion、component forecasting、representation
diagnostics 进行归因。bounded residual fusion 在对应验证实验中将 catastrophic count 从
25 降至 0，但没有恢复可靠的 cross-battery accuracy；oracle reconstruction 与
predicted-component reconstruction 的对照进一步表明，关键误差已在 fusion 前的 component
forecasting 层出现。sequence、capacity、GAN、Trend、component complexity 与 causal STL
路线被保留为固定 negative controls，而非被事后删除。

## Contribution 3 — 跨电池 negative-transfer 风险审计

在 B0005/B0006 source bank 与 B0007/B0018 targets 中，本研究显示 transfer utility
具有 source-target specificity，且 B0006 对两个已评估 targets 产生 negative-transfer
risk。进一步的两轮冻结 screening validation 表明，pure-HF nearest-neighbor selection
被拒绝，prefix-supervised screening 仅获得 battery-specific partial support。因此，简单
compatibility rule 不能被声称为通用的 source-selection algorithm。

## Secondary robustness finding（不得升级为主算法贡献）

bounded residual fusion 是 `ROBUSTNESS_ENGINEERING_FINDING`：它限制修正幅度并消除了
预定义 catastrophic outputs。它不得写成“提出了有效新 SOH model”“解决了 generalization”
或“原论文的 fusion formula”。

## 禁止替换成以下表述

- “提出一种经过验证的 SOTA SOH estimation algorithm。”
- “证明 source compatibility 可普遍预测 transfer utility。”
- “B0006 在所有场景均不适合作为 source。”
- “calibrated/few-shot transfer 是 zero-shot domain adaptation。”
- “HF shift 或 support mismatch 已证明物理/电化学负迁移机制。”
- “结果已跨数据集泛化。”
