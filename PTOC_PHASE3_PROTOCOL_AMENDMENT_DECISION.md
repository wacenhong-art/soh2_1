# Phase ③ PTOC Protocol-Amendment Decision Gate

```text
TASK=PHASE_3_PROTOCOL_AMENDMENT_DECISION_GATE
DATE=2026-09-03
PHASE=③ PTOC PRE-EXPERIMENT GATE
CURRENT_PHASE_STATUS_BEFORE=BLOCKED
ROOT_STATUS=FROZEN
ROOT_MODIFIED=False
PERFORMANCE_EXPERIMENT_RUN=False
OUTER_VALIDATION_LOADED=False
TestLoaded=False
EXPERIMENT_AUTHORIZATION=BLOCKED
PRIMARY_INNOVATION_COUNT=1
PRIMARY_INNOVATION=PTOC
```

## Gate decision

`PTOC_PROTOCOL_V1.md` remains the immutable non-executable V1 record. This
audit did not train a model, calculate an SOH metric, reopen ROOT, access a
validation/test label, or execute Phase ④.

```text
G2_FINAL_STATUS=ACCEPTABLE_PARTIAL_COLLISION
PTOC_F1=PASS_FOR_PREEXPERIMENT_GATE__PARTIAL_COLLISION_ONLY
PTOC_F4=FAIL_FOR_V1__PENDING_V1_1_HUMAN_DECISION
PROTOCOL_AMENDMENT_GATE=BLOCKED
PTOC_PROTOCOL_V1_1_CREATED=False
PHASE_3_STATUS=BLOCKED
ADVANCEMENT_ALLOWED=False
```

The gate is `BLOCKED`, not `PASS`: a finite, label-free grammar can be
specified, but the L1 timing/target interpretation across an intervening
diagnostic is not verified enough to freeze. The source manifests also do not
yet prove a matching operation ontology for either external dataset. This is
not a rejection of the candidate in principle and is not permission to change
V1.

## Mandatory Supervisor-Skills record

The required sequence was actually applied:

1. `vibe-research-workflow`: classified this as protocol/governance work.
   The researcher retains the decision to pursue PTOC; AI is limited to source
   checking, record inspection and decision recording. A retention- or
   performance-driven rule would require rejection.
2. `deep-research`: checked NASA operation metadata and EIS/RPT sources for
   operation semantics and dataset portability.
3. Codex technical audit: read only historical code, operation order,
   timestamps, raw V/I/T/time metadata and manifests; excluded capacities,
   SOH labels, validation/test labels and prediction code paths.
4. `idea-evaluator`: attacked the candidate as a methodology contribution.
   The decisive objections are L1 semantic drift, ontology portability and a
   sample-retention rescue.
5. `vibe-research-workflow` final review: no invented result/citation,
   second innovation, ROOT modification or Phase ④ work occurred.

```text
VIBE_RESEARCH_WORKFLOW_USED=True
DEEP_RESEARCH_USED=True
IDEA_EVALUATOR_USED=True
SUPERVISOR_SKILLS_GATE=PASS
FINAL_VIBE_INTEGRITY_REVIEW=PASS
```

## Historic provenance correction: `31/67` vs `23/67`

```text
PAIRING_PROVENANCE_STATUS=RESOLVED
OLD_V1_MATCHED_STATEMENT=31/67
CORRECTED_V1_MATCHED_STATEMENT=23/67
```

`31` came from `scripts/99_ptoc_matched_cycle_metadata_audit.py`, which scans
the whole B0007 raw file and counts strict immediate valid pairs (31 pairs
among 170 raw charge records). It is not restricted to ROOT's 67 historical
development candidates. The label-free reconstruction of that same 67-row
candidate sequence in `output/ptoc_phase3_blocker_resolution_1/` contains 23
immediate pairs, 42 impedance-only interludes and two charge-before-discharge
ambiguities. Only `23/67` shares ROOT's denominator; no ROOT performance was
recomputed.

## Historical extractor defect

Static review of `scripts/83_feature_adequacy_reassessment.py` shows that it
selects the first later `discharge` without stopping at a later `charge`. Raw
order/time records show `22 -> 23 -> 24` and `83 -> 84 -> 85`; both preceding
charges can be mapped to the same discharge.

