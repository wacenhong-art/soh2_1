# Experiment Decision Record 模板

> 在复制本模板前先阅读 `RESEARCH_GUARDRAILS.md`。本记录必须在任何数据加载、
> 训练、validation 或 test 访问前完成并提交。G1/G2/G3 任一 FAIL 即
> `EXPERIMENT_NOT_AUTHORIZED`。

## 基本信息

- **Experiment name：**
- **Date / author：**
- **Proposal category：** model / transfer / source selection / dataset extension /
  hyperparameter / external validation
- **Problem being solved：**
- **Supporting previous evidence：** 必须引用 Phase、报告、表或已冻结 claim。
- **Literature/theoretical basis：** 文献或理论机制；无依据时填 `NONE` 并使 G2=FAIL。

## 冻结实验设计

- **Frozen hypothesis：**
- **Independent variable：**
- **Fixed variables：** 数据边界、features、labels、seed、model、loss、source bank、
  preprocessing 与所有不可变配置。
- **Baselines：** 必须含 `TARGET_ONLY`；如涉及 transfer 必须含 `ALL_SOURCE`；并写明
  `BEST_SIMPLE_BASELINE`。
- **Validation data：**
- **Test access：** `FORBIDDEN` / 一次性冻结后最终评估；说明理由。
- **Success criterion：** 可测量、跨 target、预先冻结。
- **Failure criterion：**
- **Stop criterion：** 失败后明确关闭什么方法假设。
- **Generalization plan：** development target、未见 target、第二数据集与 claim 边界。

## G1–G7 审查表

| Gate | PASS / FAIL | Evidence / rationale | Reviewer decision |
|---|---|---|---|
| G1 PROBLEM |  | “Phase X发现__，因此方法__解决__。” |  |
| G2 PRIOR |  | 理论或经核对的文献依据 |  |
| G3 LEAKAGE |  | 证明与 validation/test SOH、历史 source 优劣独立 |  |
| G4 BASELINES |  | TARGET_ONLY / ALL_SOURCE / BEST_SIMPLE_BASELINE |  |
| G5 GENERALIZATION |  | B0007/B0018 的 development 限制与独立确认计划 |  |
| G6 FALSIFIABILITY |  | 成功、失败、停止条件已冻结 |  |
| G7 COMPLEXITY |  | 为什么 simple baseline 不足 |  |

## 授权结论

```text
G1/G2/G3 any FAIL -> EXPERIMENT_NOT_AUTHORIZED
G4-G7 unresolved -> HOLD_FOR_REVISION
all G1-G7 PASS -> AUTHORIZED_FOR_ONE_FROZEN_RUN
```

- **Authorization status：**
- **Authorized scope only：**
- **Explicitly prohibited follow-ups：**
- **Required artifact paths：** config, source manifest, metrics, predictions,
  training history, environment, Git commit.

## `PARTIALLY_SUPPORTED` 外部确认附录（仅在适用时填写）

仅适用于已获 `CLOSED_PARTIAL` 例外批准的 frozen method。

- **Frozen protocol commit / SHA：**
- **Independent new target or external dataset：**
- **Proof of no changes：** score / features / source bank / target label fraction /
  model / alpha / threshold 均必须为 `UNCHANGED`。
- **Confirmation-only statement：** 本实验不创建第三种 score，不进行方法救援。

若上述任一项不满足，记录必须标为 `EXPERIMENT_NOT_AUTHORIZED`。
