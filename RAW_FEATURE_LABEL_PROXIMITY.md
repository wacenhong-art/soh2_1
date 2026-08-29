# Raw Feature Label-Proximity Audit

All correlations below use only first-20% labelled training prefixes. `label-adjacent != leakage`: F1 is derived only from the current completed discharge waveform; SOH/Capacity labels, future cycles and total life are never features. Inputs are legal for end-of-current-cycle estimation only, not early/future/RUL prediction.

| Feature | Unit | Raw source | Current/history | Pearson / Spearman | Physical relation | Leakage status |
|---|---|---|---|---|---|---|
| `DISCHARGE_DURATION_S` | s | current discharge Time | current completed discharge | B0007: 0.859/0.827; B0018: 0.992/0.992 | direct capacity-adjacent fixed-protocol duration | `LEGAL_POST_DISCHARGE_LABEL_ADJACENT_NOT_LEAKAGE` |
| `DISCHARGE_V4P0_TO_V3P6_S` | s | current discharge Voltage_measured + Time | current completed discharge | B0007: 0.406/0.424; B0018: 0.833/0.733 | indirect voltage-traversal duration | `LEGAL_POST_DISCHARGE_LABEL_ADJACENT_NOT_LEAKAGE` |
| `DISCHARGE_VOLTAGE_MEAN_V` | V | current discharge Voltage_measured | current completed discharge | B0007: -0.759/-0.665; B0018: 0.545/0.462 | indirect discharge-profile descriptor | `LEGAL_POST_DISCHARGE_LABEL_ADJACENT_NOT_LEAKAGE` |
| `DISCHARGE_VOLTAGE_STD_V` | V | current discharge Voltage_measured | current completed discharge | B0007: 0.477/0.408; B0018: -0.028/0.048 | indirect profile-spread descriptor | `LEGAL_POST_DISCHARGE_LABEL_ADJACENT_NOT_LEAKAGE` |
| `DISCHARGE_TEMPERATURE_MEAN_C` | degC | current discharge Temperature_measured | current completed discharge | B0007: 0.635/0.571; B0018: 0.811/0.788 | indirect thermal-state descriptor | `LEGAL_POST_DISCHARGE_LABEL_ADJACENT_NOT_LEAKAGE` |
| `DISCHARGE_TEMPERATURE_STD_C` | degC | current discharge Temperature_measured | current completed discharge | B0007: 0.630/0.492; B0018: -0.630/-0.528 | indirect thermal-variability descriptor | `LEGAL_POST_DISCHARGE_LABEL_ADJACENT_NOT_LEAKAGE` |
| `DISCHARGE_ENERGY_WH` | Wh | current discharge Voltage_measured/Current_measured/Time | current completed discharge | B0007: 0.946/0.930; B0018: 0.998/0.997 | direct capacity-adjacent delivered-energy proxy | `LEGAL_POST_DISCHARGE_LABEL_ADJACENT_NOT_LEAKAGE` |

## Interpretation
Duration and energy are physically close to a capacity measurement under a fixed discharge protocol. This makes them label-adjacent but not true label leakage: neither is calculated from SOH nor uses a future cycle. Their role is therefore explicitly isolated by A1–A3 and must not be represented as an early-prediction or algorithmic-innovation result.