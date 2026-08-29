# Final Method Validation — Compatibility-Aware Source Selection

## Final judgment

`COMPATIBILITY_AWARE_SELECTION_NOT_SUPPORTED`

Frozen covariate-only selection did not avoid negative transfer or match all-source robustly.

## Protocol integrity

Frozen protocol SHA256: `9f955e5dbdcc3690967e1a44d50903f7f4e2c6a769dab0abc7a12b3eeea99195`.
The protocol was committed before this run (`cd42d3b`). Scores use only source HF1/HF2/HF3 and target first-20% HF1/HF2/HF3. Target CSVs were read with `nrows=ValidationEnd`; every result row has `TestLoaded=false`.
Selection did not use target SOH, validation/test SOH, historical Phase 8/9 metrics or manual source assignment.

## DEVELOPMENT EVIDENCE versus METHOD VALIDATION EVIDENCE

Phase 8/9 B0005/B0006 transfer outcomes are DEVELOPMENT EVIDENCE only: they motivated the covariate-only score family but were not used by the selection algorithm. The M0-M4 validation rows below are METHOD VALIDATION EVIDENCE under the frozen score. Because B0007/B0018 previously appeared in development diagnostics, this is a transparent validation on the same target set, not independent confirmation; an unseen target cohort is still required for a strong generalization claim.

## Compatibility scores and algorithmic selection

Battery,Score_B0005,Score_B0006,SelectedSource,SelectedScore,CandidateOrderReversed,SelectedWithReversedOrder,SelectedWithAliasedNames,OrderInvariant,SourceNameInvariant,ScoreInvariant,SanityCheckPassed,SelectionUsesTargetSOH,SelectionUsesValidationSOH,SelectionUsesTestSOH,TestLoaded
B0007,0.2184637486934662,0.13672466576099396,B0006,0.13672466576099396,"B0006,B0005",B0006,B0006,True,True,True,True,False,False,False,False
B0018,0.34287604689598083,0.21059559285640717,B0006,0.21059559285640717,"B0006,B0005",B0006,B0006,True,True,True,True,False,False,False,False


## M0-M4 validation metrics

Battery,Model,Track,SelectedSource,CompatibilityScore_B0005,CompatibilityScore_B0006,SelectedCompatibilityScore,TargetTrainEnd,TargetFitEnd,ValidationEnd,ValidationRows,TestLoaded,TrainingSamples,SourceTrainingSamples,TargetTrainingSamples,UsesTargetSOHLabelsForTraining,ScalerFitScope,ParameterCount,RidgeAlpha,ModelId,RMSE,MAE,R2,PredictionStd
B0007,M0_TARGET_ONLY,TARGET_ONLY,B0006,0.2184637486934662,0.13672466576099396,0.13672466576099396,33,26,67,41,False,16,0,16,True,TARGET_FIT_PREFIX_ONLY,31,1.0,M0_TARGET_ONLY,5.458054901864544,4.26894474029541,-3.5851426124572754,1.1392457485198975
B0007,M1_ALL_SOURCE_ZERO_SHOT,ALL_SOURCE_ZERO_SHOT,B0006,0.2184637486934662,0.13672466576099396,0.13672466576099396,33,26,67,41,False,274,274,0,False,B0005+B0006_SOURCE_ONLY,31,1.0,M1_ALL_SOURCE_ZERO_SHOT,1.6344938975278887,1.431807518005371,0.5888088941574097,1.9566267728805542
B0007,M2_SELECTED_SOURCE_ZERO_SHOT,SELECTED_SOURCE_ZERO_SHOT,B0006,0.2184637486934662,0.13672466576099396,0.13672466576099396,33,26,67,41,False,116,116,0,False,B0006_SOURCE_ONLY,31,1.0,M2_SELECTED_SOURCE_ZERO_SHOT,3.904224328287351,3.738307237625122,-1.3461003303527832,1.6065882444381714
B0007,M3_ALL_SOURCE_CALIBRATED,ALL_SOURCE_CALIBRATED,B0006,0.2184637486934662,0.13672466576099396,0.13672466576099396,33,26,67,41,False,290,274,16,True,B0005+B0006+TARGET_FIT_PREFIX,31,1.0,M3_ALL_SOURCE_CALIBRATED,1.0000526891179098,0.7263187170028687,0.8460701704025269,1.9464725255966187
B0007,M4_SELECTED_SOURCE_CALIBRATED,SELECTED_SOURCE_CALIBRATED,B0006,0.2184637486934662,0.13672466576099396,0.13672466576099396,33,26,67,41,False,132,116,16,True,B0006+TARGET_FIT_PREFIX,31,1.0,M4_SELECTED_SOURCE_CALIBRATED,2.683829884364053,2.4910037517547607,-0.10863101482391357,1.6483755111694336
B0018,M0_TARGET_ONLY,TARGET_ONLY,B0006,0.34287604689598083,0.21059559285640717,0.21059559285640717,25,20,51,31,False,10,0,10,True,TARGET_FIT_PREFIX_ONLY,31,1.0,M0_TARGET_ONLY,1.5171399754349848,1.0583313703536987,0.43118929862976074,1.7441445589065552
B0018,M1_ALL_SOURCE_ZERO_SHOT,ALL_SOURCE_ZERO_SHOT,B0006,0.34287604689598083,0.21059559285640717,0.21059559285640717,25,20,51,31,False,274,274,0,False,B0005+B0006_SOURCE_ONLY,31,1.0,M1_ALL_SOURCE_ZERO_SHOT,1.6527280247926264,1.339766025543213,0.32497596740722656,1.9146783351898193
B0018,M2_SELECTED_SOURCE_ZERO_SHOT,SELECTED_SOURCE_ZERO_SHOT,B0006,0.34287604689598083,0.21059559285640717,0.21059559285640717,25,20,51,31,False,116,116,0,False,B0006_SOURCE_ONLY,31,1.0,M2_SELECTED_SOURCE_ZERO_SHOT,2.972815209849348,2.7866194248199463,-1.1839983463287354,1.7611342668533325
B0018,M3_ALL_SOURCE_CALIBRATED,ALL_SOURCE_CALIBRATED,B0006,0.34287604689598083,0.21059559285640717,0.21059559285640717,25,20,51,31,False,284,274,10,True,B0005+B0006+TARGET_FIT_PREFIX,31,1.0,M3_ALL_SOURCE_CALIBRATED,1.5431543938706016,1.2211800813674927,0.4115152359008789,1.8278807401657104
B0018,M4_SELECTED_SOURCE_CALIBRATED,SELECTED_SOURCE_CALIBRATED,B0006,0.34287604689598083,0.21059559285640717,0.21059559285640717,25,20,51,31,False,126,116,10,True,B0006+TARGET_FIT_PREFIX,31,1.0,M4_SELECTED_SOURCE_CALIBRATED,2.7348546070737063,2.5576465129852295,-0.8483530282974243,1.7147152423858643


