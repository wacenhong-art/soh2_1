# PTOC Phase ③ Blocker Resolution 1 — G2 and Matched-Cycle Audit

```text
TASK=PHASE_3_BLOCKER_RESOLUTION_1
PHASE=③ PTOC PRE-EXPERIMENT GATE
ROOT_STATUS=FROZEN
ROOT_MODIFIED=False
PERFORMANCE_EXPERIMENT_RUN=False
OUTER_VALIDATION_LOADED=False
TestLoaded=False
EXPERIMENT_AUTHORIZATION=BLOCKED
```

## Boundary and method

G2 was completed before any protocol-amendment proposal. This document does not
edit `PTOC_PROTOCOL_V1.md`. Raw inspection used only record type, MATLAB start
time, and V/I/T/time metadata; it did not access capacity/SOH/validation/test
labels, fit models, create predictions, or calculate performance.

## G2 nearest-work chain

| Paper | Source status | Verified scope | PTOC overlap / missing component | Collision |
|---|---|---|---|---|
| Rizanov, Stoynova & Mihov, *Batteries* 12, 255 (2026), [DOI](https://doi.org/10.3390/batteries12070255) | Publisher indexed full text; direct PDF rate-limited. | Review, multi-fidelity validation framework and deployment checklist. | Observability/deployment validation overlap; no verified per-estimate time contract, matched intersection, later-feature enforcement, capacity-adjacent rule or cross-contract ranking prohibition. | `PRINCIPLE_AND_REPORTING_LEVEL` |
| Guo et al., *EnergyZ* (2026), [DOI](https://doi.org/10.20517/energyz.2025.08) | Publisher indexed article text. | Review pipeline and conclusion. | Signal/target/deployment alignment; no executable matched-cycle benchmark verified. | `PRINCIPLE_LEVEL` |
| Pandit & Ahlawat, *Future Batteries* 7, 100099 (2025), [DOI](https://doi.org/10.1016/j.fub.2025.100099) | Official metadata/abstract/highlights; full method unavailable. | Comparative-framework scope only. | Standardisation/split overlap; PTOC components A–I are `UNVERIFIED`. | `PARTIAL_METHOD__METHOD_DETAIL_UNVERIFIED` |
| Ma et al., *Energies* 19, 1506 (2026), [DOI](https://doi.org/10.3390/en19061506) | Crossref primary metadata/abstract; publisher PDF denied. | VTDS framework in registered abstract. | Evaluation/deployment overlap; no abstract evidence of cycle-level timing, matched cycles or capacity-adjacent restriction. | `PARTIAL_METHOD__METHOD_DETAIL_UNVERIFIED` |
| Petrella, Marzolla & Mercuri, *JES* 138, 118747 (2025), [DOI](https://doi.org/10.1016/j.est.2025.118747) | Open primary PDF. | Partial-charge V/T estimator; NASA charge uses prior-discharge capacity. | Partial observation overlap; different target association and no multi-contract matched/ranking protocol. | `PARTIAL_METHOD` |
| Zhang & Lai, *WEVJ* 16, 277 (2025), [DOI](https://doi.org/10.3390/wevj16050277) | Publisher metadata/abstract; method unavailable. | Partial-discharge method scope. | Benchmark components C–I unverified. | `PARTIAL_METHOD__METHOD_DETAIL_UNVERIFIED` |

No accessed source was verified to jointly require: prediction-time contract,
causal boundary, same target, matched population, later-information exclusion,
capacity-adjacent disclosure, comparability classification, executable protocol
and deployment eligibility. This is a possible method distinction only if PTOC
enforces those conditions in code/data, not merely as prose.

```text
G2_FINAL_STATUS=ACCEPTABLE_PARTIAL_COLLISION
DIRECT_COLLISION_LEVEL=PARTIAL_METHOD
NEAREST_EXISTING_WORK=Rizanov_2026 + Ma_2026 frameworks; Petrella_2025 partial-charge estimator
EXACT_METHOD_LEVEL_DIFFERENCE=PTOC requires a per-estimate contract, a predeclared matched-cycle intersection, and an executable prohibition on cross-contract R2 leaderboards.
PTOC_DIRECTION_STATUS=NOT_REJECTED_BY_DIRECT_COLLISION
NOVELTY_CLAIM_STATUS=NOT_ESTABLISHED__FULL_TEXT_CHAIN_REQUIRED_BEFORE_MANUSCRIPT
```

## B0007 raw-event taxonomy

The earlier “31/67” mixed denominators. Thirty-one is a whole-file strict-pair
count; it is not the count inside ROOT's 67 development candidates. Reconstructing
the first 67 historical candidates by raw V/I/T/time event eligibility yields:

| Taxonomy | Count | Example charge IDs | Pattern | Meaning |
|---|---:|---|---|---|
| `IMMEDIATE_VALID_DISCHARGE` | 23 | 0, 2, 4, 6, 8 | `charge→discharge` | v1 valid. |
| `INTERVENING_IMPEDANCE_ONLY_THEN_VALID_DISCHARGE` | 42 | 39, 43, 47, 51, 55 | `charge→impedance→discharge` | Repeated native record grammar. |
| `INTERVENING_CHARGE_BEFORE_DISCHARGE` | 2 | 22, 83 | `charge→charge→discharge` | Ambiguous; old extractor maps both charges to one discharge. |

```text
B0007_TOTAL_CANDIDATES=67
B0007_V1_MATCHED=23
B0007_GLOBAL_V1_STRICT_PAIRS=31_OF_170_RAW_CHARGES__NOT_A_67_ROW_MAPPING
B0018_TOTAL_CANDIDATES=51
B0018_V1_MATCHED=51
```

| Observed issue | Type | Scientific classification |
|---|---|---|
| 42 impedance-only intermediaries | B + C | Natural protocol structure plus v1 overconstraint. |
| 2 intervening-charge records and duplicate target mappings | A | Historical pairing implementation bug; not solved by broad matching. |
| Invalid/missing V/I/T events among the 67 | None | Not observed. |

NASA documents separate charge, discharge and EIS records in its battery data
set ([source](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/)). The raw sequence is therefore not evidence of corruption, but it does not prove that EIS is physically negligible.

```text
PAIRING_PROBLEM_TYPE=TYPE_A_CODE_PAIRING_BUG + TYPE_B_NATURAL_PROTOCOL_STRUCTURE + TYPE_C_PTOC_PROTOCOL_OVERCONSTRAINT
TYPE_D_SCIENTIFIC_INCOMPATIBILITY=NOT_ESTABLISHED
IMMEDIATE_ADJACENCY_RULE=IMPLEMENTATION_ARTIFACT
```

## Candidate rules — design only

| Candidate | Rule | Validity/freedom | B0007 count | Verdict |
|---|---|---|---:|---|
| A | `charge→discharge` immediate. | Clear guard; overconstrained. | 23/67 | Negative control only. |
| B | `charge→diagnostic*→discharge`; NASA diagnostic exactly `impedance`; no charge/unknown operation; first valid discharge. | Conditional and label-independent if ontology is frozen. L1 forecasts following reference-discharge outcome. | 65/67 | Only defensible amendment candidate. |
| C | Any later discharge by time/proximity/retention. | High degrees of freedom and duplicate risk. | N/A | Rejected. |

```text
PROTOCOL_AMENDMENT_REQUIRED=True
PTOC_PROTOCOL_V1_1_AMENDMENT_PROPOSAL=REQUIRES_HUMAN_APPROVAL
TRIGGER=V1 adjacency conflates recurring impedance records with true charge-chain ambiguity; old extraction has two duplicate mappings.
OLD_RULE=charge immediately followed by qualifying discharge
PROPOSED_RULE=charge followed by zero or more predeclared diagnostic records and then first valid discharge, with no charge or unknown operation intervening; retain all exclusion reasons.
SCIENTIFIC_JUSTIFICATION=The raw grammar separates diagnostic interludes from second-charge ambiguity; the target is the following reference-discharge outcome and earlier features remain causal.
WHY_NOT_RESULT_DRIVEN=Only type/order/time and V/I/T events were inspected; no labels/models/metrics were accessed.
AFFECTED_GATES=TARGET_SEMANTICS; MATCHED_CYCLE; EXTERNAL_PROTOCOL_FIDELITY; CONTROL_AND_FALSIFICATION
INVALIDATES_PRIOR_RESULTS=No PTOC performance result exists. V1 strict-feasibility conclusion and manifest require replacement; ROOT provenance must disclose two duplicate mappings without recomputing ROOT.
```

## Gate result and reviewer attack

```text
MATCHED_CYCLE_FEASIBILITY_V1=FAIL__23_OF_67_EXACT_DEVELOPMENT_CANDIDATES_FOR_B0007
MATCHED_CYCLE_FEASIBILITY_WITH_JUSTIFIED_AMENDMENT=CONDITIONALLY_FEASIBLE__65_OF_67_PENDING_HUMAN_APPROVAL_AND_EXTERNAL_SCHEMA_AUDIT
PAIRING_RULE_CROSS_DATASET_GENERALIZABILITY=CONDITIONAL__CANONICAL_OPERATION_GRAMMAR_NOT_NASA_LITERAL
PTOC_F1=PASS_FOR_PREEXPERIMENT_GATE__PARTIAL_COLLISION_ONLY
PTOC_F4=FAIL_FOR_V1__PENDING_V1_1_HUMAN_DECISION
PTOC_F6=FROZEN_EMPIRICAL_KILL_CONDITION
```

R1 (post-hoc relaxation), R4 (grammar freedom), R5 (label independence),
R6–R8 (external portability) and R10 (triviality) remain valid reviewer
attacks. Candidate B is defensible only with a frozen finite ontology, first
valid discharge rule, static no-label audit and external schema adapter. It
does not solve F6. `idea-evaluator` therefore returns
`ACCEPT_WITH_REVISIONS_FOR_HUMAN_PROTOCOL_REVIEW`, not Phase ④ authorization.

## Final integrity review

```text
SUPERVISOR_SKILLS_GATE=PASS
VIBE_RESEARCH_WORKFLOW_USED=True
DEEP_RESEARCH_USED=True
IDEA_EVALUATOR_USED=True
FINAL_VIBE_INTEGRITY_REVIEW=PASS
PHASE_3_STATUS=BLOCKED_PENDING_PROTOCOL_AMENDMENT
EXPERIMENT_AUTHORIZATION=BLOCKED
NEXT_ACTION=HUMAN_REVIEW_OF_PTOC_PROTOCOL_V1_1_AMENDMENT_PROPOSAL
FINAL_VERDICT=PTOC_PRE_EXPERIMENT_GATE_BLOCKED
```
