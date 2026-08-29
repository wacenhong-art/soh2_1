# Final causal chain (Phase 10)

## Verified

1. **Unconstrained paper-style fusion can produce catastrophic validation predictions under this target-prefix protocol.** Phase 1 recorded 25 catastrophic predictions for `PAPER_FUSION`; bounded residual fusion reduced this to zero without loading test data.
2. **The main observed failure precedes fusion.** Phase 4A's oracle STL reconstruction is exact, while predicted-component reconstruction has validation R2 -13.019 (B0007) and -13.642 (B0018). Phase 5 confirmed that more complex component networks do not repair this under the fixed protocol.
3. **Source selection matters.** Phase 9 finds B0005 can help, while B0006 produces negative transfer on both targets. The predefined primary attribution is `MULTIVARIATE_SUPPORT_MISMATCH`; `SOURCE_SPECIFIC_NEGATIVE_TRANSFER` is independently supported as a source-level risk.

## Partly supported

1. **Small-sample fusion capacity is a contributor, not the primary bottleneck.** Parameter/sample ratios fell from 1,793 (B0018 full fusion) to 104.6 (tiny GRU) and then 3.8 (minimal fusion), but none met the qualification gate.
2. **HF-to-target distribution/relationship shift is associated with poor target-only prediction.** Phase 6 detects large train-validation differences, especially for B0007, but the component target itself can move with appended prefix observations.
3. **Compatibility-aware transfer is a credible research mechanism.** B0007 benefits substantially from B0005/S2, while B0018 has larger nearest-source distance and no comparable S2 benefit. This is evidence for a testable selection rule, not proof of a universal physical mechanism.

## Negated as a primary explanation within the tested contracts

1. **Shorter fusion sequence is not the primary bottleneck.** It increased B0007/B0018 fusion samples but did not qualify a model.
2. **Fusion capacity alone is not the primary bottleneck.** Tiny recurrent and nonrecurrent alternatives remain non-qualifying.
3. **STL prefix instability is not causally linked to forecast failure in the fixed Ridge diagnostic.** Causal EMA/median representations are prefix invariant yet yield no predeclared >=1% RMSE improvement.
4. **More component-network complexity is not an evidenced repair.** The Phase 5 paper component models, tiny MLP/GRU and simple controls do not establish a robust replacement.

## Uncertain / deliberately not claimed

1. The physical cause of HF shift and of source-target incompatibility is not identified.
2. The paper's 60/20/20 versus first-20%-small-sample descriptions remain `PAPER_AMBIGUOUS`.
3. NASA evidence on B0007/B0018 cannot establish cross-dataset generalization. CALCE is required only for a cross-dataset claim, not for closure of the current NASA mechanism audit.
