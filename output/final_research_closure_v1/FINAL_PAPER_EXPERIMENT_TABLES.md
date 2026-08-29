# Final paper experiment tables — frozen selection from existing results

No table below requires new training. Main-text tables are deliberately compact; all remaining rows remain available in the appendix/repository and must not be discarded.

| Table | Main-text content | Required existing evidence | Key message | Placement |
|---|---|---|---|---|
| A | Mean, persistence, STL/additive and paper baseline | Phase 1 baseline metrics; Phase 4A/5 reconstruction/persistence rows | The paper system must be compared with fair simple references. | Main text §4-5 |
| B | Paper fusion versus bounded residual fusion | Phase 1 `FINAL_JUDGMENT`, Phase 2 | Catastrophic count 25 -> 0, but accuracy gate remains unmet. | Main text §5 |
| C | Oracle STL versus predicted component reconstruction, with per-component attribution | Phase 4A | Failure exists before fusion; trend is important but not unique. | Main text §5 |
| D | REAL_ONLY versus REAL+GAN reconstruction/component summary | Phase 4B | GAN is not a uniform cause or remedy. | Appendix; brief text reference |
| E | Sequence/capacity summary plus component complexity and causal-STL null result | Phases 2, 3A/3B, 5, 7 | Intuitive fusion/complexity/STL fixes are not primary. | Main text §5 compact summary; detailed Appendix |
| F | Target-only, source-only zero-shot, source+target calibrated transfer | Phase 8 | Transfer is target dependent; calibration is labelled truthfully. | Main text §6 |
| G | B0005-only, B0006-only and all-source outcomes | Phase 9 | B0006 creates source-specific negative-transfer risk. | Main text §6 |
| H | Unsupervised source selection and prefix-supervised screening | Final Method Validation; Prefix-supervised Validation | Covariate distance is rejected; prefix screen is only battery-specific/partial. | Main text §6 |

## Appendix material

- Full five-seed run-level fusion metrics, weight entropy and training logs.
- All component-by-model rows from Phase 5.
- HF distribution and relationship-shift diagnostics from Phase 6.
- Full causal representation stability rows from Phase 7.
- All source/target transfer rows, local-neighbor diagnostics, coefficient diagnostics and source-selection sanity checks.
- Protocol manifests, Git commits and `TestLoaded=false` verification rows.

## Not necessary in the thesis main text

- Repeated grid details after the negative sequence/capacity decision is established.
- Any attempt to rank an unvalidated source-selection score as a winner.
- Locked-test metrics: no frozen qualifying method exists, so the locked test remains unopened.
