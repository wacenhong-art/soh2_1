"""Write-only thesis-positioning and evidence-freeze synthesis.

This script validates presence of frozen Phase 0--10 and two selection reports,
then writes thesis materials.  It never loads a dataset, model or test split.
"""
from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "final_research_closure_v1"
SOURCES = [
    "REPRO_AUDIT.md",
    "output/phase1_failure_isolation_v1/FINAL_JUDGMENT.md",
    "output/phase2_fusion_seq_ablation_v1/PHASE2_REPORT.md",
    "output/phase3a_capacity_ablation_v1/PHASE3A_REPORT.md",
    "output/phase3b_minimal_fusion_v1/PHASE3B_REPORT.md",
    "output/phase4a_component_attribution_v1/PHASE4A_REPORT.md",
    "output/phase4b_gan_component_attribution_v1/PHASE4B_REPORT.md",
    "output/phase5_complexity_ablation_v1/PHASE5_REPORT.md",
    "output/phase6_predictability_audit_v1/PHASE6_REPORT.md",
    "output/phase7_causal_decomposition_audit_v1/PHASE7_REPORT.md",
    "output/phase8_source_transfer_audit_v1/PHASE8_REPORT.md",
    "output/phase9_compatibility_audit_v1/PHASE9_REPORT.md",
    "output/phase10_final_plan_reconciliation_v1/PHASE10_REPORT.md",
    "output/research_consolidation_v1/RESEARCH_SYNTHESIS.md",
    "output/final_method_validation_v1/METHOD_VALIDATION_REPORT.md",
    "output/prefix_supervised_selection_v1/PREFIX_SELECTION_VALIDATION_REPORT.md",
]