## Selected source versus all source

Battery,Scenario,SelectedSource,SelectedRMSE,AllSourceRMSE,TargetOnlyRMSE,SelectedMinusAllRMSE,SelectedVsAllRMSEPercent,SelectedMinusTargetOnlyRMSE,AllSourceNegativeTransferVsTargetOnly,SelectedAvoidsThatNegativeTransfer,TestLoaded
B0007,ZERO_SHOT,B0006,3.904224328287351,1.6344938975278887,5.458054901864544,2.269730430759463,138.86441755410317,-1.5538305735771925,False,False,False
B0007,CALIBRATED,B0006,2.683829884364053,1.0000526891179098,5.458054901864544,1.683777195246143,168.36884831851293,-2.7742250175004908,False,False,False
B0018,ZERO_SHOT,B0006,2.972815209849348,1.6527280247926264,1.5171399754349848,1.3200871850567215,79.87322567621842,1.455675234414363,True,False,False
B0018,CALIBRATED,B0006,2.7348546070737063,1.5431543938706016,1.5171399754349848,1.1917002132031047,77.22495026657926,1.2177146316387215,True,False,False


## RQ answers

- **RQ1:** The scores, selection manifest and order/name sanity checks establish whether a covariate-only algorithm selected the source; they do not depend on target outcomes.
- **RQ2:** Compare `SelectedMinusAllRMSE` by target and track; no post-hoc score is substituted if a row worsens.
- **RQ3:** Directional consistency requires both B0007 and B0018, not only B0007. The final judgment therefore downgrades one-target benefit to partial evidence.
- **RQ4:** Zero-shot and calibrated rows are reported separately; calibration is never called zero-shot.

## Secondary safety guard (independent evidence)

Bounded residual fusion is not combined with source selection. Phase 1 independently observed paper-style fusion catastrophic predictions=25 and bounded residual catastrophic predictions=0. It remains a safety guard, not the primary accuracy method.

## NASA-only limitation and next decision

`LOCKED_TEST_DECISION = DO_NOT_PROCEED_WITH_CURRENT_METHOD`. The frozen score selected B0006 for both targets and the selected-source models are worse than all-source in every reported contrast. A locked test cannot be used to rescue or redesign a rejected score. Any future replacement score would require a fresh, human-approved protocol and an independent development/confirmation split.

This run does not read target test data. The present B0007/B0018 validation is not enough for a cross-dataset claim and does not support this score as an undergraduate thesis's primary algorithmic innovation. It remains a valuable negative validation result: simple covariate nearest-neighbor support is insufficient to screen negative transfer here. A publication claim of general compatibility-aware transfer requires a newly supported, pre-frozen method, unseen NASA targets and CALCE or another independent dataset.
