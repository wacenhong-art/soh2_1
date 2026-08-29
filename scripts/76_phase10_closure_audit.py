"""Phase 10: write-only reconciliation of the preregistered research plan.

This script does not import model code, data loaders, or training code.  It only
checks that the Phase 0--9 evidence artifacts exist, then writes a traceable
closure audit.  It is deliberately not a new experiment.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "phase10_final_plan_reconciliation_v1"


PHASES = [
    ("0", "Repository/protocol audit", "Audit only: recover data, split, paper-parameter and leakage contracts.", "REPRO_AUDIT.md", "NO_PHASE_COMMIT_FOUND", "PAPER_AMBIGUOUS; first-20%-prefix protocol fixed; L_weight UNVERIFIED_DISABLED.", "ANALYZED", "False", "Initial contract established", "Paper's 60/20/20 versus first-20% descriptions remain ambiguous."),
    ("1", "Failure isolation", "Separate paper fusion from bounded residual fusion and test catastrophic-output hypothesis.", "output/phase1_failure_isolation_v1/FINAL_JUDGMENT.md", "0c2681b", "PAPER_FUSION catastrophic=25; all residual configurations catastrophic=0; NO_QUALIFIED_CONFIGURATION.", "VERIFIED", "False", "Safety failure isolated; accuracy gate not met", "Residual correction removed catastrophic predictions but did not produce positive R2."),
    ("2", "Fusion sequence ablation", "Test whether more usable fusion windows solve instability.", "output/phase2_fusion_seq_ablation_v1/PHASE2_REPORT.md", "cd03cce", "seq=4 increases samples B0007 13->19 and B0018 5->11; no qualified configuration.", "VERIFIED", "False", "SEQUENCE_LENGTH_NOT_PRIMARY_BOTTLENECK", "Only four predeclared sequence lengths were tested."),
    ("3A", "Fusion capacity ablation", "Test whether parameter/sample mismatch is the primary fusion bottleneck.", "output/phase3a_capacity_ablation_v1/PHASE3A_REPORT.md", "04951f9", "19,727 -> 1,150 parameters; no qualified configuration; C2 only partially improved mean RMSE.", "VERIFIED", "False", "CAPACITY_REDUCTION_PARTIALLY_EFFECTIVE; not sufficient", "Two batteries and five seeds only."),
    ("3B", "Minimal-fusion validation", "Validate capacity finding with nonrecurrent and near-minimal fusion controls.", "output/phase3b_minimal_fusion_v1/PHASE3B_REPORT.md", "eedac86", "309- and 42-parameter controls did not qualify; C4 failed catastrophically.", "VERIFIED", "False", "CAPACITY_NOT_PRIMARY_BOTTLENECK", "Architecture family coverage remains deliberately bounded."),
    ("4A", "Component attribution", "Determine whether fusion or upstream component forecasts cause reconstruction failure.", "output/phase4a_component_attribution_v1/PHASE4A_REPORT.md", "1397e51", "Oracle reconstruction R2=1; predicted component reconstruction R2=-13.019/-13.642; trend largest single substitution.", "VERIFIED", "False", "MULTI_COMPONENT_FORECASTING_FAILURE", "Diagnostic uses existing validation artifacts."),
    ("4B", "GAN/component attribution", "Check whether SCF-GAN, rather than component forecasting, explains failure.", "output/phase4b_gan_component_attribution_v1/PHASE4B_REPORT.md", "80297f0", "Real-only reconstructed RMSE=5.832; real+GAN=6.695; mixed component failure.", "VERIFIED", "False", "GAN not a unified repair", "GAN-only counterfactual was correctly not run because supervision semantics would change."),
    ("5", "Component complexity ablation", "Test paper TimesNet/iTransformer against persistence, Ridge, tiny MLP and tiny GRU under identical causal validation protocol.", "output/phase5_complexity_ablation_v1/PHASE5_REPORT.md", "596e28f", "TIMESNET_FAILURE_NOT_EXPLAINED_BY_CAPACITY; MULTI_COMPONENT_REDESIGN_REQUIRED.", "VERIFIED", "False", "Complexity increase did not repair component forecasts", "One fixed small-model set, not an unrestricted model search."),
    ("6", "Predictability audit", "Assess HF shift, STL prefix sensitivity and direct HF-to-SOH controls.", "output/phase6_predictability_audit_v1/PHASE6_REPORT.md", "6c62a5c", "HF_COMPONENT_RELATIONSHIP_SHIFT; STL_PREFIX_INSTABILITY; direct Ridge B0007 R2=-6.126, B0018 R2=0.255.", "VERIFIED", "False", "Pipeline predictability failure, with target-instability caveat", "Observed relationship shift is partly confounded by changing STL targets."),
    ("7", "Causal decomposition audit", "Test whether prefix-stable causal representations improve the fixed direct predictor.", "output/phase7_causal_decomposition_audit_v1/PHASE7_REPORT.md", "60639df", "D1/D2 prefix stability exactly 0 normalized RMSE but no >=1% RMSE improvement over D0.", "VERIFIED", "False", "STL_INSTABILITY_NOT_CAUSALLY_LINKED_TO_FORECAST_FAILURE under fixed Ridge diagnostic", "Does not rule out every alternative decomposition/model combination."),
    ("8", "Source transfer audit", "Separate target-only, zero-shot source transfer and calibrated transfer.", "output/phase8_source_transfer_audit_v1/PHASE8_REPORT.md", "ea3af45", "B0007 S2 zero-shot R2=0.658 and calibrated R2=0.916; B0018 S2 no useful gain.", "VERIFIED", "False", "BATTERY_SPECIFIC_DOMAIN_SHIFT_REMAINS", "Univariate coverage does not prove conditional compatibility."),
    ("9", "Compatibility audit", "Attribute source-transfer disparity to source selection, support mismatch or conditional shift.", "output/phase9_compatibility_audit_v1/PHASE9_REPORT.md", "e412f66", "Primary MULTIVARIATE_SUPPORT_MISMATCH; secondary SOURCE_SPECIFIC_NEGATIVE_TRANSFER; B0006 harms both targets.", "VERIFIED", "False", "Source-target compatibility is the supported next research mechanism", "Two targets cannot establish general cross-dataset universality."),
]


PLAN = [
    (1, "任务背景与失稳问题界定", "明确可检验问题并禁止以漂亮R2替代机制证据", "0-9", "COMPLETED", "REPRO_AUDIT.md; Phase1-9 reports", "全程保留负R2、失败seed和locked-test边界。", "None"),
    (2, "Track A/Track B严格分离", "避免把论文复现与自定义增强混为一谈", "0-5", "COMPLETED", "REPRO_AUDIT.md tracks; Phase2 distinct PAPER_FUSION/IPRF rows", "论文参数、REPRO_DEFINED和增强命名已分离。", "None"),
    (3, "Repository Audit", "先建立代码、数据和论文参数审计", "0", "COMPLETED", "REPRO_AUDIT.md", "已形成paper contract与L_weight边界。", "None"),
    (4, "数据数量审计", "实际计算小样本窗口数", "0,2,3", "COMPLETED", "Phase2 sample table; Phase3A parameter/sample table", "B0007/B0018 fusion samples明确为19/11（seq=4）。", "None"),
    (5, "数据泄漏审计", "锁定测试、训练前缀和缩放/窗口边界", "0-9", "COMPLETED", "REPRO_AUDIT.md; each phase protocol TestLoaded=false", "所有Phase1-9验证行显式记录test未加载。", "None"),
    (6, "可靠基线", "避免只与失败fusion比较", "1,4,5,6", "COMPLETED", "Phase4A persistence; Phase5 recursive persistence; Phase6 direct Ridge", "基线信息集与诊断性one-step持久性已分开。", "None"),
    (7, "Fusion诊断日志", "定位输出爆炸、权重坍缩和训练不稳", "1,2", "COMPLETED", "Phase1 all_run_metrics_with_gates.csv; Phase2 report", "catastrophic、权重熵和时序变化均被记录。", "None"),
    (8, "三类崩溃模式检查", "区分输出爆炸、权重坍缩和权重抖动", "1,2", "COMPLETED", "Phase1 FINAL_JUDGMENT; Phase2 metrics", "bounded residual修复输出爆炸；准确率问题仍存在。", "None"),
    (9, "多随机种子协议", "禁止只汇报最好seed", "1-5", "COMPLETED", "Phase1-5 reports, fixed seeds [42,123,2024,3407,7777]", "融合与分量模型阶段均按五seed报告。", "None"),
    (10, "模型晋级标准", "以双电池、全部seed、无catastrophic和locked-test为门", "1-5", "COMPLETED", "Phase1/2/3A/3B gate tables", "所有融合配置均诚实标为NO_QUALIFIED_CONFIGURATION。", "None"),
    (11, "一次只改一个变量", "保证因果归因与消融可解释", "1-9", "COMPLETED", "Phase2-9 protocol sections", "每阶段预注册单一核心问题；不进行隐性大网格。", "None"),
    (12, "E1 Fusion sequence length", "检验更短context是否用更多窗口提升稳定性", "2", "COMPLETED", "PHASE2_REPORT.md", "seq=4最好但全部失败，样本数增加不是主瓶颈。", "None"),
    (13, "E2 Bi-LSTM capacity", "检验减少参数是否改善小样本稳健性", "3A,3B", "COMPLETED", "PHASE3A_REPORT.md; PHASE3B_REPORT.md", "参数/sample从1793降至约3.8仍未合格。", "None"),
    (14, "E3 BatchNorm到LayerNorm", "作为单变量稳定性增强", "post-5", "NOT_REQUIRED_AFTER_CAUSAL_ATTRIBUTION", "Phase4A/5 multi-component forecasting failure", "上游分量预测先失败；未观察到fusion容量是主因。", "若提出新的上游可预测分量，应单独预注册比较。"),
    (15, "E4 stable initialization", "令初始预测接近可靠重构", "post-4", "NOT_REQUIRED_AFTER_CAUSAL_ATTRIBUTION", "Phase4A predicted reconstruction failure; Phase1 residual safety result", "可靠的上游重构不存在，初始化不能修复其系统误差。", "只有出现已验证的分量基线后再评估。"),
    (16, "E5 constrained residual fusion", "将无约束SOH生成改为有界修正", "1,2", "COMPLETED", "Phase1 FINAL_JUDGMENT; Phase2 report", "catastrophic 25->0，但没有恢复可靠正R2。", "保留为安全护栏，不作为精度结论。"),
    (17, "论文fusion与residual fusion分表", "防止把自定义增强伪称论文原式", "0-2", "COMPLETED", "REPRO_AUDIT.md; Phase2 ranking", "PAPER_FUSION与IPRF_RESIDUAL_FUSION始终分开。", "None"),
    (18, "E6 KL权重正则", "抑制attention权重极端坍缩", "post-4", "NOT_REQUIRED_AFTER_CAUSAL_ATTRIBUTION", "Phase1 L_weight UNVERIFIED_DISABLED; Phase4A/5", "论文L_weight未定义；更关键的是分量预测先失败。", "不应作为论文修复或Phase11默认任务。"),
    (19, "E7 temporal weight smoothing", "抑制权重高速抖动", "post-4", "NOT_REQUIRED_AFTER_CAUSAL_ATTRIBUTION", "Phase2 diagnostics; Phase4A/5", "权重平滑不会使错误分量成为可预测分量。", "仅在上游通过后作为增强消融。"),
    (20, "Transfer/Calibration独立轨道", "严格区分zero-shot和使用target标签的calibration", "8,9", "COMPLETED", "PHASE8_REPORT.md; PHASE9_REPORT.md", "P1无target SOH，P2明确CALIBRATED。", "None"),
    (21, "论文目标数据设置核对", "不擅自消解60/20/20与first20描述冲突", "0", "INCONCLUSIVE", "REPRO_AUDIT.md PAPER_AMBIGUOUS", "原论文公开描述未能仅凭代码审计统一。", "论文作者材料或官方代码可用于未来澄清；不影响本地前缀轨道结论。"),
    (22, "推荐执行顺序", "从审计到归因，再到转移机制", "0-9", "COMPLETED", "Phase numbering and reports", "实际执行遵守先融合、后分量、后表征、后迁移归因。", "None"),
    (23, "候选核心模型组合", "仅在单因素证据成立后组合模块", "post-5", "SUPERSEDED_BY_EVIDENCE", "Phase3B; Phase4A; Phase5", "任何fusion组合均无法绕过上游预测失败。", "不进行无证据的模块堆叠。"),
    (24, "最终实验表", "统一保存逐run与summary指标", "1-9", "COMPLETED", "Phase1 all_run_metrics; Phase2-9 metrics CSV", "各阶段均保存可追溯指标，Phase10再汇总完成度。", "None"),
    (25, "必要图表", "用预测、权重、seed与battery图支撑结论", "1-5", "COMPLETED", "Phase1-5 output figure/metric artifacts", "诊断图与表存在于对应阶段；本阶段不制造新结论图。", "论文写作时从冻结CSV重新作图。"),
    (26, "实验可复现性目录", "保存配置、指标、预测、环境和seed", "1-9", "INCONCLUSIVE", "Phase1 environment/config; phase-specific scripts and CSV", "核心追溯材料存在，但未形成跨Phase统一manifest。", "工程性整理项，不改变本次因果结论，不构成Phase11。"),
    (27, "共享配置化代码架构", "防止模型代码复制和隐性漂移", "1-9", "INCONCLUSIVE", "scripts/65-75_phase*.py", "阶段脚本可追溯但非单一通用FusionConfig架构。", "重构属于工程维护，非继续实验的必要条件。"),
    (28, "单元测试", "验证权重、bound、split、scaler和shape契约", "0-9", "INCONCLUSIVE", "Phase reports' contract checks", "运行时审计覆盖关键边界，但没有完整独立unit-test suite。", "工程硬化建议；非影响现有结论的关键证据缺口。"),
    (29, "禁止事项", "禁止test选参、挑seed、伪zero-shot和伪论文公式", "0-9", "COMPLETED", "REPRO_AUDIT.md; every phase protocol", "已保持test locked、标签轨道命名和UNVERIFIED边界。", "None"),
    (30, "研究问题回答", "从稳定性、表征到迁移机制逐项作答", "1-9", "COMPLETED", "PHASE10_REPORT.md; final_causal_chain.md", "RQ以证据强度而非最佳RMSE回答。", "None"),
    (31, "潜在创新点边界", "仅在证据支持时形成可检验研究故事", "9,10", "COMPLETED", "PHASE9_REPORT.md; research_direction_candidates.md", "支持的是兼容性感知迁移假设，不是已验证通用SOTA。", "跨电池/跨数据集验证是发表扩展，不是本NASA闭环的必需Phase11。"),
]


def write_csv(path: Path, headers: list[str], rows: list[tuple]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def assert_evidence_exists() -> None:
    missing = [evidence for _, _, _, evidence, *_ in PHASES if not (ROOT / evidence).exists()]
    if missing:
        raise FileNotFoundError("Missing evidence artifacts: " + "; ".join(missing))


def main() -> None:
    assert_evidence_exists()
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "plan_reconciliation.csv", ["item_id", "original_plan_item", "intended_purpose", "related_phase", "status", "evidence", "reason", "remaining_action"], PLAN)
    write_csv(OUT / "phase_completion_matrix.csv", ["phase", "phase_goal", "actual_execution", "evidence_artifact", "git_commit", "conclusion", "verification_status", "TestLoaded", "satisfies_target", "unresolved"], PHASES)
    (OUT / "final_causal_chain.md").write_text(CAUSAL_CHAIN, encoding="utf-8")
    (OUT / "research_direction_candidates.md").write_text(CANDIDATES, encoding="utf-8")
    (OUT / "project_closure_judgment.md").write_text(CLOSURE, encoding="utf-8")
    (OUT / "PHASE10_REPORT.md").write_text(REPORT, encoding="utf-8")
    print(f"Wrote closure audit to {OUT}")


CAUSAL_CHAIN = """# Final causal chain (Phase 10)