LEDGER = [
    ("Paper protocol has unresolved 60/20/20 versus first-20% ambiguity", "INCONCLUSIVE", "Phase 0", "B0007/B0018", "REPRO_AUDIT.md labels PAPER_AMBIGUOUS.", "The local work uses an explicitly declared target-prefix protocol.", "Do not claim a fully unique reconstruction of the paper protocol."),
    ("Paper-style fusion has a catastrophic output mode", "CONFIRMED", "Phase 1", "B0007+B0018", "25 catastrophic validation predictions across 10 paper-fusion runs.", "Unconstrained paper-style fusion was unstable under the audited small-prefix protocol.", "Do not call this a proof of failure on every dataset or protocol."),
    ("Bounded residual fusion removes the observed catastrophic mode", "CONFIRMED", "Phase 1-2", "B0007+B0018", "catastrophic count 25 -> 0; residual configurations still fail accuracy gate.", "Bounding corrections is a robustness-engineering safeguard in this setting.", "Do not claim it solves SOH generalization or is the paper's original formula."),
    ("Shorter fusion sequence is the main cure", "REJECTED", "Phase 2", "B0007/B0018", "seq=4 increases usable samples but no configuration qualifies.", "Sequence shortening is not a primary remedy here.", "Do not present a best sequence length as a general solution."),
    ("Fusion capacity is the main cause", "REJECTED", "Phase 3A-3B", "B0007/B0018", "parameter/sample ratio drops from 1793 to 3.8 without qualification.", "Capacity alone does not explain the failure.", "Do not reopen capacity grids as a thesis innovation."),
    ("Prediction failure occurs before fusion", "CONFIRMED", "Phase 4A", "B0007/B0018", "Oracle STL reconstruction R2=1; predicted-component reconstruction R2=-13.019/-13.642.", "Upstream component forecasting is a necessary failure layer before learned fusion.", "Do not claim fusion weights are the sole root cause."),
    ("Trend is the only component bottleneck", "REJECTED", "Phase 4A", "B0007/B0018", "Trend has largest single substitution degradation, but residual/seasonal errors are material.", "Trend is important but not sufficient as a standalone target.", "Do not frame a trend-only replacement as validated."),
    ("GAN is a uniform cause or remedy", "REJECTED", "Phase 4B", "B0007 diagnostic", "REAL_ONLY reconstruction RMSE=5.832; REAL+GAN=6.695; mixed component effects.", "GAN effects are battery-specific in the diagnostic.", "Do not say removing or adding GAN consistently improves transfer."),
    ("Complex/lightweight component replacements solve the issue", "REJECTED", "Phase 5", "B0007/B0018", "TimesNet/iTransformer, Ridge, tiny MLP and tiny GRU do not establish a robust component replacement.", "More or less component capacity is not a validated thesis method.", "Do not claim a lightweight replacement wins cross-battery."),
    ("HF train-validation shift is observed", "SUPPORTED", "Phase 6", "B0007/B0018", "Mean KS .562/.573; B0007 relationship-shift evidence is stronger.", "Covariate/relationship shift is a plausible upstream generalization stressor.", "Do not identify a physical mechanism or claim causation from association."),
    ("STL prefix instability is the primary causal explanation", "REJECTED", "Phase 6-7", "B0007/B0018", "Causal EMA/median are prefix stable but have no >=1% Ridge RMSE improvement.", "Prefix instability alone is insufficient in the fixed diagnostic.", "Do not generalize this null to every possible decomposition/model."),
    ("Cross-battery transfer is target dependent", "CONFIRMED", "Phase 8", "B0007/B0018", "S2 zero-shot R2=.658 for B0007 vs .149 for B0018; calibrated B0007 R2=.916 but B0018 no material gain.", "Transfer benefit depends on target/source combination.", "Do not call calibrated results zero-shot or universal."),
    ("B0006 creates source-specific negative transfer risk", "CONFIRMED", "Phase 9", "B0007/B0018", "B0006-only zero-shot R2=-2.474/-1.905; calibrated R2=-.683/-1.483.", "Indiscriminate source pooling can carry negative-transfer risk.", "Do not infer the physical reason for B0006 incompatibility."),
    ("B0005 is uniformly a good source", "PARTIALLY_SUPPORTED", "Phase 9", "B0007/B0018", "B0005-only zero-shot R2=.886/.428; effects are only two targets and protocol-specific.", "B0005 is useful development evidence in this source bank.", "Do not hard-code B0005 or claim universal source superiority."),
    ("Unsupervised HF-distance selection predicts transfer utility", "REJECTED", "Final Method Validation", "B0007/B0018", "It selects B0006 for both targets; selected-source loses to all-source in all four contrasts.", "Simple covariate nearest-neighbor distance is not a valid utility score here.", "Do not redesign/tune another HF-distance score or read test to rescue it."),
    ("Prefix-supervised screening is cross-target reliable", "PARTIALLY_SUPPORTED", "Prefix-supervised Validation", "B0007/B0018", "B0018 selects B0005 and improves C1 (1.377 vs 1.565); B0007 selects B0006 and loses to C1 (2.654 vs .589).", "Prefix supervision can have battery-specific utility under calibrated/few-shot transfer.", "Do not claim a general effective source-selection algorithm or proceed to test."),
    ("Source compatibility is a physical causal mechanism", "INCONCLUSIVE", "Phase 9 + validations", "B0007/B0018", "Support mismatch and conditional residual diagnostics are associative; two selection rules are not stable.", "Source compatibility is an audit construct associated with transfer risk.", "Do not claim electrochemical causality."),
    ("Current evidence supports cross-dataset generalization", "REJECTED", "Phase 0-10 + validations", "NASA only", "No CALCE/independent confirmation; both candidate screening methods fail/partial.", "The thesis scope is NASA reproduction and negative-transfer audit.", "Do not claim CALCE or cross-dataset generality."),
]


