# soh2_1 S0 Ridge Reproduction Report

BASELINE_REPRODUCTION_STATUS=PASS
MODEL_OR_PROTOCOL_CHANGED=False
TestLoaded=False

## Historical versus current metrics

Battery,Baseline,FeatureSet,Configuration,TrainingRows,ValidationRows,FeatureCount,TestLoaded,Seed,HistoricalRMSE,CurrentRMSE,AbsoluteDeltaRMSE,HistoricalMAE,CurrentMAE,AbsoluteDeltaMAE,HistoricalR2,CurrentR2,AbsoluteDeltaR2,BaselineReproductionStatus
B0007,S0_RIDGE,A0_FULL_F1,alpha=0.1,33,34,7,False,deterministic,0.4160898414418754,0.4160898414418754,0.0,0.3707963195116966,0.3707963195116966,0.0,0.9655895011584604,0.9655895011584605,1.1102230246251565e-16,PASS
B0018,S0_RIDGE,A0_FULL_F1,alpha=0.1,25,26,7,False,deterministic,0.2036261159594546,0.2036261159594546,0.0,0.1561409772259517,0.15614097722595177,8.326672684688674e-17,0.9873656399745836,0.9873656399745836,0.0,PASS


## Environment

```json
{
  "historical_script": "scripts\\84_strong_baseline_raw_feature_ablation.py",
  "historical_metrics": "output\\strong_baseline_raw_ablation_v1\\strong_baseline_metrics.csv",
  "source_feature_sha256": "1c2a32e2e2e413f5a005795e2a31627bd3b75a2c4509c22160808ec77931f4b5",
  "source_commit": "dc931f71be6f92f2895a7b1c26aa3158d3359fab",
  "python": "3.11.9",
  "numpy": "2.4.2",
  "pandas": "3.0.1",
  "sklearn": "1.8.0"
}
```

This verifies only that the recovered dc931f7 strong supervised S0 Ridge baseline is reproducible. It is not a paper-method reproduction or a paper-task-compatibility claim.