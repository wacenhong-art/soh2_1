# ROOT Pairing Provenance Audit — Label-Safe Source-Artifact Resolution

```text
TASK=PHASE_3_ROOT_PROVENANCE_RESOLUTION__LABEL_SAFE_SOURCE_ARTIFACT_AUDIT
PHASE=③ PTOC PRE-EXPERIMENT GATE
ROOT_PROVENANCE_AUDIT_AUTHORIZED=True
ROOT_MODIFIED=False
ROOT_RETRAINED=False
PERFORMANCE_METRIC_CALCULATED=False
OUTER_VALIDATION_LOADED=False
TestLoaded=False
PTOC_PROTOCOL_V1_1_CREATED=False
EXPERIMENT_AUTHORIZATION=BLOCKED
```

## Decision

The frozen ROOT source artifact did use duplicate-discharge input rows. The
finding is based on original, tracked historical artifacts and label-safe row
identity fields only—not on any prediction, label value, or performance
comparison.

```text
ROOT_PAIRING_BUG_IMPACT=CONFIRMED_AFFECTS_ROOT_INPUT_ROWS
ROOT_REOPENING_REQUIRED=True
ROOT_STATUS=FROZEN__REOPENING_REQUIRED
NEXT_ACTION=HUMAN_REVIEW_BEFORE_ROOT_REPAIR
```

This does **not** establish how much any historical metric would change. It
establishes only that two ROOT input rows shared a single source discharge,
which violates the intended one-charge/one-target-discharge provenance.

## Boundary and label-safe method

The audit read exactly these columns from the frozen source artifact:

```text
Battery
TestLoaded
RawChargeCycleIndex
RawDischargeCycleIndex
```

It explicitly did not load `SOH`, any F1 feature value, model parameters,
prediction, residual, metric or test data. `TestLoaded=False` was checked for
all projected rows. The deterministic audit script is
`scripts/101_root_pairing_provenance_audit.py`; its outputs are in
`output/root_pairing_provenance_audit/`.

## Git archaeology and evidence level

The initially unavailable object is available in the known legal old checkout
`C:\Users\ROG\Documents\Python\soh02`:

```text
HISTORICAL_COMMIT=dc931f71be6f92f2895a7b1c26aa3158d3359fab
HISTORICAL_COMMIT_SUBJECT=预注册消融完成 26/08/21/15:32
HISTORICAL_COMMIT_AVAILABLE_IN_CURRENT_SOH2_1=False
HISTORICAL_COMMIT_AVAILABLE_IN_KNOWN_OLD_REPOSITORY=True
OLD_REPOSITORY_BRANCHES_CONTAINING_DC931F7=main,codex/p2-clean-baseline-recovery
OLD_REMOTE_HEADS_OBSERVED=origin/main=60892a3631036ce04bd062a40ba04c2917be06c4
```

The historical commit contains both the extractor, the strong-baseline
consumer, and the frozen feature artifact. The exact feature-artifact blob is
identical between `soh02@dc931f7` and the current `soh2_1` ROOT artifact:

```text
DC931F7_FEATURE_ARTIFACT_BLOB=5026dfb06386c5880f57460c3d3158bf80fd468b
CURRENT_ROOT_FEATURE_ARTIFACT_BLOB=5026dfb06386c5880f57460c3d3158bf80fd468b
FEATURE_ARTIFACT_IDENTICAL_TO_DC931F7=True
EXTRACTOR_BLOB_IDENTICAL_TO_DC931F7=True
ROOT_PROVENANCE_EVIDENCE_LEVEL=PROVENANCE_LEVEL_A
```

`PROVENANCE_LEVEL_A` applies because both the original committed code and its
original committed input artifact are available, even though the commit object
is not in the separate `soh2_1` object database.

## Code-to-artifact chain

```text
ROOT_FROZEN_CODE_ORIGIN=soh02@dc931f7
ROOT_CURRENT_IMPLEMENTATION_PATH=scripts/84_strong_baseline_raw_feature_ablation.py::load
ROOT_ORIGINAL_IMPLEMENTATION_PATH_IF_KNOWN=soh02@dc931f7:scripts/84_strong_baseline_raw_feature_ablation.py::load
EXTRACTION_FROM_DC931F7_VERIFIED=True
CODE_DIFF_RELEVANT_TO_PAIRING=NONE__CURRENT_EXTRACTOR_AND_FROZEN_ARTIFACT_MATCH_DC931F7
```

