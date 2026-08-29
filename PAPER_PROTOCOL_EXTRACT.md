# Paper Protocol Extract for S0 Audit

## Evidence boundary

This extract uses only the locally recovered paper body (`paper_text.txt`), not recollection or later repository experiments. Page anchors refer to that file's markers. Unstated details are marked `PAPER_AMBIGUOUS`.

| Protocol item | Paper evidence | Audit extraction |
|---|---|---|
| NASA data | pp. 3–4 / lines 162–181 | NASA 18650 cells, nominal 2.0 Ah; cycle records include voltage, current, temperature and capacity. B0005/B0006 are named as source examples in the SCF-GAN discussion. |
| SOH | p. 1 / lines 41–44 | SOH is described as residual capacity relative to nominal capacity. |
| Input HFs | p. 3 / lines 151–181 | HF1=CV charging duration, HF2=CC charging duration, HF3=3.8→4.0-V charging rise time. The three HFs are from charging profiles. |
| Operational timing | pp. 3–4 / lines 192–201; p. 10 / lines 1157–1165 | Motivation concerns limited/partial charging windows, e.g. 3.8–4.0 V. |
| Small sample | p. 10 / lines 1157–1170 | Original cycles for each target are stated as the first 20% of total life; SCF-GAN generates five complete synthetic datasets, expanding training samples about fivefold. |
| Source/target logic | p. 9 / lines 492–497 | Source batteries with complete 3.6–4.2-V charge data (examples NASA B0005/B0006) train SCF-GAN; targets are limited-data recipients. |
| Augmentation | pp. 4–9 / lines 212–282, 407–445 | SCF-GAN with conditional information, feature matching and conditional batch normalization is part of the pipeline. |
| Temporal model | pp. 5–9 / lines 289–410, 472–490 | STL; TimesNet for trend/seasonal; iTransformer for residual; attention Bi-LSTM fusion. Component models use 10-step sliding windows. |
| Published split detail | accessible text | The recovered body explicitly gives first-20%-of-life original target samples, but does not uniquely state a chronological 60/20/20 target split or map it to the augmented experiment. `PAPER_AMBIGUOUS`. |
| Duration/energy boundary | accessible text | The paper specifies charging-duration HFs; it does not explicitly permit or prohibit completed-discharge energy input. It does not define a general all-sensor boundary. `PAPER_AMBIGUOUS` for a general prohibition, while its stated input is charging HFs. |

## Interpretation guard

The paper’s method and its broad end-of-cycle SOH task are distinct claims. A baseline can be informative for a related task without being the paper method. No located paper statement supports treating full-discharge delivered energy as a stated paper HF.
