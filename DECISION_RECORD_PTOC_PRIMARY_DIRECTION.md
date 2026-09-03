# Decision Record — PTOC Primary Direction

```text
DATE=2026-09-03
PHASE=PHASE_A_PTOC_GOVERNANCE_AMENDMENT_AND_DECISION_RECORD
CURRENT_HEAD=e64144f
ROOT_STATUS=FROZEN_S0_RIDGE_ALPHA_0P1
ROOT_ROLE=HIGH_OBSERVABILITY_POST_COMPLETED_DISCHARGE_REFERENCE
PRIMARY_INNOVATION_COUNT=1
PRIMARY_INNOVATION=PREDICTION_TIME_OBSERVABILITY_CONTRACT__PTOC
PTOC_STATUS=ACTIVE_PRIMARY_CANDIDATE
SCIENTIFIC_STATUS=UNRESOLVED
EXPERIMENT_AUTHORIZATION=BLOCKED_PENDING_PRE_EXPERIMENT_GATE
TestLoaded=False
```

## Research reframing and truthfulness boundary

ROOT is a strong target-only post-completed-discharge SOH baseline. It uses
capacity-adjacent duration and delivered-energy information available only at
the end of the paired current discharge. ROOT is not claimed to have failed.

The documented methodology problem is instead this: an estimator's RMSE/MAE/R2
does not by itself specify the physical time at which it can emit an estimate,
which signals it could observe, whether its current cycle was complete, or
whether it used capacity-adjacent information. Directly ranking estimators
with different information contracts can therefore overstate deployment
comparability.

This record does not assert that PTOC is novel or validated. It records a
human-authorized methodology candidate whose scientific premise must survive
the gates below.

## PTOC narrow claim and collision status

PTOC would be an executable, reproducible evaluation protocol binding an SOH
estimate to: prediction time; causal observable signal set; current-cycle
completion; capacity-adjacent access; history requirement; future-information
prohibition; target definition; deployment eligibility; and evaluation-cycle
population.

```text
DIRECT_COLLISION_STATUS=PRINCIPLE_LEVEL_COLLISION
CURRENT_NOVELTY_STATUS=UNRESOLVED
```

Recent reviews already support disclosure/alignment of sensing assumptions,
observability and evaluation. PTOC may proceed only if a secondary literature
verification shows a remaining distinction from a direct executable,
prediction-time-specific, matched-target, matched-population SOH benchmark.

## Current fatal risks

```text
MORE_INFORMATION_TRIVIALITY_RISK=FATAL_UNLESS_FALSIFIED
TARGET_SEMANTICS_STATUS=VALID_WITH_CONDITIONS
MATCHED_CYCLE_FEASIBILITY=UNRESOLVED
CHECKLIST_VS_METHOD_RISK=UNRESOLVED
EXTERNAL_DATA_REQUIREMENT=REQUIRED_FOR_GENERAL_METHODOLOGY_CLAIM
```

- If results only say L1 < L2 < L3 because later waveform information is more
  informative, PTOC is `NOT_SUPPORTED`; no new score, module, feature or
  dataset may be added to rescue it.
- A later capacity reference is a valid supervised label for an earlier-time
  predictor only if no later measurement or proxy enters that predictor's
  feature/selection path and the same target definition is retained at all
  levels.
- A common cycle intersection, native raw events, causal extractors and public
  external event/label pairing remain to be audited before any experiment.

## Governance amendment used

```text
GOVERNANCE_AMENDMENT_USED=METHODOLOGY_BENCHMARK_GATE
G1_GOVERNANCE_STATUS=PASS_FOR_PLANNING_ONLY
```

The new gate does not alter G1 for model/algorithm research. It provides a
separate problem-entry test only because the PTOC object is evaluation validity
and deployment eligibility, not a claimed model-performance repair. G2–G7,
test lock, leakage controls and protocol isolation remain fully binding.

## Current Gate status