The historical extractor `extract_prefix_raw` records, for every valid charge,
the first later record whose type is `discharge`; it does not stop at an
intervening later `charge`. Its output stores both `RawChargeCycleIndex` and
`RawDischargeCycleIndex`. The historical strong-baseline implementation loads
that exact artifact and sorts it by `RawChargeCycleIndex` before obtaining
features and target values.

```text
BUG_EXISTS_IN_EXTRACTOR=True
BUGGY_FUNCTION=scripts/83_feature_adequacy_reassessment.py::extract_prefix_raw
BUG_ACTUALLY_EXECUTED_IN_FROZEN_ROOT_ROWS=True
ROOT_ARTIFACT_CONSUMER=scripts/84_strong_baseline_raw_feature_ablation.py::load
```

## Reconstructed historical pairing map

The full machine-readable map is
`output/root_pairing_provenance_audit/root_historical_pairing_map.json`.

| Quantity | Result |
|---|---:|
| `N_ROOT_ROWS` | 118 |
| `N_UNIQUE_DISCHARGE_RECORDS` | 117 |
| `N_DUPLICATED_DISCHARGE_ASSIGNMENTS` | 1 |
| `N_ROWS_INVOLVED_IN_DUPLICATION` | 2 |
| `AFFECTED_BATTERIES` | B0007 |
| `AFFECTED_ROW_IDS` | `B0007_012`, `B0007_013` |
| `AFFECTED_RECORD_IDS` | charge 22 → discharge 24; charge 23 → discharge 24 |

The duplicated group is direct source-artifact evidence:

```text
B0007_012: charge(22) -> charge(23) -> discharge(24)
B0007_013: charge(23) -> discharge(24)
DUPLICATE_DISCHARGE_ID=B0007:24
```

Only the first row is an ambiguous `charge→charge→discharge` pairing. The
second is the immediate charge-to-discharge row for the same discharge. The
result is not an inference from current code: it is contained in the original
historical input artifact whose blob matches `dc931f7`.

## Layered ROOT validity

| Scope | Status | Meaning |
|---|---|---|
| Historical `dc931f7` strong-baseline input artifact | `CONFIRMED_AFFECTED_INPUT_ROWS` | Its committed frozen feature table contains the duplicate assignment. |
| Clean S0 reproduction input artifact | `CONFIRMED_AFFECTED_INPUT_ROWS` | It uses the byte-identical recovered feature artifact. No metric was reassessed. |
| Current ROOT methodological reference | `REOPENING_REQUIRED` | Its L3 empirical anchor cannot remain unqualified until governance decides a repair/re-audit path. |

```text
HISTORICAL_DC931F7_STATUS=CONFIRMED_AFFECTED_INPUT_ROWS
CLEAN_S0_STATUS=CONFIRMED_AFFECTED_INPUT_ROWS__NO_METRIC_REASSESSMENT
CURRENT_ROOT_REFERENCE_STATUS=REOPENING_REQUIRED
```

## Idea-evaluator attack

| Attack | Severity | Validity | Defense | Evidence | Fatal if unresolved |
|---|---|---|---|---|---|
| R1: PTOC triggered suspicion of ROOT | High | Valid | The audit follows a predeclared provenance blocker and ignores outcomes. | Label-safe manifest and script. | Yes |
| R2: artifact may be later-generated | Critical | Valid | The artifact is a tracked blob in `dc931f7`, not merely a current cache. | Matching blob IDs. | Yes |
| R3: current repo lacked `dc931f7` | High | Valid | The known old repository contains the exact commit and its tree. | Commit hash and old-repo refs. | Yes |
| R4: current bug may not be historical | Critical | Valid | Extractor and frozen input-artifact blobs match `dc931f7`. | Git blob equality. | Yes |
| R5: what actually changes | High | Valid | A duplicate source discharge affects the two rows' discharge-derived features and target source identity; magnitude is deliberately unassessed. | Record-ID map only. | No metric claim permitted |
| R6: duplicate must affect scientific role | High | Valid | It proves an input-provenance defect, not a performance conclusion. | Governance recheck is required. | Yes for unqualified anchor |
| R7: distinguish metrics from reference | High | Valid | Historical metrics are not declared false; ROOT reference status must be reopened. | Layered-status table. | Yes |
| R8: evidence threshold raised to protect ROOT | High | Valid | Exact original artifact is decisive; no stricter unattainable proof was demanded. | Level-A evidence. | Yes |
| R9: evidence threshold lowered to reopen ROOT | High | Valid | Reopening follows direct duplicate IDs, not code speculation or performance results. | Pairing map. | Yes |
| R10: independent reproducibility | Medium | Valid | A researcher can inspect the two Git blobs and rerun only the provenance-column script. | Script + JSON manifests. | No |

