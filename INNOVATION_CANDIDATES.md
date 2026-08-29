# Innovation Candidates — Authorization Status

`NO_INNOVATION_METHOD_AUTHORIZED`

| Rank | Problem-level candidate | Gate status on current targets | Minimum future falsification |
|---:|---|---|---|
| 1 | Uncertainty-gated transfer safety | G1 PASS; G2 PARTIAL; G3 FAIL | On unseen targets, freeze a reliability gate and compare `TARGET_ONLY`, `ALL_SOURCE`, and `BEST_SIMPLE_BASELINE`; reject if worst-case harm does not decrease. |
| 2 | Prefix-observable stage-mismatch diagnosis | G1 PASS; G2 PARTIAL; G3 FAIL | Use prefix-only stage observable to predict a pre-registered error regime on independent targets; reject if it fails. |
| 3 | Source-mixture robustness under incompatible samples | G1 PASS; G2 PARTIAL; G3 FAIL and red-line risk high | Freeze a sample-weight rule on new targets; reject unless it beats both all-source and target-only on worst-case harm. |

## Explicitly excluded

- A third source-selection distance or score: `CLOSED_UNSUPPORTED`.
- Modification of prefix-supervised screening: `CLOSED_PARTIAL`.
- Fusion sequence/capacity, GAN, Trend-only, lightweight components or causal STL grids: `CLOSED_NOT_PRIMARY`.
- New Transformer, attention, GAN or loss without a new Gate-approved problem statement.

## Primary innovation problem

`PRIMARY_INNOVATION_PROBLEM = NOT_AUTHORIZED_YET`

If a future independent cohort and a new Decision Record exist, the first problem to re-evaluate is: how can small-sample cross-battery SOH transfer use a pre-registered, leak-free reliability criterion to reduce worst-case negative-transfer harm when source knowledge is unreliable?

This is a problem, not a network name or a promise of positive RMSE/R2.
