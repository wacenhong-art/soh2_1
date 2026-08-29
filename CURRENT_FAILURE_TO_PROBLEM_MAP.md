# Current Failure to Problem Map

## Static evidence only

| Observed fact | Static evidence | What it supports | What it does not support |
|---|---|---|---|
| B0007 target-only Ridge fails later validation | Phase 6: HF-only Ridge RMSE 5.988, R2 -6.126 | A static prefix-fitted HF→SOH mapping is inadequate in this protocol | A specific physical stage mechanism |
| B0018 target-only Ridge is relatively stable | Phase 6: RMSE 1.564, R2 .255 | The failure is target-dependent, not a universal Ridge defect | That B0018 is an independent confirmation set |
| Adding normalized cycle scalar does not help | Phase 6: HF-only versus HF+train-scaled-cycle changes RMSE by <.01 on both targets | One scalar progression proxy is insufficient | All temporal/degradation context is useless |
| HF relationship-shift diagnostics change | Phase 6: max Pearson/Spearman change B0007 1.650/1.479; B0018 1.020/1.085 | `EARLY_TO_LATE_MAPPING_SHIFT` is a plausible diagnostic problem | Causality or a trained stage model benefit |
| B0007 calibrated transfer can work while B0018 gains little | Phase 8: B0007 R2 .916; B0018 R2 .255 | Mapping/transfer behavior is target-specific | A source selection score should be redesigned |
| Component prediction fails before fusion | Phase 4A ledger: predicted reconstruction R2 -13.019/-13.642 | Fusion is not the primary accuracy bottleneck | A new fusion backbone is justified |

## Candidate assessment

### A. EARLY_TO_LATE_DEGRADATION_MAPPING_SHIFT

The observed diagnostics make this the strongest *problem explanation*. However, the newest degradation-aligned SSL preprint already uses cycle-order ranking to learn aging-consistent representations. A distinct, leak-free contribution would need an independent target cohort and a difference beyond simply adding order ranking. **Current status: not authorized.**

### B. DEGRADATION_CONTEXT_MISSING

The failed scalar-cycle control leaves open whether richer local context helps, but it also demonstrates that merely adding progression information is not evidence of a new mechanism. Existing temporal, stage-aware and SSL papers are close prior art. **Current status: not authorized.**

### C. LABEL_EFFICIENT_DEGRADATION_REPRESENTATION

Weak-label SSL exists in Applied Energy 2024 and degradation-aligned SSL is now explicit in arXiv:2608.16612. Direct replication or a different backbone/loss would fail novelty review. **Current status: rejected as a current innovation.**

### D. SMALL-SOURCE DOMAIN GENERALIZATION

DG papers normally form or require multiple source domains. The project has only B0005/B0006 sources, which is a potentially interesting constraint, but B0007/B0018 are already development targets and cannot independently validate DG. **Current status: not feasible in the present repository.**
