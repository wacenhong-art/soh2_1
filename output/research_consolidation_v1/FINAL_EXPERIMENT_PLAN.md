# Final experiment plan — design only, not executed

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

\[
d_s = \frac{1}{|X_T|}\sum_{x\in X_T}\min_{z\in X_s}\lVert x-z\rVert_2,
\]

where `X_s` contains source-training HF covariates only. Define the deterministic compatibility score

\[
C_s=-d_s.
\]

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
