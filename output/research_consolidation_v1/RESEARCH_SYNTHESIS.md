# Research synthesis: evidence-led final story

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