## Verified

1. **Unconstrained paper-style fusion can produce catastrophic validation predictions under this target-prefix protocol.** Phase 1 recorded 25 catastrophic predictions for `PAPER_FUSION`; bounded residual fusion reduced this to zero without loading test data.
2. **The main observed failure precedes fusion.** Phase 4A's oracle STL reconstruction is exact, while predicted-component reconstruction has validation R2 -13.019 (B0007) and -13.642 (B0018). Phase 5 confirmed that more complex component networks do not repair this under the fixed protocol.
3. **Source selection matters.** Phase 9 finds B0005 can help, while B0006 produces negative transfer on both targets. The predefined primary attribution is `MULTIVARIATE_SUPPORT_MISMATCH`; `SOURCE_SPECIFIC_NEGATIVE_TRANSFER` is independently supported as a source-level risk.

## Partly supported

1. **Small-sample fusion capacity is a contributor, not the primary bottleneck.** Parameter/sample ratios fell from 1,793 (B0018 full fusion) to 104.6 (tiny GRU) and then 3.8 (minimal fusion), but none met the qualification gate.
2. **HF-to-target distribution/relationship shift is associated with poor target-only prediction.** Phase 6 detects large train-validation differences, especially for B0007, but the component target itself can move with appended prefix observations.
3. **Compatibility-aware transfer is a credible research mechanism.** B0007 benefits substantially from B0005/S2, while B0018 has larger nearest-source distance and no comparable S2 benefit. This is evidence for a testable selection rule, not proof of a universal physical mechanism.

