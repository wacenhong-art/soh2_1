# PTOC Phase ③ Blocker Resolution 2 — L1 Semantics, Operation Ontology, and ROOT Provenance

```text
TASK=PHASE_3_BLOCKER_RESOLUTION_2__L1_SEMANTICS_EXTERNAL_OPERATION_ONTOLOGY_AND_ROOT_PROVENANCE
PHASE=③ PTOC PRE-EXPERIMENT GATE
MASTER_PLAN_CHECK=True
CURRENT_PHASE_STATUS_BEFORE=BLOCKED
G2_FINAL_STATUS=ACCEPTABLE_PARTIAL_COLLISION
PTOC_F1=PASS_FOR_PREEXPERIMENT_GATE__PARTIAL_COLLISION_ONLY
PTOC_F4=FAIL_FOR_V1__NOT_REOPENED
PROTOCOL_AMENDMENT_GATE=BLOCKED
PTOC_PROTOCOL_V1_1_CREATED=False
EXPERIMENT_AUTHORIZATION=BLOCKED
ROOT_STATUS=FROZEN
LOCKED_TEST_STATUS=NOT_LOADED
PRIMARY_INNOVATION_COUNT=1
PRIMARY_INNOVATION=PTOC
```

## Scope and integrity boundary

This is a read-only Phase ③ audit. It did not train or fit a model, rerun
ROOT, calculate SOH performance, load validation/test labels, access the
locked test, change ROOT, create Protocol v1.1, or enter Phase ④. The
operation audit used only declared record types, ordering, timestamps and
published schema descriptions. The ROOT audit used source code, Git metadata
and artifact provenance only.

The mandatory workflow was applied in this order: `vibe-research-workflow`,
`deep-research`, local technical audit, `idea-evaluator`, then a final
`vibe-research-workflow` integrity review. The human researcher retains the
decision whether a protocol amendment or any future experiment may proceed.

```text
VIBE_RESEARCH_WORKFLOW_USED=True
DEEP_RESEARCH_USED=True
IDEA_EVALUATOR_USED=True
SUPERVISOR_SKILLS_GATE=PASS
FINAL_VIBE_INTEGRITY_REVIEW=PASS
```

## Blocker A — L1 temporal and target semantics

### Finding

The only scientifically coherent candidate is **Semantics A**, with a narrow
meaning: L1 emits at the end of the qualifying charge and predicts the outcome
of a predeclared upcoming reference-discharge test. It is *not* an assertion
that a later EIS/rest sequence has zero physical effect, nor an estimate of an
immutable latent capacity at the instant charging ends.

| Item | Frozen interpretation |
|---|---|
| Prediction time | `charge_completion_end`: the charge CV cutoff of the establishing charge. |
| Label reference time | The scheduled target reference-discharge operation that follows the charge under the frozen operation grammar. |
| Label acquisition time | End of that target discharge, when its capacity is measured. |
| Target | `Y_c = 100 × Capacity(target_discharge_c) / Q_nom`. |
| Allowed L1 inputs | Completed current charge and causal historical information only. |
| Forbidden L1 inputs | Any diagnostic waveform/value, current-discharge prefix/tail/duration/energy, capacity label, later-cycle data, and future-derived preprocessing/selection statistics. |
| Intermediate diagnostics | They are protocol events on the trajectory to the later reference measurement, not L1 observable model inputs. |

This separates three clocks which prior V1 wording did not make explicit:

```text
prediction_time != label_reference_time != label_acquisition_time
```

A later acquired capacity label is ordinary retrospective supervision for a
prospective predictor; it becomes leakage only if information measured after
the prediction time enters the input, feature selection, preprocessing,
eligibility selection, model selection or thresholding path. This follows the
distinction used in BMS accuracy assessment, where a reference SOH is obtained
through capacity/resistance tests rather than necessarily at the estimator's
emission instant (Song & Shin, 2023, DOI: 10.1002/ese3.1581).

### EIS / rest condition

