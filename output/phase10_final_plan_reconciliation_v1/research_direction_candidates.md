# Research direction candidates (maximum three)

## Candidate 1 — Compatibility-aware source selection for small-sample SOH transfer

- **Research question:** Can a source-selection rule based on joint HF support and a calibration-free compatibility score prevent negative transfer before target-label adaptation?
- **Core innovation:** Treat source choice as a first-class decision, rather than pooling all source batteries. Exclude or down-weight sources with poor joint support; report abstention when no compatible source exists.
- **Current evidence:** Phase 9 shows B0005 helps while B0006 harms both targets; B0018 has a larger S2 nearest-source distance than B0007 and no S2 improvement.
- **Missing evidence:** Pre-registered leave-one-target-out evaluation over more NASA batteries; a held-out source-selection rule; CALCE or another independent dataset before cross-dataset claims.
- **Risk:** Two targets can overfit a compatibility narrative; nearest-neighbor distance need not capture causal electrochemistry.
- **Suitability:** Strongest BSc thesis direction after bounded validation; plausible publication direction only with broader batteries and independent data.

## Candidate 2 — Failure-aware SOH transfer with abstention and bounded correction

- **Research question:** Can a predictor abstain or revert to a declared safe baseline when support mismatch is high, while guaranteeing bounded deviation from that baseline?
- **Core innovation:** Combine compatibility screening with the Phase-1 bounded residual safety property; evaluate safety and failure rate separately from accuracy.
- **Current evidence:** Residual fusion eliminated catastrophic predictions, but did not solve accuracy. This makes it a safety mechanism, not an accuracy innovation.
- **Missing evidence:** A pre-specified safe baseline with positive performance across targets; utility/cost definition for abstention; more batteries.
- **Risk:** May be operationally useful but weak as a standalone accuracy paper.
- **Suitability:** Good BSc engineering extension; publication value depends on genuine safety/coverage evidence.

## Candidate 3 — Descriptive small-sample fusion failure study

- **Research question:** Under what parameter/sample, component-error and source-compatibility conditions do STL-component fusion systems fail?
- **Core innovation:** A rigorously negative, mechanism-oriented reproducibility study: retain failed seeds, locked-test boundaries and causal-attribution checks rather than presenting only best results.
- **Current evidence:** Phase 1-9 jointly isolate catastrophic fusion, component failure, non-primary sequence/capacity effects and source-specific negative transfer.
- **Missing evidence:** More target batteries and a careful paper-protocol clarification; no new large neural architecture is justified by the current evidence.
- **Risk:** Novelty is methodological and may require a strong reproducibility venue fit.
- **Suitability:** Strong BSc thesis/report framing now; publication candidate if expanded with pre-registered cross-dataset validation.