## Negated as a primary explanation within the tested contracts

1. **Shorter fusion sequence is not the primary bottleneck.** It increased B0007/B0018 fusion samples but did not qualify a model.
2. **Fusion capacity alone is not the primary bottleneck.** Tiny recurrent and nonrecurrent alternatives remain non-qualifying.
3. **STL prefix instability is not causally linked to forecast failure in the fixed Ridge diagnostic.** Causal EMA/median representations are prefix invariant yet yield no predeclared >=1% RMSE improvement.
4. **More component-network complexity is not an evidenced repair.** The Phase 5 paper component models, tiny MLP/GRU and simple controls do not establish a robust replacement.

## Uncertain / deliberately not claimed

1. The physical cause of HF shift and of source-target incompatibility is not identified.
2. The paper's 60/20/20 versus first-20%-small-sample descriptions remain `PAPER_AMBIGUOUS`.
3. NASA evidence on B0007/B0018 cannot establish cross-dataset generalization. CALCE is required only for a cross-dataset claim, not for closure of the current NASA mechanism audit.
"""


CANDIDATES = """# Research direction candidates (maximum three)

## Candidate 1 — Compatibility-aware source selection for small-sample SOH transfer

- **Research question:** Can a source-selection rule based on joint HF support and a calibration-free compatibility score prevent negative transfer before target-label adaptation?
- **Core innovation:** Treat source choice as a first-class decision, rather than pooling all source batteries. Exclude or down-weight sources with poor joint support; report abstention when no compatible source exists.
- **Current evidence:** Phase 9 shows B0005 helps while B0006 harms both targets; B0018 has a larger S2 nearest-source distance than B0007 and no S2 improvement.
- **Missing evidence:** Pre-registered leave-one-target-out evaluation over more NASA batteries; a held-out source-selection rule; CALCE or another independent dataset before cross-dataset claims.
- **Risk:** Two targets can overfit a compatibility narrative; nearest-neighbor distance need not capture causal electrochemistry.
- **Suitability:** Strongest BSc thesis direction after bounded validation; plausible publication direction only with broader batteries and independent data.