NASA treats `charge`, `discharge`, and `impedance` as distinct top-level
operations, and assigns capacity to the discharge record. It also states that
rest duration contributes to state-of-life variation. Therefore an intervening
impedance record is neither corruption nor evidence of physical
non-interference. The contract must explicitly forecast the **subsequent
scheduled reference-test outcome**, rather than silently equating it with
health at charge completion. Published EIS work also reports rest/SOC
dependence, so a non-interference claim would be unjustified.

Semantics B changes the emission time to after diagnostics and would require a
new observable-signal contract; it is not a V1.1 repair. Semantics C creates
two pre/post-diagnostic contracts and expands the single PTOC question; it is
also out of scope.

```text
L1_PREDICTION_TIME=charge_completion_end
L1_LABEL_REFERENCE_TIME=scheduled_first_qualifying_reference_discharge_after_frozen_allowed_intermediates
L1_LABEL_ACQUISITION_TIME=target_discharge_end
L1_TARGET_DEFINITION=capacity_of_scheduled_upcoming_reference_discharge_normalized_by_predeclared_Q_nom
L1_ALLOWED_INFORMATION_BOUNDARY=completed_charge_plus_causal_history_only
L1_DIAGNOSTIC_OPERATION_POSITION=after_L1_emission_before_target_measurement
L1_DIAGNOSTIC_SIGNAL_ACCESS=PROHIBITED
L1_REFERENCE_CAPACITY_SEMANTICS=prospective_reference_test_outcome__not_instantaneous_charge_end_latent_state
L1_SEMANTIC_STATUS=VALID_WITH_FROZEN_CONDITIONS
```

The required future condition is exact: a future protocol may allow an
intermediate operation only if it has a predeclared canonical class and the
target is named as the following reference-test outcome. It must never use an
intermediate diagnostic value as an L1 feature.

## Blocker B — canonical operation ontology and external portability

### Canonical ontology

The ontology is intentionally small and is defined from operation semantics,
not from capacity/SOH values or performance results.

| Canonical class | Meaning | Candidate-pair role | Unknown policy |
|---|---|---|---|
| `STATE_ESTABLISHING_CHARGE` | Declared/net-energy charge event establishing the pre-discharge state. | Starts a candidate. | Exclude if mapping is ambiguous. |
| `TARGET_REFERENCE_DISCHARGE` | Predeclared capacity-measuring discharge with valid waveform/event requirements. | Ends a candidate. | Never infer from a label value. |
| `NONREFERENCE_DISCHARGE` | Driving/load/other discharge not declared as the target reference test. | Breaks and excludes. | Exclude. |
| `REST` | Declared or unambiguously zero-current pause. | Permitted only under a frozen adapter. | Exclude. |
| `DIAGNOSTIC_NON_ENERGY_THROUGHPUT` | Declared EIS/impedance diagnostic event. | Potential permitted intermediate; never L1 input. | Exclude. |
| `DIAGNOSTIC_ENERGY_THROUGHPUT` | Pulse, HPPC, qOCV or other diagnostic that cycles energy. | Breaks and excludes. | Exclude. |
| `UNKNOWN_OR_STATE_ALTERING` | Any record not safely mapped above. | Breaks and excludes. | Exclude. |

No status is derived from a capacity/SOH label, and the ontology itself does
not select a model, feature, threshold or result. A later execution adapter
must map raw records to the classes before any label is accessed.

### Dataset mapping audit

| Dataset | Officially documented raw operation schema | Label/model requirement flags | L1 and target determination | Status |
|---|---|---|---|---|
| NASA B000x | Top-level `charge`, `discharge`, `impedance`, with V/I/T/time; discharge owns capacity. | Mapping must ignore capacity. `impedance` is not an L1 feature. | L1 is charge end; target is a qualifying later discharge, subject to the frozen canonical adapter. | `PASS_FOR_SCHEMA_LEVEL_MAPPING` |
| Luh & Blank NMC/C–SiO | Published dataset reports raw `LOG` V/I/T plus scheduler states, EOC records, EIS and pulse artifacts, regular charge/discharge runs, rests, and check-up/reference-capacity measurements. | Adapter must use scheduler state/current/time, not EOC capacity/SOH fields. Pulse is not an allowed intermediate. | In principle yes: a declared charge event, optional mapped rest/EIS, and a scheduler-declared capacity-test discharge can be identified without reading the value. Exact file-level adapter remains to be independently checked before execution. | `CONDITIONAL_PASS_FOR_PRIMARY_EXTERNAL_ADAPTER` |
| RWTH ISEA NMC/graphite | Public repository documents initial/regular characterization (capacity, multi-pulse, qOCV, EIS) and high-resolution cycling ageing V/I/capacity/energy/T. | README alone does not establish individual record ordering or native event IDs; no values may be used to infer class. | Not yet determinable at an executable adapter level. | `BLOCKED_FOR_BACKUP_EXTERNAL_ADAPTER` |