POSITIONING = """# Final thesis positioning

## Selected positioning

`FINAL_THESIS_POSITIONING = C — Evidence-led reproduction failure attribution and cross-battery negative-transfer audit`

The thesis starts from a strict small-sample reproduction of the G-MTC-style SOH pipeline and follows the observed failure chain from unstable fusion, through component forecast error and representation diagnostics, to target-dependent transfer and source-specific negative-transfer risk. It is not framed as a successful new SOH algorithm.

## Why C is selected over A or B alone

| Criterion | A: Reproduction audit only | B: Transfer/compatibility only | C: Combined thesis (selected) |
|---|---|---|---|
| Evidence completeness | Strong but ends before transfer explanation | Strong transfer evidence but loses the upstream cause | Strong: all Phase 0-10 and both validation pivots form one chain |
| Narrative | Honest but mainly negative replication | Too narrow; both selection methods are not general methods | Explains why fusion tweaks failed and why source choice is risky |
| Technical contribution | Reproducibility and robustness audit | Association analysis only | Layered causal-attribution diagnostics plus transfer-risk evidence |
| Undergraduate fit | Good | Risky if claimed as an algorithm | Best: rigorous, bounded, data-backed and transparent |
| Overclaim risk | Low | High if source selection is framed as successful | Low if written as NASA-only diagnostic evidence |

## Central research question

**Under an explicitly declared NASA small-target-prefix protocol, where does a paper-style STL-component-fusion SOH pipeline fail, and what do source-specific transfer outcomes reveal about negative-transfer risk?**

Subquestions are: (1) whether bounded residual fusion changes catastrophic-output safety without claiming accuracy repair; (2) whether component forecasting fails before fusion; (3) which intuitive remedies are not primary explanations; and (4) whether source-specific effects and two pre-registered source-screening validations justify a general source-selection algorithm. The answer to the last subquestion is no for the present two-target evidence.

## Final research identity

This is a **NASA-only, development/validation-stage reproduction and robustness audit**. It contributes a disciplined negative result: the original complex pipeline is unstable in the local extreme-small-sample setting; simple source-compatibility screening rules are not reliably predictive of transfer utility. That negative result is technically useful because it prevents unsupported model tuning and test leakage.

## Formal route closure

- `CLOSED_UNSUPPORTED`: unsupervised HF-distance source selection. It selected B0006 for both targets and lost to all-source in every formal contrast.
- `CLOSED_PARTIAL`: prefix-supervised source screening. It succeeds only on B0018 and selects the wrong individual source for B0007; it cannot be a cross-target method claim.
- `CLOSED_NOT_PRIMARY`: fusion-sequence optimization, fusion-capacity reduction, GAN removal, trend-only replacement, lightweight component replacement and causal STL redesign. Their fixed diagnostics do not identify a robust remedy.

These statuses are evidence-freeze decisions. They may be discussed as negative controls, but may not be reopened as thesis tuning routes.
"""


CONTRIBUTIONS = """# Final contributions

## Contribution 1 — Strict reproduction robustness audit

Under a declared chronological target-prefix protocol, multi-seed evaluation and locked-test discipline, the thesis documents that paper-style fusion can generate catastrophic outputs and does not pass the cross-battery qualification gate. This is a reproducibility/robustness finding, not a claim that the published method fails universally.

## Contribution 2 — Layered failure attribution

The experiments separate fusion safety from accuracy, and then locate a decisive upstream issue: predicted STL components fail before fusion despite exact oracle reconstruction. Sequence length, fusion capacity, GAN, trend-only replacement, lightweight components and causal STL redesign are all retained as negative controls rather than silently discarded.

## Contribution 3 — Cross-battery negative-transfer evidence

The thesis shows source-specific transfer risk in the B0005/B0006 bank. Both a covariate-only screen and a target-prefix-supervised screen are evaluated transparently: the former is rejected and the latter is only battery-specifically supported. The conclusion is that simple screening rules cannot yet be claimed as a general transfer solution.

## Secondary robustness-engineering finding

Bounded residual fusion reduces the observed catastrophic count from 25 to 0. It may be reported as a safety guard, but it is neither the primary algorithmic contribution nor proof of generalization improvement.

## Excluded contribution claims

The thesis does not claim a successful universal source-selection algorithm, a new effective deep SOH architecture, a universal GAN/STL fix, zero-shot adaptation from calibrated results, or cross-dataset generalization.
"""


TABLES = """# Final paper experiment tables — frozen selection from existing results

No table below requires new training. Main-text tables are deliberately compact; all remaining rows remain available in the appendix/repository and must not be discarded.

| Table | Main-text content | Required existing evidence | Key message | Placement |
|---|---|---|---|---|
| A | Mean, persistence, STL/additive and paper baseline | Phase 1 baseline metrics; Phase 4A/5 reconstruction/persistence rows | The paper system must be compared with fair simple references. | Main text §4-5 |
| B | Paper fusion versus bounded residual fusion | Phase 1 `FINAL_JUDGMENT`, Phase 2 | Catastrophic count 25 -> 0, but accuracy gate remains unmet. | Main text §5 |
| C | Oracle STL versus predicted component reconstruction, with per-component attribution | Phase 4A | Failure exists before fusion; trend is important but not unique. | Main text §5 |
| D | REAL_ONLY versus REAL+GAN reconstruction/component summary | Phase 4B | GAN is not a uniform cause or remedy. | Appendix; brief text reference |
| E | Sequence/capacity summary plus component complexity and causal-STL null result | Phases 2, 3A/3B, 5, 7 | Intuitive fusion/complexity/STL fixes are not primary. | Main text §5 compact summary; detailed Appendix |
| F | Target-only, source-only zero-shot, source+target calibrated transfer | Phase 8 | Transfer is target dependent; calibration is labelled truthfully. | Main text §6 |
| G | B0005-only, B0006-only and all-source outcomes | Phase 9 | B0006 creates source-specific negative-transfer risk. | Main text §6 |
| H | Unsupervised source selection and prefix-supervised screening | Final Method Validation; Prefix-supervised Validation | Covariate distance is rejected; prefix screen is only battery-specific/partial. | Main text §6 |

## Appendix material

- Full five-seed run-level fusion metrics, weight entropy and training logs.
- All component-by-model rows from Phase 5.
- HF distribution and relationship-shift diagnostics from Phase 6.
- Full causal representation stability rows from Phase 7.
- All source/target transfer rows, local-neighbor diagnostics, coefficient diagnostics and source-selection sanity checks.
- Protocol manifests, Git commits and `TestLoaded=false` verification rows.

## Not necessary in the thesis main text

- Repeated grid details after the negative sequence/capacity decision is established.
- Any attempt to rank an unvalidated source-selection score as a winner.
- Locked-test metrics: no frozen qualifying method exists, so the locked test remains unopened.
"""


