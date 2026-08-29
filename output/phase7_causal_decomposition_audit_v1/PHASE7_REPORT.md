# Phase 7 — Prefix-Stable / Causal Decomposition Audit

Decision: STL_INSTABILITY_NOT_CAUSALLY_LINKED_TO_FORECAST_FAILURE

## Protocol
D0 is Original STL (reference). D1 EMA alpha=0.2, D2 causal rolling median window=5, and D3 first difference are REPRO_DEFINED fixed representations.
Prefix lengths: 20%, 30%, 40%; the 30% index is inferred as the midpoint of the known 20% and 40% boundaries, without reading test rows.
Every raw CSV read uses nrows=Prefix40 and all result rows set TestLoaded=false.
D3 validation SOH reconstruction uses only SOH at the final training cycle as its anchor.

## Prefix stability
Representation,MaxNormalizedRMSE,MeanNormalizedRMSE,MinCorrelation
D0_ORIGINAL_STL,231.50843914921742,33.3951695025828,-0.3152486768820476
D1_CAUSAL_EMA_A0.2,0.0,0.0,0.9999999999999999
D2_CAUSAL_ROLLING_MEDIAN_W5,0.0,0.0,0.9999999999999999
D3_FIRST_DIFFERENCE,0.0,0.0,1.0


## Predictability
Battery,Representation,RMSE,MAE,R2,PredictionVariance
B0007,D0_ORIGINAL_STL,5.987719905409865,5.076458775833663,-6.1258995494631545,1.2261313199996948
B0007,D1_CAUSAL_EMA_A0.2,5.987719029680936,5.076456756288051,-6.125897465078442,1.2261343002319336
B0007,D2_CAUSAL_ROLLING_MEDIAN_W5,5.987720361018148,5.076458551439706,-6.1259006338889606,1.2261333465576172
B0007,D3_FIRST_DIFFERENCE,27.90123691652662,21.27298793986744,-153.72612759310752,252.39273874246888
B0007,DIRECT_HF_TO_SOH_CONTROL,5.9877214147513085,5.0764598978034465,-6.125903141954802,1.2261329889297485
B0018,D0_ORIGINAL_STL,1.5637906468609095,1.068517134913272,0.25485032580684097,2.4340574741363525
B0018,D1_CAUSAL_EMA_A0.2,1.5637908021688678,1.0685165480367698,0.25485017779766794,2.4340569972991943
B0018,D2_CAUSAL_ROLLING_MEDIAN_W5,1.5637902887695372,1.068518308666277,0.2548506670694509,2.4340574741363525
B0018,D3_FIRST_DIFFERENCE,1.910271563802846,1.6589506348653988,-0.1119276122006394,2.0368557495090696
B0018,DIRECT_HF_TO_SOH_CONTROL,1.5637897977357997,1.0685177217897746,0.25485113502657686,2.4340593814849854


## Evidence boundary
A causal representation is considered predictively improved only with a predeclared >=1% RMSE reduction versus D0 on a battery; differences around 1e-6 are numerical noise.
D1/D2 ridge reconstructions are nearly identical to D0/direct Ridge because each component uses the same linear features and the components sum to SOH. Thus prefix stability is verified, but this fixed linear control does not establish a validation-generalization benefit from the stable representation.
Causal representations being prefix invariant establishes stability by construction and by code verification. The result does not establish a deployable SOH solution or use test data.