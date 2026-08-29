# B0007 Generalization Audit

## Boundary
All raw loads use `nrows=ValidationEnd`; every output row is `TestLoaded=False`.

## Independent baseline reproduction

Battery,Model,Alpha,FeatureSet,TrainingSamples,ValidationSamples,PreviousRMSE,PreviousR2,RMSE,MAE,R2,PredictionBias,ResidualStd,PredictionMean,PredictionStd,WorstError,RMSEAbsoluteDifference,R2AbsoluteDifference,ReproducedWithin1e-6,TestLoaded
B0007,F0_RIDGE,10.0,F0_HF_CURRENT,33,34,3.341344483179284,-1.2190094156635718,3.34134441893299,2.986825382008272,-1.219009330330778,2.986825382008272,1.497817299715082,91.99566852345185,0.7738608787578387,5.699333190917969,6.424629406254212e-08,8.533279372002767e-08,True,False
B0018,F0_RIDGE,1.0,F0_HF_CURRENT,25,26,1.1891560155088976,0.5691125679007699,1.189155668360783,0.9731897207406851,0.5691128194770744,0.5174407958984375,1.0706755934150045,83.65413108238808,1.9041834878947121,3.0569839477539062,3.4714811469882534e-07,2.515763044552699e-07,True,False


## Frozen decision
PRIMARY_BOTTLENECK = BOTTLENECK_INCONCLUSIVE
SECONDARY_BOTTLENECK = NONE
NEXT_STAGE = STOP_AND_REASSESS

## Evidence

{
  "B0007RollingPositiveR2Count": 2,
  "B0007BaselineValidationR2": -1.219009330330778,
  "B0007ValidationInternalRidgeR2": -0.6170695233578041,
  "B0007ValidationInternalMLPMeanR2": -1.8806279589988057,
  "B0007ValidationInternalMLPPositiveSeeds": 0,
  "DriftFeatureCountPearsonChangeGE0.5": 2,
  "DriftAnyCoefficientSignFlip": true,
  "LabelBudgetRule": false,
  "MappingRule": false,
  "HFInformationRule": false,
  "ModelFitRule": false
}

## Development-only limitation
The validation-only fits are `DIAGNOSTIC_ONLY` and `NOT_AVAILABLE_FOR_MODEL_SELECTION`. They are not formal predictor results and do not establish cross-battery generalization.

## Frozen interpretation

The independent baseline reproduction passed for both batteries (absolute RMSE/R²
differences below `1e-6`). B0007 is not explained by the frozen label-scarcity
rule: its 10/15/20% diagnostic RMSE sequence is 2.738, 2.992 and 3.341 rather
than a monotonic improvement. Its prefix rolling-origin Ridge results are mixed
(2/4 positive R²), so early-stage forward predictability is already unstable.

There is descriptive mapping drift: B0007 HF2 Pearson changes from 0.653 to
-0.767 and HF3 from -0.378 to 0.919; the corresponding standardized Ridge
coefficients change sign. Prefix Ridge applied to validation has R²=-1.219 and a
positive 2.987-point bias. Yet this is not sufficient to declare a single
early-to-late mapping-shift bottleneck under the frozen rule: validation-half to
validation-half Ridge has R²=-0.617 and every fixed-MLP seed is negative, while
the validation segment's in-split diagnostic Ridge fit has R²=0.892. Thus HF
association exists descriptively but is not temporally stable enough for a single
causal attribution.

B0018 is better on the formal prefix-to-validation control because its cross-segment
R² is 0.569 with only 0.517-point bias, compared with B0007's -1.219 and 2.987.
Its mapping is not fully stationary either; this is why these development results
do not support a generalization claim. No diagnostic result is a model-selection
signal or authorization for a repair experiment.
