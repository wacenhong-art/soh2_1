# Prefix-supervised source-screening validation

## Final judgment

`PREFIX_SUPERVISED_SOURCE_SCREENING_PARTIALLY_SUPPORTED`

The label-bounded rule has a one-target benefit but is not directionally consistent across both targets.

## Protocol integrity

Frozen protocol SHA256: `01708db0a98290cee19972280aea6b83776a887d73628cfab321df850cd4ea1e`. Protocol commit: `88355aa`.
The score is source-only Ridge error on legal target-prefix SOH. It is a calibrated/few-shot selection score, never zero-shot. It does not use validation/test labels or prior source transfer outcomes. Each target CSV is read only with `nrows=ValidationEnd`; every output row declares `TestLoaded=false`.

## Prefix source scores (formal selection)

Battery,Source,PrefixCompatibilityError,Rank,SelectedSource,SourceTrainingWindows,PrefixScoringWindows,SelectionUsesTargetPrefixSOH,SelectionUsesValidationSOH,SelectionUsesTestSOH,TestLoaded
B0007,B0005,1.9762515701779926,2,B0006,158,23,True,False,False,False
B0007,B0006,1.7829671246059298,1,B0006,116,23,True,False,False,False
B0018,B0005,1.0044997423968216,1,B0005,158,15,True,False,False,False
B0018,B0006,1.7323026906402679,2,B0005,116,15,True,False,False,False


## Prefix block stability (diagnostic only)

Battery,Source,Block,BlockWindows,BlockRMSE,MeanBlockRMSE,WorstBlockRMSE,BlockRMSEStd,FullPrefixCompatibilityError,SelectedSource,DiagnosticOnly,TestLoaded
B0007,B0005,1,8,1.6106771230697632,1.9479506015777588,2.3561301231384277,0.3084323740399547,1.9762515701779926,B0006,True,False
B0007,B0005,2,8,2.3561301231384277,1.9479506015777588,2.3561301231384277,0.3084323740399547,1.9762515701779926,B0006,True,False
B0007,B0005,3,7,1.8770445585250854,1.9479506015777588,2.3561301231384277,0.3084323740399547,1.9762515701779926,B0006,True,False
B0007,B0006,1,8,1.8441675901412964,1.772585431734721,2.0924394130706787,0.294761387269513,1.7829671246059298,B0006,True,False
B0007,B0006,2,8,1.3811492919921875,1.772585431734721,2.0924394130706787,0.294761387269513,1.7829671246059298,B0006,True,False
B0007,B0006,3,7,2.0924394130706787,1.772585431734721,2.0924394130706787,0.294761387269513,1.7829671246059298,B0006,True,False
B0018,B0005,1,5,0.49383997917175293,0.8592396080493927,1.5950695276260376,0.5203143791963464,1.0044997423968216,B0005,True,False
B0018,B0005,2,5,0.4888093173503876,0.8592396080493927,1.5950695276260376,0.5203143791963464,1.0044997423968216,B0005,True,False
B0018,B0005,3,5,1.5950695276260376,0.8592396080493927,1.5950695276260376,0.5203143791963464,1.0044997423968216,B0005,True,False
B0018,B0006,1,5,1.1694358587265015,1.6692830721537273,2.2854912281036377,0.46299733518848657,1.7323026906402679,B0005,True,False
B0018,B0006,2,5,1.5529221296310425,1.6692830721537273,2.2854912281036377,0.46299733518848657,1.7323026906402679,B0005,True,False
B0018,B0006,3,5,2.2854912281036377,1.6692830721537273,2.2854912281036377,0.46299733518848657,1.7323026906402679,B0005,True,False


## C0-C3 calibrated metrics

