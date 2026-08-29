# G-MTC Reproduction Audit and Phase 1 Contract

Verification status: `ANALYZED` for paper interpretation; experiment results become
`VERIFIED` only after `scripts/65_phase1_failure_isolation.py` completes.

## Evidence boundary

The paper discloses a chronological 60%/20%/20% target split and, separately,
defines the small-sample target training set as the first 20% of total cycle life
augmented with five synthetic trajectories. It does not reconcile the two
descriptions. Their relationship is therefore `PAPER_AMBIGUOUS`.

The paper publishes

\[
L_{total}=L_{pred}+\lambda L_{weight},
\]

but does not disclose a reproducible definition of \(L_{weight}\). Phase 1 labels
it `UNVERIFIED_DISABLED` and sets its coefficient to zero. The former repository
KL completion remains `REPRO_DEFINED_NOT_PAPER_ORIGINAL` and is prohibited in
Phase 1.

## Experiment tracks

| Track | Target labels | Allowed changes | Claim boundary |
|---|---|---|---|
| `PAPER_FUSION` | Paper protocol chosen explicitly | No enhancement switches | Structural paper baseline |
| `ENHANCEMENT` | Same split as its paired baseline | One pre-registered modification | Our modification |
| `ZERO_SHOT` | None | Source-only training | Must not use target SOH labels |
| `CALIBRATED` | Declared target prefix | Prefix-only adaptation | Must not be called zero-shot |

Phase 1 uses `PAPER_FUSION` with the paper's first-20%-of-life small-sample
description, the next 20% as validation, and the remainder locked and unloaded.

## Phase 1 fixed contract

| Parameter | Value | Status |
|---|---:|---|
| component window | 10 | `PAPER_DEFINED` |
| fusion sequence length | 10 | `REPRO_DEFINED` |
| Bi-LSTM hidden size | 16 | `PAPER_DEFINED` |
| Bi-LSTM layers | 1 | `PAPER_DEFINED` |
| normalization | BatchNorm1d | `PAPER_DEFINED` |
| learning rate | 0.001 | `PAPER_DEFINED` |
| batch size | 32 | `PAPER_DEFINED` |
| early-stopping patience | 50 | `PAPER_DEFINED` |
| weight decay | 1e-5 | `PAPER_DEFINED` |
| STL period | 12 | `REPRO_DEFINED` |
| fusion input semantics | predicted components, causal deltas, ratios | `REPRO_DEFINED` |
| L_weight | disabled | `UNVERIFIED_DISABLED` |

`PAPER_FUSION` rejects stable initialization, residual fusion, LayerNorm, KL
regularization, temporal smoothing, transfer learning, OSELM, clipping, test
calibration, and test-set selection.

## Phase 1 enhancement

Only constrained residual fusion is permitted:

\[
y_{base}=\hat T+\hat S+\hat R,
\qquad
\Delta=100\epsilon\tanh(f(x)),
\qquad
\hat y=y_{base}+\Delta.
\]

The factor 100 converts SOH fractions to the repository's percentage-point
space. The registered values are \(\epsilon\in\{0.02,0.05,0.10\}\), giving
bounds of 2, 5, and 10 percentage points.

## Evaluation gate

Seeds are `[42, 123, 2024, 3407, 7777]` on B0007 and B0018. A configuration
qualifies only when every battery-seed run has finite positive R2, beats the
paired training-mean baseline RMSE, has zero predictions outside 50--110 SOH
percentage points, and records no test access. Otherwise the decision is
`NO_QUALIFIED_CONFIGURATION`.

Baselines are training-mean, one-step persistence, and predicted STL component
addition. Persistence uses the immediately preceding observed SOH and is reported
as an online-observation baseline, not as a zero-shot model.

## Phase 1 verified result

Code commit `e4472a4` completed 40 validation-only fusion runs: 10 paper runs
and 30 constrained-residual runs. All 40 manifests record `test_loaded=false`.

| Configuration | Mean RMSE | Worst RMSE | Worst R2 | Catastrophic count | Decision |
|---|---:|---:|---:|---:|---|
| PAPER_FUSION | 11.8127 | 74.7555 | -1109.7164 | 25 | NO_QUALIFIED_CONFIGURATION |
| residual epsilon 0.02 | 6.2617 | 13.7794 | -56.8561 | 0 | NO_QUALIFIED_CONFIGURATION |
| residual epsilon 0.05 | 5.8883 | 13.5507 | -54.9516 | 0 | NO_QUALIFIED_CONFIGURATION |
| residual epsilon 0.10 | 6.1922 | 13.1762 | -51.9013 | 0 | NO_QUALIFIED_CONFIGURATION |

The paired bounded head eliminates threshold-defined catastrophic predictions,
supporting the unconstrained prediction head as a direct failure mechanism.
It does not restore positive R2 or consistent improvement over the mean baseline.
B0018 remains seed-sensitive (paper RMSE mean 4.4701, standard deviation 4.9613)
with only five fusion training samples; B0007 is even less stable because one
paper seed catastrophically fails. The next justified experiment is a small,
isolated fusion-sequence-length ablation while component window remains fixed at
the paper-defined value 10.