## Candidate 2 — Failure-aware SOH transfer with abstention and bounded correction

- **Research question:** Can a predictor abstain or revert to a declared safe baseline when support mismatch is high, while guaranteeing bounded deviation from that baseline?
- **Core innovation:** Combine compatibility screening with the Phase-1 bounded residual safety property; evaluate safety and failure rate separately from accuracy.
- **Current evidence:** Residual fusion eliminated catastrophic predictions, but did not solve accuracy. This makes it a safety mechanism, not an accuracy innovation.
- **Missing evidence:** A pre-specified safe baseline with positive performance across targets; utility/cost definition for abstention; more batteries.
- **Risk:** May be operationally useful but weak as a standalone accuracy paper.
- **Suitability:** Good BSc engineering extension; publication value depends on genuine safety/coverage evidence.

## Candidate 3 — Descriptive small-sample fusion failure study

- **Research question:** Under what parameter/sample, component-error and source-compatibility conditions do STL-component fusion systems fail?
- **Core innovation:** A rigorously negative, mechanism-oriented reproducibility study: retain failed seeds, locked-test boundaries and causal-attribution checks rather than presenting only best results.
- **Current evidence:** Phase 1-9 jointly isolate catastrophic fusion, component failure, non-primary sequence/capacity effects and source-specific negative transfer.
- **Missing evidence:** More target batteries and a careful paper-protocol clarification; no new large neural architecture is justified by the current evidence.
- **Risk:** Novelty is methodological and may require a strong reproducibility venue fit.
- **Suitability:** Strong BSc thesis/report framing now; publication candidate if expanded with pre-registered cross-dataset validation.
"""


CLOSURE = """# Project closure judgment