Battery,SelectedSource,PrefixCompatibilityError_B0005,PrefixCompatibilityError_B0006,SelectedPrefixCompatibilityError,TargetTrainEnd,ValidationEnd,ValidationRows,TestLoaded,Model,SourceSet,TrainingSamples,SourceTrainingSamples,TargetTrainingSamples,UsesTargetSOHLabelsForTraining,FeatureScalerFitScope,RidgeAlpha,ParameterCount,RMSE,MAE,R2,PredictionStd,IsOracleDiagnostic
B0007,B0006,1.9762515701779926,1.7829671246059298,1.7829671246059298,33,67,34,False,C0_TARGET_ONLY,NONE,23,0,23,True,TARGET_PREFIX_ONLY,1.0,31,6.54004948868532,5.6367573738098145,-7.501171112060547,1.2653499841690063,False
B0007,B0006,1.9762515701779926,1.7829671246059298,1.7829671246059298,33,67,34,False,C1_ALL_SOURCE_CALIBRATED,B0005+B0006,297,274,23,True,B0005+B0006+TARGET_PREFIX,1.0,31,0.5888721472181786,0.484594464302063,0.9310778379440308,1.8796128034591675,False
B0007,B0006,1.9762515701779926,1.7829671246059298,1.7829671246059298,33,67,34,False,C2_PREFIX_SELECTED_SOURCE_CALIBRATED,B0006,139,116,23,True,B0006+TARGET_PREFIX,1.0,31,2.653955433423183,2.5341386795043945,-0.399922251701355,1.6051768064498901,False
B0007,B0006,1.9762515701779926,1.7829671246059298,1.7829671246059298,33,67,34,False,C3_ORACLE_SOURCE_DIAGNOSTIC,B0005,181,158,23,True,B0005+TARGET_PREFIX,1.0,31,1.9854789126373178,1.813965916633606,0.2164851427078247,,True
B0018,B0005,1.0044997423968216,1.7323026906402679,1.0044997423968216,25,51,26,False,C0_TARGET_ONLY,NONE,15,0,15,True,TARGET_PREFIX_ONLY,1.0,31,2.8701070530294874,2.554219961166382,-1.510049819946289,1.538945198059082,False
B0018,B0005,1.0044997423968216,1.7323026906402679,1.0044997423968216,25,51,26,False,C1_ALL_SOURCE_CALIBRATED,B0005+B0006,289,274,15,True,B0005+B0006+TARGET_PREFIX,1.0,31,1.5651132474393605,1.2228736877441406,0.25358957052230835,1.6061650514602661,False
B0018,B0005,1.0044997423968216,1.7323026906402679,1.0044997423968216,25,51,26,False,C2_PREFIX_SELECTED_SOURCE_CALIBRATED,B0005,173,158,15,True,B0005+TARGET_PREFIX,1.0,31,1.3767644658268179,0.9821528196334839,0.4224289059638977,1.4123045206069946,False
B0018,B0005,1.0044997423968216,1.7323026906402679,1.0044997423968216,25,51,26,False,C3_ORACLE_SOURCE_DIAGNOSTIC,B0005,173,158,15,True,B0005+TARGET_PREFIX,1.0,31,1.3767644658268179,0.9821528196334839,0.4224289059638977,,True


## Oracle diagnostic gap

Battery,AlgorithmSelectedSource,OracleSource,SelectionMatchesOracle,SelectedValidationRMSE,OracleValidationRMSE,SelectedMinusOracleRMSE,C3DiagnosticOnly,TestLoaded
B0007,B0006,B0005,False,2.653955433423183,1.9854789126373178,0.6684765207858652,True,False
B0018,B0005,B0005,True,1.3767644658268179,1.3767644658268179,0.0,True,False


## RQ answers

- **RQ1:** B0018 prefix screening identifies B0005 and avoids B0006; B0007 selects B0006 although the validation-only oracle is B0005. The score therefore detects negative-source risk only battery-specifically.
- **RQ2:** C2 improves over C1 on B0018 (RMSE 1.377 vs 1.565) but degrades on B0007 (2.654 vs .589); it is not two-target consistent.
- **RQ3:** C2 is better than C0 on both targets, but this is insufficient because the required all-source comparator fails on B0007.
- **RQ4:** Prefix block ranking is unstable for B0007 (B0005 has lower block RMSE in blocks 1 and 3, B0006 only in block 2) and stable for B0018 (B0005 lower in all three blocks). Block results remain diagnostic and did not modify selection.
- **RQ5:** The algorithm matches the individual-source oracle on B0018 (gap 0.000) but misses it on B0007 (gap .668 RMSE).

## Interpretation

C3 is an oracle that selects source after validation RMSE and is never a formal method or winner. It only measures the gap between prefix screening and a forbidden post-hoc choice. The block statistics report robustness of prefix predictive compatibility but never alter selection.
Bounded residual fusion remains an independent secondary safety observation (Phase 1: catastrophic outputs 25 -> 0); it is not combined with prefix-supervised source screening.

## Locked-test and publication decision

`LOCKED_TEST_DECISION = DO_NOT_PROCEED`
A supported NASA-only method would still be few-shot/calibrated transfer, not zero-shot domain adaptation. A general cross-dataset claim would require unseen NASA targets plus CALCE or another independent dataset under the unchanged frozen protocol.
