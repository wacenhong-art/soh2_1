"""Write-only research consolidation for the completed Phase 0--10 audit.

No dataset, model, data loader, or test split is imported.  The source manifest
is checked solely to ensure that this synthesis is traceable to frozen reports.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "research_consolidation_v1"
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
    "output/phase10_final_plan_reconciliation_v1/plan_reconciliation.csv",
    "output/phase10_final_plan_reconciliation_v1/final_causal_chain.md",
]

EVIDENCE = [
    ("Paper protocol is not fully reconstructible", "0", "B0007/B0018 contract", "Paper separately discloses 60/20/20 and first-20%-small-sample settings; REPRO_AUDIT labels this PAPER_AMBIGUOUS.", "INCONCLUSIVE", "Do not present the local target-prefix protocol as the only paper protocol."),
    ("Paper-style fusion has a catastrophic-output mode", "1", "B0007+B0018", "PAPER_FUSION recorded 25 catastrophic validation predictions across 10 runs.", "CONFIRMED", "Unconstrained fusion is unsafe under the tested small-prefix contract."),
    ("Bounded residual fusion removes the observed catastrophic mode", "1-2", "B0007+B0018", "All residual configurations had catastrophic_count=0; epsilon=0.05 Phase-2 reference remains non-qualifying.", "CONFIRMED", "Bounded correction is a safety contribution, not an accuracy solution."),
    ("Residual fusion restores reliable accuracy", "1-2", "B0007+B0018", "Every residual configuration fails the preregistered gate; Phase-2 best mean R2=-6.874.", "REJECTED", "Do not claim residual fusion solves small-sample SOH estimation."),
    ("Short fusion context fixes generalization", "2", "B0007/B0018", "seq=4 raises fusion samples 13->19 and 5->11 respectively, but no configuration qualifies.", "REJECTED", "Sequence length is not the primary bottleneck."),
    ("Fusion parameter/sample mismatch is the primary cause", "3A-3B", "B0007/B0018", "Parameters/sample falls from 1,793 (full B0018) to 104.6 (tiny GRU) and 3.8 (minimal), without qualification.", "REJECTED", "Capacity may contribute but cannot explain the observed failure alone."),
    ("Failure is upstream of fusion", "4A", "B0007/B0018", "Oracle STL reconstruction R2=1, whereas predicted-component reconstruction R2=-13.019/-13.642.", "CONFIRMED", "Correcting fusion weights cannot repair already-unpredictable components."),
    ("Trend is the only component bottleneck", "4A", "B0007/B0018", "Trend causes largest single substitution deterioration, but several component errors are material.", "REJECTED", "Avoid a trend-only innovation claim."),
    ("GAN is a uniform root cause or uniform remedy", "4B", "B0007 diagnostic", "Real-only reconstructed RMSE=5.832; real+GAN RMSE=6.695; component effects are mixed.", "REJECTED", "GAN has battery-specific effects and is not a unified explanation."),
    ("More complex component models solve the problem", "5", "B0007/B0018", "Paper models, Ridge, tiny MLP and tiny GRU do not yield a robust component solution; decision TIMESNET_FAILURE_NOT_EXPLAINED_BY_CAPACITY.", "REJECTED", "Do not reopen a generic complexity/grid search."),
    ("HF train-validation shift exists", "6", "B0007/B0018", "Mean KS=0.562/0.573; B0007 has stronger relationship-shift evidence; validation-outside-train fractions 0.510/0.462.", "SUPPORTED", "Shift is an upstream covariate/generalization concern, not a proven physical mechanism."),
    ("Direct HF-to-SOH universally solves prediction", "6", "B0007/B0018", "Direct Ridge R2=-6.126 on B0007 but 0.255 on B0018; it outperforms the component pipeline without being universally good.", "REJECTED", "Direct mapping helps isolate pipeline harm but is not a universal final model."),
    ("STL prefix instability is the primary causal failure", "6-7", "B0007/B0018", "STL is unstable, but prefix-invariant EMA/median achieve no >=1% RMSE gain in fixed Ridge diagnostic.", "REJECTED", "State the limited diagnostic conclusion, not a universal null for all decompositions."),
    ("Source transfer usefulness differs by target", "8", "B0007/B0018", "S2 zero-shot: B0007 RMSE=1.313/R2=.658; B0018 RMSE=1.671/R2=.149, versus target-only R2=-6.126/.255.", "CONFIRMED", "Transfer is battery dependent."),
    ("Calibration benefits both targets equally", "8", "B0007/B0018", "S2 calibrated B0007 RMSE=.651/R2=.916; B0018 RMSE=1.564/R2=.255, effectively no gain.", "REJECTED", "Target-prefix labels must be named CALIBRATED, and benefit is target-specific."),
    ("B0005 is a comparatively useful source", "9", "B0007/B0018", "B0005 zero-shot R2=.886/.428; B0005+B0006 is worse than B0005-only for both targets in zero-shot.", "SUPPORTED", "Source identity matters; evidence is only two targets and is development evidence."),
    ("B0006 poses negative-transfer risk", "9", "B0007/B0018", "B0006-only zero-shot R2=-2.474/-1.905 and calibrated R2=-.683/-1.483.", "CONFIRMED", "Pooling sources without compatibility control is unsafe."),
    ("Multivariate support mismatch explains transfer disparity", "9", "B0007/B0018", "Combined-source nearest distance mean 1.123 (B0007) versus 1.472 (B0018); Phase9 predefined primary attribution is MULTIVARIATE_SUPPORT_MISMATCH.", "SUPPORTED", "A compatibility score is a justified method hypothesis, not yet a validated selection method."),
    ("Conditional physical shift is identified", "9", "B0007/B0018", "B0018 local SOH delta is positive, but its larger support distance confounds independent attribution.", "INCONCLUSIVE", "No electrochemical causal mechanism should be claimed."),
    ("Current evidence supports a universal cross-dataset method claim", "0-10", "NASA only", "Only NASA targets B0007/B0018 support the mechanism audit; no independent confirmation dataset was used.", "REJECTED", "CALCE or another independent dataset is required for cross-dataset generalization claims."),
]


def write_csv(path: Path, headers: list[str], rows: list[tuple[str, ...]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)


def require_sources() -> None:
    missing = [p for p in SOURCES if not (ROOT / p).is_file()]
    if missing:
        raise FileNotFoundError("Missing frozen evidence: " + "; ".join(missing))


SYNTHESIS = """# Research synthesis: evidence-led final story

