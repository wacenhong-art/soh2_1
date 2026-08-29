# Prefix-supervised source-screening protocol — frozen before validation

**Status:** `FROZEN_PRE_RUN`  
**Regime:** `CALIBRATED / FEW_SHOT_TRANSFER`, never zero-shot.  
**Source candidates:** B0005 and B0006. **Targets:** B0007 and B0018.  
**Test policy:** target CSVs are read only through `ValidationEnd`; target test rows and labels remain unread.

## Legal information boundary

The selection score may use only each source's full real `HF1/HF2/HF3` and `SOH`, plus the target's chronological first-20% prefix `HF1/HF2/HF3` and `SOH` (rows before `TrainEnd` in the frozen Phase-1 manifest). It may not use target validation/test rows or labels, historical Phase 8/9 transfer metrics, previous knowledge that B0005 was favourable, or any manually assigned source priority.

## One pre-registered selection score

For each source \(s\), train one fixed source-only Ridge model \(f_s\) using its full real trajectory:

- HF features: `HF1`, `HF2`, `HF3`, transformed into a fixed `W=10` lag window;
- feature scaler: mean and standard deviation fit on that source's HF rows only;
- target scaler: mean and standard deviation fit on that source's SOH rows only;
- model: `Ridge(alpha=1.0)`; no tuning, no neural model and no alternative score.

Apply \(f_s\) to target prefix windows with valid indices \(t=W,\ldots,TrainEnd-1\). Define:

\[
E(s,T)=\sqrt{\frac{1}{n_T}\sum_{t=W}^{TrainEnd-1}(y_t-f_s(x_t))^2}.
\]

`PrefixCompatibilityError(s,T) = E(s,T)`. Smaller error indicates greater supervised predictive compatibility. The automatic selection is:

\[
s^*(T)=\arg\min_{s\in\{B0005,B0006\}} E(s,T).
\]

The only tie definition is \(|E(B0005,T)-E(B0006,T)|\le10^{-12}\), resolved first by larger source training-window count, then lexical battery ID. No additional score is tested or substituted after validation outcomes are seen.

## Fixed robustness diagnostic

The target prefix's valid windows are divided chronologically into **three contiguous blocks** using `numpy.array_split`. For each source-only model, report the three block RMSEs plus mean, worst and standard deviation. These are a stability diagnostic only: the full-prefix `E(s,T)` above remains the sole selection score, even if block results disagree.

## Fixed validation models

All fitting uses the entire legal target first-20% prefix after selection is written; no target-label proportion is increased. `W=10`, `alpha=1.0`, and the Phase-8/9 HF window construction are fixed.

| ID | Model | Source labels | Target prefix SOH labels | Status |
|---|---|---:|---:|---|
| C0 | `TARGET_ONLY` | none | yes | formal baseline |
| C1 | `ALL_SOURCE_CALIBRATED` | B0005+B0006 | yes | formal comparator |
| C2 | `PREFIX_SELECTED_SOURCE_CALIBRATED` | \(s^*(T)\) | yes | formal method |
| C3 | `ORACLE_SOURCE_DIAGNOSTIC` | post-hoc best of B0005/B0006 | yes | diagnostic only; never a method winner |

For C1/C2, a common feature scaler is fit on the model's source HF rows plus legal target-prefix HF rows; the SOH scaler uses the labels entering that same model. C0 uses target-prefix rows only. This is lawful calibrated preprocessing and is applied identically to all respective model rows.

## Sanity and decision rules

Candidate-order reversal and arbitrary source-display-name permutation must leave canonical errors and selected source unchanged. Any failure invalidates the run. Save selection errors, block statistics, all C0-C3 metrics, oracle gap and `TestLoaded=false` for every row.

The strongest possible claim is `PREFIX_SUPERVISED_SOURCE_SCREENING_SUPPORTED` only when selection is label-bounded, invariant, both targets are automatically selected, C2 is not materially worse than C1 on both targets, at least one target reduces negative transfer, and test is locked. If only one target benefits, report `PREFIX_SUPERVISED_SOURCE_SCREENING_PARTIALLY_SUPPORTED`. If the score selects poorly or C2 is broadly worse, report `PREFIX_SUPERVISED_SELECTION_NOT_SUPPORTED` and stop this source-selection line—do not design a third score.

## Explicit exclusions

No validation/test-informed score, no CALCE, no GAN/STL/TimesNet/fusion grid, no complex domain adaptation, no source-bank alteration, no label-fraction expansion, and no combination with bounded residual fusion as one claimed primary method.
