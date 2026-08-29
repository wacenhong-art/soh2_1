# Final contributions

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
