# Literature Gaps for Thesis Writing

本清单是后续写作前的文献需求图，不执行联网检索，也不预设任何文献已经支持本研究的
具体数值结论。每一篇最终引用都必须在写作阶段独立核验。

| 文献类别 | 需要补充的内容 | 用于支持的论文位置/论点 | 证据边界 |
|---|---|---|---|
| Original paper | 原论文的方法、数据描述、超参数、reported metrics 与 small-sample narrative | Ch. 1–3；复现动机与 `PAPER_AMBIGUOUS` 对照 | 用于描述 authors' claims；不证明本地 performance reproduction。 |
| SOH small-sample estimation | 小样本 SOH、early-life/prefix learning、uncertainty 与 robust evaluation | Ch. 1–2；为何 multi-seed、baseline、test lock 必要 | 不将综述共识替代本项目实验结果。 |
| STL/decomposition | STL、trend/seasonal/residual decomposition、forecast-error propagation | Ch. 2–5；解释 component pipeline 的方法背景 | 不从理论可分解性推断 component forecasts 必然准确。 |
| TimesNet/iTransformer | 时序模型设计、适用前提、参数与 data regime | Ch. 2、5；复杂/轻量 component control 的文献背景 | 不以模型流行度证明适用于 11–19 samples。 |
| Transfer learning | source-only、fine-tuning/calibration、domain shift、target-label access 的定义 | Ch. 2、6；zero-shot 与 calibrated 的命名边界 | calibrated 结果不得引用为 zero-shot success。 |
| Negative transfer | negative transfer 的定义、来源、检测和风险管理 | Ch. 2、6–7；source-specific risk 的解释框架 | 不由一般理论推出 B0006 的物理机制。 |
| Source selection/domain similarity | source selection、domain distance、support overlap、compatibility measurement 的已有方法和局限 | Ch. 2、6；解释为何评估两种 frozen rules | 不用文献为被拒绝 score 重新开启调参路线。 |
| Evaluation robustness | chronological split、leakage control、nested selection、multiple seeds、baseline comparison | Ch. 3–4、7；方法学 lessons | 不将 protocol rigor 等同于 generalization proof。 |

## 后续检索与引用纪律

1. 先建立可核验 bibliography，再写 Related Work；不编造 DOI、题名或结论。
2. 将**文献背景**和**本研究的 NASA evidence**分开引用：前者支持概念，后者支持本地结果。
3. 每一条涉及“negative transfer”“domain similarity”“causality”“generalization”的句子，
   必须在提交前与 `CLAIM_BOUNDARIES.md` 和 `THESIS_CLAIM_EVIDENCE_MATRIX.csv` 交叉检查。
4. 需要跨数据集 generalization claim 时，文献不足不是唯一缺口；还需要 independent
   external validation。当前论文不满足该实验条件。