```text
EXTRACTOR_DUPLICATE_PAIRING_BUG=CONFIRMED
BUG_SCOPE=Legacy first-later-discharge extraction permits duplicate charge-to-discharge mappings for charge->charge->discharge.
AFFECTED_ONLY_PTOC_PAIRING_AUDIT=False
AFFECTS_FROZEN_ROOT=UNRESOLVED
ROOT_INVALID=False
```

This is historical ROOT/F1 extraction code, not merely PTOC code. Whether a
particular frozen ROOT artifact was affected would require a prohibited
reconstruction/comparison, hence `UNRESOLVED`, never `ROOT_INVALID`.

## Evidence on operations

NASA defines `charge`, `discharge`, and `impedance` as separate top-level
operations with independent start-time vectors; discharge owns the capacity
field. It also states that rest duration/usage variability matter. This proves
that an impedance row is a native operation rather than corruption, but does
not prove that crossing it preserves a post-charge/pre-discharge contract.
[NASA documentation](https://data.nasa.gov/dataset/li-ion-battery-aging-datasets)

EIS is commonly described as non-destructive/non-invasive, while its response
also depends on rest time and SOC. That supports treating it as a distinct
diagnostic operation, not missingness, but does not prove no short-horizon
state/timing effect on the following reference discharge.
[EIS/rest-time study](https://doi.org/10.3390/wevj14120321). Recent RPT data
likewise report capacity tests and multi-SOC EIS as distinct protocol
operations. [Khan et al.](https://doi.org/10.1016/j.dib.2025.112282)

```text
NASA_OPERATION_SEMANTICS=VERIFIED__SEPARATE_CHARGE_DISCHARGE_IMPEDANCE_RECORDS
DIRECT_PRECEDENT_FOR_CHARGE_TO_DIAGNOSTIC_TO_DISCHARGE_PAIRING=UNVERIFIED
DIAGNOSTIC_PHYSICAL_NONINTERFERENCE=UNVERIFIED_FOR_NASA_TARGET_SEMANTICS
```

## Candidate operation grammar — proposal only

| Canonical class | NASA evidence | Between establishing charge and target discharge? |
|---|---|---|
| `STATE_ESTABLISHING_CHARGE` | V1-valid `charge` | Starts a candidate only |
| `TARGET_DISCHARGE_OPERATION` | V1-valid `discharge` | Ends a candidate only |
| `DIAGNOSTIC_OPERATION` | `impedance` record | Candidate B only; semantic justification pending |
| `REST_OPERATION` | no named NASA record verified here | Only after an explicit adapter maps it |
| `NEW_CHARGE_OPERATION` | later `charge` | Never allowed; ambiguous |
| `UNKNOWN_OPERATION` | unmapped/inconsistent record | Never allowed |

| Candidate | Rule | Assessment | B0007 retention (descriptive) |
|---|---|---|---:|
| A — V1 | `CHARGE -> DISCHARGE` immediately | Mechanical but treats every native diagnostic as a break. | 23/67 |
| B — proposed V1.1 | `CHARGE -> (DIAGNOSTIC or explicitly mapped REST)* -> FIRST_ELIGIBLE_DISCHARGE` | Label-free and potentially reproducible; cannot freeze until timing/target semantics and external adapters are verified. | 65/67 |
| C — broad later discharge | `CHARGE -> any later eligible discharge` | Rejected: duplicate/ambiguous mappings and uncontrolled freedom. | not used |

`65/67` is descriptive only. Candidate B has a permissible rationale only if
the same rule remains justified with every retention count omitted.

If reconsidered, the future grammar must freeze all of the following:

```text
STATE_ESTABLISHING_CHARGE -> ALLOWED_INTERMEDIATE_OPERATION* -> FIRST_ELIGIBLE_TARGET_DISCHARGE
ALLOWED_INTERMEDIATE_OPERATION=adapter-mapped DIAGNOSTIC_OPERATION or explicitly named REST_OPERATION only
FORBIDDEN=NEW_CHARGE_OPERATION, TARGET_DISCHARGE_OPERATION, UNKNOWN_OPERATION, malformed/non-monotone record
MULTIPLE_CHARGE_POLICY=EXCLUDE_AS_AMBIGUOUS
MULTIPLE_DISCHARGE_POLICY=first eligible discharge only; no later reuse
ONE_TO_ONE_PAIRING_RULE=ONE_CHARGE_MAX_ONE_TARGET_DISCHARGE and ONE_TARGET_DISCHARGE_MAX_ONE_CHARGE
TIMESTAMP_ORDER_RULE=strictly increasing operation start times; ties/non-monotone entries excluded
CYCLE_ID_RULE=use native ID when available, otherwise grammar plus one-to-one invariant only
UNKNOWN_OPERATION_POLICY=EXCLUDE_AS_AMBIGUOUS
```

## L1 prediction-time semantics — the blocking issue

V1 sets L1 at the charge CV cutoff. A diagnostic interlude admits three
readings:

| Reading | Interpretation | Status |
|---|---|---|
| A | Emit at charge completion; use no diagnostic sample; forecast the reference-discharge capacity after scheduled diagnostics. | Coherent only if that reference-test trajectory is formally accepted. Unverified. |
| B | Emit after diagnostics just before discharge. | Alters timestamp; if diagnostic values are visible it is a new contract. Rejected for V1.1. |
| C | Treat pre- and post-diagnostic estimates as separate contracts. | May be scientifically valid but expands the frozen three-level question. Not a V1.1 repair. |

```text
L1_PREDICTION_TIMESTAMP=UNRESOLVED_FOR_V1_1
L1_OBSERVABLE_SIGNAL_SET=CHARGE_AND_CAUSAL_HISTORY_ONLY__IF_A_IS_LATER_APPROVED
L1_INTERMEDIATE_OPERATION_ACCESS=OPERATION_EXISTENCE_ONLY__NOT_SIGNAL_ACCESS
L1_DIAGNOSTIC_SIGNAL_ACCESS=PROHIBITED
L1_DEPLOYMENT_INTERPRETATION=UNRESOLVED__POST_CHARGE_REFERENCE_TEST_FORECAST_NEEDS_HUMAN_DECISION
DIAGNOSTIC_OPERATION_ALLOWED_IN_PAIRING=False__UNTIL_GATE_PASSES
DIAGNOSTIC_SIGNAL_ALLOWED_AS_FEATURE=False
```

Any future L1 extractor must whitelist charge/history arrays and reject all
impedance fields (`Battery_impedance`, `Rectified_impedance`, `Re`, `Rct` and
raw diagnostic series). This is a future conformance condition, not code work
authorized here.

## Blindness and cross-dataset checks

```text
AMENDMENT_DECISION_BLINDNESS_CHECK=PASS_FOR_INPUTS__NO_SOH_LABEL_MODEL_OR_METRIC_READ
RESULT_DRIVEN_PROTOCOL_RISK=HIGH_BUT_CONTROLLED_BY_BLOCKING_FREEZE
SCIENTIFIC_JUSTIFICATION_INDEPENDENT_OF_RETENTION=PARTIALLY_DEFINED__NOT_SUFFICIENT_TO_FREEZE
CROSS_DATASET_GENERALIZABILITY=BLOCKED__OPERATION_ONTOLOGY_MAPPING_NOT_YET_VERIFIED
```

The Luh & Blank NMC/C–SiO and RWTH ISEA NMC/graphite entries are only
source-eligible: their manifests show raw waveform/capacity availability, not
file-level operation names, ordering semantics, or native cycle identities.

| Dataset | Raw operation types | Canonical mapping | Label-free executable now? | Dataset exception needed? |
|---|---|---|---|---|
| Luh & Blank NMC/C–SiO | `UNVERIFIED_AT_FILE_SCHEMA_LEVEL` | pending adapter | No | Unknown |
| RWTH ISEA NMC/graphite | `UNVERIFIED_AT_FILE_SCHEMA_LEVEL` | pending adapter | No | Unknown |

## Idea-evaluator kill tests

| Test | Severity | Validity | Defense | Required evidence | Fatal if unresolved? |
|---|---|---|---|---|---|
| K1 post-23/67 invention | High | Valid | no labels/metrics used; V1 preserved | rationale without retention | Yes |
| K2 EIS is no longer post-charge | Critical | Valid | only reading A keeps charge-time emission | reference-test target semantics | Yes |
| K3 crossing unused EIS | High | Valid | operation may exist without becoming input | why target remains same | Yes |
| K4 EIS feature makes a new contract | Critical | Valid | diagnostic values prohibited | future extractor audit | Yes |
| K5 grammar arbitrary | High | Valid | finite ontology + unknown exclusion | cross-data adapter evidence | Yes |
| K6 who labels diagnostics | Critical | Valid | predeclared adapter only | published schema/protocol | Yes |
| K7 state perturbation differs | Critical | Valid | no noninterference claim made | protocol-specific rationale | Yes |
| K8 charge->charge->discharge | High | Valid | target identity otherwise undefined | raw ordering only | No; exclude |
| K9 65/67 bias | High | Valid | count is not a criterion | human blind-to-performance approval | Yes |
| K10 why not strict 23 | Medium | Valid | V1 remains a negative control | none | No |
| K11 no EIS externally | Medium | Valid | zero intermediates satisfy grammar | map every other operation | No |
| K12 claim changes | Critical | Valid | may become reference-test forecast | explicit researcher choice | Yes |

## Final gate

V1.1 requires a non-adjacency rationale, unique L1 timestamp/target,
diagnostic-signal prohibition, one-to-one grammar, blind selection, external
mapping and no fatal reviewer objection. The draft can meet signal prohibition
and one-to-one invariants, but target/timing semantics and portable mapping are
unresolved. K2/K3/K5/K6/K7/K12 remain fatal to a freeze.

```text
IMMEDIATE_ADJACENCY_RULE=IMPLEMENTATION_ARTIFACT__NOT_A_VERIFIED_SCIENTIFIC_INVARIANT
CANONICAL_OPERATION_GRAMMAR=PROPOSED_NOT_FROZEN
ONE_TO_ONE_PAIRING_RULE=DEFINED_FOR_FUTURE_REVIEW
AMBIGUITY_POLICY=EXCLUDE_AS_AMBIGUOUS
PROTOCOL_AMENDMENT_REQUIRED=True
PROTOCOL_AMENDMENT_GATE=BLOCKED
PTOC_F4=FAIL_FOR_V1__NOT_REOPENED
PTOC_PROTOCOL_V1_1_CREATED=False
PHASE_3_STATUS=BLOCKED
EXPERIMENT_AUTHORIZATION=BLOCKED
NEXT_ACTION=HUMAN_DECISION_ON_L1_REFERENCE_TEST_SEMANTICS_AND_EXTERNAL_OPERATION_ADAPTER_AUDIT
FINAL_VERDICT=PTOC_PROTOCOL_AMENDMENT_BLOCKED__DO_NOT_FREEZE_V1_1
```

## Master-plan provenance correction

`PTOC-003-AMENDMENT-001` is labelled a post-completion amendment yet names
Phase ③, whereas the master plan names Phase ② as last completed and Phase ③
as `BLOCKED`. Its historical evidence remains useful, but its classification
is wrong. A non-destructive correction/change-log entry records this below;
neither history nor V1 is rewritten.

```text
POST_COMPLETION_AMENDMENT_STATUS=MISCLASSIFIED
POST_COMPLETION_AMENDMENT_TARGET_PHASE=③ PTOC Pre-Experiment Gate__CURRENT_BLOCKED_NOT_COMPLETED
CORRECT_CLASSIFICATION=CURRENT_PHASE_BLOCKER_AND_PROVENANCE_UPDATE
MASTER_PLAN_UPDATE_REQUIRED=True
PLAN_CHANGE_ID=PLAN-CHANGE-0002
LEAKAGE_FOUND=False
VALIDATION_OR_TEST_LABEL_LOADED=False
SOH_METRIC_CALCULATED=False
ROOT_MODIFIED=False
SECOND_INNOVATION_ADDED=False
HYPOTHESIS_SHOPPING_FOUND=False
FINAL_VIBE_INTEGRITY_REVIEW=PASS
```
