# Reproduction Stop Audit

## Decision

`STOP_REPRODUCTION`

本审计只使用 Phase 0–10、两轮 source-selection validation、`REPRO_AUDIT.md`、
`paper_text.txt` 与既有代码/结果；未训练、未读取 locked test、未修改旧结果。

## Q1 — 是否仍有明确、可定位且论文有清楚依据的关键 mismatch？

**没有。** 原文明确给出的 component window=10、Bi-LSTM 9D/hidden=16/1 layer/
dropout=.3、BatchNorm1d、lr=.001、batch=32、patience=50 已被作为 paper baseline
核对。剩余的 fusion sequence、STL period、feature semantics 属于 `REPRO_DEFINED`；
`L_weight` 是 `UNVERIFIED_DISABLED`；60/20/20 与 first-20%-of-life small-sample 描述
之间是 `PAPER_AMBIGUOUS`。这些均不是一个能由原文唯一指定的 implementation error。

## Q2 — 修复剩余差异能否合理地显著改变结果？

**不能据论文证据作出这样的预期。** 补全上述未披露项只能产生新的复现定义；用它们追逐
reported metrics 会把复现转变为在已见 B0007/B0018 上的 reverse engineering。

## Q3 — 多个 Phase 是否表明既有模块的边际收益很低？

**是。**

- Phases 1–2：bounded residual 将 catastrophic count 从 25 降至 0，但仍未通过 accuracy
  gate；缩短 sequence 未形成 qualified configuration。
- Phases 3A–3B：parameters/sample 从 1793 降至 3.8，仍未通过 qualification。
- Phase 4A：oracle reconstruction 为 R2=1，predicted-component reconstruction 为
  R2=-13.019/-13.642，失效已在 fusion 前出现。
- Phases 4B–7：GAN、Trend、component capacity 与 prefix-stable STL alternatives 均未建立
  统一 remedy。

这些路线已由 `RESEARCH_GUARDRAILS.md` 记录为 `CLOSED_NOT_PRIMARY`。

## Q4 — 原论文是否存在无法恢复的 ambiguity 或未定义实现？

**是。** 原文未协调两种 target data regime，也未给出可复现 `L_weight` 定义。参数表不足
以唯一决定数据、STL、loss 与训练 contracts；本地严格 multi-seed/locked-test protocol
与论文 reported performance 的差距不能归因于单一代码 bug。

## Q5 — 继续复刻的收益是否高于直接进入性能增强？

**否。** 当前复刻已产生完整 failure-attribution evidence。继续复刻只能增加未验证 choices；
而性能增强也不自动获授权，因为 B0007/B0018 已是 development evidence，任何新 method
都须有独立文献理由、Decision Record 与不依赖已见结果的 evaluation design。

## Stop Gate

| Condition | Evidence | Result |
|---|---|---|
| 明确 paper mismatch 已基本排查 | `REPRO_AUDIT.md` 的 paper-defined contract | PASS |
| 剩余差异主要未充分说明 | `PAPER_AMBIGUOUS`、`REPRO_DEFINED`、`UNVERIFIED_DISABLED` | PASS |
| 多轮修正未恢复 paper-level performance | Phases 1–7 与 Final Evidence Ledger | PASS |
| 继续调参会成为 reverse engineering | 剩余项没有唯一 paper-defined value | PASS |
| 不再产生新的科学信息 | failure chain 已完成且路线已关闭 | PASS |

**Final reproduction decision：** `STOP_REPRODUCTION`。不存在
`ONE_REPRO_FIX_REMAINS`。本文件不授权训练或任何新 grid。
