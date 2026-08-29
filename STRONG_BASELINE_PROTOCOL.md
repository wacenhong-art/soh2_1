# Strong Baseline Protocol v1 — F1 Capacity & Contribution Isolation

This protocol uses the seven frozen F1 raw discharge descriptors only. It is
limited to end-of-cycle estimation after the same discharge completes.

## Experiment A: A0 model capacity

Run M0–M3 and their three fixed configurations on A0. Select configurations and
the single Experiment-B family solely by the Decision Record's 60/40 chronological
inner-prefix rule. Then refit on the complete labelled prefix and report outer
validation RMSE, MAE, MAPE, R², prediction mean/std, bias, worst absolute error,
catastrophic count and `TestLoaded`.

## Experiment B: A0–A3 contribution

For the selected family only, retain each target's A0-selected configuration and
all hyperparameters unchanged while evaluating A0, A1, A2 and A3. Report ΔRMSE
and ΔR² relative to A0. A1 removes duration; A2 removes energy; A3 removes both.

## Explicit prohibitions

No feature, voltage window, temporal context, model family, seed, outer-validation
model choice, test read, transfer, SSL/DG, source selection, CALCE, Transformer,
GAN or follow-up ablation is permitted.
