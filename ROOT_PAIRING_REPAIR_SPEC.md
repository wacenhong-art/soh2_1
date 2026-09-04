# ROOT pairing repair specification

## Status and authority

```text
REPAIR_ID=ROOT-001-PAIRING-REPAIR-001
STATUS=FROZEN_BEFORE_REGENERATION
AUTHORIZATION=PHASE_1_POST_COMPLETION_REPAIR__CLEAN_ROOT_PAIRING_AND_REFREEZE_GATE
ROOT_FROZEN_CODE_ORIGIN=soh02@dc931f7
ROOT_EXTRACTION_VERIFIED=True
ROOT_PROVENANCE_EVIDENCE_LEVEL=A
LOCKED_TEST_STATUS=NOT_LOADED
PTOC_PROTOCOL_V1_CHANGED=False
```

This is a Phase 1 post-completion repair. It preserves the historical Phase 1
completion record (`PASS`) and does not authorize PTOC experiments.

## Confirmed defect

The recovered historical ROOT table has 118 rows but only 117 unique qualified
discharge records. The only duplicate is in B0007:

```text
B0007_012: charge raw-record 22 -> discharge raw-record 24
B0007_013: charge raw-record 23 -> discharge raw-record 24
```

The operation sequence is `charge(22) -> charge(23) -> discharge(24)`. The
historical extractor selected the first subsequent discharge independently for
each charge and therefore allowed two charges to claim record 24.

## Fixed repair rule

For each candidate charge, identify its first later discharge record exactly as
the historical extractor did. The charge is eligible only when no later
`charge` record occurs before that discharge. Therefore a discharge can have at
most one eligible charge predecessor, and an eligible charge has at most one
target discharge.

For `charge -> charge -> discharge`, only the later charge immediately before
the discharge is eligible; the earlier charge is excluded with
`INTERVENING_CHARGE_BEFORE_TARGET_DISCHARGE`. This rule is determined solely by
raw operation ordering. It does not inspect SOH values, predictions, validation
metrics, sample retention, or any locked-test field.

Intervening non-charge record types retain the historical ROOT extraction
meaning: they do not create a PTOC event grammar and do not alter
`PTOC_PROTOCOL_V1.md`.

## Frozen invariants

The repair must retain all of the following without substitution:

- ROOT F1 feature definitions and ordered columns;
- SOH target definition;
- `Ridge(alpha=0.1)` model, train-only scaling, chronological split indices,
  validation metrics, and metric code;
- B0007/B0018 candidate limits of 67/51 and validation-only reassessment;
- no model selection, grid search, feature change, task redefinition, or
  hyperparameter change;
- no validation-driven choice between pairing rules and no locked-test access.

The historical extractor and historical frozen artifact are evidence and shall
not be overwritten. A separate clean artifact is required.

## Required structural gates before reassessment

```text
ONE_TO_ONE_CHARGE_TO_DISCHARGE=True
NO_DUPLICATE_TARGET_DISCHARGE=True
DETERMINISTIC_RECONSTRUCTION=True
F1_FEATURE_COLUMNS_IDENTICAL=True
TARGET_DEFINITION_IDENTICAL=True
MODEL_AND_SPLIT_IDENTICAL=True
B0018_INPUT_ARTIFACT_UNCHANGED=True
TEST_LOADED=False
```

A regression fixture containing `charge -> charge -> discharge` must prove
that only the latter charge is paired. A structural manifest must document all
removed and replacement identities; feature values for common pair identities
must be unchanged.

## Permitted single reassessment

Only after every structural gate passes, one fixed M0 reassessment is permitted:
`Ridge(alpha=0.1)` on the unchanged B0007 and B0018 chronological development
partitions. It may use the existing non-locked validation prefixes
(B0007 33--67 and B0018 25--51); it must not load an outer test set.

## Refreeze decision rule

No new performance threshold is introduced. The result will be classified from
the frozen contract and the exact reassessment record:

- `ROOT_V2_CLEAN`: all structural gates pass, the reassessment is legal, and
  the resulting frozen ROOT remains a strong high-observability reference under
  its original interpretation;
- `REPAIR_SUCCESS__ROOT_REFERENCE_REQUIRES_HUMAN_REVIEW`: structure passes but
  the reference qualification cannot be retained without a human scientific
  decision;
- `METRIC_REASSESSMENT_BLOCKED_BY_TEST_LOCK`: legality cannot be shown without
  opening locked test data;
- `REPAIR_NOT_DEFENSIBLE`: any structural, semantic, determinism, or leakage
  invariant fails.

Neither outcome opens Phase 4 automatically. PTOC remains blocked throughout.
