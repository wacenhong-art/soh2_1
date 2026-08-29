# Phase 8 — Source Transfer & HF Shift Attribution

Decision: BATTERY_SPECIFIC_DOMAIN_SHIFT_REMAINS
B0007 attribution: NOT_ESTABLISHED

## Protocol
P0 TARGET_ONLY uses the target fit prefix. P1 is SOURCE_TRANSFER/ZERO_SHOT diagnostic and does not train on target SOH labels. P2 is CALIBRATED_TRANSFER and uses source real data plus target fit-prefix labels.
Source B0005/B0006 use full real labelled lifecycle data; target CSVs are read with nrows=ValidationEnd only.
Ridge alpha=1.0 is fixed from Phase 6; no validation tuning or test access.

## Metrics
Battery,Protocol,Track,TrainingSamples,SourceTrainingSamples,TargetTrainingSamples,UsesTargetSOHLabelsForTraining,RMSE,MAE,R2,PredictionStd,TestLoaded
B0007,P0_TARGET_ONLY,TARGET_ONLY,16,0,16,True,5.98771363197792,5.076452732086182,-6.12588357925415,1.1073074340820312,False
B0007,P1_SOURCE_ONLY_ZERO_SHOT,SOURCE_TRANSFER/ZERO_SHOT_DIAGNOSTIC,274,274,0,False,1.3125056766205598,1.1858055591583252,0.657611608505249,1.8669495582580566,False
B0007,P2_SOURCE_PLUS_TARGET_CALIBRATED,CALIBRATED_TRANSFER,290,274,16,True,0.6511046468153823,0.4953393340110779,0.9157406091690063,1.8809821605682373,False
B0018,P0_TARGET_ONLY,TARGET_ONLY,10,0,10,True,1.5637874639644584,1.0685172080993652,0.25485360622406006,1.5601450204849243,False
B0018,P1_SOURCE_ONLY_ZERO_SHOT,SOURCE_TRANSFER/ZERO_SHOT_DIAGNOSTIC,274,274,0,False,1.671190068062669,1.3455041646957397,0.14898371696472168,1.7394018173217773,False
B0018,P2_SOURCE_PLUS_TARGET_CALIBRATED,CALIBRATED_TRANSFER,284,274,10,True,1.5640504392602859,1.228837251663208,0.25460296869277954,1.6406644582748413,False


## HF support coverage
Battery,MeanTargetOnlyCoverage,MeanSourceOnlyCoverage,MeanCoverageGain
B0007,0.4901960784313726,1.0,0.5098039215686274
B0018,0.5384615384615384,1.0,0.4615384615384615


## Evidence boundary
A source coverage gain is univariate feature-wise support evidence, not proof that source and target share the same conditional HF-to-SOH relationship. P1/P2 are diagnostics, not claims of a final deployed model.