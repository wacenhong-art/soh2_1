# S0 Feature Legality Audit

## Finding

```text
LABEL_LEAKAGE_FOUND=False
FUTURE_LEAKAGE_FOUND=False
S0_CAPACITY_ADJACENT_STATUS=LEGAL_CAPACITY_ADJACENT__PAPER_INPUT_MISMATCH
```

| S0 feature | Source and timing | S0 legality | Paper relation |
|---|---|---|---|
| `DISCHARGE_DURATION_S` | current completed discharge time | `LEGAL_CAPACITY_ADJACENT` | `PAPER_INCOMPATIBLE` with stated charging-HF input; no general paper prohibition located. |
| `DISCHARGE_ENERGY_WH` | current completed discharge V/I/time integration | `LEGAL_CAPACITY_ADJACENT` | `PAPER_INCOMPATIBLE` with stated charging-HF input; energy is not a stated paper HF. |
| `DISCHARGE_V4P0_TO_V3P6_S` | current completed-discharge V/time | `LEGAL_CAPACITY_ADJACENT` | `PAPER_INCOMPATIBLE` as input phase/window, not direct leakage. |
| discharge voltage mean/std | current completed discharge | `LEGAL_CAPACITY_ADJACENT` | `PAPER_INCOMPATIBLE` as paper specifies charging HFs. |
| discharge temperature mean/std | current completed discharge | `LEGAL_CAPACITY_ADJACENT` | `PAPER_INCOMPATIBLE` as paper specifies charging HFs. |

`SOH` is read only as `y`; no S0 feature column is Capacity or SOH. Every record is current-cycle and has `TestLoaded=False`. The frozen prefix has no post-validation records, and fitting/scaling occurs on training rows only. High correlation with SOH does not make same-cycle post-discharge duration or energy `DIRECT_LABEL_LEAKAGE`.

The high S0 performance is capacity-adjacent: full discharge duration and delivered energy are close to capacity measurement under a fixed protocol. They cannot support partial-charge or pre-discharge estimation claims.
