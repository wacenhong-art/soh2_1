# Supervised Bottleneck Report

PRIMARY_BOTTLENECK = BOTTLENECK_INCONCLUSIVE
SECONDARY_BOTTLENECK = NONE
NEXT_STAGE = STOP_AND_REASSESS

## Evidence boundary
This is one frozen NASA development diagnostic, not an innovation claim. Test data were not loaded and no diagnostic result was used to select or improve a model.

## Frozen evidence values

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

## Stop
This diagnostic is complete. The indicated next stage is a gate, not authorization to run another experiment.

## Why this is inconclusive

The four alternatives do not yield one dominant frozen pattern. B0007 has two
positive and two negative early-prefix rolling R² values; adding labels within
the permitted 10/15/20% budget does not improve RMSE monotonically; and its
validation-internal forward splits remain negative for both fixed model types.
At the same time, two HF relationships and Ridge coefficient signs drift across
the prefix/validation boundary, and validation can be fit in-sample. This is
evidence of instability, not proof of one exclusive mechanism. The required
action is therefore `STOP_AND_REASSESS`.
