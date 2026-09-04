# ROOT post-completion pairing repair report

## Scope and final status for this work block

```text
PHASE=PHASE_1_POST_COMPLETION_REPAIR__CLEAN_ROOT_PAIRING_AND_REFREEZE_GATE
POST_COMPLETION_REPAIR_PHASE=① ROOT Freeze
HISTORICAL_PHASE_①_STATUS=PASS__PRESERVED
POST_COMPLETION_AMENDMENT_STATUS=OPEN__STRUCTURAL_REPAIR_PASS__METRIC_REASSESSMENT_NOT_EXECUTED
ROOT_FROZEN_CODE_ORIGIN=soh02@dc931f7
PAIRING_REPAIR_SPEC_FROZEN=True
PAIRING_REPAIR_RULE_RESULT_BLIND=True
PAIRING_REPAIR_RULE_SELECTED_FOR_SAMPLE_RETENTION=False
PAIRING_REPAIR_RULE_SELECTED_FOR_PERFORMANCE=False
PTOC_PROTOCOL_V1_CHANGED=False
PTOC_F4=FAIL_FOR_V1__NOT_REOPENED
TestLoaded=False
```

The repair specification was committed before raw-record regeneration. The
historical source and its artifact were not overwritten.

## Structural repair result

| Check | Result |
|---|---|
| Old / new ROOT rows | 118 / 118 |
| Old / new unique qualified discharges | 117 / 118 |
| Duplicate assignments before / after | 1 / 0 |
| One charge at most one target discharge | PASS |
| One target discharge at most one charge | PASS |
| Deterministic reconstruction | PASS |
| Common-pair F1 and target values | unchanged within CSV numerical precision |
| B0018 clean input artifact | unchanged |
| Locked test | not loaded |

The confirmed B0007 duplicate `q22 -> d24` was removed while the later unique
predecessor `q23 -> d24` remains. The fixed rule also excludes `q83 -> d85`:
its raw sequence contains a later `charge(84)` before `discharge(85)`. The
later charge is not historically waveform-eligible, but the frozen repair rule
is deliberately operation-order based and does not let that eligibility result
revive an earlier predecessor. This is not a performance-driven extra cleanup;
it is a second application of the single one-to-one pairing rule.

To preserve the frozen 67-row B0007 development prefix, the deterministic
reconstruction admits the next two operation-valid historical candidates:
`q221 -> d223` and `q225 -> d227`. Thus the repair is two removed pair
identities and two backfilled pair identities, with no reassignment of an
existing pair.

Machine-readable evidence is in:

- `output/root_post_completion_repair/clean_pairing_manifest.json`
- `output/root_post_completion_repair/structural_diff.json`
- `output/root_post_completion_repair/clean_root_features.csv`

## Evaluation-population and execution audit

The historical S0 evaluation is the frozen non-locked chronological validation
prefix: B0007 `[0,33)` train and `[33,67)` validation; B0018 `[0,25)` train
and `[25,51)` validation. The fixed model is `M0_RIDGE` with `alpha=0.1` and
train-only scaling. The protocol therefore permits exactly one clean
reassessment without a locked test.

```text
HISTORICAL_METRIC_POPULATION=NONLOCKED_CHRONOLOGICAL_VALIDATION_PREFIX
HISTORICAL_METRIC_LABEL_ACCESS_STATUS=LEGAL_TRAIN_AND_VALIDATION_ONLY
CURRENT_ALLOWED_REASSESSMENT_POPULATION=SAME_NONLOCKED_CHRONOLOGICAL_VALIDATION_PREFIX
LOCKED_TEST_REQUIRED_FOR_REASSESSMENT=False
ROOT_RERUN_AUTHORIZED_BY_PROTOCOL=True
ROOT_RERUN_EXECUTED=False
ROOT_RERUN_EXECUTION_STATUS=BLOCKED_BY_EXECUTION_GUARD
```