`idea-evaluator` therefore treats a qualification-free ROOT reference as
unsupported, while rejecting any claim about revised RMSE/R² until a separately
authorized repair phase exists.

## Governance consequence

This is Case B. Phase ① remains historically `PASS`; it is not overwritten or
reinterpreted. A post-completion amendment records the new source-artifact
evidence and requires a separate human decision before any repair, rerun or
new ROOT-dependent PTOC experiment.

```text
MASTER_PLAN_CHANGE_REQUIRED=True
POST_COMPLETION_AMENDMENT_REQUIRED=True
POST_COMPLETION_AMENDMENT_TARGET=① ROOT FREEZE
PLAN_CHANGE_ID=PLAN-CHANGE-0005
POST_COMPLETION_AMENDMENT_CREATED=True

PTOC_F4=FAIL_FOR_V1__NOT_REOPENED
PROTOCOL_AMENDMENT_RECONSIDERATION=BLOCKED_PENDING_ROOT_REPAIR_GOVERNANCE
PHASE_3_STATUS=BLOCKED
EXPERIMENT_AUTHORIZATION=BLOCKED
ADVANCEMENT_ALLOWED=False
NEXT_ACTION=HUMAN_REVIEW_BEFORE_ROOT_REPAIR

RESEARCH_COMPLETION_STATUS=NOT_REACHED
PAPER_READINESS_STATUS=NOT_REACHED
MANUSCRIPT_AUTHORIZED=False
```

## Final Vibe Research integrity review

The audit used AI only for mechanical Git/artifact comparison and report
assembly. It did not invent data, citations, results or a repair plan; it did
not change a research question to protect a desired outcome. Human approval is
required for the next scientific/governance decision.

```text
VIBE_RESEARCH_WORKFLOW_USED=True
IDEA_EVALUATOR_USED=True
DEEP_RESEARCH_USED=NOT_REQUIRED
FINAL_VIBE_INTEGRITY_REVIEW=PASS
```

## Master Plan alignment

```text
MASTER_PLAN_READ=True
CURRENT_PHASE=③ PTOC PRE-EXPERIMENT GATE
CURRENT_PHASE_SYMBOL=③
CURRENT_PHASE_STATUS_BEFORE=BLOCKED
THIS_TASK_OBJECTIVE=Resolve whether the historical frozen ROOT actually used input rows affected by the duplicate-discharge pairing bug, using label-safe provenance evidence only.
THIS_TASK_WITHIN_PLAN=True
PREVIOUS_GATE=ROOT_PROVENANCE_ACTION
PREVIOUS_GATE_STATUS=HUMAN_GOVERNANCE_DECISION_REQUIRED
TASK_GATE_RESULT=CONFIRMED_AFFECTS_ROOT_INPUT_ROWS
CURRENT_PHASE_STATUS_AFTER=BLOCKED
ADVANCEMENT_ALLOWED=False
NEXT_PHASE=④ PTOC DEVELOPMENT EXPERIMENT
NEXT_ACTION=HUMAN_REVIEW_BEFORE_ROOT_REPAIR
MASTER_PLAN_UPDATE_REQUIRED=True
MASTER_PLAN_UPDATED=True
POST_COMPLETION_AMENDMENT_CREATED=True
PLAN_CHANGE_ID=PLAN-CHANGE-0005
ROOT_STATUS=FROZEN__REOPENING_REQUIRED
LOCKED_TEST_STATUS=NOT_LOADED
PRIMARY_INNOVATION_COUNT=1
PRIMARY_INNOVATION=PTOC
RESEARCH_COMPLETION_STATUS=NOT_REACHED
PAPER_READINESS_STATUS=NOT_REACHED
MANUSCRIPT_AUTHORIZED=False
```