## Final judgment

`PROJECT_DIAGNOSTIC_PHASES_COMPLETE`

`NO_FURTHER_PHASE_REQUIRED`

## Scope of this judgment

The completed scope is the NASA, target-prefix, validation-only mechanism audit defined in Phases 0-9. Its conclusions are: bounded residual fusion is a safety guard; sequence length and fusion capacity are not primary bottlenecks; component predictability fails before fusion; and compatibility/source selection is the best-supported next mechanism.

`CALCE_DECISION = FUTURE_VALIDATION_ONLY_FOR_NASA_CLOSURE`. CALCE becomes required before claiming cross-dataset generalization, not before closing the present NASA diagnostic program.

No Phase 11 is proposed: no unresolved item directly changes this closed causal attribution, and starting another model, grid, regularizer, decomposition, CALCE run, or transfer recipe would violate the stated stop condition.
"""


REPORT = """# Phase 10 — Final Plan Reconciliation & Research Closure Audit

## Scope and integrity result

This is a write-only reconciliation of existing Phase 0-9 evidence. It did not train a model, load test data, alter a protocol, inspect a locked test split, run CALCE, or begin Phase 11. The audit checks the presence of the source evidence artifacts and preserves their stated `TestLoaded=false` contracts.

## Original 31-point plan reconciliation