## Scope

This document consolidates Phases 0-10 only. It contains no new training, no test access and no reinterpretation of a correlation as a physical cause. The local evidence is NASA-only and uses the audited target-prefix development protocol; paper-protocol ambiguity remains visible.

## The research story

The paper-style STL-component, TimesNet/iTransformer and attention Bi-LSTM pipeline fails in this local small-sample setting for two separable reasons. First, the unconstrained fusion layer is unsafe: its paper-style form generated 25 catastrophic validation outputs. Bounded residual fusion eliminates that output mode by constraining the correction around the component reconstruction, but it does not restore positive, cross-battery R2. It is therefore a safety guard, not the central accuracy innovation.

Second, and more importantly, Phase 4A shows that component forecasts are already failing before the fusion layer receives them. Oracle STL reconstruction is exact, whereas predicted-component reconstruction has strongly negative R2 on both targets. Sequence shortening, parameter reduction and minimal fusion controls all fail to change this conclusion. Fusion is thus not the primary explanatory layer.

Neither GAN, Trend alone, component-network capacity nor STL prefix instability supplies a complete replacement explanation. GAN effects are mixed and battery specific; Trend is important but multiple component errors matter; tiny and complex component alternatives are not robustly superior; and prefix-stable causal representations remove STL instability without improving the fixed Ridge control. Direct HF-to-SOH controls outperform the component pipeline but still fail severely on B0007.

The remaining upstream pattern is target-dependent HF generalization. Train-to-validation covariate/relationship shift is observed, particularly for B0007, but its physical cause is not identified. Source transfer changes the picture: B0005 can transfer effectively, whereas B0006 causes negative transfer; adding B0006 can degrade B0005-only transfer. B0018 has poorer joint-source support and receives little combined-source benefit. This supports the **method hypothesis** that source-target compatibility should be screened before source pooling. It does not yet prove that compatibility is a universal causal mechanism or a validated selection method.

## Positive results

1. Bounded residual fusion reduces observed catastrophic predictions from 25 to 0 under the frozen Phase-1 protocol.
2. B0005-only zero-shot transfer is strong on B0007 (RMSE .759, R2 .886) and positive on B0018 (RMSE 1.370, R2 .428).
3. B0005+B0006 calibrated transfer reaches B0007 RMSE .651 and R2 .916, clearly labelled calibrated rather than zero-shot.
4. Compatibility diagnostics expose source-specific negative-transfer risk and a B0007/B0018 support contrast.

## Negative results that must remain in the paper

