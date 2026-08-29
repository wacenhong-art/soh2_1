# SOH 项目长期研究红线

## 0. 强制入口

本文件是本仓库未来研究决策的唯一长期约束来源，不得依赖聊天记忆替代。任何新的
innovation、模型修改、transfer method、source-selection score、domain adaptation、
dataset extension 或 hyperparameter experiment，必须先完整阅读本文件，并创建一份
`EXPERIMENT_DECISION_TEMPLATE.md` 的实例。未完成 Gate 不得训练。

当前默认状态：

```text
LOCKED_TEST_REMAINS_UNOPENED
EXPERIMENTAL_WORK_COMPLETE
```

## 1. 已冻结事实与论文真实性边界

- `IMPLEMENTATION_REPRODUCTION`：较完整；论文参数、`REPRO_DEFINED` 与
  `UNVERIFIED` 边界已审计。
- `PERFORMANCE_REPRODUCTION`：未成功。论文报告的性能未在当前 NASA 极小样本协议下
  复现；不得改写为“已成功复现论文性能”。
- paper-style pipeline 曾出现大量负 R2 与 catastrophic output。
- bounded residual fusion 将观测到的 catastrophic count 从 25 降至 0，但未恢复可靠
  泛化；它只能是 `ROBUSTNESS_ENGINEERING_FINDING`，不是成功 estimator 的主方法。
- fusion sequence length 与 fusion capacity 都不是主瓶颈；component forecast 在进入
  fusion 前已失败。
- GAN 不是统一主因；Trend 重要但不是唯一瓶颈；轻量 component model 没有一致替代
  TimesNet；STL prefix instability 存在但不足以解释 forecast failure。
- direct HF-to-SOH 相对 component pipeline 较好，但 B0007 仍存在严重泛化困难。
- transfer 存在 battery-specific effect：B0005 是有限 source bank 中较有效的开发证据，
  B0006 对两个 target 均有 negative-transfer 风险；这不等同于普适 source 排名。
- 无监督 HF 最近邻选源的正式结论为
  `COMPATIBILITY_AWARE_SELECTION_NOT_SUPPORTED`。
- prefix-supervised source screening 的正式结论为
  `PREFIX_SUPERVISED_SOURCE_SCREENING_PARTIALLY_SUPPORTED`：B0018 有效，B0007 选错
  source，不能作为跨 target 的通用方法。

后续创新应来自系统 failure attribution，而不是假设论文性能已经成功复现后再锦上添花。

## 2. 创新方向七个 Gate

每个新实验必须在运行前逐项写入 Decision Record。

| Gate | 必须回答的问题 | FAIL 时的动作 |
|---|---|---|
| G1 PROBLEM | 是否直接解决已观测 failure？必须写成“Phase X 发现 __，因此方法 __ 解决 __。” | `REJECT` |
| G2 PRIOR | 是否有明确理论或文献依据？不得仅因 Mamba、Transformer、新 attention 或新 loss 流行而尝试。 | 先文献审查；不运行实验 |
| G3 LEAKAGE | 方法规则是否独立于 validation/test SOH、历史 B0005/B0006 优劣和已见结果？ | `REJECT` |
| G4 BASELINES | 是否至少含 `TARGET_ONLY`、涉及 transfer 时的 `ALL_SOURCE`、以及 `BEST_SIMPLE_BASELINE`？ | 补齐后才能运行 |
| G5 GENERALIZATION | B0007/B0018 是否仅作为 development evidence？最终泛化是否留给新 target/第二数据集？ | 降级 claim 或拒绝 |
| G6 FALSIFIABILITY | 是否预先冻结成功、失败与停止条件？ | 不得运行 |
| G7 COMPLEXITY | 新复杂度是否必要，且 simple baseline 不能达到同一目的？ | 不得为“创新感”增加网络 |

`G1/G2/G3` 任一项为 FAIL 时，Decision Record 必须标为：

```text
EXPERIMENT_NOT_AUTHORIZED
```

## 3. 七条硬红线

1. 不得根据 B0007/B0018 validation 结果反复重设计 source-selection score。
2. 不得用 test 做 method selection、score selection、hyperparameter tuning 或
   research-direction selection。
3. B0007/B0018 已被大量方法开发使用；它们不能单独支持 generalization claim。
4. 任何最终 SOH 方法若 `worst-target R² < 0`，不得称为 successful estimator；只能称
   为 failed regime 下的 relative improvement。