`plan_reconciliation.csv` recovers the original numbered plan at the level of its operational sections and classifies each item only as `COMPLETED`, `SUPERSEDED_BY_EVIDENCE`, `NOT_REQUIRED_AFTER_CAUSAL_ATTRIBUTION`, `STILL_REQUIRED`, or `INCONCLUSIVE`.

Key reconciliation decisions:

- LayerNorm, KL weight regularization, temporal smoothing, stable initialization and further complex fusion are **not required** for the completed causal audit: upstream component forecasts fail before fusion, and the paper's `L_weight` formula remains `UNVERIFIED_DISABLED`.
- A larger fusion grid is **superseded by evidence**: sequence shortening and parameter reduction did not resolve the qualification failure.
- More decomposition methods are **not required** in this audit: prefix-stable replacements remove instability but do not improve the fixed predictor.
- CALCE is **future validation only**. It is not necessary to close a NASA-only mechanism audit, but it is mandatory before any cross-dataset generalization claim.

## Phase acceptance audit

`phase_completion_matrix.csv` records each phase's goal, actual execution, evidence artifact, conclusion, verification boundary, locked-test status, acceptance target and remaining limitation. No missing experiment invalidates the current causal conclusion. Engineering items left `INCONCLUSIVE` (a unified manifest, fully shared config architecture and a standalone unit-test suite) are transparently recorded; they are maintenance work, not a key experimental gap.

## Positive findings

1. Bounded residual fusion prevents the observed catastrophic-output mode (25 to 0) without claiming accuracy recovery.
2. Component oracle reconstruction is exact, separating decomposition arithmetic from forecast failure.
3. B0005 is an effective source in the observed transfers, while B0006 is a reproducible negative-transfer risk.
4. Compatibility/source selection is a concrete, evidence-supported future research mechanism.

## Negative findings

1. No paper-style or residual fusion configuration passed the cross-battery, multi-seed qualification gate.
2. More fusion samples, fewer fusion parameters and very small fusion controls do not produce a qualified configuration.
3. More complex component predictors do not repair component forecasting under the fixed small-prefix protocol.
4. Prefix-stable causal decompositions do not improve the fixed Ridge predictor, so STL instability is not the established primary cause.

## Research closure

The complete causal chain and candidate research directions are in `final_causal_chain.md` and `research_direction_candidates.md`. The project is closed at the diagnostic stage with the judgment in `project_closure_judgment.md`.
"""


if __name__ == "__main__":
    main()
