# Feature Extraction Protocol v1 — Raw NASA Health Indicators

## Existing HF audit boundary

The existing `HF1/HF2/HF3` features remain F0 without modification. New values
are never renamed HF1/HF2/HF3. Their extractor's centered Hampel smoothing and
bidirectional interpolation are applied over the full battery sequence; F0 and
F2 are therefore `LEGACY_REFERENCE_NOT_STRICTLY_CAUSAL`, not leakage-safe feature
sets. They are reported for audit comparison only; F1 is the only eligible set
for a no-leakage feature-adequacy conclusion.

## Frozen F1 candidates

| feature | unit | raw signals | current-cycle causal rule |
|---|---|---|---|
| `DISCHARGE_DURATION_S` | s | discharge `Time` | last minus first timestamp |
| `DISCHARGE_V4P0_TO_V3P6_S` | s | discharge `Voltage_measured`, `Time` | first downward 4.0-V crossing to first later 3.6-V crossing |
| `DISCHARGE_VOLTAGE_MEAN_V` | V | discharge `Voltage_measured` | current-cycle mean |
| `DISCHARGE_VOLTAGE_STD_V` | V | discharge `Voltage_measured` | current-cycle standard deviation |
| `DISCHARGE_TEMPERATURE_MEAN_C` | °C | discharge `Temperature_measured` | current-cycle mean |
| `DISCHARGE_TEMPERATURE_STD_C` | °C | discharge `Temperature_measured` | current-cycle standard deviation |
| `DISCHARGE_ENERGY_WH` | Wh | discharge Voltage/Current/Time | `∫ V·abs(I) dt / 3600` by trapezoid rule |

No additional voltage window, trend/rolling feature, curve alignment, automatic
feature selection or post-validation pruning is allowed. A feature is missing if
its raw waveform cannot produce a finite value; training-subset median imputation
is the only allowed imputation.

## Cycle mapping and data lock

For each valid charge record, the immediately following discharge record supplies
the current cycle's raw waveform and SOH label. `Capacity` is read only as the
supervised target and never as an input feature. The scanner stops when it has
created the frozen `ValidationEnd` count (B0007=67, B0018=51), and does not
traverse later raw cycles. Loading a MAT container is unavoidable for this format;
`TestLoaded=False` means no test-cycle field, feature, capacity or SOH value is
accessed after this prefix cutoff.

## Formal feature sets and models

`F0 = HF1/HF2/HF3`; `F1 = seven frozen raw descriptors`; `F2 = F0 + F1`.
M0/M1 and all boundaries, seeds, scalers and decision criteria are fixed in
`DECISION_RECORD_FEATURE_ADEQUACY_REASSESSMENT.md`.
