# soh2_1 S0 Ridge Reproduction Protocol

```text
REPOSITORY=soh2_1
RECOVERY_SOURCE=soh02@dc931f7
BASELINE=S0_RIDGE
MODEL_OR_PROTOCOL_CHANGED=False
TestLoaded=False
```

This one-time verification reuses the recovered historical script's `load`, `predict`, and `metrics` functions. It runs only `M0_RIDGE`, `alpha=0.1`, `A0_FULL_F1`, and the fixed chronological prefixes: B0007 [0,33) train/[33,67) validation; B0018 [0,25)/[25,51).

The seven frozen features are `DISCHARGE_DURATION_S`, `DISCHARGE_V4P0_TO_V3P6_S`, voltage mean/std, temperature mean/std, and `DISCHARGE_ENERGY_WH`. Scaling/imputation is fit only on each training prefix. The frozen CSV has exactly 67 B0007 rows and 51 B0018 rows, all `TestLoaded=False`; no raw MAT, test feature, or test label is opened.