CLAIMS = """# Claim boundaries

## Claims allowed in the thesis

1. **NASA-only instability evidence:** Under the declared local small-target-prefix protocol, paper-style fusion produced catastrophic validation predictions and failed the specified multi-seed, two-target qualification gate.
2. **Safety evidence:** Bounded residual fusion eliminated the observed catastrophic-output count in the paired validation experiments, while not restoring reliable cross-battery accuracy.
3. **Failure-attribution evidence:** Oracle reconstruction is exact but forecasted components fail, so the observed error is already upstream of fusion in this implementation/protocol.
4. **Negative-control evidence:** Within their stated fixed contracts, sequence shortening, capacity reduction, selected GAN/component alternatives and causal prefix-stable representations did not establish a robust remedy.
5. **Transfer-risk evidence:** B0005/B0006 source identity is associated with markedly different transfer outcomes; B0006 presents a source-specific negative-transfer risk in the audited source bank.
6. **Screening-method evidence:** Covariate-distance screening is rejected; prefix-supervised screening is only battery-specifically/partially supported. Both are calibrated/development evidence, not validated general algorithms.

## Claims that need explicit qualification

- HF shift and multivariate support mismatch are **associative diagnostic evidence**, not identified physical/electrochemical causes.
- Results are limited to NASA B0007/B0018 targets, B0005/B0006 sources, stated HF features, temporal prefix split and Ridge/fusion contracts.
- Paper-protocol interpretation remains `PAPER_AMBIGUOUS` where 60/20/20 and first-20%-small-sample descriptions conflict.
- B0005's observed usefulness is a development finding, not a universal source ranking.

## Prohibited overclaims

- “We propose an effective new source-selection method.”
- “The source-screening method generalizes across batteries/datasets.”
- “The work is zero-shot” when target prefix SOH labels are used.
- “Bounded residual fusion solves SOH generalization” or “is the original paper formulation.”
- “HF distance/support mismatch physically causes negative transfer.”
- “The original paper is disproved universally.”
- Any CALCE/cross-dataset performance claim; CALCE was not run.

## Test and dataset boundary

`LOCKED_TEST_REMAINS_UNOPENED`. Neither candidate source-selection method passed its validation rule. Therefore the thesis should report development/validation evidence, preserve the test partition, and state why a test result was intentionally not mined for a positive outcome.

## CALCE decision

- **UNDERGRADUATE_MINIMUM:** CALCE is not necessary for this NASA reproduction/failure/negative-transfer audit; list it as future work.
- **PUBLICATION_EXTENSION:** CALCE or another independent dataset, together with unseen NASA targets and a newly frozen supported method, is required before claiming cross-dataset transfer generality.
"""