1. No paper-style or residual-fusion configuration passes the multi-seed, two-target qualification gate.
2. Shorter fusion sequences and lower fusion capacity are not primary fixes.
3. Removing/adding GAN is not a cross-battery-consistent remedy; Trend is not the sole bottleneck.
4. Lightweight Ridge/MLP/GRU models do not stably replace the paper component models.
5. STL prefix instability exists but is not a sufficient causal explanation in the fixed predictor diagnostic.
6. More source batteries do not automatically help; B0006 is a demonstrated negative-transfer risk.

## Claim boundary

The defensible claim is: **within the audited NASA small-sample development setting, source identity and joint feature support are associated with transfer usefulness, motivating a pre-specified compatibility-aware source-selection method.** It is not: "compatibility causes transfer success", "the method is universally cross-dataset", or "the original paper protocol is fully reproduced".
"""


CANDIDATES = """# Innovation candidates and selection

## Candidate A — Compatibility-aware source selection (selected)

- **Research question:** Can a source selected using only target-prefix covariates and source training data improve or safely match all-source transfer under small-sample cross-battery SOH estimation?
- **Innovation:** Treat source choice as a pre-training decision. Rank individual sources by a frozen joint-HF compatibility score; select one source or abstain from transfer instead of automatically pooling every source.
- **Evidence:** Phase 9: B0005-only is beneficial, B0006-only is negative on both targets, and B0018 has larger combined-source nearest distance with weak transfer benefit.
- **Missing experiment:** A locked, pre-registered confirmation cohort with targets not used to formulate the score; five-seed zero-shot/calibrated comparisons against all-source and fixed individual-source baselines.
- **Workload / interpretability:** Moderate and high. It requires one transparent score and ordinary transfer models rather than a new opaque domain-adaptation network.
- **Difference from the original paper:** Changes source pooling/transfer protocol, not the paper's STL-fusion architecture.
- **Risk:** Phase 9 has only two targets, and score design after observing them would be post-hoc unless independently confirmed.
- **BSc / publication fit:** Best BSc main direction once confirmation is added; publication extension needs multiple new targets and preferably a second dataset.

## Candidate B — Bounded residual fusion as a secondary safety contribution

- **Research question:** Does an explicitly bounded residual correction prevent implausible SOH outputs under severe small-sample instability?
- **Innovation:** Constrain the learned correction rather than allowing unconstrained SOH generation.
- **Evidence:** Catastrophic count 25 -> 0, with no test use.
- **Missing experiment:** Broader safety evaluation with a declared safe baseline and a predefined operational utility for abstention/bounds.
- **Workload / interpretability:** Low and high.
- **Difference from original paper:** This is an explicit reproduction enhancement, not the disclosed paper formula.
- **Risk:** It has no demonstrated accuracy advantage, so it cannot be the paper's primary contribution.
- **BSc / publication fit:** Useful supporting contribution; weak alone for a methods paper.

## Candidate C — Mechanism-oriented negative reproducibility study

- **Research question:** Which upstream conditions make complex component-fusion SOH systems fail under a small target prefix?
- **Innovation:** Preserve failures, seed variance, fair baselines and causal-attribution tests instead of reporting a selected best run.
- **Evidence:** Phases 0-10 identify catastrophic fusion, upstream component failure, non-primary capacity/sequence effects and source-specific transfer risk.
- **Missing experiment:** More batteries and independent protocol clarification; no additional architecture is justified by current evidence.
- **Workload / interpretability:** Low-to-moderate and high.
- **Difference from original paper:** It is an audit/reproducibility contribution rather than a performance method.
- **Risk:** Lower algorithmic novelty.
- **BSc / publication fit:** Strong thesis/report narrative; publishable only with broader confirmation and clear venue fit.

## Decision

`PRIMARY_RESEARCH_DIRECTION = COMPATIBILITY_AWARE_SOURCE_SELECTION_FOR_SMALL_SAMPLE_CROSS_BATTERY_SOH`

`SECONDARY_CONTRIBUTION = BOUNDED_RESIDUAL_FUSION_AS_A_SAFETY_GUARD`

Candidate C remains the evidence and discussion framework, not a third claimed algorithmic innovation. Fusion regularization, LayerNorm, STL redesign and a lightweight TimesNet substitute are not selected because the Phase 4-7 evidence does not support them as primary fixes.
"""


DIRECTION = """# Final research direction

## 1. Primary innovation

**Compatibility-aware source selection for small-sample cross-battery SOH transfer.** Before transfer learning, calculate a pre-specified compatibility score from the target's labelled-prefix *covariates* and each candidate source's training covariates. Transfer only from the selected source (or abstain), rather than presuming that all available sources should be pooled.

## 2. Why this direction