The Luh & Blank primary source is Luh & Blank, *Scientific Data* (2024),
DOI: [10.1038/s41597-024-03831-x](https://doi.org/10.1038/s41597-024-03831-x).
It describes continuous charge/discharge operation, scheduler states, raw
V/I/T logs, EIS/pulse artifacts, and check-up/reference-capacity measurements.
The RWTH source is the official ISEA repository and dataset DOI
[10.18154/RWTH-2021-04545](https://doi.org/10.18154/RWTH-2021-04545); it is
source-eligible but its published README does not yet establish a complete
record-level operation grammar.

```text
PRIMARY_EXTERNAL_DATASET=Luh_Blank_NMC_C-SiO
BACKUP_EXTERNAL_DATASET=RWTH_ISEA_NMC_GRAPHITE
CANONICAL_OPERATION_ONTOLOGY_STATUS=CONDITIONAL_PASS
EXTERNAL_OPERATION_ONTOLOGY_STATUS=CONDITIONAL_PASS__NASA_AND_LUH_SCHEMA_LEVEL_MAPPING
PAIRING_RULE_CROSS_DATASET_GENERALIZABILITY=CONDITIONAL__NASA_AND_LUH_ADAPTER_POSSIBLE__RWTH_UNRESOLVED
EXTERNAL_SCHEMA_AMENDMENT_NEEDED=False
```

`CONDITIONAL_PASS` is deliberately not an execution authorization: NASA and
one independent dataset have evidence for a label-blind canonical mapping, but
the raw file-level Luh adapter and the RWTH adapter still require a later,
frozen, label-blind conformance inspection.

## Blocker C — ROOT pairing provenance

### Static chain of evidence

`scripts/83_feature_adequacy_reassessment.py` contains the legacy function
`extract_prefix_raw`. For each qualifying charge it selects the first later
record of type `discharge`; it does not stop if another `charge` appears
first. The Phase ③ metadata audit found `charge(22) -> charge(23) ->
discharge(24)` and `charge(83) -> charge(84) -> discharge(85)`. Hence two
preceding charges can map to the same discharge.

`scripts/84_strong_baseline_raw_feature_ablation.py` loads
`output/feature_adequacy_reassessment_v1/frozen_raw_features.csv`, sorts by
`RawChargeCycleIndex`, and uses its F1 features and `SOH` column. The current
`scripts/83`, `scripts/84`, and frozen feature artifact are byte-identical to
the repository initialization commit
`2c28569b76e18511733dd7edef553bece310b163`, whose message records recovery
from `soh02 dc931f7`.

However, the named historical source commit
`dc931f71be6f92f2895a7b1c26aa3158d3359fab` is not present as a local Git
object. This prevents direct source-history equivalence verification. Static
current-chain evidence is strong enough to establish a likely affected ROOT
input artifact, but not to declare a historical ROOT metric invalid.

```text
BUGGY_FUNCTION=scripts/83_feature_adequacy_reassessment.py::extract_prefix_raw
BUG_INTRODUCED_COMMIT=UNRESOLVED__historical_dc931f7_object_unavailable
ROOT_FUNCTION_PATH=scripts/84_strong_baseline_raw_feature_ablation.py::load
ROOT_PAIRING_LOGIC=loads_frozen_raw_features_sorted_by_RawChargeCycleIndex
SHARED_CODE_PATH=scripts/83_feature_adequacy_reassessment.py_to_output/feature_adequacy_reassessment_v1/frozen_raw_features.csv_to_scripts/84_strong_baseline_raw_feature_ablation.py
SHARED_BUGGY_LOGIC=first_later_discharge_without_later_charge_stop
ROOT_TRAINING_ROWS_POTENTIALLY_AFFECTED=two_duplicate_charge_to_discharge_mappings_in_B0007_candidate_prefix
ROOT_PAIRING_BUG_IMPACT=LIKELY_AFFECTS_ROOT_INPUT_ROWS
ROOT_REOPENING_REQUIRED=False
ROOT_PROVENANCE_ACTION=HUMAN_DECISION_REQUIRED__SOURCE_ARTIFACT_RECONCILIATION_BEFORE_ANY_ROOT_DEPENDENT_NEW_EXPERIMENT
```

`ROOT_REOPENING_REQUIRED=False` means this audit does **not** automatically
reopen Phase ①: the exact historical source commit cannot be compared, and no
performance conclusion was recomputed. It does not mean the risk is resolved.
Before any new PTOC experiment relying on ROOT as the empirical anchor, the
researcher must decide whether a label-safe source-artifact reconciliation is
required and, if so, authorize a Phase ① post-completion amendment rather than
silently changing ROOT.

## Protocol and decision consequences

```text
PTOC_F1=PASS_FOR_PREEXPERIMENT_GATE__PARTIAL_COLLISION_ONLY
PTOC_F4=FAIL_FOR_V1__NOT_REOPENED
PTOC_F6=FROZEN_EMPIRICAL_KILL_CONDITION
F6_DEFINITION_UNCHANGED=True
PTOC_PROTOCOL_V1_1_CREATED=False
PROTOCOL_AMENDMENT_AUTHORIZATION=NOT_GRANTED
PHASE_3_STATUS=BLOCKED
EXPERIMENT_AUTHORIZATION=BLOCKED
```

The L1 semantics and one external schema-level adapter remove two conceptual
unknowns, but neither freezes V1.1. The remaining blocker is ROOT provenance:
its input-artifact risk must be governed before ROOT can serve as an
unqualified L3 empirical anchor. No pairing rule was chosen for retention, and
no candidate was selected by SOH/performance results.

### Case classification

This audit is closest to **Case E**: a key provenance item remains unresolved.
It is not Case C or D because L1 is valid with conditions and the ontology has
a primary external conditional mapping. It is not Case A because ROOT impact
is not established as no-impact, and not Case B because reopening is not
automatically authorized on the present evidence.

```text
L1_TARGET_SEMANTICS=VALID_WITH_CONDITIONS
EXTERNAL_ONTOLOGY=CONDITIONAL_PASS
ROOT_PROVENANCE=UNRESOLVED_WITH_LIKELY_INPUT_ARTIFACT_IMPACT
FINAL_CASE=E
NEXT_ACTION=HUMAN_GOVERNANCE_DECISION_ON_ROOT_PROVENANCE_RECONCILIATION_THEN_REASSESS_PROTOCOL_AMENDMENT_GATE
FINAL_VERDICT=PTOC_PHASE3_REMAINS_BLOCKED__NO_PROTOCOL_V1_1_OR_EXPERIMENT_AUTHORIZATION
```

## Idea-evaluator reviewer attack

| Attack | Severity | Validity | Current defense | Evidence still needed | Fatal if unresolved |
|---|---|---|---|---|---|
| R1: post-23/67 relaxation | High | Valid | No amendment is frozen; semantics and ontology, not retention, were audited. | Human approval blind to performance. | Yes |
| R2: 23 rows may be enough | Medium | Valid | Sample retention is not the reason to alter V1. | None; V1 remains a negative control. | No |
| R3: why V1 used adjacency | High | Valid | It was a conservative mechanical guard, now shown not to be a physical invariant. | Frozen canonical adapter. | Yes |
| R4: new rule adds freedom | High | Valid | Finite ontology, first target, one-to-one and unknown-exclude policies are proposed only. | Independent adapter conformance audit. | Yes |
| R5: can it be label-blind | Critical | Valid | All classes are defined by type/state/current/time, never capacity values. | Future extractor inspection. | Yes |
| R6: transfers to external data | High | Valid | NASA + Luh mapping is conditionally supported; RWTH is not yet executable. | Raw file-level external adapter proof. | Yes for general claim |
| R7: dataset-specific cycle semantics | High | Valid | PTOC uses explicit operations, not a universal raw cycle index. | Adapter documentation. | Yes |
| R8: preprocessing dependence | Medium | Valid | Dependency is exposed as a contract conformance requirement. | Cross-data replication. | No |
| R9: partial collision worth repair | Medium | Valid | G2 is acceptable only for planning; novelty remains unestablished. | Full-text/citation chain before claim. | Yes |
| R10: F6 still fatal | Critical | Valid | F6 remains unchanged and is not answered by this audit. | Later pre-registered empirical test. | Yes |
| R11: later label is leakage | High | Valid | It is allowed only as a held-out reference target; no later feature/selection may enter L1. | Future causal-extractor test. | Yes |
| R12: ROOT may be affected | Critical | Valid | Risk is documented without invalidating or silently repairing ROOT. | Historical-source reconciliation/governance. | Yes |

The idea-evaluator position is `ACCEPT_WITH_REVISIONS_FOR_GOVERNANCE_ONLY`:
PTOC is not rejected by these two conceptual audits, but cannot advance with a
likely ROOT input-artifact issue and the still-unfrozen V1.1 amendment.

## Final Vibe Research integrity review

The six behavioural rules were re-applied. The researcher owns the scientific
choice; Codex performed source, schema and Git evidence organization only. No
citation is presented as a verified conclusion beyond accessed source scope;
no paper/manuscript claims, performance results or artificial failure were
created. No test/validation label was loaded, no protocol was silently
changed, no second innovation was added, and no result-driven selection was
performed.

```text
FINAL_VIBE_INTEGRITY_REVIEW=PASS
LEAKAGE_FOUND=False
OUTER_VALIDATION_LOADED=False
TestLoaded=False
MODEL_OR_PROTOCOL_CHANGED=False
```

## Master Plan alignment

```text
MASTER_PLAN_READ=True
CURRENT_PHASE=③ PTOC PRE-EXPERIMENT GATE
CURRENT_PHASE_SYMBOL=③
CURRENT_PHASE_STATUS_BEFORE=BLOCKED
THIS_TASK_OBJECTIVE=Resolve_or_classify_L1_semantics_external_operation_ontology_and_ROOT_pairing_provenance_blockers
THIS_TASK_WITHIN_PLAN=True
PREVIOUS_GATE=PTOC_PROTOCOL_V1_1_AMENDMENT_GATE
PREVIOUS_GATE_STATUS=BLOCKED
TASK_GATE_RESULT=BLOCKED__ROOT_PROVENANCE_RECONCILIATION_REQUIRED_BEFORE_ROOT_DEPENDENT_EXPERIMENT
CURRENT_PHASE_STATUS_AFTER=BLOCKED
ADVANCEMENT_ALLOWED=False
NEXT_PHASE=④ PTOC DEVELOPMENT EXPERIMENT
NEXT_ACTION=HUMAN_GOVERNANCE_DECISION_ON_ROOT_PROVENANCE_RECONCILIATION_THEN_REASSESS_PROTOCOL_AMENDMENT_GATE
MASTER_PLAN_UPDATE_REQUIRED=True
MASTER_PLAN_UPDATED=True
POST_COMPLETION_AMENDMENT_CREATED=False
PLAN_CHANGE_ID=PLAN-CHANGE-0004
ROOT_STATUS=FROZEN__PROVENANCE_RISK_RECORDED
LOCKED_TEST_STATUS=NOT_LOADED
PRIMARY_INNOVATION_COUNT=1
PRIMARY_INNOVATION=PTOC
RESEARCH_COMPLETION_STATUS=NOT_COMPLETE
PAPER_READINESS_STATUS=NOT_ASSESSED
MANUSCRIPT_AUTHORIZED=False
```