5. 不得为了获得正结果增加 target label 比例、新 source、新模型、新 distance metric 或
   新数据集；除非实验前已有独立研究理由、完整 Gate 和冻结停止条件。
6. CALCE 或 Tsinghua 的唯一研究目的只能是 external validation，不能作为 NASA 方法
   失败后的换数据集救援。
7. `NOT_SUPPORTED` 必须触发已预注册的停止条件；禁止使用“效果一般，再调一点”或
   “换个指标可能成功”继续 hypothesis shopping。

## 4. 已关闭与受限路线

### `CLOSED_UNSUPPORTED`

**无监督 pure-HF nearest-neighbor source selection** 已被拒绝。不得在当前
B0007/B0018 开发集上通过 Wasserstein、MMD、DTW、correlation、加权组合或其他距离
公式继续寻找恰好选中 B0005 的规则。这些变体属于同一被拒绝的方法假设，不是新创新。

### `CLOSED_PARTIAL`

**prefix-supervised source screening** 仅得到 battery-specific partial evidence。禁止在
B0007/B0018 上设计第三、第四种 score，或根据 block/validation/oracle 结果修改既有
score。允许的唯一后续动作是：在新的独立 target 或外部数据上，对**完全不变**的冻结
协议做一次预注册 confirmation；不得改 score、features、source bank、target label 比例、
Ridge alpha、阈值或模型。该 confirmation 前仍须通过全新的 Decision Record。

### `CLOSED_NOT_PRIMARY`

下列固定诊断未支持其作为主创新：fusion sequence optimization、fusion capacity
reduction、GAN removal、Trend-only replacement、lightweight component replacement 与
causal STL redesign。它们可以作为论文负控制讨论，不得重新作为调参路线。

## 5. Dataset Gate

```text
NASA = method development

NASA 上得到 SUPPORTED 的预注册方法
  -> FREEZE METHOD
  -> CALCE external validation
  -> 若 CALCE 支持，可考虑 Tsinghua 作为更强 external validation

NASA 上得到 NOT_SUPPORTED 的方法
  -> STOP METHOD HYPOTHESIS
  -> 不得去 CALCE 继续调该方法
  -> 重新进行研究方向审查
```

`PARTIALLY_SUPPORTED` 不自动进入 CALCE。它只能按第 4 节的 `CLOSED_PARTIAL` 例外，
在不改变冻结协议的情况下进行一次独立预注册确认；该确认不是换数据集寻找正结果。

## 6. 结果后唯一合法决策

每个结束的预注册实验只能使用以下状态：

```text
SUPPORTED
PARTIALLY_SUPPORTED
NOT_SUPPORTED
INCONCLUSIVE
```

- `SUPPORTED`：冻结方法；先审查外部验证是否满足 G5，不能立即再调参。
- `PARTIALLY_SUPPORTED`：不自动修改方法；人工审查后仅可走已写明的独立确认路径。
- `NOT_SUPPORTED`：执行停止条件并关闭方法假设。
- `INCONCLUSIVE`：说明证据为什么不足；不得把不确定性包装成成功。

## 7. 论文真实性规则

论文必须严格区分：

| 标签 | 当前含义 |
|---|---|
| `IMPLEMENTATION_REPRODUCTION` | 实现与数学/协议边界的复现审计较完整 |
| `PERFORMANCE_REPRODUCTION` | 未成功复现 paper-reported performance |
| `METHOD_DEVELOPMENT` | B0007/B0018 上的 development/validation evidence，不是泛化证明 |
| `EXTERNAL_VALIDATION` | 仅指独立新 target 或第二数据集上的冻结方法验证 |

不得称失败的 source-selection 方法为有效新算法；不得把 calibrated/few-shot transfer
称为 zero-shot；不得把关联性 support mismatch 写成物理因果；不得声称跨数据集
generalization，除非完成被冻结方法的独立外部验证。

## 8. 当前授权状态

当前没有已授权的新模型、网格、score 或训练实验。locked test 保持禁止读取。

唯一受限的未来可能性是：`CLOSED_PARTIAL` prefix-supervised screening 的完全不变协议，
在独立新 target/外部数据上进行一次有新 Decision Record 的 external confirmation。
任何其他提案先从 G1–G7 重新审查。