It is the only method direction directly motivated by an observed actionable contrast: B0005 transfers well, B0006 transfers negatively, and adding sources does not guarantee improvement. It attacks an upstream data-support decision rather than applying another fusion-side regularizer after component errors already occur.

## 3. Supporting evidence

- Phase 8 shows transfer is target dependent: S2 zero-shot R2 .658 (B0007) versus .149 (B0018).
- Phase 9 shows B0005-only zero-shot R2 .886/.428, whereas B0006-only is -2.474/-1.905.
- Phase 9's predefined primary attribution is `MULTIVARIATE_SUPPORT_MISMATCH`; B0018's combined-source nearest distance (1.472) exceeds B0007's (1.123).
- Phase 4-7 rule out fusion capacity, short context and STL instability as primary remedies under the tested contracts.

## 4. Directions formally not selected

- **Fusion regularization / LayerNorm / KL / smoothing:** no longer required because component forecasts fail before fusion; paper L_weight is undisclosed.
- **STL redesign:** prefix stability alone did not improve the fixed direct prediction diagnostic.
- **Lightweight TimesNet replacement or a larger model grid:** capacity alternatives did not yield cross-battery qualification.
- **GAN-first solution:** effects are mixed and battery specific.
- **Bounded residual fusion as the primary method:** it is retained only as a safety contribution because it does not recover robust accuracy.

## 5. Experiments still required for a paper

The Phase-9 result is a diagnostic discovery, not a validation of a source-selection algorithm. The score, tie-break rule and abstention threshold must be frozen before a confirmation set is evaluated. The final comparison must include all-source, B0005-only, B0006-only, compatibility-selected source, target-only, zero-shot and calibrated tracks, with five seeds. The current B0007/B0018 validation results cannot be reused as a confirmatory winner-selection set.

## 6. Minimum completable version (BSc scope)

1. Freeze the score and protocol in `FINAL_EXPERIMENT_PLAN.md` before any new run.
2. Hold B0007/B0018 only as development evidence; evaluate the locked final test once **or**, preferably, use additional unseen NASA target batteries for confirmation.
3. State the scope as NASA small-sample compatibility-aware transfer and report all individual-source/all-source failures.

This is sufficient for a bounded undergraduate thesis claim, provided it explicitly calls the B0007/B0018 Phase-9 finding development evidence and reports non-confirmation honestly.

## 7. Publication extension

Use multiple unseen NASA targets and an independent CALCE (or equivalent) dataset, with the score and all choices frozen before evaluation. Only then may the work claim evidence that compatibility-aware selection generalizes beyond the initial NASA development targets. CALCE is not mechanically required because the original paper used it; it is required by the broader generalization claim.

## Contribution structure (maximum three)

1. **Diagnostic contribution:** evidence that upstream component predictability and source compatibility, rather than fusion capacity alone, govern failures in the audited small-prefix setting.
2. **Method contribution:** a transparent, pre-specified compatibility-aware source-selection/abstention rule for transfer.
3. **Robustness contribution:** five-seed, per-source, all-source and locked-test reporting, with bounded residual fusion reported as a safety guard only if its scope is retained.
"""


PLAN = """# Final experiment plan — design only, not executed

## Objective and confirmation boundary

Test the pre-registered hypothesis: **a compatibility-selected single source is at least as robust as all-source pooling and avoids negative transfer more often than indiscriminate pooling.** This plan is future work. No score, source or model may be selected using a target's validation or locked-test SOH labels.

The existing B0007/B0018 Phase-9 results are **development evidence**. They may motivate the score family but must not be treated as confirmation for a score designed after observing them. Confirmation must use either (a) additional untouched NASA target batteries or (b) a truly sealed final test used once after every choice is frozen. The stronger publication design uses both NASA confirmation targets and CALCE.

## Fixed data protocol

| Item | Rule |
|---|---|
| Candidate sources | A predeclared source bank, initially B0005 and B0006; never add/remove a source after outcome inspection. |
| Target prefix | First 20% cycles, chronological; target validation is the next 20%; locked test remains unread until the one final evaluation. |
| Features | Fixed Phase-8/9 HF feature columns only; no target future cycles or validation/test labels. |
| Scaling | Fit a common robust scaler on candidate-source training covariates only. Transform target prefix/validation/test without refit. |
| Component/fusion | Do not reopen STL/fusion grids. Use one predeclared simple transfer backbone (the Phase-8/9 Ridge control) for the source-selection test. |
| Seeds | `[42, 123, 2024, 3407, 7777]` for any stochastic secondary model; deterministic Ridge is reported once but never inflated to five pseudo-seeds. |

## Compatibility score — frozen before confirmation

