# Final thesis positioning

## Selected positioning

`FINAL_THESIS_POSITIONING = C — Evidence-led reproduction failure attribution and cross-battery negative-transfer audit`

The thesis starts from a strict small-sample reproduction of the G-MTC-style SOH pipeline and follows the observed failure chain from unstable fusion, through component forecast error and representation diagnostics, to target-dependent transfer and source-specific negative-transfer risk. It is not framed as a successful new SOH algorithm.

## Why C is selected over A or B alone

| Criterion | A: Reproduction audit only | B: Transfer/compatibility only | C: Combined thesis (selected) |
|---|---|---|---|
| Evidence completeness | Strong but ends before transfer explanation | Strong transfer evidence but loses the upstream cause | Strong: all Phase 0-10 and both validation pivots form one chain |
| Narrative | Honest but mainly negative replication | Too narrow; both selection methods are not general methods | Explains why fusion tweaks failed and why source choice is risky |
| Technical contribution | Reproducibility and robustness audit | Association analysis only | Layered causal-attribution diagnostics plus transfer-risk evidence |
| Undergraduate fit | Good | Risky if claimed as an algorithm | Best: rigorous, bounded, data-backed and transparent |
| Overclaim risk | Low | High if source selection is framed as successful | Low if written as NASA-only diagnostic evidence |

## Central research question

**Under an explicitly declared NASA small-target-prefix protocol, where does a paper-style STL-component-fusion SOH pipeline fail, and what do source-specific transfer outcomes reveal about negative-transfer risk?**

Subquestions are: (1) whether bounded residual fusion changes catastrophic-output safety without claiming accuracy repair; (2) whether component forecasting fails before fusion; (3) which intuitive remedies are not primary explanations; and (4) whether source-specific effects and two pre-registered source-screening validations justify a general source-selection algorithm. The answer to the last subquestion is no for the present two-target evidence.

## Final research identity

This is a **NASA-only, development/validation-stage reproduction and robustness audit**. It contributes a disciplined negative result: the original complex pipeline is unstable in the local extreme-small-sample setting; simple source-compatibility screening rules are not reliably predictive of transfer utility. That negative result is technically useful because it prevents unsupported model tuning and test leakage.

## Formal route closure

- `CLOSED_UNSUPPORTED`: unsupervised HF-distance source selection. It selected B0006 for both targets and lost to all-source in every formal contrast.
- `CLOSED_PARTIAL`: prefix-supervised source screening. It succeeds only on B0018 and selects the wrong individual source for B0007; it cannot be a cross-target method claim.
- `CLOSED_NOT_PRIMARY`: fusion-sequence optimization, fusion-capacity reduction, GAN removal, trend-only replacement, lightweight component replacement and causal STL redesign. Their fixed diagnostics do not identify a robust remedy.

These statuses are evidence-freeze decisions. They may be discussed as negative controls, but may not be reopened as thesis tuning routes.
