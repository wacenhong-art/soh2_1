# Decision Record — Cold-start Stress Test v1

```text
EXPERIMENT_NAME=COLD_START_STRESS_TEST_v1
REPOSITORY=soh2_1
BASELINE=S0_RIDGE
BASELINE_SOURCE=soh02@dc931f7
CURRENT_AUDITED_COMMIT=b0d0af7bc5c1d0fb56230638519567d6bc12844f
BASELINE_RECOMPUTED=False
OUTER_VALIDATION_LOADED=False
TestLoaded=False
MODEL_OR_PROTOCOL_CHANGED=False
```

## 1. Research question and boundary

**Question under review (not a result claim):** Is the frozen NASA S0 protocol
large enough to test, without leakage, whether reducing only the earliest
target-labelled fitting history degrades the fixed S0 estimator on the same
chronological outer-validation interval?

This is a deployment-stress feasibility diagnostic. It neither presumes that
S0 fails under cold start nor claims a new method or innovation. S0 remains an
end-of-current-completed-discharge, target-only estimator; it is not a
pre-discharge, RUL, transfer, or paper-method-reproduction experiment.

## 2. Frozen S0 evidence inspected

| Item | Frozen evidence |
|---|---|
| Script entry | `scripts/98_reproduce_s0_ridge.py`, reusing `scripts/84_strong_baseline_raw_feature_ablation.py` |
| Features | Seven current completed-discharge F1 descriptors listed in `S0_ACTUAL_PROTOCOL.md` |
| Model | Deterministic target-only `Ridge(alpha=0.1)` |
| Preprocessing | Training-fit median imputation, feature standardization, target standardization |
| B0007 split | train `[0,33)`, validation `[33,67)`; 33 train and 34 validation rows |
| B0018 split | train `[0,25)`, validation `[25,51)`; 25 train and 26 validation rows |
| Test boundary | No post-validation row may be loaded; `TestLoaded=False` |

The recorded outer-validation reproduction metrics are historical artifacts
only and are not recalculated or used to select a budget or threshold here.

## 3. Cold-start setting determination

`COLD_START_SETTING=FIXED_FEATURE_REFIT`.

S0 contains no source model, pretrained representation, synthetic sample, or
target-calibration layer. Therefore `CALIBRATION_ONLY` is invalid. A later
authorized run may only refit the same fixed S0 Ridge on the earliest labelled
training rows; it must not change features, alpha, preprocessing, labels,
source bank, or evaluation rows.

## 4. Training-only budget audit

Budget count is `floor(N_train * ratio)`. The remainder below is unused
training-prefix history, not an alternative evaluation set. Any future outer
evaluation uses the same fixed validation interval for FULL and every
cold-start budget.

| Battery | N_train | Ratio | Labelled rows | Unused training rows | Status |
|---|---:|---:|---:|---:|---|
| B0007 | 33 | 10% | 3 | 30 | `INVALID_BUDGET` |
| B0007 | 33 | 20% | 6 | 27 | `STATISTICALLY_WEAK` |
| B0007 | 33 | 40% | 13 | 20 | eligible by count only |
| B0007 | 33 | FULL | 33 | 0 | reference |
| B0018 | 25 | 10% | 2 | 23 | `INVALID_BUDGET` |
| B0018 | 25 | 20% | 5 | 20 | `STATISTICALLY_WEAK` |
| B0018 | 25 | 40% | 10 | 15 | eligible by count only |
| B0018 | 25 | FULL | 25 | 0 | reference |

Rules: labelled rows below 5 are invalid; rows from 5 through 7 are
statistically weak. `10%` is excluded. `20%` is not eligible for a
confirmatory comparison. The only count-supported provisional cold-start
budget is `40%`; no additional ratio is authorized by this record.

## 5. Provisional future protocol — not authorized to execute

If and only if this record is later amended to `PASS` by a human reviewer,
the sole comparison is `40%` versus `FULL` for each target:

1. Sort rows by the already frozen chronological cycle order.
2. Fit only the earliest `floor(N_train * 0.40)` labelled training rows for
   the 40% condition; fit all training rows for FULL.
3. In each condition, fit all preprocessing objects and the fixed
   `Ridge(alpha=0.1)` only on that condition's fitting rows.