For each candidate source `s`, using the common source-only scaler and target-prefix HF covariates `X_T`:

\\[
d_s = \\frac{1}{|X_T|}\\sum_{x\\in X_T}\\min_{z\\in X_s}\\lVert x-z\\rVert_2,
\\]

where `X_s` contains source-training HF covariates only. Define the deterministic compatibility score

\\[
C_s=-d_s.
\\]

Select `s* = argmax_s C_s` (equivalently, smallest `d_s`). Ties within `1e-12` break by the larger **predeclared source training-row count**, then lexical battery ID. This uses no target SOH labels, validation labels, test labels, validation metrics, or historical knowledge that B0005 happened to perform better.

### Optional calibrated-only diagnostic (not the primary score)

If a calibrated track is evaluated, a separate source-plus-target-prefix model may use target-prefix SOH labels *after* source selection. It must not change `s*`. Any label-aware compatibility score would be a different, explicitly calibrated method and must be tuned only through a nested development split; it is excluded from the minimum plan.

### Abstention rule

Do not tune an abstention cutoff on target validation/test outcomes. In the minimum study, selection always chooses the minimum-distance source and reports its distance. A later publication extension may add abstention only if its threshold is calibrated from source-only leave-one-source pseudo-target splits before target evaluation.

## Required comparisons

For every confirmation target, use exactly these source policies with the same backbone and feature contract:

1. `TARGET_ONLY`.
2. `ALL_SOURCE` (B0005+B0006 pooled).
3. `B0005_ONLY`.
4. `B0006_ONLY`.
5. `COMPATIBILITY_SELECTED_SOURCE` (chosen by the frozen score, before target outcomes).

For policies 2-5 report both:

- `ZERO_SHOT`: no target SOH labels in training;
- `CALIBRATED`: source training plus the declared target-prefix SOH labels, with source choice frozen before calibration.

The individual-source rows are mandatory controls, not alternatives selectively removed after results are seen.

## Evaluation and qualification

Selection occurs from train-prefix covariates only. Validation may be used only for a predeclared early-stop mechanism of a stochastic secondary backbone; it cannot choose the source, score, feature list, source bank or method winner. The locked test is opened exactly once after the complete registry/configuration is frozen.

Save per target × policy × track × seed: RMSE, MAE, MAPE, R2, worst absolute error, prediction min/max, catastrophic count, source score/rank, `UsesTargetSOHLabelsForTraining`, and `TestLoaded`.

`COMPATIBILITY_SELECTED_SOURCE` qualifies only if all are true:

1. Source is selected without validation/test outcomes and the selection manifest is written before fit.
2. `catastrophic_count=0` and no residual-bound violation if the optional bounded guard is used.
3. Across confirmation targets, median RMSE is no worse than `ALL_SOURCE` and its worst-target RMSE is lower, with both facts reported together.
4. It does not lose to the selected fixed-source baseline on every confirmation target.
5. No source/policy is removed, no seed is discarded and all labels/tracks remain truthfully named.

If these conditions fail, report `COMPATIBILITY_SELECTION_NOT_QUALIFIED`; do not retrofit the score.

## Minimum versus publication-grade data requirement

- **Minimum BSc evidence:** frozen score; two or more confirmation targets not used to choose the score, or a clearly limited one-time sealed-test evaluation; NASA-only claims; full negative results retained.
- **Publication-grade evidence:** several unseen NASA targets **and** CALCE/another independent dataset, with a fixed score and source bank. Generalization claims require second-dataset confirmation; without it the manuscript must say NASA-only.

## Prohibited actions

No validation/test-informed source ranking; no post-hoc declaration that B0005 was selected because it won Phase 9; no source-bank edits after outcomes; no target calibration called zero-shot; no new STL/fusion/epsilon grid; no complex domain-adaptation network in this first confirmation study.
"""


def main() -> None:
    require_sources()
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "EVIDENCE_MATRIX.csv", ["Finding", "Supporting Phase", "Battery", "Evidence", "Strength", "Implication"], EVIDENCE)
    (OUT / "RESEARCH_SYNTHESIS.md").write_text(SYNTHESIS, encoding="utf-8")
    (OUT / "INNOVATION_CANDIDATES.md").write_text(CANDIDATES, encoding="utf-8")
    (OUT / "FINAL_RESEARCH_DIRECTION.md").write_text(DIRECTION, encoding="utf-8")
    (OUT / "FINAL_EXPERIMENT_PLAN.md").write_text(PLAN, encoding="utf-8")
    print(f"Wrote research consolidation to {OUT}")


if __name__ == "__main__":
    main()
