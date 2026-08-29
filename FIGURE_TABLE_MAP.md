# Figure and Table Map（冻结证据版）

所有表图均从既有 output 生成或重排，不新增训练、测试、模型选择或 score。正文按问题
组织；完整 run-level 记录进入附录，不能因结论为负而删除。

## 正文表格

| ID | title | chapter | scientific purpose | source file | 核心读者结论 | placement |
|---|---|---:|---|---|---|---|
| Table A | Baselines and paper-style reproduction under the locked protocol | 3–4 | 说明 fair comparator 与 performance reproduction 边界 | `output/phase1_failure_isolation_v1/baseline_metrics.csv`; `output/phase1_failure_isolation_v1/paper_fusion_metrics.csv` | paper fusion 必须与 Mean、persistence、STL/additive 比较。 | MAIN_TEXT |
| Table B | Paper fusion versus bounded residual safety guard | 4 | 区分 catastrophic safety 与 accuracy | `output/phase1_failure_isolation_v1/residual_fusion_metrics.csv`; Phase 2 report | catastrophic count 25→0，但 qualification 未通过。 | MAIN_TEXT |
| Table C | Oracle and forecasted component reconstruction | 4 | 证明 error 在 fusion 前已经存在 | `output/phase4a_component_attribution_v1/reconstruction_metrics.csv`; `oracle_substitution_metrics.csv` | oracle exact，不等于 predicted components 可预测。 | MAIN_TEXT |
| Table D | GAN attribution under REAL_ONLY and REAL+GAN | 5 | 排除 GAN 的单向解释 | `output/phase4b_gan_component_attribution_v1/component_metrics_by_data_source.csv` | GAN effect 是 battery-specific。 | APPENDIX;正文一句引述 |
| Table E | Negative controls: sequence, capacity, component complexity and causal STL | 4–5 | 压缩呈现未构成 remedy 的直觉改进 | Phases 2, 3A, 3B, 5, 7 reports | 这些路线在固定 contracts 下均非 primary remedy。 | MAIN_TEXT compact; APPENDIX detail |
| Table F | Target-only, source-only and calibrated transfer | 6 | 区分 transfer track 与 label use | `output/phase8_source_transfer_audit_v1/transfer_protocol_metrics.csv` | transfer benefit 依 target 而变；calibrated 不称 zero-shot。 | MAIN_TEXT |
| Table G | Source-specific transfer and negative-transfer risk | 6 | 对比 B0005-only、B0006-only 与 all-source | `output/phase9_compatibility_audit_v1/source_specific_transfer_metrics.csv` | B0006 在审计 source bank 中为两个 targets 带来 negative-transfer risk。 | MAIN_TEXT |
| Table H | Frozen source-selection validations | 6 | 同时保留 rejected 与 partially supported 结果 | `output/final_method_validation_v1/final_method_validation_metrics.csv`; `output/prefix_supervised_selection_v1/calibrated_selection_metrics.csv` | unsupervised rule rejected；prefix rule 仅 B0018 partial。 | MAIN_TEXT |

## 正文图形

| ID | title | chapter | scientific purpose | source file | 核心读者结论 | placement |
|---|---|---:|---|---|---|---|
| Figure 1 | Audited G-MTC reproduction and evaluation protocol | 3 | 展示数据流、target-prefix split、multi-seed 与 locked test | `REPRO_AUDIT.md`; protocol manifests | 所有比较位于 development/validation，test 未读。 | MAIN_TEXT |
| Figure 2 | Catastrophic-output safety comparison | 4 | 直观展示 paper fusion 与 residual fusion 的受限修正 | Phase 1 predictions / histories already saved | residual bound 防止观测到的极端输出，非 accuracy winner。 | MAIN_TEXT |
| Figure 3 | Component reconstruction attribution | 4 | 并置 oracle、predicted components 与 final reconstruction | `output/phase4a_component_attribution_v1/reconstruction_metrics.csv` | failure 已在 learned fusion 前出现。 | MAIN_TEXT |
| Figure 4 | HF train-to-validation shift diagnostics | 5 | 展示 covariate/relationship shift 的关联性证据 | `output/phase6_predictability_audit_v1/hf_component_relationship_shift_summary.csv` | shift 是 plausible stressor，不是物理因果。 | MAIN_TEXT |
| Figure 5 | Prefix stability versus fixed-predictor performance | 5 | 显示 STL stability repair 未自动转化为 RMSE improvement | `output/phase7_causal_decomposition_audit_v1/prefix_stability_metrics.csv` | prefix instability 不是充分解释。 | MAIN_TEXT or APPENDIX (版面不足时) |
| Figure 6 | Source-specific transfer outcomes | 6 | 比较 B0005、B0006 与 pooled sources 的 target-specific consequences | `output/phase9_compatibility_audit_v1/source_specific_transfer_metrics.csv` | source identity 有条件地改变 transfer outcome。 | MAIN_TEXT |
| Figure 7 | Frozen source-screening decision versus outcome | 6 | 展示 selected/all-source/oracle diagnostic 的边界 | Final Method Validation; Prefix Validation | 两种 screening 均不能支持通用方法 claim。 | MAIN_TEXT |
| Figure 8 | Evidence-led failure chain | 7 | 合成 fusion safety、component forecast、shift 与 transfer risk | `FINAL_EVIDENCE_LEDGER.csv` | 多层证据支持审计结论，非单一因果链。 | MAIN_TEXT |

## 附录与不采用项

| 内容 | placement | 理由 |
|---|---|---|
| 全部五 seed run-level logs、weight entropy、training histories | APPENDIX | 保障可审计性，但不打断主叙事。 |
| Phase 5 所有 component-by-model rows | APPENDIX | 正文只需负控制综合结论。 |
| Phase 6 完整 HF diagnostics、Phase 7 全部 stability rows | APPENDIX | 防止将关联性写成机制。 |
| 所有 grid enumeration 与重复 failure plots | OMIT from thesis main text | 已由 Table E 概括；保留在 repository。 |
| 任何 locked-test metric、后验 source-ranking winner | OMIT | 不存在合法 test 结果，也不允许事后选择。 |
