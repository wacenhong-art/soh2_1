# Innovation candidates and selection

## Candidate A — Compatibility-aware source selection (selected)

- **Research question:** Can a source selected using only target-prefix covariates and source training data improve or safely match all-source transfer under small-sample cross-battery SOH estimation?
- **Innovation:** Treat source choice as a pre-training decision. Rank individual sources by a frozen joint-HF compatibility score; select one source or abstain from transfer instead of automatically pooling every source.
- **Evidence:** Phase 9: B0005-only is beneficial, B0006-only is negative on both targets, and B0018 has larger combined-source nearest distance with weak transfer benefit.
- **Missing experiment:** A locked, pre-registered confirmation cohort with targets not used to formulate the score; five-seed zero-shot/calibrated comparisons against all-source and fixed individual-source baselines.
- **Workload / interpretability:** Moderate and high. It requires one transparent score and ordinary transfer models rather than a new opaque domain-adaptation network.
- **Difference from the original paper:** Changes source pooling/transfer protocol, not the paper's STL-fusion architecture.
- **Risk:** Phase 9 has only two targets, and score design after observing them would be post-hoc unless independently confirmed.
- **BSc / publication fit:** Best BSc main direction once confirmation is added; publication extension needs multiple new targets and preferably a second dataset.

## Candidate B — Bounded residual fusion as a secondary safety contribution

- **Research question:** Does an explicitly bounded residual correction prevent implausible SOH outputs under severe small-sample instability?
- **Innovation:** Constrain the learned correction rather than allowing unconstrained SOH generation.
- **Evidence:** Catastrophic count 25 -> 0, with no test use.
- **Missing experiment:** Broader safety evaluation with a declared safe baseline and a predefined operational utility for abstention/bounds.
- **Workload / interpretability:** Low and high.
- **Difference from original paper:** This is an explicit reproduction enhancement, not the disclosed paper formula.
- **Risk:** It has no demonstrated accuracy advantage, so it cannot be the paper's primary contribution.
- **BSc / publication fit:** Useful supporting contribution; weak alone for a methods paper.

## Candidate C — Mechanism-oriented negative reproducibility study

- **Research question:** Which upstream conditions make complex component-fusion SOH systems fail under a small target prefix?
- **Innovation:** Preserve failures, seed variance, fair baselines and causal-attribution tests instead of reporting a selected best run.
- **Evidence:** Phases 0-10 identify catastrophic fusion, upstream component failure, non-primary capacity/sequence effects and source-specific transfer risk.
- **Missing experiment:** More batteries and independent protocol clarification; no additional architecture is justified by current evidence.
- **Workload / interpretability:** Low-to-moderate and high.
- **Difference from original paper:** It is an audit/reproducibility contribution rather than a performance method.
- **Risk:** Lower algorithmic novelty.
- **BSc / publication fit:** Strong thesis/report narrative; publishable only with broader confirmation and clear venue fit.

## Decision

`PRIMARY_RESEARCH_DIRECTION = COMPATIBILITY_AWARE_SOURCE_SELECTION_FOR_SMALL_SAMPLE_CROSS_BATTERY_SOH`

`SECONDARY_CONTRIBUTION = BOUNDED_RESIDUAL_FUSION_AS_A_SAFETY_GUARD`

Candidate C remains the evidence and discussion framework, not a third claimed algorithmic innovation. Fusion regularization, LayerNorm, STL redesign and a lightweight TimesNet substitute are not selected because the Phase 4-7 evidence does not support them as primary fixes.
