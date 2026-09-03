# Prediction-Time Observability Contract — Protocol v1

```text
VERSION=1.0.0
STATUS=FROZEN_NONEXECUTABLE_PENDING_PHASE_③_RESOLUTION
EXECUTION_AUTHORIZATION=BLOCKED
ROOT_STATUS=FROZEN
TestLoaded=False
```

This freezes technical rules proposed in Phase ③. It does not authorize any
implementation or performance experiment. No rule may be changed after an
L1/L2/L3 result; an earlier change needs human approval and
`MASTER_PLAN_CHANGE_REQUIRED=True`.

## Formal contract

`C = {prediction_time, observable_signal_set, current_cycle_completion,
capacity_adjacent_access, history_access, future_information_access,
target_definition, deployment_eligibility}`.

Every field is necessary: timing/signals define knowledge; completion and
capacity-adjacent access constrain interpretation; history/future access
control causality; target definition preserves task identity; deployment
eligibility limits the claim.

## Target and pair rule

For an eligible pair `(q(c), d(c))`, use
`Y_c = 100 × Capacity(d(c)) / Q_nom`; `Q_nom` is fixed before extraction. The
reference-label timestamp is `discharge_end(d(c))`. The strict v1 pair rule is:
qualifying charge immediately followed by qualifying discharge; charge has
`V>=4.2` then later `abs(I)<=0.02`; discharge has first `V<=4.0`, then later
`V<=3.6`, and finite aligned V/I/T/time. No imputation or backfilling.

## Contracts

| Level | Prediction timestamp | Allowed information | Prohibited information | Deployment reading |
|---|---|---|---|---|
| L1 | Charge CV cutoff before paired discharge | Causal history and completed current charge | Any current discharge sample/feature | Post-charge, pre-discharge forecast |
| L2 | First predeclared `V<=3.6` after `V<=4.0` | L1 plus causal discharge prefix | Tail/end, full duration/energy, later cycles | During-discharge update/nowcast |
| L3 | Paired discharge completion | Frozen ROOT F1 post-discharge information | Future cycles, centered/retrospective processing | Post-completed-discharge reference |

L1/L2 use a future-acquired label only as held-out supervision. The label is
not allowed in inputs, preprocessing statistics, feature selection or model
selection. L3 duration/delivered energy must be marked capacity-adjacent.

## Comparability and control

1. Direct metric ranking requires identical target, split, eligible-cycle
   population and contract.
2. L1/L2/L3 may appear on a matched-cycle plot; their R²/RMSE is a
   contract-stratified description, not a direct unconditional leaderboard.
3. Any earlier contract containing later-level information is invalid.
4. Freeze `P_b = L1_valid ∩ L2_valid ∩ L3_valid` before label/performance
   loading; every ineligible cycle is excluded from every level.
5. Primary control is deterministic target-only `Ridge(alpha=0.1)` at every
   contract, with causal contract-specific features, train-only preprocessing
   and no retuning. ROOT stays frozen as L3 reference. A matched-population
   refit is `L3_RIDGE_SAME_POPULATION_CONTROL`, not ROOT reproduction.
6. Train-prefix mean is the required simple baseline. Persistence is reportable
   only if its historical capacity input is legal at the prediction timestamp.

## Falsification matrix

| ID | Frozen failure condition | Current status |
|---|---|---|
| F1 | Directly equivalent executable benchmark is verified. | `UNRESOLVED` |
| F2 | PTOC has no compliance consequence beyond a checklist. | `PASS_FOR_PROTOCOL` |
| F3 | Earlier-time target semantics cannot separate label from future feature. | `PASS_WITH_CONDITIONS` |
| F4 | Common matched population cannot form under this pair rule. | `FAIL_FOR_B0007` |
| F5 | Levels require artificial deletion/missingness/synthetic truncation. | `PASS_FOR_PROTOCOL` |
| F6 | Results only say more information gives lower error. | `FROZEN_EMPIRICAL_KILL_CONDITION` |
| F7 | Capacity-adjacent information cannot be disclosed/isolated. | `PASS_FOR_PROTOCOL` |
| F8 | ROOT is not a meaningful high-observability anchor. | `PASS_FOR_PROTOCOL` |
| F9 | No independent raw-waveform data are manifest-qualified. | `PASS_FOR_SOURCE_ELIGIBILITY` |
| F10 | PTOC adds no BMS interpretation beyond a feature list. | `FROZEN_EMPIRICAL_KILL_CONDITION` |
| F11 | Reference-capacity protocol differs across levels/datasets. | `FROZEN_EXTERNAL_KILL_CONDITION` |

F1 is unresolved and F4 fails. Protocol v1 is therefore non-executable; Phase
④ remains prohibited unless human-approved change control resolves them without
result-driven protocol rescue.
