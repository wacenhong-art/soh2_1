# Thesis outline

## 1. Introduction

- **Question:** Why can reported complex SOH pipelines appear promising yet be unreliable under an extreme small target prefix?
- **Evidence/tables:** Problem framing; Table A preview; protocol ambiguity boundary.
- **Conclusion:** The thesis asks a robustness and transfer-risk question rather than promising a new high-accuracy algorithm.

## 2. Related Work

- **Question:** What roles do decomposition, fusion, augmentation and cross-battery transfer play in SOH estimation?
- **Evidence/tables:** Paper method description; distinction between zero-shot and calibrated transfer.
- **Conclusion:** Existing claims motivate an auditable reproduction but do not substitute for local validation.

## 3. Reproduction Methodology

- **Question:** What is faithfully specified, reproduction-defined or unverified?
- **Evidence/tables:** `REPRO_AUDIT.md`; protocol table; `PAPER_AMBIGUOUS`; `L_weight=UNVERIFIED_DISABLED`.
- **Conclusion:** The implementation's epistemic boundaries are explicit before results are interpreted.

## 4. Experimental Protocol

- **Question:** How are leakage, seeds, simple baselines, source labels and test locking controlled?
- **Evidence/tables:** Table A; split diagram; five-seed rules; `TestLoaded=false` records.
- **Conclusion:** Results use chronological prefix development/validation; locked test remains unopened.

## 5. Failure Attribution of the G-MTC-Style Pipeline

- **Question:** Does failure arise from fusion, component forecasts, model capacity, GAN, or STL instability?
- **Evidence/tables:** Tables B, C and compact E; Table D reference.
- **Conclusion:** Bounded residuals improve safety, but upstream multi-component forecast failure is decisive; several plausible fixes are negative controls.

## 6. Cross-Battery Transfer Analysis

- **Question:** Does source identity alter transfer, and can simple compatibility screens predict utility?
- **Evidence/tables:** Tables F, G and H; block stability/oracle diagnostic in appendix.
- **Conclusion:** Transfer is target-dependent and B0006 is a negative-transfer risk; neither selection rule is a general method.

## 7. Discussion

- **Question:** What does the combined failure chain imply for small-sample battery SOH research?
- **Evidence/tables:** Final evidence ledger; failure-chain diagram.
- **Conclusion:** Do not use fusion tuning to conceal upstream predictability and source-compatibility uncertainty.

## 8. Limitations

- **Question:** What scope does the evidence not cover?
- **Evidence/tables:** Claim boundaries; NASA-only limitation; two targets; no test/CALCE.
- **Conclusion:** Physical causality, cross-dataset generalization and a universal source-selection algorithm remain unestablished.

## 9. Conclusion

- **Question:** What has been established and what should future work test?
- **Evidence/tables:** Contributions and future-work boundary.
- **Conclusion:** The contribution is a rigorous negative/audit result with an engineering safety observation, not an unsupported accuracy claim.
