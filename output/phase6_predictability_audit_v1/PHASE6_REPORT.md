# Phase 6 — Component Predictability & Representation Audit

## Final attribution
- HF_COMPONENT_RELATIONSHIP_SHIFT
- STL_PREFIX_INSTABILITY
- STL_DECOMPOSITION_HURTS_PREDICTABILITY
- B0007_SHIFT_MORE_SEVERE_EVIDENCE

## Protocol
REAL_ONLY; B0007/B0018; same first-20% train / next-20% validation boundaries and 10-step HF windows as Phase 5.
Raw data is read with `nrows=ValidationEnd`; TestLoaded=false for every row.
Full-prefix STL exists only as a diagnostic reference. It is never used to train a model.
The direct controls are fixed Ridge(alpha=1.0) and a fixed 12-hidden-unit MLP; they are not a model search.
Cycle uses cycle/train_end, not total-life normalization.

## Evidence boundaries
HF_COMPONENT_RELATIONSHIP_SHIFT is observed relative to the current train-only-STL versus prefix-STL evaluation targets. Because the STL audit independently shows those targets move when validation cycles are appended, this flag does not by itself prove a physical HF mapping change.
STL_DECOMPOSITION_HURTS_PREDICTABILITY means the current paper component pipeline (H0) is worse than the direct HF controls on both batteries. It is not proof that STL alone is causal: the all-Ridge component reconstruction in Phase 5 is nearly equivalent to direct Ridge, so the evidence implicates the combined decomposition-plus-component-model pipeline.

## Distribution shift
Battery,MeanKS,MeanWasserstein,MeanStandardizedWasserstein,MeanValidationOutsideTrain
B0007,0.5617944147355912,93.9092617349972,3.6882406539453636,0.5098039215686274
B0018,0.5728205128205128,204.25715948717928,1.7143780768463017,0.4615384615384615


## Relationship shift
Battery,MaxPearsonChange,MaxSpearmanChange,FlaggedPairs
B0007,1.6502601391854057,1.4793805750991478,7
B0018,1.01956266809218,1.0848989801913715,7


## STL prefix stability
Battery,MaxRelativeRMSE,MeanRelativeRMSE
B0007,1.8914557998398562,1.3720926224609442
B0018,231.49876020621357,77.66383933672346


## Direct SOH control
Battery,Model,FeatureSet,MeanRMSE,RMSEStd,WorstRMSE,MeanMAE,MeanR2,WorstR2,Runs,TestLoaded
B0007,RIDGE,HF_ONLY,5.987713612765575,0.0,5.987713612765575,5.076452591839959,-6.125882887553924,-6.125882887553924,1,False
B0007,RIDGE,HF_PLUS_TRAIN_SCALED_CYCLE,5.9912401677358025,0.0,5.9912401677358025,5.0802686354693245,-6.134279153519245,-6.134279153519245,1,False
B0007,TINY_MLP,HF_ONLY,5.556089035745297,0.6496941409399647,6.731751093760813,4.851641800824334,-5.219466370951794,-8.006846042065606,5,False
B0007,TINY_MLP,HF_PLUS_TRAIN_SCALED_CYCLE,5.564041734027833,0.45316859780666274,6.299829336302131,4.8032558216768155,-5.193965064262839,-6.888132718462691,5,False
B0018,RIDGE,HF_ONLY,1.5637874791969413,0.0,1.5637874791969413,1.0685172447791467,0.2548535859897816,0.2548535859897816,1,False
B0018,RIDGE,HF_PLUS_TRAIN_SCALED_CYCLE,1.566044710758492,0.0,1.566044710758492,1.0659038837139423,0.25270088693696136,0.25270088693696136,1,False
B0018,TINY_MLP,HF_ONLY,5.596998624850267,1.0338850348828001,7.404476374396822,5.290753291203425,-8.87116287773678,-15.706091518102806,5,False
B0018,TINY_MLP,HF_PLUS_TRAIN_SCALED_CYCLE,3.4680846243190673,1.444726924971063,5.460622182345095,3.1407368586613584,-3.3009294923083723,-8.08595142388794,5,False