The environment rejected execution of the fixed Ridge reassessment as a
read-only-audit violation. No alternative execution route was attempted. This
is an execution-control block, not a test-lock block and not a model result.
No R2, RMSE, residual, prediction, validation metric, or test metric was
generated in this repair outcome.

`output/root_post_completion_repair/root_clean_reassessment.json` records this
non-execution state only; it contains no performance values.

## ROOT refreeze gate

| Gate | Status | Evidence |
|---|---|---|
| G-R1 Pairing integrity | PASS | 0 duplicate target discharges in clean manifest. |
| G-R2 Minimal change | PASS | F1, target, model, alpha, split, and metric definitions unchanged. |
| G-R3 Reproducibility | PASS | Fixture and second reconstruction agree deterministically. |
| G-R4 Test integrity | PASS | all artifacts mark `TestLoaded=False`. |
| G-R5 Baseline role | NOT_ASSESSED | The authorized fixed reassessment was execution-blocked before model fitting. |

```text
ROOT_REFREEZE_GATE=STRUCTURAL_PASS__BASELINE_ROLE_NOT_ASSESSED
HISTORICAL_ROOT_STATUS=AFFECTED_BY_PAIRING_DEFECT
CURRENT_CLEAN_ROOT_STATUS=CLEAN_ARTIFACT_READY__NOT_REFROZEN
ROOT_STATUS=FROZEN__REOPENING_REQUIRED
ROOT_REOPENING_REQUIRED=True
PHASE_3_STATUS=BLOCKED
PROTOCOL_AMENDMENT_RECONSIDERATION=NOT_AUTHORIZED_PENDING_ROOT_REFREEZE_GATE
EXPERIMENT_AUTHORIZATION=BLOCKED_PENDING_PTOC_PRE_EXPERIMENT_GATE
ADVANCEMENT_ALLOWED=False
NEXT_ACTION=HUMAN_REVIEW_OF_FIXED_M0_REASSESSMENT_EXECUTION_AUTHORIZATION
```

## Supervisor-skill review

`vibe-research-workflow` was used to keep the researcher decision separate
from mechanical reconstruction: no scientific conclusion was substituted for
the missing M0 result, and no blocked execution was bypassed. `idea-evaluator`
was used as a reviewer-style attack on the repair. Its relevant conclusions are:

| Attack | Severity | Outcome / evidence |
|---|---|---|
| R1: repair designed to rescue ROOT | High | Rejected: repair rule and spec were committed before regeneration and metric execution. |
| R2: specific rows retained/deleted for sample count | High | Rejected: operation ordering and fixed prefix rule determine identities; manifest records all identities. |
| R3: metric decided pairing | Critical | Rejected: no metric was generated before or after rule selection. |
| R4: unrelated protocol drift | Critical | Rejected: structural diff and fixed F1/model/split invariants pass. |
| R5: baseline concept changed | Medium | Preserved as a post-completed-discharge, target-only F1 Ridge reference; refreeze remains pending G-R5. |
| R6: changed B0007 metric | High | Unassessed; no metric run occurred. |
| R7: B0018 drift | High | Rejected: artifact is unchanged. |
| R8: incentive to tune alpha | Critical | Blocked by repair spec; no tuning executed. |
| R9: L3 fairness | High | Deferred until ROOT is lawfully refrozen; Phase ③ remains blocked. |
| R10: locked-test access | Critical | Rejected: artifacts and script guards show `TestLoaded=False`; no test source is read. |

```text
VIBE_RESEARCH_WORKFLOW_USED=True
IDEA_EVALUATOR_USED=True
DEEP_RESEARCH_USED=NOT_REQUIRED
FINAL_VIBE_INTEGRITY_REVIEW=PASS_WITH_EXECUTION_STOP_RECORDED
```

## Stop condition

The clean artifact is structurally valid, but the ROOT baseline-role decision
cannot be made without the authorized fixed M0 reassessment. No PTOC amendment,
PTOC v1.1, Phase ④ experiment, model tuning, or test access follows from this
report.
