# Final research direction

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