4. Keep F1 feature columns, SOH label definition, model form, alpha, and all
   outer validation row indices unchanged.
5. Use the pre-existing validation prefix once for evaluation. Never open a
   post-validation/test row; do not tune after seeing validation outcomes.

Primary metric: RMSE. Secondary metrics: MAE and R2. No seed sweep is
applicable because fixed Ridge is deterministic.

## 6. Provisional falsifiable failure criterion

`REPRO_DEFINED`, not attributed to a paper.

For a target, cold-start degradation is present only if all conditions hold on
the identical fixed outer-validation rows:

1. `RMSE_40 / RMSE_FULL >= 1.25`;
2. `MAE_40 / MAE_FULL >= 1.20`; and
3. the median paired change `median(|e_40| - |e_FULL|) > 0`.

The cold-start failure hypothesis is supported only if the target-level
criterion holds for **both** B0007 and B0018. This prevents a one-battery
claim and the median condition prevents a conclusion driven only by one
extreme cycle. Any other outcome is `NOT_SUPPORTED` for this fixed stress
hypothesis; it does not authorize a new budget, metric, threshold, feature,
or model.

## 7. Literature basis and evidence boundary

- A 2026 early-deployment paper states in its accessible abstract that
  data-driven SOH prediction typically requires large, high-quality,
  long-duration cycling datasets. It supports the general cold-start problem,
  but its Conclusion/Limitations text was not accessible in this audit:
  `UNVERIFIED_CONCLUSION_LIMITATIONS`.
  DOI: https://doi.org/10.1016/j.egyai.2026.100712
- A 2026 real-world EV SOH review identifies sparse/irregular sampling,
  incomplete labels, noise, and domain shift as deployment challenges. It
  supports deployment relevance but does not validate the S0-specific
  cold-start hypothesis. https://www.mdpi.com/2313-0105/12/5/174
- A 2025 practical real-world-data review identifies irregular driving,
  incomplete charging cycles, and unpredictable environments as robustness
  concerns. It does not establish a numerical cold-start threshold.
  https://www.sciencedirect.com/science/article/pii/S2095495625005741

No source above is claimed to prescribe the 40% budget or the criterion in
Section 6.

## 8. Gate review

| Gate | Status | Evidence and constraint |
|---|---|---|
| G1 PROBLEM | **FAIL** | Clean S0 has high frozen outer-validation accuracy, but no observed S0 cold-start failure. A literature deployment concern is not the repository-required “Phase X observed failure”. |
| G2 PRIOR | PASS | Limited initial data is a literature-supported deployment concern; source-specific conclusions are marked unverified where inaccessible. |
| G3 LEAKAGE | CONDITIONAL PASS | Proposed budget selection uses training counts only; validation/test labels are not used for protocol selection. A future implementation must prove this mechanically. |
| G4 BASELINES | PASS | Same-target FULL S0 is the mandatory simple reference; transfer baselines are not applicable because S0 is target-only and this is not transfer. |
| G5 GENERALIZATION | PASS | B0007/B0018 could only be development evidence. No external/generalization claim is permitted. |
| G6 FALSIFIABILITY | PASS | One count-supported 40% budget, fixed integer rule, fixed outer boundary, metrics, failure rule, and stop rule are written before validation access. |
| G7 COMPLEXITY | PASS | No network, feature, hyperparameter, or training-family change is proposed. |

Because G1 is FAIL, the guardrails require:

```text
EXPERIMENT_NOT_AUTHORIZED
RESEARCH_DIRECTION_REJECTED
```

## 9. Human decision required

A human researcher must decide whether to amend the governing research
question with a documented, pre-existing observed cold-start failure, or to
close this hypothesis. This record does not redefine an absence of evidence
as failure and does not authorize an experiment.

## 10. Integrity check

```text
VIBE_RESEARCH_RULES_ACKNOWLEDGED=True
CITATION_FABRICATION_FOUND=False
AI_INNOVATION_CLAIM_MADE=False
OUTER_VALIDATION_OR_TEST_LABEL_LOADED=False
EXPERIMENT_RESULT_GENERATED=False
S0_OR_PROTOCOL_MODIFIED=False
HYPOTHESIS_SHOPPING_FOUND=False
VIBE_RESEARCH_INTEGRITY_GATE=PASS
```
