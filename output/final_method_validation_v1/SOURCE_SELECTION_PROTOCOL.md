# Source-selection protocol — frozen before Final Method Validation

**Status:** `FROZEN_PRE_RUN`  
**Scope:** NASA B0005/B0006 candidate sources; B0007/B0018 targets; validation-only method validation.  
**Prohibited information:** target validation/test SOH, target test HF rows, Phase 8/9 transfer metrics, and manual knowledge of which source previously performed well.

## Fixed candidates and target boundary

- Candidate sources: `B0005`, `B0006`; each contributes its full real training HF trajectory, exactly as in Phase 8/9 Ridge transfer diagnostics.
- Target selection input: the first `TrainEnd` rows only, where `TrainEnd` is read from the frozen Phase-1 run manifest. Only `HF1`, `HF2`, and `HF3` are used. Target SOH is never accessed by selection.
- Target model evaluation input: only rows through `ValidationEnd`; target rows after `ValidationEnd` must not be read.
- HF window length: `W=10`; Ridge regularization: `alpha=1.0`.

## One fixed compatibility score

Let \(X_s\) denote the `HF1/HF2/HF3` rows of candidate source \(s\), and \(X_T\) the target's allowed first-20% prefix HF rows.

1. Fit a **common** column-wise scaler using \(X_{B0005}\cup X_{B0006}\) only:

\[
z(x) = \frac{x-\mu_{source}}{\max(\sigma_{source},10^{-8})}.
\]

2. For every target-prefix HF row \(x\in X_T\), compute its Euclidean nearest-neighbor distance to the standardized candidate-source rows:

\[
d_s(x)=\min_{z\in X_s}\lVert z(x)-z(z)\rVert_2.
\]

3. Define the sole selection score:

\[
\operatorname{CompatibilityScore}(s,T)=\frac{1}{|X_T|}\sum_{x\in X_T}d_s(x).
\]

Smaller values mean higher compatibility. No median score, coverage threshold, label-aware score, or alternative distance is evaluated in this validation.

## Automatic selection and tie breaking

\[
s^*(T)=\arg\min_{s\in\{B0005,B0006\}}\operatorname{CompatibilityScore}(s,T).
\]

An exact numerical tie is defined as an absolute score difference \(\le 10^{-12}\). It is resolved by: (1) larger source HF training-row count; (2) lexical battery ID. The code must additionally repeat the computation after reversing candidate order and after swapping arbitrary source display aliases; the underlying selected source and score must remain identical. A failed check invalidates the experiment.

## Fixed models and comparison groups

The only predictor is the Phase-8/9 Ridge HF-to-SOH control. It is not tuned.

| ID | Model | Source labels used | Target prefix SOH labels used |
|---|---|---:|---:|
| M0 | `TARGET_ONLY` | none | yes |
| M1 | `ALL_SOURCE_ZERO_SHOT` | B0005+B0006 | no |
| M2 | `SELECTED_SOURCE_ZERO_SHOT` | \(s^*(T)\) | no |
| M3 | `ALL_SOURCE_CALIBRATED` | B0005+B0006 | yes |
| M4 | `SELECTED_SOURCE_CALIBRATED` | \(s^*(T)\) | yes |

For M0/M3/M4, target-prefix SOH can be used only inside model fitting after \(s^*(T)\) is already written to the selection manifest. Zero-shot models must have `UsesTargetSOHLabelsForTraining=false`.

## Validation-only evaluation and decision rules

All score, selection and model comparisons use the pre-existing chronological train/validation protocol. The target test partition stays unread. Each target × model row must report RMSE, MAE, R2, prediction standard deviation, training sample count, score, selected source, label-use flag and `TestLoaded=false`.

The result is `COMPATIBILITY_AWARE_SELECTION_SUPPORTED` only if selection is label-free and order/name invariant, both targets are reported, selected-source models do not show an obvious overall deterioration versus all-source, and the direction is not limited to one target. If benefit is limited to one target, the maximum permissible conclusion is `BATTERY_SPECIFIC_EVIDENCE_ONLY` / `COMPATIBILITY_AWARE_SELECTION_PARTIALLY_SUPPORTED`.

## Explicit non-goals

This protocol does not select a source because B0005 previously achieved a better transfer metric; does not rank sources using validation/test SOH; does not change the source bank after outcomes; does not increase the target label fraction; does not use CALCE; and does not combine source selection with bounded residual fusion as a single claimed method.