| Gate | Status | Reason |
|---|---|---|
| G1 / methodology problem entry | `PASS_FOR_PLANNING_ONLY` | The post-discharge information boundary and its applicability consequence are documented. |
| G2 prior | `PENDING` | Direct-method collision needs secondary verification. |
| G3 leakage | `PASS_FOR_PLANNING_ONLY` | No new data/results loaded; future protocol must preserve causal extraction and test lock. |
| G4 baselines | `PENDING` | Contract-compatible simple baselines and same-model control are not frozen. |
| G5 generalization | `PENDING` | External dataset manifest, pairing and license audit are absent. |
| G6 falsifiability | `PENDING` | Final success/failure/stop criteria must be frozen after the unresolved semantic/novelty checks. |
| G7 complexity | `PASS_FOR_PLANNING_ONLY` | PTOC adds no model/module; its necessity still depends on rejecting a checklist-only outcome. |

## Frozen next phase — not authorized now

```text
NEXT_PHASE=PTOC_PRE_EXPERIMENT_GATE
CURRENT_EXPERIMENT_AUTHORIZATION=BLOCKED_PENDING_PRE_EXPERIMENT_GATE
```

The next phase may only perform:

1. secondary literature verification and direct-collision resolution;
2. checklist-versus-methodology and information-triviality falsification;
3. external dataset manifest, raw-event, pairing and license audit;
4. target-semantics and matched-cycle feasibility audit; and
5. protocol freezing.

It may not train L1/L2/L3, fit Ridge, load locked test, download/process
external batteries, tune any parameter, modify ROOT, or automatically
authorize a performance experiment.

## Decision

```text
PTOC_STATUS=ACTIVE_PRIMARY_CANDIDATE
EXPERIMENT_AUTHORIZATION=BLOCKED_PENDING_PRE_EXPERIMENT_GATE
FINAL_DIRECTION_STATUS=GOVERNANCE_PATH_OPEN__SCIENTIFIC_AUTHORIZATION_PENDING
```

## Phase ③ pre-experiment Gate update — 2026-09-03

```text
PTOC_PRE_EXPERIMENT_GATE=BLOCKED_PENDING_PROTOCOL_AMENDMENT
G2_DIRECT_COLLISION_ACCEPTABLE=ACCEPTABLE_PARTIAL_COLLISION
MATCHED_CYCLE_V1=FAIL__23_OF_67_EXACT_DEVELOPMENT_CANDIDATES_FOR_B0007
MATCHED_CYCLE_WITH_PROPOSED_AMENDMENT=CONDITIONALLY_FEASIBLE__65_OF_67_PENDING_HUMAN_APPROVAL
EXTERNAL_MANIFEST=PASS_FOR_SOURCE_ELIGIBILITY__EXECUTION_CONDITIONAL
CONTROL_AND_FALSIFICATION=FROZEN_NONEXECUTABLE
TestLoaded=False
EXPERIMENT_AUTHORIZATION=BLOCKED
NEXT_STAGE=HUMAN_REVIEW
```

The Phase ③ audit did not run L1/L2/L3 performance experiments and did not
modify ROOT. The v1.1 pairing proposal is design-only and cannot replace v1
without human change control. See `PTOC_PHASE3_BLOCKER_RESOLUTION_1.md`.

## Phase ③ protocol-amendment decision — 2026-09-03

```text
PTOC_PROTOCOL_V1_1_AMENDMENT_GATE=BLOCKED
REASON=L1 post-charge reference-test semantics across an impedance interlude and external operation-ontology mapping are not sufficiently verified to freeze.
PTOC_PROTOCOL_V1_1_CREATED=False
PTOC_F4=FAIL_FOR_V1__NOT_REOPENED
PHASE_3_STATUS=BLOCKED
EXPERIMENT_AUTHORIZATION=BLOCKED
TestLoaded=False
NEXT_STAGE=HUMAN_DECISION_ON_SEMANTICS_AND_EXTERNAL_OPERATION_ADAPTER_AUDIT
```

The duplicate charge-to-discharge historical mappings are a confirmed extractor
defect; whether either affected a particular frozen ROOT artifact is
`UNRESOLVED`. ROOT is not invalidated and no rerun is authorized. See
`PTOC_PHASE3_PROTOCOL_AMENDMENT_DECISION.md`.