OUTLINE = """# Thesis outline

## 1. Introduction

- **Question:** Why can reported complex SOH pipelines appear promising yet be unreliable under an extreme small target prefix?
- **Evidence/tables:** Problem framing; Table A preview; protocol ambiguity boundary.
- **Conclusion:** The thesis asks a robustness and transfer-risk question rather than promising a new high-accuracy algorithm.

## 2. Related Work

- **Question:** What roles do decomposition, fusion, augmentation and cross-battery transfer play in SOH estimation?
- **Evidence/tables:** Paper method description; distinction between zero-shot and calibrated transfer.
- **Conclusion:** Existing claims motivate an auditable reproduction but do not substitute for local validation.

## 3. Reproduction Methodology

- **Question:** What is faithfully specified, reproduction-defined or unverified?
- **Evidence/tables:** `REPRO_AUDIT.md`; protocol table; `PAPER_AMBIGUOUS`; `L_weight=UNVERIFIED_DISABLED`.
- **Conclusion:** The implementation's epistemic boundaries are explicit before results are interpreted.

## 4. Experimental Protocol

- **Question:** How are leakage, seeds, simple baselines, source labels and test locking controlled?
- **Evidence/tables:** Table A; split diagram; five-seed rules; `TestLoaded=false` records.
- **Conclusion:** Results use chronological prefix development/validation; locked test remains unopened.

## 5. Failure Attribution of the G-MTC-Style Pipeline

- **Question:** Does failure arise from fusion, component forecasts, model capacity, GAN, or STL instability?
- **Evidence/tables:** Tables B, C and compact E; Table D reference.
- **Conclusion:** Bounded residuals improve safety, but upstream multi-component forecast failure is decisive; several plausible fixes are negative controls.

## 6. Cross-Battery Transfer Analysis

- **Question:** Does source identity alter transfer, and can simple compatibility screens predict utility?
- **Evidence/tables:** Tables F, G and H; block stability/oracle diagnostic in appendix.
- **Conclusion:** Transfer is target-dependent and B0006 is a negative-transfer risk; neither selection rule is a general method.

## 7. Discussion

- **Question:** What does the combined failure chain imply for small-sample battery SOH research?
- **Evidence/tables:** Final evidence ledger; failure-chain diagram.
- **Conclusion:** Do not use fusion tuning to conceal upstream predictability and source-compatibility uncertainty.

## 8. Limitations

- **Question:** What scope does the evidence not cover?
- **Evidence/tables:** Claim boundaries; NASA-only limitation; two targets; no test/CALCE.
- **Conclusion:** Physical causality, cross-dataset generalization and a universal source-selection algorithm remain unestablished.

## 9. Conclusion

- **Question:** What has been established and what should future work test?
- **Evidence/tables:** Contributions and future-work boundary.
- **Conclusion:** The contribution is a rigorous negative/audit result with an engineering safety observation, not an unsupported accuracy claim.
"""


DECISION = """# Final experiment decision

`EXPERIMENTAL_WORK_COMPLETE`

`LOCKED_TEST_REMAINS_UNOPENED`

No additional experiment is required to support the selected undergraduate thesis claim: a NASA-only evidence-led reproduction failure attribution and cross-battery negative-transfer audit. The existing Phase 0-10 and two pre-registered selection validations directly answer that claim.

Opening the locked test is not justified because neither frozen source-selection method qualifies: the covariate-only rule is rejected and the prefix-supervised rule is only battery-specific. A test evaluation would not answer an unresolved core thesis question; it would create a risk of outcome-driven method rescue.

CALCE is future work for cross-dataset generalization, not a missing condition for this thesis closure. No third selection score, model grid, or algorithm pivot is authorised by this evidence freeze.
"""


def require_sources() -> None:
    missing = [path for path in SOURCES if not (ROOT / path).is_file()]
    if missing:
        raise FileNotFoundError("Missing frozen evidence: " + "; ".join(missing))


def write_csv(path: Path) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["claim", "status", "supporting_experiment", "battery", "metric/evidence", "allowed_paper_claim", "prohibited_overclaim"])
        writer.writerows(LEDGER)


def main() -> None:
    require_sources()
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "FINAL_EVIDENCE_LEDGER.csv")
    (OUT / "FINAL_THESIS_POSITIONING.md").write_text(POSITIONING, encoding="utf-8")
    (OUT / "FINAL_CONTRIBUTIONS.md").write_text(CONTRIBUTIONS, encoding="utf-8")
    (OUT / "FINAL_PAPER_EXPERIMENT_TABLES.md").write_text(TABLES, encoding="utf-8")
    (OUT / "CLAIM_BOUNDARIES.md").write_text(CLAIMS, encoding="utf-8")
    (OUT / "THESIS_OUTLINE.md").write_text(OUTLINE, encoding="utf-8")
    (OUT / "FINAL_EXPERIMENT_DECISION.md").write_text(DECISION, encoding="utf-8")
    print(f"Wrote final closure to {OUT}")


if __name__ == "__main__":
    main()
