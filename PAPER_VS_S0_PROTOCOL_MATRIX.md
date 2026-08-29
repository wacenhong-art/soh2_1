# Paper versus S0 Protocol Matrix

`MATCH` concerns the broad item; `MISMATCH` may be expected for a baseline and does not automatically imply leakage. Task compatibility and method compatibility are assessed separately.

| Item | Paper | S0 | Status | Consequence |
|---|---|---|---|---|
| Target data family | NASA includes B0007/B0018 in reported evaluations/examples | B0007/B0018 | `COMPATIBLE` | Same dataset family/target identities, but not proof of identical protocol. |
| Source-target transfer | Source batteries train SCF-GAN for limited-data targets | target-only, no source | `MISMATCH` | S0 cannot represent transfer/augmentation evidence. |
| SOH concept | residual capacity relative to nominal | frozen SOH scalar scaled to percent | `REPRO_DEFINED` | S0 code does not reconstruct raw label formula. |
| Target small sample | first 20% stated; synthetic expansion stated | 67 B0007 / 51 B0018 prefix rows, then train/validation split | `PAPER_AMBIGUOUS` | Accessible paper text does not uniquely establish equality to its evaluation split. |
| 60/20/20 claim | not uniquely recoverable from accessible body alongside first-20% statement | no 60/20/20 split | `PAPER_AMBIGUOUS` | No favorable interpretation is selected. |
| Input phase | charging HFs, including partial-charge discussion | complete-discharge V/T/time/duration/energy | `MISMATCH` | Different observation phase and information contract. |
| Full-cycle duration | charging HF durations | complete discharge duration | `MISMATCH` | Both are timing-derived, but not the same signal. |
| Delivered energy | no stated energy HF | full discharge energy | `MISMATCH` | Legal S0 quantity, not paper-stated input. |
| Capacity label as feature | no evidence of label feature | no SOH/Capacity column in F1 | `MATCH` | No direct label input. |
| Future-cycle information | not supported | none; prefix-only rows and chronological holdout | `MATCH` | No future leakage found. |
| Train/validation boundary | validation-based early stopping is stated, but the recovered text does not expose a row-level split/selection protocol | fixed chronological validation prefix; training-only imputation/scaling and frozen outer configuration | `PAPER_AMBIGUOUS` | S0 has no train/validation leakage, but paper-level equivalence cannot be established. |
| Preprocessing | not fully disclosed in accessible text | train-only median/standardization | `PAPER_AMBIGUOUS` | S0 is auditable, paper equivalence is not established. |
| Sliding window | component models use 10 steps | no sequence/window model | `MISMATCH` | S0 is per-cycle static regression. |
| GAN augmentation | SCF-GAN required by method | absent | `MISMATCH` | S0 cannot validate GAN contribution. |
| Component/fusion pipeline | STL + TimesNet/iTransformer + attention Bi-LSTM | Ridge | `MISMATCH` | `MODEL_ARCHITECTURE=MISMATCH` is expected. |
| Evaluation metrics | RMSE/MAE/MAPE/R2 | same metrics | `MATCH` | Metric names are comparable, not protocol equivalence. |

## Compatibility separation

```text
TASK_COMPATIBILITY=PARTIALLY_COMPATIBLE
METHOD_COMPATIBILITY=MISMATCH
```

S0 measures SOH on NASA target-prefix data without label/future leakage, but uses a different completed-discharge information contract and does not reproduce paper augmentation or temporal modeling. The unresolved small-sample split prevents `PAPER_TASK_COMPATIBLE`.

```text
MODEL_ARCHITECTURE=MISMATCH
TRAIN_VAL_LEAKAGE_FOUND=False
```
